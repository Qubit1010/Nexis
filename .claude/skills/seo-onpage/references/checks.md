# The Check Registry

Every check `onpage.py` runs, what it measures, the threshold it measures against, where
that threshold comes from, and how the verdict is decided.

This file is the contract between the script and the report. If a threshold changes in
`seo-advisor`'s corpus, it changes here, and the script reads it from here - not the other
way round.

## Contents

- [The four verdicts](#the-four-verdicts)
- [1. Titles and meta descriptions](#1-titles-and-meta-descriptions)
- [2. Headings and structure](#2-headings-and-structure)
- [3. Content quality](#3-content-quality)
- [4. URLs and navigation](#4-urls-and-navigation)
- [5. Internal linking](#5-internal-linking)
- [6. Media](#6-media)
- [7. E-E-A-T](#7-e-e-a-t)
- [8. Schema](#8-schema)
- [What is deliberately not checked](#what-is-deliberately-not-checked)

---

## The four verdicts

A check emits exactly one of these. The distinction between `review` and `unknown` is the
one that matters, and conflating them is how an audit starts lying.

| Verdict | Meaning | When |
|---|---|---|
| `pass` | Measured, and it clears the threshold | The measurement happened and the answer is good |
| `fail` | Measured, and it does not clear the threshold | The measurement happened and the answer is bad |
| `review` | Measured, but the verdict needs judgment | The script can count the words in the first paragraph; it cannot tell you whether they answer the query. Evidence is attached for you to rule on. |
| `unknown` | Not measurable from any source available here | No Search Console. No AI Overview data. No rendered pixel width. The check ran and the honest answer is "cannot tell", with the reason and the manual method attached. |

An `unknown` is a finding. Reporting it as a `pass` because nothing looked broken is the
single easiest way to hand a client a confidently wrong document.

Every emitted row carries: `check_id`, `area`, `observed`, `threshold`, `verdict`, `source`,
`evidence`. `source` is either a `course/NN` pointer, an `[sN]` citation, or `measured
here`.

---

## 1. Titles and meta descriptions

Source: `course/11`. Corpus: `[s296, s207, s128, s166, s187]`, all `[practitioner]`.

| id | Measures | Threshold | Verdict logic |
|---|---|---|---|
| `title.present` | `<title>` exists and is non-empty | must exist | fail if absent or whitespace |
| `title.length` | character count | **50-60 chars** | pass 50-60; fail outside; the number is reported either way |
| `title.pixels` | estimated rendered width | **~600px** | always `unknown` on the verdict, with the estimate attached. Google measures pixels, not characters - a capital W is wider than an i - and nothing here renders a font. The estimate uses per-character widths and is directionally useful, never authoritative. |
| `title.frontload` | position of the primary keyword | **within the first 40 chars** | pass if the keyword or a close variant appears in `title[:40]`; fail if it appears later; `review` if only a partial match (the script cannot judge a synonym) |
| `title.uniqueness` | duplicate titles across crawled pages | one title, one page | fail on any exact duplicate across the crawl set; skipped in single-page mode |
| `title.agreement` | title vs H1 vs first paragraph | all three tell the same story | `review` always. This is the defence against Google rewriting the title, and it is a semantic judgment. Evidence attached: all three strings. |
| `meta.present` | `<meta name="description">` exists | must exist | fail if absent. Note in the finding that a **blank meta description beats a generic auto-generated one** - if the fix is a template, do not ship the template. |
| `meta.length` | character count | **105-155 chars** `[s207]` | pass 105-155; fail outside |
| `meta.frontload` | key information placement | **within the first 120 chars** | `review` - the script reports `meta[:120]`, you judge whether the useful part survives mobile truncation |
| `meta.specificity` | generic-phrase detection | no boilerplate | `review`, with a flag if it matches known boilerplate ("Welcome to", "We offer a wide range of", the bare company name) |

**On Google rewriting titles:** the corpus carries a genuine source conflict here - Zyppy
measured 61%, Backlinko measured 76% `[s166, s295]`. Quote the range or neither; do not
average two studies into a false single number. `what-not-to-do.md` lists this as a number
to stop quoting as fact.

---

## 2. Headings and structure

Source: `course/12`. Corpus: `[s296, s294, s181, s110, s220, s273, s269]`, `[practitioner]`.

Headings do three jobs now, and the third is why the thresholds got stricter: scanning,
hierarchy, and passage-level retrieval by AI systems that extract a section rather than a
page.

| id | Measures | Threshold | Verdict logic |
|---|---|---|---|
| `h1.count` | number of `<h1>` elements | **exactly 1** | fail on 0 or 2+ |
| `h1.keyword` | primary keyword in H1 | present, close to but not identical to the title | `review` - identical is a mild smell, not a failure |
| `heading.hierarchy` | levels skipped (H2 then H4) | no skips | fail on any skip. The fix is CSS, not heading level - if a heading looks wrong, style it, do not demote it. |
| `heading.question_ratio` | share of H2/H3 phrased as questions | **~1/3** `[s181, s294]` | pass 0.2-0.5; `review` outside. It is a target, not a quota, and a page with no natural questions should not have questions bolted on. Source the questions from People Also Ask harvested in `seo-foundation`. |
| `heading.descriptive` | headings that only name a category | headings should answer | `review`, listing every heading that is a bare noun phrase |
| `section.length` | words between one heading and the next | **split much over 200** | fail over 250, `review` 200-250. Rationale: a self-contained extractable unit runs **134-167 words** `[s110]`, and a 400-word section is not one unit, it is two glued together. |
| `section.backward_dep` | sections opening with a back-reference | none | fail on any section starting "This", "As mentioned", "The above", "Therefore" without a named subject. A section that depends on the one before it cannot be extracted on its own. |
| `heading.story` | H2s read in order | should narrate the page | `review` always, with the H2 list printed in order. If reading only the headings does not tell the story, the structure is decorative. |

**The two word counts are not in conflict, and blog-writer currently conflates them:**

- **40-60 words** is the *entity definition or direct answer* that opens a section
  `[s220, s273, s269]`.
- **134-167 words** is the *whole self-contained unit* a retrieval system extracts `[s110]`.

The first sits inside the second. A section that opens with a 50-word answer and runs to
150 words satisfies both.

---

## 3. Content quality

Source: `course/14`. Corpus: `[s220, s179, s287, s294, s128]`.

The helpful-content system folded into core ranking in 2024, which changed the sign:
content built to rank is now a demotion signal rather than a neutral one.

| id | Measures | Threshold | Verdict logic |
|---|---|---|---|
| `content.answer_first` | the first 40-60 words | must answer the primary question | `review` always. The script prints the first 60 words and the target query. You judge. This is the single most predictive check on the page and no script can make the call. |
| `content.word_count` | total words | **none** | always `pass` with the number reported. **Length is not a ranking factor.** Padding to hit a number is exactly the pattern the system catches. Reported as an observation so you can see thin against a 2,000-word competitor set, never as a verdict. |
| `content.paragraph_length` | sentences per paragraph | **2-4** | `review` if the median is above 5 or below 1.5. Reported as a distribution, not a pass/fail per paragraph. |
| `content.statistics` | count of concrete numbers | **at least 1** | fail at 0. Princeton GEO measured statistics at **+30%** citation lift `[s220, s179]` `[practitioner, peer-reviewed method]`. |
| `content.citations` | outbound links to named sources | **at least 1** | fail at 0. Inline citations **+30%** `[s220, s179]`. |
| `content.expert_quote` | a quoted named person | **at least 1** | `review` - the script can find quotation marks near a proper noun but cannot verify the person is real or relevant. Expert quotes are the strongest single lever measured, at **+41%** `[s220, s179]`. |
| `content.firsthand` | evidence of doing the thing | at least 1 marker | `review`. Markers: own numbers, named tools with versions, screenshots, "what broke", "what I would do differently". This is the first E in E-E-A-T and the thing most sites fail. |
| `content.padding` | sections that restate | none | `review`, listing candidates: a section that restates the previous one, a definition of something obvious, three examples where one would do, a summarizing conclusion. |
| `content.readability` | Flesch-Kincaid grade via `textstat` | **no corpus threshold** | always `review` with the number. The 320-source corpus sets no readability target. The aruntastic method suggests aiming for roughly 10th grade `[practitioner, aruntastic]`. Report it; never gate on it. A technical B2B page reading at grade 14 may be correct for its audience. |
| `content.satisfaction` | would the reader stop searching | the whole test | `review` always, and it is the check the other nine serve. If the answer is no, nothing else on this page matters. |

---

## 4. URLs and navigation

Source: `course/13`. Corpus: `[s299, s303, s209, s291]`, `[practitioner]`.

**Default verdict on any live URL is note-only.** The URL is the only on-page element with
a real switching cost. It is a small direct signal and a large indirect one, and the
downside of changing it is every inbound link, every share, and a settling period.

| id | Measures | Threshold | Verdict logic |
|---|---|---|---|
| `url.length` | characters | **under 60** | `review` (note only) if over; never `fail` on a live URL. `fail` is available in draft mode, where the slug has not shipped yet and is free to change. |
| `url.case` | uppercase characters | lowercase | `review` (note only) |
| `url.separators` | underscores | hyphens | `review` (note only). Underscores join words, hyphens separate them. |
| `url.depth` | path segments | **3 maximum** | `review` (note only) |
| `url.dates` | a date in an evergreen path | none | `review` (note only) |
| `url.parallel` | two structures for one topic | none | fail. `/services/seo` and `/seo-services` both existing is cannibalization wearing a different hat, and it is one of the four cases where changing a URL is justified. |
| `nav.item_count` | primary nav items | **about 7** | `review` |
| `nav.vocabulary` | internal jargon in nav labels | customer vocabulary | `review`, cross-checked against the persona's verbatim vocabulary from `08-audience-persona.md` when it exists |
| `nav.breadcrumbs` | breadcrumb markup | `BreadcrumbList` schema | fail if breadcrumbs are visible but unmarked. Described in the corpus as "one of the most under-implemented signals available" `[s291]`. |

**The four exceptions that justify changing a live URL.** Anything else is not a reason:

1. It is genuinely broken or misleading.
2. The site is being restructured anyway.
3. It contains something that must be removed.
4. A migration is happening for other reasons.

If one applies: 301 the old URL, update every internal link to point at the **new** URL
directly rather than through the redirect, and expect a settling period.

---

## 5. Internal linking

Source: `course/16`. Corpus: `[s128, s288, s299, s209]`, `[practitioner]`.

The only authority signal fully under the client's control, and reliably the most
underused.

| id | Measures | Threshold | Verdict logic |
|---|---|---|---|
| `links.density` | internal links per 2,000 words | **8-15** `[s128]` | `review` outside the range. **Treat this as a sanity range, not a quota.** Hitting 12 by bolting a link block onto the footer satisfies the number and none of the intent. |
| `links.anchor_quality` | non-descriptive anchors | none | fail on "click here", "read more", "learn more", "this article", "here" |
| `links.anchor_variety` | exact-match repetition | vary naturally | `review` if one anchor string is used for the same target more than 3 times |
| `links.orphan` | pages with zero inbound internal links | **zero orphans** | fail. Requires crawl mode. |
| `links.depth` | clicks from homepage to a commercial page | **3 maximum** `[s299, s209]` | fail over 3. Requires crawl mode. |
| `links.to_redirects` | internal links pointing at a 301 or 404 | none | fail, listing each |
| `links.bidirectional` | pillar links to cluster and back | both directions | fail if one-way. Reported at **2.7x** AI citation probability `[s288]` `[practitioner, single vendor]` - directional, not a measured multiple you should quote to a client as fact. |
| `links.opportunities` | pages mentioning a topic without linking to its target | surfaced, not scored | always `review`. This is the highest-yield output of the whole area and usually surfaces dozens. |

**Link source strength, strongest first:** contextual body links, then navigation (powerful
but blunt), then related-post modules, then footer (weak and largely discounted). A pillar
should link down to its clusters *in context*, not as a block of 15 at the bottom.

**On opportunity discovery.** `course/16`'s lab prescribes `site:yourdomain.com "topic
phrase"`. `links.py` does it locally against the crawled corpus instead - pages whose body
contains the phrase but carry no link to the target. That is free, complete, and not
subject to what Google chose to index.

---

## 6. Media

Source: `course/17`. Corpus: `[s295, s292, s296, s166]`. The LCP threshold is `[confirmed]`;
everything else is `[practitioner]`.

| id | Measures | Threshold | Verdict logic |
|---|---|---|---|
| `media.hero_weight` | bytes of the LCP-candidate image | **under 150KB** | fail over, with the **measured** WebP re-encode saving attached |
| `media.format` | image format | **WebP or AVIF** | `review` for JPEG/PNG with the measured saving; WebP is typically 25-35% smaller than equivalent JPEG and universally supported. AVIF is smaller with less support; WebP with a JPEG fallback is the safe default. |
| `media.dimensions` | natural vs displayed size | sized to display | fail if natural width is more than 2x the displayed width |
| `media.explicit_size` | `width` and `height` attributes | present on every image | fail if missing. This prevents an entire category of layout-shift failure. |
| `media.hero_lazy` | `loading="lazy"` on the LCP image | never | fail. The hero should load eagerly with `fetchpriority="high"`. |
| `media.alt_present` | alt attribute | present on every image | fail if the attribute is absent. `alt=""` on a decorative image is correct and passes - omitting the attribute entirely is the failure. |
| `media.alt_quality` | alt text content | descriptive, in context | `review`, flagging stuffed alts and bare filenames |
| `media.filename` | descriptive filenames | words, not camera output | `review` (note only) on `IMG_1234` / `DSC00567` patterns. **Going forward only** - bulk-renaming existing images is a URL change and carries the same cost as section 4. |
| `media.lcp` | Largest Contentful Paint | **2.5s at p75** `[confirmed]` | fail over 2.5s. This is a **floor**. Already passing means stop; chasing 1.1 seconds is spending engineering effort for no ranking return. |
| `media.video_host` | self-hosted video files | host on YouTube | fail on a self-hosted `<video>` with a large source |
| `media.transcript` | transcript published on the page | present when video is embedded | fail if absent. The highest-value and most-skipped video action, because models train on transcripts. |

**Media that earns citations:** original diagrams from your own data, screenshots of real
interfaces with real numbers, comparison tables. Stock photography does none of this, and
`media.py` flags likely stock by filename and CDN host.

---

## 7. E-E-A-T

Source: `course/18`. Corpus: `[s270]` and the Quality Rater Guidelines.

Not a score, not a direct ranking factor. It is the rater vocabulary approximated through
signals that happen to be measurable. **Trust is the centre.** Experience is what most
sites fail.

| id | Measures | Threshold | Verdict logic |
|---|---|---|---|
| `eeat.author_named` | a named author | not "Admin" or "The Team" | fail on absent or generic |
| `eeat.author_bio` | link to a real bio page | present | fail if the author name links nowhere |
| `eeat.author_schema` | `Person`/`Author` schema with `sameAs` | present | `review` |
| `eeat.dates` | publication and update dates | both honest and visible | `review` |
| `eeat.https` | scheme | HTTPS, no mixed content | fail on HTTP. A **confirmed** ranking factor and non-negotiable. |
| `eeat.about` | a real About page with real people | present | `review` |
| `eeat.contact` | working contact details | address, phone, email - not just a form | `review` |
| `eeat.limitations` | acknowledges what it does not do | at least one honest limitation | `review`. Balanced coverage including the limits of what you sell. Cheap, rare, and it is what "trust" concretely looks like on a commercial page. |

**The six honest-assessment questions**, surfaced as `review` on every audit. Most pages
fail three or more, and working through them is usually more valuable than the automated
rows above:

1. Who wrote this, and can I tell?
2. Is there evidence they have actually done it?
3. Are the claims sourced?
4. Can I verify the organization is real?
5. Does it acknowledge limitations?
6. If it were wrong, would there be any way to tell?

Note on authority: brand mentions correlate **0.664** with AI Overview citation against
**0.218** for backlinks `[s270]` `[practitioner]`. Correlational, one vendor, 2025. Useful
as a direction, not a number to build a proposal on.

---

## 8. Schema

Scope note: this skill checks only the schema types that are **on-page content
properties** - `Article`/`BlogPosting`, `FAQPage`, `HowTo`, `BreadcrumbList`,
`Person`/`Author`. Site-level and technical schema (`Organization`, `LocalBusiness`,
`Product`, `Service`) belongs to the technical skill, not here.

| id | Measures | Threshold | Verdict logic |
|---|---|---|---|
| `schema.parses` | every `application/ld+json` block is valid JSON | all parse | fail on a parse error, naming the block |
| `schema.types` | which `@type`s are present | reported | always `pass` with the list |
| `schema.required_fields` | required properties per type | validated locally with `jsonschema` | fail on a missing required field, naming it |
| `schema.faq_matches` | FAQ schema questions exist in the visible page | must match | fail on a schema-only question. Marking up content that is not on the page is a guidelines violation, not a clever trick. |
| `schema.howto_steps` | HowTo steps match the visible steps | must match | fail on mismatch |

**When generating schema, instruct the model to ask rather than invent.** The aruntastic
method carries a clause worth keeping verbatim: *"Make sure you've included all the required
and optional fields. If you're not sure of how to fill in a specific field ask me."* A
fabricated schema field is silently invalid - it does not error, it just quietly fails to
do anything - so an anti-hallucination clause is worth more here than almost anywhere else.

---

## What is deliberately not checked

Naming these matters as much as the checks themselves, because their absence would
otherwise read as a clean bill of health.

| Not checked | Why | Who owns it |
|---|---|---|
| Keyword density | Not a thing, and targeting a percentage produces exactly the over-optimization the helpful-content system catches | nobody, deliberately |
| A word-count target | Length is not a ranking factor; the right length is whatever covers the cluster and stops | nobody, deliberately |
| Meta keywords | Dead for over a decade | nobody |
| CWV beyond the floor | Failing hurts, exceeding buys nothing | technical skill |
| Crawl budget, robots.txt, sitemaps, rendering, hreflang, canonicals at site scale | Technical layer | technical skill |
| Backlinks, digital PR, brand mentions | Off-page layer | off-page skill |
| AI Overview presence, ChatGPT citation share | Not observable from any data source available here | AI-search skill, and it will hit the same wall |
| CTR, impressions, position, decay | Needs Search Console, which is not connected | returns `not connected` with export steps |

Citations `[sN]` resolve via `seo-advisor/_research/sources.json`, by the `index` field.
