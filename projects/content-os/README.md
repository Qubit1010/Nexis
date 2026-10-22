# Content OS

One local platform for the whole content workflow, from a daily-brief bookmark to a published
post. It replaces the copy-paste chain across the Content Ideas sheet, Topics Ideas, SM Schedule,
in-session skill runs, Google Docs and manual posting.

```
daily brief bookmark ──> Inbox ──> Shortlist ──> Calendar slot ──> headless skill run ──> Review
                                                                                          │
         LinkedIn post: Buffer (publishes even with the PC off) <── Approve ──────────────┤
         Blogs: build, commit, push, deploy, verify live      <──────────────────────────┤
         Newsletter: "ready to post", rich-text copy, mark published  <──────────────────┘
```

Open it at **http://127.0.0.1:4600**. It binds to localhost only.

## Run it

```bash
npm install
npm run build          # the UI
npm start              # server + scheduler on :4600
npm run autostart:install   # start hidden at every Windows sign-in (no admin), and now
```

For development, run `npm run dev` (API on :4600, Vite UI on :5174). Run the tests with `npm test`.

## One-time setup (Settings > Health shows each one)

| Need | Why | How |
|---|---|---|
| Claude CLI sign-in for headless runs | Drafts are `claude -p` runs on the subscription | Recommended: `claude setup-token`, then add `CLAUDE_CODE_OAUTH_TOKEN=...` to `D:\Nexis\.env`. Or run `claude` and `/login`. |
| `BUFFER_API_KEY` | LinkedIn posts are scheduled in Buffer | Buffer > Settings > API: create a key and put it in `D:\Nexis\.env`. |
| Vercel CLI login | Agency blog deploys (its Git integration points at an old repo) | `npx vercel login`, or `VERCEL_TOKEN` in `.env`. |
| Git identity | Site commits | Settings > Git (prefilled from the portfolio repo). |

Content OS never loads `D:\Nexis\.env` into its own environment. It parses the file, strips every
`ANTHROPIC_*` variable from Claude runs (an API key there would bill the API instead of the
subscription), and kills any run whose `apiKeySource` is not a subscription login.

## How the pieces work

- **Capture.** Every bookmark in the daily brief also POSTs to `/api/ideas`. News bookmarks now
  need one click. Ideas dedupe on the normalized URL, or on the title when there is no URL, so
  re-bookmarking bumps "saved Nx" instead of duplicating. The sheet write still happens; if
  either save succeeds the bookmark is kept.
- **Triage.** In the Inbox, `j`/`k` move, `s` shortlists, `a` archives and `p` plans. The
  Shortlist replaces the Topics Ideas tab.
- **Plan.** Put an idea on the calendar with a format, channel, PKT slot and brief. A newsletter
  can be "built from" a blog: it waits until that blog is live and links to it.
- **Generate.** A job runs the format's skill headless from `D:\Nexis`, reads
  `server/engine/prompts/<format>.md` plus the shared `_contract.md`, and writes only into
  `data/runs/<id>/`. The tool guard (`server/engine/hook-guard.mjs`) blocks writes outside that
  folder and every side-effecting command (git, vercel, gws, Docs, Buffer, Kit).
  - Each skill has a `references/content-os-contract.md` saying which steps to skip.
  - Content OS re-runs the hard checks itself: dashes, emojis, agency or university terms in
    personal-brand pieces, the 3,000-character limit, blog frontmatter and `check_issue.py`.
    A failure gets one automatic fix-up turn.
  - "Prepare the week" (daily at 07:00) drafts every planned item in the next 7 days that has no
    draft yet.
- **Review.** Approve, revise with feedback (it revises, not rewrites), edit by hand, compare
  versions as a word diff, restore an old version, or export to a Google Doc.
- **Publish.**
  - LinkedIn: on approval the post goes to Buffer with an exact `dueAt`, so it goes out even
    with the PC off. Images are hosted in a public Supabase bucket because Buffer has no upload
    API. A "Check Buffer" job every 30 minutes marks posts published with their LinkedIn URL.
  - Blogs: at the slot, Content OS pulls, writes the post and images into the site repo, runs
    `npm run build` as the schema gate (rolling back on failure), commits only those paths,
    pushes, deploys (git or Vercel CLI) and polls the live URL before marking it published.
  - Newsletter: it goes to "ready to post" at its slot. Copy rich text, paste it into
    LinkedIn's article editor, then "Mark published" appends the edition's issue log.
- **Scheduling.** There is a 30-second tick, and cron automations use PKT.
  - A missed automation runs once on restart, within its catch-up window, never as a backlog.
  - A blog more than 12 hours late is held as Missed rather than published stale.
  - A Buffer push interrupted by a crash becomes "needs check" rather than being retried blind,
    because a duplicate post is worse than a delay.
- **Sheets.**
  - `npm run import:sheets` (or Settings > Import) reads the Content Ideas tabs, Topics Ideas
    (strikethrough means used) and SM Schedule. It is dry-run first and idempotent.
  - The mirror writes a one-way copy of the schedule to a new tab, "SM Schedule (Content OS)".
    It only takes over the real SM Schedule tab after an explicit cutover.

## Bring in a draft written elsewhere

```bash
node scripts/run-folder.ts prepare <itemId>             # writes the exact prompt + input a run would get
node scripts/run-folder.ts adopt <itemId> <runFolder>    # validates output.json, runs the checks, stores a version
```

## Layout

`server/` has the API (Hono), scheduler, engine, publishers and integrations. `src/` is the UI
(React 19 + Tailwind v4). `test/` is `node --test` against a fake `claude`. Data lives in
`data/`, which is gitignored: `content-os.db` (SQLite, WAL), `runs/`, `assets/` and `logs/`.

## Known limits

- **Instagram, carousels and shorts are not wired yet.** Instagram is paused per current
  priorities. Buffer can carry them later.
- **The newsletter cannot auto-publish.** LinkedIn has no newsletter API.
- **NotebookLM is not installed on this machine,** so post-creator's synthesis step is done by
  the run itself.
- **Agency blog covers are uploaded by hand.** blog-images renders the personal palette.
- **It is single-user and local.** For client deployment the schema ports to Postgres. Generation
  would need an API-backed engine, since `claude -p` on a personal subscription is not a server
  engine. Weigh that against `projects/nexis-growthos`.
