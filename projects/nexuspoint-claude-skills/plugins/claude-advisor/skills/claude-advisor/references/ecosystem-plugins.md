# Claude Ecosystem - Plugins, MCP Servers, GitHub Tools (2026)

**Source basis:** `research-synthesis.md` Q6 (237-source NotebookLM synthesis). `[sN]` -> `_research/sources.json`. **Honesty rule:** install counts/star counts drift - treat them as "as of mid-2026"; confirm a specific tool via the live notebook if a client is relying on it. Don't recommend a tool you can't name a source for.

**Headline:** The ecosystem exploded - **15,134+ Claude Code plugin repos indexed by May 2026** [s29]. The skill is curation, not collection: bloated context kills agent sessions, so install a lean stack and discover the rest on demand.

---

## Where power users find tools

- **hesreallyhim/awesome-claude-code** (36.8k stars) - the canonical hand-curated list of skills, hooks, slash-commands, agents; broken tools get cut [s29].
- **punkpeye/awesome-mcp-servers** + **wong2/awesome-mcp-servers** - primary MCP server directories [s29].
- **rohitg00/awesome-claude-code-toolkit** - single-source toolkit: 135 agents, 176+ plugins, MCP configs [s150].
- **Official marketplace** - in-CLI `/plugin marketplace add`, or the Claude Desktop "Discover" tab [s32].

---

## Most useful plugins (with installs)

| Plugin | Installs | What it does |
|--------|----------|--------------|
| **Frontend Design** | 829k | Forces production-grade UX/UI, bans "AI slop" aesthetics before coding [s32] |
| **Superpowers** | 752k | Multi-agent SDLC: structured brainstorming, enforced TDD, subagent delegation [s32] |
| **Code-Simplifier** | 284k | Anthropic's internal refactor for readability - **no behavior change** [s32, s33] |
| **TypeScript LSP** | 177k | IDE-grade intelligence: jump-to-def, diagnostics, type errors after edits [s32] |
| **Security Guidance** | 175k | Real-time hook warning on injection/XSS/unsafe patterns as Claude writes [s32] |
| **Pyright LSP** | 91k | Same LSP intelligence for Python [s32] |

---

## Most useful MCP servers

- **Context7** (348k) - pulls live, version-specific docs into context, killing outdated-API hallucinations [s32].
- **Zilliz claude-context** - semantic code search over a vector index (BM25 + dense); ~**40% token reduction** vs scanning whole dirs [s237].
- **Composio** - managed MCP gateway with secure auth to **1,000+ apps** (send email, create Linear issues, read Slack) [s32].
- **Firecrawl** - reliable web scraping/search/browser automation; clean markdown from JS-heavy sites [s33].

---

## Open-source standouts (GitHub)

- **Claudebase** - backs up/restores/syncs your entire Claude Code config (agents, hooks, memory, MCPs, skills) to a private GitHub repo; multi-machine conflict detection, profile switching [s114, s116].
- **claude-mem** (35.9k stars) - persistent SQLite memory; auto-captures, AI-compresses, and re-injects context into future sessions [s150].
- **getburnd** + **llm-prices** - cost control: getburnd spots token leaks in session files; llm-prices is an MCP server that checks costs across 167 models before expensive requests [s150].

---

## Power-user tactics

1. **Start minimalist (5 plugins):** one LSP (e.g. TypeScript LSP) + GitHub MCP + Security Guidance + Commit Commands + one cross-app tool (Composio). Context bloat is the #1 session killer [s32].
2. **Lists are for discovery, not bulk install** - bookmark them, install only when you hit a specific friction point [s29].
3. **Sync your brain day one** with Claudebase - weeks of custom subagents/`SKILL.md` files vanish if a disk wipes and you didn't sync [s116].
4. **Caveman** for token control (~65% fewer output tokens) [s33].
5. **Run code-simplifier only pre-PR**, not on every change, to avoid burning tokens [s33].

For "how do the primitives (skills/hooks/MCP/subagents) actually work," see `claude-code-guide.md`. For granular mechanics, defer to the **claude-code-guide** agent.
