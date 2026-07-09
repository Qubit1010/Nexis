# NotebookLM Import — Status & the "errored sources" explainer

**The skill is fully usable and NOT affected by any of this.** It cites the on-disk Exa corpus (`_research/exa/*` + `_research/sources.json`, all 226 sources with real URLs). The NotebookLM notebook only powers the live-query *refresh* fallback (`references/notebook-live-query.md`). Nothing in the skill breaks if the notebook is partial.

## What happened on the first import (2026-07-08)
Bulk-adding 226 URLs produced **100 `ready` + 108 `error`** entries in the notebook (the red rows you saw). Root causes:
1. **YouTube URLs (~13–19)** — NotebookLM can't ingest videos without accessible transcript data ("API returned no data for URL"). **Permanent** — these are now skipped by the importer and live as on-disk citations only.
2. **Bot-protected / paywalled sites** (medium.com, oreilly.com, some Cloudflare-guarded blogs) — NotebookLM's fetcher gets blocked. Often permanent for those specific domains.
3. **Throttling during the rapid burst** — adding faster than NotebookLM likes made a run of adds fail with a placeholder `error` entry. These are recoverable on a gentler re-run.

## The fix (importer is now self-healing)
`import_to_notebooklm.py` was hardened:
- **Skips YouTube URLs** (they can't ingest; kept in the citation corpus, not the notebook).
- **Only counts `ready` sources as "already present"** — so an old `error` entry no longer blocks its own retry.
- **Paces at 3s** (was 1.2s) to avoid the throttle wall.
- New phases: `clean` (delete all error-status sources), `status` (print ready/error counts), `clean-and-import`.

## Commands (PowerShell; sandbox disabled for network)
```powershell
$env:PYTHONIOENCODING="utf-8"
$py = "C:\Users\Aleem\AppData\Local\Programs\Python\Python313\python.exe"
$imp = ".claude/skills/developer-advisor/_research/import_to_notebooklm.py"

& $py $imp status            # ready/error counts
& $py $imp clean             # delete the red (error) sources
& $py $imp import            # gentle resume: adds missing non-YouTube URLs, skips ready ones
& $py $imp clean-and-import  # clean then resume in one go
```
Progress logs to `_research/import-log.txt`. All phases are resume-safe.

## Current state (2026-07-08)
- **Notebook holds 100 healthy `ready` sources** covering **topics 1–4** (architecture, frontend, backend, database) at ~24/26 each. Run `status` for the live count.
- **Topics 5–9 (AI engineering, agentic coding, mobile, practices, hosting) are NOT yet imported.** The account's **daily NotebookLM source-add quota was exhausted** after ~100 adds today — a gentle 3s-paced resume returned `ok=0, fail=110`, confirming a hard daily cap (not a per-second throttle).
- **To finish: re-run `import` tomorrow** (after the ~24h quota reset). It skips YouTube, only counts `ready` as present (so it targets exactly the missing topics 5–9), and now **auto-cleans its own error debris** at the end of the run, so a quota-blocked attempt won't leave red entries. One or two clean days should complete it (~90 sources left).
- YouTube (27 skipped) + a few bot-protected domains (Medium, some 502 blogs) will never import — expected; they remain valid `[sN]` citations on disk.

**Impact on the skill: minimal.** Topics 5–9 are fully covered by the static references (research-synthesis.md Q5–Q9 + the playbooks + stack-scoreboard), which is what the skill cites. The notebook only matters for the *live-query* fallback; until topics 5–9 finish importing, a live query on those topics leans on the static synthesis (already comprehensive).

## After enough sources are in (optional, for the live-query UUID path)
```powershell
& $py .claude/skills/developer-advisor/_research/build_corpus.py synthesize
```
Generates per-question `q*.json` + refreshes `sources.json` from the notebook. Not required day-to-day — the Exa-built `sources.json` already resolves every `[sN]`.

## Quarterly refresh
`gather_sources.py` → `boost_sources.py` → `import_to_notebooklm.py clean-and-import` → `build_corpus.py synthesize`.
