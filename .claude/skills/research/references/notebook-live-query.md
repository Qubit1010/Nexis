# Live-Query Fallback

When the local refs (`research-synthesis.md` + the playbooks) don't answer a specific research-
technique question, fill the gap with a live cited pass **before guessing** — then log it back so it's
reusable. This skill is itself a research engine, so its primary live fallback is to research the gap
with its own deep mode.

## When to run (all true)
1. It's a specific technique/benchmark/tooling question (e.g. "does operator X still work", "cheapest
   SERP API at 1M/mo", "best 2026 email-verification method").
2. No confident answer after loading the relevant playbook + scanning `research-synthesis.md`
   (including Live Query Additions).
3. It's a knowledge question, not a "just run the research" request.

Do NOT run for things the playbooks + `service-selection.md` already cover.

## Tiers (in order)
1. **Local refs** — `research-synthesis.md` Q1-Q6 + the matching playbook.
2. **Self-research (primary live tier)** — run this skill on the gap question:
   ```
   python .claude/skills/research/scripts/research.py --query "<gap question>" --depth deep --save
   ```
   Fuses Exa+Tavily+Serper, extracts, writes a cited report. Present the answer leading with the
   finding + URL, then **append it to `research-synthesis.md` → "Live Query Additions"** so it's
   cached next time. Only cite sources the run actually returned.
3. **NotebookLM notebook (optional — currently unauthenticated)** — a `Search & Research Techniques
   2026` notebook mirroring `_research/sources.json` was **not created**: the NotebookLM CLI reported
   "Authentication expired" on 2026-07-14. To enable this tier later:
   - `notebooklm login` (interactive — Aleem runs it), then
     `notebooklm create "Search & Research Techniques 2026"`, then import the 108 URLs from
     `_research/sources.json`.
   - Record the notebook ID here and in the `reference_notebooklm_setup` memory.
   - Query: `notebooklm.exe ask "<q>" --json -n <ID>` (parse with `utf-8-sig` — the CLI writes a BOM).
   Until then, tier 2 is the live fallback (the rule explicitly sanctions an Exa pass when NotebookLM
   is down).

## Append format (into research-synthesis.md → Live Query Additions)
```
### [YYYY-MM-DD] (Q# - Topic) <question>
- <cited specific>
Source: <title> - <url>
```

## Refresh
Re-run `_research/gather.py` to refresh the 108-source corpus when the material ages (this category
moves fast — pricing and vendor facts especially). Offer a quarterly refresh.

## Notebook
- Notebook: `Search & Research Techniques 2026` — **not yet created** (auth expired 2026-07-14).
- CLI: `C:\Users\qubit\AppData\Local\Programs\Python\Python312\Scripts\notebooklm.exe`
- Notebook ID: _pending_ (add when created).
