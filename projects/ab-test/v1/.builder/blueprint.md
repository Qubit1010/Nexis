---
project: LeadQ
source: derived-in-run (developer-advisor Project Architect flow, brief supplied by user)
received: 2026-08-31T18:22:00Z
platform: web
---

# Blueprint — LeadQ

## 1. Problem Statement

Aleem receives inbound leads with no consistent capture point and no consistent way to
decide which ones deserve his time. Today the signal lives in his head. He needs three
things that work together:

1. A **public intake form** a prospect can fill in without an account (name, company,
   budget, timeline, what they need).
2. **Automatic qualification** of every submission against rules **he can change himself**,
   without editing code or redeploying.
3. An **internal triage surface** where he sorts by score and moves each lead through
   contacted / qualified / dead.

Non-negotiable: the scoring rules are data, not code. If a rule change needs a developer,
the tool has failed its main job.

**Who uses it:** exactly one operator (Aleem) plus anonymous public submitters.
**Where it runs:** his laptop first. Deployable to a host later without a rewrite.

## 2. Scale & Constraints

| Constraint | Reality | Consequence for the design |
|---|---|---|
| Users | 1 authenticated operator | No user table, no roles, no org model, no invites. A single shared secret is the whole auth model. |
| Volume | Tens to low hundreds of leads | No pagination infrastructure, no search index, no caching layer, no background jobs. |
| Environment | Local first, deploy later | The datastore must need zero install. Portability matters more than write throughput. |
| Public surface | One anonymous POST endpoint | That endpoint is the only untrusted input path, and gets the full validation + abuse budget. |
| Operator | Solo, non-DBA | Rules edited through the UI, seeded with a working default set. |

## 3. Architecture

**Modular monolith, single process.** One deployable, feature-grouped internals
(`lib/scoring`, `lib/leads`, `lib/rules`, `lib/auth`). This is the default for anything
under 50 engineers, and there is exactly one here; microservices fail their own gate on all
three criteria (no independent scaling need, no team-size pressure, no domain boundaries
worth a network hop).

```
  Public browser  --POST /api/leads-->  +---------------------------------------------+
                                        |  Next.js App Router (one process, :3000)    |
  Operator browser --session cookie-->  |                                             |
                                        |  app/       form, login, dashboard, rules   |
                                        |  app/api/   route handlers = HTTP contract  |
                                        |  lib/scoring  PURE rules engine (no I/O)    |
                                        |  lib/rules    rules + thresholds, rescoring |
                                        |  lib/leads    lead persistence + filtering  |
                                        |  lib/db       node:sqlite, boot migrations  |
                                        +----------------------+----------------------+
                                                               |
                                                               v
                                                     data/leads.db (one file)
```

The scoring engine is deliberately isolated from everything: it takes a lead object, a rule
list and band thresholds, and returns a score, a band and a breakdown. No database, no
request, no framework. That is what makes it testable and what makes the rules feel live.

## 4. Stack

| Layer | Choice | Why (for THIS problem) |
|---|---|---|
| Frontend / rendering | **Next.js 16 App Router + React 19** | The scoreboard's row for an authed product/dashboard. Server components render the lead table with no client fetch waterfall; the same process serves the public form. One toolchain instead of two, which matters when the whole team is one person. |
| UI | **Plain CSS + CSS Modules, no framework** | Next has CSS Modules built in. Tailwind would add a dependency and a config surface to produce a *more* generic-looking result, and this build has an explicit anti-generic bar. Hand-authored tokens give the design phase full control at zero dependency cost. |
| Backend | **Next.js route handlers (same process)** | The API is 7 endpoints for one user. A separate Express/Fastify service on :4000 would add a process, a CORS surface, a second deploy target and duplicated types, and buy nothing. Splitting it later is a directory move, not a rewrite. |
| API style | **REST/JSON** | Single client, CRUD-shaped, no field-selection problem. GraphQL for a single-client CRUD app is the classic over-choice. Server Actions were rejected deliberately: an explicit HTTP contract is testable without a Next request context, and survives a future split. |
| Database | **SQLite via `node:sqlite` (Node 24 built-in)** | The hard constraint is "runs locally" for one user. Postgres is the right relational default at multi-user scale, but here it would mean asking a solo operator to install and run a server for a few hundred rows. SQLite is a file, needs no install, and `node:sqlite` ships inside Node 24, so the database layer costs **zero dependencies** and cannot fail a native build. |
| Data access | **Hand-written SQL, prepared statements** | ~11 queries total. Drizzle or Prisma would be a dependency, a schema DSL, a generate step and a migration runner to save under 100 lines of SQL. Every statement is parameterized, which is the actual security requirement. |
| Auth | **Single shared secret + HMAC-signed httpOnly cookie** (Web Crypto) | One user means no identity model. `ADMIN_PASSWORD` gates login, `SESSION_SECRET` signs a short expiring token. No auth provider, no user table, no OAuth round trip, no library. Web Crypto is in the runtime already. |
| Validation | **Zod 4** | The only real runtime dependency added. One public untrusted endpoint plus a rule editor that writes an operator DSL to the database: both need schema validation at the boundary, and hand-rolling that is where injection bugs live. |
| Tests | **Vitest 4** | Ecosystem default for a TS project, no config ceremony, runs the pure engine and the route handlers in one process. |
| Hosting | **Local `next dev` / `next start` now; container host (Railway/Fly/VPS) later** | Flagged honestly: SQLite needs a persistent disk, so the deploy target is a container host with a volume, **not** Vercel serverless. If Vercel is ever required, swap `lib/db.ts` for Postgres/Turso; nothing above that module changes. |

## 5. Data Model Sketch

- **leads** — the submission plus its derived qualification. Score, band and breakdown are
  denormalized onto the row so the dashboard can sort in SQL without recomputing, and are
  refreshed whenever the rules change.
- **rules** — one row per scoring rule: `field`, `operator`, `value`, `points`, `enabled`,
  `position`. This table is the "rules I can adjust".
- **settings** — key/value; currently the two band thresholds (hot / warm).

Seeded with a working default rule set on first boot so the tool is useful before it is
configured.

## 6. Best-Practices Checklist

- **Testing shape: trophy.** Static types as the base, a thick integration layer against the
  real route handlers and a real (temporary) SQLite file, plus dense unit tests on the
  scoring engine because that is where the branching logic actually lives.
- **Priority order for tests:** (1) authz — the admin surface must not be reachable
  unauthenticated; (2) there is no money path in this product, so that budget moves to
  (3) the core loop: submit -> score -> triage -> rescore-on-rule-change.
- Consistent error envelope `{ error, code, details? }` on every endpoint.
- Validate at the boundary with Zod on both the public submission and the rule editor.
- Parameterized SQL only.
- Secrets in env only; ship `.env.example`.
- WCAG 2.2 AA: contrast, visible focus, labelled inputs, 44px targets, reduced-motion.

## 7. Milestones

- **M0** Schema, migrations, seeded default rules, the pure scoring engine + its tests.
- **M1** Public form -> `POST /api/leads` -> scored row in the database.
- **M2** Login + session gate; dashboard table with sort, filter, status transitions.
- **M3** Rule editor with rescore-on-save.
- **M4** Test suite, review, polish.

## 8. Risks

| Risk | Severity | Mitigation |
|---|---|---|
| `node:sqlite` is marked experimental in Node 24 and prints a warning | Medium | API verified working before adoption. It is isolated behind `lib/db.ts` (~80 lines); swapping to `better-sqlite3` or Postgres touches one file. Accepted deliberately over a native-compile dependency on Windows. |
| SQLite blocks a Vercel-serverless deploy | Medium | Stated up front, not discovered later. Deploy target is a container host with a volume. The escape hatch is the same one file. |
| A single shared password is weak auth if exposed publicly | Medium | Correct for one local user; flagged as the first thing to replace if this ever becomes multi-user. Cookie is httpOnly + signed + expiring, password compared in constant time. |
| Public endpoint attracts spam once deployed | Low | Honeypot field + a small in-process rate limiter. A real deployment should add a captcha or a proxy-level limit. |
| Additive rules can stack unintuitively (two budget tiers both firing) | Low | Not hidden: the per-lead breakdown shows exactly which rules fired and what each contributed. Transparency instead of a cleverer engine. |

## 9. Explicitly Out of Scope

Multi-user accounts, roles, teams. Email notifications or sequences. CRM sync. File
uploads. Analytics/reporting charts. Lead assignment. Full-text search. Pagination.
Import/export. Webhooks. AI-written rules. These are all reachable from this schema; none
are in the brief.
