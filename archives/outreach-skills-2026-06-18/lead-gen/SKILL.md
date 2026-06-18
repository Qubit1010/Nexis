---
name: lead-gen
description: >
  NexusPoint lead generation pipeline. Imports manually-curated leads from a Google Sheet,
  scores them with a 5-layer ICP system, enriches with website intel + email finding,
  generates personalized outreach via Claude, and exports to cold email, LinkedIn, and Instagram CRMs.
  Use this skill whenever the user says anything about generating leads, finding prospects,
  running the lead pipeline, scoring leads, enriching leads, exporting to CRMs, pipeline stats,
  or building a prospect list. Also trigger for phrases like "run lead gen", "find me leads",
  "who should I reach out to", "build my outreach list", "check the pipeline",
  "how many leads do we have", "any new prospects".
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

## Standard Workflow

```bash
# 1. Import from the manually-curated Google Sheet (set input_sheet_id in config.py first)
python main.py import --source sheets

# 2. Score all unscored leads
python main.py score

# 3. Enrich qualified leads (website intel, email finding)
python main.py enrich --tier warm,strong,hot

# 4. Export to all CRM sheets
python main.py export --platform all --format sheets

# 5. Check stats
python main.py stats
```

---

## Commands

### Import
```bash
# Import from Google Sheet (primary source)
python main.py import --source sheets
python main.py import --source sheets --sheet-id <SHEET_ID>
python main.py import --source sheets --dry-run

# Import from Apollo CSV export
python main.py import --source apollo path/to/apollo_export.csv [--dry-run]

# Import generic JSON
python main.py import --source harvestapi path/to/leads.json [--dry-run]
```

### Score, Enrich, Personalize
```bash
# Score all unscored leads (or rescore everything)
python main.py score [--rescore] [--dry-run]

# Enrich leads by tier (4 concurrent workers)
python main.py enrich [--tier hot|strong|warm|all] [--dry-run]

# Generate personalization packages + outreach sequences via Claude
python main.py personalize [--tier hot|strong] [--dry-run]
```

### Export
```bash
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
```

### Run (enrich + personalize + export)
```bash
# Runs enrich → personalize → export on existing DB leads
python main.py run [--limit 20] [--dry-run]
```

---

## Google Sheet Setup

Aleem manually curates leads in a Google Sheet. Mark rows to include with **"Yes"** in the `Include` column. All other rows are skipped.

**Sheet column format (LinkedIn export style):**

| Column | Notes |
|--------|-------|
| First Name | |
| Last Name | |
| Title / Position / Job Title | any variant works |
| Company | |
| Email / Email Address | optional — pipeline will try to find it |
| LinkedIn URL / Profile URL | optional |
| Company Website / Website | |
| Industry | |
| Company Size / Employees | |
| Location | |
| Include | **"Yes"** = keep, anything else = skip |

**Config (`config.py`):**
```python
"input_sheet_id":  "YOUR_GOOGLE_SHEET_ID",
"input_sheet_tab": "Sheet1",
"include_column":  "Include",
"include_value":   "yes",
```

Or pass inline: `python main.py import --source sheets --sheet-id <ID>`

---

## Pipeline Architecture

```
Google Sheet (manually curated)
  Aleem marks rows Include = Yes
        |
  sheets_importer.py reads via gws CLI
        |
  Deduplication (linkedin_url OR company+first_name)
        |
5-Layer ICP Scoring (0-100)
  L1: Contact Quality       0-20  (verified email +8, LinkedIn +6)
  L2: Company Quality       0-20  (has website +5, sweet spot size +5)
  L3: Intent & Pain Signal  0-25  (tech debt +8, job pain +8, PageSpeed +4, funding +6)
  L4: Decision Maker Access 0-20  (Founder/Owner +20, C-Suite +16, Head/Dir +12)
  L5: Reachability          0-15  (professional email +4, LinkedIn active +5)
        |
Tier: HOT (>=80) | STRONG (>=60) | WARM (>=35) | REJECTED (<35)
        |
Deep Enrichment (4 concurrent workers)
  Firecrawl website crawl + CMS detection
  Google PageSpeed Insights (timeout: 45s)
  Hunter.io email finding (25/month) + SMTP fallback
  Proxycurl LinkedIn profile (HOT only)
  Perplexity company news / funding signals
        |
Personalization (Claude claude-sonnet-4-6)
  3 hooks, pain points, value prop, best channel
        |
Export
  Cold Email CRM   (HOT/STRONG/WARM with email)
  LinkedIn CRM     (HOT/STRONG with linkedin_url)
  Instagram CRM    (HOT with instagram_url)
  CSV exports for Instantly/Lemlist
```

---

## Tier Logic

| Tier     | Score | Enrichment          | Personalization | Platforms                         |
|----------|-------|---------------------|-----------------|-----------------------------------|
| HOT      | >=80  | Full + Proxycurl    | Claude          | Cold email + LinkedIn + Instagram |
| STRONG   | >=60  | Full (no Proxycurl) | Claude          | Cold email + LinkedIn             |
| WARM     | >=35  | Website + email     | Template-based  | Cold email only                   |
| REJECTED | <35   | None                | None            | Archived                          |

---

## Environment Variables

Required in `projects/lead-gen/.env`:

```
FIRECRAWL_API_KEY=          # Website intelligence (crawl + CMS detection)
PROXYCURL_API_KEY=          # LinkedIn enrichment ($0.01/call, HOT only)
HUNTER_API_KEY=             # Email finding (25 free/month)
PAGESPEED_API_KEY=          # Google PageSpeed Insights (free)
OPENAI_API_KEY=             # Personalization fallback
```

---

## Setup (first time)

```bash
cd projects/lead-gen
pip install -r requirements.txt
# Create .env with API keys above
# Set input_sheet_id in config.py
python main.py stats  # verifies DB initializes correctly
```

---

## Cost Notes

- **Proxycurl**: ~$0.01/call — HOT leads only.
- **Hunter.io**: 25 free/month. Switches to SMTP fallback automatically after limit.
- **Firecrawl**: Free tier covers typical usage.
- **Claude API**: ~$0.01-0.03 per lead personalization.
- **PageSpeed**: Free (Google API).
