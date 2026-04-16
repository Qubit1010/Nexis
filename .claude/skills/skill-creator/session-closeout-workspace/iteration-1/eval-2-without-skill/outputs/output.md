## Session Summary — 2026-04-12

### 1. Content Engine Dashboard — Major Feature Push

**Content Modes + Pillar System**
- Added 4 content modes: News/Analysis, Opinion/POV, Personal Story, Tutorial/How-to
- Added 7 content pillars
- Each mode auto-selects a default pillar set; user can override manually

**New Format: Instagram Caption** (standalone)
**Improved Instagram Carousel Prompt** — stricter per-slide structure

**URL Fetch Context** — new `/api/fetch-url` endpoint for URL-based content import
**Content Scheduling** — full scheduling modal + schedule page + `/api/schedule` endpoint
**Ideate Page** — added source filter tabs, sort options, 4th idea source (Saved Articles)

---

### 2. Lead Gen Pipeline — Architecture Overhaul

- **Removed** old scrape-first model: deleted `linkedin_jobs.py`, `linkedin_profiles.py`, `google_search.py`, `product_hunt.py`
- **New import-first model**: leads come in from Google Sheets (`sheets_importer.py`)
- **main.py rewritten** — CLI with clean commands
- **Outreach push scripts added**: `cold_email_push.py`, `linkedin_push.py`, `instagram_push.py`
- **Transformers upgraded**: email, linkedin, instagram transformers all improved
- SKILL.md updated

---

### 3. Daily News Brief
- Minor prompt refinement in `projects/daily-news-brief/src/lib/pipeline/prompts.ts`

---

### 4. CLAUDE.md + References Cleanup
- Added `@context/ideas.md` to context index
- Skills backlog reorganized
- Daily AI/Tech Brief marked complete
- Deleted old copywriting references from `references/`
- Added `references/Copy-Writing/` and moved voice principles to content-engine skill

---

### Key Decisions Worth Logging

1. Lead gen switched from scrape-first to import-first
2. Content engine now has content modes + pillars as first-class controls
3. Copywriting references centralized into skill-level location
