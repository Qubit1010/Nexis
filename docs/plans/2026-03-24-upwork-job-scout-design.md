# Upwork Job Scout — Design Document

*Created: 2026-03-24*

## Overview

A local Next.js web app for filtering, scoring, and managing Upwork job listings. Vollna-style UI with NexusPoint branding. Uses dummy data initially; swaps to Upwork OAuth 2.0 + GraphQL API once key is approved.

## Goals

- Cut time spent manually scanning Upwork jobs
- Surface only relevant, quality jobs based on budget + client signals
- Persist bookmarks and bid queue across sessions

## Tech Stack

| Layer | Choice | Reason |
|-------|--------|--------|
| Framework | Next.js 14 (App Router) + TypeScript | Familiar, full-stack in one repo |
| Styling | Tailwind CSS + shadcn/ui | Fast, consistent, dark-theme friendly |
| Database | SQLite via `better-sqlite3` | Local, zero-config, no server needed |
| Auth | Upwork OAuth 2.0 | Official API, no ToS risk |

## Project Structure

```
projects/upwork-job-scout/
├── app/
│   ├── page.tsx                  # Main dashboard
│   ├── bookmarks/page.tsx        # Saved jobs
│   ├── bid-queue/page.tsx        # Bid later queue with status
│   ├── settings/page.tsx         # Budget floors config
│   └── api/
│       ├── jobs/route.ts         # Fetch + filter + score jobs
│       ├── bookmarks/route.ts    # CRUD bookmarks
│       ├── bid-queue/route.ts    # CRUD bid queue
│       ├── settings/route.ts     # Read/write settings
│       └── auth/callback/        # Upwork OAuth callback
├── components/
│   ├── FilterSidebar.tsx
│   ├── JobCard.tsx
│   ├── JobList.tsx
│   ├── ScoreBadge.tsx
│   └── Nav.tsx
├── lib/
│   ├── db.ts                     # SQLite client + migrations
│   ├── upwork.ts                 # API client (dummy → real swap)
│   └── scorer.ts                 # Bid scoring logic
├── data/
│   └── dummy-jobs.ts             # Realistic dummy jobs until API approved
└── .env.local                    # Upwork credentials (gitignored)
```

## UI Layout

3-column layout, NexusPoint dark theme:

```
┌─────────────────────────────────────────────────────┐
│  NexusPoint Job Scout          [Bookmarks] [Queue] [Settings] │
├──────────────┬──────────────────────────────────────┤
│              │  54 jobs found    [Sort: Newest ▼]   │
│  FILTERS     ├──────────────────────────────────────┤
│              │  ┌────────────────────────────────┐  │
│  Category    │  │ Job Title              $1,200  │  │
│  ○ Web Dev   │  │ Client: ✓ Verified  4.9★  $5k  │  │
│  ○ AI/Auto   │  │ Skills: React, Next.js         │  │
│  ○ CMS       │  │              [Score: 87] [Save] │  │
│  ○ Data      │  └────────────────────────────────┘  │
│              │  ┌────────────────────────────────┐  │
│  Keywords    │  │ Unverified job (greyed out)    │  │
│  [+ add]     │  └────────────────────────────────┘  │
│              │                                      │
│  Budget      │                                      │
│  Min: [$___] │                                      │
│              │                                      │
│  Client      │                                      │
│  ☑ Verified  │                                      │
│              │                                      │
│  [Save Filter│                                      │
│   Preset]    │                                      │
└──────────────┴──────────────────────────────────────┘
```

## Color System

| Token | Hex | Usage |
|-------|-----|-------|
| Background | `#232323` | App background |
| Surface | `#2d2d2d` | Cards, sidebar |
| Primary | `#208ec7` → `#1f5b99` | Accents, buttons |
| Text | `#ffffff` | Primary text |
| Muted | `#9ca3af` | Secondary text |
| Success | `#22c55e` | High score (70-100) |
| Warning | `#eab308` | Medium score (40-69) |
| Danger | `#ef4444` | Low score (0-39) |

## Scoring Logic

**Bid Score: 0–100**

| Signal | Weight | Logic |
|--------|--------|-------|
| Budget | 60% | Job budget vs category floor. At floor = 30pts. 2x floor = 60pts. Linear scale. |
| Client Quality | 40% | Verified + rating + total spent. Unverified = capped at 50 total score. |

Score colors: 70-100 green, 40-69 yellow, 0-39 red. Unverified clients shown greyed.

## Category Budget Floors (configurable)

Stored in `settings` table. Defaults:

| Category | Fixed Min | Hourly Min |
|----------|-----------|------------|
| Web Dev | $100 | $15/hr |
| AI/Automation | $100 | $10/hr |
| CMS | $50 | $10/hr |
| Data Analysis | $50 | $10/hr |

## Database Schema

```sql
-- Cached job listings
CREATE TABLE jobs (
  id TEXT PRIMARY KEY,
  title TEXT,
  description TEXT,
  budget REAL,
  budget_type TEXT,         -- 'fixed' | 'hourly'
  category TEXT,
  skills TEXT,              -- JSON array
  client_verified INTEGER,  -- 0 | 1
  client_spent REAL,
  client_rating REAL,
  client_hire_rate REAL,
  posted_at TEXT,
  score INTEGER,
  raw_json TEXT,
  fetched_at TEXT
);

-- Named filter presets
CREATE TABLE saved_filters (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  category TEXT,
  keywords TEXT,            -- JSON array
  min_budget REAL,
  client_verified_only INTEGER,
  created_at TEXT
);

-- Bookmarked jobs
CREATE TABLE bookmarks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id TEXT,
  notes TEXT,
  created_at TEXT
);

-- Bid queue
CREATE TABLE bid_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id TEXT,
  status TEXT,              -- 'pending' | 'sent' | 'won' | 'lost'
  notes TEXT,
  created_at TEXT
);

-- Configurable settings (budget floors etc.)
CREATE TABLE settings (
  key TEXT PRIMARY KEY,
  value TEXT,
  updated_at TEXT
);
```

## Data Source

- **Now:** `data/dummy-jobs.ts` — 20 realistic dummy jobs across all categories
- **Later:** Upwork GraphQL API via `marketplaceJobPostingsSearch` (OAuth 2.0)
- Swap controlled by `UPWORK_API_ENABLED=true` env var — no code changes needed

## Pages

| Route | Purpose |
|-------|---------|
| `/` | Main dashboard — filter + job list |
| `/bookmarks` | Saved jobs with notes |
| `/bid-queue` | Jobs to bid on with status tracking |
| `/settings` | Edit budget floors per category |

## API Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/api/jobs` | GET | Fetch, filter, score jobs |
| `/api/bookmarks` | GET/POST/DELETE | Manage bookmarks |
| `/api/bid-queue` | GET/POST/PATCH/DELETE | Manage bid queue |
| `/api/settings` | GET/PUT | Read/write settings |
