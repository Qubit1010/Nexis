---
name: api-scout
description: >
  Finds free and public developer APIs by topic or use case, sourced from a local catalog of
  ~1,600 APIs across 51 categories (Animals, Authentication, Blockchain, Business, Cryptocurrency,
  Currency Exchange, Development, Finance, Games, Geocoding, Government, Health, Machine Learning,
  Music, News, Open Data, Programming, Science & Math, Security, Shopping, Social, Sports, Test
  Data, Text Analysis, Transportation, Weather, and more), mirrored from
  github.com/public-apis/public-apis. Each entry includes auth type, HTTPS support, CORS support,
  and a description. Pre-built catalog for instant answers; live Exa AI search as a fallback for
  anything not in the catalog.

  Always trigger this skill when the user wants a free/public API for any task — even if they
  don't say "api-scout" by name. Trigger on: "search free apis for X", "find an api for X",
  "free api for X", "any apis for Y", "is there a public api for X", "look up an api for X",
  "public apis for X", "api scout", "what api should I use for X", "need an api that does X",
  or when scoping a project/integration and a free API would help (weather, currency, geocoding,
  auth, ML, etc.). This is the designated lookup source whenever searching for free APIs by topic
  — check the catalog here before searching the open web.
argument-hint: "[category | api query | 'refresh']"
---

# API Scout

Finds free and public developer APIs for any topic. The catalog is pre-built from
[public-apis/public-apis](https://github.com/public-apis/public-apis) (fast, no API cost) and
live-searchable via Exa AI on demand for anything the catalog misses.

## Categories

Animals, Anime, Anti-Malware, Art & Design, Authentication & Authorization, Blockchain, Books,
Business, Calendar, Cloud Storage & File Sharing, Continuous Integration, Cryptocurrency,
Currency Exchange, Data Validation, Development, Dictionaries, Documents & Productivity, Email,
Entertainment, Environment, Events, Finance, Food & Drink, Games & Comics, Geocoding, Government,
Health, Jobs, Machine Learning, Music, News, Open Data, Open Source Projects, Patent, Personality,
Phone, Photography, Programming, Science & Math, Security, Shopping, Social, Sports & Fitness,
Test Data, Text Analysis, Tracking, Transportation, URL Shorteners, Vehicle, Video, Weather.

This list is broad on purpose — if a query loosely matches one of these (e.g. "stock prices" ->
Finance, "flight status" -> Transportation), go straight to Catalog mode instead of guessing.

---

## Mode Detection

Pick the mode from the user's message:

| Signal | Mode |
|--------|------|
| "find an api for X", "apis for Y", "free api for X", "any apis for [category]" | **Catalog** (fast) |
| "search for [specific/niche api]", "is there an api for [very specific thing]", "look up [tool] api" | **Live Search** (Exa) |
| "refresh", "update the catalog", "rebuild the catalog", "resync from public-apis" | **Refresh** |

When unsure: check the catalog first. It covers ~1,600 APIs, so most requests resolve there.
Only fall back to Live Search if the catalog has 0-1 relevant matches, or the user names a
specific product/service whose API isn't a category match (e.g. "does Stripe have a free tier
API" is really a live lookup, not a catalog category).

---

## Catalog Mode

Read `catalog/apis.md` (path: `.claude/skills/api-scout/catalog/apis.md` from repo root). Find
the matching category section, or scan across categories for keyword matches in the API name or
description if the query doesn't map cleanly to one category.

**Output format:**
```
**[API Name]** — [Category]
- URL: [url]
- Auth: [apiKey / OAuth / No / User-Agent]
- HTTPS: [Yes/No]
- CORS: [Yes/No/Unknown]
- About: [one-line description]
```

Show up to 10 relevant APIs. If fewer than 3 match, supplement with a Live Search automatically —
tell the user "checking Exa for more options...". Prefer surfacing `No`-auth, HTTPS-yes APIs
first when several equally fit the ask — they're the fastest to actually integrate.

If `catalog/apis.md` is missing or empty, tell the user:
> "Catalog not built yet. Say 'refresh the api catalog' to pull the latest list from public-apis — takes a few seconds."

---

## Live Search Mode

Run from the repo root:
```
python .claude/skills/api-scout/scripts/search_api.py --query "[user's query]"
```

With optional category context:
```
python .claude/skills/api-scout/scripts/search_api.py --query "[query]" --category "[category]"
```

Parse the script output and present results inline, in the same output format as Catalog mode
(fill in Auth/HTTPS/CORS as "Unknown — verify at URL" since Exa results won't have these
pre-classified). After showing results, offer: "Want me to add any of these to the catalog?" — if
yes, append a matching entry to `catalog/apis.md` under the right category by hand.

---

## Refresh Mode

Re-pulls and re-parses the public-apis README — takes a few seconds, no external API cost (it's
a plain GitHub fetch, not an Exa search).

Run from the repo root:
```
python .claude/skills/api-scout/scripts/fetch_apis.py
```

When done, confirm: "Catalog updated — [N] APIs across [M] categories. Say 'find an api for X' to browse."

---

## Output Style

Keep it scannable — no paragraphs. Entries like:

**Cat Facts** — Animals
- URL: https://catfact.ninja/
- Auth: No
- HTTPS: Yes
- CORS: Yes
- About: Random cat facts

Group by category when showing 5+ results. For 10+ matches, ask which categories or use cases
matter most before dumping everything. Always mention the auth type up front when the user's
context suggests they want zero-friction integration (a demo, a quick script) — a `No`-auth API
is a materially different lift than one needing OAuth.
