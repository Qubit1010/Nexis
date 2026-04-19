# Lead Gen Pipeline: How NexusPoint Built an Automated Prospect Intelligence System

**Category:** Internal AI System / Client Acquisition  
**Built by:** NexusPoint  
**Powered by:** Python, OpenAI gpt-4o-mini, Firecrawl, Proxycurl, Hunter.io, Google Workspace

---

## The Problem

Most agencies and businesses treat lead generation the same way: buy a list, export from Apollo, paste into a spreadsheet, and start sending. The problem is that everyone on the list gets the same email. Same subject line. Same body copy. Same pitch. Response rates crater because nothing feels relevant.

There are four specific problems with that approach:

1. **No qualification.** A list of 500 contacts means nothing if 400 of them are the wrong size, wrong industry, wrong role, or simply unreachable. You spend the same effort on bad leads as good ones.
2. **No enrichment.** You know their name and company. You don't know if their website is broken, if they just raised funding, if they're running on Wix, or if they're actively hiring for the ops role they're struggling to fill.
3. **No personalization.** "I noticed your company does X and I thought..." is not personalization. Personalization is referencing their specific CMS, their PageSpeed score, their recent LinkedIn post, their funding announcement.
4. **No system.** Leads sit in a spreadsheet. Nothing is scored, nothing is tracked, nothing feeds automatically into the right outreach channel.

NexusPoint built the Lead Gen Pipeline to replace all of that.

---

## What It Is

The Lead Gen Pipeline is a Python-based command-line system that takes a raw list of prospects and runs them through five sequential stages: import, score, enrich, personalize, and export.

By the end of the pipeline, every qualified lead has:
- A score from 0-100 across five qualification layers
- A tier assignment (HOT / STRONG / WARM / REJECTED)
- A verified email address
- Website intelligence (CMS, performance score, tech stack, SSL status)
- Company news and funding signals
- LinkedIn profile data (for HOT leads)
- Three personalized outreach hooks
- Identified pain points with evidence and proposed solutions
- A recommended outreach channel and reasoning
- Full multi-touch sequences for cold email, LinkedIn, and Instagram — ready to send

One pipeline. One command. Everything needed to start outreach.

---

## Stage 1: Import

Leads enter the pipeline from three sources:

- **Google Sheets** — the primary source. Aleem manually curates a list (LinkedIn searches, referrals, research) and marks rows "Include = Yes." The importer reads the sheet and normalizes any column naming variation.
- **Apollo.io CSV** — bulk exports from Apollo's free tier (50 exports/month). Apollo leads arrive partially pre-qualified: email already verified, company size and industry populated, tech stack listed.
- **HarvestAPI JSON** — pre-downloaded LinkedIn profile datasets for targeted searches.

Before any lead enters the database, a deduplication pass runs across all sources. It matches on LinkedIn URL first (exact), then on normalized company name + first name (strips legal suffixes like "Inc", "LLC", "Ltd" before comparing). Duplicate leads from multiple sources are merged, not doubled.

Each lead gets a unique ID (format: `LG-YYYYMMDD-XXXX`) and a source tag so pipeline performance can be tracked back to where the lead came from.

---

## Stage 2: The 5-Layer ICP Scoring System

Every lead gets scored against five qualification layers. No API calls. No cost. Pure data logic on what's already in the database.

**Total score: 0-100 points across 5 layers.**

### Layer 1 — Contact Quality (0-20 points)
*Can we actually reach this person?*

- +8 for a verified email
- +6 for a LinkedIn URL
- +3 for an Instagram or Twitter presence
- -5 penalty for generic emails (info@, contact@, hello@, admin@, support@)

A lead with no verified email and no LinkedIn scores near zero here — they're effectively unreachable regardless of how good the company is.

### Layer 2 — Company Quality (0-20 points)
*Is this a real business in the right category?*

- +5 for having a real company website (not a Linktree, not a social profile)
- -10 penalty for no website at all
- +5 for sweet-spot company size (1-50 employees)
- +4 for matching target industries (SaaS, e-commerce, digital agencies, startups, consulting)

Companies over 500 employees are automatically disqualified. So are government, non-profit, and education sectors.

### Layer 3 — Intent & Pain Signal (0-25 points)
*Is there visible evidence they need what NexusPoint sells?*

This is the highest-weighted layer because it's the most predictive of response.

Pre-enrichment signals:
- +8 for a job posting with manual-ops keywords (data entry, spreadsheet, admin, copy-paste, repetitive)
- +8 for running on a tech-debt platform (Wix, Squarespace, Weebly, GoDaddy site builder)
- +6 for a funding signal
- +5 for a Product Hunt launch

Post-enrichment signals (added after website crawl):
- +8 if the website CMS is Wix, Squarespace, or another platform they've outgrown
- +4 if mobile PageSpeed score is below 60
- +3 for detected SSL or site issues
- +6 if Perplexity finds a recent funding round

The design is intentional: most leads arrive with pre-enrichment scores in the 30-45 range. The WARM threshold is set at 35 so real prospects pass through to enrichment, where website and news signals push them up into STRONG or HOT.

### Layer 4 — Decision Maker Access (0-20 points)
*Are we talking to the person who signs off?*

- +20 for founder, co-founder, or owner
- +16 for C-suite (CEO, CTO, COO)
- +12 for head of / director / VP
- +6 for manager or lead
- +0 for ICs, interns, assistants, coordinators

A perfect company means nothing if the contact is an intern.

### Layer 5 — Reachability (0-15 points)
*How likely are they to actually respond?*

- +5 for recent LinkedIn activity (posted in last 30 days)
- +4 for a professional email domain (not Gmail, Yahoo, Hotmail)
- +3 for being a 2nd-degree LinkedIn connection
- +3 for active Instagram or Twitter presence

**Tier Assignment:**

| Score | Tier | Action |
|-------|------|--------|
| 80-100 | HOT | All 3 channels + full Proxycurl enrichment |
| 60-79 | STRONG | Cold email + LinkedIn |
| 35-59 | WARM | Cold email only |
| 0-34 | REJECTED | Archived, no outreach |

---

## Stage 3: Enrichment

Enrichment runs on WARM, STRONG, and HOT leads in parallel (4 concurrent workers). Each enricher adds data that feeds back into the Layer 3 rescore — and into personalization.

### Website Intelligence
Firecrawl crawls the company website. The system detects:
- **CMS and tech stack**: Wix, Squarespace, WordPress, Webflow, Shopify, Framer, React, Next.js, Vue, Angular — identified by signature strings in the HTML
- **Analytics tools**: Google Analytics, GTM, Facebook Pixel, Hotjar, Segment, Intercom, HubSpot
- **Performance**: Google PageSpeed Insights pulls mobile + desktop scores and Core Web Vitals (LCP, CLS, FID)
- **Site health**: SSL certificate status, last updated year from copyright

A founder running a $2M ARR SaaS on a 42/100 mobile PageSpeed score with no SSL is a high-signal prospect. The system surfaces that automatically.

### Email Finding
Two-step process:

1. **Hunter.io** for HOT leads (25 free/month). Returns email with confidence percentage. ≥70% = verified, <70% = unverified.
2. **SMTP pattern guessing + MX verification** as a free fallback for everyone else. The system generates candidate patterns (firstname@domain, first.last@domain, etc.), checks DNS MX records, tests for catch-all domains, and verifies deliverability directly. Free. Unlimited.

### LinkedIn Enrichment (HOT leads only)
Proxycurl pulls the full LinkedIn profile: work history, follower count, headline, location, 2nd-degree connection distance, and the last 3 posts with engagement counts (likes, comments). Cost: ~$0.01 per lead, only for HOT tier.

The recent posts are used directly in personalization — a founder who posted last week about struggling with manual reporting is a warmer lead than one who hasn't posted in three months.

### Company News Intelligence
OpenAI gpt-4o-mini-search-preview runs a live web search: "What are the most recent news, funding rounds, or product launches for {company}?" Returns funding amounts, dates, and growth signals. Near-zero cost. Used in hook generation.

---

## Stage 4: Personalization

After enrichment, every HOT and STRONG lead gets a personalization pass using OpenAI gpt-4o-mini.

The model receives the full enriched profile — CMS, PageSpeed score, company news, recent LinkedIn posts, pain signal, funding status, industry, company size — and NexusPoint's services and positioning context.

It returns a structured JSON object for each lead:

**3 personalized hooks:**
- Hook 1: Based on website tech/performance ("Noticed {company} is running on Squarespace with a 38 mobile score...")
- Hook 2: Based on pain signal ("Saw you're hiring an operations admin — curious what the manual workflow looks like...")
- Hook 3: Based on funding or news ("Congrats on the Series A — curious what the biggest operational constraint is post-raise...")

Empty if there's no evidence for that hook type. No hallucinated signals.

**Pain points (2-3):**
Each one includes: the specific pain, the evidence that revealed it, and how NexusPoint addresses it. Not generic. Not invented.

**Value proposition:**
One sentence connecting NexusPoint's capabilities to this specific company's situation.

**Best channel + reasoning:**
The system recommends cold email, LinkedIn, or Instagram based on the lead's profile — and explains why. A founder who posts daily on LinkedIn gets a LinkedIn-first approach. One who's Instagram-active with 12K followers gets Instagram-first.

---

## Stage 5: Sequence Generation + Export

### Multi-Touch Outreach Sequences

For each lead, the system generates complete, send-ready sequences for every applicable channel.

**Cold Email — 4-touch sequence:**
- Day 0: Hook + pain signal + low-friction CTA ("worth a 15-min call?")
- Day 4: Value add, no pitch ("not looking for anything — just thought this was relevant")
- Day 9: Loom offer ("happy to do a 5-minute walkthrough, no strings attached")
- Day 16: Breakup email ("should I close your file, or is timing just off?")

**LinkedIn — connection note + 4-DM sequence:**
- Connection note: ≤300 characters (hard LinkedIn limit), personalized to recent post or pain signal
- DM 1 (after acceptance): Warm opener, genuine question, zero pitch
- DM 2 (Day 4): Value add referencing specific pain point
- DM 3 (Day 9): Bridge to services
- DM 4 (Day 16): Direct ask ("would it make sense to hop on a 20-min call?")

**Instagram — pre-engagement plan + 4-DM sequence:**
- Days 1-3: Follow → Like 3 posts → Comment on best post → Reply to story
- DM 1 (Day 4): Cold reading opener, casual tone, no pitch
- DM 2 (Day 7): Value add ("not looking for a reply, just thought this was relevant")
- DM 3 (Day 12): Soft transition to services
- DM 4 (Day 18): Final touch, no pressure

### Export to CRM

Three separate Google Sheets CRMs — cold email, LinkedIn, Instagram — receive their relevant leads automatically. Exports are idempotent: the system tracks what's been exported and never duplicates a row.

CSV exports in Instantly / Lemlist / Waalaxy / Dripify format are generated on demand. Every CSV includes the full email sequence bodies and LinkedIn DM text as merge-ready columns — drop it into the sending tool and go.

---

## What's Built and Working

| Capability | Status |
|-----------|--------|
| Google Sheets import (manual curation) | Live |
| Apollo.io CSV import | Live |
| HarvestAPI JSON import | Live |
| Cross-source deduplication | Live |
| 5-layer ICP scoring (100-point system) | Live |
| Tier assignment (HOT / STRONG / WARM / REJECTED) | Live |
| Firecrawl website crawl + CMS detection | Live |
| Google PageSpeed Insights scoring | Live |
| Hunter.io email finding + SMTP fallback | Live |
| Proxycurl LinkedIn enrichment (HOT only) | Live |
| OpenAI company news research | Live |
| AI-powered personalization (3 hooks, pain points, value prop) | Live |
| Best channel recommendation | Live |
| Cold email 4-touch sequence generation | Live |
| LinkedIn connection note + 4-DM sequence | Live |
| Instagram pre-engagement plan + 4-DM sequence | Live |
| Google Sheets CRM export (3 platforms) | Live |
| CSV export (Instantly / Lemlist / Waalaxy format) | Live |
| Pipeline stats + lead profile viewer | Live |
| Rate limiting + retry logic | Live |

---

## Cost Per Lead

| Tier | Email Finding | Website | LinkedIn | News + Personalization | Total |
|------|--------------|---------|----------|----------------------|-------|
| HOT | ~$0.50 (Hunter) | Free | ~$0.01 (Proxycurl) | ~$0.03 (OpenAI) | ~$0.54 |
| STRONG | ~$0.50 (Hunter) | Free | None | ~$0.03 (OpenAI) | ~$0.53 |
| WARM | Free (SMTP) | Free | None | None | ~$0.00 |
| REJECTED | None | None | None | None | Free |

If Hunter.io's 25 free monthly calls are exhausted, SMTP verification takes over at zero cost. At scale, the effective cost per enriched, personalized HOT lead is under $0.60.

---

## The Architecture

**Language:** Python (fully CLI-driven, no UI dependency)  
**Database:** SQLite (7 tables: leads, scores, enrichment, personalization, outreach_sequences, exports, app_config)  
**External APIs:** Firecrawl, Proxycurl, Hunter.io, Google PageSpeed Insights, OpenAI  
**CRM Integration:** Google Workspace CLI (gws) for Sheets read/write  
**Concurrency:** 4 parallel enrichment workers  
**Cost controls:** Hunter.io monthly usage tracked in DB; Proxycurl limited to HOT tier; SMTP fallback for email  

**Pipeline commands:**
```
import   → Load leads from Sheets / Apollo / JSON
score    → 5-layer ICP scoring + tier assignment
enrich   → Website + email + LinkedIn + news (by tier)
personalize → AI hooks, pain points, value prop, channel
export   → Google Sheets CRM + CSV
stats    → Pipeline overview
run      → Full pipeline in one command
```

---

## End-to-End Walkthrough

Here's what the pipeline looks like on a real batch:

1. Aleem curates a Google Sheet with 80 prospects found from LinkedIn searches, filtered to founders at 10-50 person SaaS companies in the US and UK. Marks 60 rows "Include = Yes."

2. `python main.py import --source sheets` — 60 leads enter the DB. Dedup removes 4 duplicates from a prior import. 56 net new leads.

3. `python main.py score` — 5-layer scoring runs in seconds. Results: 8 HOT, 14 STRONG, 21 WARM, 13 REJECTED. The 13 rejected are large enterprises or non-decision-makers.

4. `python main.py enrich` — Runs on HOT and STRONG (22 leads). 4 concurrent workers pull Firecrawl, Hunter.io, Proxycurl (HOT only), and OpenAI in parallel. Takes ~4 minutes. 6 HOT leads have Wix or Squarespace sites. 3 have mobile PageSpeed under 50. 2 have recent funding news. Scores are updated — 3 STRONG leads push to HOT after enrichment.

5. `python main.py personalize` — 11 HOT leads get AI-generated hooks, pain points, and value props. Each one references actual signals: the specific CMS, the actual PageSpeed number, the actual funding amount.

6. `python main.py export --platform all --format both` — 11 HOT leads go to all 3 CRM sheets and 3 CSVs. 14 STRONG leads go to cold email and LinkedIn CRMs. Ready for Instantly and Dripify.

Total time from import to export: under 10 minutes for a 60-lead batch.

---

## The Prospect Takeaway

The Lead Gen Pipeline is NexusPoint's internal prospecting engine. Every client conversation NexusPoint starts comes through this system or a version of it.

The architecture is not specific to NexusPoint's ICP. The ICP definition, scoring weights, pain signal keywords, and personalization context are all configuration. The underlying system is the same:

- Define what a good lead looks like (industry, size, title, signals)
- Score every prospect against that definition before spending a dollar on enrichment
- Enrich only the leads worth enriching, with the data that actually moves the needle
- Personalize using real signals, not templates pretending to be personal
- Export to whatever tools the team already uses

Any business with a sales motion — agency, SaaS, consulting, services — can run this. Different ICP. Different signals. Same system.

If your business is still running outreach off a static spreadsheet with no scoring and no enrichment, this is what replacing that looks like.

---

*Built and maintained by NexusPoint. Last updated: April 2026.*
