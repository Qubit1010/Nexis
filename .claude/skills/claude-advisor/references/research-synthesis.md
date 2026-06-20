# Claude - Complete Guide 2026: Research Synthesis (MASTER)

**Research basis:** Synthesis of **237 unique 2026 sources** imported into the NotebookLM notebook *Claude - Complete Guide 2026 (NexusPoint)* (id `63a3705e-e871-4830-83a5-966f584a3142`) via 8 deep web-research passes, then a per-question `ask --json` synthesis (Q1-Q8).

**Citations:** `[sN]` resolves to the global source index N in `_research/sources.json` (`sources[]` -> title + url). The raw per-question answers + their local citation arrays live in `_research/q1..q8.json`.

**Honesty rule:** Every load-bearing number traces to a 2026 source. Some striking specifics (exact customer ROI figures, the newest model names) are corroborated only by NotebookLM's own synthesized analytical reports (`s118`, `s183`, `s193`, `s194`, `s195`, `s196` - these have no external URL); where a claim rests only on those, treat it as directional and verify via the live notebook before quoting it to a client. If a number isn't here or in the notebook, say so - don't invent.

**Date:** 2026-06-10

> Note on velocity: Claude's products and model versions move fast. The numbers below were current on 2026-06-10. For anything version/price/feature-sensitive, run the live fallback (`references/notebook-live-query.md`) before treating a figure as today's truth.

---

## Q1 - How Claude Works + the 2026 Model Lineup

**Bottom line:** In 2026 Claude is not one model but a **tiered system** - route by task complexity and cost, don't default to the flagship.

**The lineup (per-million-token API pricing):**
- **Claude Haiku 4.5** - $1 in / $5 out, 200K context. Fastest, cheapest; matches old Sonnet 4 coding at high speed; supports extended thinking, prompt caching, computer use [s78, s79, s92].
- **Claude Sonnet 4.6** - $3 in / $15 out, **1M context at standard rates** (the long-context surcharge from 4.5 is gone). The "production sweet spot," near-Opus intelligence at a fraction of cost; ~79.6% SWE-bench Verified; strong agentic coding + browser automation (72.5% OSWorld) [s92, s98, s99].
- **Claude Opus 4.8** - $5 in / $25 out (Fast Mode $10/$50 for ~2.5x faster output), 1M context / up to 128K output. Best for the hardest reasoning, multi-step agentic workflows, deep science/math; "adaptive thinking" picks its own reasoning depth; released May 2026 (4.6 and 4.7 still active at the same price) [s86, s89, s92].
- **Claude Fable 5** - $10 in / $50 out, an ultra-premium tier for multi-day, highly autonomous projects [s71, s76]. *(Newest tier; corroborate before quoting.)*

Anthropic dropped the Opus tier price ~67% vs earlier generations [s20, s92].

**Which model when (plain terms):**
- **Haiku 4.5** - high-volume/simple/repetitive where a wrong answer is cheap: classification, basic extraction, request routing, summarization, sub-agents [s34, s79].
- **Sonnet 4.6** - your **default for ~80% of daily work**: coding, PR review, content, chatbots, day-to-day workflows. Using Opus for standard dev is wasted money [s10, s86, s99].
- **Opus 4.8** - reserve for the hardest, highest-stakes 10-15%: massive multi-file refactors, graduate-level reasoning, financial audits, long unattended agents [s48, s86, s193].

**Cost optimization (the 3 levers):**
- **70/20/10 routing** - 70% Haiku, 20% Sonnet, 10% Opus saves thousands/month [s156, s183].
- **Prompt caching** - cached input reads cost **10% of base** (Sonnet 4.6 drops $3 -> $0.30/M) [s182, s92].
- **Batch API** - 50% off all tokens for non-urgent jobs (≤24h) [s54, s182]. Stacking caching + batch can cut input costs ~95% [s156].

Full detail: `references/claude-models.md`.

---

## Q2 - The Surfaces Compared (one engine, many doors)

Anthropic frames it as **"one engine, three jobs"**: Chat, Code, and Cowork all run the same models but give different hands to different audiences [s111, s195].

- **Claude.ai chat (Projects + Artifacts)** - web conversational interface. **Projects** = persistent RAG workspaces (up to 20 files, 30MB each; custom instructions); **Artifacts** = standalone interactive assets (HTML sites, React, SVG, Mermaid) in a side panel. For writers/researchers/marketers/teams who want a human in the loop every turn. Context: 200K (Pro/Team) / 500K (Enterprise) [s77, s194, s210].
- **Claude Code** - terminal- and IDE-native agentic coding (VS Code, JetBrains). Maps the repo, edits files, runs shell/tests, stages Git. For engineers. **64.3% SWE-bench Pro / 87.6% Verified**; authors **80%+ of Anthropic's own production code** [s27, s29, s62]. Use a `CLAUDE.md` for standing rules; `Shift+Tab` -> Plan Mode [s111, s179].
- **Claude Cowork** - desktop **autonomous agent for non-technical workers**; same agentic architecture as Code but a GUI, running in a local isolated VM with folder access (no terminal). GA April 2026. Builds Excel/PPT deliverables, sorts files, runs scheduled reports; `/schedule` for recurring work [s64, s145, s195].
- **Claude Desktop app** - native macOS/Windows; unifies Chat/Code/Cowork tabs; ~180-250MB RAM vs 1.2-2GB browser tabs; Quick Entry overlay; one-click local MCP extensions [s67, s194].
- **Claude mobile (Dispatch + Remote Control)** - iOS/Android; trigger local desktop actions from your phone; monitor/approve Claude Code sessions remotely; `claude --teleport` pulls a mobile thread into your terminal; Dispatch approvals expire after 30 min [s68, s113, s194].
- **Claude API** - programmatic access to Opus 4.8 / Fable 5 / Sonnet 4.6 / Haiku 4.5 via Anthropic, Amazon Bedrock, Google Vertex, Microsoft Foundry. For custom features, high-volume async jobs, ZDR compliance [s2, s6].

Full scoreboard + "best for X": `references/surface-comparison.md`.

---

## Q3 - Claude Code in Depth

**Bottom line:** Terminal-first agentic engineering system; powered by Opus 4.8 / Sonnet 4.6 with 1M context; ~87.6% SWE-bench Verified [s2, s77].

**Limits to respect:**
- **Context drift** - sessions over ~120K tokens lose focus; verbose shell output (npm logs) pollutes context [s33].
- **Cost multipliers** - Pro is $20/mo (~44K tokens per 5-hr window); multi-agent fan-out multiplies cost (a 50-agent run = 50x tokens, a $50 job -> $2,500) [s59, s86].
- **Autonomy risk** - without git discipline/guardrails it can over-engineer, touch unrelated files, or expose credentials [s33, s69].

**The composable primitives:**
- **Skills** - reusable `SKILL.md` instruction packages with **progressive disclosure** (name+desc ~100 tokens at startup; full body <5K only when relevant). Two kinds: capability uplift vs encoded preference [s33, s120].
- **Hooks** - event scripts at `PreToolUse`/`PostToolUse`/`SessionStart`; e.g. a `PreToolUse` hook blocks reading `.env` or running `curl` [s10, s69].
- **MCP (Model Context Protocol)** - open JSON-RPC standard connecting Claude to external data/tools (Jira, Sentry, Postgres) without custom glue [s172, s213].
- **Subagents / Dynamic Workflows** - spawn isolated-context subagents, return only summaries; Opus 4.8 can orchestrate hundreds in parallel for big migrations [s86, s196].
- **Plugins** - `/plugin install` bundles that package MCP + skills + hooks + subagents [s58].
- **Slash commands** - `/compact` summarizes history; `/handoff` compresses the session to markdown for a fresh session/agent [s33, s77].
- **Headless mode** - `claude -p` runs without the interactive UI for 24/7 background ops [s150].
- **Agent SDK** - TS/Python library wrapping the Claude Code runtime; build custom autonomous agents with built-in tools (Read/Bash/Edit/WebSearch) without coding the agent loop [s10, s183].

**Highest-leverage practices (real, named tools):** Caveman skill (strips narration, ~65% fewer output tokens) [s33]; `/grill-me` (Grill Me skill, 156k+ installs - interrogates assumptions before coding) [s33]; Karpathy's 4 rules skill (144k+ stars) [s33]; Context Mode plugin (filters verbose shell output) [s33]; Superpowers plugin (752k installs - enforced TDD, worktrees, parallel subagents) [s32]; sandbox on a cheap VPS + route enterprise traffic through an MCP gateway [s59, s69].

Full detail: `references/claude-code-guide.md`. For granular feature mechanics, defer to the **claude-code-guide** agent.

---

## Q4 - Claude Cowork (the agentic product)

**Bottom line:** An **autonomous desktop agent for non-technical knowledge workers**. Research preview Jan 12, 2026; **GA across all paid plans (Pro/Max/Team/Enterprise) April 9, 2026**. Built internally by Boris Cherny in ~10 days using Claude Code [s50, s64, s195].

**How it works:** continuous **plan-to-action loop**. You grant folder access; it runs shell/code inside a **sandboxed local Linux VM** (Apple `VZVirtualMachine` on macOS), drafts a plan, splits into subtasks, and reads/creates/edits files on your filesystem; can use computer-use to click around SaaS dashboards. Modes: **"Ask before acting"** vs **"Act without asking"**; an un-bypassable prompt always gates permanent file deletion [s145, s194, s195].

**Best uses:** organize messy folders / batch rename, turn receipt images into a formatted expense report, build real-formula Excel models, compile research into brand-correct PowerPoint, `/schedule` recurring reports; Dispatch from mobile; "Claude for Small Business" (May 2026) connects QuickBooks/PayPal/Canva/HubSpot [s145, s161, s194].

**Limits:** your desktop must stay awake/online with the app open (sleep pauses tasks); heavy token burn; **not yet in the Claude Compliance API** (audit gap); no cross-session memory unless inside a Project; prompt-injection risk in "Act without asking" + web access [s145, s146, s199].

**Vs the others:** Chat = think/draft (human every turn). Code = developers, terminal/IDE, outputs committed software. **Cowork = non-technical operators, GUI, outputs business deliverables** (sheets/decks/cleaned dirs) without a terminal [s111, s194].

Full detail: `references/claude-cowork-guide.md`.

---

## Q5 - Business Applications + Use Cases

**Bottom line:** Deployment shifted from chat to **agentic workflows embedded in systems**. Anthropic estimates Claude cuts task time ~80%, ~$55 labor saving per transaction, contributing ~1.8% annual US labor-productivity growth [s118, s140].

**By function (with real, URL-backed case studies):**
- **Engineering:** Stripe - 10,000-line Scala->Java migration in 4 days (was ~10 engineer-weeks), Claude Code across 1,370 engineers [s62]. Satispay - Claude writes 75% of code + pre-human review [s136]. Anthropic - 80%+ of production code [s118].
- **Sales/Marketing/Ops:** Attention - automated 1.6M hours of admin, +up to 40% win rates [s125]. Advolve - 90% less ops time, +15% ROAS on ad creative [s123]. Brainlabs - 1,000+ marketers on Cowork authored 400 custom skills in 4 weeks [s127].
- **Finance:** Brex - automated 75% of expense transactions, 94% compliance, ~$56.5M saved [s129]. BlueFlame AI - deal-room analysis 4h -> <5 min [s126].
- **Legal:** GC AI - ~14 hrs/week saved across 1,500 companies, -14% outside-counsel spend [s132]. Wordsmith - 400-page bundles vs 300-point checks in 4-5 min [s137].
- **Support:** Coinbase - chatbot + agent-assist at $226B trading volume, 99.9999% availability [s131]. Gradient Labs - 80-90% resolution, up to 98% CSAT [s133].
- **Life sciences:** Bristol Myers Squibb - Claude Enterprise to 30,000 employees, faster data-lock-to-filing [s30]. Healthcare agents connect PubMed/ClinicalTrials.gov [s9].

**Creative / unusual:** neurodivergent "declutter my room" photo coaching + Notion life-admin; historical roleplay; timber-flooring cut optimization; Fable 5 autonomously designing 3D-printable CAD models [s76, s211, s118].

Full detail + ROI framing for NexusPoint pitches: `references/business-applications.md`.

---

## Q6 - The Ecosystem (plugins, MCP servers, GitHub tools)

**Bottom line:** By May 2026, **15,134+ Claude Code plugin repos indexed** [s29]. Use curated lists + the official marketplace; don't bulk-install.

**Where to find tools:** hesreallyhim/awesome-claude-code (36.8k stars) [s29]; punkpeye + wong2/awesome-mcp-servers [s29]; rohitg00/awesome-claude-code-toolkit (135 agents, 176+ plugins) [s150]; official marketplace via `/plugin marketplace add` or the Desktop Discover tab [s32].

**Top plugins:** Frontend Design (829k) [s32]; Superpowers (752k - multi-agent TDD) [s32]; Code-Simplifier (284k - Anthropic's behavior-preserving refactor) [s32, s33]; TypeScript LSP (177k) / Pyright LSP (91k) [s32]; Security Guidance (175k) [s32].

**Top MCP servers:** Context7 (348k - live version-specific docs) [s32]; Zilliz claude-context (semantic code search, ~40% token reduction) [s237]; Composio (managed gateway, 1,000+ apps) [s32]; Firecrawl (web scraping/search) [s33].

**Open-source standouts:** Claudebase (sync your whole Claude config across machines via GitHub) [s114, s116]; claude-mem (35.9k - persistent SQLite memory) [s150]; getburnd + llm-prices (cost control) [s150].

**Power-user tactics:** start with a minimalist 5-plugin stack (one LSP + GitHub MCP + Security Guidance + Commit Commands + Composio) [s32]; treat lists as discovery not install; sync with Claudebase day one; Caveman for token control; run code-simplifier only pre-PR [s29, s33].

Full detail: `references/ecosystem-plugins.md`.

---

## Q7 - Building with the Claude API

**Bottom line:** 2026 building = stateful agentic systems via the **Agent SDK + MCP + cost engineering**, not chat wrappers [s183].

- **Agent SDK** (Python/TS) wraps the Claude Code runtime - state, filesystem tracking, no manual tool loop. Use subagents for task isolation; lifecycle hooks for governance (scrub PII, block dangerous commands) [s10, s183].
- **Server vs client tools:** client-executed for local logic; server-executed (`web_search`, `code_execution`, `web_fetch`) run in Anthropic's sandbox, cutting your loop code + latency. Mind the **tool tax** (~290 input tokens for `auto` on Opus 4.8, ~410 if forced) [s157, s182, s183].
- **MCP** solves the N×M integration problem. Direct API MCP connector via the `mcp-client-2025-11-20` beta header [s171]. **"Code Mode"** (let Claude write a local script to query/filter instead of dumping schemas+data through the LLM) cut a large-data task from ~150,000 -> ~2,000 tokens (98.7%) [s117, s183].
- **Cost:** prompt caching (reads 10% of base), Batch API (50% off), 70/20/10 routing; stacking can hit ~95% input savings [s54, s156, s183].

**Build-vs-buy:** Use **products** (Pro/Max/Team/Enterprise, Code, Cowork) for human-in-the-loop and to arbitrage heavy individual cost (a coder could burn $3,650/mo on raw API; Max 20x $200 or Team Premium ~$125-150 is far cheaper) [s59, s183]. **Build on the API** for unattended automation (using a subscription for automated unattended scripts violates ToS), customer-facing apps, and ZDR/auditing. Mature orgs run **both** (governed seats + API workflows) [s70, s183, s219].

Full detail: `references/building-with-claude.md`. For exact request params/SDK code, hand off to the **claude-api** skill.

---

## Q8 - Plans, Pricing + Claude vs Competitors

**Plans (2026):**
- **Free ($0):** Sonnet 4.6 + limited Haiku; ~30-100 msgs/day; Artifacts, memory, file upload, web search; limits drop 30-40% at peak [s20, s52, s193].
- **Pro ($20/mo, $17 annual):** 5x Free (~44K tokens / 5-hr window); all models incl. Opus 4.8, Cowork, unlimited Projects, M365. *Claude Code on Pro is contested - verify* [s52, s193].
- **Max ($100 / $200):** 5x (~220K tokens) / 20x (~880K tokens) Pro; full Claude Code; top queue priority [s83, s193].
- **Team (min 5 seats):** Standard $25/seat (1.25x Pro, SSO, shared workspaces, **no Claude Code**); Premium $125-150/seat (6.25x Pro, **full Claude Code**); seats mixable [s193].
- **Enterprise (custom, ~$20-75/seat + API):** 500K context, HIPAA-ready, RBAC, SCIM, no training on inputs [s20, s193].

**Claude vs ChatGPT vs Gemini (business, 2026):**
- **Claude** - best for accuracy, writing, production coding. ~**36% hallucination rate** on long-form factuality (vs GPT-5.5's 86%), 64.3% SWE-bench Pro. No native image/video gen [s110].
- **ChatGPT (GPT-5.5)** - best for autonomous agents/tool ecosystems (82.7% Terminal-Bench 2.0), broadest media (Sora/voice/DALL-E); only truly unlimited $200 tier; weak long-form factuality [s110].
- **Gemini (3.1 Pro)** - best for Google Workspace + **2M-token context**; cheapest flagship API ($2/$12); $19.99 includes 5TB storage [s110].

**Decision frameworks** (product + model routing): see `references/plans-and-pricing.md` and `references/surface-comparison.md`.

---

## Live Query Additions

> Findings from on-demand live queries to the *Claude - Complete Guide 2026 (NexusPoint)* NotebookLM notebook, captured when the original Q1-Q8 synthesis didn't fully answer a specific question. Each entry is dated and tagged to the relevant Q section. Append new ones here (format: `### [YYYY-MM-DD] (Q# - Topic) <question>` then key specifics + a Source line).

### [2026-06-10] (Q3 - Claude Code) Does Claude Code run natively on Windows or need WSL?

- Claude Code **runs natively on Windows in 2026 and does not require WSL** (Windows Subsystem for Linux), though it is fully supported on WSL if you prefer it. Anthropic provides a native Windows install path.
- Source: live query to the *Claude - Complete Guide 2026 (NexusPoint)* notebook (6 citations, within the locked corpus). Relevant since Aleem's primary machine is Windows 11 - Claude Code works directly, no WSL setup needed.

### [2026-06-10] (Q4 - Cowork) Step-by-step tutorial: how to use Claude Cowork as a first-time user

- **Requirement:** a paid plan (Pro/Max/Team/Enterprise). Cowork is NOT on the web - it lives only in the **Claude Desktop app** (macOS / Windows x64).
- **Step 1 - Open it:** install + log into the Desktop app, then click the **Cowork** tab in the top mode selector (Chat / Cowork / Code).
- **Step 2 - Grant folder access:** click **"Work in a folder"** and pick the directory; Cowork runs in a sandboxed local VM and can only touch folders you connect.
- **Step 3 - Pick permission mode:** **"Ask before acting"** (recommended - pauses to show its plan and wait for approval before editing files / running scripts / visiting sites) vs **"Act without asking"** (continuous, faster, higher prompt-injection risk - only for supervised trusted files). Either mode hard-stops for explicit approval before permanent file deletion or high-risk actions (e.g. purchases).
- **Step 4 - First task (good beginner one):** point it at Downloads/Screenshots and type a natural-language goal, e.g. *"Clean up my Screenshots folder: group by date, rename descriptively by contents, delete duplicates, move old ones to an Archive subfolder."* Review the generated plan, click **Start**. The app must stay open and the computer awake or the session ends.
- **Step 5 - Schedule recurring work:** inside an active task type `/schedule`, set cadence (daily/weekly/monthly); manage them under **Scheduled** in the left sidebar. Only fires if the machine is awake + app open at the time.
- **Step 6 - Dispatch (mobile remote control):** Desktop = Cowork tab > **Dispatch** > "Get started", toggle keep-awake, grant file/connector access. Mobile = send instructions in the Dispatch thread; the desktop does the heavy lifting locally and pushes you a notification when done or when it needs approval.
- Source: live query to the notebook (22 citations; primary source "Get started with Claude Cowork" [s145/s146] plus the Desktop app and Dispatch docs). Within the locked corpus.

---

> **Source note for the 2026-06-16 entries below:** These findings come from a batch of ~47 practitioner YouTube videos added to the notebook on 2026-06-16 (creator tutorials: Dan Martell, the "7 Levels" series, "All 35 Claude Code Concepts," tool round-ups, integration walkthroughs, Cowork courses, etc.). Treat as **current practitioner consensus, not Anthropic documentation** - the level frameworks, tool names, and tactics are creator opinion and move fast. Verify any specific command, plan limit, or product name against the live notebook or official docs before quoting to a client. Captured to support the lead-magnet guide build.

### [2026-06-16] (Q3 - Claude Code) The "Levels of Mastery" framing (the guide's new spine)

Multiple videos independently frame Claude mastery as a **ladder**, not a feature list. The general progression (synthesized from Martell's "Full Claude Guide" + "Every Level Explained"):

1. **Amateur** - Claude as a stateless search bar; one-off questions, start from zero each time.
2. **Regular** - Projects as persistent workspaces; preloaded reference docs; a Master Prompt (role/context "ingredients") + System Prompt (the "recipe"); have Claude interview you to write them.
3. **Integrator** - connect Claude to where work lives: Connectors (Gmail, Drive, Slack, Notion), Artifacts, Claude in Chrome; Cowork for desktop autonomy.
4. **Operator** - doer -> director; if you do a workflow 3x/week, turn it into a Skill; chain skills; schedule them in Cowork.
5. **Builder** - Claude Code to build apps/tools even without coding; Plan Mode (`/pl`), remote control from phone.
6. **Architect / Orchestrator** - self-running systems, human-on-the-loop; cloud routines, subagents, memory consolidation.

Domain-specific **"7 Levels" ladders** (same escalation pattern):
- **Web design:** prompt-only ("AI slop") -> design-education skills (UIUX Pro Max) -> visual director (screenshots from Awwwards/Dribbble) -> cloner (teardown HTML/CSS) -> custom components -> external tools (Figma/Stitch, glassmorphism) -> 3D/WebGL.
- **Content:** AI slop -> voice injector (`CLAUDE.md` with banned words/approved phrasing) -> research pipelines -> multimodal carousels -> content cascade (1 asset -> many platforms) -> cron automation -> autonomous agent (trap: losing brand identity).
- **Memory/RAG:** automemory -> `CLAUDE.md` rulebook -> state files & chunking (index pattern) -> **Obsidian vault (the "99% solution" for solo users)** -> naive RAG (vector, "crappy search engine" trap) -> Graph RAG (LightRAG) -> agentic/multimodal RAG (orchestrator routes queries).
- Source: live notebook queries (Q1/Q4 of the 2026-06-16 batch); creator sources.

### [2026-06-16] (Q3 - Claude Code) New/2026 workflow features

- **Routines (Cloud routines):** scheduled tasks that run on Anthropic's cloud (machine can be OFF). Create via Desktop "Scheduled" tab, `claude.ai/code`, or CLI; configure name + prompt + model + env; **must link a GitHub repo** for deliverables. Triggers: schedule, API call, or GitHub event. Max plan ~15 runs/24h.
- **Dynamic Workflows / Ultra Code (`/workflows`, `/deep research`, `/ultracode`):** Claude writes a JS execution script and spawns hundreds of parallel subagents, validates with an adversarial "devil's advocate" agent, merges results. Ultra Code auto-elevates effort to "extra high" and decides if a prompt warrants a workflow. **Can cost ~50x tokens** - reserve for big parallelizable jobs (large migrations, codebase-wide bug hunts).
- **The Dashboard (`claude agents`, `/bg`):** unified view of parallel sessions in three columns - Needs Input / Working / Completed. Spacebar to peek/reply, Ctrl+X to delete, `/bg` to push a task to background.
- **Managed Agents (Claude Console):** Anthropic-hosted agent builder; guided 5-step UI (task, tools, guardrails, model); deploys to a cloud sandbox triggered by an API endpoint. For building agents ~10x faster without local infra. For heartbeat/constant-check agents, custom Agent SDK + Trigger.dev may still be better.
- Source: live notebook query (B2 of the 2026-06-16 batch); creator sources.

### [2026-06-16] (Q3 - Claude Code) Non-coder onboarding: concepts + beginner hacks

- **Mindset:** treat Claude as an "infinitely patient tutor"; don't be an "accept monkey" - read output, ask "what is this?/why did you do that?"
- **WAT framework:** Workflows (plain-language SOPs) + Agent (Claude, the brain) + Tools (code exec, terminal). Core mental model for automation.
- **Core concepts:** the IDE (VS Code = file explorer + terminal where the agent lives); `CLAUDE.md` = the project "brain"/system prompt, keep lean (<150-200 lines); context window + context rot; Skills (progressive disclosure); **CLIs vs MCPs** (CLIs live in the terminal, faster + far more token-efficient than MCP servers); permissions (`--dangerously-skip-permissions` for full autonomy).
- **Hacks:** Plan Mode (Shift+Tab); `/init` (auto-generate a `CLAUDE.md` from your codebase); `/btw` (sidebar chat that does NOT add to context tokens); custom status line (`/status line`) to show context-usage %; the screenshot loop (feed UI screenshots back for visual iteration); load the front-end-design skill + tag brand assets to beat "AI slop"; Obsidian as a free second brain.
- Source: live notebook query (B1 of the 2026-06-16 batch); creator sources.

### [2026-06-16] (Q3 - Claude Code) Subagents, 24/7 agents, and the "Agentic OS"

- **Subagents (`/agents`):** main session = project manager dispatching to isolated, fresh-context workers that return only final output (keeps main context clean). Subagents do NOT talk to each other (vs "agent teams" which debate). Generates a markdown file in `.claude/agents` with YAML front matter. Best practices: trim the description (progressive disclosure), enforce read-only where possible, route heavy reads to Haiku, only delegate independent/parallelizable tasks.
- **24/7 remote agents:** built on cloud routines; stateless per run but keeps the full agentic loop (can reason, use tools, self-correct). Write "one-shot" prompts, store secrets in env vars (never in the prompt/repo), audit failure logs.
- **Agentic OS:** solves 3 gaps - memory, consistency, accessibility. Stack = Claude Code (engine) + Obsidian vault (structured memory: raw / wiki / index folders) + Skills (reusable SOPs) + a dashboard for non-technical teammates. Avoid bloated `CLAUDE.md`; treat skills as living docs; package workflows by domain (marketing pack, research pack).
- Source: live notebook query (B3 of the 2026-06-16 batch); creator sources.

### [2026-06-16] (Q6 - Ecosystem) Expanded practitioner toolkit (named tools + what each does)

- **CLIs:** CLI Anything (auto-generate a CLI for any OSS program, by LightRAG makers); NotebookLM-CLI (offload analysis to Google's servers, free); Stripe; FFmpeg (video/audio/subtitles); GitHub; Vercel (frontend deploy); Supabase (DB/auth); Playwright (browser automation, faster/cheaper than the MCP); LLM Fit (pick the right local model for your machine); GWS (Google Workspace, 100+ workflow recipes).
- **Open-source repos:** Auto Research (Karpathy - "ML algorithm in a box," runs optimization experiments); OpenSpace (MCP tracking skill performance); Claude Peers (multiple sessions talk via MCP + SQLite); Claude Obsidian (auto-build an Obsidian wiki from raw sources).
- **Plugins:** Superpowers (14-skill TDD methodology dispatcher); GSD/Get Shit Done (fresh-context subagents + quality gates); Graphify (codebase -> knowledge graph, fewer tokens, can export Obsidian); Official Codex plugin (OpenAI adversarial review / "Codex rescue"); Impeccable 3.0 (23 commands, live in-browser UI editing, beats "AI slop"); Context Mode (filters verbose shell logs, SQLite session restore); Claude Mem (cross-session memory in a local SQLite vector DB); Higgsfield (AI image/video); n8n MCP server (build + validate n8n flows).
- **Skills:** Skill Creator (official - drafts, tests, benchmarks, packages a skill); Caveman (strips filler, ~75% token savings, can improve accuracy); Grill Me / Grill with Docs (+ Codex variants: adversarial plan review, up to 5 rounds); Karpathy's Guidelines (4-rule lean `CLAUDE.md`: think first, simplicity, surgical changes, goal-driven); Memory OS + Wrap-up (3-bucket memory: archive / immutable knowledge / current strategy); Official Front-End Design.
- Source: live notebook query (B4 of the 2026-06-16 batch); creator sources. Some overlap with the locked corpus (Caveman [s33], Superpowers [s32], Context7); the rest are net-new from these creator videos - directional.

### [2026-06-16] (Q6 - Ecosystem) Integration combos ("X + Y = superpower")

- **Claude Code + Firecrawl:** reliable scraping at scale; schema -> clean JSON/Markdown instead of raw HTML; bypasses anti-bot + JS-heavy sites. Use: competitor pricing, market research, lead-gen directory scraping.
- **Claude Code + NotebookLM:** "infinite" persistent memory at ~zero token cost; offloads analysis to Google; can generate NotebookLM audio/video assets; pair with a "Wrap-up" skill to save whole sessions into a "brain" notebook.
- **Claude Code + Playwright:** end-to-end browser automation (navigate, click, fill forms, test logged-in sessions); CLI is more token-efficient than the MCP. Use: automated QA, web task execution.
- **Graphify + Obsidian:** maps a codebase/docs into a knowledge graph, exports linked Markdown into an Obsidian vault = structured second brain; search big repos without context rot.
- Source: live notebook query (B5 of the 2026-06-16 batch); creator sources.

### [2026-06-16] (Q4 - Cowork) Cowork full business playbook

- **Setup:** write a `business_brain.md` (audience, revenue, brand voice, workflows) in a "Sandbox" folder; set Global Instructions to always check it for strategic questions; authenticate Connectors (Calendar, Gmail, Notion, Slack, Canva, Apify, etc.).
- **Marketing workflows:** X/Grok trend intelligence (recency + authority + velocity matrix, then `/schedule` daily); Apify competitor scraping (20k+ scrapers - e.g. last 5 competitor reels into a table); content repurposer plugin (YouTube URL -> brand-voiced posts -> Notion calendar); Canva batch design (master brand template -> 10 fresh slides).
- **Ops workflows:** morning brief + inbox triage (Chief of Staff); financial/revenue dashboards (Mercury/Stripe -> P&L -> HTML chart, monthly recurring); Computer Use for legacy portals without APIs (takes over mouse/keyboard); automated invoicing via Projects + template.
- Source: live notebook query (B6 of the 2026-06-16 batch); creator sources.

### [2026-06-16] (Q5 - Business) Concrete money-making workflows + the "6 AI skills"

- **Web design:** Stitch 2.0 workflow (design in Stitch -> export code -> refine in Claude Code with 21st.dev); client CMS workflow (scrape inspiration via Firecrawl/blueprint-extractor -> generate site -> push to Vercel via GitHub -> build a client-editable CMS dashboard).
- **Local SEO (the "50,000 clicks/mo" case):** GMB optimization via a setup markdown + Semrush "money keywords"; automated GMB posting via make.com with voice files (`humor.md`, `tone.md`, `vocabulary.md`); service + city keyword-cluster pages (SSR); Lighthouse -> paste report -> Claude fixes technical SEO toward 100.
- **Content:** content gap analysis (scrape competitor titles/views); Callaway Desire hooks (visual/spoken/text from an ICP language library + swipe file); content cascade (1 YouTube URL -> LinkedIn/Facebook/Reddit/X + a Gumroad HTML page); carousel fix (Higgsfield/GPT Images 2 cover + HTML body slides + browser "tweak loop").
- **The 6 AI skills (career framing):** (1) become "the AI person" in your current role; (2) taste & judgment (build an examples library, feed corrections back); (3) context engineering (never a blank chat - feed proprietary context like a new intern); (4) iteration speed (define "done" as one business metric); (5) build your own Jarvis (background agents that ping you); (6) know when NOT to use AI (deterministic "vending machine" beats a non-deterministic "slot machine" agent for predictable tasks).
- Source: live notebook query (B7 of the 2026-06-16 batch); creator sources.

### [2026-06-16] (Q3/Q7 - Deploy + OS) Deploying automations (3 methods) + the AI Operating System

- **3 deployment methods:** (1) **Local loops / internal cron** (`cron create/list/delete`) - zero setup, full agentic loop, but machine + terminal must stay on; (2) **Scheduled tasks + Cloud routines** - runs on Anthropic's cloud 24/7, machine can be off, triggers by schedule/API/GitHub event, local tasks can "play catch-up" on missed runs; (3) **External cloud (Modal / Trigger.dev)** - Python/TS scripts on cron/webhooks for deterministic jobs; add the **Agent SDK** ("the brain plus the hands") for the full agentic experience on external servers.
- **AI Operating System (Opus 4.8 as your "second brain"):** mindset shift = do everything inside Claude Code / VS Code first (stop opening Chrome/SaaS apps), which naturally builds a local knowledge base. **Four C's framework: Context, Connections, Capabilities, Cadence.** Steps: context over model ("context is king" - dump transcripts/emails/posts in); everything as files/folders (`decisions`, `audits`, `archives`, "other worlds" sub-projects); connect apps via APIs/MCP; manage tokens like money (isolate tasks to avoid polluting the main session).
- Source: live notebook queries (Q3/Q5 of the first 2026-06-16 batch); creator sources.

---

> **Source note for the 2026-06-20 entries below:** Findings from new YouTube sources added to the notebook covering Claude second-brain, Obsidian, Graphify, LLM Wiki (Karpathy), and the 5-level memory framework (Nate Herk / Chase AI). Queried via 7 targeted `ask --json` calls (Q_SB1-Q_SB7). Full synthesized reference in `references/claude-second-brain.md`. Same practitioner-consensus caveat as the 2026-06-16 batch - not Anthropic documentation.

### [2026-06-20] (Q3/memory - Second Brain) What is a Claude second-brain and how it differs from regular chat

- A Claude second-brain (AI OS) = always-on infrastructure linking Claude to a **structured local file system**. The AI reads, writes, and maintains its own memory. "Knows what is going on in your world better than you do" - recalls meeting notes, strategies, relationships, decisions without re-explaining.
- **The amnesia problem:** regular AI chat = stateless disposable threads; once context window fills or new chat starts, Claude forgets everything. Second-brain = persistent, self-updating memory.
- **Key components (2026 full stack):**
  - Engine: **Claude Code** or **Claude Cowork** (the AI agent running locally, using Opus 4.8 or Fable 5)
  - Visual layer: **Obsidian** (free markdown app; visualizes the interconnected knowledge graph Claude Code builds)
  - Architecture: **Karpathy LLM Wiki** (3 layers: Raw Sources / The Wiki / The Schema `CLAUDE.md`)
  - Knowledge mapping: **Graphify** (turns files/repos into a knowledge graph; ~60k GitHub stars)
  - Long-term RAG: **Pinecone** / **NotebookLM CLI** (semantic search through massive unstructured archives without burning Claude's token limits)
  - Session memory: **Context Mode** + **Claude Mem** (35.9k stars; SQLite vector DB, cross-session capture)
  - Data extraction: **"Grill Me" skill** (Claude interviews you with 15-25 questions and auto-populates your rule files); **Wrap-up skill** (summarizes session + archives insights into long-term vault)
- **Token efficiency:** querying a pre-built wiki uses up to 95% fewer tokens than re-reading raw transcripts per query.
- Full detail: `references/claude-second-brain.md`

### [2026-06-20] (Q3/memory - Second Brain) The 5 Levels of an AI second-brain (Nate Herk / Chase AI)

- **Level 1 - Exact Match Retrieval:** folder structure + exact keyword search; Claude Code **automemory** (auto-generates `.claude/memory/` notes); lean `CLAUDE.md` as a router pointing to directories. Tools: Claude Code native.
- **Level 2 - Topic Aggregation (The LLM Wiki):** Claude reads raw sources, autonomously writes and links summarized wiki pages; index files for navigation. Tools: **Obsidian** (visual layer) + **Andrej Karpathy's LLM Wiki** (`raw/` / `wiki/` / `CLAUDE.md` 3-folder structure). 95% fewer tokens vs re-reading raw docs.
- **Level 3 - Semantic Search (Vector RAG):** meaning-based search (X ~ Y even if exact word absent); good for vast unstructured archives (email, Slack history). Tools: **Pinecone**, **Supabase** vector databases.
- **Level 4 - Knowledge Graphs:** maps relationships and traces logical chains ("Project A -> Tool B -> Person C"); requires extracting tacit knowledge from your own head. Tools: **Graphify**, **LightRAG**, **Microsoft GraphRAG**; **"Grill Me" skill** for knowledge extraction.
- **Level 5 - Autonomous AI OS:** 24/7 continuous sync; a "Top-of-Funnel" AI router decides whether a query needs markdown lookup vs vector search vs graph traversal; multimodal (video, images, tables). Tools: **GBrain** (Gary Tan/YC concept), **Hermes** (always-on persistent agent), **Gemini embedding 2** for video indexing.
- Source: live query Q_SB2 (2026-06-20); Nate Herk "5 Levels" + Chase AI "7 Levels" series.

### [2026-06-20] (Q3/memory - Second Brain) Obsidian: what it is and how it integrates with Claude

- Free, local-first markdown app. Data = plain `.md` files in a local "vault." You own all data. **Graph view** maps how notes connect via internal links.
- In a second-brain setup: Claude Code runs in the terminal *inside* your Obsidian vault folder. Claude writes and maintains the wiki; Obsidian visualizes it.
- **Integrations:** Terminal Plugin (run `claude` without leaving Obsidian); Obsidian Markdown Skill (trains Claude on wiki-links `[[note]]`, tags, callouts); Obsidian Web Clipper (browser extension saves articles into `/raw` as markdown); Graphify `graphify-obsidian` command (auto-generates a linked Obsidian vault from any repo); Filesystem MCP (Cowork/non-terminal path: read/write Obsidian folders from Claude Desktop).
- **What you can do:** drop a 50-page PDF into `/raw` -> Claude ingests, extracts key ideas, updates concept pages, links in graph view; build a full "command center" AI OS with dashboards; store client profiles + meeting transcripts so Claude acts as an executive assistant with perfect recall.
- Source: live query Q_SB3 (2026-06-20); creator sources.

### [2026-06-20] (Q3/memory - Second Brain) Graphify: the knowledge graph builder

- Open-source, **~60,000 GitHub stars**. Turns any codebase, repo, or document collection into a dynamic knowledge graph. Solves Claude's amnesia + token expense: without it, Claude greps (rescans) the codebase every query; with it, Claude queries a pre-built relationship map.
- **3-pass system:** (1) tree-sitter deterministically parses code structure (no LLM, no API cost); (2) Faster Whisper transcribes audio/video into the graph; (3) LLM extracts concepts from PDFs/images.
- **Output:** nodes (concepts/files) + edges (relationships) + communities (clusters) + "god nodes" (critical load-bearing files).
- **Token savings:** reliable **40% reduction** in real-world tests (some users claim 70x). `graphify hook install` = git hook that rebuilds the graph after every commit at zero API cost.
- **vs alternatives:** Traditional RAG uses vector embeddings, good for policy PDFs, bad for code relationships. Graphify has NO vector embeddings - optimized for architectural wiring. Obsidian alone requires manual linking; Graphify automates it and can generate the vault.
- **Commands:** `graphify hook install` (auto-rebuild); `/graphify obsidian` (generate linked Obsidian vault from graph).
- Source: live query Q_SB4 (2026-06-20); Graphify GitHub + creator sources.

### [2026-06-20] (Q3/memory - Second Brain) LLM Wiki: Karpathy's memory architecture

- Coined by **Andrej Karpathy** (OpenAI founding member, former Tesla AI Director). Analogy: Obsidian = IDE, LLM = programmer, wiki = codebase.
- **Beats standard RAG:** RAG re-reads raw docs every query and forgets the answer. LLM Wiki pre-computes: when a new source is added, AI reads once, updates 10-15 interconnected markdown pages, logs changes. Future queries hit pre-built summaries. Uses actual markdown `[[wiki-links]]`, not vector similarity - deterministic relationship tracing.
- **3-folder structure:** `/raw` (read-only intake; AI never modifies) / `/wiki` (AI-written knowledge base; interlinked concept pages) / `CLAUDE.md` at root (the rulebook/schema).
- **Core tracking files inside `/wiki`:** `index.md` (master catalog for navigation) + `log.md` (operation history of every AI change).
- **Ingestion workflow:** add file to `/raw` -> "read this and update the wiki" -> Claude extracts concepts, creates/updates 10-15 wiki pages, flags contradictions with existing knowledge.
- **Linting workflow:** periodically "lint the wiki" -> Claude scans for orphaned pages, broken links, stale claims, missing data.
- No vector databases needed at this level. 95% fewer tokens vs re-reading raw transcripts.
- Source: live query Q_SB5 (2026-06-20); Karpathy's LLM Wiki writings + creator implementations.

### [2026-06-20] (Q3/memory - Second Brain) Step-by-step Claude second-brain setup

- **Install:** Claude Code (`irm https://claude.ai/install.ps1 | iex` on Windows) + Obsidian (free download) + optional Graphify.
- **Create vault:** open Obsidian -> new Vault (local folder) -> open folder in terminal -> `claude` -> create `raw/`, `wiki/`, `templates/` subfolders.
- **Configure CLAUDE.md:** run `/init` for base file, then add: architecture definition (where `raw/` and `wiki/` are), ingest workflow, page formatting rules, routing rules. **Hard limit: keep under 150-200 lines.** Claude reads CLAUDE.md on every prompt - bloating it burns thousands of tokens per interaction.
- **Feed the system:** drag files into `raw/` -> "I just added a new source to the raw folder. Please read it and update the wiki."
- **Maintain health:** `/compact` at ~60% context; AutoDream (mid-2026 background sub-agent) prunes contradictions + merges duplicates + updates temporal refs between sessions; `/handoff` to transfer session state cleanly.
- **Critical pitfalls:** context rot (use `/compact` and `/clear` at 200k tokens); overstuffed CLAUDE.md; ingesting noisy/volatile data (daily Slack threads); privacy risk (sensitive client data to Enterprise ZDR tier only).
- Full setup: `references/claude-second-brain.md` (Step 1-6 with commands).

### [2026-06-20] (Q5/memory - Second Brain) Agency/freelancer Claude second-brain setup

- **Folder structure (LLM Wiki + Four C's):** `/context` (brand_voice.md + icp_and_offer.md) / `/projects/[Client Name]/` (brief, transcripts, deliverables) / `/skills` (SOP markdown files: content_cascade.md, proposal.md, onboarding.md) / `/raw` (staging area) / `/wiki` (auto-maintained knowledge base) / `/decisions` (running strategy log).
- **CLAUDE.md schema:** keep lean (<200 lines); routing rules pointing to folders (not full content); role definition; operating principles (think before executing, maintain brand voice, surgical changes).
- **Key workflows:**
  - Client management: Claude scans call transcript -> updates HubSpot CRM via MCP connector -> drafts personalized follow-up email referencing specific pain points.
  - Proposals: drop RFP + past proposals + client brief -> Claude synthesizes + generates structured proposal draft (40% less drafting time).
  - Content Cascade: one YouTube transcript/meeting note -> blog post + LinkedIn carousel + Twitter thread, all in brand voice -> Canva integration for on-brand graphics.
  - SOP execution (WAT framework: Workflows + Agent + Tools): write recurring tasks as Skills; `/schedule` in Cowork to run automatically (e.g. Friday SEO audit -> PDF report -> left in client folder).
- **Advanced:** NotebookLM CLI as "infinite memory" MCP - massive archives (every client email, SOP, deliverable) stored in NotebookLM, Claude semantically retrieves only exact insights needed. Mobile Dispatch: dictate idea on phone -> Cowork processes on desktop -> draft ready when you arrive.
- Full agency setup: `references/claude-second-brain.md` (Agency section with example CLAUDE.md schema).
