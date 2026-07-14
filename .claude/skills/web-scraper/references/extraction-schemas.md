# Extraction & Schemas — turning HTML into well-formatted data

This is the "well-formatted data" answer to Aleem's complaint about raw custom-HTTP output. Distilled from
`research-synthesis.md` Q3. Extraction is orthogonal to the engine: any engine returns HTML/markdown, then
`extract.py` (`--extract`) turns it into typed rows.

## Pick the extraction mode
| Mode | When | Cost | How |
|---|---|---|---|
| `raw` / markdown | corpora, RAG, "just give me the clean text" | ~free | engine's markdown, boilerplate stripped |
| `links` | URL discovery, sitemaps, "find all listing pages" | ~free | Firecrawl `/map` or crawl4ai link set |
| `css` | **stable** DOM, one known site, high volume | fractions of a penny, 5-50ms/page [Q3 37] | CSS/XPath schema → rows |
| `llm` | **messy/varying** pages, many sites, layout drifts | dollars/page, seconds [Q3 37] | JSON schema + cleaned HTML → LLM → validated rows |

Rule of thumb [Q3 36][39]: **CSS when you tell it *where* (stable structure you own/know); LLM when you tell
it *what* (varies across sites, redesigns often).** CSS is underrated — don't reach for LLM on a stable
government table [Q3 37]. LLM's superpower: one schema often works across Amazon/BestBuy/Walmart unmodified
[Q3 36].

## The schema-driven LLM pipeline (the core of `--extract llm`)
From Q3 [40][45][51], the pattern that produces clean rows reliably:
1. **Fetch** (any engine) → HTML/markdown.
2. **Prune the DOM** — strip nav/ads/scripts/boilerplate. Controls token cost; every token costs money
   [Q3 40]. (crawl4ai/firecrawl markdown already does most of this.)
3. **Send schema + content to the LLM** (OpenAI structured output / latest model). The schema is the
   contract: fields, types, which are optional [Q3 45].
4. **Validate against the schema** — non-negotiable. LLMs are probabilistic: a price comes back as a string,
   a required field missing, a hallucinated value [Q3 45].
5. **On failure, retry with the validation error in the prompt** so the model self-corrects [Q3 40][44].

## Schema design
- **Python: Pydantic `BaseModel`**; TS: Zod. The model documents + instructs + validates simultaneously
  [Q3 45][51].
- Give every field a clear name and type; mark optional fields optional (don't force the model to hallucinate
  a value for a field that isn't on the page).
- Add validators for sanity bounds (e.g. `price > 0`, `price < 1_000_000` catches parse errors) [Q3 51].
- **DOM pruning + a good schema beats a bigger model**: AXE hit F1 88.1% on SWDE with a 0.6B model + pruning
  [Q3 43]; schema optimization (PARSE) gave +64.7% accuracy and −92% errors on first retry [Q3 44][46];
  prompting strategy matters more than model size [Q3 42]. So: prune well, write a precise schema, validate +
  retry — before reaching for a bigger/pricier model.

Schema templates live in `templates/` (`leadgen_schema.json`, `realestate_schema.json`). Pass one with
`--schema <path>`.

## Cleaning (three layers — most of the actual work)
Over **70%** of engineering effort is cleaning, not scraping [Q3 53]; retail dup rates **>25%** [Q3 53];
poor data quality costs ~**$12.9M/yr** avg [Q3 52]. Keep three layers [Q3 48][50]:
- **Raw** — untouched engine output. Keep both `raw_price="£1,299.00 inc VAT"` and `clean_price=1299.00`
  for a debug trail.
- **Normalized** — trim whitespace, fix casing/encoding (decode HTML entities, NFKD unicode, strip
  zero-width chars), standardize dates + currencies + units.
- **Curated** — deduped, validated, analysis-ready.

Per dataset, define four things up front [Q3 50]: **record identity** (what makes a row unique — powers
dedup), **required fields**, **acceptable freshness**, **field ownership** (source vs derived). Order
matters: **dedup too early** collapses distinct items; **enrich before validating** multiplies bad data
[Q3 50]. Attach crawl metadata to every row (source URL, canonical URL, scrape timestamp, job/parser
version) [Q3 50] — `formats.py` does this.

## Output formats
`--out json|csv|md`. `formats.py` normalizes rows, dedupes by the identity key, and writes JSON (default),
CSV (leads/tabular), Markdown table (quick human read), or JSONL (ML corpora, one row per line + provenance).
