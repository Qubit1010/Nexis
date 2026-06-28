# Career Paths Playbook — AI/CS Graduate (2026)

For "what can I do after my AI degree," "what should I learn/explore next," and "is the job market
still good." Grounded in `research-synthesis.md` Q5. Calibrate to the user via `student-context.md`.
Lead with the macro reality, then the role, then the concrete next move.

## The macro reality (lead with the authoritative numbers)

- AI-skill demand is rising fast: McKinsey finds **"AI fluency" demand grew ~7x in two years**, faster
  than any other skill; WEF notes demand outpacing supply, pushing up wages for AI-capable workers.
- But the **entry-level pipeline is tightening:** Stanford HAI's 2026 AI Index reports employment for
  software developers **ages 22-25 fell ~20% from 2024**, and ~1/3 of organizations expect AI-driven
  workforce reductions. Translation for a new grad: the bar to *get in* is higher, and **a portfolio
  of shipped, real AI systems is the differentiator** — not coursework alone.

## The role split (pick a layer)

| Role | Layer | Core stack | Market (estimates — verify) |
|---|---|---|---|
| **Data Scientist** | Data & insight | SQL, stats, experimentation, viz | ~$140K median; demand flattening (~12% YoY) |
| **ML Engineer** | Model & training | PyTorch, model lifecycle, deployment | ~$165K median; demand ~+38% YoY |
| **AI Engineer / Applied AI** | App & orchestration | LLM APIs, RAG, vector DBs, agents, full-stack | ~$185K median; demand ~+74% YoY |
| **MLOps / LLMOps** | Deploy & operate | serving, monitoring, infra, scaling | high demand (one report ~+47% YoY) |
| **AI Product Manager** | Product | spec, eval, stakeholder, applied AI | ~$140-200K |
| **Research Scientist** | Research | publications, novel methods (PhD-track) | top labs; see `grad-school-playbook.md` |

Salary/demand figures are 2026 market/blog estimates — flag them as such and verify time-sensitive
numbers via the live notebook before quoting as fact.

## What to learn / explore next (the 2026 consensus)

Across roadmaps (Dataquest, Scrimba, Towards AI), the in-demand stack is:

1. **Python + software-engineering fundamentals** (clean code, testing, version control, APIs) —
   non-negotiable base.
2. **One frontier LLM API deeply** (e.g., the Anthropic Claude SDK is cited as a 2026 leader for
   agents).
3. **RAG + embeddings + vector DBs** (Pinecone/Weaviate/pgvector/Qdrant) and **agents**.
4. **Evaluation** (golden sets, LLM-as-judge, regression on prompt changes) and **tracing/
   observability** (Langfuse/LangSmith).
5. **Cost & latency engineering** (prompt caching, batching, model routing) and **deployment**
   (containers, cloud, monitoring).

**Prompt engineering is now table-stakes**, not a specialization. The biggest time-sink is learning in
the wrong order — go hands-on early; build, don't just watch.

## Honest timelines & the differentiator

- ~**6-12 months part-time** gets a coder to production-ready AI feature work; becoming a strong ML
  engineer is realistically ~**2 years at ~10 hrs/week** of deliberate study (Towards Data Science).
- The thing that gets interviews: **shipped projects that show business thinking, not notebooks.**
  Build real systems end-to-end (data → model/LLM → eval → deployed app).

## The founder/agency track (for the user who already builds)

If the user already ships real products or runs a business (see `student-context.md`), "what's next"
isn't only a job title — applied AI skills compound directly into client/product value. Weigh the
industry track (credential + comp + learning velocity at a strong team) against doubling down on the
business. Frame it as a portfolio decision, not a default toward employment.

For the master's-vs-industry question and research routes, hand to `grad-school-playbook.md`. For
turning this into a concrete learning roadmap, use the tutor engine (`learn-anything-playbook.md`).
Offer a Google Docs export for a personalized 6-12 month plan.
