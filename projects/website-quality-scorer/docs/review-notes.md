# Code Review Notes — v1

Self-review applying the code-reviewer skill framework to the v1 build of `projects/website-quality-scorer/`.

## Summary

| Category | Status |
|---|---|
| Python syntax (22 files) | ✅ All pass `ast.parse` |
| TypeScript files | ✅ Type-safe, strict mode enabled |
| Security (SSRF, CORS, API keys) | ✅ Mitigations in place |
| Tests | ✅ Smoke tests for features + predict |
| Documentation | ✅ README + CLAUDE + architecture |

## Findings

### Resolved during review

| # | Issue | Resolution |
|---|---|---|
| 1 | Feature count was documented as "40" but actual schema has 41 (UX 10, Content 10, Technical 11, Trust 10) | Documented in CLAUDE.md; proposal text "~40" remains accurate |
| 2 | No `.gitignore` for backend | Added |
| 3 | No `data/README.md` describing labeling rubric | Added |

### Non-critical (deferred / acceptable)

| # | Issue | Why deferred |
|---|---|---|
| A | `coerce_numeric` lambda relies on Python's truthy comparison (`1 == True`) — works correctly but slightly opaque | Functional, well-tested by feature tests |
| B | SHAP dimension sub-scores use `tanh(sum/10)` mapping — magic constant | Heuristic for cold-start; will retune once real labels exist |
| C | No retry logic on Firecrawl/PageSpeed network calls | Simple errors surface to user; retry adds complexity for marginal benefit |
| D | No prediction logging (SQLite) | Out of scope for stateless v1 — already noted in architecture as scalability path |
| E | Frontend has no test suite | MVP scope — pages tested manually during verification |

### Security review

- ✅ **SSRF:** `firecrawl_client._is_safe_url` blocks private IPs (10.x, 192.168.x, 127.x), reserved/link-local addresses, `localhost`, and non-HTTP schemes
- ✅ **CORS:** restricted via `ALLOWED_ORIGINS` env var (default localhost:3000)
- ✅ **API keys:** never exposed to the browser — `BACKEND_URL` is read by the Next.js server-side route only
- ✅ **Input validation:** Pydantic at API boundary; URL normalization in crawler
- ✅ **No SQL:** stateless v1 — no query injection surface

### Code quality observations

**Strengths:**
- Type hints throughout backend (Python 3.11+)
- Strict TypeScript on frontend with full type definitions in `lib/types.ts`
- Single API client (`lib/api-client.ts`) — no scattered fetch calls
- Clear module boundaries (crawler / features / ml are independently testable)
- Recommendations decoupled from inference — easy to extend templates

**Anti-patterns avoided:**
- No global mutable state
- No tight coupling between FastAPI handlers and ML logic
- No hardcoded magic strings (feature names live in `FEATURE_SCHEMA`)
- No premature abstractions (kept the cold-start synthetic generator simple)

## Files Reviewed

```
backend/  (22 Python files)
  api/score_endpoint.py
  crawler/{firecrawl_client,pagespeed}.py
  features/{ux,content,technical,trust}_features.py + extractor.py
  ml/{train,predict,preprocessing,recommendations,heuristic_label,synthetic_dataset}.py
  main.py + tests/{test_features,test_predict}.py

frontend/ (10 TypeScript files)
  app/{layout,page}.tsx + score/page.tsx + api/proxy/score/route.ts
  components/{score-gauge,dimension-bars,shap-waterfall,recommendations-list}.tsx
  lib/{utils,types,api-client}.ts
```

## Verdict

**Approved for v1.** Build is production-quality for the MVP scope. Real labeled data collection (course Phase 2) and model retraining are the next steps; no architectural rework needed.
