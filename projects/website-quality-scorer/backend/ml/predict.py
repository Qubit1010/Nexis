"""Inference + SHAP explainability."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

import joblib
import numpy as np
import shap

from features.extractor import FEATURE_NAMES, FEATURE_SCHEMA, features_by_dimension
from ml.preprocessing import coerce_numeric, features_to_dataframe

_MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
_V2 = _MODELS_DIR / "xgboost_v2.joblib"
_V1 = _MODELS_DIR / "xgboost_v1.joblib"
DEFAULT_MODEL_PATH = _V2 if _V2.exists() else _V1


def _model_path() -> Path:
    return Path(os.environ.get("MODEL_PATH") or DEFAULT_MODEL_PATH)


@lru_cache(maxsize=1)
def _load_model_bundle() -> dict:
    path = _model_path()
    if not path.exists():
        raise FileNotFoundError(
            f"Model not found at {path}. Run `python -m ml.train` to create it."
        )
    return joblib.load(path)


@lru_cache(maxsize=1)
def _explainer():
    bundle = _load_model_bundle()
    return shap.TreeExplainer(bundle["model"])


def _tier(score: float) -> str:
    if score < 41:
        return "Poor"
    if score < 61:
        return "Average"
    if score < 81:
        return "Good"
    return "Excellent"


def _dimension_subscores(shap_per_feature: dict[str, float]) -> dict[str, float]:
    """Map per-feature SHAP contributions to 4 sub-scores in [0, 25].

    Each dimension's SHAP sum is normalized via tanh-bounded mapping centered at 0,
    then scaled to a 0-25 range with 12.5 as the neutral midpoint.
    """
    subscores = {}
    for dim in ("ux", "content", "technical", "trust"):
        feats = features_by_dimension(dim)
        total = sum(shap_per_feature.get(f, 0.0) for f in feats)
        # Squash to [-1, 1], scale to [0, 25] with 12.5 center
        squashed = np.tanh(total / 10.0)
        subscores[dim] = round(12.5 + squashed * 12.5, 2)
    return subscores


def predict_score(features: dict, top_n_shap: int = 12) -> dict:
    """Run inference + SHAP. Returns score, tier, sub-scores, top SHAP values."""
    bundle = _load_model_bundle()
    model = bundle["model"]

    df = coerce_numeric(features_to_dataframe(features))
    raw_score = float(model.predict(df)[0])
    score = round(max(0.0, min(100.0, raw_score)), 2)

    explainer = _explainer()
    shap_values_arr = explainer.shap_values(df)
    shap_row = shap_values_arr[0] if shap_values_arr.ndim == 2 else shap_values_arr

    shap_per_feature = {name: float(shap_row[i]) for i, name in enumerate(FEATURE_NAMES)}

    # Sort by absolute magnitude
    sorted_shap = sorted(shap_per_feature.items(), key=lambda kv: abs(kv[1]), reverse=True)
    top_shap = [
        {
            "feature": name,
            "shap_value": round(value, 4),
            "raw_value": features.get(name),
            "dimension": FEATURE_SCHEMA[name]["dim"],
        }
        for name, value in sorted_shap[:top_n_shap]
    ]

    return {
        "score": score,
        "tier": _tier(score),
        "sub_scores": _dimension_subscores(shap_per_feature),
        "shap_values": top_shap,
        "model_version": bundle.get("version", "unknown"),
    }
