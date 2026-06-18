# Claude Code - Intricacies + Productivity (2026)

**Source basis:** `research-synthesis.md` Q3/Q6 (237-source NotebookLM synthesis). `[sN]` -> `_research/sources.json`. **Honesty rule:** features/installs move fast - confirm via the live notebook. For exhaustive feature mechanics (exact hook event payloads, settings keys, slash-command edge cases), defer to the **claude-code-guide** agent. For API/SDK request specifics, defer to the **claude-api** skill.

**What it is:** Anthropic's terminal- and IDE-native **agentic** software-engineering system. It maps the repo, autonomously edits files, runs shell commands and tests, and stages Git - powered by Opus 4.8 / Sonnet 4.6 with up to 1M context. It authors **80%+ of Anthropic's own production code** and scores **64.3% SWE-bench Pro / 87.6% Verified** [s2, s62, s77].

---

## Capabilities vs limits (set expectations honestly)

**Can do:** agentic search over dependencies, multi-file refactors with self-correcting loops, debugging CI failures, running tests, committing/PRs, browser + computer use, scheduled/headless background jobs [s61, s62, s150].

**Limits to design around:**
- **Context drift** - past ~120K tokens, focus degrades; verbose shell output (e.g. npm logs) pollutes context. Mitigate with `/compact`, `/handoff`, and the Context Mode plugin [s33].
- **Cost multipliers** - Pro = $20/mo (~44K tokens / 5-hr window); multi-agent fan-out is linear in tokens (a 50-agent run = 50x; a $50 job can hit $2,500) [s59, s86].
- **Autonomy risk** - without git discipline it can over-engineer, modify unrelated files, or expose credentials. Use hooks + plan mode + worktrees [s33, s69].

---

## The composable primitives (how the pieces fit)

- **Skills** (`SKILL.md`) - reusable instruction packages with **progressive disclosure**: name+description (~100 tokens) load at startup; the full body (<5K) loads only when the task matches. Two kinds: *capability uplift* (new actions) and *encoded preference* (your style) [s33, s120].
- **Hooks** - event scripts at `PreToolUse` / `PostToolUse` / `SessionStart`. Security workhorse: a `PreToolUse` hook can block reading `.env` or running `curl` [s10, s69].
- **MCP (Model Context Protocol)** - open JSON-RPC standard connecting Claude to external tools/data (Jira, Sentry, Postgres) with no custom glue [s172, s213].
- **Subagents / Dynamic Workflows** - spawn isolated-context subagents that return only a summary (keeps the main context clean); Opus 4.8 can orchestrate hundreds in parallel for big migrations [s86, s196].
- **Plugins** - `/plugin install`; a distribution unit bundling MCP servers + skills + hooks + subagents [s58].
- **Slash commands** - e.g. `/compact` (summarize history to save tokens), `/handoff` (compress session to markdown for a fresh session/agent) [s33, s77].
- **Headless mode** - `claude -p` runs without the interactive UI for 24/7 background ops (scheduled CI maintenance, repo monitoring) [s150].
- **Agent SDK** - TS/Python library wrapping the Claude Code runtime; build custom autonomous agents with built-in tools (Read/Bash/Edit/WebSearch) without coding the agent loop [s10, s183].

---

## Highest-leverage productivity practices (named, real)

1. **Use a `CLAUDE.md`** at repo root for standing rules + architecture; `Shift+Tab` -> **Plan Mode** to explore + propose before editing [s111, s179].
2. **Caveman skill** - strips narration/filler, ~**65% fewer output tokens**, longer sessions [s33].
3. **`/grill-me` (Grill Me skill, 156k+ installs)** - interrogates your assumptions before any code is written [s33].
4. **Karpathy's 4 rules skill (144k+ stars)** - think before coding, keep it simple, surgical changes only, verify against success criteria [s33].
5. **Context Mode plugin** - intercepts verbose shell output, passes only meaningful errors, keeps a session log for recovery [s33].
6. **Superpowers plugin (752k installs)** - enforced TDD (deletes code written without a failing test first), Git worktrees, parallel subagents, dual-stage review [s32, s33].
7. **Sandbox + governance** - run on a cheap Linux VPS to protect the host; route enterprise traffic through an **MCP gateway** for tool limits, identity, and budget controls [s59, s69].

For the best plugins/MCP servers and where to find them, see `ecosystem-plugins.md`. For "should this client workflow be Code vs Cowork vs API," see `surface-comparison.md`.
