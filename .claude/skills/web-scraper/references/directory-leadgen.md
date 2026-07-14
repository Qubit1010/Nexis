# Recipe: Directory -> Leads

Turn a business directory, Maps category, Yelp/Clutch/Expertise list, or any "list of companies"
page into clean, deduped lead rows that feed `lead-generator` / `leads-to-crm`.

## Output shape
`templates/leadgen_schema.json` — company, category, website, phone, email, address, city, rating,
instagram, linkedin, facebook. Blank fields are expected on index pages (contact details usually live
on each business's detail page).

## Pick the engine by target
| Target | Engine | Why |
|---|---|---|
| Google Maps category | `apify` + `compass/crawler-google-places` | Maps has no clean HTML; the actor returns structured places (name, phone, site, socials). Router auto-selects it. |
| Yelp | `apify` + `yin/yelp-scraper` | Same — heavy anti-bot, purpose-built actor. |
| Generic directory (Expertise, chamber, "top agencies" list) | `auto` (http -> crawl4ai) | Usually server-rendered; free tiers handle it. LLM schema does the parsing. |
| JS directory that free tiers can't render | escalates to `firecrawl` | Managed render + light anti-bot. |

## Commands (validated)
Generic directory (LLM extraction, deduped by company, CSV out):
```
python scripts/scrape.py --url "<directory-url>" \
  --extract llm --schema templates/leadgen_schema.json \
  --out csv --dedup company --save --outfile leads.csv
```
(Live test: `expertise.com/ca/san-diego/web-design` -> 24 clean deduped web-design leads.)

Google Maps category — use the specialized actor via a direct run (Maps input differs from a URL crawl):
```
# The Maps actor takes search strings, not startUrls. Run it directly:
python -c "from scripts.engines import apify_engine as a; import json; \
print(json.dumps(a.actor('compass/crawler-google-places', \
{'searchStringsArray':['plumbers'],'locationQuery':'San Diego, CA','maxCrawledPlacesPerSearch':30})['rows'][:3], indent=2))"
```
Then feed the rows through the leadgen schema fields (name/site/phone are already structured).

## Enrich detail pages (optional second pass)
Index pages rarely carry phone/site/socials. Collect each business's detail URL first
(`--extract links` or the company `website` field), then scrape those pages with the same schema:
```
python scripts/scrape.py --urls detail_urls.txt --extract llm \
  --schema templates/leadgen_schema.json --out csv --dedup company,phone
```

## Hand off
- Clean phone (keep `+`-prefixed only) and drop South-Asia-geography rows the way
  `lead-generator/scripts/push.py` does before pushing — that skill already owns this. Don't duplicate it.
- Write the CSV where `lead-generator` / `leads-to-crm` expect the "Instant ... Leads" sheet columns,
  or import the CSV into that sheet, then run `leads-to-crm`.
- For Instagram/LinkedIn/Facebook *resolution* from a business name (not directory-listed), that's
  `lead-generator`'s WebSearch job — this skill supplies the raw directory rows, it resolves socials.

## Quality bar (from research Q4)
- Dedup after cleaning, on a stable key (company, or company+phone) — see `formats.dedup`.
- Don't trust a 200: a near-empty or challenge page raises `BlockedError` and escalates. If a directory
  returns rows for page 1 only, it paginates via `?page=N` or infinite scroll — see `scraping-playbook.md`.
- Expect 60-80% field completeness on index pages; the detail-page second pass fills the rest.
