# LeadQ

Lead intake and qualification for one operator. A public form captures enquiries, a rule set
you control scores each one, and a private dashboard ranks them for triage.

## Run it

```bash
npm install
cp .env.example .env.local     # then fill in ADMIN_PASSWORD and SESSION_SECRET
npm run dev                    # http://localhost:3000
```

Without a `.env.local` it still starts, using development defaults and printing a warning.
Do not expose it to the internet in that state.

| Route | Who | What |
|-------|-----|------|
| `/` | public | The intake form |
| `/login` | you | Password sign-in |
| `/dashboard` | you | The triage ledger |
| `/dashboard/rules` | you | The scoring rules |

Production:

```bash
npm run build
npm start                      # also :3000
```

## Environment

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `ADMIN_PASSWORD` | yes in production | `changeme` (warns) | The single operator password |
| `SESSION_SECRET` | yes in production | dev value (warns) | HMAC key for the session cookie |
| `LEADQ_DB_PATH` | no | `data/leads.db` | Where the SQLite file lives |

## How scoring works

Every rule that matches a lead adds its points. Points can be negative. The total is capped
at 0-100, then bucketed into hot / warm / cold by two thresholds you set.

A rule is `field` + `operator` + `value` + `points`:

| Field | Sensible operators |
|-------|--------------------|
| Budget (number) | is at least, is at most, is, is not |
| Timeline | is, is not, is one of |
| Services (list) | contains, is one of, is at least (counts how many they picked), is filled in, is empty |
| What they need / Company / Source / Email (text) | contains, is, is filled in, is empty |

Tiers stack on purpose: a $10k lead matches both "at least 10000" and "at least 5000". That
is why every lead stores a **scoring receipt** showing exactly which rules fired and what
each contributed. Expand a row in the dashboard to see it.

**Saving rules rescores every lead you already have**, inside one transaction, so a lead's
score always reflects the current rules. Status and notes are never touched by a rescore.

The app ships with eleven default rules so it is useful before you configure anything.

## Verify

```bash
npm run typecheck    # tsc --noEmit, strict
npm run lint         # eslint
npm test             # vitest run - 65 tests
```

## Notes and limits

- **The database is a file.** SQLite through Node 24's built-in `node:sqlite`, so there is
  nothing to install and no native module to compile. Node prints an
  `ExperimentalWarning` for that module; the API is stable enough for this use and is
  isolated in `src/lib/db.ts`.
- **Deploy to a container host with a persistent volume** (Railway, Fly, a VPS), not to
  Vercel serverless, because the data is on local disk. Swapping `src/lib/db.ts` for
  Postgres is the escape hatch if that changes; nothing above that module would move.
- **Auth is one shared password**, correct for one person and the first thing to replace if
  a second one ever needs access.
- **`data/` is gitignored.** Back it up by copying the file.

## Layout

```
src/
  app/           pages and route handlers (the whole HTTP contract)
  components/    ScoreMeter, StatusPill, Field
  lib/           scoring engine, repositories, auth, db
tests/           vitest suites
.builder/        how this was designed: blueprint, architecture, design system,
                 test plan, review report, decision log
```

`src/lib/scoring.ts` is pure: no database, no request, no framework. That is the piece worth
reading first.
