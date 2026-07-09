# Project Intake Framework — from vague idea to build blueprint

This is the marquee flow of developer-advisor. When Aleem describes a project ("I want to build X", "a client needs Y", "how would I architect Z"), **don't jump to a stack.** Run a structured discovery, then output a blueprint. This is the pre-project decision layer — the `senior-*` skills take over at implementation time.

---

## Step 1 — Extract what's already known (don't ask what you can infer)

Read the prompt first and silently fill in as much of the intake grid as you can. Only ask about the gaps that would actually change the recommendation. Never fire all questions blindly — that's the fast way to annoy Aleem.

**The intake grid (what you need before recommending a stack):**

| Dimension | What to pin down | Why it changes the answer |
|---|---|---|
| **Problem & users** | What problem, for whom, what's the core job-to-be-done | Determines whether it's a content site, app, API, or agent |
| **Project type** | Client project · internal tool · product/SaaS · one-off | Changes delivery constraints + who maintains it |
| **Scale & load** | Expected users, read/write ratio, traffic pattern, data volume | Monolith vs services, DB choice, hosting, serverless vs containers |
| **AI surface** | Is there an AI/LLM feature? RAG, agent, chat, automation? | Whole extra layer (Q5) + DB (pgvector) + provider choice |
| **Constraints** | Timeline, budget, team available, must-use tech | Boring-stack vs bespoke; delegate map (Areeba/Muzammil/etc.) |
| **Integrations** | Auth, payments, email, third-party APIs, existing systems | Pulls in specific tools; can dictate framework |
| **Delivery context** | Who runs it after ship, hosting preference, compliance | Hosting + handoff + maintenance model |
| **Platform** | Web · mobile · both · desktop | Q2/Q7 branch; PWA-vs-native gate |

## Step 2 — Ask the smallest set of high-leverage questions

Use `AskUserQuestion`, batched (2–4 at once), only for the gaps that move the recommendation. Adaptive: skip anything the prompt already answered. Typical high-value questions:

1. **"What's the core thing it has to do, and who uses it?"** (if problem/users unclear)
2. **"Is this a client deliverable, an internal tool, or a product you're launching?"** (delivery context)
3. **"Roughly what scale — a handful of users, hundreds, or public/viral?"** (scale)
4. **"Any AI/automation in it, or is it a standard app?"** (AI surface)
5. **"What's the constraint that matters most — timeline, budget, or a tech you must use?"** (constraints)
6. **"Web, mobile, or both?"** (platform)

Keep it to one round if you can. If the ask is concrete enough already, skip straight to the blueprint and state your assumptions.

## Step 3 — Output the Project Blueprint

A blueprint is the deliverable. Structure (adapt length to project size — a small tool gets a tight version):

### 1. Problem statement
One or two sentences: what we're building, for whom, and the core job. Restate so Aleem can correct a wrong assumption before you design on top of it.

### 2. Recommended architecture
Name the pattern (almost always **modular monolith** to start — see `research-synthesis.md` Q1) and one line on why it fits this scale/team. Note the one thing that would later justify splitting a service.

### 3. Stack table (cite the why)
| Layer | Choice | Why (cite research) |
|---|---|---|
| Frontend | … | … |
| Backend | … | … |
| API | … | … |
| Database | … | … |
| AI layer (if any) | … | … |
| Auth / payments / email | … | … |
| Hosting | … | … |

Pull defaults from `stack-scoreboard.md`; deviate only with a stated reason. Every row should have a "why" a client would accept.

### 4. Data model sketch
The core entities and their relationships (bullet list or a tiny ERD in prose). Enough to expose the hard modeling decisions (multi-tenancy? relational vs document? vector data?), not a full schema.

### 5. How the pieces connect
The wiring: auth flow, API contracts between frontend/backend, where the AI calls sit, how data flows, caching points, third-party integration seams. This is where architecture becomes concrete.

### 6. Best-practices checklist for this build
Tailored, not generic: the testing approach (pyramid vs trophy), CI/CD baseline, security must-dos (OWASP items relevant to *this* app), CWV/a11y targets if web, eval strategy if AI. From `research-synthesis.md` Q8.

### 7. Build milestones
A rough phased path (M0 scaffold → … → ship), sized to the timeline. Where relevant, map phases to the team (Areeba: frontend/design; Muzammil: full-stack; Muhammad Usman: automation — see `dev-context.md`) or to a Claude Code agentic workflow (spec → plan → build → review, Q6).

### 8. Risks & what-not-to-do
The 2–4 things most likely to go wrong or the tempting-but-wrong choices for this project. Run the plan through `what-not-to-do.md` before delivering.

### 9. Offer the follow-ups
End with concrete next steps: "Want me to (a) write the spec for spec-driven development, (b) scaffold M0, (c) generate a client-facing version of this, or (d) go deeper on [the contested decision]?" Offer to save it as a Google Doc via `scripts/save_blueprint.py`.

---

## Modes this framework serves

- **Full blueprint** (default for "build X") — run all 3 steps.
- **Single decision** ("Postgres or Mongo for this?", "tRPC or REST?") — skip intake, answer directly from the scoreboard + research, give the decision + the one-line why + the deviation condition. No blueprint needed.
- **Architecture review** ("here's my stack, critique it") — map their choices against the scoreboard, flag mismatches and `what-not-to-do` hits, recommend changes with reasons.

## Rules
- Lead with the recommendation, then the reasoning (Aleem's communication style).
- No em dashes in body text; no emojis.
- Cite research for load-bearing calls; if the local refs don't cover it, use `notebook-live-query.md`.
- Client-facing blueprints get NexusPoint framing (positioning AI automation as the premium wedge) and hand deep pitch/ROI work to `ai-use-case-generator` / `proposal-generator`.
- Don't over-engineer the recommendation. The whole skill biases toward the simplest thing that ships.
