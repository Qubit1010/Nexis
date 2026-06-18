# Archived: outreach skills + lead-gen pipeline (2026-06-18)

These four were NexusPoint's first-generation outreach stack. They carried a lot of
functionality Aleem no longer uses (Apify auto-scraping, cold-email sequencing, ICP
geo-filters) and the push pipeline had two persistent bugs: it silently dropped
freshly-scraped "New" rows and duplicated rows already in the CRM.

They were superseded by the **`leads-to-crm`** skill (`.claude/skills/leads-to-crm/`),
which does only the part Aleem actually runs today: read a manually-scraped
"Instant ... Leads" sheet, push genuinely-new rows into the matching CRM with a
Claude-Haiku Touch 1 message, keyed on a stable identity (Instagram `@handle`,
LinkedIn `/in/<slug>`) so it never drops or duplicates. It's channel-config-driven
and built to extend (Facebook next).

## Mapping

| Archived | Replaced by |
|---|---|
| `instagram-outreach/` (Apify hashtag scrape + GPT DMs → CRM) | `leads-to-crm` (Instagram channel). Sourcing is now manual; the skill only does sheet → CRM + messages. |
| `linkedin-outreach/` (Apify scrape + GPT connection notes → CRM) | `leads-to-crm` (LinkedIn channel). |
| `cold-outreach/` (full free cold-email pipeline: scrape → find emails → send → reply track) | Not replaced. Email outreach is paused; revive from here if Aleem restarts cold email. |
| `lead-gen/` (lead discovery, scoring, enrichment + `instagram_push.py` / `linkedin_push.py` / `push_blank_dms.py` / `dedup_instagram_crm.py` / `fill_blank_dms.py`) | The push/dedup logic was rebuilt clean in `leads-to-crm`. Discovery/scoring/enrichment are not carried over. |

## Why both bugs happened (for the record)

- **New rows dropped:** newer scrapes are post-level (post/reel URLs + "X likes"
  instead of follower counts). `instagram_push.py` hard-dropped those via
  `INVALID_URL_PATTERNS` (`/p/`) and a `MIN_FOLLOWERS` gate.
- **Sent rows duplicated:** dedup keyed off the normalized URL; post URLs collapsed
  to `.../p`, so a profile already in the CRM didn't match its post URL and got
  re-added. `leads-to-crm` keys on the @handle / slug instead, computed identically
  for source, CRM set, and the dedup pass, and re-checks the CRM every run (idempotent).

## Note on the lead-gen data dependency

`projects/website-quality-scorer/scripts/crawl_batch.py` reads two data files from
this archived `lead-gen/data/` folder (`leads.db`, `cold_email_touch1_2026-04-09.csv`).
Its `LEADS_DB` / `LEADS_CSV` path constants were repointed here when this was archived.

Kept for history per the repo's "archive, don't delete" rule. Do not load these as
active skills.
