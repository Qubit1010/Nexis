# Website Quality & Conversion Gap Scorer

ML-driven framework for automated website evaluation, multi-dimensional scoring, and explainable recommendations.

**Course:** Machine Learning AIN-373, Iqra University, Spring 2026
**Team:** Aleem Ul Hassan (42490), Abdul Hadi Minhas (37520)

---

## Overview

A full-stack ML application that:
1. Accepts any website URL
2. Crawls and extracts ~40 quality features (UX, content, technical, trust)
3. Scores the website 0-100 via XGBoost
4. Explains the score with SHAP-based per-feature contributions
5. Generates ranked, actionable recommendations

## Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16 + TypeScript + Tailwind + shadcn/ui + recharts |
| Backend | FastAPI (Python 3.11) |
| ML | XGBoost + scikit-learn + SHAP |
| Crawling | Firecrawl + BeautifulSoup4 + Google PageSpeed Insights API |

## Folder Structure

```
backend/      FastAPI server, ML pipeline, crawler, feature extraction
frontend/     Next.js dashboard
notebooks/    Jupyter notebooks (EDA, training, SHAP analysis)
data/         Labeled dataset (CSV)
docs/         Project proposal (PDF/HTML), architecture docs
scripts/      Dataset labeling and bulk crawl utilities
```

## Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # fill in FIRECRAWL_API_KEY, PAGESPEED_API_KEY
python ml/train.py    # trains and saves models/xgboost_v1.joblib
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
cp .env.local.example .env.local  # set BACKEND_URL
npm run dev
```

Open `http://localhost:3000`.

## Demo

Paste any URL into the input field. Within 30 seconds:
- Composite score (0-100) shown as a circular gauge
- 4 dimension sub-scores (UX, Content, Technical, Trust)
- SHAP waterfall showing what drove the score up or down
- Ranked recommendations tied to specific feature gaps

## ML Approach

**Primary model:** XGBoost regression. Predicts composite score 0-100 from 40 engineered features. Tier classification (Poor/Average/Good/Excellent) derived from score thresholds.

**Explainability:** SHAP TreeExplainer computes exact Shapley values per prediction. Top negative contributors map to recommendation templates.

**Cold-start:** Initial v1 model trained on heuristic-bootstrapped synthetic dataset. Retrain on real labeled data once 100+ sites are annotated.

## Project Proposal

See [`docs/proposal.html`](docs/proposal.html) for the full course proposal (open in Chrome → Ctrl+P → Save as PDF).
