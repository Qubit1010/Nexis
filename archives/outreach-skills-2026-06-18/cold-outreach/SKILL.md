---
name: cold-outreach
description: >
  Runs NexusPoint's automated cold email client acquisition pipeline. Manages
  the full workflow from lead scraping to email sending to reply tracking — all
  free, using Apify (free tier), Gmail (gws), and Google Sheets as CRM.
  Trigger phrases: "scrape leads", "find companies", "build lead list",
  "find emails", "enrich leads", "verify emails", "send emails", "send today's batch",
  "run outreach", "run outreach today", "check replies", "any replies",
  "who replied", "outreach status", "pipeline status", "cold email pipeline",
  "cold outreach", "setup cold email"
argument-hint: [scrape / enrich / send / check / status — or describe what you want to do]
---

# Cold Outreach Pipeline

NexusPoint's fully automated client acquisition system. Free stack: Apify (lead scraping) + Python SMTP (email finding) + Gmail via gws (sending) + Google Sheets (CRM).

## CRM Location

Google Sheets: **NexusPoint Cold Outreach CRM**
Auto-created on first run. Three tabs: Raw Leads, Enriched Leads, Daily Stats.

## Required Setup (One-Time)

Before running any mode, confirm:
1. `APIFY_API_KEY` environment variable is set (free at apify.com → Account → Integrations)
2. `requests` and `dnspython` are installed: `pip install requests dnspython`
3. gws is authenticated as hassanaleem86@gmail.com

If user hasn't done this, walk them through it step by step before running anything.

---

## Mode Detection

Auto-detect from user input:

| Mode | Triggers | Script |
|------|---------|--------|
| **scrape-enriched** | "scrape with emails", "get leads with emails", "multi-actor scrape", "leads finder", "apify leads", "fast scrape" | `scrape_enriched.py` |
| **scrape** | "scrape leads", "find companies", "build lead list" | `scrape_leads.py` |
| **enrich** | "find emails", "enrich leads", "verify emails" | `find_emails.py` |
| **send** | "send emails", "send today's batch", "run outreach", "run outreach today" | `send_sequence.py` |
| **check** | "check replies", "any replies?", "who replied" | `check_replies.py` |
| **status** | "pipeline status", "outreach status", "how many leads" | Read Sheets directly |
| **setup** | "setup", "cold email system", "get started", "first time" | Walk through one-time setup |

If input is ambiguous, ask: "Do you want to scrape new leads, find emails for existing ones, send today's emails, or check for replies?"

---

## Workflow

### Step 1: Parse Mode

Detect mode from trigger keywords. If the user says something like "run the outreach pipeline", default to asking which step they want.

### Step 2: Confirm Before Running

Before running any script, show what will happen:

**Scrape mode:**
> "I'll scrape LinkedIn Jobs using Apify for '[query]', find decision makers, and add new leads to your CRM. This uses ~$0.50-$1 of Apify credits. Go ahead?"

**Enrich mode:**
> "I'll process [N] unprocessed leads from your CRM — guess their email patterns and verify via SMTP. Takes ~2-5 minutes. Go ahead?"

**Send mode:**
> "I'll send today's batch of cold emails (up to 50) from hassanaleem86@gmail.com. This will actually send emails. Go ahead?"

**Check mode:**
> "I'll scan your Gmail inbox for replies from leads in the CRM. Go ahead?"

Do not run scripts without confirmation.

### Step 3: Run the Script

**Scrape with emails (fast path — preferred):**
```bash
python .claude/skills/cold-outreach/scripts/scrape_enriched.py --query "<query>" --limit <N>
```
Runs Leads Finder + Google Maps + Google Search actors. Leads go directly to Enriched Leads as Status="Ready". Each actor also gets its own tab (LF Leads, GMaps Leads, GSearch Leads).

Default query if user doesn't specify: `"operations manager"` targeting SaaS/tech companies.

Optional flags:
- `--actors leads_finder,google_maps,google_search` — run specific actors only
- `--location "United States"` — location filter (default: United States)
- `--test` — dry run, print results without saving

**Scrape (old path — LinkedIn Jobs, no emails):**
```bash
python .claude/skills/cold-outreach/scripts/scrape_leads.py --query "<query>" --limit <N>
```

Default query if user doesn't specify: `"operations manager"` targeting SaaS/tech companies.

**Enrich:**
```bash
python .claude/skills/cold-outreach/scripts/find_emails.py --limit 50
```

**Send:**
```bash
python .claude/skills/cold-outreach/scripts/send_sequence.py --limit 50
```

First time or testing: always add `--test-to hassanaleem86@gmail.com` and confirm the email looks right before real sends.

**Check:**
```bash
python .claude/skills/cold-outreach/scripts/check_replies.py --days 2
```

### Step 4: Display Results

After each script run, show the output cleanly:

**Scrape result:**
```
Scraped: [N] companies
New leads added: [N]
CRM: [link]
Next step: Run "find emails" to enrich these leads.
```

**Enrich result:**
```
Emails found: [N]
No email found: [N]
CRM: [link]
Next step: Run "send emails" to start the sequence.
```

**Send result:**
```
Sent: [N] emails
Skipped: [N] (not yet due)
Errors: [N]
Next step: Run "check replies" tomorrow.
```

**Check result:**
```
Replies: [N]
Companies: [list]
Next step: Respond manually in Gmail. Use labels, mirrors. No "just following up."
```

**Status mode:** Read the CRM Sheets directly and display:
```
Pipeline Status
───────────────────
Total leads scraped:  [N]
Emails found:         [N]
In sequence:          [N]
Replied:              [N]
Calls booked:         [N]
```

### Step 5: Suggest Next Step

Always end with the logical next step in the pipeline:
- After scrape → suggest enrich
- After enrich → suggest send
- After send → suggest check replies tomorrow
- After check replies with results → remind to respond manually, flag leads for follow-up

---

## Pipeline Order

```
scrape → enrich → send → [wait 3-14 days] → check → respond manually
```

The full sequence per lead takes ~14-17 days (4 emails over 14 days). After Email 4, the lead either replied or is done — don't contact again for 3 months.

---

## Safety Rules

- Never send more than 50 emails per day (Gmail deliverability protection)
- Always test with `--test-to hassanaleem86@gmail.com` on first real run
- Never auto-reply to leads — responses must be written by Aleem
- If a lead replies "unsubscribe" or similar, update their status to "Unsubscribed" in Sheets immediately
- Ramp up slowly: Week 1 = 10/day, Week 2 = 25/day, Week 3+ = 50/day

---

## Troubleshooting

| Issue | Solution |
|-------|---------|
| `APIFY_API_KEY not set` | Go to apify.com → Account → Integrations → copy API token |
| `dnspython not installed` | Run: `pip install dnspython` |
| `requests not installed` | Run: `pip install requests` |
| Apify actor fails | Check Apify console for run logs. Try `--skip-profiles` flag |
| gws send fails | Check `gws gmail +send --help` for correct flags |
| Sheets not created | Delete `.sheet_id` cache file in skill folder and rerun |
| All emails "unknown" | Server blocking SMTP probing — mark as "Unverified" and send anyway |

---

## Scripts Reference

| Script | Location | Purpose |
|--------|----------|---------|
| `gws_utils.py` | `scripts/gws_utils.py` | Shared gws + Sheets utilities |
| `scrape_leads.py` | `scripts/scrape_leads.py` | Apify LinkedIn Jobs + Profile scraper |
| `find_emails.py` | `scripts/find_emails.py` | SMTP email finder + verifier |
| `send_sequence.py` | `scripts/send_sequence.py` | Gmail 4-email sequence sender |
| `check_replies.py` | `scripts/check_replies.py` | Gmail inbox reply checker |
