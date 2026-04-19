# Daily News Brief: How NexusPoint Built an AI-Powered Intelligence Dashboard for $0.03 a Day

**Category:** Internal AI System / Business Intelligence  
**Built by:** NexusPoint  
**Powered by:** Next.js 16, OpenAI (gpt-4o-mini + gpt-4o), SQLite, NewsAPI, Hacker News, RSS

---

## The Problem

Anyone who works in AI, tech, or a fast-moving industry faces the same daily problem: there's too much to read and no way to know what actually matters.

The default approach is to check Twitter, skim newsletters, and hope something important surfaces. But that process is slow, scattered, and inconsistent. You miss things. You read the same story in five different places. You get news without context, headlines without insight, and no signal on what's worth your time.

Four specific problems:

1. **Volume.** 100+ AI and tech stories break daily across NewsAPI, Hacker News, RSS feeds, and research journals. Nobody has time to read all of it.
2. **Duplication.** The same story gets published on TechCrunch, picked up on Hacker News, syndicated to three newsletters. You see it four times or zero times — never exactly once.
3. **No synthesis.** Aggregators show you headlines. They don't tell you what the pattern is, what's rising, or what the week's signal is across all that noise.
4. **No action.** Even a good summary doesn't tell you what to *do* with the information — what to write about, what angle is missing, what the community is already discussing.

NexusPoint built the Daily News Brief to solve all four — in one automated pipeline that runs daily for under $0.03.

---

## What It Is

The Daily News Brief is a full-stack intelligence system: a TypeScript pipeline that ingests news from multiple sources, runs it through a two-pass AI analysis, and renders everything in a Next.js dashboard that works like a daily intelligence briefing — not a feed.

One command triggers the pipeline. Thirty to sixty seconds later, the dashboard shows:
- 6 categorized AI/tech coverage areas with per-category insights
- 5 cross-category trends with 7-day momentum tracking
- 10 ready-to-use content ideas with hooks, angles, and key points
- Sentiment pulse on the overall AI news mood
- Source breakdown and engagement heatmap

Every brief is stored. Every trend is tracked over time. Every content idea can be saved to Google Sheets in one click.

---

## The Pipeline: 6 Steps

### Step 1 — Fetch from 3 Source Types (in parallel)

Three adapters run simultaneously to pull 100-150 raw articles:

**NewsAPI** — 6 targeted queries, one per category, pulling the last 48 hours. Returns titles, URLs, source names, publish times, and descriptions. ~60 articles.

**Hacker News** — Top 150 stories fetched from the Firebase API, filtered to AI-related content by keyword. Returns every article with its community engagement: upvote score and comment count. ~20-40 AI-related articles.

**RSS Feeds** — 5 curated feeds: ArXiv cs.AI (academic papers), TechCrunch AI, MIT Technology Review, The Verge AI, Ars Technica. Filtered to last 48 hours. ~30-50 articles.

No API key required for Hacker News or RSS. Total raw input: 100-150 articles per run.

---

### Step 2 — Deduplication

Before any AI is involved, a deduplication pass runs across all sources.

The algorithm: normalize every title (lowercase, strip punctuation, collapse whitespace), then match. If a shorter title (over 10 characters) is a substring of a longer one, they're the same story. Exact matches group together.

Within each duplicate group, the system keeps the richest description (longest), takes the maximum engagement score across all versions, and records how many sources covered the story (`sourceCount`). A story appearing in TechCrunch, Hacker News, and two RSS feeds gets a `sourceCount` of 4 — a signal that it matters.

Typical deduplication rate: 30-40%. 150 articles becomes ~80-90 unique stories.

---

### Step 3 — Categorization

Every article is scored against 6 category keyword sets. The category with the highest keyword match score wins. Articles with no match are flagged as uncategorized (system logs a warning if this exceeds 20% of the batch).

**The 6 categories:**

| Category | What It Covers |
|----------|---------------|
| AI Models & Breakthroughs | Model releases, benchmarks, research papers, GPT/Claude/Gemini/Llama |
| AI Tools & Products | Product launches, developer tools, APIs, Cursor, v0, Copilot |
| AI Business & Strategy | Funding, acquisitions, OpenAI/Anthropic/Google AI strategy, IPOs |
| AI Automation & Workflows | Agents, MCP, n8n, LangGraph, workflow automation, function calling |
| AI Content & Creator Economy | Midjourney, Sora, ElevenLabs, AI video/image, creator tools |
| AI Ethics, Safety & Regulation | EU AI Act, alignment, bias, deepfakes, policy, governance |

Each category holds up to 12 articles, sorted by engagement score then recency. Output: 50-72 articles across 6 buckets.

---

### Step 4 — Per-Category Analysis with Fast AI (Haiku pass)

Six parallel AI calls — one per category — using a fast, cost-efficient model (gpt-4o-mini). Each call receives the full list of articles in that category, including engagement scores and comment counts.

For each category, the model produces:

**Category insight:** A 2-3 sentence "so what?" — opinionated and forward-looking, not just a summary. Example: *"Multimodal models are reaching parity with specialized systems on coding benchmarks, but the gap on reasoning-heavy tasks is narrowing faster than expected. The industry is approaching a threshold where model choice becomes a cost and latency decision, not a capability one."*

**Per-article analysis:**
- TL;DR (1-2 sentences)
- Sentiment tag: `excited` / `neutral` / `concerned` / `skeptical`
- Relevance score (1-10)

**Emerging themes:** 2-3 keywords per category showing what's bubbling up within that area.

Six calls, six insights, every article summarized and scored. Total cost for this pass: under $0.002.

---

### Step 5 — Cross-Category Synthesis (Sonnet pass)

One synthesis call using a more powerful model (gpt-4o) that sees all six category outputs simultaneously. This is where the brief goes from "news summaries per topic" to "intelligence."

The model produces three outputs:

**5 Trends** — cross-category patterns that emerge when you look at all the news at once, not just one bucket at a time.

Each trend includes:
- Title and slug
- 2-3 sentence summary
- Momentum signal: `rising` / `steady` / `cooling`
- Which categories contribute to it
- Content potential score (1-10) — how worth writing about is this trend right now

Trends are tracked across days. If the same trend slug appears within 7 days, the system preserves the `firstSeenDate` and updates `lastSeenDate` — creating a 7-day momentum trail visible as a sparkline in the dashboard.

**Overall Sentiment** — a macro read on the AI news mood: `bullish` / `cautious` / `mixed` / `bearish`, with a 2-3 sentence explanation of what's driving it. Tracked daily for a 7-day sentiment timeline.

**10 Content Ideas** — the most actionable output. Each idea includes:
- Topic title
- Specific angle (the distinct take, not just the topic)
- Format: `thread` / `blog` / `newsletter`
- Hook (opening line, ready to use)
- 3-5 key points
- Timeliness: `breaking` / `trending` / `evergreen`
- Related trend slugs

Selection rules are strict: the system must include stories with 200+ HN upvotes, must have at least 2 breaking ideas, must span at least 3 different categories, and must connect to the highest-scoring trend. Duplicate angles on the same topic are collapsed — only the stronger hook survives.

---

### Step 6 — Store and Serve

Everything goes into SQLite across 5 tables: `briefs`, `categories`, `articles`, `trends`, `contentIdeas`. The write is atomic — the brief is created with a `_pending` suffix and only renamed to the real date once all data is inserted. No partial briefs ever serve.

The dashboard renders instantly from the database. Every brief is permanent. Historical data is queryable. Trend sparklines draw from 7 days of stored records.

---

## The Dashboard: 10 Sections

**Brief Header** — Date, total articles fetched, categories covered, sources used. Regenerate button for re-running the pipeline.

**Sentiment Pulse** — Today's macro mood (bullish/cautious/mixed/bearish) with an icon, summary, and the single top takeaway: one sentence capturing the most important signal of the day.

**Sentiment Timeline** — 7-day area chart showing how the overall AI news mood has moved. Bullish streaks, cautious stretches, and mixed weeks are all visible at a glance.

**Trending Now** — The 5 cross-category trends. Each card shows the momentum signal (rising/steady/cooling arrow), a content potential bar, which categories feed into it, and a 7-day sparkline of its content potential score over time.

**Content Opportunities** — The 10 content ideas, filterable by format (thread / blog / newsletter). Each idea is expandable: click to see the hook, angle, key points, and related trends. Actions: copy hook to clipboard, export as markdown, save directly to Google Sheets.

**Most Discussed** — Top 5 Hacker News articles by engagement score. Community signal, separate from editorial judgment.

**Category Heatmap** — A grid showing each category's average relevance score, sentiment breakdown (counts of excited/neutral/concerned/skeptical articles), and article volume. Instant visual on where the activity is and what the tone is.

**Source Breakdown** — Bar chart of articles by origin (NewsAPI / Hacker News / RSS). Shows which sources are contributing most on any given day.

**Category Keynotes** — Top 3 category insights as quick-scan cards with anchor links to their full coverage below.

**Full Coverage** — The complete filtered article list. Toggle categories on/off. Filter by sentiment tag. Sort by relevance, engagement, recency, or source count. Every article shows its TL;DR, source, publish time, engagement score, and how many sources covered it.

---

## What's Built and Working

| Feature | Status |
|---------|--------|
| Multi-source fetching (NewsAPI + Hacker News + 5 RSS feeds) | Live |
| Title-based deduplication with engagement merging | Live |
| Keyword-based categorization (6 categories) | Live |
| Per-category Haiku analysis (insight + TL;DR + sentiment + relevance) | Live |
| Cross-category Sonnet synthesis (5 trends + 10 ideas + sentiment) | Live |
| 7-day trend momentum tracking + sparklines | Live |
| 7-day sentiment timeline | Live |
| SQLite storage with atomic writes | Live |
| Full-stack Next.js dashboard (10 sections) | Live |
| Article filtering by category + sentiment tag | Live |
| Article sorting (relevance / engagement / recency / source count) | Live |
| Content idea management (copy / export markdown / save to Sheets) | Live |
| Bookmarking (localStorage) | Live |
| Full-text search across articles and TL;DRs | Live |
| Dark/light mode | Live |
| Google Sheets integration for content ideas | Live |

---

## Cost Breakdown

| Step | Model | Tokens per Run | Cost |
|------|-------|---------------|------|
| Per-category analysis × 6 | gpt-4o-mini | ~9,000 total | ~$0.002 |
| Synthesis | gpt-4o | ~3,500 total | ~$0.022 |
| **Total per run** | | | **~$0.02-0.03** |

Running daily: under $1/month. The pipeline generates 5 trends, 10 content ideas, 60+ summarized articles, and a full intelligence brief — every day — for less than the cost of a single coffee per month.

---

## The Architecture

**Frontend:** Next.js 16, React 19, TypeScript, Tailwind CSS v4, shadcn/ui  
**Backend:** Next.js API routes (TypeScript), tsx for CLI scripts  
**Database:** SQLite + Drizzle ORM (5 tables, atomic transactions)  
**AI:** gpt-4o-mini (fast analysis), gpt-4o (synthesis) via OpenAI API  
**Data sources:** NewsAPI, Hacker News Firebase API, rss-parser (5 feeds)  
**Integrations:** Google Workspace CLI (gws) for Sheets  

**Commands:**
```
npm run generate              → Run today's pipeline
npm run generate -- YYYY-MM-DD → Run for specific date
npm run dev                   → Start dashboard at localhost:3000
```

**Database tables:** `briefs` → `categories` → `articles` (one-to-many); `briefs` → `trends` (5 per brief); `briefs` → `contentIdeas` (10 per brief)

---

## End-to-End Walkthrough

Here's what running the brief looks like on a typical day:

1. `npm run generate` — pipeline starts. NewsAPI, Hacker News, and RSS feeds fetch in parallel.

2. 142 raw articles come in. Dedup removes 48 duplicates (34% rate). 94 unique stories remain.

3. Categorization assigns articles to 6 buckets. AI Automation & Workflows gets 12 (capped), AI Models gets 11, AI Business gets 10. 3 articles don't match any category — flagged in logs.

4. Six Haiku calls run in parallel (one per category). Each returns a category insight, per-article TL;DRs, sentiment tags, and relevance scores. Takes ~8 seconds.

5. One Sonnet synthesis call fires with all 6 category outputs. Returns 5 trends (one flags "agentic coding tools" as rising, matching the past 3 days' pattern), overall sentiment (cautious — two major safety stories today), and 10 content ideas. The top idea: a thread on why MCP is eating the plugin ecosystem, hook pre-written, 4 key points ready.

6. Everything stores to SQLite. Brief is available at `/brief/2026-04-18`.

7. Open the dashboard. Sentiment pulse shows cautious. Trending Now shows "Agentic Coding Tools" with a rising arrow and a 7-day sparkline that's been climbing for 4 days. Content Opportunities shows the MCP thread idea in slot 1. Click "Save to Sheet" — it's in the content planning Google Sheet in 2 seconds.

Total time from `npm run generate` to actionable brief in the dashboard: under 60 seconds.

---

## The Prospect Takeaway

The Daily News Brief is NexusPoint's internal intelligence tool. It runs every morning and feeds directly into the content engine, marketing decisions, and strategic conversations about where AI is heading.

The architecture behind it — multi-source aggregation, deduplication, two-pass AI analysis, persistent storage, and a clean dashboard — is not specific to AI news. The same system works for:

- A law firm tracking regulatory changes across multiple legal databases
- A retail brand monitoring competitor product launches and press coverage
- A VC fund synthesizing portfolio company news and sector signals
- A marketing agency briefing clients on industry developments weekly
- Any business that needs to stay ahead of a fast-moving information landscape

The data sources change. The categories change. The AI prompts and synthesis rules change. The underlying architecture is the same.

If your business generates value from staying informed — and most do — and you're still doing that manually, this is what automating it looks like.

---

*Built and maintained by NexusPoint. Last updated: April 2026.*
