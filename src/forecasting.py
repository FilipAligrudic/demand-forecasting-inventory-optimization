"""
Forecasting modeli — baseline, LightGBM (glavni) i opcioni Prophet.

Funkcije:
- baseline_moving_average: naivni forecast (prosjek prethodnih N dana)
- train_lightgbm: glavni model (point + quantile za intervale)
- recursive_forecast_lgbm: dnevni rekurzivni forecast za H dana
- prophet_forecast: opcioni sezonski model
- evaluate_models: MAE / RMSE / MAPE poređenje
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

import lightgbm as lgb

from .feature_engineering import (
    LAG_DAYS,
    ROLLING_WINDOWS,
    add_calendar_features,
    add_lag_features,
    add_rolling_features,
    build_features,
)


@dataclass
class ForecastResult:
    """Container za rezultate jednog modela."""

    name: str
    forecast: pd.DataFrame  # kolone: Date, yhat, yhat_lower, yhat_upper
    metrics: dict = field(default_factory=dict)
    model: object | None = None


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def _mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    mask = y_true > 1e-6
    if not mask.any():
        return float("nan")
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def compute_metrics(y_true, y_pred) -> dict:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return {
        "MAE": float(mean_absolute_error(y_true, y_pred)),
        "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "MAPE": _mape(y_true, y_pred),
    }


# ---------------------------------------------------------------------------
# Baseline
# ---------------------------------------------------------------------------

def baseline_moving_average(history: pd.DataFrame, horizon: int, window: int = 7) -> pd.DataFrame:
    """Naivni baseline — prosjek posljednjih `window` dana, ponovljen H puta."""
    last_date = history["Date"].max()
    mean = history["Sales"].tail(window).mean()
    std = history["Sales"].tail(window * 2).std()
    future_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=horizon, freq="D")
    return pd.DataFrame(
        {
            "Date": future_dates,
            "yhat": mean,
            "yhat_lower": max(0, mean - 1.96 * std),
            "yhat_upper": mean + 1.96 * std,
        }
    )


def seasonal_naive_forecast(history: pd.DataFrame, horizon: int, season_length: int = 7) -> pd.DataFrame:
    """Sezonski naivni model — prognoza = vrijednost od prije `season_length` dana.

    Klasičan i jak benchmark za serije sa sedmičnom sezonalnošću. Bez ijedne
    eksterne biblioteke, uvijek radi (za razliku od Prophet-a na Python 3.13).
    Interval pouzdanosti se računa iz greške sezonskog ponavljanja na istoriji.
    """
    last_date = history["Date"].max()
    sales = history["Sales"].to_numpy(dtype=float)
    future_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=horizon, freq="D")

    if len(sales) < season_length:
        mean = float(np.mean(sales)) if len(sales) else 0.0
        return pd.DataFrame({"Date": future_dates, "yhat": mean, "yhat_lower": mean, "yhat_upper": mean})

    last_season = sales[-season_length:]
    yhat = np.array([last_season[i % season_length] for i in range(horizon)], dtype=float)

    # rezidual sezonskog ponavljanja na istoriji -> širina intervala
    resid = sales[season_length:] - sales[:-season_length]
    sigma = float(np.std(resid)) if resid.size else 0.0
    return pd.DataFrame(
        {
            "Date": future_dates,
            "yhat": np.clip(yhat, 0, None),
            "yhat_lower": np.clip(yhat - 1.96 * sigma, 0, None),
            "yhat_upper": np.clip(yhat + 1.96 * sigma, 0, None),
        }
    )


# ---------------------------------------------------------------------------
# Holt-Winters (klasičan sezonski model — statsmodels, radi i na Python 3.13)
# ---------------------------------------------------------------------------

def holt_winters_forecast(history: pd.DataFrame, horizon: int, season_length: int = 7) -> Optional[pd.DataFrame]:
    """Holt-Winters Exponential Smoothing (trend + sedmična sezonalnost).

    Klasičan statistički model za sezonske serije. Vraća None ako statsmodels
    nije instaliran ili ima premalo podataka. Interval pouzdanosti iz reziduala.
    """
    try:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing  # lazy import
    except Exception:  # pragma: no cover
        return None

    y = history["Sales"].astype(float).reset_index(drop=True)
    if len(y) < 2 * season_length + 10:
        return None

    last_date = history["Date"].max()
    future_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=horizon, freq="D")
    try:
        model = ExponentialSmoothing(
            y, trend="add", seasonal="add",
            seasonal_periods=season_length, initialization_method="estimated",
        )
        fit = model.fit()
        yhat = np.asarray(fit.forecast(horizon), dtype=float)
        resid = np.asarray(y) - np.asarray(fit.fittedvalues, dtype=float)
        sigma = float(np.nanstd(resid))
    except Exception:  # konvergencija/numerika
        return None

    yhat = np.clip(yhat, 0, None)
    return pd.DataFrame(
        {
            "Date": future_dates,
            "yhat": yhat,
            "yhat_lower": np.clip(yhat - 1.96 * sigma, 0, None),
            "yhat_upper": np.clip(yhat + 1.96 * sigma, 0, None),
        }
    )


# ---------------------------------------------------------------------------
# Ensemble (hibrid) — težinski spoj više modela
# ---------------------------------------------------------------------------

def ensemble_forecast(
    forecasts: dict[str, Optional[pd.DataFrame]],
    weights: Optional[dict[str, float]] = None,
) -> Optional[pd.DataFrame]:
    """Težinski prosjek prognoza više modela poravnatih po istim datumima.

    `forecasts` je npr. {"LightGBM": df, "Holt-Winters": df, ...}; None se ignoriše.
    Ovo je "hibridni" model iz postavke — kombinuje ML (LightGBM) i klasičan
    sezonski model (Holt-Winters), opciono i Prophet.
    """
    items = [(name, f) for name, f in forecasts.items() if f is not None and len(f) > 0]
    if not items:
        return None
    if len(items) == 1:
        return items[0][1].copy()

    if weights is None:
        weights = {name: 1.0 for name, _ in items}
    total = sum(weights.get(name, 1.0) for name, _ in items)

    base = items[0][1].reset_index(drop=True)
    n = len(base)
    yhat = np.zeros(n)
    lo = np.zeros(n)
    hi = np.zeros(n)
    for name, f in items:
        w = weights.get(name, 1.0) / total
        f = f.reset_index(drop=True)
        yhat += w * f["yhat"].to_numpy()[:n]
        lo += w * f["yhat_lower"].to_numpy()[:n]
        hi += w * f["yhat_upper"].to_numpy()[:n]
    return pd.DataFrame({"Date": base["Date"].values, "yhat": yhat, "yhat_lower": lo, "yhat_upper": hi})


# ---------------------------------------------------------------------------
# LightGBM main model
# ---------------------------------------------------------------------------

LGB_DEFAULT_PARAMS = dict(
    objective="regression",
    learning_rate=0.05,
    num_leaves=31,
    max_depth=-1,
    min_data_in_leaf=20,
    feature_fraction=0.9,
    bagging_fraction=0.9,
    bagging_freq=5,
    random_state=42,
    verbose=-1,
)


def train_lightgbm(
    df: pd.DataFrame,
    features: list[str],
    target: str = "Sales",
    val_fraction: float = 0.15,
    quantiles: tuple[float, float] = (0.1, 0.9),
) -> dict:
    """Treniraj LightGBM regression + dva quantile modela za interval pouzdanosti.

    Vraća dict: {"point": model, "lower": model, "upper": model, "val_metrics": {...}}.
    """
    df = df.dropna(subset=features + [target]).reset_index(drop=True)
    if len(df) < 50:
        raise ValueError("Premalo redova za treniranje LightGBM modela.")

    cut = int(len(df) * (1 - val_fraction))
    train, val = df.iloc[:cut], df.iloc[cut:]

    X_train, y_train = train[features], train[target]
    X_val, y_val = val[features], val[target]

    point = lgb.LGBMRegressor(**LGB_DEFAULT_PARAMS, n_estimators=600)
    point.fit(
        X_train,
        y_train,
        eval_set=[(X_val, y_val)],
        callbacks=[lgb.early_stopping(40, verbose=False), lgb.log_evaluation(0)],
    )

    lower_params = dict(LGB_DEFAULT_PARAMS)
    lower_params.update(objective="quantile", alpha=quantiles[0])
    lower = lgb.LGBMRegressor(**lower_params, n_estimators=600)
    lower.fit(X_train, y_train, eval_set=[(X_val, y_val)],
              callbacks=[lgb.early_stopping(40, verbose=False), lgb.log_evaluation(0)])

    upper_params = dict(LGB_DEFAULT_PARAMS)
    upper_params.update(objective="quantile", alpha=quantiles[1])
    upper = lgb.LGBMRegressor(**upper_params, n_estimators=600)
    upper.fit(X_train, y_train, eval_set=[(X_val, y_val)],
              callbacks=[lgb.early_stopping(40, verbose=False), lgb.log_evaluation(0)])

    val_pred = point.predict(X_val)
    val_metrics = compute_metrics(y_val, val_pred)

    return {
        "point": point,
        "lower": lower,
        "upper": upper,
        "val_metrics": val_metrics,
        "val_index": val.index.tolist(),
        "val_pred": val_pred,
        "val_true": y_val.values,
        "val_dates": val["Date"].values,
    }


def recursive_forecast_lgbm(
    history: pd.DataFrame,
    models: dict,
    features: list[str],
    horizon: int,
    target: str = "Sales",
) -> pd.DataFrame:
    """Iterativni dnevni forecast: predikcija ulazi kao lag za sljedeći dan."""
    work = history.copy().sort_values("Date").reset_index(drop=True)
    point_model = models["point"]
    lower_model = models["lower"]
    upper_model = models["upper"]

    last_date = work["Date"].max()
    future_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=horizon, freq="D")

    preds, lowers, uppers = [], [], []
    for d in future_dates:
        # napravi jedan red sa istim feature setom
        new_row = {col: np.nan for col in work.columns}
        new_row["Date"] = d
        for col in ("Store", "Product"):
            if col in work.columns:
                new_row[col] = work[col].iloc[-1]
        # Bez planiranog događaja, budući dani su "normalni": nema promocije/praznika.
        # (Kopiranje posljednje vrijednosti je bug — ako je zadnji dan bio promo,
        #  cijeli forecast bi bio naduvan ~40%.) What-if u dashboardu dodaje promo.
        for col in ("Promo", "SchoolHoliday"):
            if col in work.columns:
                new_row[col] = 0
        if "Price" in work.columns:
            # cijena perzistira (planski podatak) — zadnja poznata vrijednost
            new_row["Price"] = work["Price"].iloc[-1]
        if "StateHoliday" in work.columns:
            new_row["StateHoliday"] = "0"

        work = pd.concat([work, pd.DataFrame([new_row])], ignore_index=True)
        work = add_calendar_features(work)
        work = add_lag_features(work, target=target)
        work = add_rolling_features(work, target=target)
        if "StateHoliday" in work.columns:
            work["StateHoliday_flag"] = (work["StateHoliday"].astype(str) != "0").astype(int)

        X_last = work[features].ffill().iloc[[-1]].fillna(0)
        yhat = float(point_model.predict(X_last)[0])
        ylo = float(lower_model.predict(X_last)[0])
        yhi = float(upper_model.predict(X_last)[0])
        yhat = max(0.0, yhat)
        ylo = max(0.0, ylo)
        yhi = max(yhi, yhat)

        work.loc[work.index[-1], target] = yhat
        preds.append(yhat)
        lowers.append(ylo)
        uppers.append(yhi)

    return pd.DataFrame(
        {"Date": future_dates, "yhat": preds, "yhat_lower": lowers, "yhat_upper": uppers}
    )


# ---------------------------------------------------------------------------
# Prophet (opciono)
# ---------------------------------------------------------------------------

def prophet_forecast(history: pd.DataFrame, horizon: int) -> Optional[pd.DataFrame]:
    """Prophet sa default-nim sezonskim parametrima. Vraća None ako Prophet nije dostupan."""
    try:
        from importlib import import_module

        Prophet = import_module("prophet").Prophet  # lazy import — sporo se učitava
    except Exception:  # pragma: no cover
        return None

    df = history[["Date", "Sales"]].rename(columns={"Date": "ds", "Sales": "y"}).dropna()
    if len(df) < 30:
        return None

    m = Prophet(
        weekly_seasonality=True,
        yearly_seasonality=True,
        daily_seasonality=False,
        interval_width=0.8,
    )
    m.fit(df)
    future = m.make_future_dataframe(periods=horizon, freq="D")
    fcst = m.predict(future).tail(horizon)
    return pd.DataFrame(
        {
            "Date": fcst["ds"].values,
            "yhat": fcst["yhat"].clip(lower=0).values,
            "yhat_lower": fcst["yhat_lower"].clip(lower=0).values,
            "yhat_upper": fcst["yhat_upper"].clip(lower=0).values,
        }
    )


# ---------------------------------------------------------------------------
# Compare
# ---------------------------------------------------------------------------

def evaluate_on_backtest(history_with_features: pd.DataFrame, features: list[str], horizon: int = 28) -> pd.DataFrame:
    """Brzi backtest: zadnjih `horizon` dana se drže kao test set, model uči na ostatku.

    Vraća DataFrame poređenja: kolone Model, MAE, RMSE, MAPE.
    """
    df = history_with_features.dropna(subset=features + ["Sales"]).reset_index(drop=True)
    if len(df) <= horizon + 30:
        return pd.DataFrame()

    train = df.iloc[:-horizon].copy()
    test = df.iloc[-horizon:].copy()
    y_true = test["Sales"].values

    # Baseline
    baseline_fc = baseline_moving_average(train, horizon=horizon)

    # Sezonski naivni (jak klasičan benchmark)
    snaive_fc = seasonal_naive_forecast(train, horizon=horizon)

    # Holt-Winters (klasičan sezonski)
    hw_fc = holt_winters_forecast(train, horizon=horizon)

    # LightGBM
    models = train_lightgbm(train, features=features, val_fraction=0.15)
    lgbm_fc = recursive_forecast_lgbm(train, models, features, horizon=horizon)

    rows = [
        {"Model": "Baseline (moving avg)", **compute_metrics(y_true, baseline_fc["yhat"].values)},
        {"Model": "Sezonski naivni", **compute_metrics(y_true, snaive_fc["yhat"].values)},
        {"Model": "LightGBM", **compute_metrics(y_true, lgbm_fc["yhat"].values)},
    ]
    if hw_fc is not None:
        rows.append({"Model": "Holt-Winters", **compute_metrics(y_true, hw_fc["yhat"].values)})

    # Prophet (opciono)
    pf = prophet_forecast(train, horizon=horizon)
    if pf is not None and len(pf) == horizon:
        rows.append({"Model": "Prophet", **compute_metrics(y_true, pf["yhat"].values)})

    # Ensemble (hibrid): LightGBM + Holt-Winters [+ Prophet]
    ens = ensemble_forecast(
        {"LightGBM": lgbm_fc, "Holt-Winters": hw_fc, "Prophet": pf},
        weights={"LightGBM": 0.6, "Holt-Winters": 0.25, "Prophet": 0.15},
    )
    if ens is not None and len(ens) == horizon:
        rows.append({"Model": "Ensemble (hibrid)", **compute_metrics(y_true, ens["yhat"].values)})

    return pd.DataFrame(rows)


def rolling_origin_backtest(
    history_with_features: pd.DataFrame,
    features: list[str],
    horizon: int = 28,
    n_splits: int = 3,
) -> pd.DataFrame:
    """Rolling-origin (walk-forward) kros-validacija.

    Pravi `n_splits` uzastopnih cutoff-a; na svakom trenira na prošlosti i mjeri
    grešku narednih `horizon` dana. Vraća prosječne MAE/RMSE/MAPE po modelu —
    robusnija procjena tačnosti od jednog backtest-a.
    """
    df = history_with_features.dropna(subset=features + ["Sales"]).reset_index(drop=True)
    min_train = max(120, horizon + 60)
    if len(df) < min_train + horizon:
        return pd.DataFrame()

    # cutoff-i: posljednjih n_splits prozora po `horizon`
    n_splits = max(1, min(n_splits, (len(df) - min_train) // horizon))
    fold_rows: list[dict] = []
    for k in range(n_splits, 0, -1):
        cut = len(df) - k * horizon
        if cut < min_train:
            continue
        train = df.iloc[:cut]
        test = df.iloc[cut:cut + horizon]
        if len(test) < horizon:
            continue
        y_true = test["Sales"].values

        baseline_fc = baseline_moving_average(train, horizon=horizon)
        snaive_fc = seasonal_naive_forecast(train, horizon=horizon)
        hw_fc = holt_winters_forecast(train, horizon=horizon)
        models = train_lightgbm(train, features=features, val_fraction=0.15)
        lgbm_fc = recursive_forecast_lgbm(train, models, features, horizon=horizon)
        ens = ensemble_forecast(
            {"LightGBM": lgbm_fc, "Holt-Winters": hw_fc},
            weights={"LightGBM": 0.6, "Holt-Winters": 0.4},
        )

        fold_rows.append({"Model": "Baseline (moving avg)", **compute_metrics(y_true, baseline_fc["yhat"].values)})
        fold_rows.append({"Model": "Sezonski naivni", **compute_metrics(y_true, snaive_fc["yhat"].values)})
        fold_rows.append({"Model": "LightGBM", **compute_metrics(y_true, lgbm_fc["yhat"].values)})
        if hw_fc is not None:
            fold_rows.append({"Model": "Holt-Winters", **compute_metrics(y_true, hw_fc["yhat"].values)})
        if ens is not None:
            fold_rows.append({"Model": "Ensemble (hibrid)", **compute_metrics(y_true, ens["yhat"].values)})

    if not fold_rows:
        return pd.DataFrame()

    out = pd.DataFrame(fold_rows).groupby("Model", as_index=False)[["MAE", "RMSE", "MAPE"]].mean()
    return out.sort_values("MAPE").reset_index(drop=True)


# ---------------------------------------------------------------------------
# Convenience
# ---------------------------------------------------------------------------

def fit_and_forecast(series: pd.DataFrame, horizon: int = 28) -> dict:
    """Pipeline: feature engineering -> train -> forecast -> baseline.

    Vraća dict:
      {
        "features_df": df sa feature-ima (za SHAP i anomalije),
        "feature_list": [...],
        "models": dict iz train_lightgbm,
        "forecast": DataFrame,
        "baseline": DataFrame,
        "metrics": {...},
      }
    """
    feat_df, features = build_features(series)
    models = train_lightgbm(feat_df, features=features)
    fcst = recursive_forecast_lgbm(feat_df, models, features, horizon=horizon)
    baseline = baseline_moving_average(feat_df, horizon=horizon)
    return {
        "features_df": feat_df,
        "feature_list": features,
        "models": models,
        "forecast": fcst,
        "baseline": baseline,
        "metrics": models["val_metrics"],
    }
