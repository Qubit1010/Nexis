# What Not To Do

Run this over the whole deliverable before it goes out.

---

## Numbers you must not invent

- **Clicks, impressions, CTR, position, decay.** There is no Search Console access. Every
  one of these is `not connected`, with the export steps attached. An invented traffic
  number poisons every track assignment downstream and is the single most damaging thing
  this skill could get wrong.
- **AI Overview presence, or a share of AI citations.** Not observable from anything
  available here. Verified across five query shapes by `seo-foundation` that Serper never
  returns it. Report `unknown` and tell them to check in incognito.
- **Backlink counts.** No free API. `not connected`.
- **A rendered title pixel width.** The estimate in `title.pixels` is directional; the
  verdict stays `unknown`. Check the live SERP snippet.
- **A search volume.** That is `seo-foundation`'s territory and its answer is the same:
  never estimate one.

## Thresholds that do not exist

- **Keyword density.** Not a thing. Targeting a percentage produces exactly the
  over-optimization the helpful-content system catches.
- **A word-count target.** Length is not a ranking factor. Report the count as an
  observation and the competitor median as context. Padding to match it is the pattern that
  gets caught.
- **A readability grade as a gate.** The 320-source corpus sets none. Report the number,
  tag it `[practitioner, aruntastic]`, and let the audience decide - a technical B2B page
  at grade 14 may be exactly right.
- **A term frequency from `terms.py`.** The output is coverage, not a quota. "The top three
  all explain X and this page never mentions it" is a finding. "Add X eleven times" is not.
- **Meta keywords.** Dead for over a decade.

## Method failures

- **Auditing in checklist order instead of impact order.** Intent, then cannibalization,
  then content, *then* metadata. Rewriting titles on a page that targets the wrong query is
  effort spent making a wrong thing more clickable.
- **Skipping phase 1.** Auditing 200 pages equally produces forty findings and no
  diagnosis. Identify the 5-10 pages that matter commercially first.
- **Changing live URLs.** Note-only unless one of the four exceptions in `checks.md`
  applies. "It would be tidier" costs every inbound link.
- **Bulk-renaming existing images.** Same cost, smaller return. Name new ones well.
- **Optimizing past a floor.** Core Web Vitals, HTTPS and mobile are floors. Telling a
  client already passing LCP to chase 1.1 seconds is telling them to waste money.
- **Reporting `pass` where the honest answer is `review`.** If the check needs judgment,
  return the evidence and make the call in the report. A fabricated `pass` is how a
  confidently wrong document gets shipped.
- **Calling a date change a refresh.** Fake freshness is a recognized pattern and it does
  not work.
- **Lowering the competitor bar in `terms.py` to manufacture a term list.** If page one is
  platforms and forums, that is the finding.
- **Rewriting instead of revising.** The regeneration failure mode: the improved page is
  smoother, blander, and missing the first-hand detail that was the only thing making it
  worth reading.

## Delivery failures

- **Forty findings.** Three, ranked, with evidence. `push_sheet.py` blocks more than five at
  "this week" for this reason.
- **A summary posing as a diagnosis.** "Several SEO issues were found" could be copied onto
  any client's report. That is the test.
- **Omitting "what is fine".** It proves you looked rather than pattern-matched, and it
  stops the client breaking something that works.
- **Burying the Search Console gap.** It makes the whole document look more certain than it
  is. Name it in section 0 and again at the end.
- **Untranslated jargon.** "LCP" means nothing to a client. "The biggest thing on the screen
  takes 4.1 seconds to appear on a phone" means something.
- **Promising an effect you cannot support.** "This will dramatically improve your rankings"
  is what every previous vendor said. Be honest when the expected effect is small.

## Claims to leave alone

Restating `seo-advisor`'s numbers as if they were measured here is how the two skills drift
apart. Cite `[sN]` and let it own the corpus.

Handle these with the tier tag attached, because they are weaker than they sound:

| Claim | Handle as |
|---|---|
| Google rewrites 61% of titles | A **conflict**: Zyppy 61% vs Backlinko 76% `[s166, s295]`. Quote the range or neither. Never average two studies into one number. |
| Bidirectional linking gives 2.7x AI citations | `[practitioner, single vendor]`. Directional only. |
| Brand mentions correlate 0.664 with AI citation | Correlational, one vendor, 2025 `[s270]`. Not a mechanism. |
| Princeton GEO lifts (+41% quotes, +30% stats, +30% citations) | The best-evidenced content finding in the corpus `[s220, s179]`, and still `[practitioner, peer-reviewed method]`. Say the direction, not the decimal, to a client. |
| Clustered content earns +30-43% more traffic | `[s288]`, single vendor, directional. |

The corpus is **18 confirmed against 302 practitioner**. Flattening that into one confident
voice is the failure mode. The only `[confirmed]` numbers this skill touches are the Core
Web Vitals thresholds and HTTPS.

## Scope

| If the ask is | It goes to |
|---|---|
| Keyword research, intent, clustering, the keyword map | `seo-foundation` |
| Theory, benchmarks, "why did traffic drop", the course | `seo-advisor` |
| Writing the article | `blog-writer` |
| A prospect-facing audit with a hook email | `website-audit-system` |
| Crawl budget, rendering, sitemaps, canonicals at scale, hreflang | technical skill (not built yet - say so) |
| Backlinks, digital PR, brand mentions | off-page skill (not built yet - say so) |
| AI Overview presence, ChatGPT citation share | AI-search skill (not built yet - and it will hit the same observability wall) |

Saying "that is out of scope and here is who owns it" is a complete answer. Quietly doing a
worse version of another skill's job is not.
