---
status: pass
critical_issues: 0
warnings: 2
suggestions: 0
tests: 65/65
reviewed: 2026-09-01T01:10:00Z
---

# Review Report - LeadQ

## Summary

| Category | Count | Status |
|----------|-------|--------|
| Critical Issues | 0 | - |
| Warnings | 2 | accepted, documented |
| Suggestions | 0 | - |
| **Overall** | | **PASS** |

Every endpoint in architecture section 6 is implemented on both sides with matching shapes,
the four gates (typecheck, lint, test, build) are green, and the full core loop was
exercised over real HTTP against the built server, not just in tests.

---

## Contract Verification (architecture section 6)

| Endpoint | Backend | Frontend caller | Request match | Response match | Status |
|----------|---------|-----------------|---------------|----------------|--------|
| `POST /api/leads` (public) | OK `api/leads/route.ts` | OK `intake-form.tsx` | OK | OK | OK |
| `GET /api/leads` (admin) | OK `api/leads/route.ts` | OK `dashboard/page.tsx` reads via repository; `triage.tsx` re-reads after mutation | OK | OK | OK |
| `PATCH /api/leads/:id` | OK `api/leads/[id]/route.ts` | OK `triage.tsx` | OK | OK | OK |
| `DELETE /api/leads/:id` | OK `api/leads/[id]/route.ts` | OK `triage.tsx` | OK | OK | OK |
| `GET /api/rules` | OK `api/rules/route.ts` | OK `dashboard/rules/page.tsx` via repository | OK | OK | OK |
| `PUT /api/rules` | OK `api/rules/route.ts` | OK `rule-editor.tsx` | OK | OK | OK |
| `POST /api/session` | OK `api/session/route.ts` | OK `login-form.tsx` | OK | OK | OK |
| `DELETE /api/session` | OK `api/session/route.ts` | OK `sign-out-button.tsx` | OK | OK | OK |

Error envelope `{ error, code, details? }` is produced by a single `fail()` helper, so it
cannot drift between endpoints. Verified live: `unauthorized`, `validation_error`,
`bad_request`, `not_found`, `rate_limited` all observed with the documented shape.

**Deviation from the contract, by design:** the dashboard and rules pages are server
components that call the repositories directly instead of fetching `GET /api/leads` and
`GET /api/rules` over HTTP. Fetching your own API from your own server on first paint is a
pointless round trip in Next. Both endpoints still exist, are still authorized, and are the
path every client-side mutation and refresh uses.

## Completeness (architecture sections 5, 7, 8)

| Item | Type | Exists | Correct | Status |
|------|------|--------|---------|--------|
| `leads`, `rules`, `settings` tables + 2 indexes | schema | Yes | Yes | OK |
| Seeded default rules (11) + band thresholds | seed | Yes | Yes, verified in the live run | OK |
| `/`, `/thanks`, `/login`, `/dashboard`, `/dashboard/rules` | pages | Yes | Yes, all render 200 | OK |
| 10 routes in the build manifest | build | Yes | Yes | OK |
| `ScoreMeter`, `StatusPill`, `Field` | components | Yes | Yes | OK |
| `scoring.ts` pure (no db/next imports) | constraint | Yes | Verified by inspection and by unit tests running with no DB | OK |
| `.env.example` with all three variables | config | Yes | Yes, no real values | OK |

## Security Baseline

| Check | Result |
|-------|--------|
| No secrets in source | OK. Dev fallbacks are obvious placeholders and warn at runtime. |
| Input validated at the boundary | OK. Zod on both the public submission and the rule editor; live 400 carries per-field details. |
| Parameterized queries only | OK. Every value is a `?` bind. The one interpolated fragment is the sort column, resolved through a whitelist map. |
| SQL injection through the sort key | OK. Tested with `sort=name);DROP TABLE leads;--`, returns 200 and the table survives. |
| Authz re-checked on every admin handler | OK. `requireAdmin()` at the top of all five admin handlers, independent of the page-level layout gate. Tested unauth on all five. |
| Session cookie httpOnly / SameSite / signed / expiring | OK. Verified in the live `Set-Cookie` and in unit tests for tamper, forged expiry and expiry. |
| Password compared in constant time | OK. Both sides hashed to a fixed width first, so the compare cannot leak length. |
| Score not leaked to the public caller | OK. Asserted in tests and confirmed live. |
| Abuse control on the public endpoint | OK. Honeypot plus a 5-per-minute per-IP limiter. |
| Webhooks / payment idempotency | N/A. No money path in this product. |

## Verification Run

All commands executed in `projects/ab-test/v1`.

| Command | Result |
|---------|--------|
| `npx tsc --noEmit` | exit 0, 32 project files checked |
| `npm run lint` | exit 0, no findings |
| `npm test` | exit 0, **65 passed (65)**, 3 files |
| `npm run build` | exit 0, 10 routes emitted |
| `npx next start -p 3000` + 14 curl checks | all as specified, see below |

Live HTTP checks against the built server, in order: public form renders (200); `/dashboard`
redirects to `/login` (307) when unauthenticated; `GET /api/leads` refuses (401); a valid
submission is accepted (201) and scored 100/hot by the seeded rules with a 6-line receipt;
an invalid submission returns 400 with five field errors; the wrong password is refused
(401); the right one sets an HttpOnly cookie (200); the authenticated list and dashboard
render (200); a status change to `contacted` persists; the rules page renders the seeded
set; a rule-set replacement rescores the stored lead 100 -> 40 while preserving its
`contacted` status; invalid bands are rejected (400).

## Fix Log

| # | Issue | Severity | Fix |
|---|-------|----------|-----|
| 1 | `eslint.config.mjs` spread `eslint-config-next` as a function; ESLint crashed with `next is not a function` | critical for the lint gate | The v16 default export is already an array. Changed to `...next`. Lint then passed clean. |
| 2 | A malformed duplicated `describe` block in `scoring.test.ts` (a mangled expectation left mid-edit) | critical | Removed the block; the following `matches - presence` suite already covered it properly. |
| 3 | `.summary` error box used a 3px coloured left border | warning (design) | Flagged by the design hook as the classic side-tab AI tell, and it contradicted this system's own "separate with hairlines, not slabs" rule. Replaced with a 1px danger border and the mono `/` marker used by field-level errors. |
| 4 | `.sr-only` was used in three components but never defined | warning (a11y) | Added the utility to `globals.css` and removed an inline off-screen style from `ScoreMeter`. |

## Polish Pass

Behaviour-preserving only; typecheck, lint, tests and build were re-run green afterwards.

- Un-exported `MIN_SCORE`, `MAX_SCORE`, `getLead` and `ruleInputSchema`: all consumed only
  inside their own module, so the export was public surface nothing asked for.
- Removed six CSS tokens for components this product does not have: `--copper-wash`,
  `--slate-wash`, `--r-md`, `--z-menu`, `--z-dialog`, `--shadow-pop`. The z-scale is now the
  two layers that actually exist.
- No duplicated logic worth extracting was found. The one near-duplicate,
  `toLead` / `toScorable` in `leads.ts`, is deliberate: `ScorableLead` is the narrower shape
  the engine is allowed to see, and collapsing them would hand the scoring engine fields it
  has no business reading.

## Warnings Accepted (not fixed, deliberately)

1. **`node:sqlite` prints an `ExperimentalWarning` on every boot.** Cosmetic, appears in the
   dev, test and build output. Accepted at Phase 0 with reasoning in `decisions.md`: the
   alternative was a native module that has to compile on Windows. Isolated in `db.ts`.
2. **The client-side sort and filter in `triage.tsx` have no automated test.** Reaching them
   needs jsdom plus Testing Library, a dependency and a runner the rest of the suite does not
   need. Named as the honest gap in `test-plan.md` section 3 rather than papered over with a
   hollow test. It was exercised by hand in the browser-equivalent HTTP run only insofar as
   the page renders; the sort interaction itself is unverified.

## Design-System Drift

`design-system.md` section 4 says `--shadow-pop` is "for the one floating surface (the
expanded receipt)". The receipt was built as an inline expanded table row on `--sunken`
rather than a floating popover, which suits the ledger register better and avoids a
focus-trap problem. The token is therefore unused and was removed in the polish pass. The
doc is left as written per the append-only artifact rule; this note is the correction.
