# Scraping Playbook — techniques that make a scrape work

Practical technique layer distilled from `research-synthesis.md` (Q1 architecture, Q2 anti-bot,
Q4 pagination). Load this when a scrape is getting blocked, returning junk, or you're designing a new job.

## 1. Before writing anything: check for an API
API-first extraction is **10-100x faster, more reliable, often ToS-allowed** where HTML scraping isn't
[Q1 2]. Open DevTools → Network → Fetch/XHR, reload, look for a JSON endpoint feeding the page. If you can
replicate its auth + headers, hit it directly with `http` — no parsing, no browser. This beats every other
method when it's available [Q1 12].

## 2. Match the engine to render complexity
Static HTML → `http`. JS-rendered → `crawl4ai`/`firecrawl`. Hard platform → `apify` actor. See
`engine-selection.md`. Don't default everything to a browser or a premium API — that's the expensive
mistake [Q1 12].

## 3. Resilient selectors (when using `css`)
Stability order [Q1 2]: `id` (`#product-price`) and `data-*` (`[data-testid="price"]`) = high; semantic
HTML (`h1`, `article`, `time`) = medium; framework classes (`.css-3xk23f`, `.tw-mt-4`) = low. **Write
multiple fallback selectors** and take the first that hits. For anything that varies across sites or drifts
often, use `--extract llm` instead (Q3).

## 4. Rate limiting + backoff (the polite-and-unblocked layer)
- **Exponential backoff with full jitter on 429/503** reduces server impact up to **85%** vs constant
  polling [Q2 32]. Pattern: `wait = (2 ** attempt) + random.uniform(0, 1)`.
- **Add jitter to normal pacing too** — one request exactly every 500ms is *easier* to detect than natural
  variance [Q2 30].
- Think **load per target, not requests per script**: five "polite" concurrent jobs on one domain still
  overload it [Q2 33][35]. Cap concurrency per domain.
- Layers [Q2 33][35]: baseline throttle + concurrency cap → per-domain rules → adaptive backoff on error →
  retry discipline (limited, spaced; never instant loops) → monitoring.

## 5. robots.txt + identification
- Fetch + cache `robots.txt` per host before crawling. Stdlib: `urllib.robotparser` (`rp.can_fetch(ua, url)`);
  richer: `protego` [Q2 34].
- `Crawl-delay` is a **binding request**, not a suggestion [Q2 32]. Honour it.
- It's advisory/unenforced but the clearest signal the site published — honour unless you have a compelling,
  documented reason [Q2 34]. Identify your bot honestly (UA + contact) on jobs where you want to stay welcome.

## 6. Getting past anti-bot (escalate, don't hand-roll)
Cloudflare = ~20-22% of the web, **5 simultaneous layers** (IP reputation, TLS JA3/JA4, HTTP/2 fingerprint,
JS challenge, behavioral) — fixing one rarely clears the rest [Q2 19][21]. Don't build a bypass in-process;
**escalate the engine** (`crawl4ai` stealth → `firecrawl` → `apify` residential → `scrapingant` unblocker),
which bundles all five layers [Q2 20].
- **A residential IP is a clean network identity, not a clean request** — most detection is self-inflicted
  (wrong header order, contradictory `Accept-Language`, a `requests` TLS fingerprint) [Q2 24][28].
- **Sticky session for auth/multi-step flows; per-request rotation for stateless fetches.** Rotating IP
  mid-session = instant flag [Q2 24].
- **Probe which layer blocks you** before escalating: `curl` vs `curl_cffi impersonate=chrome` vs a browser,
  same proxy. curl 403 but `curl_cffi` 200 → TLS; both fail but browser passes → JS challenge [Q2 21].

## 7. Pagination + infinite scroll (list crawling)
Three shapes [Q4 61][62][65]: (1) **URL param** (`?page=N`/offset) — cheapest, iterate; (2) **"Load more"** —
replicate the backing XHR or click it in a browser; (3) **infinite scroll** — scroll + wait-for-network-idle
in a browser, or better, find and hit the backing JSON API. **Detect the end** (empty page / repeated
content / missing "next"), never scroll forever [Q4 63].

## 8. Don't trust HTTP 200 — validate content
The #1 silent failure: a login-wall/CAPTCHA page returns 200 with zero records and nobody notices for days
[Q1 9]. Always check the payload has the expected shape/row-count before declaring success; on empty,
escalate the engine.

## 9. Cache fetches; keep raw
Cache each successful fetch by content hash; never re-fetch a success [Q1 8][10]. Keep raw output alongside
cleaned (audit trail for when a selector/rule turns out wrong) — see `extraction-schemas.md` §cleaning.
