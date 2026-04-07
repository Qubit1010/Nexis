---
name: lead-gen
description: >
  NexusPoint lead generation pipeline. Discovers, scores, enriches, and personalizes
  high-quality prospects across LinkedIn, Apollo.io, Product Hunt, and Google — then distributes them
  to cold email, LinkedIn, and Instagram CRMs. Use this skill whenever the user says anything
  about generating leads, finding prospects, running the lead pipeline, scoring leads, enriching leads,
  exporting to CRMs, pipeline stats, or building a prospect list. Also trigger for phrases like
  "run lead gen", "find me leads", "who should I reach out to", "build my outreach list",
  "check the pipeline", "how many leads do we have", "any new prospects".
---

# Lead Gen Pipeline

## Location

```
projects/lead-gen/
```

Run all commands from that directory:
```bash
cd projects/lead-gen
python main.py <command> [options]
```

---

## Commands

### Full Pipeline
```bash
# Discover → score → enrich → personalize → export (full run)
python main.py run [--limit 20] [--dry-run]
```

### Individual Phases
```bash
# Discover leads from live sources
python main.py discover [--source all|linkedin-jobs|linkedin-profiles|google|product-hunt] [--limit 30] [--dry-run]

# Import Apollo.io CSV export (PRIMARY source — fastest path to verified leads)
python main.py import --source apollo path/to/apollo_export.csv [--dry-run]

# Import generic JSON (HarvestAPI or other)
python main.py import path/to/leads.json [--dry-run]

# Score all unscored leads (or rescore everything)
python main.py score [--rescore] [--dry-run]

# Enrich leads by tier (runs 4 concurrent workers)
python main.py enrich [--tier hot|strong|warm|all] [--dry-run]

# Generate personalization packages + outreach sequences via Claude
python main.py personalize [--tier hot|strong] [--dry-run]

# Export to CRM Google Sheets and/or CSV
python main.py export [--platform cold-email|linkedin|instagram|all] [--format sheets|csv|both] [--dry-run]
```

### Viewing & Stats
```bash
# Pipeline overview: tier breakdown, source breakdown, export counts
python main.py stats

# List leads with filters
python main.py leads [--tier hot|strong|warm|rejected] [--limit 20]

# Full profile for one lead (enrichment + personalization + sequences)
python main.py lead <lead_id>
# e.g.: python main.py lead LG-20260401-0001
```

---

## Pipeline Architecture

```
Discovery
  Apollo.io CSV import        → verified contacts with emails + tech stack (PRIMARY)
  LinkedIn Jobs Apify         → companies posting ops/admin jobs (pain signal)
  LinkedIn Profile Search     → founders by title + industry (Apify credits reset Apr 13)
  Google Search Apify         → supplemental LinkedIn discovery (CSE API needs enabling)
  Product Hunt GraphQL        → DISABLED — API now redacts all maker names/usernames
        ↓
  Deduplication (linkedin_url OR company+first_name)
        ↓
5-Layer ICP Scoring (0–100)
  L1: Contact Quality       0–20  (verified email +8, LinkedIn +6)
  L2: Company Quality       0–20  (has website +5, sweet spot size +5, industry +4)
  L3: Intent & Pain Signal  0–25  (tech debt signal +8, job pain +8, PageSpeed +4, funding +6)
  L4: Decision Maker Access 0–20  (Founder/Owner +20, C-Suite +16, Head/Dir +12)
  L5: Reachability          0–15  (professional email +4, LinkedIn active +5)
        ↓
Tier: HOT (≥80) | STRONG (≥60) | WARM (≥35) | REJECTED (<35)
        ↓
Deep Enrichment (concurrent — 4 workers via ThreadPoolExecutor)
  Firecrawl website crawl + CMS detection
  Google PageSpeed Insights (timeout: 45s)
  Hunter.io email finding (25/month) + SMTP fallback
  Proxycurl LinkedIn profile (HOT only — $0.01/call)
  Perplexity company news / funding signals
        ↓
Personalization (Claude — claude-sonnet-4-6)
  3 hooks, pain points, value prop, best channel
        ↓
Export
  Cold Email CRM (HOT/STRONG/WARM with email)
  LinkedIn CRM (HOT/STRONG with linkedin_url) — also exports to NexusPoint LinkedIn Outreach CRM
  Instagram CRM (HOT with instagram_url)
  CSV exports for Instantly/Lemlist
```

---

## Tier Logic

| Tier     | Score | Enrichment          | Personalization | Platforms                         |
|----------|-------|---------------------|-----------------|-----------------------------------|
| HOT      | ≥80   | Full + Proxycurl    | Claude          | Cold email + LinkedIn + Instagram |
| STRONG   | ≥60   | Full (no Proxycurl) | Claude          | Cold email + LinkedIn             |
| WARM     | ≥35   | Website + email     | Template-based  | Cold email only                   |
| REJECTED | <35   | None                | None            | Archived                          |

---

## Apollo.io Import (Primary Lead Source)

Apollo gives verified contacts with emails, LinkedIn URLs, company size, and tech stack — STRONG tier immediately at import, no enrichment required.

**Workflow:**
1. Sign up at apollo.io (free — no credit card)
2. Filter: Title = Founder/CEO/Owner, Industry = SaaS/E-commerce/Marketing & Advertising, Size = 1-50, Location = US/UK/AU/CA
3. Export → select up to 50 contacts → Export to CSV
4. Run:
```bash
python main.py import --source apollo ~/Downloads/apollo_export.csv
python main.py score
python main.py stats
```

**Why Apollo leads score STRONG immediately:**
- Verified email → L1 +8
- LinkedIn URL present → L1 +6
- Technologies column (Squarespace/Wix/WordPress) → L3 tech_debt +8 at import time
- Founder/CEO title → L4 +20
- Professional email domain → L5 +4
- Typical total: 60–68 → STRONG without enrichment

**Free tier:** 50 verified contacts/month. Paid ($49/mo) = 10,000/month.

---

## Tech Debt Signal (Pre-Enrichment)

The intent scoring layer detects tech debt platforms from `pain_signal` at import time — before Firecrawl enrichment runs. This means Apollo leads with WordPress/Squarespace/Wix in their Technologies column score +8 immediately.

Platforms detected: wix, squarespace, weebly, godaddy website builder, jimdo, strikingly, yola, webflow, wordpress

Guard is in place to prevent double-counting if Firecrawl later also detects the CMS.

---

## Environment Variables

Required in `projects/lead-gen/.env`:

```
APIFY_API_KEY=              # Apify — lead discovery (credits reset monthly)
OPENAI_API_KEY=             # Personalization fallback
FIRECRAWL_API_KEY=          # Website intelligence (crawl + CMS detection)
PROXYCURL_API_KEY=          # LinkedIn enrichment ($0.01/call, HOT only)
HUNTER_API_KEY=             # Email finding (25 free/month)
PAGESPEED_API_KEY=          # Google PageSpeed Insights (free)
GOOGLE_CSE_ID=              # Google Custom Search (needs CSE API enabled in GCloud Library)
PRODUCT_HUNT_API_TOKEN=     # PH token (set but disabled — API redacts maker data)
```

---

## Source Status

| Source | Status | Notes |
|--------|--------|-------|
| Apollo CSV import | LIVE | Primary source — 50 free verified leads/month |
| LinkedIn Jobs (Apify) | Credits depleted | Reset monthly — check `python main.py stats` |
| LinkedIn Profiles (HarvestAPI) | Credits depleted | Reset April 13 |
| Google Search (Apify) | Broken | Custom Search JSON API not enabled in GCloud Library |
| Product Hunt | Disabled | API redacts all maker names — not usable |

---

## Setup (first time)

```bash
cd projects/lead-gen
pip install -r requirements.txt
# Create .env with API keys above
python main.py stats  # verifies DB initializes correctly
```

---

## Common Workflows

**Apollo import run (recommended when credits available):**
```bash
python main.py import --source apollo ~/Downloads/apollo_export.csv
python main.py score
python main.py enrich --tier strong
python main.py personalize
python main.py export --platform all --format sheets
python main.py stats
```

**Export STRONG leads to LinkedIn Outreach CRM manually:**
Query `leads` + `scores` + `personalization` tables, format as:
`[Name, First Name, Company, Role, LinkedIn URL, Location, Pain Signal, Connection Note (≤300 chars), Status, Date]`
Append to sheet: `1rJM42Hd1kh8G4d3MGIO1SMILSyM86iU5nSD7QQTdOoo` → `Leads` tab

**Quick check what's in the pipeline:**
```bash
python main.py stats
python main.py leads --tier strong
```

**Preview a specific lead's full profile before exporting:**
```bash
python main.py lead LG-20260401-0001
```

**Dry run the full pipeline (no writes):**
```bash
python main.py run --limit 10 --dry-run
```

**Re-export after adding new leads:**
```bash
python main.py export --platform cold-email --format sheets
# (idempotent — already-exported leads are skipped automatically)
```

---

## Lead ID Format

`LG-YYYYMMDD-XXXX` — e.g., `LG-20260401-0042`

Use `python main.py leads` to find IDs, then `python main.py lead <id>` for full detail.

---

## Cost Notes

- **Apollo.io**: Free = 50 contacts/month. Paid $49/mo = 10,000/month. Best ROI in the stack.
- **Proxycurl**: ~$0.01/call — HOT leads only. Budget ~$1–2 for 100–200 HOT leads.
- **Hunter.io**: 25 free/month. Switches to SMTP fallback automatically after limit.
- **Firecrawl**: Free tier covers typical usage. 402 = credits exhausted.
- **Claude API**: ~$0.01–0.03 per lead personalization. Budget ~$1–3 for 100 leads.
- **PageSpeed**: Free (Google API, no billing required for basic usage).
