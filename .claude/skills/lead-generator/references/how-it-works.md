# How resolution actually works

Built and live-verified 2026-07-10 against real rows from Aleem's "Instant Google Maps Data"
sheet. Replaces the earlier Apify/SocialCrawl/Hunter.io build (archived at
`archives/lead-generator-apify-2026-07-10/`) after that version's Instagram hashtag-scraping
surfaced low-quality, wrong-geography leads.

## Why WebSearch, not Exa

Exa (`tools/exa/exa_client.py`, used elsewhere in this repo for research) was the first thing
tried. It's dead for this specific job:

- `search(query, include_domains=["instagram.com"])` -> HTTP 403, `SOURCE_NOT_AVAILABLE`
- `search(query, include_domains=["facebook.com"])` -> same 403
- An unrestricted query with the platform name in the text never surfaces either domain in
  results either — Exa's index doesn't carry these platforms at all, not just domain-filtered out.
- `include_domains=["linkedin.com"]` **does** work.

A direct website-scrape (fetch the business's own `Website Link`, regex the social hrefs out of
the raw HTML) was tried next and worked when it worked — exact match, zero ambiguity, since
they're the business's own published links. But roughly 1 in 3 real sites tested were behind
Cloudflare-style bot protection that a plain `requests.get` (even with full browser headers)
couldn't get past.

**WebSearch beat both.** One combined query reliably surfaced exact-match profile URLs for all
three platforms in a single call, including on a business whose own website blocked direct
scraping entirely.

## The query patterns

**Primary, all three platforms in one call:**
```
f"{company_name} {city} instagram.com OR linkedin.com OR facebook.com"
```
`{city}` comes from the business's `Experience` column text (e.g. "San Diego, CA"). Take the top
result per domain; reject non-profile URL shapes:
- Instagram: reject `/p/`, `/reel/`, `/explore/`, `/tv/`
- LinkedIn: reject `/posts/`, `/pulse/`
- Facebook: reject `/posts/`, `/photo/`, deep group-post links
- Any platform: reject review/directory sites that just mention the business (Yelp, Clutch,
  BBB, DesignRush, etc. showing up in results means no confident match, not a match)

**LinkedIn-specific, second call, only for LinkedIn:**
```
f"{company_name} founder OR owner OR CEO linkedin.com/in"
```
Necessary because the combined query above finds the company PAGE
(`linkedin.com/company/<slug>`), but `leads-to-crm`'s LinkedIn channel is built for 1:1 connection
notes to a person — its `_li_slug()` (channels.py) only parses `/in/<slug>` URLs, so a company
page gets an empty identity and silently lands in `push.py`'s "Needs Review" bucket instead of
being pushed with a drafted message.

Confidence bar for the person match: their title/snippet must clearly tie them to the business
(e.g. "Founder/CEO - WISE Digital Partners", not just someone who once worked there). Real hit
rate on this query, from the first live batch: 2 of 4 businesses had a clear match. When no
confident person is found, leave LinkedIn unresolved for that business rather than falling back
to the company page — better to skip a channel than send a "connection note" that reads like it's
addressed to the wrong target.

**Team/leadership page pass (added 2026-07-13):** when scrape_socials.py's homepage/contact pass
still leaves LinkedIn empty, it tries `/team/`, `/our-team/`, `/meet-the-team/`, `/about/team/`,
`/about-us/team/`, `/people/`, `/leadership/` specifically. This is where a founder's personal
LinkedIn is actually linked on most agency/small-business sites (headshot + name + icon) — the
homepage footer usually only has the company page, which gets rejected outright now (see below).
Uses BeautifulSoup to pull the name/title text surrounding each `/in/` href into a `context`
string, with a `likely_founder` regex hint (`founder|co-founder|owner|principal|ceo|president`)
— surfaced as `linkedin_candidates`, never auto-written. Confirm the context text before treating
it as resolved, same bar as the WebSearch founder query.

**Company-page rejection (fixed same day):** `scrape_socials.py`'s homepage/contact pass used to
accept `linkedin.com/company/...` into the `linkedin` field with no filter — live-caught testing
this addition (thinkjuice.com resolved to `linkedin.com/company/juice-labs`), which also silently
blocked the team-page pass above from ever running (it only fires when `linkedin` is still empty).
Now rejected the same way the WebSearch pass already rejects it.

**FB/LinkedIn junk patterns backported (same day):** `apify_merge_preview.py`'s junk filters
(`facebook.com/tr` — Meta's tracking-pixel beacon, `2008/fbml`, `profile.php`, `plugins/`,
`linkedin.com/feed|showcase`, `linkedin.com/authwall`) existed only in the Apify merge script, not
in `scrape_socials.py` itself. Live-caught during testing (dtestudio.com returned `facebook.com/tr`
as its "Facebook"). Ported into `scrape_socials.py`'s own filters so both scripts reject the same
junk.

## Phone number cleanup

Instant Data Scraper output sometimes prepends a bullet/middot (`· +1 619-727-6165`). Strip that,
then keep the number only if it starts with `+`. Anything else (`0322 9966458`-style local-format
numbers) gets blanked — these are near-always Pakistani/Indian/other non-internationalized numbers
from this data source, per the pattern Aleem flagged directly, and aren't usable for outreach
without a country code anyway.

## Geo exclusion

The `Experience` column already carries real city/country text straight from Google (e.g. "10+
years in business · San Diego, CA, United States") — no separate location lookup needed. A row
gets dropped entirely (marked `Skipped - geo`, no WebSearch call spent) if that text matches
`leads-to-crm/scripts/push.py`'s existing `SOUTH_ASIA` list — the same list already used
downstream to filter Pakistan/India/Bangladesh/Sri Lanka/Nepal results, just applied here before
any resolution work happens instead of after.

## Note/Bio text fed to message generation

`f"{rating} Google rating. {experience}. {note}"` — written into whichever column each channel's
`source_aliases` maps to `bio` (Instagram/Facebook: `Note`; LinkedIn: `Note` -> `Recent Post`;
Google Maps fallback: `Note`, added this session). `leads-to-crm/scripts/messages.py` already
treats a non-empty `bio` as a personalization signal (picks the "with_signal" archetype pool
instead of "no_signal"), so this is the only lever needed for rating/experience/testimonial to
show up in drafted messages — no message-gen code changes required.
