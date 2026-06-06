"""
Klasične supply-chain formule za optimizaciju zaliha.

Sve funkcije su čiste — bez side-effecta — kako bi se lako koristile u
Streamlit what-if simulaciji.

Notacija:
- D     : godišnja potražnja (units/year)
- S     : trošak po jednoj narudžbi (ordering cost)
- H     : trošak držanja jedne jedinice godišnje (holding cost)
- L     : lead time (dani)
- σ_d   : standardna devijacija dnevne potražnje
- z     : faktor service level-a (npr. 1.65 za 95%)
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

import numpy as np
import pandas as pd
from scipy.stats import norm


# ---------------------------------------------------------------------------
# Service level → z
# ---------------------------------------------------------------------------

def service_level_z(service_level: float) -> float:
    """Pretvori service level (npr. 0.95) u z-vrijednost iz normalne raspodjele."""
    service_level = float(np.clip(service_level, 0.5, 0.9999))
    return float(norm.ppf(service_level))


# ---------------------------------------------------------------------------
# Core formule
# ---------------------------------------------------------------------------

def economic_order_quantity(annual_demand: float, ordering_cost: float, holding_cost: float) -> float:
    """EOQ = sqrt(2*D*S / H)."""
    if annual_demand <= 0 or holding_cost <= 0:
        return 0.0
    return float(sqrt(2.0 * annual_demand * ordering_cost / holding_cost))


def safety_stock(std_daily_demand: float, lead_time_days: float, service_level: float) -> float:
    """SS = z * σ_d * sqrt(L)."""
    z = service_level_z(service_level)
    return float(z * std_daily_demand * sqrt(max(0.0, lead_time_days)))


def reorder_point(mean_daily_demand: float, lead_time_days: float, ss: float) -> float:
    """ROP = D_mean * L + SS."""
    return float(mean_daily_demand * lead_time_days + ss)


def total_inventory_cost(
    order_qty: float, annual_demand: float, ordering_cost: float, holding_cost: float, ss: float
) -> float:
    """Ukupni godišnji trošak: ordering + holding (cycle + safety)."""
    if order_qty <= 0:
        return float("inf")
    ordering = (annual_demand / order_qty) * ordering_cost
    holding = (order_qty / 2 + ss) * holding_cost
    return float(ordering + holding)


# ---------------------------------------------------------------------------
# High-level API
# ---------------------------------------------------------------------------

@dataclass
class InventoryParams:
    ordering_cost: float = 50.0       # po narudžbi (€)
    holding_cost: float = 2.0          # po jedinici godišnje (€)
    stockout_cost: float = 5.0         # po jedinici izgubljene prodaje (€)
    lead_time_days: float = 7.0
    service_level: float = 0.95
    review_period_days: int = 7        # koliko često se planira


@dataclass
class InventoryRecommendation:
    eoq: float
    safety_stock: float
    reorder_point: float
    recommended_order_qty: float
    expected_annual_cost: float
    service_level_z: float
    forecast_horizon_demand: float
    mean_daily_demand: float
    std_daily_demand: float
    annual_demand: float

    def to_dict(self) -> dict:
        return self.__dict__


def recommend_order(
    forecast: pd.DataFrame,
    historical_daily_sales: pd.Series,
    params: InventoryParams,
    current_stock: float = 0.0,
) -> InventoryRecommendation:
    """Glavna funkcija za dashboard.

    - forecast: DataFrame sa kolonama Date, yhat (dnevna predviđena potražnja)
    - historical_daily_sales: pd.Series prošlih dnevnih prodaja (za std)
    - params: InventoryParams
    - current_stock: trenutna količina na lageru
    """
    horizon = len(forecast)
    horizon_demand = float(forecast["yhat"].sum())
    mean_daily = float(forecast["yhat"].mean()) if horizon > 0 else float(historical_daily_sales.mean())
    _std = historical_daily_sales.tail(90).std()
    if pd.isna(_std) or _std == 0.0:
        _std = forecast["yhat"].std()
    std_daily = float(_std) if pd.notna(_std) else 0.0

    # Godišnja potražnja — projekcija na 365 dana
    annual_demand = mean_daily * 365.0

    eoq = economic_order_quantity(annual_demand, params.ordering_cost, params.holding_cost)
    ss = safety_stock(std_daily, params.lead_time_days, params.service_level)
    rop = reorder_point(mean_daily, params.lead_time_days, ss)

    # Preporučena količina: prilagođena horizonu planiranja
    # Tipično: pokrij review_period + lead_time + safety stock, ali ne manje od EOQ
    cover_days = params.review_period_days + params.lead_time_days
    coverage_qty = mean_daily * cover_days + ss
    recommended = max(eoq, coverage_qty - current_stock)
    recommended = max(0.0, recommended)

    expected_cost = total_inventory_cost(
        order_qty=recommended if recommended > 0 else eoq,
        annual_demand=annual_demand,
        ordering_cost=params.ordering_cost,
        holding_cost=params.holding_cost,
        ss=ss,
    )

    return InventoryRecommendation(
        eoq=round(eoq, 2),
        safety_stock=round(ss, 2),
        reorder_point=round(rop, 2),
        recommended_order_qty=round(recommended, 2),
        expected_annual_cost=round(expected_cost, 2),
        service_level_z=round(service_level_z(params.service_level), 3),
        forecast_horizon_demand=round(horizon_demand, 2),
        mean_daily_demand=round(mean_daily, 2),
        std_daily_demand=round(std_daily, 2),
        annual_demand=round(annual_demand, 2),
    )


def sensitivity_table(
    base_params: InventoryParams,
    forecast: pd.DataFrame,
    historical_daily_sales: pd.Series,
    vary: str = "service_level",
    values=None,
) -> pd.DataFrame:
    """Brza tabela kako se preporuka mijenja sa parametrom — za what-if grafikon."""
    if values is None:
        if vary == "service_level":
            values = [0.80, 0.85, 0.90, 0.95, 0.975, 0.99]
        elif vary == "lead_time_days":
            values = [3, 5, 7, 10, 14, 21]
        else:
            values = [0.5, 1.0, 2.0, 4.0, 8.0]

    rows = []
    for v in values:
        p = InventoryParams(**base_params.__dict__)
        setattr(p, vary, v)
        rec = recommend_order(forecast, historical_daily_sales, p)
        rows.append({vary: v, **rec.to_dict()})
    return pd.DataFrame(rows)
