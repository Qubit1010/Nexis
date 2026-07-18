---
name: weekly-business-review
description: >
  Generate the NexusPoint Weekly Business Review: one weekly rollup across Upwork
  (proposals, connects, spend, viewed, interviews, hired), outreach volume from the
  LinkedIn/Instagram/Facebook CRMs, content performance via Buffer (posts + per-platform
  impressions/reach/reactions/comments), ProductivityHub completed tasks, and a website
  section (phase 2). Prints a text summary and writes a JSON snapshot rendered by the
  projects/weekly-business-review dashboard. Use whenever the user says "weekly business
  review", "run the WBR", "weekly review", "weekly stats", "how did this week go",
  "how was my week", "business review", "weekly report", or asks for their weekly
  numbers across Upwork/outreach/content.
---

# Weekly Business Review

One command rolls up the week (ISO Mon-Sun) from every wired source and writes a
snapshot the dashboard reads. Each source degrades gracefully — a failing source
becomes an "unavailable" section, never a crash.

## Run it

```bash
cd .claude/skills/weekly-business-review/scripts
python wbr.py                    # current week -> summary + snapshot
python wbr.py --week 2026-07-13  # any date inside the target week
python wbr.py --no-write         # summary only
```

Snapshot goes to `projects/weekly-business-review/data/weeks/<monday>.json`.
Re-running a week overwrites its snapshot (idempotent).

## Dashboard

```bash
cd projects/weekly-business-review
npm run dev      # http://localhost:3000
```

Overview: header + week selector, then Upwork / Outreach / Content /
Productivity / Website cards with week-over-week deltas. Each card drills into a
detail route that carries the selected week:

- `/upwork` — every proposal with its outcome (hired / interview / viewed / no response), sorted wins-first
- `/outreach/<channel>` — the full per-channel lead list (name, company, role, type, status, profile link)
- `/content/<platform>` — every post with its complete metric set + platform totals
- `/productivity` — the full task log + a by-category bar breakdown

Snapshots carry the item-level data (`upwork.items`, each channel's `leads`,
`content.posts`, `productivity.tasks`), so the detail pages need no extra fetch.
Generate a missing week with `wbr.py --week`.

**Live at:** https://weekly-business-review-nine.vercel.app (Vercel prod deployment,
project `qubit1010s-projects/weekly-business-review`).

## Refreshing the live dashboard

The Vercel deployment is static per-deploy — it can't pull live data itself, since
`gws` (Google auth), the Supabase CLI, and `.env` only exist on this machine. One
command does both steps:

```bash
cd projects/weekly-business-review
npm run refresh                  # current week: wbr.py -> vercel deploy --prod
npm run refresh -- --week 2026-07-13  # a specific week instead
```

(`refresh.py` under the skill's `scripts/` runs `wbr.py` then `npx vercel deploy
--prod --yes` from the dashboard folder.) Do this weekly, or whenever a week's
data needs updating on the public URL.

## Sources (and their honest limits)

| Section | Source | Notes |
|---|---|---|
| Upwork | Proposals Timeline sheet | Full funnel. Spend = connects x $0.15 (`config.UPWORK_CONNECT_USD`) |
| Outreach | 3 CRM sheets | Sent-volume only — CRMs track New/Sent; replies/closes aren't recorded anywhere |
| Content | Buffer GraphQL API | Only posts published through Buffer; metrics differ per platform |
| Productivity | ProductivityHub Supabase | Live. `task_entries` scoped to `PRODUCTIVITY_USER_EMAIL` (project is multi-user; service_role sees everyone) |
| Website | — | Phase 2: GA4 + Search Console + MailerLite not wired yet |

Sheet IDs and constants live in `scripts/config.py`. Buffer auth = `BUFFER_API_KEY`
in the repo `.env` (works as a Bearer token on `api.buffer.com/graphql` — the old
REST API rejects it; don't "fix" the client back to `api.bufferapp.com`).

## Typical asks

- **"Run the weekly review" / "how did this week go"** — run `wbr.py`, present the
  summary conversationally, lead with what moved vs last week.
- **"Show me week X"** — `wbr.py --week <date>`, any date inside that week.
- **"Open the dashboard"** — `npm run dev` in `projects/weekly-business-review`.
- **A specific number dispute** — the sheet is ground truth; check the source tab
  (see `references/how-it-works.md` for column mappings) before blaming the rollup.

## Gotchas

- `gws` must be authenticated (hassanaleem86@gmail.com) — sheet reads shell out to it.
- Upwork dates are D/M/YY; CRM `Date Added` is ISO. Parsers in `scripts/weekutil.py`
  (has a `python weekutil.py` self-check).
- "Date Added ≈ send date" for CRM Sent rows — leads-to-crm adds + sends in one run.
- Buffer week window is UTC.
