# Daily News Brief

AI-powered daily intelligence brief for AI/tech news. Fetches from multiple sources, deduplicates, categorizes, analyzes with Claude, and displays in a polished dashboard.

## Architecture

```
NewsAPI (6 queries)  ──┐
Hacker News (top 150) ─┼── Dedup ── Categorize ── Haiku (per-cat) ── Sonnet (synthesis) ── SQLite ── Dashboard
RSS (5 feeds)        ──┘
```

**Pipeline steps:**
1. Fetch from NewsAPI, Hacker News, RSS (ArXiv, TechCrunch, MIT Tech Review, The Verge, Ars Technica)
2. Deduplicate via fuzzy title matching, merge engagement scores
3. Categorize into 6 AI/tech categories using keyword scoring
4. Analyze each category with Claude Haiku (TL;DRs, sentiment, relevance)
5. Synthesize across categories with Claude Sonnet (trends, content ideas, overall sentiment)
6. Store in SQLite, display in Next.js dashboard

**Cost:** ~$0.06 per run (Haiku for bulk analysis, Sonnet for synthesis only).

## Setup

```bash
npm install
cp .env.example .env
# Fill in your API keys in .env
npx drizzle-kit push
```

## Usage

**Generate a brief:**
```bash
npm run generate                    # Today's brief
npm run generate -- 2026-03-19      # Specific date
```

**Run the dashboard:**
```bash
npm run dev
# Open http://localhost:3000
```

**Via Claude Code skill:**
Say "generate the daily brief" or use `/daily-brief`.

## Tech Stack

- Next.js 16 + React 19
- Anthropic SDK (Haiku + Sonnet)
- SQLite + Drizzle ORM
- Tailwind CSS v4 + shadcn/ui

## Categories

1. AI Models & Breakthroughs
2. AI Tools & Products
3. AI Business & Strategy
4. AI Automation & Workflows
5. AI Content & Creator Economy
6. AI Ethics, Safety & Regulation

## Security

- Never commit `.env` — use `.env.example` as a template
- Set `BRIEF_AUTH_TOKEN` in production to protect the generate endpoint
- If migrating from the old project, rotate your API keys immediately
