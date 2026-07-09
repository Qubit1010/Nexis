# Live Query Fallback — NotebookLM

When the loaded references + `research-synthesis.md` don't confidently answer a specific technical question (a current benchmark, a tool comparison, a version-era detail), **query the developer-advisor notebook before guessing.** Then persist the answer so it's cached next time.

## Notebook
- **Title:** `Developer Advisor - Curated Sources 2026`
- **Notebook ID:** `5c8257d3-cdb3-469e-8d8c-da500a99ea14`
- **CLI (full path):** `C:\Users\Aleem\AppData\Local\Programs\Python\Python313\Scripts\notebooklm.exe`
  (fallback: the `find_exe()` list in `_research/build_corpus.py`)

## Command (run via PowerShell, not Bash — Python isn't on the Bash PATH)
```powershell
$env:PYTHONIOENCODING="utf-8"
& "C:\Users\Aleem\AppData\Local\Programs\Python\Python313\Scripts\notebooklm.exe" `
  ask "<the question, phrased to pull specifics, tools, numbers>" `
  --json -n 5c8257d3-cdb3-469e-8d8c-da500a99ea14
```
`--json` returns `answer` (prose with inline `[n]`) + `references[]` (`{citation_number, source_id, cited_text}`). Resolve `source_id` against `_research/sources.json`. NotebookLM outputs UTF-8 **with a BOM** — parse with `utf-8-sig`.

## Trigger conditions (ALL true)
1. It's a specific technical knowledge question (a benchmark, a current tool/version, a comparison).
2. No confident answer after loading the mode's refs + scanning `research-synthesis.md`.
3. It's a knowledge question, not a build/blueprint request you can already answer from the scoreboard.

Do NOT run it for things already covered by `stack-scoreboard.md` + the matching playbook.

## 6-step decision flow
1. Load the mode's references.
2. Scan `research-synthesis.md` (incl. the "Live Query Additions" section at the bottom).
3. Still a gap? Run the live query above.
4. Present the answer — lead with the recommendation/number, cite the source URL.
5. **Log it:** append a dated entry to `research-synthesis.md`'s **"Live Query Additions"** section so step 2 catches it next time (no re-query).
6. **Honesty:** if a net-new fact's `source_id` isn't in `sources.json`, flag it as a fresh live-query result, not part of the locked 226-source corpus.

## Append format (into research-synthesis.md → Live Query Additions)
```
### [YYYY-MM-DD] (Q# — Topic) <the question>
- <key specific / number / recommendation>
- <second specific if any>
Source: <title> — <url>
```

## Notes
- **Corpus caveat:** the notebook is being populated by `_research/import_to_notebooklm.py` (resume-safe, quota-paced ~130–150/day). If the import isn't complete, the live query answers from the imported subset; the full 226-source corpus is always available on disk in `_research/exa/` + `sources.json`. See `_research/PENDING-IMPORT.md` for status.
- **Auth:** if "Authentication expired," run `notebooklm login` (browser sign-in as hassanaleem86@gmail.com).
- **Refresh:** to age-out stale benchmarks, re-run the Exa gather/boost + re-import + `build_corpus.py synthesize` (offer a quarterly refresh). New sources require a fresh pass; the live fallback only surfaces what's already in the notebook.
