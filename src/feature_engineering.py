"""
Kreiranje feature-a za forecasting modele.

Generiše kalendarske, lag i rolling feature-e za jednu vremensku seriju
(Store + Product). Vraća dva DataFrame-a: cijela tabela sa feature-ima
i lista feature kolona koje se prosljeđuju modelu.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


LAG_DAYS = [1, 2, 3, 7, 14, 28]
ROLLING_WINDOWS = [7, 14, 28]


def add_calendar_features(df: pd.DataFrame, date_col: str = "Date") -> pd.DataFrame:
    """Dodaj kalendarske feature: dan u sedmici, mjesec, vikend, kvartal..."""
    out = df.copy()
    d = out[date_col]
    out["dayofweek"] = d.dt.dayofweek
    out["day"] = d.dt.day
    out["month"] = d.dt.month
    out["quarter"] = d.dt.quarter
    out["weekofyear"] = d.dt.isocalendar().week.astype(int)
    out["year"] = d.dt.year
    out["is_weekend"] = (out["dayofweek"] >= 5).astype(int)
    out["is_month_start"] = d.dt.is_month_start.astype(int)
    out["is_month_end"] = d.dt.is_month_end.astype(int)
    # ciklični enkodi za sezonu
    out["dow_sin"] = np.sin(2 * np.pi * out["dayofweek"] / 7)
    out["dow_cos"] = np.cos(2 * np.pi * out["dayofweek"] / 7)
    out["month_sin"] = np.sin(2 * np.pi * out["month"] / 12)
    out["month_cos"] = np.cos(2 * np.pi * out["month"] / 12)
    return out


def add_lag_features(df: pd.DataFrame, target: str = "Sales", lags=LAG_DAYS) -> pd.DataFrame:
    """Dodaj lag feature-e na cilj. Pretpostavlja sortirano po datumu."""
    out = df.copy()
    for lag in lags:
        out[f"lag_{lag}"] = out[target].shift(lag)
    return out


def add_rolling_features(df: pd.DataFrame, target: str = "Sales", windows=ROLLING_WINDOWS) -> pd.DataFrame:
    """Rolling mean i std (shift(1) da izbjegnemo leakage)."""
    out = df.copy()
    shifted = out[target].shift(1)
    for w in windows:
        out[f"rmean_{w}"] = shifted.rolling(window=w, min_periods=max(2, w // 2)).mean()
        out[f"rstd_{w}"] = shifted.rolling(window=w, min_periods=max(2, w // 2)).std()
    return out


def build_features(df: pd.DataFrame, target: str = "Sales") -> tuple[pd.DataFrame, list[str]]:
    """Glavna funkcija — vraća (df_sa_feature-ima, lista_imena_feature-a)."""
    if df.empty:
        return df, []

    df = df.sort_values("Date").reset_index(drop=True)
    df = add_calendar_features(df)
    df = add_lag_features(df, target=target)
    df = add_rolling_features(df, target=target)

    # Opcioni egzogeni feature-i koji su POZNATI (ili planirani) za buduće dane.
    # NAPOMENA: "Customers" se NAMJERNO izostavlja — to je istovremena (same-day)
    # informacija koja nije poznata u trenutku prognoze; uključivanje bi bilo
    # curenje informacija (leakage) i ruši rekurzivni forecast.
    extra = []
    for col in ("Promo", "SchoolHoliday", "Price"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            extra.append(col)

    if "StateHoliday" in df.columns:
        df["StateHoliday_flag"] = (df["StateHoliday"].astype(str) != "0").astype(int)
        extra.append("StateHoliday_flag")

    base_features = [
        "dayofweek",
        "day",
        "month",
        "quarter",
        "weekofyear",
        "year",
        "is_weekend",
        "is_month_start",
        "is_month_end",
        "dow_sin",
        "dow_cos",
        "month_sin",
        "month_cos",
    ]
    lag_features = [c for c in df.columns if c.startswith("lag_")]
    roll_features = [c for c in df.columns if c.startswith("rmean_") or c.startswith("rstd_")]

    features = base_features + lag_features + roll_features + extra

    # drop redove gdje je target NaN ili gdje najduži lag nije pun
    longest_lag = max(LAG_DAYS + ROLLING_WINDOWS)
    df = df.iloc[longest_lag:].reset_index(drop=True)

    return df, features


def make_future_frame(history: pd.DataFrame, horizon: int) -> pd.DataFrame:
    """Pripremi prazne redove za buduće datume — bez Sales vrijednosti."""
    last_date = history["Date"].max()
    future_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=horizon, freq="D")
    template = history.iloc[-1].copy()
    rows = []
    for d in future_dates:
        row = {col: template[col] for col in history.columns if col not in ("Date", "Sales")}
        row["Date"] = d
        row["Sales"] = np.nan
        rows.append(row)
    return pd.DataFrame(rows)
