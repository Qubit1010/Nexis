# Web Stack Playbook (frontend + backend + database)

**Source basis:** `research-synthesis.md` Q2–Q4 (frontend `[s27]`–`[s52]`, backend/API `[s53]`–`[s77]`, database `[s78]`–`[s103]`). Load for any "how do I build the web app" question.

## Frontend
**Default: Next.js App Router + React + TS + Tailwind** — biggest hiring pool, deepest ecosystem, RSC stable [s39][s40].
- **Astro** for content/marketing/docs/SEO — zero JS default, Lighthouse 95–100, cheapest hosting [s29][s32].
- **SvelteKit** for smallest bundle / max perf, at the cost of a smaller hiring pool [s29][s31].
- **Rendering:** SSG (static content, fastest) · SSR (personalized/fresh) · ISR (static + background refresh) · PPR (shell + streamed holes) · RSC (server-render before bundling) [s45][s46][s48].
- **Targets:** CWV — INP ≤200ms, LCP ≤2.5s, CLS ≤0.1 [s38]. A11y — WCAG 2.2 AA, 24×24px tap targets, semantic HTML [s38][s34].
- App Router hygiene: route groups, type-safe params, streaming, no fetch waterfalls, server actions [s40][s36].

## Backend
**Match the team first, then the workload** [s54]. RPS benchmarks are mostly noise [s53].
- **Node/NestJS** — TS full-stack, real-time, API-first [s54][s57].
- **FastAPI** — Python/AI-heavy; auto OpenAPI + Pydantic [s54][s55].
- **Django** — CRUD-heavy startups, batteries included [s54].
- **Go** — genuine high-throughput needs [s53]. **Bun** — fast, newer, watch maturity [s57].

## API style (different layers, often combined)
- **REST** — public APIs, CRUD, cacheable; still ~70% of listings [s58][s59]. OpenAPI 3.1 universal [s60].
- **tRPC** — internal TS full-stack: no API boundary, end-to-end types [s58][s61].
- **GraphQL** — many clients / relational traversal in one request [s59][s62].
- **gRPC** — sub-10ms internal calls [s66]. Most SaaS combine two [s61].
- **Design:** resource URIs [s65], backward-compatible-first then version [s76], cursor pagination [s69], consistent error envelopes + status codes [s70], idempotency keys, rate limits, docs [s65][s66]. Anchor on Stripe/GitHub/Google/Microsoft conventions [s63][s68].

## Database
**Default: Postgres** — covers ~95% (JSONB, FTS, pgvector, PostGIS, TimescaleDB) [s80][s86].
- **Neon** — serverless Postgres, scale-to-zero (~500ms), branching, best Vercel fit [s81][s82].
- **Supabase** — Postgres + auth + storage + realtime [s79][s82].
- **Turso/D1** — edge SQLite [s81][s84]. **MongoDB** — genuinely document-shaped + horizontal writes [s86]. **PlanetScale** — MySQL/Vitess extreme scale [s84].
- **ORM:** Drizzle (SQL-first, fast cold starts) vs Prisma (abstraction, mature) [s88][s92].
- **Vector:** start with pgvector inside Postgres before adding a dedicated vector DB [s87].
- **Caching:** Redis cache-aside (hash params → key → TTL) offloads reads, cuts DB cost [s89][s91]; design keys to access patterns [s93].
- **Scaling:** reads ≥80% → read replicas; writes dominate → bigger compute [s102]. Index to query patterns (order-of-magnitude gains) [s103]. Partitioning for huge tables [s99]; multi-tenancy via `tenant_id` column vs schema-per-tenant [s100].

## Checklist for a web blueprint
- [ ] Frontend framework matched to content-vs-app.
- [ ] Rendering strategy chosen per route type.
- [ ] Backend matched to team language; API style (often REST+tRPC).
- [ ] Postgres unless a document/edge case proven; ORM picked.
- [ ] Auth, caching, and scaling seams named.
