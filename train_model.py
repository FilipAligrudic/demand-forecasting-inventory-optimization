"""
Offline training script for Demand Forecasting & Inventory Optimization.

Purpose:
- trains the main LightGBM Quantile model for one or more Store/Product series
- creates a hybrid forecast by combining LightGBM + Holt-Winters
- saves model bundles, metrics and a manifest under models/


"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from src.data_processing import filter_series, load_sales_csv
from src.feature_engineering import build_features
from src.forecasting import (
    ensemble_forecast,
    evaluate_on_backtest,
    holt_winters_forecast,
    recursive_forecast_lgbm,
    rolling_origin_backtest,
    train_lightgbm,
)

from src.inventory_optimization import InventoryParams, recommend_order


ROOT = Path(__file__).resolve().parent
DEFAULT_DATA = ROOT / "data" / "rossmann_train.csv"
DEFAULT_OUTPUT_DIR = ROOT / "models"


def safe_slug(value: str) -> str:
    """Make Store/Product names safe for filenames."""
    text = str(value).strip()
    text = re.sub(r"[^A-Za-z0-9_.-]+", "_", text)
    return text.strip("_") or "unknown"


def json_default(obj: Any) -> str:
    """Fallback serializer for dates/numpy values in manifest.json."""
    return str(obj)


def relpath(path: Path) -> str:
    """Return path relative to project root when possible."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_dataset(data_path: Path) -> pd.DataFrame:
    """Load real sales dataset."""
    if not data_path.exists():
        raise FileNotFoundError(
            f"Nije pronađen dataset: {data_path}. "
            "Preuzmi Rossmann train.csv, preimenuj ga u rossmann_train.csv "
            "i ubaci ga u data folder."
        )
    return load_sales_csv(data_path)


def select_pairs(df: pd.DataFrame, store: str | None, product: str | None) -> list[tuple[str, str]]:
    """Return Store/Product pairs to train."""
    pairs_df = df[["Store", "Product"]].drop_duplicates().sort_values(["Store", "Product"])
    if store is not None:
        pairs_df = pairs_df[pairs_df["Store"] == str(store)]
    if product is not None:
        pairs_df = pairs_df[pairs_df["Product"] == str(product)]
    return [(str(r.Store), str(r.Product)) for r in pairs_df.itertuples(index=False)]


def train_one_series(
    df: pd.DataFrame,
    store: str,
    product: str,
    horizon: int,
    output_dir: Path,
    use_cv: bool,
) -> dict[str, Any]:
    """Train one Store/Product model and save a joblib bundle."""
    series = filter_series(df, store, product)
    if len(series) < 90:
        return {
            "Store": store,
            "Product": product,
            "status": "skipped",
            "reason": "Premalo podataka: potrebno je najmanje 90 dnevnih redova.",
            "rows": int(len(series)),
        }

    feat_df, features = build_features(series)
    models = train_lightgbm(feat_df, features=features)
    lgbm_forecast = recursive_forecast_lgbm(feat_df, models, features, horizon=horizon)
    holt_winters = holt_winters_forecast(feat_df, horizon=horizon)
    hybrid_forecast = ensemble_forecast(
        {"LightGBM": lgbm_forecast, "Holt-Winters": holt_winters},
        weights={"LightGBM": 0.6, "Holt-Winters": 0.4},
    )
    final_forecast = hybrid_forecast if hybrid_forecast is not None else lgbm_forecast

    eval_df = (
        rolling_origin_backtest(feat_df, features, horizon=horizon, n_splits=3)
        if use_cv
        else evaluate_on_backtest(feat_df, features, horizon=horizon)
    )

    params = InventoryParams()
    rec = recommend_order(final_forecast, series["Sales"], params, current_stock=0.0)

    best_model = None
    best_mape = None
    if not eval_df.empty and "MAPE" in eval_df.columns:
        best_row = eval_df.loc[eval_df["MAPE"].idxmin()]
        best_model = str(best_row["Model"])
        best_mape = float(best_row["MAPE"])

    bundle = {
        "project": "Demand Forecasting & Inventory Optimization",
        "trained_at": datetime.now().isoformat(timespec="seconds"),
        "model_type": "Hybrid Ensemble: LightGBM Quantile Regressor + Holt-Winters",
        "main_ml_model": "LightGBM Quantile Regressor",
        "store": store,
        "product": product,
        "horizon_days": horizon,
        "last_history_date": series["Date"].max(),
        "features": features,
        "lightgbm_models": models,
        "lgbm_forecast": lgbm_forecast,
        "hybrid_forecast": final_forecast,
        "evaluation": eval_df,
        "inventory_recommendation": rec.to_dict(),
        "notes": (
            "Customers is intentionally excluded from features to avoid data leakage. "
            "Future Promo/Holiday values are treated as planned scenario inputs."
        ),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / f"model_{safe_slug(store)}__{safe_slug(product)}.joblib"
    joblib.dump(bundle, model_path)

    forecast_path = output_dir / f"forecast_{safe_slug(store)}__{safe_slug(product)}.csv"
    final_forecast.to_csv(forecast_path, index=False)

    metrics_path = None
    if not eval_df.empty:
        metrics_path = output_dir / f"metrics_{safe_slug(store)}__{safe_slug(product)}.csv"
        eval_df.to_csv(metrics_path, index=False)

    return {
        "Store": store,
        "Product": product,
        "status": "trained",
        "rows": int(len(series)),
        "features": int(len(features)),
        "horizon_days": horizon,
        "best_model": best_model,
        "best_mape": best_mape,
        "lgbm_val_mape": float(models["val_metrics"].get("MAPE", 0.0)),
        "recommended_order_qty": float(rec.recommended_order_qty),
        "model_path": relpath(model_path),
        "forecast_path": relpath(forecast_path),
        "metrics_path": relpath(metrics_path) if metrics_path else None,
    }


def run_training(args: argparse.Namespace) -> pd.DataFrame:
    data_path = Path(args.data)
    if not data_path.is_absolute():
        data_path = ROOT / data_path

    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir

    df = load_dataset(data_path)
    pairs = select_pairs(df, args.store, args.product)
    if args.max_series and args.max_series > 0:
        pairs = pairs[: args.max_series]

    if not pairs:
        raise ValueError("Nema Store/Product parova za trening. Provjeri --store, --product ili ulazni CSV.")

    rows: list[dict[str, Any]] = []
    for idx, (store, product) in enumerate(pairs, start=1):
        print(f"[{idx}/{len(pairs)}] Training {store} / {product} ...")
        try:
            rows.append(train_one_series(df, store, product, args.horizon, output_dir, args.cv))
        except Exception as exc:
            rows.append({
                "Store": store,
                "Product": product,
                "status": "failed",
                "reason": str(exc),
            })
            print(f"    ERROR: {exc}")

    summary = pd.DataFrame(rows)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "training_summary.csv"
    manifest_path = output_dir / "manifest.json"

    summary.to_csv(summary_path, index=False)
    manifest = {
        "trained_at": datetime.now().isoformat(timespec="seconds"),
        "data_path": relpath(data_path),
        "output_dir": relpath(output_dir),
        "horizon_days": args.horizon,
        "evaluation": "rolling-origin CV" if args.cv else "single backtest",
        "n_pairs_requested": len(pairs),
        "n_trained": int((summary["status"] == "trained").sum()) if "status" in summary else 0,
        "n_skipped_or_failed": int((summary["status"] != "trained").sum()) if "status" in summary else 0,
        "summary_csv": relpath(summary_path),
        "results": rows,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, default=json_default), encoding="utf-8")

    print("\nTraining completed.")
    print(f"Summary:  {summary_path}")
    print(f"Manifest: {manifest_path}")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train LightGBM hybrid forecasting models.")
    parser.add_argument("--data", default=relpath(DEFAULT_DATA), help="CSV dataset path.")
    parser.add_argument("--output-dir", default=relpath(DEFAULT_OUTPUT_DIR), help="Output folder for models/metrics.")
    parser.add_argument("--store", default=None, help="Train only this Store.")
    parser.add_argument("--product", default=None, help="Train only this Product/SKU.")
    parser.add_argument("--horizon", type=int, default=28, help="Forecast horizon in days.")
    parser.add_argument("--max-series", type=int, default=0, help="Limit number of Store/Product pairs; 0 means all.")
    parser.add_argument("--cv", action="store_true", help="Use rolling-origin CV instead of a single backtest.")
    return parser.parse_args()


if __name__ == "__main__":
    run_training(parse_args())
