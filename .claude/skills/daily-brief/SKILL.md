---
name: daily-brief
description: |
  Generate and manage the daily AI/tech intelligence brief and YouTube Intelligence brief.
  Use this skill when the user asks to generate a brief, check AI news, see what's happening
  in AI/tech today, run the news pipeline, or anything related to the daily news digest or
  YouTube channel analysis. Triggers on: "generate brief", "daily brief", "news brief",
  "what's happening in AI", "AI news today", "tech news", "run the brief", "morning brief",
  "news update", "youtube brief", "youtube trends", "what's on youtube", "youtube channels",
  "scrape youtube", "generate youtube", "youtube intelligence", "what channels are posting".
---

# Daily AI/Tech Intelligence Brief

Generate a comprehensive daily intelligence brief covering AI and tech news from multiple sources, analyzed and synthesized by Claude.

## Pipeline Overview

The brief runs a 6-step pipeline:

1. **Fetch + rank** evidence via the **last30days engine** (multi-source: Reddit, Hacker News, GitHub, Web, + optional social), with RRF fusion, cross-source corroboration, and graceful per-source degradation. Replaces the old brittle NewsAPI/RSS sweep.
2. **Deduplicate** via fuzzy title matching, merge engagement scores
3. **Categorize** into 6 AI/tech categories using keyword scoring
4. **Analyze** each category with Claude Haiku (TL;DRs, sentiment, relevance scores)
5. **Synthesize** across categories with Claude Sonnet (trends, content ideas, overall sentiment)
6. **Store** in SQLite database for the dashboard

The engine does deterministic **fetch + rank** (no LLM key required — it falls back to local RRF scoring; with a key it uses a cheap rerank). daily-brief's Haiku/Sonnet still do all the **analysis**. Topics drive *what is fetched*; the 6 categories drive *how it is displayed*.

**Cost:** ~$0.06 per run for analysis (Haiku bulk + Sonnet synthesis) + cheap web-search calls from the engine. Social sources (`--full`) add paid ScrapeCreators/xAI calls.

## Two run modes

- **Daily mode (default):** a broad sweep of the **last 1-2 days of AI news** across all 6 categories, driven by the curated theme list in `src/lib/pipeline/themes.ts` **plus** up to 2 live breaking topics auto-derived from today's headlines (on by default; disable with `DAILY_BRIEF_DERIVE_TOPICS=0`).
- **On-demand topic mode:** name a **specific topic** + **timeline** to fetch just that, deeper.

## How to Run

### Generate the daily brief (last 1-2 days, all categories)

```bash
cd projects/daily-news-brief && npx tsx scripts/daily-cron.ts
```

For a specific date:
```bash
cd projects/daily-news-brief && npx tsx scripts/daily-cron.ts 2026-03-19
```

### On-demand: a specific topic over a specific timeline

```bash
cd projects/daily-news-brief && npx tsx scripts/daily-cron.ts --topic "Claude Code" --days 7
```

### Deep mode (adds paid social sources: X, TikTok, YouTube, Instagram, Threads, Polymarket)

```bash
# add --full (or --deep) to either run
npx tsx scripts/daily-cron.ts --full
npx tsx scripts/daily-cron.ts --topic "AI agents" --days 7 --full
```

Flags: `--topic "<topic>"` (on-demand mode), `--days N` (timeline, default 2), `--full`/`--deep` (depth, default lean). No flags = daily lean sweep over the last 2 days.

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
# Fill in OPENAI_API_KEY + ANTHROPIC_API_KEY
npx drizzle-kit push
```

## Prerequisites

**Python:** the last30days engine needs Python 3.12+. The wrapper invokes `LAST30DAYS_PYTHON` (defaults to the local `python3.14.exe`).

**Keys** — the project `.env` (`projects/daily-news-brief/.env`) needs:
- `OPENAI_API_KEY` — Pass 1 analysis + the engine's cheap rerank
- `ANTHROPIC_API_KEY` — analysis fallback (Sonnet synthesis)
- `BRIEF_AUTH_TOKEN` (optional) — protects the HTTP generate endpoint

The engine's **source keys** live in the **repo-root `.env`** (loaded automatically by the wrapper; single source of truth):
- `PARALLEL_API_KEY` — web search (used by the default lean source set)
- `SCRAPECREATORS_API_KEY`, `XAI_API_KEY` — social sources (only hit on `--full` runs)

Reddit, Hacker News and GitHub work keyless. NewsAPI is no longer used.

Path overrides (optional, set in `.env` if running outside the project root): `LAST30DAYS_DIR` (engine scripts dir), `LAST30DAYS_ENV` (repo-root .env path), `LAST30DAYS_PYTHON` (interpreter). Live headline auto-derive is on by default — `DAILY_BRIEF_DERIVE_TOPICS=0` disables it, `DAILY_BRIEF_MAX_DERIVED` tunes the count (default 2).

## 6 News Categories

1. **AI Models & Breakthroughs** — New models, benchmarks, research papers
2. **AI Tools & Products** — Product launches, developer tools, platforms
3. **AI Business & Strategy** — Funding, acquisitions, big tech strategy
4. **AI Automation & Workflows** — Agents, MCP, workflow tools, agentic AI
5. **AI Content & Creator Economy** — Creator tools, generative media, content AI
6. **AI Ethics, Safety & Regulation** — Safety research, regulation, policy

## Practical AI: "Look up any tool" (NotebookLM-grounded)

The dashboard's Practical AI page has a **"Look up any tool"** search (e.g. "Claude Code", "n8n", "Cursor"). It is grounded on **NotebookLM**, not the news pipeline:

1. Creates a throwaway notebook (`Tool Lookup: <tool> (date)`).
2. Runs fast web research (`source add-research ... --import-all`) — imports real docs, blogs, YouTube, GitHub, Reddit.
3. Removes any blocklisted sources from the notebook (`removeIgnoredSources`).
4. Asks a grounded question for a cited synthesis, then formats it into the lookup JSON via `callWithFallback` (gpt-5.2 primary, Claude fallback).
5. Stores a `practical_lookups` row (in `data/news.db`) including a `notebook_url`, then redirects to `/practical/lookup/[id]`.

The notebook **persists** so the result page shows a **"Grounded via NotebookLM"** link to verify the search; it is only deleted if the lookup fails. If NotebookLM is unavailable (see auth note below), it **falls back** to GitHub-star-ranked + Firecrawl web + last30days community sources — usable, but ungrounded and with no notebook link.

**Source blocklist** (`src/lib/pipeline/sources/notebooklm.ts`):
- `IGNORED_URLS` — exact URLs to drop.
- `IGNORED_DOMAINS` — whole hostnames to drop (currently `code.claude.com`; covers every path under it).
- `isIgnoredUrl` checks both, and the filter applies to both the NotebookLM and fallback paths. Add new blocks to whichever set fits.

**NotebookLM auth expires every few hours.** When it does, lookups silently fall back (no "Grounded via NotebookLM" badge = it fell back). Re-authenticate with `notebooklm login` (see the `reference-notebooklm-setup` memory for the exe path and login command). Code + ops detail: see the `project-practical-lookup-notebooklm` memory.

## After Generating

Once the brief is generated, offer to:
- **Open the dashboard** — `npm run dev` in the project directory
- **Summarize inline** — Read the brief data from the SQLite database and present key findings
- **Highlight content ideas** — Pull the 5 content ideas and present them as actionable next steps
- **Show trends** — Display the 5 cross-category trends with momentum signals

## YouTube Intelligence (3rd Vertical)

A separate daily analysis of 13 AI/automation YouTube channels, integrated into the same dashboard with a rose/red accent.

### How to Run

```bash
# Standalone
cd projects/daily-news-brief && npx tsx scripts/youtube-cron.ts

# Via unified cron
npx tsx scripts/daily-cron.ts --youtube

# Dashboard button
# Click "Generate YouTube Brief" (rose button) in the sidebar at http://localhost:3000
```

### Dashboard
http://localhost:3000/youtube/[date]

### What it shows
Trending topics, top videos (with thumbnails), content ideas, suggested topics with competition level, per-channel stats, format distribution.

### Prerequisites
`GOOGLE_API_KEY` + `OPENAI_API_KEY` must be set in `projects/daily-news-brief/.env`. The pipeline is self-contained — the Python scripts live in `.claude/skills/youtube-daily-brief/scripts/` and read keys from the inherited process env.

For full details see the `youtube-daily-brief` skill.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "ANTHROPIC_API_KEY is not set" | Add key to `projects/daily-news-brief/.env` |
| "last30days requires Python 3.12+" | Install Python 3.12+ and point `LAST30DAYS_PYTHON` at it |
| "last30days exited N" / non-JSON | Check the engine path (`LAST30DAYS_DIR`) and that the repo-root `.env` has `PARALLEL_API_KEY` |
| A source shows errors but run completes | Expected — the engine + wrapper fail open per source/topic |
| No social sources in output | Social only runs on `--full`; needs `SCRAPECREATORS_API_KEY` / `XAI_API_KEY` |
| "No articles fetched" | Every topic failed — check internet, Python, and the engine keys |
| Tool lookup returns weak sources / no "Grounded via NotebookLM" badge | NotebookLM session expired and it fell back — run `notebooklm login`, then re-run the lookup |
| Lookup shows a source you want gone | Add the URL to `IGNORED_URLS` or its host to `IGNORED_DOMAINS` in `src/lib/pipeline/sources/notebooklm.ts` |
| Build errors after changes | Run `npm run build` to check TypeScript errors |
