---
name: leads-to-crm
description: >
  NexusPoint's outreach lead router. Pushes manually-scraped leads from the
  per-channel "Instant ... Leads" Google Sheets into the matching "NexusPoint ...
  Outreach CRM", generating a personalized Touch 1 message (OpenAI gpt-5.4-mini, with a
  Claude Haiku fallback) for each
  new lead. Handles Instagram, LinkedIn, and Facebook (Facebook profile URLs are
  sourced upstream by the facebook-lead-nav skill). It only pushes rows that are
  genuinely new (identity-based dedup on the @handle / LinkedIn slug / Facebook
  profile slug or id) and never re-pushes or duplicates rows already in
  the CRM, fixing the two long-standing bugs in the old lead-gen pipeline (new rows
  silently dropped, sent rows duplicated). Use this skill whenever Aleem wants to
  move scraped leads into a CRM or run the outreach sync. Trigger on: "push leads to
  CRM", "sync my instagram leads", "sync linkedin leads", "run the instagram push",
  "run the linkedin push", "push the new leads", "update the outreach CRM", "send
  the instant leads to the CRM", "run leads to crm", "dedup the CRM", "fill the blank
  DMs", "any new leads to push", "add facebook leads to the CRM". Also trigger when
  Aleem mentions the Instant Instagram/LinkedIn Leads sheet, the Instagram/LinkedIn
  Outreach CRM, or generating Touch 1 / connection messages for scraped leads.
  Do NOT trigger for requests to scrape, find, source, or enrich leads (Apify, Apollo,
  hashtag scraping, email finding) - sourcing is done manually outside this skill, which
  only moves rows already sitting in the source sheet. Also not for live DM-reply drafting,
  follow-up strategy, or benchmark questions (those are sales-playbook / marketing-advisor).
  This replaces the archived instagram-outreach, linkedin-outreach, cold-outreach
  skills and the projects/lead-gen push pipeline.
---

# Leads to CRM

The current NexusPoint outreach loop, end to end:

1. Aleem **manually scrapes** Instagram / LinkedIn (Instant Data Scraper) into a
   per-channel source sheet ("Instant Instagram Leads", "Instant LinkedIn Leads").
2. This skill reads that sheet, figures out which rows are **genuinely new**,
   writes a personalized **Touch 1 message** for each, and **appends them to the
   matching CRM** ("NexusPoint Instagram/LinkedIn Outreach CRM").
3. It stamps each pushed/known row **"Added"** back in the source sheet so the next
   run skips it.

One engine (`scripts/push.py`) runs every channel off a config block in
`scripts/channels.py`. **Instagram, LinkedIn, and Facebook** are live. Adding a
channel is a config + one identity function, not new pipeline code.

Facebook adds one extra step the other channels don't need: a **preprocessing pass**
that resolves *who* posted before the push (many Facebook leads are group posts whose
URL holds the group, not the author). See "Facebook: group-post resolution" below.

## When to use

Trigger whenever Aleem wants scraped leads moved into a CRM or the outreach synced:
"push the instagram leads", "sync my linkedin leads", "run the push", "any new leads
to push", "dedup the CRM", "fill the blank messages". If he names a channel, use it;
if not, ask which channel (or run both).

## The two bugs this skill exists to fix

The old `projects/lead-gen` pipeline keyed dedup off the raw profile URL and
re-judged every row against ICP filters each run. That caused:

- **New rows never reaching the CRM** — newer scrapes are *post-level* (post/reel
  URLs + "X likes" instead of follower counts). The old code hard-dropped those as
  "invalid URL" / "low followers". This skill does **not** auto-filter; it trusts
  the rows Aleem curated and never silently drops (unresolvable rows are flagged
  "Needs Review" in the sheet).
- **Sent rows getting duplicated** — post URLs collapsed to a useless `.../p` key,
  so a profile already in the CRM didn't match its post URL and got re-added. This
  skill keys on a **stable identity** (Instagram `@handle`, LinkedIn `/in/<slug>`)
  computed the same way for source rows, the CRM set, and the dedup pass. And every
  run cross-checks the CRM, so it's **idempotent**: run it twice, the second run
  appends zero rows.

If you ever touch the dedup logic, keep `channel.identity()` and
`channel.crm_identity()` returning the same key for the same person. That single
invariant is what keeps the CRM clean.

**Self-healing status (`--reconcile-status`, opt-in):** by default a row tagged
"Added" is skipped on sight. Pass `--reconcile-status` to instead verify each "Added"
row against the live CRM: a stale "Added" whose identity isn't actually in the CRM
gets **re-pushed**, and one that no longer resolves is downgraded to "Needs Review".
Use it to repair a sheet whose tags drifted from the CRM (e.g. a freshly-created CRM,
or tags left by an older pipeline). It's opt-in because if you've *intentionally
pruned* leads from the CRM, reconciling would resurrect them — so dry-run it first.

## Prerequisites

- **gws CLI** (Google Workspace CLI) authenticated as hassanaleem86@gmail.com.
  `scripts/sheets.py` locates it automatically (node + run.js on Windows).
- **OPENAI_API_KEY** (primary) and/or **ANTHROPIC_API_KEY** (fallback) for message
  generation. Per lead, `scripts/messages.py` tries OpenAI (`gpt-5.4-mini`) first and
  falls back to Claude (`claude-haiku-4-5`) on any failure (no key, quota, error).
  Keys are read from the environment, then the repo `.env`, then
  `projects/bid-engine/backend/.env`, then `projects/daily-news-brief/.env`. If both
  providers are unavailable (no keys, or both out of quota/credit), the push still
  runs and leaves Touch 1 blank (recoverable; see `--no-messages`).
- Python with `openai` and/or `anthropic` installed (`pip install openai anthropic`).
  A missing package just disables that provider; it never crashes the push.
- **Facebook only:** `FIRECRAWL_API_KEY` + `firecrawl-py` (`pip install firecrawl-py`)
  for the optional author-link backup. Both are optional — without them, Facebook
  resolution falls back to LLM extraction from the scraped Note text.

## How to run

Always start with a dry run so Aleem can see the decision table before any writes:

```bash
python .claude/skills/leads-to-crm/scripts/push.py --channel instagram --dry-run
```

Then the live run:

```bash
python .claude/skills/leads-to-crm/scripts/push.py --channel instagram
python .claude/skills/leads-to-crm/scripts/push.py --channel linkedin
python .claude/skills/leads-to-crm/scripts/push.py --channel facebook
```

For Facebook the push auto-runs the author-resolution pass first. You can also run it
standalone to preview/build the cache before pushing:

```bash
python .claude/skills/leads-to-crm/scripts/facebook_resolve.py --dry-run --limit 15
```

For **Facebook**, the source rows must already be enriched with a profile URL by the
`facebook-lead-nav` skill. Rows that still hold only a group post link (no Profile URL)
resolve to no identity and are flagged **Needs Review** — run `facebook-lead-nav` on them
first, then re-run this push.

Flags:

- `--dry-run` — classify + preview only, write nothing.
- `--no-messages` — push rows with a blank Touch 1 (e.g. if the Anthropic key is
  down). Fill them later by re-running without the flag, or hand the blank rows to
  the **sales-playbook** skill to write by hand.
- `--dedup` — remove duplicate rows already in the CRM (keeps the first of each
  identity). Safe to run anytime; pair with `--dry-run` to preview.
- `--limit N` — cap new pushes; useful for a small first live test.
- `--filter-followers N` / `--exclude-geo` — opt-in ICP guards, **off by default**
  because Aleem curates the source by hand. Only add them if he asks.

## What each row becomes (the decision table)

| Source row state | Decision | CRM write | Source "Include to CRM" |
|---|---|---|---|
| status already "Added" | skip | none | unchanged |
| identity already in CRM | reconcile | none (no dupe) | "Added" |
| new identity, resolves | **push** | append + Touch 1 | "Added" |
| no resolvable identity | needs review | none | "Needs Review" |
| blank row | skip | none | unchanged |

The summary printed at the end counts each bucket. In a healthy run after the
first sync, most rows are "skipped (Added)" or "reconciled", and only the truly
new handles get pushed.

**Facebook adds one CRM-side status:** a group-post lead whose author name we got
but whose profile URL we couldn't resolve is still pushed (so nothing is lost), with
a **blank URL** and **Status = "Find Profile"** in the CRM. Aleem grabs the profile
link before sending. The source "Include to CRM" is still stamped "Added", so re-runs
skip it (the "Find Profile" flag lives only in the CRM).

## Sheet shapes (confirmed live, 2026-06)

Source "Instant ... Leads" (status column **"Include to CRM"**):
- Instagram (tab `Raw`): `Name ("Name (@handle)") | Link | Followers | Note | Location/Designation | Include to CRM`
- LinkedIn (tab `Raw`): `Link | Name | Followers | Note | Designation | Location | Company Name | Include to CRM`
- Facebook (tab `Sheet1`): `Link (group POST url) | Name (post snippet) | Followers | Note | Designation | Location | Company Name | Include to CRM | Lead Name | Profile URL | Date Added`
  — the **Profile URL** + **Lead Name** columns are filled upstream by `facebook-lead-nav`; identity keys off Profile URL, not the post Link.

- Facebook: `Link | Name | Followers | Note | Designation | Location | Company Name | Include to CRM`
  (tab `Sheet1`; the `Designation`/`Location`/`Company Name` columns are noisy for
  group posts — the resolver trusts LLM-extracted role/company instead.)

CRM "NexusPoint ... Outreach CRM" (tab `Leads`, 13 columns). The skill writes by
**header name**, not position, so a column reorder won't corrupt it:
- Instagram: `Name | Username | Company | Role | Instagram URL | Followers | Bio | Touch 1-4 | Status | Date Added`
- LinkedIn: `Name | First Name | Company | Role | LinkedIn URL | Location | Recent Post | Touch 1-4 | Status | Date Added`
- Facebook: `Name | First Name | Company | Role | URL | Location | Recent Post | Touch 1-4 | Status | Date Added` (tab `Sheet1`; note the generic `URL` header)

Column detection is by header, with the Instant-Data-Scraper Name/Link column-flip
handled in `channels.split_url_and_name`. If a sheet's tab name ever changes, the
engine falls back to the first tab automatically.

## Facebook: group-post resolution

Facebook leads come in three URL shapes, classified in `scripts/facebook_resolve.py`:

| URL shape | Author / identity |
|---|---|
| `facebook.com/<slug>/` | the slug |
| `facebook.com/profile.php?id=<n>` | `id:<n>` |
| `facebook.com/<slug>/posts\|videos\|photos/...` | the slug (the page IS the author) |
| `facebook.com/groups/<g>/posts/<id>/` | **resolved author** → else `name:<name>` → else `post:<g>/<id>` |

For group/page posts the author isn't in the URL, so a preprocessing pass resolves it:

1. **LLM-extract** `{name, first_name, role, company, location, profile_url}` from the
   already-scraped `Name` (post title) + `Note` (self-intro) text. OpenAI `gpt-5.4-mini`
   primary → Claude `claude-haiku-4-5` fallback. This is the workhorse — most group
   intros say "Hi, I'm Mary, I run a digital marketing agency...".
2. **Firecrawl** the post URL as a backup to recover the real profile link. Note:
   Firecrawl **blanket-blocks facebook.com** ("Website Not Supported"), so this almost
   always returns nothing; the run detects that and disables it after the first hit to
   avoid burning calls. Pass `--no-firecrawl` to skip it entirely.

Results are cached in `scripts/.cache/facebook_resolved.json` keyed by source URL, so
the LLM work runs **once per URL** (idempotent; re-runs reuse the cache, `--refresh`
rebuilds). The push reads the cache via `FacebookChannel.preprocess()`.

Because Firecrawl can't see Facebook, a large share of group leads resolve to a **name
but no profile URL** → those are pushed as `Status = "Find Profile"` (see the decision
table). Real-profile and page-post leads push as normal `New`. The dedup invariant still
holds: `matt.capala/` (profile) and `matt.capala/videos/...` both key to `matt.capala`.

## Adding another channel

1. In `scripts/channels.py`, add a `<Name>Channel(Channel)` subclass: sheet IDs/tabs,
   the `source_aliases` header map, the `message_style`, and implement `parse_row`,
   `identity`, `crm_identity`, `crm_record` (model on `InstagramChannel`/`LinkedinChannel`).
2. Register it in the `CHANNELS` dict.
3. Add a style to `_STYLE` in `scripts/messages.py` if its tone differs.
4. If the channel needs a resolution/enrichment step (like Facebook), give the channel a
   `preprocess(data_rows, col_map, dry_run=False)` method — `push.py` calls it
   automatically if present. Channels without it are untouched.
5. Test with `--dry-run` before the first live push.

## Message generation

Touch 1 is written by OpenAI `gpt-5.4-mini` (primary), with Claude `claude-haiku-4-5`
as a per-lead fallback if OpenAI fails, grounded in the opener archetypes in
`references/message-archetypes.md` (distilled from the sales-playbook skill, the
canonical source). Messages rotate archetypes per lead, strip em-dashes,
respect the channel length cap, and never pitch. For the full sourced playbook or
to evolve the prompts, read `.claude/skills/sales-playbook/`.
