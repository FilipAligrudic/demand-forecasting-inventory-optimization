"""
Detekcija anomalija u prodaji.

Dva pristupa:
- z-score na rolling prozoru (jednostavno, brzo)
- Isolation Forest na (Sales, dayofweek, month) feature-ima

Vraća isti DataFrame kao ulaz + bool kolonu `is_anomaly` i `anomaly_score`.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


def zscore_anomalies(df: pd.DataFrame, target: str = "Sales", window: int = 28, threshold: float = 3.0) -> pd.DataFrame:
    """Rolling z-score — anomalija ako |z| > threshold."""
    out = df.copy()
    s = out[target]
    rolling_mean = s.rolling(window=window, min_periods=7).mean()
    rolling_std = s.rolling(window=window, min_periods=7).std().replace(0, np.nan)
    z = (s - rolling_mean) / rolling_std
    out["anomaly_score"] = z.fillna(0).abs()
    out["is_anomaly"] = out["anomaly_score"] > threshold
    return out


def isolation_forest_anomalies(
    df: pd.DataFrame,
    target: str = "Sales",
    contamination: float = 0.03,
    extra_features: list[str] | None = None,
) -> pd.DataFrame:
    """Isolation Forest sa par feature-a (target + kalendar)."""
    out = df.copy()
    feats = [target]
    for c in ("dayofweek", "month", "is_weekend"):
        if c in out.columns:
            feats.append(c)
    if extra_features:
        feats.extend([c for c in extra_features if c in out.columns])

    X = out[feats].ffill().fillna(0)
    if len(X) < 30:
        out["is_anomaly"] = False
        out["anomaly_score"] = 0.0
        return out

    iso = IsolationForest(contamination=contamination, random_state=42, n_estimators=200)
    iso.fit(X)
    out["anomaly_score"] = -iso.score_samples(X)  # veći score = veća anomalija
    out["is_anomaly"] = iso.predict(X) == -1
    return out


def detect(
    df: pd.DataFrame,
    method: str = "isolation_forest",
    target: str = "Sales",
    **kwargs,
) -> pd.DataFrame:
    """Glavna funkcija — bira metodu."""
    if method == "zscore":
        return zscore_anomalies(df, target=target, **kwargs)
    return isolation_forest_anomalies(df, target=target, **kwargs)
