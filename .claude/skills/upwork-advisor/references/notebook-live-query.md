# Live Fallback — when the corpus doesn't answer it

**Purpose:** when a strategy question isn't answered by the loaded reference files or
`research-synthesis.md`, don't guess and don't answer from stale memory. Run a live pass, present the
sourced answer, then **append it to `research-synthesis.md` under "Live Query Additions"** so the
corpus grows and the next identical question is answered instantly from disk.

This matters most for the fast-moving parts of Upwork: **connect pricing, Boost mechanics, fee tiers,
badge thresholds, and anything about the 2026 algorithm or AI features.** Those age in months. The
structural advice (specialize, protect JSS, cut scope not rate) is stable and almost always already
in the references.

---

## When to trigger

Run the fallback when ALL of these are true:

1. Aleem asked a specific factual question — a number, threshold, fee, deadline, mechanic, or
   "is X still true in 2026".
2. After loading the relevant reference file(s) and scanning `research-synthesis.md`, you **don't
   have a confident, current answer**.
3. It's a knowledge question, not an audit, a triage, or a "save this to Docs".

**Check the "Known gaps" list** at the bottom of `research-synthesis.md` first. Six questions are
already known-unanswerable; for those, say so directly rather than burning a live pass.

Always run it before falling back to memory on anything price-, fee-, threshold-, or
algorithm-related.

---

## Tier 1: NotebookLM (preferred, currently blocked)

NotebookLM-first is the house standard per `.claude/rules/research-backed-skills.md`, but **auth was
flagged expired 2026-07-14** (`reference_notebooklm_setup` memory) and this corpus was therefore
built on Exa instead. **No notebook exists for this skill yet.**

If NotebookLM is restored, create one and record the ID here:

```
Notebook:     Upwork Strategy 2026   (NOT YET CREATED)
Notebook ID:  <fill in once created>
CLI:          $env:LOCALAPPDATA\Programs\Python\Python312\Scripts\notebooklm.exe
```

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\Scripts\notebooklm.exe" `
  ask "<question, phrased to pull specifics and numbers>" `
  --json -n <notebook-id>
```

Seed it from `_research/sources.json` (96 URLs already curated). Note the utf-8-sig BOM gotcha when
parsing JSON written by `Out-File -Encoding utf8`.

**Never run a destructive NotebookLM command** (`source clean`, `delete`) without asking Aleem first
— per the `feedback_notebooklm_no_autonomous_deletes` memory, it silently broke citation links once.

## Tier 2: Exa live search (the working path today)

Run via PowerShell with `dangerouslyDisableSandbox: true`:

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" tools/exa/exa_client.py answer "<question>"
```

Or reuse the corpus builder's own helpers for a cited answer plus a widened source pool — see
`_research/gather.py`, which imports `answer` and `search` from `tools/exa/exa_client.py`.

Depth is caller-controlled:
- **"deep"** — 3+ queries, 10+ sources, synthesize before answering
- **default / "medium"** — 1-2 queries, 5-7 sources
- **"quick"** — 1 query, 2-3 sources

Constrain to recent material (`start_published_date="2025-01-01"`) for anything about platform
mechanics. Stale Upwork numbers are worse than no numbers.

## Tier 3: the `research` skill

For a broader question that needs multi-engine fusion (Exa + Tavily + Serper + Jina), hand off to the
`research` skill rather than hand-rolling queries.

---

## Decision flow (every factual question)

1. **Load** the mode's reference file(s). Answer if covered.
2. **Scan** `research-synthesis.md` (the right Q section) + `upwork-scoreboard.md`. Answer if found.
3. **Check "Known gaps."** If listed there, say it isn't documented and stop.
4. **Miss? Run the live pass** (Tier 2 today, Tier 1 if restored).
5. **Present** the answer, leading with the number, and name the source.
6. **Log it** in `research-synthesis.md` → **"Live Query Additions"**, dated and tagged to the
   relevant Q section. That's what stops the same question being re-queried.
7. **Honesty:** flag clearly that the figure came from a live pass, not the locked 2026-07-26 corpus.
   Never invent a number, threshold, or fee.

---

## Standing items that need a live check

- **Specialized profiles** — single source claims phase-out May 2026 (Q1), date already past.
  Verify against Aleem's live account, then correct Q1 and `profile-playbook.md`.
- **Connect pricing and fee tiers** — re-verify on any question where the answer changes a spend
  decision.
- **Badge thresholds** — Q7 came from Upwork's own support docs, so it's the most durable section,
  but confirm before Aleem makes a badge-driven decision.
