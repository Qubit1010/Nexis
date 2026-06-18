# Plans, Pricing + Claude vs Competitors (2026)

**Source basis:** `research-synthesis.md` Q8 (237-source NotebookLM synthesis). `[sN]` -> `_research/sources.json`. Plan structures come partly from NotebookLM's synthesized procurement report (`s193`) cross-checked against pricing pages (`s20`, `s52`, `s83`); token-per-window figures are estimates that shift with demand. **Honesty rule:** pricing changes often - confirm the live page / notebook before quoting a client a number.

---

## The plan lineup

| Plan | Price | Capacity (rough) | Key unlocks |
|------|-------|------------------|-------------|
| **Free** | $0 | ~30-100 msgs/day; drops 30-40% at peak | Sonnet 4.6 + limited Haiku, Artifacts, memory, file upload, web search [s20, s52, s193] |
| **Pro** | $20/mo ($17 annual) | 5x Free (~44K tokens / 5-hr window) | All models incl. Opus 4.8, **Cowork**, unlimited Projects, M365. *Claude Code on Pro is contested - verify* [s52, s193] |
| **Max 5x** | $100/mo | ~220K tokens / 5-hr | Full Claude Code [s83, s193] |
| **Max 20x** | $200/mo | ~880K tokens / 5-hr | Top queue priority [s83, s193] |
| **Team Standard** | $25/seat (min 5; $20 annual) | 1.25x Pro | SSO, shared workspaces, central billing; **no Claude Code** [s193] |
| **Team Premium** | $125-150/seat ($100 annual) | 6.25x Pro | **Full Claude Code**; seats mixable [s193] |
| **Enterprise** | Custom (~$20-75/seat + API) | **500K context** | HIPAA-ready, RBAC, SCIM, no training on inputs [s20, s193] |

---

## Which plan to buy (quick guide)

- **Just exploring / light use** -> Free [s193].
- **Daily individual use, want Opus + Cowork** -> Pro ($20) [s52].
- **Heavy coder / power user hitting Pro limits** -> Max 5x ($100) for full Code, Max 20x ($200) if you still cap out [s83]. Cheaper than raw API for all-day use [s59].
- **Small team, no heavy coding** -> Team Standard ($25/seat) [s193].
- **Engineering team needing Code** -> Team Premium ($125-150/seat) [s193].
- **Regulated / large org** -> Enterprise (500K context, HIPAA, SSO/SCIM, no-train) [s193].
- **Automation / product features** -> API, not a subscription (ToS) - see `building-with-claude.md` [s219].

---

## Claude vs ChatGPT vs Gemini (business, 2026)

At ~$20/mo, pricing has converged; choose on capability profile [s110]:

| | Best for | Edge | Watch-out |
|--|----------|------|-----------|
| **Claude** (Opus 4.8 / Sonnet 4.6) | Accuracy, writing, production coding | **~36% hallucination** on long-form factuality (vs GPT-5.5's 86%); 64.3% SWE-bench Pro | No native image/video gen; even Max 20x has a usage ceiling [s110] |
| **ChatGPT** (GPT-5.5) | Autonomous agents, tool ecosystems | 82.7% Terminal-Bench 2.0; Sora/voice/DALL-E; only truly unlimited $200 tier | **86% hallucination** on long-form factual work [s110] |
| **Gemini** (3.1 Pro) | Google Workspace, massive context | **2M-token context**; cheapest flagship API ($2/$12); $19.99 incl. 5TB storage | Ecosystem lock-in to Google [s110] |

**One-line positioning for clients:** Claude wins where being *right* matters - legal, finance, compliance, client-facing research, and production code - because of its honesty profile and coding lead [s110].

---

## Decision frameworks (where they live)

- **Which surface (chat/Code/Cowork/API):** `surface-comparison.md`.
- **Which model (Haiku/Sonnet/Opus/Fable):** `claude-models.md` (the 70/20/10 routing default).
- **Build vs buy:** `building-with-claude.md`.
