# Cold Email & Lead Generation Session — 2026-03-30

Full session notes covering client acquisition strategy, cold email sequences, Apify lead building, and the n8n automation pipeline blueprint.

---

## Channel Strategy: Core Four in Order

Work through channels in sequence. Never add a new channel until the current one is maxed.

| Stage | Channel | Status | Action |
|-------|---------|--------|--------|
| 1 | Cold Outreach | Building | 100 emails/day — primary focus now |
| 2 | LinkedIn | Not active | Start parallel — 1 post/day, 20-30 connections/day |
| 3 | Content | Not active | After 5-10 clients from cold channels |
| 4 | Paid Ads | Not yet | Only after cold email is converting and CAC is known |

**Volume target (Rule of 100):** 100 cold emails/day. At standard benchmarks:
- 50% open rate = 50 opens
- 5% reply rate = 5 replies/day
- 20% meeting rate = 1 call/day
- 25% close rate = 1-2 new clients/week

Don't touch Paid Ads until cold email system is converting and you know your CAC. Running ads before that is burning cash to find information cold outreach gives you for free.

---

## Lead List Building

### ICP Targeting Criteria

- Company size: 5-50 employees
- Revenue: $500K-$10M (funded startups, profitable SMBs)
- Industry: SaaS, e-commerce, tech-enabled services
- Decision maker: Founder, CEO, COO, Head of Operations
- Signals: hiring ops/admin roles, recently funded, manual-heavy tech stack

### Who NOT to Target

- Solopreneurs with <$1K budgets
- Enterprise with 6-month procurement
- Anyone wanting "just a cheap website"

### Lead Building Tools

| Tool | Role | Cost | Output |
|------|------|------|--------|
| Apollo.io | B2B database — search by title, industry, company size | Free (50 exports/day) | 300+ leads in a week |
| LinkedIn Sales Navigator | Most accurate B2B data, active users filter | Free 30-day trial | 500-1,000 leads in trial |
| Apify | Automated scraping — LinkedIn jobs, profiles, emails | $5-$49/month | 500-10,000 leads/month |
| Hunter.io | Email finding from company domains | Free 25/month / $49 for 500 | Email + confidence score |
| NeverBounce / ZeroBounce | Email verification before sending | $0.003-0.004/email | Valid/invalid classification |
| BuiltWith / Wappalyzer | Tech stack enrichment | Free browser extension | Shows what software they use |

### Targeting Priority Order

1. **Highest:** Companies with a specific pain signal (job posting, LinkedIn complaint, obvious manual process on website)
2. **Second:** Recently funded (money to spend, scaling fast)
3. **Third:** ICP match but no specific signal (pure demographic)

The first group gets fully personalized Email 1s. The third group gets semi-templated.

---

## Apify Lead Building

### What Apify Does

Apify is a scraping platform with pre-built Actors (scrapers) you run without writing code.

| Actor | What it scrapes | Best for |
|-------|----------------|----------|
| LinkedIn Scraper | Profiles, job titles, companies | Finding decision makers |
| LinkedIn Jobs Scraper | Job postings with company info | Pain signal targeting |
| Website Contact Scraper | Emails from any website | Enriching company domains |

**Cost:** Free tier = $5/month credits (~500-1,000 leads/month). Starter = $49/month (~5,000-10,000 leads/month).

### Manual Scraping Sources

| Source | What it tells you |
|--------|------------------|
| Job postings (Indeed, LinkedIn Jobs) | What they're manually doing — bottleneck = your pitch |
| Product Hunt launches | New SaaS companies, founder email often public |
| Crunchbase | Recently funded startups with money to spend |
| G2 / Capterra reviews | Companies using tools you can automate around |

**Key insight:** A company posting a "Data Entry Specialist" job is advertising their bottleneck. Pitch: "It seems like your team is still handling [X] manually — I mapped out how to automate that for a similar company last month."

### Apify First Week Schedule

| Day | Actor | Target | Expected Output |
|-----|-------|--------|----------------|
| Day 1 | LinkedIn Jobs Scraper | "operations manager" + SaaS 11-50 employees | 100-200 companies |
| Day 2 | LinkedIn Profile Scraper | Founders at those companies | 100-200 profiles |
| Day 3 | Website Email Scraper | Domains from Day 2 | 80-150 emails |
| Day 4 | NeverBounce | Full list verification | Clean verified list |
| Day 5 | Manual enrichment | Top 50 leads — add pain signal note | Ready-to-send 50 leads |

### Email Verification Rules

Run all emails through NeverBounce or ZeroBounce before sending. Keep only "valid" results. Target <3% bounce rate to protect domain deliverability.

---

## The 4-Email Cold Outreach Sequence

### Pre-Send Setup Checklist

- Register a new outreach domain (e.g., nexuspointai.com) — never cold email from your main domain
- Configure SPF, DKIM, and DMARC on the outreach domain
- Warm up the domain for 2-3 weeks using Instantly or Lemlist built-in warmup
- Cap at 50 emails/day per mailbox — use 2-3 mailboxes to hit 100-150/day total
- Tool: Instantly.ai or Lemlist for sequence management

---

### Email 1 — Initial Outreach (Day 1)

**Subject:** `quick question about [COMPANY]'s workflows`

```
Hey [FIRST_NAME],

I know you probably get a lot of emails like this — I'll keep it short.

It seems like [COMPANY] is scaling fast, and that usually means a few
operational bottlenecks start eating your team's time.

I run NexusPoint, an AI automation agency. I'm doing free custom workflow
teardowns this week for a handful of [INDUSTRY] founders — I map out
exactly how to automate your biggest bottleneck using tools like n8n and
AI, recorded as a 5-minute Loom video.

No pitch. Just the blueprint. You can hand it to your devs or build it yourself.

Would it be a bad idea if I sent over a quick 3-question link so I know
which bottleneck to look at for [COMPANY]?

Aleem
NexusPoint
```

**Why it works:**
- Accusation audit in opener ("I know you probably get a lot of emails like this")
- Label in second paragraph ("It seems like [COMPANY] is scaling fast")
- CTA is a no-oriented micro-commitment ("Would it be a bad idea if...")
- "No pitch. Just the blueprint." lowers guard completely

---

### Email 2 — Social Proof Follow-up (Day 3-4, new thread)

**Subject:** `re: quick question about [COMPANY]'s workflows`

```
Hey [FIRST_NAME],

Wanted to share a quick example. Last month I mapped out an automation for
a [SIMILAR_INDUSTRY] company that was spending [X] hours/week manually
[SPECIFIC_TASK]. The teardown showed them how to cut it to near-zero with
a simple n8n workflow.

Still happy to do the same for [COMPANY] if you're open to it.

Worth a look?

Aleem
```

---

### Email 3 — Value-First Observation (Day 7-8, new thread)

**Subject:** `noticed something on [COMPANY]'s site`

```
Hey [FIRST_NAME],

I took a quick look at [COMPANY] and noticed [SPECIFIC_OBSERVATION —
e.g., "your lead intake form doesn't connect to your CRM automatically"
or "your onboarding flow has a few manual handoffs that could be cut"].

Not pitching anything. Just figured it was worth flagging since it's
probably costing your team a few hours a week.

If you want, I can record a quick Loom showing the fix. Takes me 5 minutes.

Aleem
```

---

### Email 4 — Breakup (Day 14, new thread)

**Subject:** `should I close your file?`

```
Hey [FIRST_NAME],

It sounds like the timing isn't right or this isn't a priority for
[COMPANY] right now.

No hard feelings. If you ever want a fresh set of eyes on your workflows,
the offer stands.

Should I close your file, or is this worth revisiting down the line?

Aleem
```

**Why it works:** "Should I close your file?" triggers loss aversion (Voss). Almost always gets a reply — either a "yes go ahead" (clean close) or a "wait actually..." (re-engage).

---

## The Lead Magnet: 100-Hour Reclaim Audit

A free custom Loom video showing exactly how to automate their biggest bottleneck.

**Process:**
1. Prospect fills a 3-question form (biggest bottleneck, current tools, email)
2. Record a 5-minute Loom: map their current messy process, then show the automated architecture
3. Give away the strategy completely for free
4. Close the video with: "You can hand this to your devs to build, or if you want it done right the first time, NexusPoint can have it built, tested, and deployed by [DATE]."

**The model:** Strategy is free. Implementation is the paid product. This turns free intellectual capital into high-ticket clients.

---

## n8n Automation Blueprint: Full Pipeline

### Overview

```
[SCHEDULE TRIGGER]
       ↓
  Apify Scrape (Jobs + Profiles)
       ↓
  Google Sheets (Raw Lead Store)
       ↓
  Email Finding (Hunter.io API)
       ↓
  Email Verification (NeverBounce API)
       ↓
  Instantly.ai (Sequence Enrollment)
       ↓
  Notify via Gmail
```

### Tools Required

| Tool | Role | Cost |
|------|------|------|
| n8n | Workflow orchestration | Free self-hosted / $20/month cloud |
| Apify | Web scraping | $5-$49/month |
| Hunter.io | Email finding | Free 25/month / $49 for 500 |
| NeverBounce | Email verification | $0.003/email |
| Google Sheets | Lead database | Free |
| Instantly.ai | Outreach sequences | $37/month |
| Gmail | Notifications | Free |

---

### Workflow 1: Lead Scraping (7:00 AM PKT Daily)

**Trigger:** n8n Schedule node — 7:00 AM PKT

1. **HTTP Request** — call Apify API to start LinkedIn Jobs Scraper
   - Search: ops/admin roles at 11-50 employee SaaS companies
   - `POST https://api.apify.com/v2/acts/[actor-id]/runs`
2. **Wait node** — pause 5 minutes for Apify run to complete
3. **HTTP Request** — fetch results from Apify run
   - Returns: company name, job title, description, LinkedIn URL
4. **Code node (JS)** — extract pain signal from job description
   - Scan for keywords: manual, data entry, spreadsheet, tracking, reporting
   - Output: `pain_signal` field (1-sentence summary)
5. **Google Sheets** — append rows to Raw Leads tab, Status = "Unprocessed"

**Exit condition:** If Apify fails or returns 0 results, send notification email and stop.

---

### Workflow 2: Lead Enrichment (7:30 AM PKT Daily)

**Trigger:** Schedule node — 7:30 AM PKT

1. **Google Sheets** — read all rows where Status = "Unprocessed"
2. **HTTP Request** — call Apify LinkedIn Profile Scraper per company (50 max per run)
   - Returns: founder/CEO name, LinkedIn profile URL, title
3. **HTTP Request** — call Hunter.io Domain Search API
   - `GET https://api.hunter.io/v2/domain-search?domain=[domain]&api_key=[key]`
   - Returns: email addresses, confidence score
4. **IF node** — if no email found → mark Status = "No Email Found", skip
5. **HTTP Request** — call NeverBounce to verify email
   - `GET https://api.neverbounce.com/v4/single/check?email=[email]&api_key=[key]`
   - Returns: valid / invalid / catchall / unknown
6. **IF node** — if valid → continue; if not → mark Status = "Bad Email"
7. **Google Sheets** — update row: name, title, email, Verified = Y, Status = "Ready"

**Exit condition:** If Hunter.io API limit hit, pause and send notification.

---

### Workflow 3: Sequence Enrollment (8:00 AM PKT Daily)

**Trigger:** Schedule node — 8:00 AM PKT

1. **Google Sheets** — read all rows where Status = "Ready" and Enrolled = blank
2. **Limit node** — cap at 50 leads per day
3. **HTTP Request** — call Instantly.ai API to add lead to campaign
   - `POST https://api.instantly.ai/api/v1/lead/add`
   - Custom variables: `{{first_name}}`, `{{company}}`, `{{pain_signal}}`
4. **Google Sheets** — mark Enrolled = Y, Enrolled Date = today, Status = "In Sequence"
5. **Gmail node** — send daily summary to Aleem (scraped / verified / enrolled / failed counts)

**Exit condition:** If Instantly API error, log to Errors tab and skip that lead. Do not stop the full run.

---

### Workflow 4: Reply Handling

Instantly handles sending and reply detection. Route replies manually.

1. Instantly detects reply → marks lead "Replied" in campaign dashboard
2. Optional: Instantly webhook → n8n → Gmail forward to Aleem with context (company, pain signal, email number)
3. **Aleem responds manually** — do not automate replies. Tactical empathy requires a human.
4. Update Google Sheets manually: "Call Booked" / "Not Interested" / "Follow-Up"

---

### Google Sheets Structure

| Tab | Columns |
|-----|---------|
| Raw Leads | Company, LinkedIn URL, Job Posted, Pain Signal, Industry, Date Added, Status |
| Enriched Leads | First Name, Last Name, Title, Company, Email, Verified, LinkedIn URL, Pain Signal, Enrolled, Enrolled Date, Sequence Status |
| Errors | Date, Lead, Error Type, Notes |
| Daily Stats | Date, Scraped, Verified, Enrolled, Replies, Calls Booked |

---

### Build Order: Minimum Viable Start

Don't build all 4 workflows at once. Build progressively so you're sending emails by Week 1.

| Week | Build | Manual Tasks |
|------|-------|-------------|
| Week 1 | Workflow 1 only (Apify to Sheets) | Manual enrichment + Instantly enrollment |
| Week 2 | Add Workflow 2 (Hunter.io + NeverBounce) | Manual Instantly enrollment |
| Week 3 | Add Workflow 3 (auto-enrollment) | Monitor and adjust |
| Week 4 | Add Workflow 4 (reply notifications) | Fully automated pipeline running |

---

## How Claude Code Skills Work

Skills live in `.claude/skills/`. Each skill = a folder with a `SKILL.md` file. Claude reads the SKILL.md and follows the instructions inside it.

```
.claude/skills/your-skill/
├── SKILL.md          ← required (YAML frontmatter + instructions)
├── references/       ← optional: framework files, playbooks
└── scripts/          ← optional: Python/JS scripts
```

### SKILL.md Frontmatter

```yaml
---
name: skill-name
description: >
  What this skill does and when to trigger it.
  Include trigger phrases here.
argument-hint: [what the user passes]
---
```

The `description` field is most important — Claude reads it to decide whether to auto-trigger the skill.

### Two Trigger Methods

1. **Explicit:** `/skill-name`
2. **Automatic:** Claude pattern-matches your request against skill descriptions

### Build a Skill When

You find yourself giving Claude the same setup instructions 3+ times before asking for X. That setup = a skill.

### Fast Path

Use `/skill-creator` — it guides design decisions, builds SKILL.md, and registers it in CLAUDE.md.
