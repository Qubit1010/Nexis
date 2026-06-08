# Research-Backed Skills (NotebookLM-First)

When building a **new advice/strategy/knowledge skill** (or upgrading one from a "framework dump" to evidence-backed), do the research FIRST with NotebookLM. Don't ship opinions or aging frameworks as if they were fact. This is the standard set by `sales-playbook` and `marketing-advisor`.

**Applies to:** skills that give advice, strategy, benchmarks, or "best practice" (marketing, sales, pricing, content, ML/tech recommendations, etc.). Does NOT apply to pure execution/automation pipelines that just move data.

## The principle
Every load-bearing claim, number, or "best practice" in a knowledge skill must trace to a real, current source. Frameworks (Hormozi, Voss, Sandler, etc.) are allowed only where the research validates them, and they must be labeled as such. If there's no source for a number, say so - never invent or extrapolate.

## The method (run before/while building the skill)
Use the `notebooklm` skill (paths + login in the `reference-notebooklm-setup` memory). Mechanics: run via PowerShell with the full exe path; `Out-File -Encoding utf8` writes a BOM, so parse JSON with `utf-8-sig`.

1. **Create one notebook** for the topic: `notebooklm create "<Topic> <Year>"`.
2. **Deep web-research, several passes**, importing cited sources:
   `source add-research "<focused query>" --mode deep --no-wait` then `research wait --import-all --cited-only --timeout 1800`. Batch the passes in a background script.
3. **Synthesize with citations:** one `ask "<question>" --json` per sub-topic. The JSON gives `answer` (inline `[n]`) + a `references[]` array (`citation_number -> source_id`) - that's your traceability.
4. **Build the audit trail** in the skill's `_research/`: a deduped `sources.json` (global index + `uuid_to_index`) and the raw `q*.json` answers.
5. **Write `references/research-synthesis.md`** - the cited master doc, organized by question, with **benchmark tables**, **inline `[n]` citations**, and **honest "Not in sources" flags**. Distill it into tight, actionable reference files (a `channel-benchmarks.md`-style scoreboard + per-topic playbooks), each citing back to the synthesis.

## Quality bar (the sales-playbook standard)
- Inline citations resolvable to a real URL via `_research/sources.json`.
- A scoreboard/benchmarks file that leads with the number, then the tactic.
- Explicit honesty flags where data doesn't exist.
- Retire stale claims into a `what-not-to-do.md`; archive superseded framework files to `archives/` (don't delete).

## Always wire the live fallback
Every research-backed skill gets a `references/notebook-live-query.md`: when the local references + `research-synthesis.md` don't answer a specific question, **query that skill's NotebookLM notebook before guessing**, present the cited answer, then **append it to `research-synthesis.md` under a "Live Query Additions" section** so it's reusable. This keeps the skill current without re-running the whole pipeline. Record the notebook ID in the operation file + the `reference-notebooklm-setup` memory.

## Keep it fresh
Notebooks persist in the Google account, so the corpus can be refreshed with a new deep-research pass when benchmarks age (offer a quarterly refresh). The live fallback only surfaces detail already in the locked corpus - new sources require a fresh pass.

**Reference implementations:** `.claude/skills/sales-playbook/` and `.claude/skills/marketing-advisor/` (see each skill's `_research/`, `references/research-synthesis.md`, and `references/notebook-live-query.md`).
