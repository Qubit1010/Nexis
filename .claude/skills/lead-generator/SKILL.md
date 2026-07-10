---
name: lead-generator
description: Resolves social media profiles (Instagram, LinkedIn, Facebook) for businesses already sourced via Google Maps (Aleem's manual Instant Data Scraper output), then writes each resolved profile into the matching leads-to-crm Instant sheet so its existing pipeline handles dedup, message drafting, and the CRM push. Use this whenever the user wants to find social profiles for a batch of Google Maps leads, or expand outreach beyond what leads-to-crm already has rows for. Trigger on "resolve socials for these maps leads", "find their instagram/linkedin/facebook", "enrich the google maps leads", "process the maps sheet", "find social profiles for [sheet/business]", or any request to turn a Google Maps business list into outreach-ready leads. Does NOT draft outreach messages or manage the CRM itself — leads-to-crm's push.py owns that once a lead is in an Instant sheet.
---

# Lead Generator

Turns a Google Maps business list Aleem already scraped (Instant Data Scraper — Company Name,
Category, Rating, Experience, Number, Note, Website Link, Google Map Link) into outreach-ready
rows in `leads-to-crm`'s existing Instant sheets. One business in, up to three resolved social
profiles out (Instagram, LinkedIn, Facebook), each written into the exact sheet that channel
already reads.

**What this skill does NOT do:** draft outreach copy, manage the CRM, or decide whether a lead
gets messaged. Once a resolved profile lands in an Instant sheet, `leads-to-crm/scripts/push.py`
takes over exactly like it does for every hand-scraped row today.

## Why this is agent-in-the-loop, not one script

Resolution runs on WebSearch (Claude Code's built-in web search), not a script-callable API —
Exa was tried first and confirmed dead for this: it flatly rejects `instagram.com` and
`facebook.com` (`SOURCE_NOT_AVAILABLE`), and no query phrasing gets around it. WebSearch reliably
resolves all three platforms including businesses whose own website blocks a plain HTTP fetch.
That means you (the agent) do the searching, one business at a time; two small scripts handle the
deterministic I/O around it. Rows are processed one at a time in a session by default — not
parallelized via subagents — so matches can be spot-checked live as they're found.

## The loop

1. **Read the next batch:**
   ```
   python scripts/read_batch.py --sheet-id <id> --tab <tab-name> --limit 10
   ```
   Returns unprocessed businesses as JSON, each with `row`, `company`, `category`, `rating`,
   `experience`, `phone`, `note`, `website`. Already handles, before you see anything:
   - **Phone cleanup:** keeps a number only if it starts with `+` (a real country code); bare
     local-format numbers (e.g. `0322 9966458`) are blanked — Instant Data Scraper mixes these in
     and they're not internationally dialable anyway.
   - **Geo exclusion:** drops a row outright (marks it `Skipped - geo` on the source sheet) if its
     `Experience`/company text matches `leads-to-crm`'s own South-Asia exclusion list — the same
     list `push.py` already filters on downstream, applied here so a bad-geography lead never
     costs a WebSearch call. (The `Experience` column already carries real city/country text from
     Google Maps, e.g. "10+ years in business · San Diego, CA, United States" — that's what this
     matches against, no separate location field needed.)
   - **Resume-safe:** adds/reads a `Social Search Status` column on the source sheet; anything
     already marked gets skipped, so re-running the same sheet only surfaces new rows.

2. **For each business, one WebSearch call:**
   ```
   f"{company} {city} instagram.com OR linkedin.com OR facebook.com"
   ```
   Take the top result whose URL matches each platform's domain. Reject non-profile shapes
   (`/posts/`, `/glossary/`, `/p/`, `/reel/`, or a review/directory site like Yelp/Clutch that just
   mentions the business). No confident match on a platform -> leave it unresolved, don't guess.

   **LinkedIn needs a second, separate query** — the combined query above finds the business's
   LinkedIn COMPANY page, but `leads-to-crm`'s LinkedIn outreach is a 1:1 connection note to a
   person (`_li_slug()` only recognizes `/in/<slug>` URLs; a company page gets no identity and
   silently lands in "Needs Review" instead of being pushed). Run:
   ```
   f"{company} founder OR owner OR CEO linkedin.com/in"
   ```
   and use that person's profile instead, when found with confidence (their name/title clearly
   ties them to the business). About half of real businesses tested had a clear owner/founder
   match this way — when none is found, leave the LinkedIn field empty for that business rather
   than falling back to the company page; an unresolved LinkedIn is better than a wrong-target
   message. (If a company page genuinely gets written some other way, it's not broken — it just
   lands in `push.py`'s existing "Needs Review" bucket for manual triage, same as any lead that
   can't be auto-classified.)

3. **Write what was found:**
   ```
   python scripts/write_resolved.py --business '<json for this row from step 1>' \
       --instagram <url or omit> --linkedin <url or omit> --facebook <url or omit> \
       --source-sheet-id <id> --source-tab <tab-name> --status-col <status_col from step 1>
   ```
   Appends a row into each matched channel's Instant sheet (Instagram/LinkedIn/Facebook), and
   marks the source row's status column `Resolved - <channels>`. A business with **no** confident
   match on any platform falls back automatically to the existing Google Maps/email channel
   (`Fallback - maps/email`) — still outreach-ready, just via the business's phone/website instead
   of a social DM.

   The Note/Bio column each channel gets is `"{rating} Google rating. {experience}. {note}"` —
   `leads-to-crm`'s message generator already treats a non-empty bio as a personalization signal
   (see `messages.py`'s `has_signal` check), so Touch-1 drafts reference the real rating, years in
   business, and testimonial automatically. No `leads-to-crm` changes needed for this beyond the
   one-time `GoogleMapsChannel` bio alias already in place.

4. **Second pass on the leftovers:** businesses WebSearch found nothing for often still publish
   their own social links in their website's footer/contact/about page. Run:
   ```
   python scripts/scrape_socials.py '<json array of businesses with a "website" field>'
   ```
   Fetches the homepage (falling back to `/contact/`, `/about/` etc. if needed) and regexes
   Instagram/LinkedIn/Facebook hrefs straight out of the HTML — same zero-ambiguity logic as the
   old direct-scrape idea, just used as a cheap free secondary pass instead of the primary method.
   **Sanity-check every hit before writing it** — this pass throws real false positives: generic
   `facebook.com/profile.php` links (broken, no ID), `facebook.com/plugins/post.php` (an embedded
   widget, not a profile), `linkedin.com/authwall` (LinkedIn's login redirect, not a profile), and
   occasionally a wholly unrelated cross-linked account from the page. Reject anything that doesn't
   plausibly match the business/founder name. On the first real batch this pass recovered about
   half of the businesses WebSearch missed, once the junk was filtered out.

5. **After a batch**, suggest `leads-to-crm`'s `push.py --channel {channel} --dry-run` per touched
   channel to preview what would move into the CRM next.

## Setup this skill needs

Nothing new. WebSearch is built into Claude Code. Sheets I/O reuses `leads-to-crm`'s existing gws
auth. No API keys to configure.

## Files

```
scripts/
  read_batch.py       — reads the source sheet, applies phone cleanup + geo exclusion, returns
                         the next N unprocessed businesses, tracks resume status
  write_resolved.py   — appends a resolved business into each matched channel's Instant sheet
                         (via sheet_writer.py) and writes the status column back
  scrape_socials.py   — secondary pass: footer/contact/about-page scrape for WebSearch's misses
  sheet_writer.py     — shared low-level writer (unchanged from before, channel-agnostic)
references/
  how-it-works.md     — the WebSearch query patterns, URL-shape validation rules, and the
                         phone/geo cleanup rules, for when a query needs tuning
```

## leads-to-crm change this skill depends on

`GoogleMapsChannel` (`leads-to-crm/scripts/channels.py`) now has a `Note`/`Notes` -> bio alias so
Maps-fallback leads (no resolved social profile) still get a personalized email draft instead of a
blank one. Everything else in `leads-to-crm` is unchanged — Instagram/LinkedIn/Facebook rows
written by this skill flow through the exact same `push.py` pipeline as any hand-scraped row.
