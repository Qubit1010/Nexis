# Dev Context — Aleem / NexusPoint (internal, not research-derived)

This is the company + personal anchor for developer-advisor. It is **not** cited research — it's who's building, with what, and for whom. Use it to tailor every blueprint to Aleem's actual skills, team, stack, and revenue model. Keep recommendations inside what NexusPoint can realistically deliver.

---

## Who's building

- **Aleem Ul Hassan** — founder, NexusPoint. BSAI (6th sem, Iqra University). Full-stack + AI/ML.
- **Core strengths:** MERN, Next.js, Python; AI/ML integration (LangChain, LangGraph, RAG, agentic AI); automation (n8n, Make, Claude Code); data science.
- **Strategic position:** moving from "freelancer selling websites" to "agency selling business outcomes powered by AI + web." **AI automation is the premium wedge — never lead a client with web dev.**

## Aleem's default stack (bias recommendations here unless a project needs otherwise)

| Layer | Default | Notes |
|---|---|---|
| Frontend | Next.js (App Router) 16, React 19, Tailwind 4, TypeScript | Proven in `sales-playbook-dashboard`, `content-engine-dashboard`, etc. |
| Backend | Next.js route handlers / server actions; Python/FastAPI when AI-heavy | Single-API-route pattern is the dashboard norm |
| Database | **Neon Postgres + Drizzle** (Business Brain default); Supabase when auth+realtime wanted | pgvector for embeddings |
| Auth | Better Auth (orgs/roles); Clerk/Supabase Auth as alternates | |
| AI | `@anthropic-ai/sdk`, OpenAI SDK, LangChain/LangGraph when stateful; Exa for research/retrieval | Claude-first |
| Background jobs | Inngest | |
| Email | Resend (+ React Email) | |
| Hosting | Vercel | |
| Automation | n8n, Make, custom Python, Claude Code | |
| Design/build | Figma, Canva, Stitch; Framer, Webflow, WordPress, Shopify for CMS | |

*The canonical worked example of this stack is `references/business-brain-v1-spec.md` (Next.js 16 / Neon / Drizzle / Better Auth / Inngest / Resend / Vercel, tenancy via a `scopedDb(businessId)` guard).*

## NexusPoint services & revenue mix (keeps recommendations realistic)

- Web design & dev ~60–70% · CMS ~15–20% · **AI automation ~5–10% (the growth lever)** · custom SaaS ~5–10% · data/marketing <5%.
- Productize AI automation + web as a combined premium offering. Default to productized offerings over bespoke scoping when possible.

## Team & delegation map (use in blueprint milestones)

| Person | Role | Route to them for |
|---|---|---|
| Areeba Noor | Frontend / UI-UX | Most web + design (Framer, Webflow, frontend) |
| Muzammil | Full-stack dev | Complex frontend / full-stack |
| Sher Nadir | Senior UI/UX | Large web design |
| Hafeez | Senior Webflow | Complex Webflow |
| Muhammad Usman | Workflow automation | Automation-heavy builds |
| Moiz Hussain | Ops / bidding | Upwork bidding, ops tasks |
| Kaleem | Data analyst / co-founder | Executive/strategic only |

When a blueprint implies work outside Aleem's direct execution, name who to loop in.

## Boundaries with sibling skills (don't duplicate them)

- **`senior-architect` / `senior-backend` / `senior-frontend`** — implementation-time guidance *inside a codebase* (writing/reviewing the actual code). developer-advisor is the **pre-project decision layer** (what to build, which stack, how it connects). Hand off to them once the blueprint is approved and code starts.
- **`claude-advisor`** — anything about the Claude *product* (surfaces, chat vs Code vs Cowork, models, plans, pricing). developer-advisor covers agentic-coding *technique* (Q6); route product questions to claude-advisor.
- **`claude-code-guide` agent** — granular Claude Code mechanics (hooks, specific settings, MCP config).
- **`ml-expert`** — actual ML implementation (training, EDA, model code). developer-advisor covers AI *application architecture* (RAG/agents/evals), not model training.
- **`ai-use-case-generator` / `proposal-generator` / `sales-playbook`** — client pitch, ROI framing, and closing. developer-advisor produces the technical blueprint; hand the sell to them.
- **`website-audit-system`** — auditing an existing prospect site. Different job.

## House rules for this skill

- Lead with the recommendation. Bullets over paragraphs. No em dashes in body text. No emojis.
- Simplest thing that ships — the whole skill biases toward YAGNI (pairs with the `ponytail` skill's philosophy).
- Cite research for load-bearing technical calls (`research-synthesis.md` → `sources.json`); flag honestly when a number isn't in the corpus and use `notebook-live-query.md`.
- Client-facing output stays authoritative-but-human; internal output is direct and terse.
