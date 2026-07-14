---
name: web-scraper
description: >
  The one powerful web-scraping + structured-extraction skill. Runs five engines behind one router on
  a cheapest-to-most-capable ladder — direct HTTP (free), Crawl4AI (free, self-hosted, Playwright/JS),
  Firecrawl (managed API), Apify (actors), ScrapingAnt (proxy/unblocker, last resort) — auto-escalating
  when a page is blocked and rotating numbered API keys (Apify x4, Firecrawl x2) when one hits its limit.
  Four extraction modes turn any page into well-formatted data: raw markdown, links, deterministic CSS
  schema, or schema-driven LLM extraction (OpenAI structured output) for messy pages. Outputs json / csv
  / jsonl / md with dedup. Purpose-built for three workloads, all live-tested: (1) directory -> clean
  lead rows feeding lead-generator/leads-to-crm, (2) ML/LLM training-data gathering from papers/forums/
  repos into provenance-tagged JSONL, (3) real-estate/investment listing data. Grounded in a research-
  first corpus of 141 cited 2026 sources (references/research-synthesis.md) on scraping architecture,
  anti-bot, extraction, lead-gen, ML-data, real-estate, legal/ethics, and tool selection, with a live-
  query fallback. Use whenever Aleem says "scrape X", "scrape this site/directory", "extract data from
  X", "get me leads from this directory", "turn this listing site into a spreadsheet", "gather training
  data / build a corpus", "scrape real estate listings", "get structured data from a page", "is it
  possible to scrape X", "crawl this site", "scrape with apify/firecrawl/crawl4ai", or describes a
  scraping scenario and asks whether it's doable and how. Hands off target *discovery* to the research
  skill, Google-Maps social resolution to lead-generator, and lead CRM push to leads-to-crm.
argument-hint: [url / directory / scraping scenario]
---

# Web Scraper — multi-engine scraping + structured extraction

The one entry point for "go get this data." Match the target to the cheapest engine that will work,
escalate only when blocked, and return **well-formatted structured data** (json/csv/jsonl/md), not raw
HTML. Problem-first: pick the engine, depth, and extraction mode that fit the target — don't default to
the most expensive tier.

## Built research-first
Every technique below traces to a 2026 source in `references/research-synthesis.md` (141 sources,
`_research/sources.json`). Cite only what the corpus actually covers; if it doesn't cover something,
say so. Pricing/tool facts move fast — verify before quoting them as fixed.

## The engine ladder (cheapest -> most capable)
| Tier | Engine | Cost | Best for |
|---|---|---|---|
| 1 | `http` | free | static / server-rendered pages |
| 2 | `crawl4ai` | free (self-hosted) | JS/dynamic, deep BFS crawl, clean markdown for LLM corpora |
| 3 | `firecrawl` | paid API | reliable managed markdown, `/scrape` `/crawl` `/map`, JS + light anti-bot |
| 4 | `apify` | paid actors | hard platforms with a purpose-built actor (Maps, Yelp, Zillow, IG, LinkedIn) |
| 5 | `scrapingant` | paid proxy | last-resort unblocker (residential proxies + headless) when all else is blocked |

`--engine auto` (default) starts a generic target at `http` and **escalates on a block** (403/CAPTCHA/
empty page -> next tier up). Known hard platforms start at `apify` with a specialized actor (the router
picks it). On a quota/limit error inside Apify or Firecrawl, the engine **rotates to the next numbered
key** before failing (Aleem's policy).

**Apify actor policy (Aleem):** the default actor for generic Apify jobs is `apify/website-content-crawler`.
When the target has a purpose-built actor (Maps `compass/crawler-google-places`, Zillow
`maxcopell/zillow-scraper`, Yelp, Instagram, LinkedIn, ...), the router recommends and uses that instead.

## Extraction modes (orthogonal to the engine)
| Mode | What | When |
|---|---|---|
| `raw` | page markdown as-is | corpora, reading, "just get the text" |
| `links` | all links / sitemap | discovery, crawl seeds, Firecrawl `/map` |
| `css` | CSS-schema -> rows | regular DOM, fast/free/deterministic |
| `llm` | schema-driven LLM -> clean rows | messy/varied pages — the "well-formatted data" answer |

CSS + LLM schema shapes and design tips: `references/extraction-schemas.md`. Ready schemas:
`templates/leadgen_schema.json`, `templates/realestate_schema.json`.

## Context to load first (max 3 refs per invocation)
- Always: `references/engine-selection.md` (which engine/tier for this target).
- Blocked / anti-bot / pagination / rate-limit questions -> `references/scraping-playbook.md`.
- "Get structured fields" -> `references/extraction-schemas.md`.
- One of the three workloads -> the matching recipe (`directory-leadgen.md` / `ml-data-gathering.md` /
  `realestate-listings.md`).
- Legality / PII / ToS in doubt -> `references/legal-and-ethics.md`.

## Workflow
1. **Classify the target.** Known platform (Maps/Yelp/Zillow/IG/LinkedIn) -> apify + its actor. Generic
   -> start cheap, escalate on block. Deep whole-site -> `--depth crawl`.
2. **Pick the extraction mode.** Need clean fields -> `llm` (or `css` if the DOM is regular). Just text
   -> `raw`. Discovery -> `links`.
3. **Run it (UNSANDBOXED — needs DNS + a real browser for crawl4ai):**
   ```
   python .claude/skills/web-scraper/scripts/scrape.py --url "<url>" \
     --extract raw|links|css|llm [--schema <path>] [--engine auto|http|crawl4ai|firecrawl|apify|scrapingant] \
     [--depth page|crawl --pages N --max-depth N] [--out json|jsonl|csv|md] [--dedup <fields>] [--save --outfile <f>]
   ```
   Batch: `--urls <file>` (one URL per line, parallel). Direct actor run: call
   `scripts/engines/apify_engine.py`'s `actor(actor_id, run_input)` (the recipes give the input shape).
4. **Read + present**, leading with the result and where it saved. Note which engine won (`note` shows
   the escalation trail, e.g. `tried=http>crawl4ai`).
5. **Gap?** A specific technique/tool/legal question the refs don't cover -> the live-query fallback
   (`references/notebook-live-query.md`): research it via the `research` skill, then append to the synthesis.

## The three workloads (recipes, all live-tested)
1. **Directory -> leads** (`references/directory-leadgen.md`): directory/Maps/Yelp/Clutch/Expertise ->
   clean lead rows (company, site, phone, socials, category, city) -> `lead-generator` / `leads-to-crm`.
   Live: Expertise.com SD web-design -> 24 deduped leads CSV.
2. **ML data gathering** (`references/ml-data-gathering.md`): papers (arXiv), forums (HN/Reddit/SE),
   repos (GitHub) -> provenance-tagged JSONL corpus. Live: arXiv + crawl4ai README + HN -> 3-line JSONL,
   HN auto-escalated http->crawl4ai.
3. **Real-estate / investment** (`references/realestate-listings.md`): Zillow/Redfin/Realtor via Apify
   actor (they block free tiers); smaller sites via crawl4ai + llm schema. Live: Zillow-clone sandbox ->
   clean rows (address/price/beds/baths/sqft/type).

## "Is it possible to scrape X?" — how to answer
1. Is there an official **API** or dataset? Prefer it (check `api-scout` / `free-tool-scout`). Q1: always
   check for an API before scraping.
2. What renders the data — static, JS, or behind anti-bot? Static -> http; JS -> crawl4ai/firecrawl;
   hard platform -> apify actor; hostile -> scrapingant, and if even that fails, it may not be feasible
   cheaply/legally.
3. Is it **legal/ethical** for this use? robots.txt, ToS, PII, redistribution — `legal-and-ethics.md`.
   Public facts for internal analysis = defensible; republishing a compiled DB or dodging ToS via proxies
   = the danger zone.
4. Give the verdict: engine + extraction mode + rough cost + the legal caveat. If it's not feasible, say
   so and name the sanctioned alternative (official API / Apify actor / licensed dataset).

## Writing rules
- No emojis. No em dashes in body text (use commas/periods) — headings may use them.
- Lead with the result, then how it was obtained. Be honest about gaps, blocks, and field completeness.
- Never fabricate field values — the LLM extractor is instructed to leave missing fields blank; keep it that way.
- Don't quote this category's pricing/vendor/actor facts as fixed — verify (they change constantly).

## Handoffs
- **Discover** which URLs/targets to scrape -> `research` skill (general/entity/scientific), then feed its
  URLs here.
- **Resolve socials** from a business name (not directory-listed) -> `lead-generator` (WebSearch).
- **Push leads to CRM** -> `leads-to-crm`. **Free tool/API/actor lookups** -> the scout skills.
- **Parse scientific PDFs / literature** -> `scientific-agent-skills` (this skill gets the raw text).
- `website-audit-system` keeps its own Firecrawl crawl for audits — untouched.

## Reference map
```
web-scraper/
├── SKILL.md
├── scripts/
│   ├── scrape.py            orchestrator/CLI (router + escalation + extract + formats, parallel)
│   ├── router.py            target classify + escalation ladder + platform actors (self-check)
│   ├── extract.py           raw/links/css/llm extraction (self-check on css)
│   ├── formats.py           json/csv/jsonl/md render + dedup (self-check)
│   ├── _env.py              key loader + get_keys() numbered-key rotation
│   └── engines/
│       ├── base.py          shared result shape, block detection, SSRF guard, error taxonomy
│       ├── http_engine.py       tier 1 (requests + BS4)
│       ├── crawl4ai_engine.py   tier 2 (self-hosted, Playwright, deep crawl)
│       ├── firecrawl_engine.py  tier 3 (managed API, /scrape /crawl /map, key rotation)
│       ├── apify_engine.py      tier 4 (actors, default website-content-crawler, key rotation)
│       └── scrapingant_engine.py tier 5 (proxy/unblocker)
├── references/
│   ├── engine-selection.md      which engine/tier (default load)
│   ├── scraping-playbook.md     anti-bot, rate-limit, pagination, retry, validation
│   ├── extraction-schemas.md    CSS vs LLM schema design + examples
│   ├── directory-leadgen.md     recipe 1
│   ├── ml-data-gathering.md     recipe 2
│   ├── realestate-listings.md   recipe 3
│   ├── legal-and-ethics.md      guardrails (case law, GDPR/EDPB, operating rules)
│   ├── what-not-to-do.md        sourced kill list
│   ├── research-synthesis.md    cited master (Q1-Q8) + Live Query Additions
│   └── notebook-live-query.md   live fallback (self-research via research; NotebookLM optional)
├── templates/  leadgen_schema.json, realestate_schema.json
└── _research/  audit trail: gather.py, sources.json (141), exa/q*.json
```
Keys used (all in repo `.env`): `APIFY_API_KEY`(+_2/_3/_4), `FIRECRAWL_API_KEY`(+_2),
`SCRAPING_ANT_API_KEY`, `OPENAI_API_KEY` (llm extraction), `EXA_API_KEY` (research corpus).
Deps: `crawl4ai` (+`crawl4ai-setup`), `apify-client`, `firecrawl-py`, `beautifulsoup4`, `requests`.
