# Live-Query Fallback

When the local refs (`research-synthesis.md` + the playbooks) don't answer a specific scraping question
(a new anti-bot technique, a better actor for a platform, a 2026 tool benchmark, a legal update), fill
the gap with a live cited pass **before guessing** — then log it back so it's reusable.

## When to run (all true)
1. It's a specific technique / tool / benchmark / legal question (e.g. "what beats Cloudflare Turnstile
   in 2026", "cheapest residential-proxy API at 5M req/mo", "is there an Apify actor for <platform>",
   "did the EDPB update scraping guidance").
2. No confident answer after loading the relevant playbook + scanning `research-synthesis.md`
   (including Live Query Additions).
3. It's a knowledge question, not a "just scrape this" request.

Do NOT run for things `engine-selection.md` / `scraping-playbook.md` / `extraction-schemas.md` /
`legal-and-ethics.md` already cover.

## Tiers (in order)
1. **Local refs** — `research-synthesis.md` Q1-Q8 + the matching playbook.
2. **Self-research via the `research` skill (primary live tier)** — run the sibling skill on the gap:
   ```
   python .claude/skills/research/scripts/research.py --query "<gap question>" --depth deep --save
   ```
   Fuses Exa+Tavily+Serper, extracts, writes a cited report. Present the answer leading with the finding
   + URL, then **append it to `research-synthesis.md` -> "Live Query Additions"** so it's cached next
   time. Only cite sources the run actually returned.
   - For "is there a free tool/API/actor for X", route to the scout skills first (api-scout,
     free-tool-scout, free-for-dev-scout, selfhosted-scout) — same Layer-0 rule the `research` skill uses.
3. **NotebookLM notebook (optional — currently unauthenticated)** — a `Web Scraping Techniques 2026`
   notebook mirroring `_research/sources.json` was **not created**: the NotebookLM CLI reported
   "Authentication expired" on 2026-07-14 (same as the `research` skill). To enable this tier later:
   - `notebooklm login` (interactive — Aleem runs it), then
     `notebooklm create "Web Scraping Techniques 2026"`, then import the 141 URLs from
     `_research/sources.json`.
   - Record the notebook ID here and in the `reference_notebooklm_setup` memory.
   - Query: `notebooklm.exe ask "<q>" --json -n <ID>` (parse with `utf-8-sig` — the CLI writes a BOM).
   Until then, tier 2 is the live fallback (the `research-backed-skills` rule explicitly sanctions an
   Exa/self-research pass when NotebookLM is down).

## Append format (into research-synthesis.md -> Live Query Additions)
```
### [YYYY-MM-DD] (Q# - Topic) <question>
- <cited specific finding> [url]
```
Keep the corpus current without re-running the whole `_research/gather.py` pipeline. New load-bearing
numbers require a real source — never invent or extrapolate (the house `research-backed-skills` rule).
