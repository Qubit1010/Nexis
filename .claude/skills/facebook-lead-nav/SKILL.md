---
name: facebook-lead-nav
description: >
  Enriches the "Instant Facebook Leads" Google Sheet by turning Facebook group POST
  links into the post author's canonical PROFILE URL. Column A holds group post URLs
  (facebook.com/groups/{id}/posts/{id}/); for each not-yet-enriched row this drives a
  logged-in Chrome via playwright-cli to open the post, find the author, drill to their
  profile (the "View profile" step), and write Lead Name + Profile URL + Date Added back
  to the row. This is the SOURCING step that feeds the leads-to-crm skill (Facebook
  channel). Use this skill whenever Aleem wants to get/collect/scrape Facebook profile
  URLs from group posts, enrich or fill in the Instant Facebook Leads sheet, resolve who
  posted in a group, or run the Facebook lead navigation. Trigger on: "enrich the facebook
  leads", "get the profile urls from the facebook posts", "fill profile urls in Instant
  Facebook Leads", "resolve facebook post authors", "scrape facebook group post profiles",
  "run the facebook lead nav", "turn these facebook post links into profiles", "who posted
  these facebook posts". Do NOT trigger for pushing rows into a CRM or writing outreach
  messages (that is leads-to-crm), for Instagram/LinkedIn sourcing, or for live
  DM-reply / objection drafting (that is sales-playbook / marketing-advisor).
---

# Facebook Lead Navigation (post → profile enrichment)

Group posts give you a person worth reaching, but the post link isn't the person — you
need their **profile URL** to work the lead. Doing that by hand (open post → click the
author → View profile → copy the URL → paste into the sheet) is slow and repetitive.
This skill automates exactly that, faithfully reproducing the manual flow in
`references/Facebook Group Leads Navigation New.mp4`.

It only **sources** profile URLs. Once they're in the sheet, the **`leads-to-crm`** skill
routes them into the CRM and writes the Touch-1 message. Keep that separation: this skill
moves nobody into a CRM and writes no outreach copy.

## What it does

For each row in the target sheet whose **column A is a group post link** and whose
**Profile URL cell is still empty**:

1. Open the post in the attached Chrome.
2. Find the **post author** (not a commenter).
3. Resolve the author's **canonical profile URL** — vanity (`facebook.com/{username}`)
   preferred, `profile.php?id={uid}` as fallback.
4. Write **Lead Name**, **Profile URL**, **Date Added** to new columns on that row.
   Column A (the post link) and existing columns are left untouched.

It is **resume-safe / idempotent**: rows that already have a Profile URL are skipped, so
re-running continues where the last run stopped. Default cap is 10–20 posts per run.

## Prerequisites — run preflight first

Two things must be true, and a helper sets them up:

```bash
node .claude/skills/facebook-lead-nav/scripts/preflight.mjs
```

Preflight checks/handles:
- **`gws` auth** — the Google Workspace CLI must have a valid token (it reads/writes the
  sheet). If expired it tells you to run `gws auth login` (sign in as hassanaleem86@gmail.com).
- **A dedicated CDP Chrome on :9222, logged into Facebook** — it launches the dedicated
  profile Chrome if it's down, and tells you to log into Facebook once if needed. Important:
  the in-browser "Allow remote debugging for this instance" toggle does **not** work with
  Playwright — Chrome must be started with the `--remote-debugging-port` flag (preflight does
  this). See `references/setup-and-troubleshooting.md`.

Preflight prints `READY ✓` or `NOT READY ✗` with the exact fix.

## How to run

Always dry-run first — it resolves and prints the table but writes nothing:

```bash
cd .claude/skills/facebook-lead-nav/scripts
node facebook-lead-nav.mjs --dry-run --limit 3      # preview
node facebook-lead-nav.mjs --limit 15               # live, conservative batch
```

### Flags

| Flag | Default | Meaning |
|---|---|---|
| `--limit N` | 15 | Max rows to enrich this run (keep 10–20 for low detection risk) |
| `--dry-run` | off | Resolve + print only, no sheet writes |
| `--start-row N` | 2 | Skip sheet rows below N (1-based) |
| `--spreadsheet ID` | Instant Facebook Leads | Target spreadsheet (or env `FB_LEADS_SHEET_ID`) |
| `--tab NAME` | `Sheet1` | Target tab (or env `FB_LEADS_TAB`) |
| `--cdp URL` | `http://localhost:9222` | CDP endpoint of the attached Chrome |
| `--delay-min/--delay-max MS` | 3000 / 8000 | Randomized delay between posts |

A typical session: `preflight` → `--dry-run --limit 3` → `--limit 15` → repeat the live
run until a dry-run reports `Found 0 post row(s)`.

## How resolution works (two strategies)

Facebook obfuscates post markup, so there are two paths — the script tries the fast one,
then falls back. Full detail + the DOM signals are in
`references/navigation-and-selectors.md`; read it before changing any selectors.

1. **Clean link (most posts):** the author appears as a `/groups/{gid}/user/{uid}/` link in
   the post header. Open that user's group page and read the vanity / "View profile" URL.
2. **Hovercard fallback (obfuscated posts):** the header author link is scrambled
   (`?__cft__…`, shuffled name text). Hover the author actor to spawn the profile hovercard,
   then read the canonical profile link it injects.

Rows where neither yields an author (deleted post, author left the group) are reported as
**needs review** and skipped — nothing wrong is written.

## Output (sheet shape)

New columns added by header name (never by fixed position), to the right of existing data:

| Lead Name | Profile URL | Date Added |
|---|---|---|

The lead's name goes in a **new** "Lead Name" column rather than the existing "Name"
column, because for these post rows "Name" holds the post-text snippet, not a person.

## Terms of Service / safety

Group-member scraping is against Facebook's ToS and Facebook actively detects automation.
This is intended for low-volume, authorized first-party lead-gen: it reuses a real
logged-in session, processes 10–20 posts per run, and waits 3–8s between posts. Keep
volumes conservative; don't remove the delays.

## Hand-off & follow-ups

- **Next step for these leads:** the `leads-to-crm` skill (Facebook channel) consumes the
  enriched rows. The Profile URL (vanity slug or `uid`) is the stable dedup identity it
  keys on. Wiring `FacebookChannel` into `leads-to-crm/scripts/channels.py` is the open
  follow-up.
- **Optional later:** a feed-driven mode that scrolls a live group and collects new
  `/posts/` links automatically (today the post links are sourced manually into column A).
