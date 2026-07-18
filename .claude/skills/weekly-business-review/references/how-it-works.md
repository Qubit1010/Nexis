# Weekly Business Review — How It Works

## Architecture

```
wbr.py (orchestrator)
  ├─ sources/upwork.py        Proposals Timeline sheet   (gws via sheets.py)
  ├─ sources/outreach.py      3 CRM sheets               (gws via sheets.py)
  ├─ sources/content.py       Buffer GraphQL             (buffer.py)
  ├─ sources/productivity.py  ProductivityHub Supabase   (supa.py) — live
  └─ sources/website.py       phase-2 placeholder
        │
        ▼
projects/weekly-business-review/data/weeks/<monday>.json
        │
        ▼
projects/weekly-business-review  (Next 16 dashboard, reads JSON via fs)
   ├─ /                     overview (5 section cards + WoW deltas)
   ├─ /upwork               per-proposal ledger (outcome pills, wins-first)
   ├─ /outreach/<channel>   full per-channel lead list
   ├─ /content/<platform>   every post + its metric set
   └─ /productivity         task log + by-category bars
```

One computation path (Python), a thin overview + one detail route per section
(all Next server components reading `data/weeks/*.json`). The dashboard never
calls APIs — regenerate a snapshot to refresh it. Weeks are ISO Mon–Sun; the
Monday date is the week key + filename.

Each source keeps item-level rows alongside its aggregates so the detail pages
need no extra fetch: `upwork.items` (one row/proposal + `outcome`), each outreach
channel's `leads[]` (name/company/role/url/type/status), `content.posts[]`
(per-post metrics), `productivity.tasks[]`.

## Column mappings (ground truth per sheet)

**Upwork — "Proposals Timeline"** (id `1mDzFkxBOzvxq6joYO9K86EZim30qeXV11Rjhm4jgQBM`, tab `Sheet1`)
- A `Date` (D/M/YY, day-first), G `Boosted`, I `Connects` (int, sparsely filled),
  J `Proposal Viewed`, K `Interview`, L `Hired`, M `Sender`, N `Invited`.
- Yes-detection is prefix-based (`Yes (1:33pm)` counts as Yes).
- Spend = Σ connects × `UPWORK_CONNECT_USD` (0.15) — there is no dollar column in the sheet.

**CRMs** (LinkedIn `1rJM42…`, Instagram `1xql6…`, Facebook `1Gkbz…`, tab `Leads` each)
- Keyed on `Date Added` (ISO) + `Status`. Status realities: only `New`/`Sent` are used
  (FB also has stray `Find Profile`). LinkedIn's Replied/Interview/Closed columns are
  empty/contaminated — deliberately ignored.
- `Contact Type` (`Founder`/`Company`) exists on IG/FB; counted only when clean.

**Buffer** (`api.buffer.com/graphql`, Bearer = `BUFFER_API_KEY`)
- Org → channels → `posts(filter: {status: sent, dueAt: {start,end}})`, paginated 50/page.
- Per-network metrics as returned (IG: Views/Reach/Reactions/Saves/Shares; FB:
  Impressions/Reactions/Shares/Clicks; LI: Impressions/Reach/Views/Unique Viewers/Watch Time).
- Sums everything except `Eng. Rate`, which is averaged across posts.
- The legacy REST API (`api.bufferapp.com/1`) returns 401 "Public API tokens are not
  accepted" — the GraphQL endpoint is the only working path for this token type.

**ProductivityHub** (its own Supabase project `veuufpiafzglyuwcbaxw`, Singapore —
NOT the sales-playbook project, which only holds `conversations`)
- Keys pulled via the Supabase CLI: `SUPABASE_ACCESS_TOKEN` (PAT) →
  `npx supabase projects api-keys --project-ref veuufpiafzglyuwcbaxw`. The
  service_role key is saved as `PRODUCTIVITY_SUPABASE_KEY`.
- **Multi-user project** (4 users) — the service_role key bypasses RLS and sees
  everyone, so `productivity.py` resolves this account's `user_id` by
  `PRODUCTIVITY_USER_EMAIL` (default hassanaleem86@gmail.com) and filters to it.
  Only Aleem is active, but the filter is load-bearing — never drop it.
- Table `task_entries` (the per-day completed-task log): `title`, `category_id`
  (→ `categories.name`), `is_completed`, `completed_at`, `duration_minutes`,
  `star_rating`. Reports completed count, focused hours (Σ minutes / 60), and
  a category breakdown. (`backlog_items` is the recurring backlog, not used here.)
- Overrides: `PRODUCTIVITY_TASKS_TABLE`, `PRODUCTIVITY_USER_EMAIL`.
  `sources/productivity.py discover()` re-lists tables if the schema changes.

## Known limitations (deliberate, not bugs)

1. **Outreach is volume-only.** Accepted/replied/booked/closed are not recorded in any
   CRM — the sheets would need new columns (offered, declined for v1).
2. **Date Added ≈ send date.** True for the leads-to-crm flow (add + send same run);
   a lead added one week and manually sent the next is counted in its added week.
3. **Buffer only sees Buffer.** Posts published natively don't appear.
4. **Website section is a stub** until GA4/Search Console (OAuth or service account)
   + MailerLite (API key) are wired — phase 2.
5. **Snapshot metrics freeze at generation time.** Engagement accrues after posting;
   re-run `wbr.py --week <that week>` to refresh a week's numbers.

## Phase 2 (when asked)

- GA4 Data API + Search Console: needs OAuth scopes or a service account on the
  nexus-point.co properties. The `GOOGLE_CLIENT_ID/SECRET/REFRESH_TOKEN` trio in
  `projects/upwork-proposal-dashboard/.env.local` is the reusable client — mint a new
  refresh token including `analytics.readonly` + `webmasters.readonly` scopes.
- MailerLite: add `MAILERLITE_API_KEY`, simple bearer REST.
- Personal site: instrument first (GA4 + GSC), then same client.
