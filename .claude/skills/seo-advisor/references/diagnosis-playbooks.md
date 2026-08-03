# Diagnosis Playbooks - symptom to ordered hypotheses

The default mode. Someone describes a symptom; you produce an **ordered** list of
hypotheses with the evidence that would confirm or kill each one. You do not guess at a
single cause.

## The method

1. **Get the data before theorizing.** Search Console is the minimum. Without it you are
   guessing, and saying so is better than guessing confidently.
2. **Separate the three failure surfaces.** A page can fail to be *crawled*, fail to be
   *indexed*, or be indexed and fail to *rank*. These have completely different fixes and
   the symptom usually tells you which.
3. **Order by likelihood x cheapness to check**, not by how interesting the cause is.
4. **Name the falsifying evidence** for each hypothesis. "If it were X, we would see Y."
5. **Give one highest-leverage fix at the end**, not a list of twelve.

---

## Symptom: traffic dropped, rankings look stable

The single most common 2026 pattern, and usually **not** a ranking problem.

| # | Hypothesis | Confirming evidence | Tier |
|---|---|---|---|
| 1 | **AI Overview took the clicks** | GSC: impressions flat or up, clicks down, CTR down. AI Overview present on affected queries. CTR drop of **up to 58%** is documented | `[P]` [s145, s288] |
| 2 | **SERP feature pushed you down the page** | Rank unchanged but a featured snippet, shopping pack, or video carousel now sits above | `[P]` |
| 3 | **Seasonality** | Compare year over year, not month over month. Requires GA4 retention raised to **14 months**, which is not the default | `[C]` [s251, s254] |
| 4 | **GA4 misattribution, not a real drop** | GA4 misclassifies **30-50%** of search traffic as Direct/Unassigned. Check Direct traffic landing on deep pages (4+ URL segments) | `[P]` [s254] |
| 5 | **Tracking broke** | Tag missing on a template, consent banner change, filter added |  |

**Highest-leverage first move:** open GSC, compare clicks against impressions over 28 days.
If impressions held and clicks fell, it is a CTR problem, and no amount of ranking work
will fix it.

---

## Symptom: rankings fell after a core update

| # | Hypothesis | Confirming evidence | Tier |
|---|---|---|---|
| 1 | **Still mid-rollout** | Core updates roll out over days; the May 2026 update took **12 days**. Do not diagnose until a week after completion | `[C]` [s219] |
| 2 | **Domain-level quality weighting** | Thin content in one site section suppressing good content elsewhere. Look for a sitewide drop, not a page-level one | `[P]` [s294] |
| 3 | **Intent mismatch that finally caught up** | The SERP changed shape. Check what now ranks: if the format changed (guides replaced by tools), your page is answering the wrong question |  |
| 4 | **E-E-A-T gap on YMYL topics** | No named author, no credentials, no first-hand evidence | `[P]` [s294, s292] |
| 5 | **INP regression** | Sites with INP > 500ms saw **2-4 position drops** in the March 2026 update | `[P]` [s252] |

**Key framing:** core updates are **reassessments, not penalties**. Nothing was "done to"
the site; other pages were judged more useful. There is no reconsideration request to file
[s219, s184].

**Highest-leverage first move:** consolidate or remove thin content, then add genuine
first-hand experience and named authorship to the pages that dropped.

---

## Symptom: a page will not index

| # | Hypothesis | Confirming evidence |
|---|---|---|
| 1 | **`noindex` present** | View source, check the meta robots tag and the X-Robots-Tag header |
| 2 | **Blocked in robots.txt** | If also `noindex`, the two **conflict**: disallowed means Google never reads the noindex, and the URL can stay indexed with no content. Pick one [s188, s209] |
| 3 | **Canonical points elsewhere** | GSC URL Inspection shows "Google-selected canonical" differing from yours |
| 4 | **"Discovered - currently not indexed"** | A crawl budget signal. Only a real constraint above **10,000-50,000 pages** [s136, s298] |
| 5 | **"Crawled - currently not indexed"** | A **quality** signal, not a technical one. Google saw it and declined [s145, s252] |
| 6 | **Orphaned** | No internal links pointing at it |
| 7 | **JavaScript-dependent content** | Raw HTML is empty; content arrives in wave two, **24-72 hours** later [s299, s297] |
| 8 | **Past the 2MB fetch limit** | Googlebot reads **2MB per URL**; content after that is invisible [s282] |

**The distinction that resolves most cases:** "Discovered" is a crawling problem,
"Crawled - not indexed" is a quality problem. They look similar and share no fixes.

---

## Symptom: ranking on Google but invisible in AI answers

Now a distinct diagnosis, because the overlap between the two collapsed from **92% to
~38%** [s233, s220, s110].

| # | Hypothesis | Confirming evidence | Tier |
|---|---|---|---|
| 1 | **Query fan-out mismatch** | You match the literal query but none of the **5-11 sub-queries** the engine actually ran. Ask the engine what sub-queries it would use | `[P]` [s271, s286] |
| 2 | **Thin topical coverage** | One page on a broad topic. **80%+ coverage retains 85.4% of AI visibility**; single pages do not survive fan-out | `[P]` [s110] |
| 3 | **Content not extractable** | No self-contained answer units. Target **134-167 words** per unit, entity definition in the **first 40-60 words**, BLUF structure | `[P]` [s110, s269] |
| 4 | **AI crawlers blocked or blind** | Check robots.txt for GPTBot/ClaudeBot/PerplexityBot blocks. Separately: AI crawlers **often skip JavaScript**, so a JS-rendered site is invisible to them regardless | `[P]` [s181, s291, s111] |
| 5 | **No entity identity** | No Wikidata entry, no `sameAs`, no consistent brand co-occurrence. Mentions correlate **0.664** with AI citation vs **0.218** for links | `[P]` [s270] |
| 6 | **Wrong platform expectation** | ChatGPT cites **~90%** from pages ranked 21+; Perplexity is **half Reddit**. Being absent from one engine is not being absent from all | `[P]` [s233, s198] |

**Highest-leverage first move:** confirm AI crawlers can actually fetch and read the page
(server-side rendered, not blocked). Everything else is wasted if they cannot.

---

## Symptom: new site, nothing ranks at all

| # | Hypothesis | Note |
|---|---|---|
| 1 | **Targeting keywords far above domain strength** | KD is relative to your domain. New sites should target **KD under 20**, volume **100-1,000** [s288] |
| 2 | **Not enough time elapsed** | Foundation phase is **months 1-3 with minimal movement** by design. This is normal, not failure [s107, s119] |
| 3 | **No topical depth** | One page per topic loses. Pillar of **2,500-4,000 words** plus **8-15 clusters** [s288, s128] |
| 4 | **Zero authority signals** | No links, no mentions, no entity presence |
| 5 | **Indexation not verified** | Confirm indexed before diagnosing rank |

---

## Symptom: local business not in the map pack

| # | Hypothesis | Note |
|---|---|---|
| 1 | **Wrong or too-generic primary category** | The strongest single signal. "Personal Injury Attorney" beats "Lawyer" [s191, s243] |
| 2 | **Distance** | A hard constraint you cannot optimize away. Check the searcher's location |
| 3 | **Review volume or velocity** | Target **2-4/week**; **5-15/month over 6 months** moves 5-10 positions [s137, s243] |
| 4 | **NAP inconsistency** | Even "St." vs "Street" can suppress. Audit Tier 1 first: Google, Bing Places, Apple Maps, Yelp, Facebook [s172, s173] |
| 5 | **Incomplete profile** | GBP signals are **32%** of local weighting [s191, s172] |
| 6 | **No local landing page** | Or a page that is a city-name find-and-replace, which counts as thin |

---

## Symptom: client says "we did SEO and it did nothing"

A commercial diagnosis, not a technical one.

| # | Hypothesis | Note |
|---|---|---|
| 1 | **Not enough time** | Measurable impact is **6-12 months**, competitive markets **12-18+** [s107, s119, s275] |
| 2 | **Underfunded for the difficulty** | KD 30-45 needs **$2,000-$3,500/mo minimum**. Below the floor buys activity, not results [s260] |
| 3 | **Deliverables were activity, not outcomes** | Reports full of "optimized 12 pages" with no ranking or traffic movement |
| 4 | **Wrong keywords** | High volume, no commercial intent. High-intent terms convert **5-10x** better [s127] |
| 5 | **Measured wrong** | GA4 misattributing **30-50%** of organic as Direct. The work may have worked invisibly [s254] |

**Never respond to this by promising rankings.** Nobody controls Google's ranking, and a
guarantee is the clearest signal of a bad vendor.

---

## What not to do when diagnosing

- **Do not diagnose without data.** Ask for GSC access or a screenshot. Saying "I need the
  Search Console data to tell you" is a better answer than a confident guess.
- **Do not blame the most recent thing that changed.** Correlation in time is not cause.
- **Do not lead with a technical audit** when the symptom points at CTR or content. Most
  technical audits find real issues that are not the reason traffic fell.
- **Do not present a 40-item checklist.** Order by impact and give the first move.
- **Do not quote a vendor statistic as a fact.** Say who measured it.
