# Recipe: Real-Estate / Investment Data

Turn listing sites into structured property + financial rows (price, beds, baths, sqft, price/sqft,
year built, HOA, taxes, days-on-market) for market and investment analysis.

## Output shape
`templates/realestate_schema.json` — address, price, beds, baths, sqft, lot_size, price_per_sqft,
year_built, property_type, hoa, property_tax, days_on_market, url.

## The anti-bot reality (Q2, Q6 — read first)
Zillow, Redfin, Realtor.com, Trulia, Apartments.com **block free scraping hard** (fingerprinting +
CAPTCHA + legal ToS). Confirmed live: free tiers get a ~1.8KB challenge page, not listings. So:

| Target | Engine | Why |
|---|---|---|
| Zillow | `apify` + `maxcopell/zillow-scraper` | Purpose-built actor returns structured listings past the anti-bot. Router auto-selects it. |
| Realtor / Redfin / Apartments | `apify` + Zillow-family actor | Router maps these to the same actor family. Check Apify Store for a site-specific one. |
| Smaller brokerage / MLS-IDX site that server-renders | `auto` -> `crawl4ai` + `llm` schema | Some regional sites render listings in HTML; LLM schema parses them. |
| A page the free tiers CAN fetch | `--extract llm --schema realestate_schema.json` | Extraction is proven; the hard part is getting the HTML. |

**Do not** hammer a major listing site through the proxy tier to dodge its ToS — that's the case-law
danger zone (Meta v. Bright Data, Q7). Use the sanctioned Apify actor or an official data source.

## Commands (validated)
LLM extraction on a fetchable listings page (proven on the App Brewery Zillow-clone sandbox):
```
python scripts/scrape.py --url "<listings-url>" \
  --extract llm --schema templates/realestate_schema.json --out json --save --outfile listings.json
```
Live test: `appbrewery.github.io/Zillow-Clone/` -> clean rows (address, price, beds, baths, sqft, type).

Zillow via the specialized actor (the production path for the majors) — run the actor directly, since
its input is search URLs + maxItems, not a generic crawl:
```
python -c "from scripts.engines import apify_engine as a; import json; \
print(json.dumps(a.actor('maxcopell/zillow-scraper', \
{'searchUrls':[{'url':'https://www.zillow.com/san-diego-ca/'}],'maxItems':20})['rows'][:3], indent=2))"
```
Rows come back already structured; map them onto the schema fields (the actor's keys are close already).
Check the actor's Apify Store page for the current input shape before a big run — actor inputs change.

## Financial / investment fields
- `price_per_sqft` is often derivable (`price / sqft`) even when not shown — compute it in a post-step.
- HOA, property_tax, days_on_market are inconsistently present; expect gaps and don't fabricate them
  (the LLM prompt forbids inventing values).
- For rental/cap-rate analysis, scrape both for-sale and rental comps, then compute yield yourself —
  the skill gathers data, it doesn't model the investment.

## Legal (Q6, Q7 — read `legal-and-ethics.md`)
- Listing data is often copyrighted/compiled by the MLS; redistribution has real limits.
- Personal data (agent/owner names, contact) is regulated (GDPR/CCPA). Minimize and don't republish.
- Scraping *public* listing facts for internal analysis is the defensible zone; republishing a
  competitor's compiled database is not. Honor robots.txt and ToS.
