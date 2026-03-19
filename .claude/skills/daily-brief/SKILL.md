---
name: daily-brief
description: |
  Generate and manage the daily AI/tech intelligence brief. Use this skill when the user
  asks to generate a brief, check AI news, see what's happening in AI/tech today, run the
  news pipeline, or anything related to the daily news digest. Triggers on: "generate brief",
  "daily brief", "news brief", "what's happening in AI", "AI news today", "tech news",
  "run the brief", "morning brief", "news update".
---

# Daily AI/Tech Intelligence Brief

Generate a comprehensive daily intelligence brief covering AI and tech news from multiple sources, analyzed and synthesized by Claude.

## Pipeline Overview

The brief runs a 6-step pipeline:

1. **Fetch** from 3 source types (NewsAPI, Hacker News top 150, 5 RSS feeds)
2. **Deduplicate** via fuzzy title matching, merge engagement scores
3. **Categorize** into 6 AI/tech categories using keyword scoring
4. **Analyze** each category with Claude Haiku (TL;DRs, sentiment, relevance scores)
5. **Synthesize** across categories with Claude Sonnet (trends, content ideas, overall sentiment)
6. **Store** in SQLite database for the dashboard

**Cost:** ~$0.06 per run (Haiku handles bulk, Sonnet only for final synthesis).

## How to Run

### Generate a brief

```bash
cd projects/daily-news-brief && npx tsx scripts/daily-cron.ts
```

For a specific date:
```bash
cd projects/daily-news-brief && npx tsx scripts/daily-cron.ts 2026-03-19
```

### View the dashboard

```bash
cd projects/daily-news-brief && npm run dev
```
Then open http://localhost:3000

### First-time setup

```bash
cd projects/daily-news-brief
npm install
cp .env.example .env
# Fill in ANTHROPIC_API_KEY and NEWSAPI_KEY
npx drizzle-kit push
```

## Prerequisites

The `.env` file in `projects/daily-news-brief/` must contain:
- `ANTHROPIC_API_KEY` — for Claude Haiku + Sonnet analysis
- `NEWSAPI_KEY` — get one free at https://newsapi.org
- `BRIEF_AUTH_TOKEN` (optional) — protects the HTTP generate endpoint

## 6 News Categories

1. **AI Models & Breakthroughs** — New models, benchmarks, research papers
2. **AI Tools & Products** — Product launches, developer tools, platforms
3. **AI Business & Strategy** — Funding, acquisitions, big tech strategy
4. **AI Automation & Workflows** — Agents, MCP, workflow tools, agentic AI
5. **AI Content & Creator Economy** — Creator tools, generative media, content AI
6. **AI Ethics, Safety & Regulation** — Safety research, regulation, policy

## After Generating

Once the brief is generated, offer to:
- **Open the dashboard** — `npm run dev` in the project directory
- **Summarize inline** — Read the brief data from the SQLite database and present key findings
- **Highlight content ideas** — Pull the 5 content ideas and present them as actionable next steps
- **Show trends** — Display the 5 cross-category trends with momentum signals

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "ANTHROPIC_API_KEY is not set" | Add key to `projects/daily-news-brief/.env` |
| "NEWSAPI_KEY not set, skipping" | Add NewsAPI key to `.env` (free tier works) |
| NewsAPI returns 426 error | Free tier only works on localhost, not deployed |
| HN fetch fails | Transient — pipeline has retry logic, run again |
| RSS feed timeout | Some feeds are slow — pipeline continues with available sources |
| "No articles fetched" | All sources failed — check internet connection and API keys |
| Build errors after changes | Run `npm run build` to check TypeScript errors |
