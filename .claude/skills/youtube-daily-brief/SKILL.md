---
name: youtube-daily-brief
description: |
  Generate and manage the YouTube Intelligence brief — a daily analysis of 13 AI/automation
  YouTube channels. Use this skill when asked to generate a YouTube brief, check what's
  trending on YouTube, analyze YouTube channel performance, or get content ideas from
  YouTube. Triggers on: "youtube brief", "youtube trends", "what's on youtube",
  "youtube channels", "scrape youtube", "generate youtube", "youtube intelligence",
  "what channels are posting", "youtube analysis".
---

# YouTube Intelligence Brief

The YouTube vertical analyzes 13 AI/automation YouTube channels daily — tracking trending topics, top-performing videos, channel stats, format distribution, and surfacing content opportunities. It is the 3rd vertical in the daily-news-brief dashboard (rose/red accent), alongside News Brief (amber) and Practical AI (teal).

## Self-Contained — Everything Lives Here

This skill is fully self-contained. All Python scripts live in `scripts/` in this folder — there is **no external repo dependency**. The Next.js dashboard (`projects/daily-news-brief/`) spawns these scripts as subprocesses.

```
.claude/skills/youtube-daily-brief/
├── SKILL.md
├── .gitignore                 # ignores .tmp/, scripts/.env, __pycache__
└── scripts/
    ├── config.py              # channel list, paths, env loading
    ├── scrape_channels.py     # YouTube Data API v3 scrape → .tmp/raw_videos.json
    ├── analyze_content.py     # GPT-5.2 analysis → .tmp/analysis.json
    └── requirements.txt
```

`.tmp/` (raw_videos.json, analysis.json, history/) is created automatically on first run.

## Pipeline Overview

Two Python scripts run sequentially:

1. **`scripts/scrape_channels.py`** — YouTube Data API v3 scrape of 13 channels (5 recent videos each, Shorts under 3 min skipped). Writes raw video data to `.tmp/raw_videos.json` and archives a daily snapshot to `.tmp/history/`.
2. **`scripts/analyze_content.py`** — GPT-5.2 analysis (`reasoning_effort=medium`, `max_completion_tokens=8192`) of scraped videos. Writes structured analysis to `.tmp/analysis.json`.

The Next.js pipeline (`src/lib/pipeline/youtube-run.ts`) spawns both scripts, reads `analysis.json`, and stores results in SQLite via Drizzle. It resolves this skill dir automatically (or honors `YOUTUBE_BRIEF_DIR` if set).

**Cost:** YouTube Data API free tier covers ~50-100 channels/day. GPT-5.2 at `reasoning_effort=medium` is the main cost (~$0.05-0.15/run depending on video count).

## How to Run

### From the dashboard (recommended)
Click **"Generate YouTube Brief"** in the sidebar (rose/red button) at http://localhost:3000

### Standalone cron
```bash
cd projects/daily-news-brief && npx tsx scripts/youtube-cron.ts
# specific date:
npx tsx scripts/youtube-cron.ts 2026-06-27
```

### Via the unified cron (`--youtube` flag)
```bash
cd projects/daily-news-brief && npx tsx scripts/daily-cron.ts --youtube
cd projects/daily-news-brief && npx tsx scripts/daily-cron.ts --youtube 2026-06-27
```

### Run the Python scripts directly (debugging)
```bash
cd .claude/skills/youtube-daily-brief
python scripts/scrape_channels.py
python scripts/analyze_content.py
```
For direct runs, drop a `scripts/.env` with `GOOGLE_API_KEY` + `OPENAI_API_KEY` (gitignored). When run via the dashboard/cron, the keys come from `projects/daily-news-brief/.env` through the inherited process env.

### View the dashboard
```bash
cd projects/daily-news-brief && npm run dev
```
Then open http://localhost:3000/youtube/[date]

## Prerequisites

**Keys** — set in `projects/daily-news-brief/.env` (the cron/API entrypoints load it, then pass it to the Python subprocess):
- `GOOGLE_API_KEY` — YouTube Data API v3 key (required)
- `OPENAI_API_KEY` — GPT-5.2 analysis (required — reused from the news pipeline)

**Python deps** (install once):
```bash
pip install -r .claude/skills/youtube-daily-brief/scripts/requirements.txt
```

**Optional `.env` overrides** (`projects/daily-news-brief/.env`):
- `YOUTUBE_BRIEF_DIR` — override the skill dir (defaults to `<repo>/.claude/skills/youtube-daily-brief`)
- `LAST30DAYS_PYTHON` — Python interpreter path (reused from the news pipeline)

## Editing the Channel List

Edit the `CHANNELS` list in `scripts/config.py`. Each entry is `{"handle": "@username", "name": "Display Name"}`. The handle is resolved to a channel ID via the YouTube Data API at scrape time.

## What the Analysis Covers

| Section | What it shows |
|---------|--------------|
| Sentiment Pulse | Overall tone across videos (bullish/cautious/neutral/hype-driven), confidence, signals |
| Trending Topics | Top topics by mention count, which channels covered them, per-topic sentiment |
| Top Videos | Best-performing videos this period: title, views, channel, thumbnail, external link |
| Content Ideas | GPT-derived content opportunities (10-15) — format + estimated interest |
| Suggested Topics | High-opportunity topics (10-15): angle, why now, competition level, reference videos |
| Channel Breakdown | Per-channel stats: total views, avg views, most common format, posting frequency |
| Format Distribution | CSS bar chart — tutorial / opinion / news / demo / explainer / interview |

## DB Tables

All stored in `projects/daily-news-brief/data/news.db` (SQLite):
- `youtube_briefs` — one row per date (top-level brief)
- `youtube_trending_topics` — trending topics for each brief
- `youtube_top_videos` — top-performing videos
- `youtube_channel_stats` — per-channel breakdown
- `youtube_content_ideas` — content opportunities
- `youtube_suggested_topics` — suggested topics with competition level

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Clicking "Generate" gives a 404 | The pipeline failed (no brief written). The sidebar now shows the error instead of redirecting — read it; usually a missing `GOOGLE_API_KEY` / `OPENAI_API_KEY` or a Python dep |
| "scrape_channels.py exited 1" | Check `GOOGLE_API_KEY` in `projects/daily-news-brief/.env` — likely missing or quota exceeded |
| "analyze_content.py exited 1" | Check `OPENAI_API_KEY` in `projects/daily-news-brief/.env`; also check quota/credits |
| "No module named googleapiclient/openai" | Run `pip install -r scripts/requirements.txt` |
| Python not found | Set `LAST30DAYS_PYTHON` in `projects/daily-news-brief/.env` to the correct interpreter |
| `.tmp/analysis.json` not found after script | scrape_channels.py failed — check `.tmp/raw_videos.json` exists first |
| Thumbnails not loading | `i.ytimg.com` must be in `next.config.ts` `images.remotePatterns` (already added) |
| Stale data shown | Run generate again; the pipeline is idempotent — re-running a date overwrites the existing brief |
| GPT-5.2 `max_tokens` error | The model requires `max_completion_tokens` + `reasoning_effort` — already set in `analyze_content.py` |
