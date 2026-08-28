---
name: seo-technical
description: "Use to AUDIT or FIX the technical SEO layer of a site: whether search engines and AI crawlers can fetch, render, index and trust it. Execution skill that produces the artifact, not the advice skill. Triggers on: technical SEO, technical SEO audit, site audit, crawl my site, crawlability, 'can Google crawl this', robots.txt, disallow, blocked by robots, crawl budget, AI crawler, GPTBot, ClaudeBot, PerplexityBot, 'should I block AI bots', llms.txt, indexation, 'my pages aren't indexed', crawled not indexed, discovered not indexed, sitemap.xml, XML sitemap, lastmod, IndexNow, canonical, self-referencing canonical, duplicate content, 'Google picked a different canonical', parameter URLs, faceted navigation, trailing slash, www vs non-www, http vs https, redirect, 301, 302, redirect chain, redirect loop, 404, 410, soft 404, status codes, 'my 404 page returns 200', site migration, URL map, site architecture, crawl depth, click depth, orphan pages, breadcrumbs, pagination, JavaScript SEO, client-side rendering, CSR, SSR, 'does Google see my JavaScript', 'am I invisible to ChatGPT', raw vs rendered, hydration, mobile-first indexing, mobile parity, Core Web Vitals, CWV, LCP, INP, CLS, PageSpeed, TTFB, 'my site is slow', Lighthouse score, field data, CrUX, structured data, schema markup, JSON-LD, Organization schema, BreadcrumbList, FAQ schema, HowTo schema, rich results, 'is FAQ schema dead', hreflang, international SEO, ccTLD vs subdirectory. Works from a URL, a client-projects slug, or a saved crawl graph. Crawls once and runs nine checks off that one pass, and says 'not connected' rather than inventing Search Console data. Two modes: AUDIT (a prioritized diagnosis) and BUILD (deployable robots.txt, sitemap, redirect map and JSON-LD). Tier 3 only (course sections 21-31). For SEO THEORY, benchmarks or the course use seo-advisor; for KEYWORD research use seo-foundation; for on-page and content use seo-onpage; to WRITE the article use blog-writer; for a prospect-facing sales audit with a hook email use website-audit-system. Off-page, links, local and AI-search execution are out of scope."
argument-hint: [URL, client-projects slug, or a crawl graph - optionally "audit" / "build" / an area]
---

# SEO Technical

Audits or fixes the **technical layer**: whether a search engine or an AI crawler can fetch
the page, render it, store the right URL for it, reach it through the site, and trust the
markup on it.

Two jobs:

1. **AUDIT** a site: a prioritized diagnosis, in tier order, with every claim traced to a
   measurement.
2. **BUILD** the fixes: a corrected robots.txt, a clean sitemap, a flattened redirect map,
   and the two JSON-LD blocks worth having - as files, verified against this skill's own
   rules.

## Where this sits

```
seo-foundation   ->   seo-onpage      ->   seo-technical   ->   blog-writer
 what they search      is the page          can anything         the next
 and which page wins   any good             reach it at all      article
```

`seo-advisor` knows things. This skill does things. It is **Tier 3 of the course - sections
21 to 31 - and nothing else.** Off-page, local and AI-search execution are separate skills
that do not exist yet.

## The thesis: crawl once, check nine times

`scripts/crawl.py` makes one pass over the site and writes a graph. Every other script reads
that graph and makes no requests of its own. A full technical audit therefore costs one crawl,
and re-running it after a fix costs nothing.

`crawl.py` **never renders JavaScript**, deliberately. Comparing raw HTML against rendered
HTML *is* the JavaScript SEO check, so a crawler that silently substituted a render would
report "no rendering problem" on precisely the sites that have one, with the evidence
destroyed at fetch time. `render_diff.py` renders separately, on a sample, on purpose.

## Operating principles

- **Tier order is not negotiable.** A failure at a lower layer invalidates the work above it.
  Fixing schema on a site whose pages are not indexed is polishing something invisible.
  `push_sheet.py` blocks a deliverable that inverts the order.
- **Measure, do not assert.** "Your redirects are messy" is worthless. "`/old-services`
  redirects 302 then 301 to `/services`, and eleven internal links point at the first hop" is
  a work item.
- **Field data or nothing.** Google ranks on CrUX. A page can score 100 in Lighthouse and
  fail the field assessment, so a lab-sourced Core Web Vitals verdict is `unknown`.
- **Floors are not levers.** Core Web Vitals passing buys nothing further. Tell a client
  who is already over the floor to stop.
- **`review` and `unknown` are answers.** A judgment call and a missing data source are both
  real results. Collapsing them into `pass` is how an audit hands a client a confidently
  wrong document.
- **Three findings beat forty.** Ranking ninety check rows down to three fixes is the
  judgment this skill exists to supply, which is why it is not automated.
- **Never invent a fact.** No fabricated `sameAs` URL, no approximated indexation ratio, no
  guessed Google-selected canonical.

## The scripts

| Script | Covers | Cost |
|---|---|---|
| `crawl.py` | the shared graph: robots, sitemaps, every page, origin probes | N requests, cached per origin |
| `technical.py` | course/21-25 + 31 - robots, sitemaps, canonicals, redirects, architecture, hreflang | free |
| `schema.py` | course/30 - JSON-LD, retired types, entity graph | free |
| `vitals.py` | course/27-28 - CWV by template, field-first, course/28's fix order | 1 free PSI call per template |
| `render_diff.py` | course/26 + 29 - raw vs rendered, mobile parity | 2 local renders per sample |
| `push_sheet.py` | the 6-tab Sheet, with 6 blocking invariants | Sheets API |
| `emit.py` | BUILD mode artifacts, self-verified | free |

Every one takes `--selftest`. Run it before concluding a site is broken.

## Running it

```bash
python scripts/crawl.py https://client.com --max-pages 300 --yes
python scripts/technical.py https://client.com --out results/technical.json
python scripts/schema.py     https://client.com --out results/schema.json
python scripts/vitals.py     https://client.com --templates 5 --out results/vitals.json
python scripts/render_diff.py https://client.com --sample 3 --out results/render.json
python scripts/push_sheet.py --from-results results/*.json --validate-only
python scripts/emit.py https://client.com --out client-build/     # BUILD mode
```

`references/method.md` has the full runbook, the cost model and the politeness rules.

## Output

- A **6-tab Google Sheet**: Technical Audit, Findings, Indexation, Redirects, Architecture,
  Core Web Vitals.
- A **report** at `client-projects/<slug>/11-seo-technical.md`, numbered to sit beside
  `09-seo-foundation.md` and `10-seo-onpage.md`. Structured as one-line diagnosis, three
  prioritized fixes, what is fine, and the structural question - see
  `references/report-structure.md`.
- In BUILD mode, a **directory of deployable files** with a README naming the deploy order.

## The honest gap: Search Console

Half of Tier 3 is an indexation question and Search Console is the only thing that can answer
it. There is no credential here - `gws` exposes no Search Console service, verified, not
assumed.

So the indexed-to-submitted ratio, the "Crawled - not indexed" versus "Discovered - not
indexed" split, Google-selected canonical, the soft-404 report, Crawl stats, the Core Web
Vitals report and the Enhancements report all return `not connected` with the manual steps
attached. A crawler reports what it fetched, which is not what Google stored, and presenting
one as the other is the single easiest way for this skill to be confidently wrong.

## Politeness

This is the one skill in the SEO family that hits a site we do not own at volume. The crawler
obeys robots.txt including `crawl-delay`, runs single-threaded with a 0.5s floor, caps at 300
URLs, and refuses more than 50 pages without `--yes`. Do not remove those.

## References

- `references/checks.md` - the threshold contract. Owns every number; the scripts implement.
- `references/method.md` - the runbook, tier order, cost, and the two live-run lessons.
- `references/what-not-to-do.md` - claims this skill must never make.
- `references/report-structure.md` - the deliverable's shape.
- `references/sheet-schemas.md` - the six tabs and the six blocking invariants.

No corpus of its own. Thresholds cite `seo-advisor`'s 320-source corpus by `course/NN` plus
its evidence tier, so the two cannot drift. `[sN]` indices are deliberately not used: they
are not portable between skills, and in seo-advisor's `sources.json` the lookup is by the
`index` field rather than list position.

## Handoffs

| Ask | Skill |
|---|---|
| theory, benchmarks, the course, "is SEO dead" | `seo-advisor` |
| keyword research, clustering, keyword map | `seo-foundation` |
| titles, content, internal linking, E-E-A-T, images | `seo-onpage` |
| writing the article | `blog-writer` |
| a prospect-facing audit with a hook email | `website-audit-system` |
| bulk extraction from a site | `web-scraper` |
