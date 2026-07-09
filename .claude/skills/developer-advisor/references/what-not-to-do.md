# What Not To Do — the anti-pattern filter

**Source basis:** `research-synthesis.md` Q1–Q9 (cites `_research/sources.json`). Run every recommendation and blueprint through this before delivering. These are the tempting-but-wrong 2026 defaults.

## Architecture
- **Don't start with microservices** because it feels "grown-up" or because Netflix does it. It's a scale mismatch; you buy an order-of-magnitude more observability/debugging cost for nothing [s1][s5]. Modular monolith first [s8].
- **Don't treat architecture as a maturity ladder** (monolith → microservices → cloud-native). Real systems don't work that neatly; choose by constraint [s3].
- **Don't over-apply Clean Architecture/DDD** to a small CRUD app — proportional to longevity/complexity [s11].

## Frontend
- **Don't pick a framework by tribe/hype.** "Next.js is bloated / Astro is only blogs / SvelteKit is niche" are all wrong-when-absolute [s31]. Pick by content-vs-app.
- **Don't reach for chase-the-new** when the boring consolidated stack (Next.js/React/TS/Tailwind) wins on hiring + docs + ecosystem [s39].
- **Don't ship without CWV/a11y baselines** — retrofitting WCAG 2.2 and Core Web Vitals is far more expensive than building them in [s38].

## Backend / API
- **Don't choose a backend on RPS benchmarks.** Most backends never hit the scale where it matters; match the team's language first [s53][s54].
- **Don't default to GraphQL** for a single-client CRUD app — REST is simpler, cacheable, and dominant [s58]. Don't version an API preemptively; prefer backward-compatible additive changes [s76].
- **Don't ship inconsistent error responses / no pagination / no idempotency** — that's integration debt that's expensive to unwind [s67].

## Database
- **Don't reach for MongoDB by default.** Postgres covers ~95% incl. JSON and vectors; use Mongo only for genuinely document-shaped data [s80][s86].
- **Don't add a dedicated vector DB** before trying pgvector inside Postgres [s87].
- **Don't scale compute blindly** — if reads are ≥80%, replicas beat a bigger box; index to query patterns first [s102][s103].

## AI / LLM
- **Don't reach for a framework first.** Simple composable patterns beat complex frameworks; a single call or direct SDK often wins [s125][s118].
- **Don't adopt LangGraph early** for a linear 2–3-tool flow — you pay the abstraction tax on every debug/upgrade [s115][s118].
- **Don't regex JSON out of prose** — use schema-validated structured outputs [s113].
- **Don't ship an LLM app without evals** — it's the only reliable way to improve [s126].
- **Don't skip rungs** — prompt < RAG < agentic RAG < multi-agent; add complexity only when the problem forces it.

## Agentic coding
- **Don't let the agent jump straight to code** — it solves the wrong problem. Explore → plan → code → commit [s140].
- **Don't dump everything into context** — bloat is the #1 token waste; curate [s136].
- **Don't let the agent grade its own work** — use a fresh reviewer [s140][s144].
- **Don't code by vibes at scale** — write a spec with testable acceptance criteria [s138].

## Mobile
- **Don't build native by default.** A PWA is ~80% of the UX at ~40–60% of the cost; go native only for deep hardware/AR/app-store-discovery [s162][s164].
- **Don't pick RN vs Flutter on FPS charts** — decide on team skills + hiring market [s159].
- **Don't start a new RN/Expo app on the Old Architecture** — SDK 55+ is New-Architecture-only [s172].

## Practices / hosting
- **Don't chase test coverage %** — risk-based testing is the right default [s181]. Don't treat the pyramid as dogma; use the trophy for frontends [s179].
- **Don't run heavyweight external change-approval boards** — peer review + automation outperforms them [s201].
- **Don't ignore the egress trap.** Vercel Hobby is capped and bans commercial use; at high bandwidth Cloudflare is 70–95% cheaper [s205][s217].
- **Don't compare hosting on sticker price** — normalize to one workload; credit-based pricing hides the real bill [s214][s218].
- **Don't force one compute model everywhere** — serverless and containers each fit different workloads; most systems use both [s210].

## Meta
- **Don't quote a number or "best practice" that isn't in the corpus.** If it's not in `sources.json` / the synthesis, say so and use `notebook-live-query.md` before guessing.
- **Don't over-engineer the recommendation.** The whole skill biases toward the simplest thing that ships.
