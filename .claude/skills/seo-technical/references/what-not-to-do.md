# What not to do

Claims this skill must never make, and mistakes that look like diligence.

---

## Never claim

- **"Schema will improve your rankings"** or **"schema gets you cited by AI."** Google has
  confirmed structured data is not a direct ranking factor, and the two studies designed to
  detect causation - Ahrefs across 1,885 pages and SearchAtlas on coverage versus citation
  rate - found nothing. The 3.2x numbers are correlational and come from companies selling
  schema tools. Sell it as rich-result eligibility and entity clarity.
- **"Core Web Vitals will lift your rankings."** They are a floor and a tiebreaker between
  comparable pages. They will not lift thin content above an authoritative page. The Rakuten,
  Vodafone and Deloitte case studies measure **conversion**, not ranking - a strong business
  argument and a weak SEO one. Do not blend them.
- **"A duplicate content penalty."** There is none for ordinary duplication. There is signal
  dilution, which is worse because nothing reports it.
- **"hreflang will improve your rankings."** It shows the right version to the right user and
  stops translations reading as duplicates. That is all.
- **"Sitemaps are a ranking factor."** Confirmed not to be, and never have been.
- **"Your crawl budget is a problem"** on a site under ~10,000 pages. Below that, uncrawled
  pages are an architecture, linking or quality problem. Optimizing crawl budget on a
  200-page site is a way of feeling technical while achieving nothing.
- **A field-data verdict from a Lighthouse score.** A page can score 100 in the lab and fail
  the field assessment. `push_sheet.py` blocks this and it should stay blocked.
- **"Indexation looks healthy"** from a crawl. A crawler reports what it fetched, not what
  Google stored. Without Search Console the honest answer is `unknown`.

---

## Never do

- **Report a per-agent robots.txt rule as a site-wide block.** Parse the user-agent groups.
  This produced the single most alarming possible false positive on the first live run.
- **Delete FAQPage or HowTo markup** because Google retired the rich result. ChatGPT,
  Perplexity and Bing Copilot still consume both. Leave the markup, reset the expectation.
- **Invent a schema field.** A fabricated field is silently invalid: it does not error, it
  just quietly does nothing. `emit.py` writes `<<FILL IN>>` and that is correct behaviour,
  not laziness.
- **Canonicalize the site to its homepage.** It tells Google the rest of the site does not
  exist.
- **Both `Disallow` and `noindex` the same URL.** Disallowed means the noindex is never read,
  so the URL can stay indexed as a bare link indefinitely. Pick one.
- **Redirect en masse to the homepage during a migration.** It is the classic way to lose
  everything at once, and it is treated as a soft 404.
- **Remove a redirect two years later.** External links and bookmarks point at the old URL
  forever. Redirects are cheap; keep them.
- **Optimize past the Core Web Vitals threshold for ranking reasons.** Telling a client
  already passing to chase 1.1 seconds is telling them to spend money for nothing. Say so.
- **Implement hreflang on a site that does not need it.** It adds permanent maintenance for
  no benefit, and it is the more common of the two hreflang mistakes.
- **Go completely flat** to fix depth. Linking every page from the homepage removes hierarchy
  and tells Google nothing about relationships.
- **Canonicalize page 2 to page 1.** They are different content, and it hides everything on
  page 2.
- **Add `priority` or `changefreq`.** Both ignored.
- **Set `lastmod` to today on everything.** It is generated rather than observed, and it
  destroys the value of the hint.

---

## Measurement failures

Each of these produced a real false positive during the build. They generalize into one rule:
**measure the thing the course names, not the nearest available artifact.**

| Mistake | What it actually measured | The fix |
|---|---|---|
| Flat line scan of robots.txt | one bot's rules, reported as everyone's | group by user-agent |
| Comparing image `src` mobile vs desktop | the responsive CDN's URL transform | compare alt text, which is what course/29 asks for |
| Counting all internal links to find link-list pages | the sitewide navigation, on every page | subtract the derived sitewide set first |
| Treating a zero-width-space heading as content | an invisible character | strip invisibles before deciding a heading has text |
| `_live()` before building the sitemap exclusion list | only healthy pages, so the 404s it existed to explain were already gone | iterate every crawled URL |
| `review` on a check with nothing to review | noise that trains the reader to skim | `pass` when the population is empty, and say so |

---

## Report failures

- **Forty findings.** Three beat forty. An audit that lists everything is the standard output
  of an automated tool and it is why tool exports do not sell.
- **Findings out of tier order.** A `this week` schema fix above a `this month` indexation
  failure is the most common way an otherwise-correct audit becomes wrong advice.
- **A finding with no evidence.** An opinion wearing a finding's clothes. The client has no
  way to check it.
- **Silence about what is fine.** Naming what passes is what makes the failures credible, and
  it stops a client paying to fix something that already works.
- **Approximating a Search Console number.** Say "not connected" and give the manual route.
  A confident wrong indexation figure is worse than an admitted gap.
- **Presenting a heuristic as a measurement.** Template grouping by URL shape is not Google's
  clustering. Click depth from a capped crawl is a floor. Say which is which.
