"""Sklearn preprocessing pipeline for the 41-feature schema."""

from __future__ import annotations

import numpy as np
import pandas as pd

from features.extractor import FEATURE_NAMES, FEATURE_SCHEMA


def features_to_dataframe(features: dict) -> pd.DataFrame:
    """Convert a single feature dict to a 1-row DataFrame in canonical order."""
    return pd.DataFrame([{name: features.get(name) for name in FEATURE_NAMES}])


def features_batch_to_dataframe(rows: list[dict]) -> pd.DataFrame:
    """Convert a list of feature dicts to a DataFrame."""
    return pd.DataFrame([{name: row.get(name) for name in FEATURE_NAMES} for row in rows])


def coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce all columns to numeric. Bools become 0/1, None becomes NaN.

    XGBoost handles NaN natively — no imputation needed.
    """
    out = df.copy()
    for col in out.columns:
        if FEATURE_SCHEMA[col]["type"] == "bool":
            out[col] = out[col].apply(lambda v: 1 if v in (1, True) else (0 if v in (0, False) else np.nan))
        out[col] = pd.to_numeric(out[col], errors="coerce")
    return out
