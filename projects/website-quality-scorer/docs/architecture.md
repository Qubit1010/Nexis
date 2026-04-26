# Architecture — Website Quality & Conversion Gap Scorer

## System Overview

A three-tier full-stack ML system. Stateless inference: URL in, scored report out. No persistence required for v1.

```
┌──────────────────────────────────────────────────────────────────┐
│  PRESENTATION LAYER                                              │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Next.js 16 (TypeScript, Tailwind, shadcn/ui, recharts)   │  │
│  │  • app/page.tsx          URL input form                   │  │
│  │  • app/score/page.tsx    Score dashboard                  │  │
│  │  • app/api/proxy/...     Server-side proxy → FastAPI      │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────┬───────────────────────────────────────┘
                           │ HTTPS / JSON
┌──────────────────────────▼───────────────────────────────────────┐
│  APPLICATION LAYER                                               │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  FastAPI (Python 3.11, uvicorn ASGI)                       │  │
│  │  • POST /score    Orchestrates pipeline                    │  │
│  │  • GET  /health   Liveness probe                           │  │
│  └─────────────┬──────────────────────────────┬───────────────┘  │
│                │                              │                  │
│  ┌─────────────▼─────────────┐  ┌─────────────▼───────────────┐  │
│  │  Crawler Module           │  │  ML Inference Module        │  │
│  │  • Firecrawl client       │  │  • XGBoost predictor        │  │
│  │  • PageSpeed API client   │  │  • SHAP TreeExplainer       │  │
│  │  • URL normalization      │  │  • Recommendation engine    │  │
│  └─────────────┬─────────────┘  └─────────────▲───────────────┘  │
│                │                              │                  │
│  ┌─────────────▼──────────────────────────────┴───────────────┐  │
│  │  Feature Extraction Pipeline (40 features)                  │  │
│  │  • UX (10)  • Content (10)  • Technical (10)  • Trust (10) │  │
│  └─────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
                           │
                           ▼
                ┌────────────────────────┐
                │  External Services     │
                │  • Firecrawl API       │
                │  • PageSpeed Insights  │
                └────────────────────────┘
```

## Component Contracts

### POST /score (FastAPI)

**Request:**
```json
{ "url": "https://example.com" }
```

**Response (200):**
```json
{
  "ok": true,
  "data": {
    "url": "https://example.com",
    "score": 72.4,
    "tier": "Good",
    "sub_scores": {
      "ux": 18.2,
      "content": 14.5,
      "technical": 22.1,
      "trust": 17.6
    },
    "shap_values": [
      { "feature": "pagespeed_mobile", "value": 0.082, "raw": 95 },
      { "feature": "cta_above_fold", "value": 0.061, "raw": 1 }
    ],
    "recommendations": [
      {
        "priority": 1,
        "title": "Add testimonials above the fold",
        "rationale": "Trust signals are absent. Adding 2-3 testimonials...",
        "impact": "+8 to +12 score points"
      }
    ],
    "elapsed_ms": 8421
  }
}
```

**Response (4xx/5xx):**
```json
{ "ok": false, "error": "Unable to crawl URL: timeout after 30s" }
```

### GET /health
Returns `{ "ok": true, "model_loaded": true, "version": "v1" }`.

## Data Flow

1. User enters URL on `localhost:3000` → submits form
2. Frontend POSTs to its own `/api/proxy/score` route (server-side)
3. Proxy route POSTs to `http://localhost:8000/score`
4. FastAPI:
   - Validates URL with Pydantic
   - Calls Firecrawl → HTML + markdown
   - Calls PageSpeed Insights API → Core Web Vitals
   - Runs feature extractor → 40-dim feature vector
   - Loads XGBoost model (cached at startup) → score prediction
   - Runs SHAP TreeExplainer → per-feature contributions
   - Maps top negative SHAP values → recommendation templates
   - Returns JSON response
5. Frontend renders gauge, dimension bars, waterfall, recommendations

## Tech Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Backend language | Python 3.11 | ML stack (XGBoost, SHAP) is Python-native |
| Web framework | FastAPI | Async, auto OpenAPI docs, Pydantic validation, fast |
| Frontend framework | Next.js 16 | Matches Nexis convention; SSR support; easy proxy routing |
| State management | None (URL params) | Stateless inference doesn't need Redux/Zustand |
| Charting | recharts | Already used in Nexis projects; React-native; SHAP waterfall feasible |
| Persistence | None for v1 | Stateless app; add SQLite later if logging needed |
| Crawling | Firecrawl | Handles JS-rendered pages; already paid for; lifted from website-audit-system |
| Performance metrics | PageSpeed Insights API | Authoritative source; free tier 25k req/day |
| Auth | None for v1 | Course project; localhost only |
| Deployment | Local (uvicorn + npm) | MVP scope; demo-only |

## Module Responsibilities

### `backend/api/score_endpoint.py`
- Single async function: `score_url(req: ScoreRequest) -> ScoreResponse`
- Orchestrates: crawler → features → ML → SHAP → recommendations
- Handles errors with explicit Pydantic error models

### `backend/crawler/`
- `firecrawl_client.py`: `crawl(url) -> dict` returning `{html, markdown, metadata}`
- `pagespeed.py`: `fetch_metrics(url) -> dict` returning Core Web Vitals
- Both have graceful error handling; if either fails, the pipeline still returns a score using available features (with NaN handling in XGBoost)

### `backend/features/`
- `extractor.py`: master pipeline `extract_all(crawl_data, pagespeed_data) -> dict`
- 4 feature modules, one per dimension, each exposes `extract(crawl_data, pagespeed_data) -> dict`
- All features have a fixed schema documented in `extractor.py`

### `backend/ml/`
- `train.py`: standalone training script — runs once, produces `models/xgboost_v1.joblib`
- `predict.py`: `predict(features: dict) -> {score, sub_scores, shap_values}`
- `preprocessing.py`: `build_pipeline()` returns sklearn ColumnTransformer
- `recommendations.py`: `generate(shap_values: list, features: dict) -> list[Recommendation]`

### `frontend/`
- Server components by default; client components only where interactivity is needed (URL form, charts)
- Single API client at `lib/api-client.ts` — no scattered fetch calls
- shadcn/ui provides design system primitives (Button, Card, Input, etc.)

## Dependency Direction

```
frontend ──→ FastAPI (HTTP only)
FastAPI ──→ crawler, features, ml
features ──→ (uses crawler output, no direct dependency)
ml ──→ features (only via dict schemas)
recommendations ──→ shap_values (read-only)
```

No circular dependencies. ML module is decoupled from web framework — testable in isolation.

## Security Considerations

- **SSRF risk:** users submit URLs that the backend fetches. Mitigations:
  - Reject private IP ranges (10.0.0.0/8, 192.168.0.0/16, 127.0.0.0/8)
  - Reject non-http(s) schemes
  - Timeout aggressively (30s total budget)
- **Input validation:** Pydantic at API boundary; URL normalization in crawler
- **API keys:** never exposed to frontend; only server-side `.env`
- **CORS:** restricted to `ALLOWED_ORIGINS` env var (default `http://localhost:3000`)

## Performance Targets

| Metric | Target |
|---|---|
| End-to-end latency | < 30s |
| Crawler step | < 10s |
| PageSpeed API call | < 15s |
| Feature extraction | < 1s |
| ML inference + SHAP | < 200ms |
| Concurrent users (v1) | 1-5 (single uvicorn worker) |

## Scalability Path (post-MVP, not in scope)

1. Cache PageSpeed responses per URL in Redis (TTL 1h)
2. Add SQLite for prediction logging
3. Move to multi-worker uvicorn (`--workers 4`)
4. Containerize with Docker
5. Deploy to GCP Cloud Run / Vercel

## Risk Register

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Firecrawl credit exhaustion | Medium | High | MCP fallback (already in audit-system); cache during dev |
| PageSpeed API rate limit | Low | Medium | 25k/day free tier far exceeds course needs |
| No labeled dataset at MVP | High | Medium | Heuristic-bootstrapped synthetic dataset for v1 |
| SHAP recommendations feel generic | Medium | Medium | Hand-craft 30+ templates tied to specific feature groups |
| CORS issues | Low | Low | Next.js API proxy avoids browser CORS entirely |

## Confirmed: Build Can Proceed

All decisions are aligned with project plan. Backend build (Phase 2) can begin.
