# Lead Intake & Qualification — Plan

## The problem, restated

One operator (the owner) needs three things that are really one thing: a public form that
collects enough signal to judge a lead, a scoring rule set the owner can change without
touching code, and a triage surface that ranks the pipeline by that score and tracks state.

The interesting part is not CRUD. It is that **rules are data**, so changing a rule has to be
able to re-rank leads that already exist. Everything else follows from that.

## Stack

| Layer | Choice | Why this and not the obvious alternative |
|---|---|---|
| Runtime | Node 24.14 (verified on this machine) | Runs `.ts` files natively via type stripping, so no `tsx`, no build step for the server, no ts-node. Verified with a live test before committing. |
| Server | Fastify 5 | `app.inject()` gives real HTTP integration tests with no port binding and no supertest. Built-in schema hooks, first-party cookie and rate-limit plugins. Express would need 3 extra deps for the same. |
| Database | `node:sqlite` (built-in `DatabaseSync`) | Zero native compilation. `better-sqlite3` needs a prebuilt binary matching Node 24's ABI on win32 or it falls back to compiling, which is the single most common install failure on Windows. Verified `node:sqlite` works on this exact runtime before committing. Cost: it prints an ExperimentalWarning, suppressed via `--no-warnings=ExperimentalWarning`. Synchronous API is correct here anyway: one user, one process, local file. |
| Validation | zod 4 | Every request body is parsed, not trusted. `z.infer` keeps the wire types and the TS types from drifting. |
| Frontend | Vite 8 + React 19, TypeScript | Vite dev proxy sends `/api` to 4100, so no CORS in dev and the prod path (one origin) is the same path as dev. |
| Routing | ~25 lines of `pushState` + `popstate` | Four views. `react-router-dom` is 40kb and a dependency for something a small hook does. |
| Styling | One hand-written `styles.css` with CSS custom properties | No Tailwind, no component library. A framework's defaults are exactly the generic look this must not have. |
| Tests | Vitest 4 | Runs TS with no config, one runner for the pure engine and the HTTP layer. |

Ports: web dev server 3100, API 4100. In production the API serves the built frontend from
one origin on 4100, so deploying later is one process and one port.

## Data model

- `leads` — submission fields, plus `score`, `band`, `status`, `notes`, and a persisted
  `score_breakdown` JSON so the dashboard can show *why* a lead scored what it scored.
- `rules` — `{label, field, op, value, points, enabled}`. Points are signed, so a rule can
  subtract. This is the whole rule engine's storage.
- `settings` — `hot_min` / `warm_min` band thresholds.

`budget` and `timeline` are stored as ordinals 1-5, not strings, so `gte`/`lte` rules work on
them. The form's option labels come from one server-side catalog that both the form and the
rules editor read, so a rule can never reference a value the form cannot produce.

## Scoring engine

A pure function: `score(lead, rules, settings) -> {score, band, breakdown}`. No I/O, no DB, no
clock. That is what makes it worth testing properly.

- Operators: `gte`, `lte`, `eq` (numeric), `includes` (needs multi-select), `contains`,
  `not_contains` (case-insensitive text).
- Sum of matched rule points, clamped to 0-100.
- Band from thresholds: hot / warm / cold.
- Editing rules or thresholds offers a **Recompute all** action that re-scores the whole table.

## Security

Single user. `ADMIN_PASSWORD` and `SESSION_SECRET` from `.env`, never in source; the server
refuses to start in production without a real `SESSION_SECRET`. Login compares SHA-256 digests
with `timingSafeEqual`. Session is an HMAC-signed, httpOnly, sameSite=lax cookie with an
expiry, verified on every admin route by an `onRequest` hook. Every query is parameterized;
the `sort` and `dir` query params are matched against an allowlist rather than interpolated.
Public endpoints are rate-limited (form 10/min, login 8/5min) and every body is zod-parsed.

## Design direction

**Ink on paper, editorial.** Not a dark neon dashboard, and not default-framework white.

Warm paper ground (`#FBF9F5`), near-black ink, one deep-blue accent, band colors in terracotta
/ ochre / slate. Display type is a serif stack; UI type is sans; every number renders with
tabular figures so the score column reads as a ledger. System font stacks only, so it works
offline and never flashes. The public form reads like a considered questionnaire with numbered
sections, not a SaaS signup. The dashboard is the same paper, denser: a ruled table, the score
as a large numeral with a thin gauge bar beside it, and a detail drawer that shows the
per-rule breakdown.

## Deliberately not building

- Multi-user, roles, invites, signup. One user was the brief.
- Email or Slack notification on new lead. No credentials to send with, and it is an
  integration, not the product.
- CSV import. CSV **export** is in, it is four lines and it is how a single operator actually
  gets data out.
- A visual rule builder with AND/OR nesting. Flat additive rules with signed points cover the
  stated need; nesting is where scoring tools go to become unusable.
- Full-text search infrastructure. `LIKE` over four columns on a single-operator table.
- Docker, CI, migrations framework. One idempotent schema bootstrap.
