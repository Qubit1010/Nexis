# Web Scraping — Research Synthesis (2026)

Cited master doc for the `web-scraper` skill. Every load-bearing claim traces to a real 2026 source.
Inline `[n]` resolves to `_research/sources.json` -> `sources[n-1]` (title + URL). Built research-first
via an Exa full-text pass (`_research/gather.py`, 141 deduped sources across Q1-Q8). Where the corpus
doesn't support a specific number, it says so — **do not invent figures**. This category re-prices and
re-litigates constantly (pricing, actor IDs, case law); verify before quoting to a client.

Question map: Q1 architecture `[1-17]` · Q2 anti-bot `[18-35]` · Q3 extraction `[36-53]` ·
Q4 directory/lead-gen `[54-71]` · Q5 ML data `[72-89]` · Q6 real-estate `[90-107]` ·
Q7 legal/ethics `[108-123]` · Q8 tool comparison `[124-141]`.

---

## Q1 — Scraping architecture & tool selection

**The single most expensive mistake in scraping is picking the wrong tool for the target** — the cost
spread across approaches is 10-50x [12]. There are three primitives, and a real pipeline routes per
target rather than defaulting to one [1][12][14]:

| Approach | Cost / 1k pages | Setup | JS render | Maintenance | Best for |
|---|---|---|---|---|---|
| Direct HTTP + parse (`requests`/`httpx` + BS4/lxml) | $0-0.20 (proxies) | High (headers/auth) | You add it | Medium | static / server-rendered, API-backed [1][12][15] |
| Headless browser (Playwright/Puppeteer) | $0.50-5 (compute) | Low | Built-in | High (browser + fingerprints) | JS-heavy SPAs, interactive/auth flows [1][13][16] |
| Managed scraping API (Firecrawl/ScrapingBee/Apify) | $1-5 | ~10 min | Included | Low (provider absorbs anti-bot) | most projects <1M pages/mo [1][5][14] |

**The decision tree** [12]: (1) **Check for an API / JSON XHR first** — API-first extraction is
10-100x faster, more reliable, and often ToS-allowed where HTML scraping isn't [2]. Watch DevTools →
Fetch/XHR; if you can replicate the auth + headers, call the JSON endpoint directly. (2) Server-rendered,
no JS → direct HTTP. (3) JS-heavy / anti-bot / complex flow → browser or managed API. (4) Google/Bing/
Amazon SERPs → a SERP/actor API regardless of the above [12].

**Production scraping is engineering, not selectors** [10]. The extraction code is the *smallest* part;
everything around it decides whether it survives contact with the real internet [3][10]. Ranked best
practices [2]: (1) check for APIs, (2) match tool to render complexity, (3) rate-limit with delays +
backoff, (4) proxy rotation for blocked targets, (5) schema-validated extraction with retries, (6)
structured metric logging. Resilient selector priority: `id` and `data-*` attributes are stable;
semantic HTML (`h1`, `article`, `time`) medium; framework class names (`.css-3xk23f`) low — write
multiple fallback selectors [2].

**Pipeline shape** (stage-per-concern, shared store) [8][10][11]: Discover (seed/sitemap/search) →
Fetch (cache by content hash; never re-fetch a success) → Parse → Validate (schema) → Store (raw +
curated) → Monitor. A minimal job schema (`target, job_type, url, attempt, max_attempts, parser_version,
trace_id`) enables retry routing + debugging without over-engineering [8]. **Architecture tiers** [3]:
Tier 1 single-process prototype (<10k req/day, requests+BS4+CSV — where most projects correctly live);
Tier 2 production single-node (queue + storage + retries + monitoring; Scrapy/Crawlee); Tier 3
distributed multi-node (shared queue + central proxy pool). Match the tier to the scale, don't build
Tier 3 on day one [3].

**The 5 silent failure modes** [9] — scrapers usually degrade quietly, they don't crash: (1) silent
empty results (a login-wall/CAPTCHA page returns HTTP 200 with zero records), (2) schema drift (selectors
still match but return garbage/nulls), (3) IP burnout with no escalation tier, (4) no alerting, (5)
schedule overlap (a slow run collides with the next). The fix is a stack of defensive layers, not better
selectors: output validation, tier-escalating retry, drift detection, alerting, idempotent scheduling,
and a managed API layer that abstracts proxy/fingerprint upkeep [9].

**Python library defaults** [15]: `requests`+`BeautifulSoup` for static HTML; `Playwright` for JS;
`Scrapy` for scale; `httpx`+`selectolax` for fast async parse. "The escape hatch: when the right answer
stops being 'pick a library' and starts being 'use an API'" [15].

Sources: [1][2][3][4][5][6][7][8][9][10][11][12][13][14][15][16][17].

---

## Q2 — Anti-bot / anti-blocking

**Cloudflare is the most common blocker in 2026** — 24M+ active sites, ~20-22% of all websites [19][22].
It is not one system but **five simultaneous layers**, and fixing one rarely clears the rest [19][20][21][23]:

| Layer | Signal checked | Beaten by |
|---|---|---|
| IP reputation | datacenter/VPN/known-scraper ASN | residential / mobile proxies |
| TLS fingerprint (JA3/JA4) | `requests`/`httpx`/`axios` have distinct TLS ClientHello | browser TLS via `curl_cffi` / `tls-client`, or a real browser |
| HTTP/2 fingerprint | frame order, SETTINGS, pseudo-headers | `curl_cffi` impersonation / real browser |
| JS challenge (Managed/Turnstile) | in-browser proof-of-work + env checks | stealth Playwright; `cf_clearance` cookie |
| Behavioral | request rate, mouse/scroll, timing | human-paced navigation |

Key operational truths from the corpus:
- **A residential IP buys a clean network identity, not a clean request** — most residential-proxy
  detection is self-inflicted at the config layer (contradictory `Accept-Language`, wrong header order,
  a `requests` TLS fingerprint) [24][28]. Changing your IP is not changing your identity [28].
- **Match rotation to the task** [24][26][27]: per-request rotation for stateless fetches; a **sticky
  session** (one IP held) for multi-step/auth flows. Rotating IP mid-session teleports an authenticated
  session to a new address = instant flag [24]. `cf_clearance` binds to IP + fingerprint; rotating IP
  without re-solving the challenge fails [21].
- **Probe which layer blocks you** before building: compare `curl` vs `curl_cffi impersonate=chrome` vs
  Playwright through the same proxy. Plain curl 403 but `curl_cffi` 200 → TLS was the bottleneck; both
  HTTP clients fail but Playwright passes → it's the JS challenge [21].
- Managed unblockers (Apify proxy, Bright Data, ScrapingAnt, ScrapingBee) bundle all five layers so you
  don't hand-roll them [20] — this is why the router escalates to a paid unblocker rather than fighting
  Cloudflare in-process.

**Respectful crawling is also anti-detection.** ~50% of all web traffic is non-human (Imperva 2025);
aggressive scrapers get blocked because they behave like a DoS, not because scraping is wrong [32].
- **`robots.txt`**: fetch + cache per host before crawling; stdlib `urllib.robotparser` (`can_fetch`),
  or `protego` for richer parsing [34]. `Crawl-delay` is a binding request, not a suggestion [32].
  Advisory, not enforced — but the clearest signal the site has published; honour it absent a compelling
  reason [34].
- **Exponential backoff with full jitter on 429/503 reduces server impact by up to 85% vs constant-rate
  polling** (AWS Architecture Blog 2015, still the canonical reference) [32]. A scraper that fires
  exactly one request / 500ms is *easier* to detect than one with natural variance — jitter matters [30].
- Layered rate-limit model [33][35]: baseline throttle + concurrency cap, per-domain rules, adaptive
  backoff on error, retry discipline (limited, spaced — not instant loops), monitoring. Think **load per
  target, not requests per script**: five "polite" jobs hitting one domain still overload it [33][35].
- Identify your bot honestly (UA + contact email) on jobs where you want to stay welcome [34].

Sources: [18][19][20][21][22][23][24][25][26][27][28][29][30][31][32][33][34][35].

---

## Q3 — Structured extraction (CSS/XPath vs LLM)

**Two philosophies:** CSS/XPath tells the machine *where* to look; LLM extraction tells it *what* to
find [36]. The trade is enormous — selectors cost fractions of a penny / 1k pages and run in 5-50 ms;
LLM extraction costs dollars per page and takes seconds [37]. Both output JSON; picking wrong wastes
money or engineering time [37].

- **CSS/XPath**: fast, deterministic, free, but **brittle** — tied to a DOM that A/B tests and
  redesigns break silently (returns `None`/nulls) [36][41]. 30 sites = 30 selector sets, each a
  maintenance liability [36]. Still the right answer for stable, well-structured sites (gov databases,
  your own tools) — underrated amid the LLM hype [37].
- **LLM / schema-driven extraction**: describe the output schema, hand it + cleaned HTML/markdown to a
  model, get validated JSON. Resilient to layout drift; one prompt often works across Amazon, Best Buy,
  Walmart, Target unmodified [36][38][39]. Cost: latency, tokens, occasional guesses [39].
- **The four LLM roles in scraping** [39]: selector generation, structured extraction (most practical
  today), content classification, quality validation. Firecrawl `/extract`, Apify AI extract, Diffbot
  expose this as endpoints [39].

**The schema-driven pipeline** (the "well-formatted data" answer) [40][45][51]: Fetch → **prune the DOM /
strip nav+ads+scripts** (controls token cost) → send schema + content to LLM → **validate against schema**
→ on failure, **retry with the validation error in the prompt** so the model self-corrects. Define the
schema with **Pydantic (Python)** or **Zod (TS)**; the schema simultaneously documents, instructs the
model, and validates output [45][51]. Validation is non-negotiable — LLMs are probabilistic and will
emit a price as a string, miss a required field, or hallucinate a value [45].

**Benchmarks / evidence (2026):**
- **PARSE** (Amazon, EMNLP 2025 Industry): schema optimization + reflection extraction → up to **64.7%
  accuracy improvement on SWDE**, **92% fewer extraction errors within the first retry** [44][46].
- **AXE** (Cairo Univ, 2026): DOM pruning lets a **0.6B model hit F1 88.1% on SWDE**, beating larger
  models; Grounded XPath Resolution keeps every extraction traceable to a source node [43].
- **Co-Scraper** (2026): query-aware DOM pruning + Qwen3-8B → **F1 94.78% SWDE, 90.39% reuse** [47].
- **LLMStructBench** (22 models, 5 prompting strategies): **prompting strategy matters more than model
  size** for valid-JSON extraction [42].
- Market context: AI-based web scraping projected to **$3.16B by 2029, 39.4% CAGR** [40].

**Cleaning is most of the work, not an afterthought.** Over **70% of engineering effort** in retail/
marketplace projects is cleaning/validating/integrating, not scraping [53]; duplicate rates frequently
**exceed 25%** in retail monitoring [53]; poor data quality costs organizations an avg **$12.9M/yr**
(Gartner, cited) [52]. Keep **three layers** [48][50]: Raw (untouched, keep both `raw_price="£1,299.00
inc VAT"` and `clean_price=1299.00` for an audit trail), Normalized (trim/casing/encoding/date+currency
standardized), Curated (deduped, validated, analysis-ready). Define per dataset: **record identity**
(what makes a row unique), **required fields**, **acceptable freshness**, **field ownership** (source vs
derived) [50]. Order matters: dedup too early collapses distinct items; enrich before validating
multiplies bad data [50]. Attach crawl metadata to every row (URL, canonical URL, timestamp, job ID,
parser version, source) [50].

Sources: [36][37][38][39][40][41][42][43][44][45][46][47][48][49][50][51][52][53].

---

## Q4 — Directory / lead-gen scraping & pagination

Public web data is a legitimate B2B prospecting source: business directories, Maps, and industry lists
yield name / site / phone / socials / category / location that feed a sales pipeline [56][57][66][68][69].
For NexusPoint this is the front-half of the existing `lead-generator` → `leads-to-crm` flow.

- **Prefer a purpose-built actor for hard platforms.** Google Maps / local-business intelligence and
  B2B-lead actors exist on Apify and return clean structured rows rather than raw HTML
  [54 (b2b-lead-scraper)][55 (Ultimate Local Business Intelligence Scraper)]. This is exactly why the
  skill's Apify policy prefers a specialized actor when one fits.
- **Pagination is the core mechanic of list crawling** [60][61]. Three shapes [61][62][65]: (1) **URL
  patterns** (`?page=N` / offset) — cheapest, iterate the param; (2) **"Load more" buttons** — click or
  replicate the underlying XHR; (3) **infinite scroll** — trigger scroll events in a browser and wait
  for network idle, or (better) find and hit the backing JSON API directly [63][64]. Detect the
  end-of-pages condition (empty page / repeated content / missing "next") rather than scrolling forever
  [63].
- **Data quality is the differentiator for leads** [67][69][71]: dedupe by identity, validate contact
  fields, enrich carefully, and drop wrong-geography / junk rows before they cost outreach credits. The
  house `lead-generator` already encodes this (phone-`+`-only, `SOUTH_ASIA` geo-exclusion, junk social
  filters) — reuse it.

Note: the corpus for Q4 is mostly vendor/how-to content (actor listings, agency service pages); treat
specific actor names as *verify-before-use* — actor IDs and their input schemas change. The load-bearing
claims here (pagination shapes, dedup/quality, prefer-API-over-HTML) are well supported; specific vendor
pricing is not in the returned text.

Sources: [54][55][56][57][58][59][60][61][62][63][64][65][66][67][68][69][70][71].

---

## Q5 — ML / LLM training-data collection

Scraping for datasets is a first-class use case: papers, forums, and repos → a clean, deduped,
**provenance-tracked** corpus, typically emitted as **JSONL** [75][79][82]. Clean LLM-ready **markdown**
(what Crawl4AI/Firecrawl produce) is the preferred shape because it strips boilerplate and uses far fewer
tokens than raw HTML [79][82].

- **Provenance and licensing are the real risk, and they are frequently wrong.** The **Data Provenance
  Initiative** audited dataset licensing/attribution at scale and found widespread mislabeling
  [84][86]; a 2025 follow-up argues **"Do Not Trust Licenses You See"** — compliance needs massive-scale
  lifecycle tracing, not the license string on the dataset card [85]. For every scraped item, **record
  source URL, crawl timestamp, license, and transformation steps** — provenance rules increasingly
  require it [6][88]. This is why the ML recipe writes provenance into every JSONL row.
- **Curation pipeline** (FineWeb/`datatrove`-style) [80]: fetch → extract main text → language/quality
  filter → **dedup (near-duplicate, not just exact)** → PII scrub → shard to JSONL. Deduplication and
  quality filtering are what separate a usable corpus from noise [77][80][82].
- **Source-specific**: arXiv has bulk/structured access — prefer it over HTML scraping (an
  `arxiv-corpus-builder` pattern exists) [89]; Reddit data for training has its own collection tooling
  and **licensing exposure** (Reddit has sued AI labs — see Q7) [87]; forums can be scraped with
  LLM-generated per-forum scrapers [73][74].
- **The "ethical data" framing matters**: there is active work on the largest *ethically-sourced*
  pre-training corpus [77] and dataset-licensing audits under the GQM model [88] — cite openness/consent,
  don't scrape gated or clearly-licensed content for training.

Sources: [72][73][74][75][76][77][78][79][80][81][82][83][84][85][86][87][88][89].

---

## Q6 — Real-estate / investment data

Listing sites (Zillow, Redfin, Realtor.com, Trulia, Crexi for commercial) yield property + financial
fields for investment analysis: **price, beds/baths, sqft, price/sqft, Zestimate, taxes, HOA,
days-on-market, yield/KPIs** [91][92][98]. **Zillow aggressively blocks scrapers** — direct scraping is a
running arms race [95], so the practical 2026 answer is a **purpose-built Apify actor** [90][91]:

- Apify real-estate actors in the corpus: multi-source **Zillow/Realtor/Redfin** [94], a general
  **Real Estate Data API** [93], **Zillow Property Scraper** variants incl. Zestimate + investor KPIs
  [96][98], and **Crexi** commercial yield/off-market + property-details actors [97][101]. (Verify actor
  IDs + input schema before use — these change.)
- Fallback for smaller/regional listing sites: `crawl4ai`/`firecrawl` + **LLM-schema extraction** into a
  fixed property schema, then validate (Q3 pipeline).

**Legality is genuinely contested for this vertical** and needs care [102][104][105]: public listing
*facts* are generally scrapeable, but listing *photos/descriptions* can be copyrighted, MLS/portal ToS
often forbid scraping, and some data is licensed. Treat the legal refs [102][103][104][106][107] as a
"read before a client engagement" gate, and see Q7. Do not present any legality claim as settled — flag
it as jurisdiction- and ToS-dependent.

Sources: [90][91][92][93][94][95][96][97][98][99][100][101][102][103][104][105][106][107].

---

## Q7 — Legal & ethics

Public-data scraping is broadly defensible in the US, but the exposure has shifted from computer-fraud
law to **contracts, copyright, and privacy** [110][111][112]. **State the boundaries, never assert
blanket legality — it is jurisdiction-, data-type-, and ToS-specific.**

- **hiQ v. LinkedIn (9th Cir.)**: scraping *publicly accessible* data does not violate the CFAA — a
  foundational US precedent [118][119][120][121][123]. But hiQ ultimately lost on **breach of contract
  (ToS)** — public ≠ permission [123].
- **Meta v. Bright Data (Jan 2024)**: reinforced that scraping *public* data (logged-out) is defensible
  [126]. **The real 2026 exposure is publisher contracts, not the CFAA**: Reddit sued Anthropic (June
  2025) and Perplexity (Oct 2025) over unlicensed scraping [126].
- **EU / GDPR is stricter for personal data.** The **EDPB Guidelines 03/2026 on web scraping in the
  context of generative AI** [109][114] and **CNIL's legitimate-interest focus sheet** [113] set out
  concrete measures: lawful basis (usually legitimate interest, balanced against data-subject rights),
  data minimization, transparency, and exclusion of special-category data. GDPR/CCPA both bite when you
  collect personal data [115][116][117].
- **Operating rules that keep you defensible** [108][110][112]: (1) scrape only public data; (2) read +
  respect `robots.txt` and ToS, document exceptions with approval; (3) don't scrape behind logins/paywalls;
  (4) minimize + avoid personal/special-category data unless you have a lawful basis; (5) rate-limit so
  you never degrade the target (aggressive scraping can itself be a CFAA/DoS issue) [30][32]; (6) keep
  provenance for anything downstream.

For NexusPoint's actual uses — public business directories for B2B outreach, public listing facts,
public papers/repos for research — this sits in the defensible zone **provided** ToS/robots are honored,
volume stays polite, and personal data is minimized. When a client engagement touches gated or clearly
personal data, escalate to a real read of the legal refs, don't guess.

Sources: [108][109][110][111][112][113][114][115][116][117][118][119][120][121][122][123].

---

## Q8 — Tool head-to-head (Crawl4AI / Firecrawl / Apify / proxy APIs)

The 2026 market split: **purpose-built LLM-ready tools** (Firecrawl, Crawl4AI) vs **general-purpose
platforms retrofitted with AI** (Apify, ScrapingBee, ScraperAPI, ZenRows) [126]. LLM-ready markdown beats
raw HTML for AI pipelines — Firecrawl claims its markdown uses **~67% fewer tokens** than raw HTML [126].

| Tool | Model | Cost (approx, 2026) | Anti-bot | Sweet spot |
|---|---|---|---|---|
| **Crawl4AI** | OSS Apache-2.0, Playwright-backed, self-host | free software; ~$4.85 TCO/1k incl. compute+proxy [130] | you add proxies | self-hosted AI pipelines, high volume, data privacy, lowest cost at scale [124][129][138] |
| **Firecrawl** | API-first (AGPL core, self-host option) | $16/mo entry (3k credits), ~$0.83/1k, ~3s [130][132] | JS + light anti-bot; **blocks social + weak on Amazon/LinkedIn** [127] | quick RAG/markdown, `/scrape` `/crawl` `/map` `/extract` [125][129] |
| **Apify** | actor marketplace (1,500-2,000+) | $39-49/mo, ~$0.20-0.30/compute-unit + proxy [126][131] | **strongest**; residential proxies, most consistent crawl coverage (hit 1000-page limit on every test domain) [128] | hard platforms, pre-built scrapers, scheduling, scale [128][134] |
| **ScrapingBee** | proxy API, raw HTML | $49/mo, ~$14.70/1k stealth [130] | residential proxies + JS render | raw HTML + proxy rotation when you parse yourself [132] |

**When to use each** (the router's basis):
- **Crawl4AI (self-hosted, free)** — default for bulk generic crawling and ML corpora where you control
  infra and want zero per-page cost; multiple CSS/XPath/LLM extraction strategies, clean markdown, crash
  recovery [138][139][140]. Runs local via Playwright (already installed).
- **Firecrawl (managed)** — when you want clean markdown with zero infra, non-Python stacks, or the
  `/map` (URL discovery) and `/extract` (LLM extraction across a site) endpoints [125][129][132]. Note it
  intentionally blocks social media and struggles on the most-protected sites [127].
- **Apify actors** — the answer for tough, structured platforms (Maps, Yelp, Instagram, LinkedIn,
  Zillow) and the most reliable anti-bot; a self-hosted Firecrawl loses the proprietary anti-bot layer,
  so hard targets go to Apify [128][141].
- **Proxy/unblocker API (ScrapingAnt/ScrapingBee)** — last resort when a target blocks Crawl4AI +
  Firecrawl and you don't have an actor: rotating residential proxies + JS render + CAPTCHA solving
  [49][132].
- **"Many teams use both: Crawl4AI for the bulk of pages and Firecrawl for the tough ones. Run a POC on
  your real targets and let success rate + cost decide."** [129] — the skill encodes exactly this as the
  escalation ladder.

Pricing here re-prices constantly (Exa raised capital, tools change plans monthly); every number above
is "as reported in the 2026 corpus," verify before quoting.

Sources: [124][125][126][127][128][129][130][131][132][133][134][135][136][137][138][139][140][141].

---

## Live Query Additions
_Appended by the live-query fallback (`notebook-live-query.md`) when a gap is filled. Format: `### [YYYY-MM-DD] (Q# - Topic) question` then the cited finding + source._
