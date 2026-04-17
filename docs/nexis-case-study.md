# Nexis: How NexusPoint Built an AI Executive Assistant That Runs the Agency

**Category:** Internal AI System / Agency Operations  
**Built by:** NexusPoint  
**Powered by:** Claude Code (Anthropic), OpenAI, Python, Next.js

---

## The Problem

Most agency founders hit the same ceiling.

You're good at the work. Clients trust you. The team delivers. But you're spending 60% of your week on things that don't move the needle — manual lead research, writing follow-up emails, chasing content ideas, explaining the same context to different tools, rebuilding the same proposal structure for every new client.

The high-leverage work — closing deals, positioning your offer, designing systems — keeps getting pushed to tomorrow.

NexusPoint hit this ceiling. The business was Upwork and Fiverr dependent. There was no independent client acquisition engine. Every session with an AI tool started from scratch, with no memory of what was already decided or what the business actually needed. The team was capable, but coordination was informal and slow.

The solution wasn't hiring more people. It was building a system that would handle the operational layer so the founder could stay focused on growth.

---

## The Solution: Nexis

Nexis is NexusPoint's internal AI executive assistant — a custom-built operating system for running a digital agency, built on top of Claude Code (Anthropic's agentic AI environment).

It's not a chatbot. It's not a prompt library. It's a persistent, context-aware system that knows the business, the team, the goals, and the active workflows — and executes them on demand.

Three sentences that capture it:

> Nexis handles the operational layer of NexusPoint — lead generation, daily intelligence, content creation, client proposals, team delegation, and research. Everything is triggered by natural language. It gets smarter with every session.

**Core architecture:**

- **Context Layer** — 5 persistent files that ground every interaction: who Aleem is, what NexusPoint does, the team and their roles, current priorities, and quarterly goals. No re-explaining. No context loss.
- **Skills Layer** — 19+ modular workflows, each triggered by a plain English command ("scrape leads", "generate brief", "create a proposal"). Each skill knows what tools to use, what to output, and how to store results.
- **Projects Layer** — 4 active technical projects running as standalone apps: Daily News Brief, Lead Gen Pipeline, Content Engine Dashboard, Upwork Job Scout.
- **Memory Layer** — An append-only decision log captures every meaningful choice. Claude Code's memory preserves learned patterns, preferences, and behaviors across sessions.
- **Integrations Layer** — 15+ connected tools and APIs including Google Workspace, Apify, Firecrawl, OpenAI, Hunter.io, Proxycurl, Perplexity, NewsAPI, and more.

---

## What Nexis Can Do

### 1. Client Acquisition — Automated

**Lead Generation Pipeline**

The lead gen system turns a manually curated list of prospects into a fully enriched, scored, and personalized outreach-ready database.

- Leads enter from a Google Sheet (Aleem marks "Include = Yes")
- A 5-layer ICP scoring system evaluates each lead on 100 points: contact quality, company quality, intent signals, decision-maker access, and reachability
- Leads are tiered (HOT ≥80 / STRONG ≥60 / WARM ≥35 / REJECTED <35)
- Each lead is enriched: website crawl + CMS detection, PageSpeed score, email finding (Hunter.io), LinkedIn profile data (Proxycurl, HOT only), and company news/funding signals (Perplexity)
- Claude Sonnet generates personalized hooks, pain points, and value props for each lead
- Leads are exported automatically to cold email, LinkedIn, and Instagram CRMs
- Current pipeline: 300+ scored and enriched prospects

**Cold Email Outreach**

Say "send today's batch" and the system:
- Pulls warm leads from Google Sheets
- Sends a 4-touch email sequence over 14-17 days via Gmail
- Tracks replies and surfaces any responses for manual follow-up
- Cost: near-zero (free tier Apify, Gmail, Google Sheets)

**LinkedIn Outreach**

Say "scrape linkedin leads" and the system:
- Scrapes founder, COO, and ops leads from LinkedIn via Apify
- Filters by ICP signals (role, industry, company size)
- Generates personalized 300-character connection notes via OpenAI

**Instagram Outreach**

Say "generate instagram DMs" and the system:
- Scrapes founder and agency accounts via hashtag search (Apify)
- Filters by follower count (100 to 100K) and bio signals
- Writes Voss-style opening DMs via GPT-4o-mini
- All sending is manual (to stay within platform limits)

---

### 2. Daily Intelligence Brief

Every morning, Nexis runs a complete AI and tech intelligence pipeline.

Say "generate brief" and the system:
- Pulls articles from NewsAPI (6 targeted queries), Hacker News (top 150), and 5 RSS feeds (ArXiv, TechCrunch, MIT Tech Review, The Verge, Ars Technica)
- Deduplicates across sources
- Classifies every article into 6 categories: AI Models, AI Tools, AI Business, AI Automation, AI Content, AI Ethics/Safety
- Claude Haiku analyzes each category (cost-efficient bulk processing)
- Claude Sonnet synthesizes cross-category trends and signals
- Stores everything in SQLite and surfaces it via a Next.js dashboard

Cost per run: ~$0.06. No subscriptions. No manual curation.

---

### 3. Content and Brand

Say "create content" and the Content Engine:
- Pulls ideas from 3 sources: the daily brief database, a YouTube brief (AI channel summaries), and a saved topics Google Sheet
- Scores each idea on 10 points: timeliness, competition, momentum, brand pillar fit, and saved-topic bonus
- Researches the top-scoring idea via OpenAI web search
- Writes a full 800-2000 word blog post in Aleem's voice
- Repurposes it into a LinkedIn post (300-800 words) and an Instagram carousel (5-8 slides)
- Saves to Google Docs and logs to Google Sheets

One command. Three pieces of content. Research included.

---

### 4. Sales and Revenue

**Proposal Generator**

Say "create a proposal for [client]" and the system generates a full client proposal using Hormozi's $100M Offers framework — including offer name, dream outcome, value stack, bonuses, 3-tier pricing, ROI math, and a dual guarantee. Delivered directly to Google Docs.

**Discovery Call Prep**

Say "prep me for a call with [company]" and Nexis:
- Crawls the prospect's website (Firecrawl)
- Pulls funding and news signals
- Outputs a 2-minute scan brief: company snapshot, likely pain points, NexusPoint positioning angle, Voss-style discovery questions, and watch-outs

**AI Use Case Generator**

Before any pitch, say "generate use cases for [business type]" and get 3 ROI-framed automation opportunities — operational efficiency, revenue growth, and customer experience — with specific metric ranges ready to drop into cold emails or discovery calls.

**Marketing Advisor**

For any strategic question — cold email copy, LinkedIn strategy, offer positioning, content calendars — the Marketing Advisor skill applies Hormozi's $100M Leads and $100M Offers frameworks alongside Voss's negotiation tactics to give grounded, actionable guidance.

---

### 5. Executive Operations

**Team Delegation**

Say "delegate [task]" and the system:
- Auto-matches the task to the right team member based on their skills
- Generates a ready-to-send WhatsApp or Discord message (6-8 lines, direct, no fluff)
- Optionally logs the delegation to a file

No context switching. No thinking about who's available for what.

**Deep Research**

Say "research [topic]" and the system:
- Reads the current business context (priorities, goals, work) to frame the query
- Routes to the right mode: deep (GPT-4o, multi-source), quick (GPT-4o-mini), or lite (Claude Haiku)
- Saves deep research to a dated file in the research/ directory

**Session Closeout**

Say "close out" at the end of a session and the system:
- Summarizes what was built or decided
- Appends meaningful decisions to an append-only decision log
- Updates the current-priorities file if focus has shifted
- Flags any patterns worth saving to long-term memory

---

## Results

| What | Impact |
|------|--------|
| Lead pipeline | 300+ prospects scored, enriched, and ready for outreach |
| Daily intelligence | Full AI/tech brief for <$0.10/day |
| Content creation | Blog + LinkedIn + Instagram from one command |
| Proposals | Hormozi-framed Google Doc in minutes |
| Team delegation | Zero context-switch overhead |
| Client acquisition | Independent pipeline replacing Upwork/Fiverr dependency |
| Revenue positioning | AI automation added as premium service offering |

---

## The Architecture (For Technical Readers)

**Tech Stack:**
- Python (automation scripts, pipelines, CLI tools)
- Next.js 16 + React 19 + TypeScript (dashboards)
- SQLite + Drizzle ORM (structured data storage)
- Tailwind CSS v4 + shadcn/ui (UI components)
- Anthropic SDK (Claude Haiku + Sonnet)

**AI Models:**
- Claude Haiku — bulk analysis, cost-sensitive tasks
- Claude Sonnet — synthesis, personalization, proposals
- OpenAI GPT-4o — deep research
- OpenAI GPT-4o-mini — quick lookups, Instagram DM generation

**Integrations:**
- Apify (LinkedIn, Instagram, Google Maps scraping)
- Firecrawl (website crawling)
- Hunter.io (email finding)
- Proxycurl (LinkedIn enrichment)
- Perplexity (company news, funding signals)
- Google Workspace via gws CLI (Gmail, Sheets, Docs, Calendar)
- NewsAPI + Hacker News + RSS (daily brief)
- Google PageSpeed Insights (site performance scoring)

**Design Principles:**
- Modular skills (each workflow is independent and reusable)
- Persistent context (no re-explaining the business)
- Compounding memory (decisions and patterns accumulate over time)
- Cost-stratified AI usage (Haiku for bulk, Sonnet for synthesis, GPT-4o for depth)

---

## The Takeaway for Prospects

Nexis is NexusPoint's internal proof of concept. It's the answer to the question: what does it actually look like when an agency goes AI-native?

Not AI-assisted — AI-native. Where the operational layer runs on automation, the strategic layer runs on systems, and the founder's time goes toward closing deals and designing what's next.

The same architecture that powers Nexis — agentic AI, modular workflows, persistent context, deep integrations — is what NexusPoint builds for clients.

Lead generation. Content. Operations. Sales support. Customer intelligence. These are universal business needs. The specific tools change. The stack adapts. But the core design: a system that knows your business, executes your workflows, and gets smarter over time — that's what we build.

If you want to see what this looks like applied to your business, that's the conversation worth having.

---

*Built and maintained by NexusPoint. Last updated: April 2026.*
