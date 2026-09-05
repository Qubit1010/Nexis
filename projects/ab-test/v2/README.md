# Lead Intake & Qualification

A public enquiry form, a scoring engine whose rules you edit in the browser, and an internal
board to triage what comes in. Single operator, runs locally, deploys as one process.

## Run it

```bash
npm install
cp .env.example .env      # then set ADMIN_PASSWORD and SESSION_SECRET
npm run dev
```

- Public form: http://localhost:3100/
- Dashboard:   http://localhost:3100/admin

`npm run dev` starts the API on 4100 and Vite on 3100. Vite proxies `/api` to the API, so
both surfaces are same-origin in development exactly as they are in production.

| Command | What it does |
|---|---|
| `npm run dev` | API on 4100 and the frontend on 3100, both watching |
| `npm test` | The server test suite (50 tests) |
| `npm run typecheck` | `tsc --noEmit` across both workspaces |
| `npm run build` | Builds the frontend into `web/dist` |
| `npm start` | Runs the API alone on 4100; serves `web/dist` too if it has been built |

Requires Node 22.6 or newer. It runs the server's TypeScript directly through Node's type
stripping, so there is no server build step. Verified on Node 24.14.

## Deploying

`npm run build && npm start` is the whole thing. Once `web/dist` exists the API serves it, so
production is one process on one port. Set in the environment:

- `SESSION_SECRET` (required, 16+ random chars). The server refuses to start without it.
- `ADMIN_PASSWORD` (required). The server refuses to start on the default.
- `DB_PATH` pointing at persistent disk.
- `TRUST_PROXY=true` only if a reverse proxy you control is in front. It makes the rate
  limiter trust `X-Forwarded-For`, which a direct caller could otherwise forge.

## How the scoring works

Rules live in the database, not in code, so you edit them on `/admin/rules`.

A rule is `when <field> <test> <value>, add <points>`. Points can be negative. Every enabled
rule that matches contributes, the total is clamped to 0-100, and the thresholds you set turn
that into hot / warm / cold.

Two things follow from rules being data:

- **Recompute all scores** re-runs every lead you already have through the current rules, so
  changing your mind re-ranks the pipeline instead of only affecting new arrivals.
- Each lead stores the breakdown that produced its score, so the drawer shows exactly which
  rules fired and which did not.

`budget` and `timeline` are stored as ordinals 1-5 rather than strings, which is what lets
`at least` and `at most` work on them. The form's options come from one server-side catalog
(`server/src/catalog.ts`) that the rules editor reads too, so a rule can never reference a
value the form cannot produce.

## Layout

```
server/
  src/
    catalog.ts   the option catalog both surfaces read
    scoring.ts   the engine: pure, no I/O, exhaustively tested
    schemas.ts   zod schemas for every request body
    db.ts        node:sqlite bootstrap, default rules, settings
    repo.ts      lead queries, rescoring
    auth.ts      password check, signed session cookie
    app.ts       routes
    index.ts     entry point, static hosting, startup guards
  test/          scoring.test.ts (unit), api.test.ts (HTTP integration)
web/
  src/
    pages/       Intake, Dashboard, Rules
    api.ts       typed client
    router.tsx   ~25 lines, no routing library
    styles.css   the whole design system
```

## Security

Single user. The password lives in the environment and is compared as a SHA-256 digest with
`timingSafeEqual`. The session is an HMAC-signed, httpOnly, sameSite=lax cookie with a 12 hour
expiry, checked by an `onRequest` hook on every admin route rather than per handler. Every
query is parameterized, and the `sort` and `dir` params are matched against an allowlist
instead of being interpolated. Public endpoints are rate limited (form 10/min, login 8/5min),
bodies are capped at 128KB, and every body is parsed with zod before it reaches a handler.
