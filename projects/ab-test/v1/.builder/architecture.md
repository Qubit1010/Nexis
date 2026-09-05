---
project: LeadQ
complexity: standard
tech_stack:
  frontend: Next.js 16 App Router + React 19 (TypeScript strict)
  backend: Next.js route handlers (same process)
  database: SQLite via node:sqlite (Node 24 built-in)
  auth: single shared secret, HMAC-signed httpOnly cookie (Web Crypto)
  hosting: local now; container host with a volume later
created: 2026-08-31T18:26:00Z
source_blueprint: .builder/blueprint.md
---

# Architecture — LeadQ

## 1. Overview

LeadQ captures inbound leads through a public form, scores each one against an operator-
editable rule set, and presents them in a private triage dashboard sorted by score. One
operator, one process, one SQLite file.

## 2. Complexity Assessment

| Dimension | Score (1-5) | Rationale |
|-----------|-------------|-----------|
| Data | 3 | Three tables, one derived-value dependency (rules -> lead scores) that must stay consistent on rule change. |
| Auth | 1 | One user, one shared secret, no roles, no registration, no recovery. |
| UI | 3 | Three real surfaces: a public form, a sortable/filterable triage table with inline mutation, and a rule editor with add/remove/reorder rows. |
| Integrations | 1 | None. No email, no payments, no third-party API. |
| Scale | 1 | Hundreds of rows, one concurrent user. |
| **Total** | **9** | **Tier: standard** (bottom of the band) |

Standard tier drives: a real API contract, integration tests over the route handlers, a
designed empty state, and a rule editor rather than a config file. It does **not** buy
pagination, caching, background jobs or an ORM.

## 3. Tech Stack (from the blueprint)

Copied verbatim from `blueprint.md` section 4; rationale lives there and is not restated.

| Layer | Choice |
|-------|--------|
| Frontend / rendering | Next.js 16 App Router, React 19, TypeScript strict |
| UI | Plain CSS + CSS Modules, hand-authored tokens |
| Backend | Next.js route handlers, same process |
| API style | REST/JSON |
| Database | SQLite, `node:sqlite` (`DatabaseSync`) |
| Data access | Hand-written parameterized SQL in `lib/` repositories |
| Auth | `ADMIN_PASSWORD` login, HMAC-SHA256 signed session cookie |
| Validation | Zod 4 at both boundaries |
| Tests | Vitest 4 |
| Hosting | `next dev` / `next start` on :3000 |

No separate backend process, so port 4000 is unused by design.

## 4. Project Structure

```
projects/ab-test/v1/
  .builder/                    pipeline artifacts
  data/                        leads.db (gitignored, created on first boot)
  src/
    app/
      layout.tsx               root shell, fonts/tokens
      globals.css              design tokens + base styles
      page.tsx                 PUBLIC intake form
      form.module.css
      thanks/page.tsx          post-submit confirmation
      login/page.tsx           operator login
      login/login-form.tsx     client component
      login/login.module.css
      dashboard/
        layout.tsx             AUTH GATE (redirects to /login)
        page.tsx               server component: loads leads + rules, renders triage
        triage.tsx             client component: sort, filter, status mutation
        triage.module.css
        rules/page.tsx         server component: loads rules
        rules/rule-editor.tsx  client component: add/edit/remove/save rules
        rules/rules.module.css
      api/
        session/route.ts       POST login, DELETE logout
        leads/route.ts         POST (public), GET (admin)
        leads/[id]/route.ts    PATCH, DELETE (admin)
        rules/route.ts         GET, PUT (admin)
    components/
      score-meter.tsx          the signature score visualisation
      score-meter.module.css
      status-pill.tsx
      status-pill.module.css
      field.tsx                labelled form control wrapper
    lib/
      db.ts                    connection, migrations, seed
      schema.ts                Zod schemas + shared enums
      scoring.ts               PURE rules engine
      leads.ts                 lead repository
      rules.ts                 rule + threshold repository, rescoreAll
      auth.ts                  password check, cookie sign/verify
      http.ts                  json/error response helpers, requireAdmin
      rate-limit.ts            in-process fixed-window limiter
    types.ts                   shared domain types
  tests/
    scoring.test.ts
    auth.test.ts
    api.test.ts
    helpers/test-db.ts
  package.json  tsconfig.json  next.config.ts  vitest.config.ts
  .env.example  .gitignore  README.md
```

## 5. Database Schema

Created idempotently on first import of `lib/db.ts`. No migration tool: one `CREATE TABLE
IF NOT EXISTS` block, because there is no deployed schema history to migrate from yet.

### leads

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PK | UUID v4 |
| name | TEXT | NOT NULL | Contact name |
| email | TEXT | NOT NULL | Contact email |
| company | TEXT | NOT NULL DEFAULT '' | Company name, optional at the form |
| budget | INTEGER | NOT NULL | USD, the lower bound of the selected band |
| timeline | TEXT | NOT NULL | `asap` / `1_month` / `1_3_months` / `3_plus_months` / `exploring` |
| services | TEXT | NOT NULL DEFAULT '[]' | JSON array of service tags |
| needs | TEXT | NOT NULL | Free-text description of the requirement |
| source | TEXT | NOT NULL DEFAULT '' | How they found us |
| status | TEXT | NOT NULL DEFAULT 'new' | `new` / `contacted` / `qualified` / `dead` |
| score | INTEGER | NOT NULL DEFAULT 0 | 0-100, derived |
| band | TEXT | NOT NULL DEFAULT 'cold' | `hot` / `warm` / `cold`, derived |
| breakdown | TEXT | NOT NULL DEFAULT '[]' | JSON array of `{ruleId,label,points}` for the rules that fired |
| notes | TEXT | NOT NULL DEFAULT '' | Operator notes |
| created_at | TEXT | NOT NULL | ISO 8601 |
| updated_at | TEXT | NOT NULL | ISO 8601 |

Indexes: `idx_leads_score (score DESC)`, `idx_leads_status (status)`.

### rules

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PK | UUID v4 |
| label | TEXT | NOT NULL | Human name shown in the breakdown |
| field | TEXT | NOT NULL | `budget` / `timeline` / `services` / `needs` / `company` / `source` / `email` |
| operator | TEXT | NOT NULL | `gte` / `lte` / `eq` / `neq` / `contains` / `in` / `present` / `absent` |
| value | TEXT | NOT NULL | JSON-encoded operand (number, string, or string[]) |
| points | INTEGER | NOT NULL | May be negative |
| enabled | INTEGER | NOT NULL DEFAULT 1 | 0/1 |
| position | INTEGER | NOT NULL | Display order |

### settings

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| key | TEXT | PK | `band_hot` / `band_warm` |
| value | TEXT | NOT NULL | Stringified integer threshold |

**Derived-value rule:** `leads.score`, `leads.band` and `leads.breakdown` are a pure
function of the row's answers plus the current rules and thresholds. They are written on
insert and rewritten for every lead by `rescoreAll()` whenever `PUT /api/rules` succeeds.
Nothing else may write them.

## 6. API Contract

Error envelope on every non-2xx: `{ "error": string, "code": string, "details"?: unknown }`.
Codes used: `validation_error`, `unauthorized`, `not_found`, `rate_limited`, `bad_request`.

Admin endpoints require the `leadq_session` cookie; without it they return **401
`unauthorized`** and no body data. Auth is re-checked inside every admin handler, not only
at a gate.

### POST /api/leads (PUBLIC)

Request:
```json
{
  "name": "Dana Reyes", "email": "dana@acme.io", "company": "Acme",
  "budget": 10000, "timeline": "asap",
  "services": ["ai-automation"], "needs": "We need our intake automated.",
  "source": "referral", "website": ""
}
```
`website` is a honeypot: if non-empty the request is accepted with a 201 and silently
discarded. `company` and `source` default to `""`. Rate limited to 5 requests / 60s / IP.

Response `201`: `{ "ok": true, "id": "<uuid>" }`
The score is deliberately **not** returned to the public caller.

Errors: `400 validation_error` (with `details` = flattened Zod issues), `429 rate_limited`.

### GET /api/leads (ADMIN)

Query params, all optional: `status` (`all`|status), `band` (`all`|band),
`sort` (`score`|`created_at`|`name`, default `score`), `order` (`asc`|`desc`, default
`desc`), `q` (case-insensitive substring over name/company/email/needs).

Response `200`:
```json
{ "leads": [Lead], "counts": { "all": 12, "new": 5, "contacted": 3, "qualified": 2, "dead": 2 } }
```
`Lead` is the full row with `services` and `breakdown` parsed into arrays.

### PATCH /api/leads/:id (ADMIN)

Request: `{ "status"?: "new"|"contacted"|"qualified"|"dead", "notes"?: string }`
(at least one key required). Response `200`: `{ "lead": Lead }`.
Errors: `400 validation_error`, `404 not_found`.

### DELETE /api/leads/:id (ADMIN)

Response `200`: `{ "ok": true }`. Errors: `404 not_found`.

### GET /api/rules (ADMIN)

Response `200`: `{ "rules": [Rule], "bands": { "hot": 70, "warm": 40 } }`
`Rule` = `{ id, label, field, operator, value, points, enabled, position }` with `value`
JSON-parsed.

### PUT /api/rules (ADMIN)

Replaces the whole rule set atomically, then rescores every lead.

Request: `{ "rules": [RuleInput], "bands": { "hot": number, "warm": number } }`
`RuleInput` omits `id` and `position` (both assigned server-side by array order).
Constraint: `bands.hot > bands.warm`, both 0-100.

Response `200`: `{ "rules": [Rule], "bands": {...}, "rescored": 12 }`
Errors: `400 validation_error`.

### POST /api/session

Request `{ "password": string }`. Response `200` `{ "ok": true }` plus
`Set-Cookie: leadq_session=<exp>.<hmac>; HttpOnly; SameSite=Lax; Path=/; Max-Age=604800`
(`Secure` added when `NODE_ENV=production`).
Errors: `401 unauthorized` on a wrong password, `400 validation_error` on a missing field.

### DELETE /api/session

Response `200` `{ "ok": true }` plus a `Max-Age=0` cookie.

## 7. Frontend Breakdown

| Route | Type | Access | Responsibility |
|-------|------|--------|----------------|
| `/` | server + client form | public | The intake form. Client component posts to `POST /api/leads`, shows inline field errors, redirects to `/thanks`. |
| `/thanks` | server | public | Confirmation. No data. |
| `/login` | server + client form | public | Password field, posts to `POST /api/session`, redirects to `/dashboard`. |
| `/dashboard` | server shell + client table | admin | Reads leads server-side on first paint, hands them to a client component for sort/filter/mutation. Status changes PATCH and update in place. |
| `/dashboard/rules` | server shell + client editor | admin | Rule rows (field/operator/value/points/enabled), add/remove/reorder, band thresholds, save -> PUT -> shows the rescored count. |

`dashboard/layout.tsx` verifies the session cookie server-side and redirects to `/login`.
Every admin route handler re-checks independently.

Component hierarchy:
- `ScoreMeter` — score number in tabular mono + a band-coloured signal bar. Used in the table.
- `StatusPill` — the four states, each with its own treatment.
- `Field` — label + control + error + hint, keeps every input labelled.

## 8. Backend Breakdown

Layering: `route handler` (parse, authorize, validate, respond) -> `repository`
(`lib/leads.ts`, `lib/rules.ts`) -> `lib/db.ts`. The scoring engine is called by the
repositories, never by a handler. No SQL outside `lib/`.

| Module | Exports | Notes |
|--------|---------|-------|
| `lib/db.ts` | `getDb()`, `resetDbForTests()` | Lazy singleton `DatabaseSync`, WAL on, schema + seed on first open. Path from `LEADQ_DB_PATH`, default `data/leads.db`. |
| `lib/scoring.ts` | `scoreLead(lead, rules, bands)`, `bandFor(score, bands)` | PURE. No imports from db/next. Clamps 0-100. Returns `{score, band, breakdown}`. |
| `lib/leads.ts` | `createLead`, `listLeads`, `getLead`, `updateLead`, `deleteLead`, `countsByStatus` | Owns the derived columns. |
| `lib/rules.ts` | `listRules`, `replaceRules`, `getBands`, `setBands`, `rescoreAll` | `replaceRules` + `rescoreAll` run inside one transaction. |
| `lib/auth.ts` | `verifyPassword`, `createSessionToken`, `verifySessionToken`, `sessionCookie` | HMAC-SHA256 via Web Crypto; constant-time compares. |
| `lib/http.ts` | `json`, `fail`, `requireAdmin(req)` | `requireAdmin` reads the cookie off the `Request`, not `next/headers`, so handlers are unit-testable. |
| `lib/rate-limit.ts` | `hit(key, limit, windowMs)` | Fixed window in a `Map`. Per-process only; documented as such. |

## 9. Environment Variables

| Name | Required | Default | Purpose |
|------|----------|---------|---------|
| `ADMIN_PASSWORD` | yes | `changeme` (dev only, warns) | The single operator password. |
| `SESSION_SECRET` | yes | dev-only fallback (warns) | HMAC key for the session cookie. |
| `LEADQ_DB_PATH` | no | `data/leads.db` | SQLite file location; tests point it at a temp file. |

`.env.example` ships all three with no real values.

## 10. Implementation Order

1. `lib/db.ts`, `lib/schema.ts`, `types.ts`, seed data.
2. `lib/scoring.ts` (pure) + `tests/scoring.test.ts`.
3. `lib/leads.ts`, `lib/rules.ts`, `lib/auth.ts`, `lib/http.ts`.
4. Route handlers.
5. Design tokens + `globals.css`, then the public form, login, dashboard, rule editor.
6. `tests/api.test.ts`, `tests/auth.test.ts`.
7. Typecheck, build, test, review, polish.

## 11. Deliberate Non-Goals

Pagination, caching, background jobs, an ORM, a migration runner, multi-user auth, email,
CRM sync, charts, exports, webhooks. Each would be justified by a constraint this product
does not have.
