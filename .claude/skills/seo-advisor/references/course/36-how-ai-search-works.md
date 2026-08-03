# Authority, AI Search & Strategy - Section 36: How AI Search Works

*One prompt becomes ten to twenty searches, and the winner is decided before your page is ever read.*

**Bottom line:** AI search does not rank pages, it retrieves passages and synthesizes an
answer. A single prompt fans out into **10 to 20 sub-queries**, Google narrows **200 to 500
candidate documents down to 5 to 15 citations**, and the overlap between ranking in the
organic top 10 and being cited has collapsed from **92% in mid-2025 to roughly 38% in early
2026**. Ranking first no longer implies being quoted.

---

## The mechanism, in one pass

Traditional search: query goes in, an ordered list of ten pages comes out, you click one.

AI search runs a **multi-stage pipeline**:

1. **Interpretation.** The system works out what you actually mean, including implicit
   sub-questions you did not ask.
2. **Query fan-out.** Your prompt is expanded into multiple synthetic sub-queries run in
   parallel.
3. **Retrieval.** Each sub-query pulls candidate documents from an index.
4. **Selection.** Candidates are narrowed hard. **200 to 500 documents down to 5 to 15
   cited sources.** `[practitioner]`
5. **Synthesis.** A model writes one answer from the selected passages and attributes some of
   them.

**The important structural point: you are not competing for a position, you are competing to
be selected as source material.** Everything in Sections 37 through 40 follows from that.

## Query fan-out

The single most important concept in this tier.

A prompt expands into **5 to 11 sub-queries** typically, **10 to 20** on deeper analysis, and
**hundreds of parallel searches** for deep-research modes. `[practitioner]`

Ask an engine "what's the best CRM for a small agency" and behind the scenes it may run:
what is a CRM, best CRM for small business, CRM pricing comparison, CRM for agencies
specifically, HubSpot vs Pipedrive, CRM features small teams need, CRM reviews 2026, and a
dozen more.

**You do not need to win the original query. You need to be the best answer to several of the
sub-queries.** That is a completely different optimization target than a keyword ranking, and
it is why keyword-level thinking under-performs here.

**AI queries are also far longer:** **70 to 80 words on average versus 3 to 4** for a
traditional search, a **17 to 26x complexity increase**. People type full situations into AI,
not keywords. `[practitioner]`

## The coverage finding

This is the most actionable number in the entire AI-search block.

**Sites with 80%+ topical coverage of their domain retain 85.4% of AI visibility** despite
fan-out instability. `[practitioner]`

The reasoning is direct. Fan-out is unpredictable: the same prompt generates different
sub-queries on different runs. A site with one strong page on a topic wins only when a
sub-query happens to match that page. A site that covers the whole topic area comprehensively
gets caught by whichever sub-queries fire.

**Depth of coverage is the durable strategy. Individual page optimization is not.** This is
the Section 15 topical cluster argument, restated with an AI-specific number attached, and it
is the reason clusters were worth building before AI search existed and are worth more now.

## The overlap collapse

| Period | Organic top-10 to AI citation overlap |
|---|---|
| **Mid-2025** | **92%** |
| **Early 2026** | **~38%** |
| **AI Mode specifically** | **14 to 17%** |

`[practitioner]`

This is the number that justifies AI search being its own discipline rather than a footnote
to SEO.

In 2025, optimizing for Google essentially optimized for AI citation as a side effect. That
is no longer true. Roughly six in ten cited sources are now pages that do not rank in the
organic top ten for the query being answered.

**The practical read:** your ranking report and your citation report are now two different
reports measuring two different things, and a client can be winning one while losing the other.
Section 41 handles measuring both.

**Do not overcorrect.** Ranking still matters, both for direct traffic and for entering the
candidate pool. The collapse means AI visibility needs its own work, not that classic SEO
stopped mattering.

## Retrieval favors passages, not pages

Because synthesis works from retrieved passages, the unit of competition is smaller than a
page.

The corpus is specific: content should be structured as **self-contained answer units of
roughly 134 to 167 words**. `[practitioner]`

An answer unit is a chunk that makes sense in isolation. It states what it is about, answers
one thing, and does not depend on the paragraph above it for context. A section that opens
"As we discussed earlier, this approach..." is unusable as a retrieved passage because
extracted alone it means nothing.

This is why Sections 12 and 14 emphasized standalone section structure. Section 37 turns it
into a concrete rewriting method.

## What this changes about strategy

| Traditional SEO | AI search |
|---|---|
| Compete for a position | Compete to be selected as source material |
| Optimize a page for a query | Cover a topic well enough to catch many sub-queries |
| Ranking is the outcome | Citation is the outcome, and ranking does not predict it |
| The page is the unit | The passage is the unit |
| Links are the authority signal | Mentions correlate ~3x more strongly (Section 34) |

Both columns are live. You are running two overlapping games, not replacing one with the
other.

> **Why this matters:** most people encountering AI search reach for a tactic, usually schema
> or llms.txt, because a tactic is easy to sell and easy to implement. The mechanism tells you
> why those are minor. Selection happens across many fan-out sub-queries from a pool of
> hundreds of candidates, which rewards comprehensive topical coverage and clear extractable
> passages far more than any markup.

## Do this now

1. **Pick your most important commercial query.**
2. **Ask ChatGPT, Perplexity and Google AI Mode the same question**, phrased as a real person
   would in 70 words, not as a keyword.
3. **Write down every source each one cited.** Note how much they overlap. They usually do not.
4. **Check whether the cited pages rank in Google's top 10** for your query. Most will not.
   That is the 38% collapse in front of you.
5. **List the sub-questions each answer covered.** That is observable fan-out, and it is your
   real content target list.
6. **Score your own topical coverage.** Of the sub-questions you just listed, how many do you
   have a genuinely good page for? That fraction is your coverage estimate against the 80%
   benchmark.
7. **Open your best page and check its passages.** Does any 150-word chunk stand alone and
   answer one thing? If every section depends on the one above it, note that for Section 37.
8. **Record which platform cited you, if any.** This is your citation baseline.

## Capstone step

You have traced one core query's fan-out across three engines, recorded the cited sources and
whether they rank organically, listed the observable sub-questions as a content target list,
and scored your capstone site's topical coverage against the 80% benchmark.

## Key takeaways

- AI search retrieves passages and synthesizes. You compete to be selected as source material,
  not to hold a position.
- Query fan-out expands one prompt into **10 to 20 sub-queries**. Win several sub-queries, not
  the original one.
- **80%+ topical coverage retains 85.4% of AI visibility.** Comprehensive clusters beat
  optimized individual pages because fan-out is unpredictable.
- Organic top-10 to citation overlap fell from **92% to ~38%**. Ranking and citation are now
  two different reports, and you need both.
