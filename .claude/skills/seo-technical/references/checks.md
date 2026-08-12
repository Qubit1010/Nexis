# The check contract

This file owns the thresholds. `technical.py`, `schema.py`, `vitals.py` and `render_diff.py`
implement them. The contract is one-directional: a number moves here first, then in the
script. If they disagree, this file is right and the script is a bug.

Every threshold traces to a section of seo-advisor's course, which carries its own evidence
tier. Those tiers are reproduced here rather than flattened, because the difference between
`[confirmed]` (Google's own documentation or a Google spokesperson) and `[practitioner]`
(the field's working consensus) is the difference between a fact and a strong opinion, and a
client is entitled to know which one they are being handed.

**Citation note.** seo-advisor's corpus is 320 sources with 18 confirmed against 302
practitioner. `[sN]` indices are NOT portable between skills - blog-writer's 83-source corpus
uses the same notation for different sources - and in seo-advisor's `sources.json` the lookup
is by the `index` field, not by list position (`sources[N-1]` is wrong for 256 of 320
entries). This skill therefore cites `course/NN` plus the tier, which is stable, rather than
`[sN]`, which is not.

---

## The tier order

Not a preference. course/21 states it and states that it is not negotiable, because a
failure at a lower layer invalidates the work above it.

| Tier | Layer | Sections |
|---|---|---|
| 1 | Crawlability | 21 |
| 2 | Indexation | 22 |
| 3 | Canonicals and duplication | 23 |
| 4 | Redirects and status codes | 24 |
| 5 | Architecture | 25 |
| 6 | Rendering | 26, 29 |
| 7 | Performance | 27, 28 |
| 8 | Structured data | 30 |
| 9 | International | 31 |

`push_sheet.py` blocks a write that inverts this order. Fixing schema on a site whose pages
are not indexed is polishing something invisible.

---

## 1. Crawlability and robots (course/21)

| Check | Threshold | Tier | Verdict rule |
|---|---|---|---|
| `robots.not_5xx` | must not be 5xx | `[confirmed]` | fail on 5xx. A 5xx stops Googlebot crawling the **entire site** until it resolves. Highest-risk small file on the site. |
| `robots.reachable` | 200, or 404 | `[confirmed]` | 404 is fine and reads as "crawl everything". Anything else fails. |
| `robots.disallow_all` | Googlebot may fetch `/` | - | Asked of the **grouped** parser, never a flat line scan. A `Disallow: /` scoped to one agent is not a site-wide block. |
| `robots.css_js_open` | never block CSS or JS | `[practitioner]` | fail on any rule matching `.css`, `.js`, `/wp-includes`, `/wp-content/themes`, `/assets`, `/static` in the `*` group. |
| `robots.sitemap_directive` | at least one `Sitemap:` | - | fail if absent. |
| `robots.noindex_conflict` | never both Disallow and noindex | `[confirmed]` | `review` when robots was obeyed (the noindex state is unobservable); `fail` under `--ignore-robots` when both are seen. |
| `robots.ai_policy` | a deliberate policy | `[practitioner]` | always `review`. It is a business decision, not a defect. |
| `robots.no_deprecated_agents` | no `anthropic-ai` | `[practitioner]` | fail. Deprecated legacy agent; live ones are ClaudeBot and Claude-SearchBot. |
| `crawl.budget_binding` | binds above ~10,000 pages | `[practitioner]` | `pass` below it. Optimizing crawl budget on a 200-page site is a way of feeling technical while achieving nothing. |

**The disallow + noindex conflict, stated precisely.** Disallowed means Google never fetches
the page. Never fetching means never seeing the `noindex`. If the URL is linked from
anywhere, it can stay indexed as a bare URL with no description, indefinitely. To remove
from the index: allow crawling, use `noindex`. To save crawl budget: `Disallow`, and accept
bare URLs. For most sites the answer is `noindex` and leave robots.txt alone.

**The 2026 AI default.** Block `GPTBot`, `ClaudeBot`, `CCBot`, `Google-Extended`. Allow
`OAI-SearchBot`, `ChatGPT-User`, `Claude-SearchBot`, `PerplexityBot`. Training crawlers and
search crawlers are different bots, and blocking indiscriminately opts the site out of AI
answers while trying to opt out of training. robots.txt is voluntary; real enforcement is
WAF or server-level.

---

## 2. Sitemaps and indexation (course/22)

| Check | Threshold | Tier |
|---|---|---|
| `sitemap.limits` | **50,000 URLs**, **50MB** uncompressed per file | `[confirmed]` |
| `sitemap.only_200` | only 200-status URLs | - |
| `sitemap.no_redirects` | no redirecting URLs | - |
| `sitemap.only_indexable` | no `noindex` | - |
| `sitemap.only_canonical` | self-canonical only | - |
| `sitemap.not_disallowed` | nothing Disallowed in robots.txt | - |
| `sitemap.lastmod` | reflects real change dates | `[practitioner]` |
| `sitemap.split_by_type` | split above ~500 URLs | `[practitioner]` |
| `index.ratio` | above **85%** indexed-to-submitted | `[practitioner]` |

A sitemap is **not a ranking factor** `[confirmed]`. Its value is diagnostic: it is a
statement of intent, and that statement is only useful if it is true. Including junk trains
Google to distrust the whole file `[practitioner]`.

`lastmod` set to today on every URL every day is a recognized bad pattern - it is generated
rather than observed, and it destroys the value of the hint. `priority` and `changefreq` are
ignored; do not spend time on them.

**`index.ratio` is always `unknown` here.** Only Search Console can report what Google
indexed. See "Not connected" below.

---

## 3. Canonicals and duplicates (course/23)

There is **no duplicate content penalty** `[confirmed]`. There is signal dilution, which is
worse because it is silent: links, engagement and relevance split across several URLs,
Google picks one to represent the group and it may not be the one you wanted, and crawl
budget is wasted fetching the same content repeatedly.

| Check | Threshold |
|---|---|
| `canonical.present` | a self-referencing canonical on every indexable page |
| `canonical.absolute` | absolute URLs, never relative |
| `canonical.single` | exactly one per page - multiple tags make Google ignore all of them |
| `canonical.target_200` | targets return 200, not a redirect and not a 404 |
| `canonical.not_homepage` | nothing canonicalizes to `/` except `/` |
| `canonical.noindex_conflict` | canonical or noindex, never both |
| `canonical.links_agree` | internal links point at canonical URLs directly `[practitioner]` |
| `dupe.host_variants` | http, https, www and non-www all resolve to one version |
| `dupe.trailing_slash` | one form only |

**The canonical tag is a hint, not a directive** `[confirmed]`. Google can pick a different
one. The fix when it does is to make every signal agree: tag, internal links, sitemap
inclusion, redirects.

**Tool selection.** Same content, one permanent preferred URL -> 301. Same content, both must
stay reachable -> canonical. Never want it indexed -> `noindex`. Infinite parameters ->
canonical plus a robots disallow on the trap, cleaned up first. Different intents -> rewrite
so they are different. Different languages -> hreflang. **Redirect when you can, canonicalize
when you must.**

**The location-page trap.** Twenty pages identical except for a city name are not twenty
pages. This is a *content* problem wearing a technical costume and canonicals do not solve
it. `dupe.titles` surfaces it as `review`, pointing at course/35.

---

## 4. Redirects and status codes (course/24)

| Check | Threshold | Tier |
|---|---|---|
| `redirect.single_hop` | one redirect, not two | `[practitioner]` |
| `redirect.under_abandon_limit` | fewer than **5** hops | `[practitioner]` |
| `redirect.no_loops` | none | - |
| `redirect.permanent` | 301 for anything permanent | - |
| `redirect.not_to_homepage` | redirect to the closest equivalent page | `[practitioner]` |
| `redirect.links_are_final` | internal links point at final destinations | - |
| `status.404_is_404` | a missing URL returns 404 or 410 | - |
| `status.no_5xx` | none | - |

Each hop costs **100 to 500ms** of latency plus some signal loss, and Googlebot may abandon
chains beyond five hops entirely, so the destination never gets crawled. Chains accumulate
silently: nobody creates a five-hop chain deliberately, it is five people each making one
reasonable change.

A redirect to an irrelevant page is treated as a **soft 404**, so the signal being preserved
is lost anyway. Keep redirects in place indefinitely - external links and bookmarks point at
the old URL forever.

**410 vs 404.** A 404 says "not found" and Google keeps re-checking. A 410 says
"deliberately gone" and drops the URL faster `[practitioner]`. When something was removed on
purpose with no replacement, 410 is the honest answer.

**Migrations** are where sites lose the most traffic in the shortest time, and nearly always
because URLs were not mapped. The three failures that cause most disasters: staging
`noindex` left in production, everything redirected to the homepage, and no URL map. All
three are avoidable with an afternoon of preparation. This skill does not run migrations; see
course/24's checklist.

---

## 5. Site architecture (course/25)

| Check | Threshold | Tier |
|---|---|---|
| `depth.within_3_clicks` | **3 clicks** maximum to any commercial page | `[practitioner]` |
| `depth.not_neglected` | nothing important at **5+** clicks | `[practitioner]` |
| `arch.no_orphans` | every indexable page reachable by link | - |
| `nav.item_count` | about **7** main navigation items | `[practitioner]` |
| `arch.breadcrumbs` | present below the top level | `[practitioner]` |
| `arch.pagination` | self-referencing canonical on every paginated page | - |

Click depth is the **shortest link path**, not URL folder depth. A page at `/a/b/c/d/e/page`
linked from the homepage is one click deep.

`depth.within_3_clicks` is `review`, never `fail`: nothing in a crawl knows which pages are
commercial. The list is produced; the judgment is the auditor's.

`nav.item_count` derives the navigation from links appearing on 80%+ of crawled pages rather
than parsing a `<nav>` element, which is more reliable and also catches footer and utility
links. It is reported as `review` with that caveat attached.

Do not go completely flat. Linking every page from the homepage removes hierarchy entirely
and tells Google nothing about relationships.

`rel=next` and `rel=prev` are no longer used by Google. Do not canonicalize page 2 to page 1
- they are different content.

---

## 6. Rendering (course/26) and mobile-first (course/29)

**This is the most consequential check in the skill.** Google indexes in two waves: raw HTML
immediately, JavaScript execution 24 to 72 hours later `[practitioner]`. That delay is
survivable. What is not survivable is that GPTBot, OAI-SearchBot, ClaudeBot and
PerplexityBot crawl independently and several of them fetch raw HTML and stop. There is no
wave two `[practitioner]`. A client-rendered site can rank normally in Google and be
completely absent from AI answers, and checking Google rankings will never reveal it.

**The gap between raw and rendered HTML is the AI visibility gap.**

| Check | Threshold |
|---|---|
| `render.raw_h1` / `render.raw_headings` | headings in the raw HTML |
| `render.raw_metadata` | title, meta description and canonical server-rendered |
| `render.raw_links` | navigation is real `<a href>` in the raw HTML |
| `render.js_only_nav` | no `<span onclick>` acting as a link |
| `render.raw_schema` | JSON-LD in the raw HTML |
| `render.strategy` | inferred from the raw:rendered word ratio - under 10% is CSR, 90%+ is SSR/SSG |

Metadata is the one that catches people constantly: a client-side SEO plugin setting titles
after load means bots see the default template title.

**Mobile-first (course/29).** Google indexes the mobile version - it *is* the page
`[confirmed]`. Content missing on mobile is content that does not exist. Parity covers body
content, headings, internal links, structured data, metadata and images with their alt text.

Hidden behind an accordion but **present in the DOM** is fine, and Google has said so.
Conditionally rendering a component only above a breakpoint is not. A collapsed hamburger
menu is fine as long as the links exist in the markup.

**Two deliberate measurement decisions**, both made after live runs produced false positives:

- **Images compare by alt text, not by `src`.** A responsive CDN bakes the viewport into the
  URL, so `src` comparison measures the CDN transform. A live run reported all 32 images on a
  homepage as missing on mobile for this reason.
- **Body-text volume is always `review`, never a verdict.** course/29 requires parity and
  states no numeric tolerance. A threshold invented here would be a number in a client report
  that the corpus does not support. Report the ratio; judge it.

---

## 7. Core Web Vitals (course/27) and page speed (course/28)

| Metric | Good | Needs improvement | Poor |
|---|---|---|---|
| **LCP** | **<= 2.5s** | 2.5 to 4.0s | > 4.0s |
| **INP** | **<= 200ms** | 200 to 500ms | > 500ms |
| **CLS** | **<= 0.1** | 0.1 to 0.25 | > 0.25 |

`[confirmed]`. Assessed at the **75th percentile** of real visits over a rolling **28-day**
window, and **all three must pass simultaneously**.

The p75 detail matters: you are measured on your slower quarter, which is mid-range Android
phones on mobile networks, not a laptop on office wifi. INP replaced FID in March 2024 and
is a far harder test.

**Field versus lab is the distinction that wastes the most time when missed.** Google ranks
on field data (CrUX) only. A page can score **100 in Lighthouse and fail the field
assessment** `[practitioner]`. `push_sheet.py` blocks any Core Web Vitals row carrying a
pass or fail with a lab data source.

**They are a floor, not a lever.** Failing suppresses you; passing buys nothing further.
Going from 2.4s to 1.1s is real engineering with no ranking return. Get to good, then go do
content or links.

Sources agree CWV act as a **tiebreaker** between comparable pages `[practitioner]`. One
ranking-adjacent point: sites with INP above 500ms saw **2 to 4 position drops** in the March
2026 core update `[practitioner]`.

**The conversion case studies are a different argument.** Rakuten 33% more conversions and
53% more revenue; Vodafone 15% more sales from a 31% LCP improvement; Deloitte and Google
8.4% retail conversion per 100ms. These measure **revenue, not ranking**. They are a strong
business case for speed and a weak ranking case. Say which argument you are making.

**Fix on the template, not the page.** Search Console groups by pattern, so one template fix
resolves hundreds of URLs. `vitals.py` samples templates for exactly this reason.

**course/28's priority order**, which `vitals.py` reproduces:

1. Compress and correctly load the hero image (fixes most LCP failures)
2. Add width and height to all images (fixes most CLS failures)
3. Audit and defer third-party scripts (fixes most INP failures)
4. Fix TTFB if over **800ms** - nothing else compensates
5. Eliminate render-blocking CSS and JS

**Do not lazy-load the LCP element** - it delays the exact thing being measured. Set
`loading="eager"` and `fetchpriority="high"`, and preload it. `[practitioner, aruntastic]`

CrUX is a 28-day rolling window, so a fix takes weeks to appear. Deploying an improvement and
checking the next morning proves nothing.

---

## 8. Structured data (course/30)

**The clearest evidence conflict in the entire corpus**, and this skill states it rather than
picking a side:

- **Vendor claims:** 71% of ChatGPT-cited pages and 65% of Google AI Mode pages carry
  structured data; 3.2x, 2.5x and 3:1 citation multipliers.
  `[practitioner, correlational, self-interested]`
- **Counter-evidence:** Ahrefs studied **1,885 pages** and found no major uplift from schema
  alone. SearchAtlas found no direct correlation between coverage and citation rate. Both
  causal or large-sample. `[practitioner, causal design]`
- **Google:** structured data is **not a direct ranking factor**, and the May 2026 AI search
  guidance states it is **not required** to appear in AI Overviews. `[confirmed]`

**Resolution:** the vendor numbers are correlational and come from companies selling schema
tools. The two studies designed to detect causation found nothing. Implement for **rich
result eligibility** and **entity disambiguation**. Never as a ranking or citation play.

| Check | Threshold |
|---|---|
| `schema.jsonld_format` | JSON-LD, in the `<head>` `[confirmed]` |
| `schema.parses` | every block is valid JSON |
| `schema.organization` | Organization on the homepage |
| `schema.organization_sameas` | `sameAs` pointing at real profiles |
| `schema.breadcrumbs` | BreadcrumbList sitewide (>80% of pages) `[practitioner]` |
| `schema.article_fields` | author, headline, accurate `dateModified` |
| `schema.iso_8601` | `2026-04-18`, `PT30M` - the most common validation error |
| `schema.absolute_urls` | absolute, always |
| `schema.stable_ids` | `@id` connecting entities into one graph |
| `schema.matches_visible` | markup matches visible content |

Schema.org has 800+ classes and Google renders rich results for roughly **30**
`[practitioner]`. For most business sites the useful set is small: **Organization with
`sameAs`** plus **sitewide BreadcrumbList** is the highest-value, lowest-effort pair.

### Retired types

| Type | Status |
|---|---|
| **FAQ rich results** | Sunset entirely **7 May 2026**, including the former health and government exceptions |
| **HowTo** | Effectively dead on desktop since 2023 |
| **ClaimReview** | Restricted to verified fact-checkers (June 2025 sweep) |
| **Book Actions, Course Info (old), Estimated Salary, Learning Video, Special Announcement, Vehicle Listing** | Phased out, June 2025 sweep |
| **Sitelinks Searchbox** | Sunset late 2024 |

`[practitioner]`

**The nuance that must survive into the report:** FAQPage and HowTo markup **still carry
value for non-Google engines** - ChatGPT, Perplexity and Bing Copilot continue to use them.
Ripping the markup out because Google stopped rendering the rich result is the wrong
reaction. `schema.py` therefore reports retired types as `review` with this attached, never
as `fail`.

**Marking up content that is not on the page is a structured data spam violation** and
carries manual-action risk. `schema.matches_visible` names every page with rating or review
markup for a visual check, because the page text is not in the crawl graph.

**When generating schema, ask rather than invent.** A keeper worth quoting: *"Make sure
you've included all the required and optional fields. If you're not sure how to fill in a
specific field ask me."* `[practitioner, aruntastic]` A fabricated schema field is silently
invalid - it does not error, it just quietly does nothing. `emit.py` emits `<<FILL IN>>`
placeholders for `sameAs` and the legal name rather than plausible guesses.

---

## 9. International and hreflang (course/31)

**Most sites do not need this, and deciding so is a legitimate audit finding.** A documented
"not applicable" stops someone implementing it later for no reason. `technical.py` returns
exactly one `pass` row when no hreflang exists, and `emit.py` writes the reasoning to
`hreflang.md`.

You need it only with substantially the same content in multiple languages, or targeted at
multiple countries with real differences - currency, pricing, shipping, legal terms. Not a
swapped currency symbol. A single well-executed site usually outperforms three thin
translated ones.

**Subdirectories** (`example.com/de/`) are the right default. ccTLDs only when the market
genuinely demands local presence. Parameters (`?lang=de`) never.

| Check | Threshold |
|---|---|
| `hreflang.codes_valid` | ISO 639-1 language, optional ISO 3166-1 alpha-2 region. **Region alone is invalid.** `de` valid, `de-AT` valid, `AT` not. `en-UK` is wrong; the code is `GB`. |
| `hreflang.self_referencing` | every page includes itself |
| `hreflang.return_links` | bidirectional - if A declares B, B must declare A |
| `hreflang.x_default` | always include it |
| `hreflang.targets_indexable` | canonical, indexable, 200-status URLs |
| `hreflang.canonical_agrees` | no conflict with the canonical |

**Every one of these fails silently.** Nothing alerts you. A one-way declaration is ignored
entirely, and it is the most common failure.

**hreflang is not a ranking signal.** It shows the right version to the right user and stops
translations being read as duplicates. It is often sold as a ranking play; it is not one.

---

## Not connected

Named rather than approximated. Half of Tier 3 is an indexation question and Search Console
is the only thing that can answer it.

| Missing | What it would answer | Manual route |
|---|---|---|
| **Search Console Pages report** | indexed-to-submitted ratio; "Crawled - not indexed" (a quality rejection) vs "Discovered - not indexed" (a crawl-reach problem) | Search Console -> Pages |
| **URL Inspection** | Google-selected vs user-declared canonical; what Googlebot smartphone actually rendered | URL Inspection on 5 key pages |
| **Crawl stats** | requests over time, response time trend, what Googlebot spent budget on | Settings -> Crawl stats |
| **Core Web Vitals report** | field data grouped by Google's own URL clustering | Search Console -> Core Web Vitals -> Mobile |
| **Enhancements report** | template-wide schema errors | Search Console -> Enhancements |
| **Rich Results Test / validator.schema.org** | render eligibility and vocabulary conformance - two different questions, you want both | run both by hand |
| **Backlink profile** | which URLs carry external links, which sets redirect-mapping priority | any backlink tool |
| **AI Overview presence** | whether the site appears | check in incognito, record by hand |

Verified, not assumed: `gws` exposes no Search Console service and no credential exists.

---

## On the aruntastic material

The sibling skills cross-check a practitioner course by aruntastic against the corpus and
carry the parts that genuinely add something, tagged `[practitioner, aruntastic]`. Two of its
keepers are load-bearing here and are cited above: **do not lazy-load the LCP element**, and
**the schema anti-hallucination clause**.

No separate aruntastic Tier 3 material was available in the repo when this skill was built,
so unlike `seo-foundation` this file carries **no full cross-check** of that source against
sections 21 to 31. That is a gap, stated rather than papered over. If the material surfaces,
cross-check it and record which methods hold and which the corpus supersedes.
