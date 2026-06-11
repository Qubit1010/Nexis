# AI-Driven Financial Fraud Detection, Risk Scoring & Explainable Decision Support

**Complex Computing Problem (CCP)** — Data Science & Visualization Lab, BS Artificial Intelligence (7th Semester), Iqra University.

An end-to-end fraud analytics framework on mobile-money transaction data (PaySim schema): EDA → feature engineering → imbalance handling → supervised + deep models → explainability (SHAP/LIME) → a dynamic risk-scoring engine → unsupervised anomaly discovery → a 4-view BI dashboard, plus a written report covering business understanding, scalability, a literature review, and critical evaluation.

## Deliverables

| File | Covers |
|------|--------|
| `notebooks/fraud_detection_ccp.ipynb` | **Tasks 2-9** (implementation, runnable top-to-bottom) |
| `report/report.pdf` | **Tasks 1, 10, 11, 12** (business understanding, scalability, literature review, critical evaluation) |
| `outputs/figures/` | All generated figures (EDA, model eval, SHAP/LIME, dashboard) |
| `models/` | Persisted trained models |

## Task coverage

1. Business Understanding — `report/`
2. EDA — notebook
3. Feature Engineering (behavioral features, scaling, encoding, selection, PCA) — notebook
4. Imbalanced Data (RandomOver/Under, SMOTE, ADASYN, hybrid) — notebook
5. ML + DL Models (LogReg, Decision Tree, Random Forest, XGBoost, ANN, Autoencoder) — notebook
6. Explainable AI (SHAP + LIME) — notebook
7. Fraud Risk Scoring (Low/Medium/High/Critical) — notebook
8. Unsupervised Discovery (Isolation Forest, LOF, DBSCAN) — notebook
9. BI Dashboard (Executive / Operational / Analytical / Predictive) — notebook
10. Scalability & Big Data — `report/`
11. Literature Review (2023-2026) — `report/`
12. Critical Evaluation — `report/`

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
# 1. fetch data (real mirror -> synthetic fallback) into data/raw/
python src/data_loader.py

# 2. develop / run the full pipeline as a script (debug-friendly)
python src/pipeline.py

# 3. assemble + execute the notebook (bakes outputs in)
python build_notebook.py

# 4. render the written report to PDF
python src/md_to_pdf.py
```

## Notes on the lean stack

- **No TensorFlow.** The ANN and Autoencoder (Task 5) are implemented with scikit-learn's `MLPClassifier` and `MLPRegressor` (a reconstruction autoencoder trained on legitimate transactions only). This keeps the environment light while remaining a faithful neural-network implementation; the substitution is documented in the notebook.
- **Data source.** The loader tries public PaySim mirrors first; if the download is unavailable it generates a reproducible PaySim-schema synthetic dataset (fraud only in TRANSFER/CASH_OUT, with the balance-error signal preserved). The active source is printed and labelled in the notebook.
- **Compute.** Tree models train on the full working set; computationally heavy steps (deep models, SHAP, LIME, DBSCAN/LOF) run on a stratified subsample by necessity — documented in-notebook.
