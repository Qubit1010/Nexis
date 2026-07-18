---
name: daily-brief
description: |
  Generate and manage the daily AI/tech intelligence brief, the Practical AI (SMB
  marketing) brief, and the YouTube Intelligence brief, plus the scheduled noon
  digest that logs both to a Google Sheet and emails it.
  Use this skill when the user asks to generate a brief, check AI news, see what's
  happening in AI/tech today, run the news pipeline, generate Practical AI, run the
  daily digest, schedule the brief, or anything about the daily news digest or
  YouTube analysis. Triggers on: "generate brief", "daily brief", "news brief",
  "what's happening in AI", "AI news today", "tech news", "run the brief", "morning
  brief", "practical AI", "generate tools brief", "daily digest", "schedule the
  brief", "email me the brief", "youtube brief", "youtube trends", "youtube channels",
  "generate youtube", "youtube intelligence".
---

# Daily AI/Tech Intelligence Brief

Three verticals in one Next.js + SQLite dashboard (`projects/daily-news-brief`):
**News Brief** (`/brief/[date]`), **Practical AI** (`/tools/[date]`), **YouTube
Intelligence** (`/youtube/[date]`). Evidence for the first two comes from the repo's
`research` skill; analysis is a Haiku-tier per-section pass + a Sonnet-tier synthesis.

## Evidence engine (research skill)

Both the News Brief and Practical AI fetch through `src/lib/pipeline/sources/research.ts`,
which shells out to `.claude/skills/research/scripts/research.py` (Exa + Tavily +
Serper fused, URL-deduped, ranked by cross-source corroboration). A shared junk-URL
filter drops GitHub issues/PRs/commits, bare Hacker News threads, Reddit comment pages,
and blocklisted domains before anything reaches the LLM; a TRUSTED_DOMAINS set gives
authoritative publishers a small rank nudge.

**Interpreter:** `RESEARCH_PYTHON` must point at a Python with the research skill's deps
(`exa-py`) installed — on this machine `.../Python312/python.exe`, NOT the 3.14 install
the retired last30days engine used. Search keys (`EXA_API_KEY`, `TAVILY_API_KEY`,
`SERPER_API_KEY`) auto-load from the repo-root `.env`.

## News Brief

**Daily mode (default):** a 1-2 day sweep across 6 AI/tech categories, driven by the
curated themes in `src/lib/pipeline/themes.ts` plus up to 2 breaking topics auto-derived
from today's RSS/HN headlines (disable with `DAILY_BRIEF_DERIVE_TOPICS=0`).
**On-demand topic mode:** a specific topic + timeline, fetched deeper.

```bash
cd projects/daily-news-brief
npx tsx scripts/daily-cron.ts                       # today, all categories
npx tsx scripts/daily-cron.ts 2026-03-19            # a specific date
npx tsx scripts/daily-cron.ts --topic "Claude Code" --days 7   # on-demand
npx tsx scripts/daily-cron.ts --full                # deeper (research deep depth)
```

"Most Discussed" ranks by cross-source corroboration (`sourceCount`) and auto-hides when
nothing is corroborated (no engagement/upvote data exists anymore).

### 6 News Categories
AI Models & Breakthroughs · AI Tools & Products · AI Business & Strategy · AI Automation
& Workflows · AI Content & Creator Economy · AI Ethics, Safety & Regulation.

## Practical AI (SMB marketing educator)

Topic-led: rotates 2 (lean) / 3 (full) of **9 SMB marketing topics** per day
(Business Overview, Content Automation, Target Audience, Market Analysis, Marketing Goals,
Marketing Strategy, Social Media Strategy, Sales Funnel, KPIs), deterministic by date so a
full cycle completes within 9 days and regenerating a past date reproduces its topics.
Each topic teaches: business problem in plain language -> agentic-AI solutions
(Claude Code / Claude Cowork / Codex) -> exactly 3 copy-paste steps -> ready-to-post
content ideas. A movers rail (GitHub Trending + OpenRouter) covers "what's new".

```bash
npx tsx scripts/daily-tools.ts                      # today's Practical AI brief
npx tsx scripts/daily-tools.ts 2026-07-19           # a specific date (rotates topics)
npx tsx scripts/daily-tools.ts --full               # 3 topics, deep research depth
```

### Look up any tool
The Practical AI page has a **"Look up any tool"** search (`/api/practical/search` ->
`runToolLookup` -> `/practical/lookup/[id]`). It runs two research queries for the tool
(new features/changelog + how-to-use-for-business) over a day window; the shared junk
filter keeps GitHub issues and forum threads out. Older lookup rows that predate the
research rebuild keep their "Grounded via NotebookLM" badge; new rows don't use it.

## Scheduled Daily Digest (noon) — Sheet + email

A once-a-day job that generates both briefs, logs a one-row-per-day summary to a Google
Sheet, and emails the digest to `DIGEST_EMAIL` (defaults to the gws-authed account).

```bash
# Register / remove the Windows scheduled task (fires daily at 12:00 local time)
npx tsx scripts/daily-digest.ts --schedule
npx tsx scripts/daily-digest.ts --unschedule

# Run the digest by hand (reads already-generated briefs; does NOT regenerate)
npx tsx scripts/daily-digest.ts                     # today: log + email
npx tsx scripts/daily-digest.ts 2026-07-18          # a specific date
npx tsx scripts/daily-digest.ts --no-email          # log to the sheet only
```

- **Scheduled target:** `scripts/run-digest.cmd` runs `daily-cron` -> `daily-tools` ->
  `daily-digest` in order, so the sheet + email reflect fresh briefs. The task
  (`NexisDailyBrief`) needs the machine on and signed in at noon.
- **Sheet:** self-bootstrapping — the first run creates "NexusPoint Daily Brief" (two
  tabs, News Brief + Practical AI) and remembers its ID in `data/digest-sheet.json`.
  One row per day per tab, upserted (re-running a date overwrites that day's row). Pin a
  specific sheet with `DIGEST_SHEET_ID`.
- **Email:** HTML digest (sentiment, takeaway, trends, corroborated stories; Practical AI
  topics, top pick, workflow recipe, content ideas) with links back to the dashboard
  (`DIGEST_DASHBOARD_URL`, default localhost — only clickable while `npm run dev` runs).
- Sheets + Gmail go through `scripts/gws.ts`, which calls the gws CLI via `node run.js`
  directly (no cmd.exe) — the same quoting-safe pattern as leads-to-crm's `sheets.py`.

## View the dashboard

```bash
cd projects/daily-news-brief && npm run dev   # http://localhost:3000
```

## First-time setup

```bash
cd projects/daily-news-brief
npm install
cp .env.example .env
# Fill in OPENAI_API_KEY + ANTHROPIC_API_KEY; ensure repo-root .env has EXA/TAVILY/SERPER
npx drizzle-kit push
```

## YouTube Intelligence (3rd vertical)

Separate daily analysis of 13 AI/automation YouTube channels (own Python pipeline in
`.claude/skills/youtube-daily-brief/`, needs `GOOGLE_API_KEY` + `OPENAI_API_KEY`).

```bash
npx tsx scripts/youtube-cron.ts          # standalone
npx tsx scripts/daily-cron.ts --youtube  # via unified cron
```

Dashboard: `/youtube/[date]`. Full details in the `youtube-daily-brief` skill.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "exa-py not installed" / research returns nothing | Point `RESEARCH_PYTHON` at the Python312 interpreter that has `exa-py`; check repo-root `.env` has EXA/TAVILY/SERPER keys |
| "No articles fetched" | Every research query failed — check internet + keys; research.py fails open per query and exits 0 even when all engines fail |
| Brief header shows a low source count | Expected when few results are cross-corroborated; the stat now counts real publisher domains |
| Digest email didn't arrive | Run `npx tsx scripts/daily-digest.ts` by hand and read the output; gws must be authenticated (`gws` account = the digest recipient default) |
| Scheduled task didn't fire | Machine must be on + signed in at noon; check `schtasks /Query /TN NexisDailyBrief` |
| "ANTHROPIC_API_KEY is not set" | Add the key to `projects/daily-news-brief/.env` |
| Build errors after changes | `npm run build` to surface TypeScript errors |
