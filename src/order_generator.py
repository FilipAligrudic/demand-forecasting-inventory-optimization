"""
Generator narudžbenica.

Spaja forecast + inventory preporuke u jedan tabelarni izvještaj
spreman za export (CSV / Excel).
"""

from __future__ import annotations

import io
from datetime import datetime
from pathlib import Path

import pandas as pd

from .inventory_optimization import InventoryParams, recommend_order


def build_purchase_order(
    df: pd.DataFrame,
    forecasts_by_pair: dict[tuple[str, str], pd.DataFrame],
    params: InventoryParams,
    current_stock_by_pair: dict[tuple[str, str], float] | None = None,
    unit_cost_by_pair: dict[tuple[str, str], float] | None = None,
) -> pd.DataFrame:
    """Napravi narudžbenicu za sve (Store, Product) parove sa forecastom.

    Vraća DataFrame sa kolonama:
      Store, Product, Forecast (horizon), Safety stock, Reorder point,
      Recommended order qty, Unit cost, Expected cost
    """
    current_stock_by_pair = current_stock_by_pair or {}
    unit_cost_by_pair = unit_cost_by_pair or {}

    rows = []
    for (store, product), forecast in forecasts_by_pair.items():
        historical = df[(df["Store"] == store) & (df["Product"] == product)]["Sales"]
        rec = recommend_order(
            forecast=forecast,
            historical_daily_sales=historical,
            params=params,
            current_stock=current_stock_by_pair.get((store, product), 0.0),
        )
        unit_cost = unit_cost_by_pair.get((store, product), 0.0)
        if unit_cost == 0.0 and "Price" in df.columns:
            avg_price = df[(df["Store"] == store) & (df["Product"] == product)]["Price"].mean()
            unit_cost = float(avg_price) if pd.notna(avg_price) else 0.0

        rows.append(
            {
                "Store": store,
                "Product": product,
                "Forecast_horizon_days": len(forecast),
                "Forecast_demand": rec.forecast_horizon_demand,
                "Mean_daily_demand": rec.mean_daily_demand,
                "Safety_stock": rec.safety_stock,
                "Reorder_point": rec.reorder_point,
                "EOQ": rec.eoq,
                "Recommended_order_qty": rec.recommended_order_qty,
                "Service_level": params.service_level,
                "Lead_time_days": params.lead_time_days,
                "Unit_cost": round(unit_cost, 2),
                "Expected_total_cost": round(unit_cost * rec.recommended_order_qty, 2),
                "Generated_at": datetime.now().isoformat(timespec="seconds"),
            }
        )

    return pd.DataFrame(rows)


def to_excel_bytes(df: pd.DataFrame, sheet_name: str = "PurchaseOrder") -> bytes:
    """Konvertuj DataFrame u Excel bajtove za Streamlit download_button."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return buf.getvalue()


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def save_to_outputs(df: pd.DataFrame, out_dir: str | Path = "outputs") -> Path:
    """Snimi narudžbenicu sa timestamp imenom."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = out_dir / f"purchase_order_{stamp}.csv"
    df.to_csv(path, index=False)
    return path
