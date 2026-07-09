# Research Fallback — the three-tier knowledge resolution

This is the core loop of the skill: **when you don't already know the best answer for the specific problem, go research it — don't default to a familiar stack.** Escalate through three tiers, in order, and stop at the first that confidently answers.

```
Tier 1  Local references   ──miss──▶  Tier 2  NotebookLM notebook  ──miss──▶  Tier 3  Exa live research
(curated corpus)                      (the 226-source notebook)               (fresh search for THIS problem)
```

Always prefer the lowest tier that actually answers. Only escalate on a genuine gap, not to show work.

---

## Tier 1 — Local references (default)

The curated corpus, already on disk:
- `stack-scoreboard.md` — problem-shape → best-fit lookup.
- `research-synthesis.md` — Q1-Q9 cited evidence (`[sN]` → `_research/sources.json`).
- The topic playbooks (`architecture-`, `web-stack-`, `ai-engineering-`, `agentic-coding-`, `mobile-`, `practices-and-hosting-`).
- `what-not-to-do.md` — the anti-pattern filter.

If these answer the problem confidently and current, you're done. Cite `[sN]`.

**Escalate when:** the problem is more specific than the corpus (a niche domain, a tool not covered, a very recent release, a benchmark you don't have), or two sources conflict and you need a tie-break.

---

## Tier 2 — NotebookLM live query

Ask the skill's own notebook (`Developer Advisor - Curated Sources 2026`, `5c8257d3-cdb3-469e-8d8c-da500a99ea14`) — it may hold detail the distilled refs dropped. Full mechanics + the append-back rule are in `notebook-live-query.md`.

Quick form (PowerShell, not Bash — Python isn't on the Bash PATH):
```powershell
$env:PYTHONIOENCODING="utf-8"
& "C:\Users\Aleem\AppData\Local\Programs\Python\Python313\Scripts\notebooklm.exe" `
  ask "<question, phrased for specifics/tools/numbers>" `
  --json -n 5c8257d3-cdb3-469e-8d8c-da500a99ea14
```
Present the cited answer, then append it to `research-synthesis.md` under "Live Query Additions" so it's reusable. Resolve `source_id` via `_research/sources.json`.

**Note:** the notebook currently holds ~100 sources (topics 1-4 fully; topics 5-9 pending a quota-reset import — see `_research/PENDING-IMPORT.md`). If a topic-5-9 query comes back thin, skip to Tier 3.

**Escalate when:** the notebook also misses — a genuinely novel problem, a brand-new framework/service, a niche vertical, or anything outside the 9 curated topics.

---

## Tier 3 — Exa live research (research THIS problem)

**This is the point of the skill: when the corpus doesn't cover the problem, go research the problem itself** rather than forcing a familiar answer. Use the shared Exa client (`tools/exa/exa_client.py`; loads `EXA_API_KEY` from repo `.env`). Live calls need the sandbox disabled.

Pick the mode by need:

```bash
# Fast cited answer to a specific question (best default for a single decision):
"C:/Users/Aleem/AppData/Local/Programs/Python/Python313/python.exe" tools/exa/exa_client.py \
  answer "which auth service best fits <specific constraints> in 2026"

# Multi-source search when you need to read + compare (best for a stack decision):
"C:/Users/Aleem/AppData/Local/Programs/Python/Python313/python.exe" tools/exa/exa_client.py \
  search "<problem-specific query> 2026 comparison tradeoffs" --num 8 --type deep --highlights

# Deep agentic research for a gnarly, multi-part architecture question:
"C:/Users/Aleem/AppData/Local/Programs/Python/Python313/python.exe" tools/exa/exa_client.py \
  research "<the specific architecture problem, with constraints>" --model exa-research -o report.json
```
Run with `PYTHONIOENCODING=utf-8` set, and the sandbox disabled (network). Prefer `--highlights` over full `--text` to control cost; `answer`/`research` cost more than `search`.

**How to use the results:**
- Query for the ACTUAL problem, not a generic topic. Pull the constraints from the intake (scale, data shape, latency, budget, compliance, existing systems) into the query.
- Read multiple sources; prefer primary/authoritative (official docs, vendor eng blogs, Fowler/ThoughtWorks/OWASP/DORA) over SEO listicles.
- Present the recommendation with source URLs. **Flag it as fresh live research, not from the locked 226-source corpus.**
- If the finding is durable and reusable, offer to fold it into the corpus: append a note to `research-synthesis.md` (Live Query Additions) and optionally add the sources to the Exa curation for the next quarterly refresh.

**Escalate when:** even Exa can't find a solid answer — then say so plainly, give the best-reasoned recommendation with explicit assumptions, and flag it as low-confidence. Never invent a benchmark or fabricate a "best practice."

---

## The rule this enforces

The skill's value is **researching the specific problem to the best available answer**, at whatever tier that lives. A familiar stack is never the answer just because it's familiar — it has to win on the problem's merits, sourced. When in doubt, go one tier deeper before you recommend.
