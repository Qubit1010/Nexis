---
name: instagram-outreach
description: >
  Instagram lead generation and personalized DM system for NexusPoint client acquisition.
  Scrapes founder, CEO, COO, and ops lead profiles from Instagram using Apify hashtag scraping,
  stores them in a Google Sheets CRM, and generates personalized Touch 1 DM messages using
  OpenAI (GPT-4o-mini). Use this skill whenever the user says "scrape instagram leads",
  "find founders on instagram", "generate instagram DMs", "instagram outreach",
  "run instagram pipeline", "get me prospects on instagram", "personalize my instagram messages",
  "find agency owners on instagram", or wants to find and message potential clients on Instagram
  for NexusPoint. Also trigger for "check my instagram sheet", "how many instagram leads",
  "instagram CRM status", or "set up instagram outreach".
---

# Instagram Outreach System

NexusPoint's personalized Instagram client acquisition pipeline. Scrapes target founders and
operators via hashtag search, stores them in a Google Sheet CRM, and generates human-sounding
opening DMs using OpenAI — ready for Aleem to review and send manually from Instagram.

**Important:** Never automate the actual DM sending. Instagram bans bot activity.
This system only generates messages and tracks status. All sending is manual.

## CRM Location

**Sheet name:** NexusPoint Instagram Outreach CRM
**Tab:** Leads
**Columns:** Name | Username | Company | Role | Instagram URL | Followers | Bio | Touch 1 Message | Status | Date Added

Sheet ID is cached in `.sheet_id` in the skill root directory.

---

## Mode Detection

| What user says | Mode | Script |
|---------------|------|--------|
| "scrape instagram leads", "find prospects on instagram", "get leads" | **scrape** | `scrape_leads.py` |
| "generate instagram DMs", "write DM messages", "personalize messages" | **generate** | `generate_messages.py` |
| "run the instagram pipeline", "full pipeline", "scrape and generate" | **pipeline** | scrape → generate |
| "instagram status", "how many leads", "check instagram sheet" | **status** | read sheet + display stats |

If intent is unclear, ask: "Do you want to scrape new leads, generate DMs for existing ones, or run the full pipeline?"

---

## Workflow

### Step 1: Check environment (first run only)

Required env vars:
- `APIFY_API_KEY` — from https://console.apify.com/account/integrations
- `OPENAI_API_KEY` — from https://platform.openai.com/api-keys

```powershell
# Windows PowerShell:
$env:APIFY_API_KEY = "your_apify_key"
$env:OPENAI_API_KEY = "your_openai_key"
```

### Step 2: Run the appropriate script

All scripts live in `.claude/skills/instagram-outreach/scripts/`. Always `cd` to the skill root first so `.sheet_id` resolves correctly.

**scrape mode:**
```bash
cd c:\Users\qubit\OneDrive\Documents\Automations\Nexis\.claude\skills\instagram-outreach

# Default: searches #saasfounder #startupfounder #agencyowner etc.
python scripts/scrape_leads.py

# Custom hashtags:
python scripts/scrape_leads.py --hashtags "saasfounder,b2bsaas,agencyowner"

# Limit results:
python scripts/scrape_leads.py --limit 30

# Preview without saving:
python scripts/scrape_leads.py --dry-run
```

**generate mode:**
```bash
cd c:\Users\qubit\OneDrive\Documents\Automations\Nexis\.claude\skills\instagram-outreach

# Preview first (always recommended):
python scripts/generate_messages.py --dry-run

# Generate and save to sheet:
python scripts/generate_messages.py

# Regenerate existing messages:
python scripts/generate_messages.py --overwrite

# Process only N leads:
python scripts/generate_messages.py --limit 20
```

**pipeline mode** (scrape + generate in sequence):
```bash
cd c:\Users\qubit\OneDrive\Documents\Automations\Nexis\.claude\skills\instagram-outreach
python scripts/scrape_leads.py --limit 50
python scripts/generate_messages.py
```

**status mode:**
Read the sheet and report:
- Total leads in CRM
- Leads with messages vs. without
- Status breakdown
- Sheet link

### Step 3: After running, always show

1. What was done (leads scraped / messages generated / errors)
2. The Google Sheet link: `https://docs.google.com/spreadsheets/d/{sheet_id}`
3. The logical next step

---

## Script Reference

| Script | Purpose |
|--------|---------|
| `scrape_leads.py` | Scrapes Instagram profiles via Apify hashtag search, filters ICP, deduplicates, writes to sheet |
| `generate_messages.py` | Reads leads, generates Touch 1 DMs via OpenAI, writes back to sheet |
| `gws_utils.py` | Shared Google Sheets utilities — do not run directly |

---

## ICP Filter (built into scrape_leads.py)

Leads must pass both checks before entering the CRM:
- **Follower range:** 100 to 100,000 (filters out ghost accounts and major influencers)
- **Bio signal:** bio must contain at least one of: founder, co-founder, ceo, coo, owner, operator, building, scaling, startup, saas, agency, e-commerce, entrepreneur, bootstrapped, b2b

Default hashtags searched: `#saasfounder`, `#startupfounder`, `#agencyowner`, `#ecommercefounder`, `#startupCEO`, `#techfounder`, `#b2bsaas`

---

## 4-Touch DM Sequence

Aleem sends all messages manually. This system generates Touch 1 only. Touches 2-4 are drafted based on their response (or lack of one).

| Touch | Timing | Goal | Mention NexusPoint? | CTA? |
|-------|--------|------|---------------------|------|
| 1 — Opening DM | Day 0 | Start a real conversation | No | Genuine question only |
| 2 — Value Drop | Day 3-4 (no reply) | Build trust | No | No — "no reply needed" |
| 3 — Soft CTA | Day 8-10 (no reply) | Book a call | Yes, briefly | No-oriented question |
| 4 — Breakup | Day 15 (no reply) | Close loop, leave door open | Light reference | No |

### Touch 1 Template (generated by OpenAI)
Observation + Voss label ("It looks like...", "It sounds like...") + one genuine question.
No pitch. No NexusPoint. Human and casual.

**Example:**
> Hey [Name] - it looks like you're betting heavily on the productized service model. The way you've packaged your offer is different from most agency owners I've seen. Curious - what made you move away from custom scoping?

### Touch 2 Template (manual — send if no reply by Day 3-4)
> Hey [Name] - not looking for a reply, just thought this was relevant to what you're building.
>
> [Specific insight, case study, or tool recommendation — 2-3 sentences]. Thought it might be useful given where [Company] is heading.
>
> No response needed — just passing it along.

### Touch 3 Template (manual — send if no reply by Day 8-10)
> Hey [Name] - I've been a bit roundabout so I'll be straight.
>
> I run NexusPoint. We help [their type of company] automate the ops work slowing their team down - things like [specific to their context]. Based on what you're building, it seemed like that might be on your radar.
>
> Would it be completely off base to do a quick 20-min call and see if there's a fit?

### Touch 4 Template (manual — send if no reply by Day 15)
> Hey [Name] - will stop reaching out, no hard feelings.
>
> If automating [their specific pain] ever becomes a priority, I'm easy to find. Either way - what you're building at [Company] is genuinely interesting. Rooting for it.

---

## CRM Status Values

| Status | Meaning |
|--------|---------|
| New | Lead scraped — Touch 1 not yet sent |
| DM Sent T1 | Touch 1 sent — waiting for reply |
| DM Sent T2 | Value drop sent |
| DM Sent T3 | CTA sent |
| DM Sent T4 | Breakup sent — sequence complete |
| Replied | Responded to any message — manual follow-up |
| Interested | Expressed interest in a call or more info |
| Booked | Call scheduled |
| Closed | Became a client |

---

## Safety Rules

- Aleem sends all DMs manually — never automate Instagram sending
- Instagram daily DM limit: ~50 DMs/day to new accounts (conservative — stay under 30/day)
- Deduplication enforced by Instagram URL — same profile won't be added twice
- Review Touch 1 messages before sending — OpenAI output should feel real and specific, not generic

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `APIFY_API_KEY not set` | `$env:APIFY_API_KEY = "your_key"` |
| `OPENAI_API_KEY not set` | `$env:OPENAI_API_KEY = "your_key"` |
| Apify 402 error | Credits exhausted — check https://console.apify.com |
| No leads returned | Try different hashtags or check if actor is running correctly |
| 0 leads after ICP filter | Relax follower range or add more hashtags |
| Sheet not found | Delete `.sheet_id` file and re-run — will create a new sheet |
| `gws` not found | Install: `npm install -g google-workspace-cli` |
