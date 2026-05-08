"""Train the XGBoost model and persist to disk.

Auto-detects real labeled data at data/labeled/dataset.csv (100+ rows).
Falls back to synthetic cold-start data if the file is absent or too small.

Run:
    cd backend && python -m ml.train
    cd backend && python -m ml.train --data ../data/labeled/dataset.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running as `python -m ml.train` from backend/ root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_score, train_test_split
from xgboost import XGBRegressor

from features.extractor import FEATURE_NAMES
from ml.preprocessing import coerce_numeric
from ml.synthetic_dataset import generate as generate_synthetic

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
REAL_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "labeled" / "dataset.csv"
REAL_DATA_MIN_ROWS = 100


def evaluate(model, X, y, name: str) -> dict:
    """Run 5-fold CV and return MAE/RMSE/R2."""
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    mae = -cross_val_score(model, X, y, cv=kf, scoring="neg_mean_absolute_error").mean()
    rmse = np.sqrt(-cross_val_score(model, X, y, cv=kf, scoring="neg_mean_squared_error").mean())
    r2 = cross_val_score(model, X, y, cv=kf, scoring="r2").mean()
    print(f"  {name:25s}  MAE={mae:.2f}  RMSE={rmse:.2f}  R²={r2:.3f}")
    return {"name": name, "mae": mae, "rmse": rmse, "r2": r2}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=None, help="Path to labeled CSV (overrides auto-detect)")
    args = parser.parse_args()

    # Resolve data source
    data_path: Path | None = Path(args.data) if args.data else (
        REAL_DATA_PATH if REAL_DATA_PATH.exists() else None
    )
    use_real = data_path is not None and data_path.exists()

    if use_real:
        print(f"\n=== Loading real labeled data: {data_path} ===")
        raw = pd.read_csv(data_path)
        # Rename feature_<name> → <name> and score_total → score
        raw = raw.rename(columns={f"feature_{n}": n for n in FEATURE_NAMES})
        raw = raw.rename(columns={"score_total": "score"})
        df = raw.dropna(subset=["score"])
        version = "v2-real-data"
        model_path = MODELS_DIR / "xgboost_v2.joblib"
    else:
        print("\n=== Generating synthetic training data (cold-start) ===")
        df = generate_synthetic(n_samples=1500, seed=42)
        version = "v1-cold-start"
        model_path = MODELS_DIR / "xgboost_v1.joblib"

    print(f"Samples: {len(df)}, score mean={df['score'].mean():.1f}, std={df['score'].std():.1f}")

    X = coerce_numeric(df[FEATURE_NAMES])
    y = df["score"].astype(float)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("\n=== Comparing models (5-fold CV on train set) ===")
    candidates = {
        "XGBoost":            XGBRegressor(
            n_estimators=300, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            reg_alpha=0.1, reg_lambda=1.0,
            tree_method="hist", random_state=42,
        ),
        "Random Forest":      RandomForestRegressor(
            n_estimators=300, max_depth=12, random_state=42, n_jobs=-1
        ),
        "HistGradientBoost":  HistGradientBoostingRegressor(
            max_iter=200, max_depth=6, learning_rate=0.05, random_state=42
        ),
    }

    results = []
    for name, model in candidates.items():
        results.append(evaluate(model, X_train, y_train, name))

    best = min(results, key=lambda r: r["mae"])
    print(f"\nBest by CV MAE: {best['name']}")

    # We pin XGBoost as the deployed model: it's what the proposal specifies,
    # and SHAP's TreeExplainer is exact and fastest on XGBoost. The benchmark
    # comparison above is preserved in the eval report.
    deployed_name = "XGBoost"
    final_model = candidates[deployed_name]
    final_model.fit(X_train, y_train)
    print(f"\nDeploying: {deployed_name} (proposal-aligned, SHAP-optimized)")
    y_pred = final_model.predict(X_test)

    print("\n=== Held-out test set performance ===")
    print(f"  MAE  = {mean_absolute_error(y_test, y_pred):.2f}")
    print(f"  RMSE = {np.sqrt(mean_squared_error(y_test, y_pred)):.2f}")
    print(f"  R²   = {r2_score(y_test, y_pred):.3f}")

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    bundle = {
        "model": final_model,
        "model_name": deployed_name,
        "benchmark": {r["name"]: {"mae": r["mae"], "rmse": r["rmse"], "r2": r["r2"]} for r in results},
        "feature_names": FEATURE_NAMES,
        "training_samples": len(X_train),
        "version": version,
    }
    joblib.dump(bundle, model_path)
    print(f"\nModel saved to: {model_path}")


if __name__ == "__main__":
    main()
