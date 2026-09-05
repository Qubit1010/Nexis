---
project: ReplyLab
phase: 6 (review + polish)
status: pass
reviewed: 2026-09-01
---

# Review Report — ReplyLab

## 1. Contract verification (architecture section 6)

Every endpoint implemented on both sides and exercised. "Tested" means an assertion in
`tests/api.test.ts`; "manual" means executed over HTTP during review.

| # | Endpoint | Server | Client (`src/api.ts`) | Verified |
|---|---|---|---|---|
| 1 | GET `/api/health` | yes | `api.health` | tested + manual |
| 2 | GET `/api/enquiries` | yes | `api.listEnquiries` | tested |
| 3 | POST `/api/enquiries` | yes | `api.createEnquiry` | tested + manual |
| 4 | GET `/api/enquiries/:id` | yes | `api.getEnquiry` | tested |
| 5 | POST `/api/enquiries/:id/drafts` | yes | `api.generateDraft` | tested + manual |
| 6 | PATCH `/api/drafts/:id` | yes | `api.saveEdit`, `api.rate` | tested + manual |
| 7 | GET `/api/prompts` | yes | `api.listPrompts` | tested |
| 8 | POST `/api/prompts` | yes | `api.createPrompt` | tested + manual |
| 9 | POST `/api/prompts/:id/activate` | yes | `api.activatePrompt` | tested |
| 10 | GET `/api/stats` | yes | `api.stats` | tested + manual |

Field names and types match between `server/db.ts` and `src/types.ts`. No orphan client calls,
no unreachable server routes.

## 2. Invariants

| Invariant | How it is enforced | Test |
|---|---|---|
| `generated_text` is never overwritten | `updateDraft` has no code path that writes it | api.test.ts "records an edit without ever overwriting what the model wrote" |
| Edit distance is always measured against the original | `routes.ts` measures against `existing.generatedText`, never the previous edit | api.test.ts "measures a second edit against the original draft" |
| Prompt versions are append-only | only `is_active` is ever UPDATEd | api.test.ts "saving a prompt creates a new version ... leaving the old text intact" |
| Exactly one active version | activate/create both clear all flags inside a transaction | api.test.ts "can roll back to an earlier version" |
| Ratings attribute to the producing version | `drafts.prompt_version_id` set at generation time | scoreboard.test.ts "attributes ratings to the prompt version that produced the draft" |
| Small samples never read as conclusive | Wilson interval + `enoughData` | scoreboard.test.ts, 6 cases |

## 3. Verification run

```
npx tsc --noEmit     -> exit 0
npx vitest run       -> 4 files, 64 tests, all passed
npx vite build       -> exit 0, dist/ 211.62 kB js / 11.97 kB css
```

Runtime, with `ANTHROPIC_API_KEY` unset and no `.env` file present:

- `npm start` on a fresh database: boots, logs `provider STUB`, serves the API on 4200.
- Full loop over HTTP: create enquiry, draft, edit, rate, create prompt v2, re-draft, rate,
  read `/api/stats`. Correct attribution, correct intervals.
- `npm run dev`: Vite on 3200 and Express on 4200 together; `/api/health` through the Vite
  proxy returns the same payload as the direct call, so the proxy wiring is confirmed.
- UI verified in headless Chrome over CDP against the demo database: stub banner present,
  6 enquiries in the rail, Scoreboard renders 3 ledger rows with 3 gauges and 3 whiskers whose
  geometry matches the computed Wilson bounds, gauge `aria-label`s read correctly, no horizontal
  overflow at 1440px or at 360px.

## 4. Security baseline

| Check | Status |
|---|---|
| No secrets in source | Pass. `.env.example` has an empty key; `.env` is gitignored |
| Input validated at the boundary | Pass. zod on every body and every path id |
| Parameterised queries only | Pass. Every statement is `prepare` + bound params; no string interpolation into SQL |
| Errors do not leak internals | Pass. Unknown errors log server-side and return a generic 500 |
| CORS | Not applicable. Vite proxies `/api`, so the browser is same-origin. No CORS middleware, which is the correct answer here rather than a permissive one |
| Authz | Not applicable. Single local user, no accounts, by design |
| Parent-repo secret isolation | Pass, and deliberate. `config.ts` reads only this directory's `.env`; the parent repo's real key is never picked up |

## 5. Issues found and fixed during review

1. **Express 5 param typing.** `req.params.id` is `string | string[] | undefined`; `parseId` took
   `string | undefined` and failed typecheck in four places. Widened to `unknown`, which is also
   more correct since zod coercion rejects arrays as NaN.
2. **Seed script path resolution.** `loadConfig({ dbPath })` overrides bypassed the `path.resolve`
   inside `loadConfig`, so the demo database location depended on the shell's cwd. Now resolved
   explicitly against `PROJECT_ROOT`.
3. **Demo edits were nonsense text.** The seed simulated user edits by appending `x` to words,
   which produced garbage in the draft pane, since the pane shows the edited text. Replaced with
   two realistic edit functions (a light tidy-up, a full rewrite) that still produce the intended
   spread of keep-ratios.
4. **Duplicate import** of `../server/db.ts` in the seed script, merged.
5. **Design: over-applied accent rule.** The 3px accent left-border was used in five places,
   which made it a tic rather than a signature. Reduced to two, both meaning "this is the active
   prompt version". Enquiry selection and the rating control now carry their state differently.
6. **Design: layout-thrashing animation.** The scoreboard bar animated `width`; changed to
   `transform: scaleX()` with `transform-origin: left`, which is compositor-only and identical
   visually. Confirmed in the browser (`scaleX(0.833333)` etc. in the rendered DOM).

## 6. Polish pass

- No dead code, no speculative abstraction, no unused exports (`noUnusedLocals` and
  `noUnusedParameters` are on and typecheck is clean).
- Dependency count kept deliberately low: `node:sqlite` and Node's native TS execution removed
  the need for `better-sqlite3`, `tsx`, and `dotenv`. Tests use Node's global `fetch` rather than
  `supertest`.
- Comments explain why, not what: the provenance block in `pricing.ts`, the reason Wilson is used
  over a bare rate, and the reason the parent `.env` is not read.

## 7. Remaining risk

**The live Anthropic path has never been executed.** There is no API key in this environment. The
request shape follows the `claude-api` skill (adaptive thinking, no `budget_tokens`, no prefill,
`effort` inside `output_config`) and is asserted in a unit test against a fake client, but no
real HTTP request has been made to the API. A test asserting the request shape is not proof the
API accepts it. This is the one thing a reader should not assume is verified.
