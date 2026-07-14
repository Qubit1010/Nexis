# Query Craft — operators + keyword formatting

Evidence + citations in `research-synthesis.md` Q2. Google's own "Refine web searches" page is the
authoritative operator list [32]; cheat-sheets aggregate the working 2026 set [21][31][34].

## Build a query from concepts, not sentences
1. Extract the core concepts (2-4). 2. List synonyms/variants per concept. 3. Combine with operators.
Broaden with `OR`/synonyms; narrow with extra terms, `"phrases"`, and `-exclusions` [25][26][30].

## Operators that work in 2026

| Operator | Does | Example |
|---|---|---|
| `"..."` | exact phrase / word order | `"model context protocol"` |
| `site:` | one domain / TLD | `site:linkedin.com/in`, `site:.gov` |
| `-term` | exclude | `jaguar -car` |
| `OR` / `\|` | either term | `(founder OR CEO)` |
| `( )` | group logic | `"acme" (ceo OR founder)` |
| `intitle:` / `allintitle:` | term in title | `intitle:"annual report" 2026` |
| `inurl:` / `allinurl:` | term in URL | `inurl:careers` |
| `filetype:` / `ext:` | file type | `filetype:pdf "pitch deck"` |
| `intext:` / `allintext:` | term in body | `intext:"pricing"` |
| `related:` | similar sites | `related:stripe.com` |
| `AROUND(n)` | proximity (n words apart) | `climate AROUND(3) policy` |
| `*` | wildcard in phrase | `"best * for startups"` |

Retired / unreliable: `+`, `~`, `cache:` [31]. Combine freely — stacking `site:` + `"phrase"` +
`OR` is where dorks earn their keep [39][41].

## High-leverage recipes
- Find a PDF report: `site:company.com filetype:pdf (report OR whitepaper)`
- Find pages a site buried: `site:company.com "keyword"`
- Find discussions: `("keyword") (site:reddit.com OR site:news.ycombinator.com)`
- Competitor lookalikes: `related:competitor.com`
- Recent only: add the year, or use the engine's date filter (`--start-date` on Exa; Serper `tbs`).

## In this skill
Pass dorks verbatim as the `--query` — Serper runs them as-is on Google. For semantic/topical asks
(not exact strings) prefer Exa `neural` instead of stacking operators; operators are for exact,
scoped, Google-shaped retrieval [85][94].
