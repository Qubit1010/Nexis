# Engine Selection — which engine for this job

The one thing to get right: **the wrong engine costs 10-50x more or fails outright** (`research-synthesis.md`
Q1 [12]). Lead with the pick, escalate only on block. All engines live behind `scrape.py --engine`;
`--engine auto` (default) runs this table for you.

## Pick by target (lead with this)

| Target | Engine | Why |
|---|---|---|
| Static / server-rendered site, or a discoverable JSON/XHR API | `http` | free, fast; API-first is 10-100x faster than HTML [Q1 2] |
| JS-heavy / SPA, or bulk generic crawl for an LLM corpus | `crawl4ai` | free self-hosted, Playwright render, clean markdown, CSS/LLM extract [Q8 138] |
| Want clean managed markdown, non-Python job, or site-wide URL discovery (`/map`) / `/extract` | `firecrawl` | zero infra, reliable markdown; but blocks social + weak on Amazon/LinkedIn [Q8 127] |
| Hard platform with a purpose-built actor: **Google Maps, Yelp, Instagram, LinkedIn, Zillow/real-estate** | `apify` + specialized actor | ready structured output, strongest anti-bot, best crawl coverage [Q8 128] |
| Generic Apify job (no specialized actor fits) | `apify` (default actor `apify/website-content-crawler`) | Aleem's policy: WCC by default, specialized actor when one fits |
| Everything above blocked (403 / CAPTCHA / empty) and no actor exists | `scrapingant` | rotating residential proxies + JS + CAPTCHA, last resort [Q8 49][132] |

## The decision tree (from Q1 [12])
1. **Is there an API / JSON XHR?** DevTools → Fetch/XHR. If auth+headers are replicable → `http` against
   the JSON endpoint. Cheapest, most reliable, often ToS-allowed where HTML scraping isn't.
2. **Server-rendered, no JS?** → `http`.
3. **JS-heavy / needs render?** → `crawl4ai` (free) or `firecrawl` (managed).
4. **Known hard platform?** → `apify` + the specialized actor (Maps/Yelp/IG/LinkedIn/Zillow).
5. **Google/Bing/Amazon SERP?** → an actor / SERP API regardless of the above.

## Escalation ladder (router auto-escalates on block/empty)
`http` → `crawl4ai` → `firecrawl` → `apify` → `scrapingant`. A "block" = HTTP 403/429, a CAPTCHA/"Just a
moment" challenge page, or an HTTP 200 with empty/near-empty content (the #1 silent failure, Q1 [9]).
Never treat a 200 as success without a content check.

## Cost cheat sheet (2026 corpus — verify before quoting, Q8)
- `http` (self + proxies): **$0-0.20 / 1k** [Q1 12]
- `crawl4ai` self-hosted: **free software, ~$4.85/1k TCO** incl. compute+proxy [Q8 130]
- `firecrawl`: **$16/mo entry, ~$0.83/1k, ~3s** [Q8 130]
- `apify`: **~$0.20-0.30/compute-unit** + actor + proxy passthrough [Q8 126]
- `scrapingbee`/proxy stealth: **~$14.70/1k** [Q8 130]
- Key rotation: Apify (4 keys) and Firecrawl (2 keys) rotate automatically on quota/limit (402/429).

## Extraction is a separate axis (`--extract`, see `extraction-schemas.md`)
Any engine returns HTML/markdown; `--extract llm|css|raw|links` turns it into rows. Use `llm` (schema)
for messy/varying pages (the "well-formatted data" fix), `css` for stable DOMs, `raw` for corpora.

## Key rotation & limits
Both Apify and Firecrawl carry numbered keys in `.env` (`APIFY_API_KEY`..`_4`, `FIRECRAWL_API_KEY`..`_2`).
Engines try them in order and rotate to the next on a limit/quota error, only failing once all are spent.
