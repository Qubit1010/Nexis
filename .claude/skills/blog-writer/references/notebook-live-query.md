# Live Query Fallback

When the loaded references + `research-synthesis.md` don't confidently answer a specific knowledge question (a benchmark, a 2026 platform change, a tactic not covered), run a fresh cited research pass before guessing, then persist the answer so it's answered from disk next time.

## When to trigger (ALL of these)
1. It's a specific **knowledge/benchmark question** (e.g. "what's the current AI Overview citation rate for how-to content", "did Google change X in 2026"), not a "write the blog" request.
2. You checked the right section of `research-synthesis.md` + the relevant reference file and genuinely **missed**.
3. The answer would materially change the blog or the advice.

Do NOT trigger for normal writing/optimization — that's what the corpus already covers.

## The operation
NotebookLM auth is expired (repo-wide, since 2026-07-14), so the primary fallback is the **`research` skill's deep pass**, not NotebookLM. Run UNSANDBOXED (DNS fails otherwise), with Python 3.12:

```powershell
& "C:\Users\qubit\AppData\Local\Programs\Python\Python312\python.exe" `
  ".claude\skills\research\scripts\research.py" --query "<focused question 2026>" --depth deep --save --json
```

- Deep auto-saves a cited report to `research/YYYY-MM-DD-<slug>.md` and prints JSON (`report` + `results[]` with url/title).
- Read the saved report or the JSON `report` field. Parse JSON with `utf-8-sig` if you redirected to a file.
- One dead engine won't sink the run (Tavily is often quota-capped; Exa/Serper/Jina carry it).

## After the query
1. **Present** the answer leading with the number/finding, and **cite the URL(s)** from the new report.
2. **Append it to `research-synthesis.md`** under "Live Query Additions" (newest at bottom):
   ```
   ### [YYYY-MM-DD] (Q# - topic) <the question>
   - <key finding with the number>
   - Source: live research pass, <url>. (net-new, not in the locked 83-source corpus)
   ```
3. **Honesty:** flag it as a live-query finding, not part of the original locked corpus. If the pass finds nothing solid, say the corpus doesn't cover it — do not invent.

## Refresh
The corpus ages (AEO/GEO especially). To refresh benchmarks, re-run the five deep passes in `_research/gather_blog.sh` (or new focused queries), then re-run `_research/build_sources_index.py` and update `research-synthesis.md`. Offer a quarterly refresh.
