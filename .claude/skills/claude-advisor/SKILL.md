---
name: claude-advisor
description: >
  The go-to, research-backed guide to everything Claude. Explains how Claude works, the differences between the surfaces - Claude.ai chat (Projects, Artifacts), Claude Code, and Claude Cowork (the agentic product) - plus Desktop, mobile, and the API, and gives a clear "which one is best for this task" decision framework. Covers Claude Code intricacies and productivity (hooks, MCP, subagents, skills, plugins, slash commands, Agent SDK), business applications and creative use cases across functions, the ecosystem (best plugins, MCP servers, GitHub tools, marketplaces), building with the Claude API, model selection (Opus vs Sonnet vs Haiku), the Free/Pro/Max/Team/Enterprise plans, and the full second-brain / AI memory / AI OS topic (Obsidian, Graphify, LLM Wiki/Karpathy, the 5 levels of an AI second-brain, step-by-step setup, agency setup). Every load-bearing claim is grounded in a NotebookLM synthesis of cited 2026 sources (references/research-synthesis.md + surface-comparison.md), with a live-query fallback to the notebook when the static refs miss. Use this skill whenever Aleem (or a prospect/client question routed through him) asks anything about Claude: "what's the difference between Claude chat and Claude Code", "which Claude should I use for X", "can I build this workflow in Claude Code", "is X possible in Claude Code", "Opus vs Sonnet vs Haiku for this", "what is Claude Cowork", "how are businesses using Claude", "best Claude Code plugins / MCP servers", "useful Claude tools on GitHub", "how do I get more productive with Claude Code", "which Claude plan should I buy", "how does Claude compare to ChatGPT/Gemini", "explain Claude to a client", "build the free Claude guide / lead magnet", "what is a Claude second-brain", "how do I set up Obsidian with Claude", "what is Graphify", "what is LLM Wiki", "how do I make Claude remember everything", "build an AI OS for my agency", or "how to set up Claude as my second brain". Make sure to use this skill even when the user doesn't say the word "Claude" but is clearly asking which AI surface or model fits a task, or wants a comprehensive explainer of Claude's capabilities. For deep API/SDK reference specifics, it hands off to the claude-api skill; for granular Claude Code feature mechanics, it defers to the claude-code-guide agent.
argument-hint: [question about Claude, its surfaces, models, ecosystem, or a "which should I use" decision]
---

# Claude Advisor

NexusPoint's research-backed brain for everything Claude. Two jobs:
1. **Aleem's internal go-to guide** - fast, specific answers ("which surface/model for this task", "is X possible in Claude Code", "what plugin do I need", deep Claude Code/Cowork/API intricacies).
2. **A comprehensive guide for a business/general audience** - the basis for a free lead magnet on the NexusPoint site (the `guide` mode; final structure is TBD with Aleem - see below).

Both draw from the same cited corpus. Lead with the answer, ground it in the 2026 research, never invent a spec/price/feature.

## Operating principles (read once)

- **Research-backed, not memory-backed.** This skill is built on a NotebookLM synthesis of cited 2026 sources. `references/surface-comparison.md` is the scoreboard; `references/research-synthesis.md` is the cited evidence behind it. Claude's products move fast, so prefer the corpus + live notebook over training memory on anything version-, price-, or feature-specific.
- **Honesty rule.** Never quote a model name, price, limit, or feature that isn't in `_research/` / the references / the notebook. If you don't have it, run the live fallback (`references/notebook-live-query.md`); only after a genuine notebook miss do you say the corpus doesn't cover it. Flag any net-new fact that came from a live query rather than the locked corpus.
- **Lead with the recommendation.** For "which should I use" questions, give the pick first, then the one-line why, then the tradeoff. Don't survey every option unless asked.

## Boundaries / handoffs (important)

- **claude-advisor owns:** the strategic/business/comparative layer - explaining Claude, comparing the surfaces, "which surface + which model for this task", productivity patterns, business + creative use cases, the ecosystem map, plan selection, and the comprehensive guide / lead magnet.
- **Hand off deep API/SDK specifics to the `claude-api` skill** (exact model IDs, request params, streaming, token counting, pricing tables, SDK code). When the ask is "write the API call" or "what's the exact parameter for X", frame the approach here and point to `claude-api`.
- **Defer granular Claude Code feature mechanics to the `claude-code-guide` agent** (the precise behavior of a specific hook event, a settings.json key, a slash-command edge case). This skill gives the practical, high-leverage version; that agent is the exhaustive reference.
- State the handoff when you make it; don't silently stop.

## Context to load first

Before answering, read:
- `references/surface-comparison.md` - the 2026 scoreboard + "best for X" decision table (near-always useful).

Then load the mode-specific reference(s) below. Consult `references/research-synthesis.md` when you need fuller context or to cite the source behind a claim. **Max 3 reference files per invocation** (surface-comparison is the lightweight default; swap research-synthesis in when depth is needed). For NexusPoint-specific framing (pitching Claude to clients, internal use), also skim `context/work.md`.

---

## Mode Detection

Auto-detect the mode, then load the corresponding references.

| Mode | Trigger keywords | References to load |
|------|-----------------|-------------------|
| **decide** | "which should I use", "which is best for", "can I do X in Claude Code", "is X possible in", "chat or code or cowork", "best tool for this task", client-workflow feasibility | `surface-comparison.md` (+ `claude-code-guide.md` and/or `claude-cowork-guide.md` as relevant) |
| **models** | "which model", "Opus vs Sonnet vs Haiku", "model for this task", capabilities, context window, token pricing, "is Opus worth it" | `claude-models.md` |
| **code** | Claude Code intricacies, hooks, MCP, skills, plugins, subagents, slash commands, headless, "productivity with Claude Code", "what can Claude Code do" | `claude-code-guide.md` (+ `ecosystem-plugins.md`) |
| **cowork** | "Claude Cowork", "agentic", "autonomous", "Claude as a teammate", "Cowork vs Claude Code" | `claude-cowork-guide.md` |
| **second-brain** | "second brain", "second-brain", "AI memory", "persistent memory", "Claude memory", "Obsidian", "Graphify", "LLM Wiki", "AI Wiki", "AI OS", "AI operating system", "Claude as my assistant that remembers everything", "how do I make Claude remember", "build a knowledge base with Claude", "agency brain", how to set up Claude for my agency/business | `claude-second-brain.md` (+ `claude-code-guide.md` for Claude Code mechanics) |
| **business** | "how are people using Claude", "business applications", use cases, ROI, creative uses, "use Claude for my agency/clients", "pitch Claude to a client" | `business-applications.md` |
| **ecosystem** | "best plugins", "MCP servers", "Claude tools on GitHub", "plugin marketplace", "useful add-ons", "awesome claude" | `ecosystem-plugins.md` |
| **building** | "Claude API", "Agent SDK", "tool use", "function calling", "prompt caching", "build a custom agent", "build vs buy" | `building-with-claude.md` (+ hand off deep specifics to `claude-api` skill) |
| **plans** | "which plan", "Pro vs Max", "Team / Enterprise", "pricing", "usage limits", "Claude vs ChatGPT/Gemini" | `plans-and-pricing.md` |
| **guide** (BUILT) | "build the lead magnet", "make the free Claude guide", "the giveaway guide", "update the playbook" | The lead magnet is shipped: `references/The-Practical-Claude-Playbook-FULL.pdf`. To revise, edit the section files + rerun `build_full_playbook.py` (see "Lead magnet" below) |
| **advise** (default) | anything Claude-related not clearly matched | `surface-comparison.md` + the 1-2 most relevant references |

If ambiguous between two modes, pick the more specific one. If the ask spans two modes, handle the primary first, then offer the second.

---

## Workflow

### Step 1: Parse and classify
Extract: **mode**, **who it's for** (Aleem himself, a client/prospect, or the public guide), **the task behind the question** (for "which should I use", what are they actually trying to do), and **specificity needed** (quick pick vs full explainer).

If too vague to act on, ask ONE question (e.g., "What are you trying to get done - a one-off task, an ongoing workflow, or a built product?"). Don't ask multiple at once.

### Step 2: Load context and references
Load `references/surface-comparison.md` first, then the mode-specific reference(s). Pull citations/depth from `references/research-synthesis.md` when needed.

### Step 3: Decide response type
**Quick advisory** (questions, "which/should I/can I"): direct answer under ~300 words. Lead with the pick/answer + the one specific 2026 fact behind it, then the key tradeoff, then one concrete next step.

**Structured explainer / guide** ("explain X", "walk me through", "give me the full picture", or `guide` mode): use the explainer format below. For substantial outputs, offer the Google Doc export.

### Step 4: Ground in research (not memory)
- **Lead with the concrete fact, then the implication.** ("Claude Code can run that workflow headlessly via the Agent SDK; you'd wire it as a scheduled job, no chat UI needed. The tradeoff vs Cowork is...")
- **Quote specifics from the references** (resolve deeper citations via `research-synthesis.md` -> `_research/sources.json`).
- **Live fallback:** if the loaded references + `research-synthesis.md` don't confidently answer a specific knowledge question - especially anything version/price/feature-sensitive - **query the live notebook** before answering from memory. Follow `references/notebook-live-query.md` (ask the notebook, present the cited answer, append the finding to `research-synthesis.md` under "Live Query Additions"). Only after a genuine notebook miss do you say the corpus doesn't cover it.
- **Honesty:** if there's no fact for something (and the notebook has none either), say so. Flag any net-new fact that came from a live query rather than the locked corpus.

### Step 5: Deliver and offer follow-ups
- Substantial explainers/guides: offer "Want me to save this to Google Docs?"
- "Which should I use" answers: end with the next step (e.g., "Want me to sketch how that'd run in Claude Code?").
- For client-facing framing: offer to turn it into a use-case pitch (hand to `ai-use-case-generator`) or a proposal (hand to `proposal-generator`).

---

## Writing Rules

- **Internal (to Aleem):** direct, analytical, no fluff. Bullets over paragraphs. Say it in one line if you can.
- **External / guide / client-facing:** authoritative yet natural. **No emojis. No em dashes** (use commas or periods). Write like a sharp operator explaining a tool he uses daily, not a vendor brochure.
- **Be concrete:** name the model, the surface, the plan, the tool, the number. Vague is useless here.
- **The marquee question** ("a client wants a workflow built - is that possible in Claude Code, and which surface is best?"): answer feasibility first (yes/no/with-caveats), then the recommended surface, then the rough shape of how it'd be built, then when a different surface (Cowork, API, chat) would be the better call. Use `surface-comparison.md`'s decision table.

### Explainer / guide structure
For full explainers and the lead-magnet guide, use clear H2/H3 sections, a short "bottom line" up top, comparison tables where a decision is involved, and concrete examples. Keep claims cited-able back to `research-synthesis.md`.

---

## Edge Cases

| Scenario | Action |
|----------|--------|
| Vague ask ("tell me about Claude") | Ask ONE scoping question, or default to `surface-comparison.md` overview |
| Version/price/feature question, refs silent | Run the live notebook fallback before answering from memory |
| "Write the API call / exact params" | Frame the approach, hand off to **claude-api** skill |
| Granular Claude Code feature mechanic | Give the practical answer, point to the **claude-code-guide** agent for the exhaustive spec |
| Asked for a spec/price you don't have | Live-query the notebook; if still nothing, say so - never invent |
| "Build the lead magnet" | This is `guide` mode but the structure is DEFERRED - confirm the structure with Aleem before assembling |
| Client use-case pitch | Frame here, hand to **ai-use-case-generator** |
| Google Docs script fails | Output the guide inline, note the failure |

---

## Reference Map

```
references/
├── research-synthesis.md     # MASTER: Q1-Q8 cited synthesis of 2026 sources + "Live Query Additions"
├── surface-comparison.md     # the 2026 scoreboard + "best for X" decision table (load by default)
├── claude-models.md          # Opus/Sonnet/Haiku lineup, context, pricing, which model when
├── claude-code-guide.md      # Claude Code intricacies + productivity (granular -> claude-code-guide agent)
├── claude-cowork-guide.md    # the agentic product: what it is, use cases, limits, vs Claude Code
├── claude-second-brain.md    # second-brain / AI memory / AI OS: concept, 5 levels, Obsidian, Graphify, LLM Wiki, step-by-step setup, agency setup
├── business-applications.md  # use cases by function + creative uses + ROI
├── ecosystem-plugins.md      # best plugins, MCP servers, GitHub tools, marketplaces
├── building-with-claude.md   # API/agents/MCP/caching (granular -> claude-api skill)
├── plans-and-pricing.md      # Free/Pro/Max/Team/Enterprise + Claude vs ChatGPT/Gemini + decision framework
├── what-not-to-do.md         # misconceptions, anti-patterns, real limits, security, what Claude can't/shouldn't do
└── notebook-live-query.md    # LIVE FALLBACK: ask the NotebookLM notebook on a miss; appends findings to research-synthesis.md
_research/                     # audit trail: sources.json + q1..q8.json + logs + build_corpus.py (refreshable)
scripts/save_guide.py          # export a guide/answer to a formatted Google Doc (NexusPoint Guides folder)
```

Sibling skills/agents: **claude-api** skill (deep API/SDK reference), **claude-code-guide** agent (exhaustive Claude Code mechanics), **ai-use-case-generator** (turn Claude capabilities into a client pitch), **proposal-generator** (full proposals), **marketing-advisor** / **sales-playbook** (the reference implementations this skill mirrors).

---

## Google Docs Output (User-Gated)

Only for substantial outputs (full explainers, the comprehensive guide, the lead magnet). Do NOT offer for quick advisory answers.

When the user says yes, pipe a JSON plan to the save script:

```bash
echo '<JSON>' | python .claude/skills/claude-advisor/scripts/save_guide.py
```

Creates a formatted Google Doc in the "NexusPoint Guides" folder and returns the URL.

**JSON structure:**
```json
{
  "title": "The Complete Guide to Claude (2026)",
  "sections": [
    { "heading": "Section Title", "level": 1, "body": "Optional paragraph text" },
    { "heading": "Subsection", "level": 2, "bullets": ["Bullet one", "Bullet two"] },
    { "heading": "Comparison", "level": 2, "table": { "headers": ["Surface", "Best for"], "rows": [["Claude Code", "..."]] } }
  ]
}
```

Avoid em dashes and special unicode in the JSON (plain hyphens) to keep Google Docs encoding clean. If the script fails, output the guide inline and note the failure.

## Lead magnet (BUILT - 2026-06-17)

**"The Practical Claude Playbook"** is the shipped lead magnet: a 66-page PDF at `references/The-Practical-Claude-Playbook-FULL.pdf` (front matter + Table of Contents + 30 sections, 10 each across Beginner / Intermediate / Advanced), CTA -> https://nexus-point.co/.

- **Structure:** 3 tiers x 10 sections. Beginner = what Claude is + the surfaces + prompting + use cases + plans/safety. Intermediate = Cowork, models, connectors, Skills, scheduling/routines, the Four C's assistant. Advanced = Claude Code, custom workflows/subagents, orchestration, plugins/CLI/MCP, integration combos, building systems, the business operating system, real-business workflows.
- **Source of truth:** content is grounded in `references/research-synthesis.md` (including the 2026-06-16 "Live Query Additions" from ~47 practitioner-YouTube sources). Keep honesty flags on version/price-sensitive claims; no em dashes; clean encoding.
- **Build tooling (not in this repo, lives in C:\tmp):** `playbook_pdf.py` (reusable reportlab engine), `section_01.py`..`section_30.py` (per-section content), `build_frontmatter_pdf.py`, and `build_full_playbook.py` (merges + adds the TOC + continuous page numbers). To revise: edit a section file, re-run it, then re-run `build_full_playbook.py`.
- Note: built with a bespoke PDF generator rather than `save_guide.py` (which targets Google Docs) because Aleem wanted a styled, branded PDF. `save_guide.py` + the `guide` mode remain available for a Google Docs version if needed.
