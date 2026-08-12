# The kill list

Run this over the whole deliverable before showing it to anyone.

---

## Numbers you must not invent

**Search volume.** There is no free volume API in 2026. Not from Serper, not from
autocomplete, not from anywhere this skill touches. The Volume column stays empty and
labelled "not measured". If a volume figure appears anywhere in the output, something
hallucinated it, and it will silently distort every priority score built on top.

**Keyword difficulty as a 0-100 score.** No such metric exists at Google; it is a vendor
construct built mainly from incumbent link profiles [s290]. This skill produces a
winnability read from the live SERP with stated reasons. Never dress that up as a KD score,
and never quote one from memory.

**AI Overview presence.** Not returned by this data source. Verified across query types.
Report `unknown` and tell the user to check in incognito. Never infer it from the answer
box, the PAA count, or the query's shape.

**Domain Rating, Domain Authority, traffic estimates, backlink counts.** No free source.
`sitelinked_results` is a proxy for brand prominence and must be described as one.

**Ranking predictions and traffic forecasts.** "This should get you to page one in three
months" has no basis in anything measured here.

---

## Method failures

**Sorting by volume.** The single most common failure. It produces a list of broad terms
that are unwinnable, unspecific, and full of people who will never buy. Sort by Relevance x
Intent value. This holds even when the client asks for a volume sort - explain why, then
show them the difference between the two orderings.

**One page per keyword.** Splits what should be one strong page into several weak ones.
Cluster first.

**Clustering by wording.** "seo audit" and "seo audit tool" look nearly identical and are
different intents. Cluster by shared SERP results.

**Accepting the clusters without reading `borderline_pairs`.** Those are the judgment calls.
The script surfaces them precisely so a human looks.

**Letting one URL serve several clusters.** That is cannibalization, not efficiency.
`push_sheet.py` blocks it, and forcing past it without documenting why is how a map becomes
a wish list.

**Treating zero-volume as zero demand.** Roughly 15% of daily searches are entirely new
[s290], and AI fan-out sub-queries and long conversational phrasings return zero in every
tool. Zero is evidence of no measurement.

**Skipping the persona.** Keywords built from an industry term instead of customer language
produce a list that would fit any competitor equally well. If the top 30 is not recognisably
about *this* client, go back to Phase 1.

**Optimising for winnability.** Easy irrelevant keywords are a cost. Relevance first,
winnability as a tiebreaker.

**Running 200 SERPs without saying what it costs.** Credits are finite and the first Serper
key is already exhausted. State the number before spending it.

---

## Scope

This skill covers **Tier 1 only**: audience grounding, competitors, intent, SERP reading,
keyword finding and judging, clustering, mapping, and the measurement baseline.

Not here, on purpose - the user is building separate execution skills for each:

| Out of scope | Where it goes |
|---|---|
| On-page optimisation, titles, metas, headings, internal linking execution | its own skill; `seo-advisor` for strategy |
| Technical SEO, crawling, indexing, Core Web Vitals, schema | `website-audit-system` to run it, `seo-advisor` for strategy |
| Off-page, link building, digital PR | `seo-advisor` |
| AI search execution, AEO/GEO, llms.txt | `seo-advisor` |
| Writing the actual article | `blog-writer` |

Producing the map and then drifting into on-page recommendations makes the deliverable
vaguer, not more generous. Name the handoff instead.

---

## Claims to leave alone

**Do not restate `seo-advisor`'s numbers as if measured here.** Cite `[sN]` and let it own
the corpus. The two drift apart the moment this skill starts carrying its own copies.

**Do not present correlation as causation.** "Bidirectional linking correlates with 2.7x AI
citation probability, single-vendor practitioner finding" is honest. "Bidirectional linking
causes 2.7x more citations" is not.

**Do not claim keyword research improves rankings on its own.** It decides what to build.
The ranking comes from the page.

**Tier every load-bearing number.** `[confirmed]` for Google documentation and
peer-reviewed sources, `[practitioner]` for vendor blogs and correlation studies. The
underlying corpus is 18 confirmed against 302 practitioner, which is the honest shape of
this field.

---

## Delivery

**Never mention NexusPoint or Aleem** in the client's foundation. It is their document.

**No em dashes in body text.** Headings may use them. Commas or periods otherwise.

**No emojis.**

**Every number resolves** to a measurement made here, an `[sN]` citation, or a named
assumption. If it does none of those three, cut it.

**Say what you could not establish.** The report ends with that section for a reason. A
foundation with three honest gaps is more useful than one with three invented certainties,
because the client can act on a gap.
