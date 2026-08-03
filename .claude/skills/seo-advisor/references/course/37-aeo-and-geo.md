# Authority, AI Search & Strategy - Section 37: AEO and GEO

*One peer-reviewed study, three content modifiers, and a great deal of vendor noise around them.*

**Bottom line:** The Princeton GEO study is the only peer-reviewed evidence in this field, and
it found three content changes that raise citation probability: **expert quotes +41%**,
**statistics +30%**, **inline citations +30%**. All three are about how you write, not what
you mark up. Almost everything else sold as AEO or GEO is vendor correlation.

---

## The terms, briefly

**AEO** (Answer Engine Optimization) and **GEO** (Generative Engine Optimization) are used
almost interchangeably. Some practitioners distinguish AEO as optimizing for direct answers
including featured snippets, and GEO as optimizing for generative synthesis specifically. You
will also see AIO and LLMO.

**The distinction does not matter and arguing about it is a tell.** The underlying work is the
same: make your content the thing an engine selects and quotes. Use whichever term your client
uses.

## The Princeton study

The strongest evidence available for any AI-visibility tactic, and worth knowing precisely
because you will be arguing against vendor claims that have none.

| Modifier | Citation probability lift |
|---|---|
| **Adding expert quotes** | **+41%** |
| **Adding statistics** | **+30%** |
| **Adding inline citations** | **+30%** |

`[peer-reviewed]`

**Three things to notice.**

**First, all three are content structure, not technical markup.** No schema, no llms.txt, no
crawler configuration. The intervention is writing differently.

**Second, they are all forms of verifiable specificity.** A quote has an attributable source. A
statistic is checkable. A citation points somewhere. The common factor is that each one gives
a synthesis engine something concrete it can safely repeat with attribution.

**Third, this is the ceiling of what is actually proven.** Everything past these three numbers
is practitioner correlation. Being clear about that distinction is the whole method from
Section 3.

## What that means for writing

The Princeton findings translate into a concrete rewriting pass:

**Add real quotes from real named people.** Not "experts say". A named person with a stated
credential, quoted directly. If you are the expert, quote yourself with your credential
attached, which is also the E-E-A-T argument from Section 18.

**Add specific numbers with sources.** "Most sites fail" is unusable. "**60% of searches end
without a click**" is quotable. Where the number came from matters as much as the number.

**Cite your sources inline.** Link out to where a claim came from. The instinct to hoard link
equity actively works against citation, and the equity you are protecting is worth less than
the citation you are forgoing.

## Structural changes that support extraction

Beyond Princeton, the corpus supports a set of structural practices. These are practitioner
tier, and they are consistent across enough independent sources to act on.

**Answer first, always.** BLUF structure: bottom line up front. State the answer in the first
sentence, then explain. A section that builds to its conclusion is a section whose conclusion
never gets extracted.

**Self-contained answer units of roughly 134 to 167 words.** From Section 36. Each chunk should
survive being pulled out alone.

**Define the entity in the first 40 to 60 words** of an informational section. Say what the
thing is before discussing it.

**One question per heading, phrased as people ask it.** Headings are strong retrieval anchors
and a heading that matches a fan-out sub-query is a direct hit.

**Comparison tables.** Genuinely one of the most extractable formats that exists. An engine
answering "X vs Y" can lift a well-built table nearly verbatim.

**Keep `dateModified` accurate** per Section 30. Recency is a real selection input, especially
on Perplexity.

## What the evidence does not support

Being precise here is what separates this from vendor content.

**Schema as an AI ranking lever.** Section 30 covered it: **Ahrefs found no uplift across 1,885
pages**, SearchAtlas found no correlation, and Google's own May 2026 guidance says structured
data is **not required** to appear in AI Overviews. Some vendors report 30 to 40% visibility
gains from schema. The causal tests do not find it. Implement schema for rich results and
entity clarity, not as a GEO tactic.

**llms.txt.** Section 40 covers it fully. Google explicitly ignores it and has compared it to
the keywords meta tag. Adoption is around 10% of domains. Do not sell it as a deliverable.

**"AI-optimized content" as a product.** There is no separate content type. The Princeton
modifiers describe better writing, which is what good content already did.

**Any vendor guarantee of AI citation.** Nobody controls selection, the systems change monthly,
and fan-out is non-deterministic. Anyone guaranteeing this is either mistaken or lying.

> **Why this matters:** GEO is where the largest gap between evidence and marketing currently
> sits in this industry. There is exactly one peer-reviewed study, it found three writing
> changes, and a whole tooling category has been built selling everything except those three
> changes. Knowing which is which is the most commercially valuable thing in this tier.

## The honest summary of AEO and GEO

Do the three Princeton modifiers. Structure content for extraction. Build topical coverage per
Section 36. Build entity clarity and brand mentions per Sections 34 and 40. Keep your technical
foundations sound so you get crawled at all.

That is the entire defensible playbook. It is much shorter than the category's marketing
implies, and the shortness is the point.

## Do this now

1. **Pick your most important page**, ideally one that came up in the Section 36 lab.
2. **Rewrite the opening as an answer.** First sentence states the conclusion. Move context
   below it.
3. **Add one real expert quote** with a named person and a credential. Yourself counts if you
   have the credential.
4. **Add three specific statistics with sources.** Replace the vaguest three claims on the page.
5. **Add inline citations** linking out to where each claim came from.
6. **Check every H2 answers one question**, phrased the way someone would ask it.
7. **Break the page into 150-word chunks and read each alone.** Rewrite any that make no sense
   in isolation.
8. **Add a comparison table** if the topic supports one.
9. **Define the main entity in the first 40 to 60 words.**
10. **Re-ask the Section 36 question a week later** and note any citation change. One page is
    not a measurement, but it starts the habit.

## Capstone step

Your top capstone page is restructured for extraction: answer-first opening, at least one
attributed expert quote, three sourced statistics, inline citations linking out, question-shaped
headings, standalone 150-word chunks, an entity definition in the opening, and a comparison
table where applicable.

## Key takeaways

- Princeton is the only peer-reviewed evidence: **expert quotes +41%, statistics +30%, inline
  citations +30%.** All three are writing changes, not markup.
- The common factor is verifiable specificity. Give a synthesis engine something concrete it
  can safely repeat with attribution.
- Answer first, self-contained 134 to 167 word units, question-shaped headings, comparison
  tables, accurate dates.
- Schema, llms.txt and "AI-optimized content" as a product are not supported by the causal
  evidence. Knowing that is commercially valuable.
