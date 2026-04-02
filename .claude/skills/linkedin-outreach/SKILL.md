---
name: linkedin-outreach
description: >
  LinkedIn lead generation and personalized connection request message system for NexusPoint.
  Scrapes founder, COO, and ops lead profiles from LinkedIn using Apify, stores them in a
  Google Sheets CRM, and generates personalized 300-character connection request messages
  using OpenAI (ChatGPT). Use this skill whenever the user says "scrape linkedin leads",
  "find linkedin prospects", "generate connection messages", "linkedin outreach",
  "run linkedin pipeline", "linkedin leads", "get me prospects on linkedin",
  "personalize my linkedin messages", or wants to find and message potential clients
  on LinkedIn for NexusPoint. Also trigger for "check my linkedin sheet", "how many
  linkedin leads", or "set up linkedin outreach".
---

# LinkedIn Outreach System

NexusPoint's personalized LinkedIn client acquisition pipeline. Scrapes target prospects
(founders, COOs, ops leads at 5-50 person companies), stores them in a Google Sheet CRM,
and generates human-sounding 300-character connection request notes using OpenAI — ready
for Aleem to review and send manually from LinkedIn.

## CRM Location

**Sheet name:** NexusPoint LinkedIn Outreach CRM
**Tab:** Leads
**Columns:** Name | First Name | Company | Role | LinkedIn URL | Location | Recent Post | Connection Message | Status | Date Added

Sheet ID is cached in `.sheet_id` in the skill root directory.

---

## Mode Detection

| What user says | Mode | Script |
|---------------|------|--------|
| "scrape linkedin leads", "find prospects", "get leads", "scrape leads" | **scrape** | `scrape_leads.py` |
| "generate connection messages", "write messages", "personalize messages", "create messages" | **generate** | `generate_messages.py` |
| "run the pipeline", "full pipeline", "run linkedin pipeline", "start pipeline" | **pipeline** | scrape → generate |
| "pipeline status", "show leads", "how many leads", "check sheet" | **status** | read sheet + display stats |
| "setup", "create sheet", "initialize", "first time setup" | **setup** | `setup.py` |

If the intent is unclear, ask: "Do you want to scrape new leads, generate connection messages for existing ones, or run the full pipeline?"

---

## Workflow

### Step 1: Check environment (first run only)

If this is the first time, run setup:
```bash
cd c:\Users\qubit\OneDrive\Documents\Automations\Nexis\.claude\skills\linkedin-outreach
python scripts/setup.py
```

Required env vars:
- `APIFY_API_KEY` — from https://console.apify.com/account/integrations
- `OPENAI_API_KEY` — from https://platform.openai.com/api-keys

### Step 2: Run the appropriate script

All scripts live in `.claude/skills/linkedin-outreach/scripts/`. Always `cd` to the skill root first so `.sheet_id` resolves correctly.

**scrape mode:**
```bash
cd c:\Users\qubit\OneDrive\Documents\Automations\Nexis\.claude\skills\linkedin-outreach
# Default: targets founders/COOs/ops leads in SaaS, Agency, E-commerce
python scripts/scrape_leads.py

# Custom titles and industries:
python scripts/scrape_leads.py --titles "Founder,CEO,COO" --industry "SaaS,Agency"

# Provide a specific LinkedIn search URL (most targeted):
python scripts/scrape_leads.py --search-url "https://www.linkedin.com/search/results/people/?keywords=founder+saas"

# Limit results:
python scripts/scrape_leads.py --limit 30

# Preview without saving:
python scripts/scrape_leads.py --dry-run
```

**generate mode:**
```bash
cd c:\Users\qubit\OneDrive\Documents\Automations\Nexis\.claude\skills\linkedin-outreach
# Preview first (recommended):
python scripts/generate_messages.py --dry-run

# Generate and save to sheet:
python scripts/generate_messages.py

# Regenerate messages that already exist:
python scripts/generate_messages.py --overwrite

# Process only N leads:
python scripts/generate_messages.py --limit 20
```

**pipeline mode** (scrape + generate in sequence):
```bash
cd c:\Users\qubit\OneDrive\Documents\Automations\Nexis\.claude\skills\linkedin-outreach
python scripts/scrape_leads.py --limit 50
python scripts/generate_messages.py
```

**status mode:**
Read the sheet and report:
- Total leads in CRM
- Leads with messages vs. without
- Status breakdown (New / Sent / Connected / Not Interested)
- Sheet link

### Step 3: After running, always show

1. What was done (leads scraped / messages generated / errors)
2. The Google Sheet link: `https://docs.google.com/spreadsheets/d/{sheet_id}`
3. The logical next step

---

## Script Reference

| Script | Purpose |
|--------|---------|
| `setup.py` | Creates the Google Sheet CRM with headers. Run once. |
| `scrape_leads.py` | Scrapes LinkedIn profiles via Apify, deduplicates, writes to sheet |
| `generate_messages.py` | Reads leads, generates 300-char connection notes via OpenAI, writes back |
| `gws_utils.py` | Shared Google Sheets utilities — do not run directly |

---

## First-Time Setup

```bash
# 1. Install dependencies
pip install requests openai

# 2. Set environment variables (add to your shell profile)
# Windows PowerShell:
$env:APIFY_API_KEY = "your_apify_key"
$env:OPENAI_API_KEY = "your_openai_key"

# 3. Create the sheet
cd c:\Users\qubit\OneDrive\Documents\Automations\Nexis\.claude\skills\linkedin-outreach
python scripts/setup.py

# 4. Run first scrape
python scripts/scrape_leads.py --limit 30 --dry-run   # preview first
python scripts/scrape_leads.py --limit 30              # then save

# 5. Generate messages
python scripts/generate_messages.py --dry-run          # preview
python scripts/generate_messages.py                    # save
```

---

## Apify Actor

Default actor: `curious_coder~linkedin-people-search-scraper`

To use a different actor, set the env var:
```
LINKEDIN_SCRAPER_ACTOR=your~actor-name
```

The actor must accept `startUrls` (array of LinkedIn search URLs) and return items with
fields like `fullName`, `headline`, `currentCompany`, `profileUrl`, `location`.

---

## Connection Message Rules

OpenAI generates messages following these constraints (enforced in system prompt):
- **Hard 300-character limit** — LinkedIn rejects longer notes
- Start with `Hey [FirstName],`
- Reference something specific: company name, role, or recent post topic
- No pitch, no ask — only a reason to connect
- Human and natural tone — not a template

**Good examples:**
- `Hey Sarah, saw your post on scaling ops at Growlio. Building something similar in automation. Would love to connect.`
- `Hey James, noticed ShipStack's been growing fast. Your async team breakdown was spot on. Would love to connect.`

---

## Safety Rules

- Aleem sends connection requests manually — this system only generates the messages
- LinkedIn weekly limit: ~100 connection requests for standard accounts (don't exceed)
- Deduplication is enforced by LinkedIn URL — same profile won't be added twice
- If Apify returns 402 (credits exhausted): pause, check dashboard, notify user

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `APIFY_API_KEY not set` | `$env:APIFY_API_KEY = "your_key"` |
| `OPENAI_API_KEY not set` | `$env:OPENAI_API_KEY = "your_key"` |
| Apify 402 error | Credits exhausted — check https://console.apify.com |
| No leads returned | Try broader keywords or a different search URL |
| Messages over 300 chars | Script auto-truncates — check the `--dry-run` output |
| Sheet not found | Run `python scripts/setup.py` to recreate |
| `gws` not found | Install: `npm install -g google-workspace-cli` |
