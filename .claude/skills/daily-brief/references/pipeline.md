# Pipeline Architecture

## Data Flow

```
Sources (parallel)          Processing              AI Analysis           Storage
──────────────────          ──────────              ───────────           ───────
NewsAPI (6 queries) ──┐
HackerNews (top 150) ─┼── Dedup ── Categorize ── Haiku (per-cat) ── Sonnet (synth) ── SQLite
RSS (5 feeds)        ──┘
```

## Sources

### NewsAPI
- 6 parallel queries (one per category using `newsApiQuery`)
- Last 2 days, English only, sorted by publishedAt
- Filters out removed articles and those without descriptions
- Free tier: localhost only

### Hacker News
- Fetches top 150 stories via Firebase API (batches of 20)
- Filters by AI-related keywords in titles
- Captures engagement (upvotes) and comment counts

### RSS Feeds
- ArXiv cs.AI, TechCrunch AI, MIT Tech Review, The Verge AI, Ars Technica
- Last 2 days, 10-second timeout per feed
- Extracts content snippets (first 500 chars)

## Processing

### Deduplication
- Normalizes titles (lowercase, strip punctuation)
- Groups articles with matching titles (exact or substring inclusion)
- Picks article with richest description, merges engagement scores

### Categorization
- Scores each article against all 6 categories using keyword matching
- Assigns to highest-scoring category
- Caps at 12 articles per category
- Sorts by engagement score, then recency
- Logs uncategorized articles with percentage

## AI Analysis

### Pass 1: Haiku (per-category)
- Runs in parallel across all categories
- Produces: category insight, per-article TL;DR + sentiment + relevance score, emerging themes
- Articles include `originalIndex` for reliable matching back to raw data

### Pass 2: Sonnet (synthesis)
- Takes all Pass 1 results as input
- Produces: 5 cross-category trends, overall sentiment, 5 content ideas, top takeaway
- Trends track across days via slug matching (7-day window)

## Database Schema

- **briefs** — One per date. Stores overall sentiment, top takeaway, fetch stats.
- **categories** — Per-brief category rows with insights.
- **articles** — Individual articles with TL;DR, sentiment, relevance, engagement.
- **trends** — Cross-category trends with momentum signals and multi-day tracking.
- **content_ideas** — Actionable content suggestions with format, hook, key points.

## Key Files

| File | Purpose |
|------|---------|
| `scripts/daily-cron.ts` | CLI entry point |
| `src/lib/pipeline/run.ts` | Main orchestrator |
| `src/lib/pipeline/sources/` | NewsAPI, HN, RSS fetchers |
| `src/lib/pipeline/deduplicator.ts` | Title-based dedup |
| `src/lib/pipeline/categorizer.ts` | Keyword scoring |
| `src/lib/pipeline/processor.ts` | Claude API calls |
| `src/lib/pipeline/prompts.ts` | Prompt templates |
| `src/lib/pipeline/utils.ts` | Retry, JSON extraction, title similarity |
| `src/lib/db/schema.ts` | Drizzle ORM schema |
