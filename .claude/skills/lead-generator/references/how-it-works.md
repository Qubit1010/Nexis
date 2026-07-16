# How resolution actually works

Built and live-verified 2026-07-10 against real rows from Aleem's "Instant Google Maps Data"
sheet. Replaces the earlier Apify/SocialCrawl/Hunter.io build (archived at
`archives/lead-generator-apify-2026-07-10/`) after that version's Instagram hashtag-scraping
surfaced low-quality, wrong-geography leads.

## v3 (2026-07-16): website-first, because search-first attached the wrong founder

The v2 flow below resolved the founder by **search first** (query the company + role words, take the top
LinkedIn `/in/` hit). A live-verified batch of ~130 NYC marketing agencies proved that approach
unreliable on exactly the field that matters most for outreach — the founder. Aleem manually verified the
output against live Google searches, the company's own Clutch/website/team pages, and each linked social
profile, and found repeated, severe errors. The failure modes, all real from that batch (company/person
names genericized below to keep real third parties out of this public repo):

- **Same-named stranger.** "Meridian Rank"'s founder came back as "Jamie Rourke," an unrelated notary/mobile-
  business owner, and his unrelated Instagram/LinkedIn/Facebook (three *different* people's profiles) were
  attached to the row. The founder-social follow-up query `"{name} {company} instagram OR facebook"` took
  the first hit with zero check it was the same person.
- **Unrelated current/past role.** "Meridian Rank"'s real candidates were Evan Castell and Marcus Feld —
  Castell's LinkedIn currently reads "Chief Business Officer at Meridian Rank" (he *founded* a different,
  earlier company, Peak Rank). The boolean-OR query `"{company} founder OR owner OR CEO"` matches anyone
  associated with those words, regardless of whether they founded *this* business.
- **Common-word / personal-name company.** "Halstead" (the agency) matched to an unrelated "Halstead Cole"
  purely because the person's name contains the company's name. "Lark Studio" matched to "Priya Anand"
  instead of its real co-founder Sofia Marek. "Vertex360" matched to "Elena Vosk," who is actually
  Co-Founder @ Korvex / Founder @ Nova Digital — a completely different company.

The lesson Aleem drew (and his own method proves): **the company's own website is the reliable source.**
Its footer links the company socials; its About/Team/Contact pages name the founder + their real personal
socials. So v3 inverts the order:

1. **Ensure a website.** Use the row's `Website Link`; else, for a Clutch-only lead, extract the real site
   from the Clutch "Visit Website" redirect (`clutch_resolve.py` — the redirect URL carries the domain in
   its `provider_website`/`u` params; Clutch is Cloudflare-protected so it fetches through the web-scraper
   escalation ladder); else one light reverse-lookup search as a last resort. **Live-verified 2026-07-16:**
   "Vertex360"'s Clutch profile → its own site, which then gave the correct founder Nadia Kastrup
   and all three company socials — the exact row the old flow got wrong.
2. **Scrape that website FIRST** (free tiers only): `scrape_socials.py`'s footer/contact/team pass for the
   company socials, then the web-scraper crawl4ai + llm extraction on About/Team/Contact for the founder's
   name + personal socials from prose. Everything found here is tagged provenance `"website"` and is
   trusted (it's the company's own published claim).
3. **Search only fills gaps.** Company socials the website didn't have → the same combined + per-platform
   queries as v2. A founder the website didn't name → the **fallback** search, using Aleem's own
   natural-language phrasing `"founder of {company} {category} {location}"` (not the boolean-OR shape),
   with a real confidence gate: a candidate passes only if a founder-word sits within ~40 chars of the
   company's distinctive brand token (in either order) — checked against both the raw LinkedIn candidates
   and Tavily's synthesized answer text. Two passing candidates → marked `ambiguous`, not silently picked.
4. **Search-sourced founder fields are NEVER auto-written.** They land in a `needs_review` list on the
   resolve report; `run_batch.py` collects them into a review queue for one-by-one confirmation instead of
   writing them. No regex is bulletproof when the company name is a common word — so the code refuses to
   assert a search-derived founder as fact. The website path (provenance `"website"`) is the only founder
   source trusted enough to auto-write.

Why this is a code change, not just a doc change: through v2, the resolve→write loop lived only in
throwaway `C:\tmp` driver scripts, re-derived per run. A founder-confidence fix built mid-run once lived
only in one such driver and never reached the shipped `resolve.py`, so the next run repeated the bug.
v3 ships that loop as `scripts/run_batch.py`, and the "confirm before writing" bar is enforced there in
code — not left to however a batch happens to be driven.

Everything below documents the v2 search-based method, still used as the gap-fill/fallback layer.

---

## v2 (2026-07-14): the research skill + founder + multi-directory merge + web-scraper fallback

The primary resolution engine is now the **`research` skill** (script-callable, multi-API), not
Claude's built-in WebSearch. WebSearch worked but wasn't scriptable; the research skill fuses
Serper (Google SERP) + Tavily + Exa, and — critically — **Serper/Tavily surface `instagram.com`/
`facebook.com` URLs that Exa's index can't** (see the next section for why). It's also the founder
engine: its **entity mode auto-adds the `site:linkedin.com/in` dork**, exactly the founder query
this skill used to run by hand. The flow, one business at a time (agent confirms the matches):

1. **Phase 0 - merge + dedup** (`scripts/merge_leads.py`): Aleem drops raw leads from several
   directories (Google Maps, Clutch, DesignRush, ...) as one tab each in a single Google Sheet.
   `merge_leads.py` normalizes every tab's headers (a superset `HEADER_ALIASES`), dedups across
   tabs AND against rows already in Main (website domain > phone last-10 > normalized company+city,
   reusing leads-to-crm's `_domain`/`_digits`), and appends only new uniques to the Main tab.
   Idempotent. `--selftest` covers the keying.
2. **Phase 1 - read batch** (`read_batch_main.py`): unchanged (phone clean + geo exclude + skip
   fully-resolved rows). Now also carries existing social/founder values so resolve fills only gaps.
3. **Phase 2 - resolve** (`scripts/resolve.py`, prints a JSON candidate report):
   - Company socials: `research.py --json --depth light --services serper,tavily,exa` on
     `"{company} {location} instagram OR linkedin OR facebook"`, filtered through the shared
     `url_filters.social_profile()` (company LinkedIn pages are KEPT now — the founder's personal
     `/in/` lives in its own column). Per-platform `site:{platform}.com` fallback for any miss.
   - Founder: `research.py --mode entity --depth light` -> a ranked list of person `/in/` candidates
     with name + title snippet. **The agent confirms** which one is the founder (title must tie to
     the business) before it's written; resolve pre-picks the top candidate as a best-guess only.
     Then `"{founder} {company} instagram OR facebook"` for the founder's own IG/FB.
4. **Phase 3 - free-tier website fallback** (`resolve.py --website-fallback`, only if gaps remain):
   fast free http pass first (`scrape_socials.py` footer -> /about/ -> /team/ -> /contact/), then
   escalate a specific About/Team page to the **web-scraper skill's crawl4ai tier** (free, gets past
   the ~1/3 of sites Cloudflare blocks a plain fetch) with `templates/founder_socials_schema.json`
   llm extraction to read a founder NAME out of prose. **Capped at free tiers** — never spends
   Firecrawl/Apify credits per lead. No website? reverse-lookup it via research first (search before
   scrape). Standard pages all miss on a big site -> **report it for a manual look, don't crawl**.
5. **Phase 4 - write** (`write_result_main.py`): writes company IG/LI/FB + `Founder` +
   `Founder Instagram/LinkedIn/Facebook Link` + `Social Search Status` back onto the Main row.
   Results land on the Main sheet only (CRM fan-out is deferred).

Live-verified 2026-07-14: a live agency site -> all 3 company socials, 7 founder candidates (top =
correct co-founder) + his personal IG/LinkedIn/FB; free-tier fallback pulled the same socials
+ a founder from page prose. Runs UNSANDBOXED (research + web-scraper need network). **Sheet I/O
needs a live gws token** — re-auth `gws` if it reports `invalid_grant: Token expired`.

## Why WebSearch, not Exa (still the reason the research skill leans on Serper/Tavily)

Exa (`tools/exa/exa_client.py`, used elsewhere in this repo for research) was the first thing
tried. It's dead for this specific job — which is exactly why the research skill's Serper + Tavily
carry Instagram/Facebook while Exa only helps LinkedIn:

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
(e.g. "Founder/CEO - Anchor Digital Partners", not just someone who once worked there). Real hit
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
this addition (a business site resolved to its own `linkedin.com/company/...` page), which also silently
blocked the team-page pass above from ever running (it only fires when `linkedin` is still empty).
Now rejected the same way the WebSearch pass already rejects it.

**FB/LinkedIn junk patterns backported (same day):** `apify_merge_preview.py`'s junk filters
(`facebook.com/tr` — Meta's tracking-pixel beacon, `2008/fbml`, `profile.php`, `plugins/`,
`linkedin.com/feed|showcase`, `linkedin.com/authwall`) existed only in the Apify merge script, not
in `scrape_socials.py` itself. Live-caught during testing (a business site returned `facebook.com/tr`
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
