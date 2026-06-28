# Pending source import (finish later)

The curated NotebookLM notebook for this skill (`Student Advisor - Curated Sources 2026`,
ID `ffcd6d51-673d-4308-9400-c01976e3a849`) is **partially loaded**.

- **Imported so far:** ~139 of the 217 Exa-curated sources.
- **Why it stopped:** NotebookLM hit a daily add-source quota for the account (an earlier
  auto-research notebook consumed most of the day's quota before these were added). The remaining
  sources fail instantly with `ADD_SOURCE failed` until the quota resets (~24h). This is a quota
  wall, not a problem with the links.
- **A few will always fail:** paywalled journal pages (e.g., some Springer/SAGE article URLs) that
  NotebookLM can't fetch. Those are expected and fine — the data from them is already captured in the
  Exa highlight snippets in `_research/exa/*.md`.

## What still needs transferring

All 217 source URLs are saved in [`exa/urls.txt`](exa/urls.txt). The skill currently runs on the
~139 already imported **plus** the full Exa-curated data on disk (`_research/exa/*.json` + `*.md`),
which is the real citation base for the reference playbooks — so the skill is complete and usable now.

## How to finish the import (later)

The importer is **resume-safe** — it skips URLs already in the notebook and only adds the missing
ones. After the quota resets, run:

```powershell
& "C:\Users\Aleem\AppData\Local\Programs\Python\Python313\python.exe" `
  ".claude\skills\student-advisor\_research\import_to_notebooklm.py"
```

Then (optional) refresh the live-query corpus index:

```powershell
& "C:\Users\Aleem\AppData\Local\Programs\Python\Python313\python.exe" `
  ".claude\skills\student-advisor\_research\build_corpus.py" sources
```
