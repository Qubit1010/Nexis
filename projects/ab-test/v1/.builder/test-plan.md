---
project: LeadQ
shape: trophy
runner: Vitest 4 (node environment)
complexity: standard
created: 2026-09-01T00:00:00Z
---

# Test Plan - LeadQ

## 1. Strategy

- **Shape: trophy.** Static types are the base (`tsc --noEmit` over 32 project files, strict
  plus `noUncheckedIndexedAccess`). The bulk of the value is a thick integration layer that
  drives the real route handlers against a real SQLite file, because the seams that can
  actually break here are handler -> repository -> engine -> database. A dense unit layer
  sits under the scoring engine, which is the only place with real branching logic.
- **Why not a pyramid:** almost nothing in this app is pure computation except the engine.
  Testing the repositories in isolation would mostly assert that SQLite works.
- **Runner:** Vitest 4, node environment, `fileParallelism: false` because the suites share
  one `LEADQ_DB_PATH` process env var.
- **Test data:** every DB-touching suite gets a fresh temp directory and file via
  `tests/helpers/test-db.ts`, and drops it afterwards. No fixtures are shared between files
  and no test writes to `data/leads.db`.
- **No E2E.** Playwright would add a browser dependency and a second runner to assert what
  the integration tests already assert about behaviour. Flagged honestly in section 3.

## 2. Prioritized Coverage

| # | Area | What it verifies | Level | Priority |
|---|------|------------------|-------|----------|
| 1 | Authz | Every admin endpoint (GET leads, PATCH, DELETE, GET rules, PUT rules) returns 401 with no cookie and no data body; a forged and an expired cookie are both rejected; a valid cookie is accepted | integration | critical |
| 2 | Session crypto | Token signs and verifies; a tampered signature fails; a tampered expiry fails; an expired token fails; a wrong password fails; the right one passes | unit | critical |
| 3 | Core loop | Public submit -> scored row -> visible in triage -> status transition -> rule change rescores the existing lead | integration | critical |
| 4 | Public boundary | Bad payload gives 400 with per-field details; the honeypot returns a fake 201 and writes nothing; the score is never in the public response; rate limit returns 429 on the 6th hit | integration | critical |
| 5 | Scoring engine | Every operator (gte, lte, eq, neq, contains, in, present, absent) on every field shape (number, string, array); disabled rules skipped; negative points; clamping at 0 and 100; band boundaries; breakdown contents; nonsense operator/field pairs return false instead of throwing | unit | high |
| 6 | Data integrity | Rescore rewrites score, band and breakdown for existing rows; rule save is transactional; status counts stay correct | integration | high |

There is **no money path** in this product, so the budget that would normally go to payment
idempotency and webhook signatures went to items 1 and 4 instead.

## 3. Deliberately Not Tested (and why)

- **Browser E2E.** No Playwright. The route handlers are covered directly and the UI is
  three screens for one user. A real E2E suite would earn its place the moment a second
  person uses this or the form gains conditional logic.
- **React component rendering.** No jsdom, no Testing Library. The components are
  presentational; their logic (sorting, filtering) is a pure `useMemo` that would need the
  component harness to reach. This is the honest gap in the trophy: the client-side sort
  and filter in `triage.tsx` are **not** covered by an automated test, only by manual
  browser checking.
- **SQLite itself.** Constraints and index behaviour are the engine's job, not ours.
- **Rate limiter time-window expiry.** The reset path is asserted by calling the limiter
  directly rather than by sleeping for a real minute.

## 4. How to Run

```
npm install
npm run typecheck     # tsc --noEmit, the base of the trophy
npm test              # vitest run
```

No environment setup is required: the suites set `ADMIN_PASSWORD`, `SESSION_SECRET` and
`LEADQ_DB_PATH` themselves.

## 5. Plug into Review

Phase 6 runs `npm run typecheck`, `npm test`, `npm run lint` and `npm run build`, and
records the output verbatim in `review-report.md`.
