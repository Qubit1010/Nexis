# Surface Comparison - Which Claude for Which Task (2026 Scoreboard)

**Source basis:** Distilled from `research-synthesis.md` Q2/Q4/Q8 (237-source NotebookLM synthesis). `[sN]` -> `_research/sources.json`. **Honesty rule:** if a fact isn't here or in the notebook, don't invent it - run the live fallback.

**The frame:** Anthropic ships **one engine (the same models) behind many doors**. Pick the door by *who is doing the work* and *how much autonomy the task needs* [s111, s195].

---

## The matrix

| Surface | What it is | Best for | Who | Autonomy | Context |
|---------|-----------|----------|-----|----------|---------|
| **Claude.ai chat** (Projects, Artifacts) | Web chat; Projects = persistent RAG workspaces, Artifacts = interactive HTML/React/SVG/diagram outputs | Writing, analysis, brainstorming, UI prototyping, research | Anyone; human-in-the-loop every turn | Low (you steer each turn) | 200K Pro/Team, 500K Enterprise [s77, s194] |
| **Claude Code** | Terminal/IDE agentic coding (VS Code, JetBrains); edits files, runs tests, stages Git | Multi-file refactors, debugging, feature builds, CI/CD | Software engineers | High (autonomous loops, you review) | Up to 1M (Opus 4.8 / Sonnet 4.6) [s62, s77] |
| **Claude Cowork** | Desktop autonomous agent in a local sandboxed VM with folder access; GUI, no terminal | Excel/PPT deliverables, file ops, scheduled reports, SaaS clicking | Non-technical knowledge workers | High (plan-to-action; ask vs act modes) | Model-dependent [s64, s195] |
| **Claude Desktop app** | Native macOS/Windows unifying Chat/Code/Cowork; local MCP | Friction-free daily use, local integrations, Quick Entry overlay | Power users | Mixed | ~180-250MB RAM vs 1.2-2GB browser [s67] |
| **Claude mobile** (Dispatch) | Phone app that remote-controls your desktop agents | Dictate/monitor/approve on the go | Founders/devs away from desk | Remote trigger | Dispatch approvals expire 30 min [s68, s194] |
| **Claude API** | Programmatic access (Anthropic / Bedrock / Vertex / Foundry) | Custom features, unattended automation, high-volume async, ZDR | Developers, architects | Full (you build the loop, or use Agent SDK) | Up to 1M at standard rates [s2, s6] |

---

## "Best for X" decision table

| If the task is... | Use | Why |
|-------------------|-----|-----|
| Drafting, thinking, one-off analysis, a quick interactive artifact | **Claude.ai chat** | Human-in-the-loop, no setup [s111] |
| Editing a codebase, refactor, tests, PRs, CI work | **Claude Code** | Repo-aware agentic loops; 87.6% SWE-bench Verified [s62, s77] |
| Repeatable **non-code** ops (sort files, build a spreadsheet/deck, weekly report) | **Claude Cowork** | Desktop autonomy, business deliverables, `/schedule` [s145, s194] |
| An **unattended/automated** workflow or a feature inside your own product | **Claude API** (Agent SDK) | Subscriptions forbid unattended automation; API gives control + ZDR [s183, s219] |
| A client wants a workflow built and asks "can Claude Code do it?" | See the playbook below | Feasibility -> surface -> shape [s183] |

---

## The marquee question: "A client wants a workflow built - is Claude Code right, and which surface is best?"

Answer in this order:

1. **Feasibility:** Almost always yes for digital, multi-step work. Claude can read files, call tools/APIs via MCP, run code, browse, and act on a schedule [s62, s183].
2. **Pick the surface by who runs it and where it lives:**
   - **It's a coding/repo task, run by a developer** -> **Claude Code** (or headless Claude Code / Agent SDK for scheduled runs) [s10, s150].
   - **It's an ongoing automated/unattended service, or embedded in the client's product** -> **Claude API + Agent SDK + MCP**. Running automation on a Pro/Max/Team subscription violates ToS [s183, s219].
   - **It's desktop knowledge-work the client's non-technical staff will run themselves** (reports, file wrangling, deck/sheet building) -> **Claude Cowork** [s111, s194].
   - **It's "help me think/draft", human in the loop** -> **Claude.ai chat + a Project** [s111].
3. **Shape it:** trigger -> steps -> tools (MCP servers by name) -> model routing (70/20/10) -> guardrails (hooks, ask-before-acting, ZDR if regulated) [s69, s156, s183].
4. **Name the tradeoff:** Code/API = most control + auditability but needs a developer; Cowork = fastest for non-technical ops but desktop must stay awake and it's not yet in the Compliance API; chat = zero setup but no autonomy [s145, s183].

For NexusPoint client framing, this maps cleanly onto the AI-automation wedge - hand the actual pitch to **ai-use-case-generator** / **sales-playbook**.

---

## How to use this file
- For "which should I use" / "can I do X", lead with the pick, cite the one fact behind it, then the tradeoff.
- Deeper detail per surface: `claude-code-guide.md`, `claude-cowork-guide.md`, `building-with-claude.md`, `plans-and-pricing.md`.
- Anything version/price-sensitive and not here: run `notebook-live-query.md`.
