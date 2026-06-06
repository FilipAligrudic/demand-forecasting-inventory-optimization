"""
SHAP objašnjenja za LightGBM forecasting model.

Vraća:
- global feature importance (mean |SHAP|)
- lokalna objašnjenja za jedan red (pojedinačnu prognozu)
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import shap


def compute_shap_values(model, X: pd.DataFrame) -> shap.Explanation:
    """SHAP TreeExplainer za LightGBM."""
    explainer = shap.TreeExplainer(model)
    values = explainer(X)
    return values


def global_importance(model, X: pd.DataFrame, top_k: int = 12) -> pd.DataFrame:
    """Globalna važnost feature-a (mean apsolutni SHAP)."""
    shap_values = compute_shap_values(model, X)
    arr = np.abs(shap_values.values).mean(axis=0)
    df = pd.DataFrame({"feature": X.columns, "mean_abs_shap": arr})
    df = df.sort_values("mean_abs_shap", ascending=False).head(top_k).reset_index(drop=True)
    return df


def explain_row(model, X: pd.DataFrame, row_idx: int = -1, top_k: int = 8) -> pd.DataFrame:
    """Lokalno objašnjenje za jedan red — top_k feature-a sa najvećim doprinosom."""
    shap_values = compute_shap_values(model, X)
    row = shap_values.values[row_idx]
    df = pd.DataFrame(
        {
            "feature": X.columns,
            "value": X.iloc[row_idx].values,
            "shap": row,
        }
    )
    df["abs_shap"] = df["shap"].abs()
    df = df.sort_values("abs_shap", ascending=False).head(top_k).reset_index(drop=True)
    df["direction"] = np.where(df["shap"] >= 0, "↑ povećava prognozu", "↓ smanjuje prognozu")
    return df.drop(columns="abs_shap")


def humanize_feature(name: str) -> str:
    """Mapa imena feature-a u kratki opis za dashboard."""
    mapping = {
        "dayofweek": "Dan u sedmici",
        "day": "Dan u mjesecu",
        "month": "Mjesec",
        "quarter": "Kvartal",
        "weekofyear": "Sedmica u godini",
        "year": "Godina",
        "is_weekend": "Vikend",
        "is_month_start": "Početak mjeseca",
        "is_month_end": "Kraj mjeseca",
        "dow_sin": "Dan u sedmici (sin)",
        "dow_cos": "Dan u sedmici (cos)",
        "month_sin": "Mjesec (sin)",
        "month_cos": "Mjesec (cos)",
        "Promo": "Promocija",
        "SchoolHoliday": "Školski praznik",
        "StateHoliday_flag": "Državni praznik",
        "Price": "Cijena",
        "Customers": "Broj kupaca",
    }
    if name in mapping:
        return mapping[name]
    if name.startswith("lag_"):
        return f"Prodaja prije {name.split('_')[1]} dana"
    if name.startswith("rmean_"):
        return f"Prosjek prodaje (zadnjih {name.split('_')[1]} dana)"
    if name.startswith("rstd_"):
        return f"Varijabilnost prodaje (zadnjih {name.split('_')[1]} dana)"
    return name
