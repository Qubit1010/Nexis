# Website Quality & Conversion Gap Scorer — Architecture Notes

## What This Is

ML course project (Machine Learning AIN-373, Iqra University, Spring 2026). Full-stack web app that scores any website URL 0-100 using XGBoost + SHAP for explainability.

## Three-Tier Architecture

```
Next.js Frontend (port 3000)
    ↓ POST /api/proxy/score { url }
Next.js API Proxy Route (avoids CORS)
    ↓ POST http://localhost:8000/score
FastAPI Backend (port 8000)
    ↓
Crawler (Firecrawl) → Feature Extractor (~40 features) → XGBoost → SHAP TreeExplainer
    ↓
JSON: { score, sub_scores, shap_values, recommendations }
```

## Key Modules

| Path | Responsibility |
|---|---|
| `backend/main.py` | FastAPI app, CORS, route registration |
| `backend/api/score_endpoint.py` | POST /score orchestration |
| `backend/crawler/firecrawl_client.py` | URL → HTML + markdown (lifted from `.claude/skills/website-audit-system/scripts/crawl_site.py`) |
| `backend/crawler/pagespeed.py` | Google PageSpeed API → Core Web Vitals (lifted from website-audit-system) |
| `backend/features/extractor.py` | Master feature extraction pipeline |
| `backend/features/{ux,content,technical,trust}_features.py` | Per-dimension feature extractors |
| `backend/ml/train.py` | Training script with bootstrapped synthetic labels |
| `backend/ml/predict.py` | Inference + SHAP computation |
| `backend/ml/recommendations.py` | SHAP values → recommendation text templates |
| `frontend/app/page.tsx` | URL input landing |
| `frontend/app/score/page.tsx` | Score dashboard with gauge, bars, waterfall, recommendations |
| `frontend/app/api/proxy/route.ts` | Server-side proxy to FastAPI (avoids CORS) |

## ML Pipeline

- **Model:** XGBRegressor with 5-fold CV hyperparameter tuning
- **Features:** 40 across UX (10), Content (10), Technical (10), Trust (10)
- **Preprocessing:** ColumnTransformer (StandardScaler / OrdinalEncoder / passthrough)
- **Explainability:** shap.TreeExplainer (exact, fast for tree models)
- **Sub-scores:** Sum SHAP contributions per feature group, normalize to 0-25

## Cold-Start Strategy

No labeled dataset exists yet. v1 model trains on synthetic data: features extracted from real crawled sites, labels computed via weighted heuristic (PageSpeed × 0.4 + readability × 0.2 + CTA × 0.2 + trust × 0.2). Retrain on real labels (100+ sites) once dataset annotation is complete.

## Reused Code

From `.claude/skills/website-audit-system/scripts/`:
- `crawl_site.py` → `backend/crawler/firecrawl_client.py` (URL normalization, Firecrawl integration, truncation logic)
- `pagespeed.py` → `backend/crawler/pagespeed.py` (Core Web Vitals extraction)

## Conventions

- Python: type hints on all public functions; pytest for tests
- TypeScript: strict mode; zod for input validation
- API responses: always JSON with `{ ok: bool, data?, error? }` shape
- All HTTP calls through `frontend/lib/api-client.ts` — no fetch scattered in components

## Running Locally

```bash
# Terminal 1
cd backend && uvicorn main:app --reload

# Terminal 2
cd frontend && npm run dev
```

Visit `http://localhost:3000`.

## Testing

```bash
cd backend && pytest tests/
```
