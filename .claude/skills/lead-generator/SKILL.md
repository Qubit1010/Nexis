---
name: lead-generator
description: Turns raw directory leads into enriched, outreach-ready rows on a consolidated "Main" sheet. Merges + dedups leads from multiple directories (Google Maps, Clutch, DesignRush, ...), then for each unique business resolves a website (via Clutch redirect-extraction when only a directory profile exists), scrapes that website FIRST for the company's Instagram/LinkedIn/Facebook and the founder's name + personal socials (footer/header, then About/Team/Contact pages), and only falls back to the in-repo research skill (fused Serper/Tavily/Exa) when the website doesn't have what's needed. Search-sourced founder matches are always flagged for manual confirmation rather than auto-written. Use this whenever the user wants to merge/dedup directory leads, find social profiles for a batch of businesses, resolve founders and their socials, or enrich a Google Maps / Clutch / DesignRush export. Trigger on "resolve socials for these maps leads", "find their instagram/linkedin/facebook", "find the founder", "enrich the directory leads", "merge these directory tabs", "dedup the leads", "process the main sheet", "find social profiles for [sheet/business]". Does NOT draft outreach messages or manage the CRM — leads-to-crm owns that. Directory *scraping* automation is out of scope (later).
---

# Lead Generator (v3 — website-first)

Turns raw directory leads into enriched rows on a single **Main** sheet. Two big jobs: (1) merge +
dedup leads from several directories into Main; (2) for each unique business, resolve the **company**
socials (Instagram, LinkedIn, Facebook) AND the **founder** (name + the founder's own IG/LI/FB),
writing everything back onto that business's Main row.

**The company's own website is now the primary source of truth**, not search. A live-verified batch
showed search-first founder resolution repeatedly attaching the wrong person — a same-named stranger,
someone in an unrelated past/current role, or a coincidental name/company-word overlap (see
`references/how-it-works.md` for the specific cases). The
`research` skill (fused Serper/Tavily/Exa) is now a **fallback**, only reached when the website doesn't
name a founder, and anything it finds is flagged for manual confirmation — never auto-written.

**What this skill does NOT do:** draft outreach copy, manage the CRM, decide whether a lead gets
messaged, or scrape the directories themselves (that automation is deferred). Resolved rows land on
the Main sheet only; CRM fan-out is a later step.

## Why website-first (not search-first)

A business's own About/Team/Contact page is "exact match, zero ambiguity" when it names a founder — it's
the company's own published claim. A generic search for "{company} founder OR owner OR CEO" matches
anyone loosely associated with those words at the company, including a person's unrelated past role, a
same-named stranger, or (when the company's own brand name is a common word) someone
whose personal name merely happens to overlap the company name. No confidence heuristic on search results
closes that gap reliably — which is why the website is checked first, and a search-sourced founder is
always surfaced for review rather than written straight to the sheet. Exa's index still can't return
`instagram.com`/`facebook.com` (`SOURCE_NOT_AVAILABLE`), so when search IS needed, Serper (Google SERP) +
Tavily carry those platforms. Full rationale + query patterns: `references/how-it-works.md`.

## The loop

Runs UNSANDBOXED (research + web-scraper need network). Sheet I/O needs a live **gws** token — if it
reports `invalid_grant: Token expired`, re-auth gws first.

### Phase 0 — merge + dedup directory tabs into Main
Aleem drops each directory's leads as one tab in a single Google Sheet.
```
python scripts/merge_leads.py --sheet-id <id> --main-tab Main [--source-tabs "Google Maps,Clutch,DesignRush"]
```
Normalizes every tab's headers, dedups across tabs AND against existing Main rows (website domain >
phone last-10 digits > normalized company+city, reusing leads-to-crm's `_domain`/`_digits`), and
appends only new uniques. Idempotent. Ensures the Main header carries every column (company +
founder + status). `--selftest` checks the keying.

### Phase 1 — read the next unresolved batch
```
python scripts/read_batch_main.py --sheet-id <id> --tab Main --limit 12
```
Same phone-clean + geo-exclude + resume rules as before; skips rows already fully resolved (has a
company social AND a founder), and carries any existing social/founder values so resolve fills only gaps.

### Phase 2/3 — resolve one business (website-first, search-fallback)
For each business from the batch:
```
python scripts/resolve.py --business '<json for this row>'
```
Runs, in order:
1. **Ensure a website** — the row's own `Website Link`, else Clutch redirect-extraction (`clutch_resolve.py`)
   when the `Link` column is a Clutch profile, else one light reverse-lookup search as a last resort.
2. **Website extraction FIRST, unconditionally** — fast free http pass (`scrape_socials.py`: footer ->
   /about/ -> /team/ -> /contact/), then escalates to the **web-scraper crawl4ai tier** (free) with
   `templates/founder_socials_schema.json` llm extraction for the founder's name + personal socials from
   About/Team prose. This is now the primary source for both company socials and the founder.
3. **Search gap-fill** for whatever company socials the website didn't have (unchanged: combined query,
   then per-platform `site:{platform}.com`).
4. **Founder search-fallback, only if the website named no founder** — `"founder of {company} {category}
   {location}"` (not a boolean-OR query), with a real confidence gate (company-token + founder-word
   proximity, checked against both the raw candidates and Tavily's synthesized answer text).

Prints a JSON report: `company_socials`, `founder`, `website` (+ whether it was freshly found),
`provenance` (per field: `"website"` or `"search"`/`"search_fallback"`), and `needs_review` — the list
of fields sourced from search that must be confirmed before writing (never auto-write these).

### Phase 4 — write results back onto the Main row
`run_batch.py` (below) does this automatically for anything NOT in `needs_review`. For a manual single
write:
```
python scripts/write_result_main.py --sheet-id <id> --tab Main --row <n> \
  --status "Resolved - instagram, linkedin, facebook" \
  [--website URL] [--instagram URL] [--linkedin URL] [--facebook URL] \
  [--founder NAME] [--founder-instagram URL] [--founder-linkedin URL] [--founder-facebook URL]
```
Writes the company socials + `Founder` + the three `Founder ... Link` columns + `Social Search
Status`. Ensures any missing columns exist first, so it never crashes mid-batch.

### Batch runner (Phases 1-4 in one loop)
```
python scripts/run_batch.py --sheet-id <id> --tab Main --limit 12            # incremental (new leads)
python scripts/run_batch.py --sheet-id <id> --tab Main --rows 2-165          # reprocess a row range
python scripts/run_batch.py --sheet-id <id> --tab Main --rows 2-165 --dry-run  # resolve+print, no writes
```
The permanent orchestrator. **Write policy (locked with Aleem 2026-07-16):**
- **Auto-writes** the company website + all company socials — each already passed its gate (website
  footer links, or search results token-verified against the company name).
- **Never auto-writes a founder.** Even a website team-page extraction can surface a prominent
  non-founder exec (one live case returned its current Chief Business Officer, not the co-founder), so every
  founder — website- or search-sourced — goes to a **review queue** (`docs/lead-generator-review-queue.md`)
  with its evidence (website, best guess + provenance, ranked LinkedIn candidates, the search answer) for
  a human confirm. Any stale founder value on a reprocessed row is **cleared**, so the sheet never shows
  an unverified founder.

**Incremental mode** (`--limit`) pulls the next unresolved batch. **Reprocess mode** (`--rows A-B`) re-runs
an explicit range that already carries data (bypasses the "already resolved" skip) — used after a resolver
logic change. Reprocess is **resume-safe**: finished rows get a `v3:` status marker and are skipped on a
re-run, so a batch that dies partway continues where it left off. Regenerate the full review queue anytime
with a `--dry-run` pass over the same range (dry-run ignores the marker).

## Files

```
scripts/
  merge_leads.py       — Phase 0: merge + dedup multiple directory tabs into Main (self-check)
  read_batch_main.py   — Phase 1: next unresolved batch from Main (phone/geo/resume + gap-fill)
  resolve.py           — Phase 2/3: website-first resolution + search fallback + confidence gate (self-check)
  clutch_resolve.py    — resolves a business's real website from its Clutch profile redirect (self-check)
  url_filters.py       — shared social-URL classifier (one source of truth with scrape_socials.py)
  scrape_socials.py    — free http footer/contact/team pass (fast tier of the website pass)
  write_result_main.py — Phase 4: write_row() + clear_fields() + CLI, writes/clears columns + status on Main
  run_batch.py         — permanent orchestrator: Phases 1-4, incremental + --rows reprocess, founder review queue
  read_batch.py / write_resolved.py / sheet_writer.py — legacy per-channel Instant-sheet flow (kept)
templates/
  founder_socials_schema.json — web-scraper llm schema (founder name + socials from About/Team)
references/
  how-it-works.md      — v3 flow + why website-first, query patterns, URL-shape rules, phone/geo rules
```

## Handoffs

- **Resolve a Clutch-only lead's website** -> `clutch_resolve.py` (this skill calls it).
- **Search / discover** target URLs or a missing website when the website pass doesn't have it ->
  `research` skill (this skill calls it, as a fallback).
- **Scrape a website** (About/Team, blocked sites) -> `web-scraper` skill, free tiers (this skill calls it).
- **CRM push / message drafting** -> `leads-to-crm` (out of scope here; deferred for the Main-sheet flow).
- The older per-channel flow (`read_batch.py` -> `write_resolved.py` into Instant IG/LI/FB sheets)
  still exists for the leads-to-crm handoff and is untouched.
