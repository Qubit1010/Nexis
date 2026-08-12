# Scoring and prioritisation

The trap at this stage is optimising for winnability and ending up with a list of easy,
irrelevant terms that never produce a customer. A rankable keyword attracting people who
will never buy is a cost, not an asset.

The formula in circulation, useful as a way of thinking rather than as arithmetic:

> **Priority = (Business Relevance x Conversion Intent) / Competitive Feasibility**
> `[practitioner]` [s288]

The load-bearing term is business relevance. High-intent, mid-to-low-volume terms convert
**5-10x** better than broad informational ones `[practitioner]` [s127].

---

## The four columns

Score **Relevance** and **Intent value** yourself, 1-5, fast and by instinct. By this phase
you have read the persona and the strategic foundation; you know the business. Slow scoring
is not more accurate scoring.

### Relevance (1-5) - you
**"If this ranked first tomorrow, would it produce enquiries?"**

| Score | Meaning |
|---|---|
| 5 | Directly describes what they sell. A first-place ranking produces enquiries this month. |
| 4 | Adjacent to the offer. The searcher is a plausible customer. |
| 3 | Right audience, wrong moment. Useful for awareness, not for revenue. |
| 2 | Overlaps the industry but not the buyer. |
| 1 | Same words, different world. Students, competitors, job seekers. |

The most common scoring error is generosity here. If a 5 does not feel like it would ring
the phone, it is a 3.

### Intent value (1-5) - you
Where the query sits in the six intents, weighted by how close it is to a decision.

| Score | Intent |
|---|---|
| 5 | Transactional, or Commercial investigation with a clear buying signal |
| 4 | Commercial investigation |
| 3 | Local (high when they serve a geography, otherwise lower), or Informational with strong buying proximity |
| 2 | Informational |
| 1 | Navigational to someone else's brand, or post-purchase support |

### Click availability - from Phase 4, mostly unknown
Comes back `unknown` from the script because AI Overview presence is not observable (see
`serp-read.md`). **Check the top 20 manually in incognito** and fill it in for those only.
Below the top 20 it is not worth the time.

### Winnability (1-5) - script proposes, you override
The manual SERP read, not a tool score. Override it when questions 3 and 6 of the read
disagree with the number, and say why.

---

## The sort

```
Priority = Relevance x Intent value        (range 1-25)
```

**Sort by that. Use click availability and winnability as tiebreakers only.**

**Never sort by volume.** Beyond the fact that this skill measures no volume, `course/07`
is explicit: volume is modelled from clickstream and bucketed advertiser data, differs up
to **30x** between tools [s290], hides seasonality, hides the click economy, and reports
zero for the roughly **15% of daily searches that are entirely new** [s290]. A zero-volume
row is evidence of no measurement, not of no demand.

A volume-sorted list and a relevance-sorted list look completely different, and the second
one is the one that produces customers.

### Reading the bands

| Priority | Meaning |
|---|---|
| 20-25 | The core. Usually 5-15 keywords. If there are 60, Relevance was scored generously. |
| 12-19 | The real working set. Most of the content plan lives here. |
| 6-11 | Supporting and awareness content. Build after the above earns its keep. |
| 1-5 | Do not build for these. Keep them in the sheet as evidence of what was considered and rejected. |

### The two tiebreaker patterns worth knowing

**High priority, low winnability.** Right target, wrong time. These belong in the plan with
a note that they need authority first - usually the pillar page and the cluster around it.
Do not delete them; the map should show where the client is going.

**Mid priority, very high winnability (UGC on page one).** These are the fastest wins
available and are routinely skipped because the priority score looks unremarkable. A
Reddit thread ranking in the top five means Google is actively looking for a better page.
Flag them explicitly in the report as quick wins, separately from the priority ranking.

---

## What good output looks like

After scoring, the top 30 should be **recognisably about this client's business**. If it
reads like a generic industry keyword list, the persona was not used - go back to Phase 1.

Then **show the top 30 to the user before clustering.** If the ranking is wrong, everything
after it is wrong, and this is the cheapest place to find out.

Citations `[sN]` resolve via `seo-advisor/_research/sources.json`.
