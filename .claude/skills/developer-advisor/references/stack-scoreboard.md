# Stack Scoreboard — the problem-to-decision lookup

**Source basis:** distilled from `research-synthesis.md` (Q1–Q9), which cites `_research/sources.json`. This is the fast lookup layer: match the problem shape to the research-backed best-fit, lead with the recommendation, then the reasoning. **Load this on every invocation.** For depth or a contested call, open the matching Q-section of `research-synthesis.md`.

**There is no house stack. Do not carry a stack over from another project.** Every row below is a *conditional*: "if the problem looks like X, the evidence points to Y, because Z." Start from the actual problem and read off the rows that apply. Where the problem is genuinely novel or the corpus is thin, escalate per `research-fallback.md` (NotebookLM, then Exa live research) rather than forcing a familiar tool.

---

## "If the task is X → use Y → why" (the fast lookup)

### Architecture
| If the project is… | Start with | Why |
|---|---|---|
| Almost anything, < 50 engineers | **Modular monolith** | ~80% of microservices' org wins at ~20% of the cost [research Q1] |
| A component with genuinely independent scaling needs | Extract that one service | Microservices only earn their complexity per-constraint |
| Long-lived, domain-heavy | Clean Architecture / DDD (proportional) | Maintenance is 60–80% of lifecycle cost |
| Sporadic/event-driven workload | Serverless functions | Removes ops burden for the right shape |

**Microservices gate:** only if YES to ≥1 of — independent scaling needed · 50+ engineers · crystal-clear domain boundaries. Otherwise modular monolith.

### Frontend
| If you're building… | Use | Why |
|---|---|---|
| SaaS app / dashboard / authed product | **Next.js App Router** | Biggest hiring pool, deepest ecosystem, stable RSC |
| Marketing site / blog / docs / SEO | **Astro** | Zero JS by default, Lighthouse 95–100, cheapest hosting |
| Max performance / smallest bundle | **SvelteKit** | Compiles small; cost is a smaller hiring pool |
| Static content | SSG | Prerender, serve from CDN, fastest |
| Personalized / real-time | SSR | Fresh per request |
| Static shell + dynamic parts | ISR / PPR | Hybrid |

**CWV targets:** INP ≤200ms · LCP ≤2.5s · CLS ≤0.1. **A11y:** WCAG 2.2 AA.

### Backend & API
| If… | Use | Why |
|---|---|---|
| TS full-stack team | Node/Next server or NestJS | Ecosystem + one language |
| Python / AI-heavy | FastAPI | Type-hints, auto OpenAPI, async |
| CRUD-heavy startup | Django | Batteries included |
| Real perf need at scale | Go | Throughput |
| Public API | REST | Dominant, cacheable, documentable |
| Internal TS full-stack | tRPC | No API boundary, end-to-end types |
| Many clients / relational | GraphQL | One request, many shapes |

### Database
| If data is… | Use | Why |
|---|---|---|
| Anything relational (default) | **Postgres** | Covers 95%: JSONB, FTS, pgvector, PostGIS, time-series |
| Needs auth+storage+realtime too | Supabase | Whole backend platform |
| Needs branching / scale-to-zero | Neon | Serverless Postgres, ~500ms cold start |
| Genuinely document-shaped | MongoDB | Flexible schema, horizontal writes |
| Edge-distributed | Turso / D1 | SQLite at the edge |
| Vector search | pgvector (in Postgres) first | Avoid a separate DB until you must |

**ORM:** Drizzle (SQL-first, fast cold starts) vs Prisma (abstraction, mature). **Scaling:** reads ≥80% → read replicas; writes dominate → bigger compute. Index to query patterns.

### AI / LLM
| If the agent… | Use | Why |
|---|---|---|
| Makes 1 call / simple RAG | Direct SDK | Simple composable patterns beat frameworks |
| Calls 2–3 tools linearly | Direct SDK (`maxSteps`) / OpenAI Agents SDK | Framework adds friction |
| Linear RAG pipeline | LangChain (LCEL) | Fast, huge ecosystem |
| Stateful, branching, human-in-loop | LangGraph | State mgmt is where it earns complexity |
| Needs machine-readable output | Structured outputs (JSON schema) | Never regex JSON from prose |
| Ships to production | Evals (eval-driven dev) + logging | Only reliable way to improve |

**Order of escalation:** single prompt → +retrieval (RAG) → agentic RAG → multi-agent. Don't skip ahead.

### Mobile
| If… | Build | Why |
|---|---|---|
| B2B SaaS / internal / content | Web app | Users find you via search/links |
| Need home-screen + push + offline | **PWA** | ~80% of native UX at ~40–60% of cost |
| Deep hardware / AR / games / app-store discovery | Native | Only case native clearly wins |
| Cross-platform + React/web team | React Native + Expo | One codebase incl. web; New Arch default |
| Pixel-perfect UI / no web reach | Flutter | Bespoke UI engine |

### Hosting
| If… | Deploy on | Why |
|---|---|---|
| Next.js SaaS, early stage | **Vercel** | Best DX, $20/seat covers early traffic |
| High bandwidth / global edge / cost-sensitive | Cloudflare | 330+ PoPs, ~free bandwidth, 70–95% cheaper at scale |
| Full-stack w/ persistent state | Railway / Render | Long-running processes (weigh Railway reliability) |
| Want VM control / global | Fly.io | Docker-first micro-VMs |
| Max flexibility, have DevOps | AWS | Everything, but you run it |
| Escape platform pricing | Hetzner / Coolify / Kamal | Cents/month VPS |

**Serverless vs containers:** event-driven/sporadic → serverless; sustained RPS / long-running / stateful → containers. Most systems use both.

---

## The DORA scoreboard (how "good delivery" is measured)

| Metric | What it measures | Elite signal |
|---|---|---|
| Deployment frequency | Throughput | On-demand / multiple per day |
| Lead time for changes | Throughput | < 1 day |
| Change failure rate | Stability | < 5% |
| MTTR | Stability | < 1 hour |
| Reliability | Operational | Meets SLOs |

Pipelines < 10 min · shift-left + shift-right as a loop · trunk-based (+ feature flags, merge queue) · security shifted into daily work (peer review + automation).

---

## Universal heuristics (tie-breakers, applied only after fit)

These break ties between options that are already a good fit for the problem. They never pre-empt the problem analysis.

1. **Best-fit first** — the problem's real constraints (scale, data shape, latency, team, timeline) decide the stack. Everything below is secondary.
2. **Simplest thing that genuinely solves it** — monolith before microservices, single call before agents, PWA before native, pgvector before a vector DB. Only when each is actually sufficient for the problem.
3. **Boring wins ties** — between two equally-fit options, proven + deep-docs + big-ecosystem beats novelty. A tie-breaker, not a stack selector.
4. **Capability as a tie-breaker only** — when two options fit equally, a familiar one is fine; when the best-fit tool is unfamiliar, recommend it anyway and flag the ramp-up.
5. **Ship measurably** — DORA + evals; you can't improve what you don't measure.
6. **AI-in-the-loop, human-on-the-hook** — agents draft, humans review; a fresh agent grades, not the one that did the work.
