# How to run a technical audit

The thesis: **crawl once, check nine times.** Every script here reads one graph, so a full
audit costs one pass over the site and re-running it after a fix costs nothing.

---

## The order

Fix in tier order (see `checks.md`). It is course/21's pyramid and it is not negotiable,
because a failure at a lower layer invalidates the work above it. The temptation runs the
other way: schema and speed findings are the easy ones to generate and the satisfying ones to
fix, which is exactly why an automated tool always leads with them.

```
1-2  crawlability, indexation   ->  can this page be fetched and stored at all
3-4  canonicals, redirects      ->  is the right URL the one being stored
5    architecture               ->  can authority reach it
6    rendering                  ->  is the content actually in the HTML
7    performance                ->  is it over the floor
8-9  schema, hreflang           ->  the polish
```

---

## AUDIT mode

```bash
# 1. Crawl once. Everything else reads this.
python scripts/crawl.py https://client.com --max-pages 300 --yes

# 2. The six-area registry. No requests - reads the graph.
python scripts/technical.py https://client.com --out results/technical.json

# 3. Structured data. Also free.
python scripts/schema.py https://client.com --out results/schema.json

# 4. Core Web Vitals by template. One PSI call per template.
python scripts/vitals.py https://client.com --templates 5 --out results/vitals.json

# 5. Raw vs rendered and mobile parity. Two browser renders per sampled template.
python scripts/render_diff.py https://client.com --sample 3 --out results/render.json

# 6. Assemble the sheet.
python scripts/push_sheet.py --from-results results/*.json --validate-only
python scripts/push_sheet.py --payload payload.json --title "Client - Technical SEO Audit"
```

Every script takes `--selftest`. Run it when something looks wrong before assuming the site
is broken.

**Cost.** The crawl is N HTTP requests plus 5 origin probes, delayed at least 0.5s apart and
obeying the target's `crawl-delay`. `technical.py` and `schema.py` are free. `vitals.py` is
one free PSI call per template. `render_diff.py` is two local browser renders per sampled
template. Nothing here is a paid API.

**Politeness.** This is the one skill in the SEO family that hits a site we do not own at
volume. The crawler obeys robots.txt including `crawl-delay`, runs single-threaded, caps at
300 URLs, and refuses more than 50 pages without `--yes`. Do not remove those.

---

## BUILD mode

AUDIT ends at a diagnosis. BUILD ends at files someone deploys.

```bash
python scripts/emit.py https://client.com --out client-build/
```

Writes a corrected `robots.txt`, a clean `sitemap.xml` plus the excluded-with-reasons list, a
flattened `redirects.csv`, `organization.jsonld` and `breadcrumbs.jsonld`, an `hreflang.md`
(corrected set or a written not-applicable), and a `README.md` with the deploy order.

Then it re-runs this skill's own rules against what it just wrote. An audit that ships a
generated robots.txt with no `Sitemap:` line, or a generated sitemap containing a 404, has
shipped the defect it charged to find.

**Nothing is deployed.** These are files in a directory.

---

## Reading the crawl before reading the findings

Three things about the crawl change how every number below it should be read:

- **Did it hit the cap?** `stats.hit_cap` true means every count is a floor, not a total.
  Raise `--max-pages` or say so in the report.
- **How many pages were skipped by robots?** Those URLs were never fetched, so nothing is
  known about their noindex state, their status or their content.
- **Is `graph_version` current?** A cached graph from an older version is recrawled
  automatically. If a check reports `unknown` citing a missing field, recrawl with
  `--refresh`.

---

## The two live-run lessons

Both were false positives caught by running against a real site, and both are now regression
tests. They generalize:

**Parse the structure, not the text.** A flat line scan of robots.txt read PetalBot's
`Disallow: /` as a site-wide block and would have shipped "your site blocks all crawlers" as
the headline finding of a clean audit. User-agent grouping fixed it.

**Compare the semantic thing, not the artifact.** Comparing image `src` between mobile and
desktop reported all 32 images on a homepage as missing, because a responsive CDN bakes the
viewport into the URL. Comparing alt text - which is what course/29 actually asks for - fixed
it. Same class of error: a zero-width-space heading counted as content until it was stripped.

When a finding looks dramatic, check whether the measurement is measuring what the course
asks for before writing it up.

---

## What this skill does not do

- **Migrations.** course/24 has the checklist. Building the URL map is the deliverable and it
  needs backlink and Search Console exports this skill has no access to.
- **On-page and content.** `seo-onpage`.
- **Keyword research and mapping.** `seo-foundation`.
- **Writing the article.** `blog-writer`.
- **Theory, benchmarks, the course, "is SEO dead".** `seo-advisor`.
- **A prospect-facing sales audit with a hook email.** `website-audit-system`.
- **Off-page, links, local, AI search execution.** Not built yet. Tiers 4 and the AI-search
  half of the course remain open.
