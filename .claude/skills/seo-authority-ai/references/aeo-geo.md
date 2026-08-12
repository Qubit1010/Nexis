# OPTIMIZE mode: making a page citable

## The evidence ceiling, stated first

There is **exactly one peer-reviewed study** in this field. It found **three** content changes
that raise citation probability:

| Modifier | Lift | Tier |
|---|---|---|
| Adding expert quotes | **+41%** | `[peer-reviewed]` |
| Adding statistics | **+30%** | `[peer-reviewed]` |
| Adding inline citations | **+30%** | `[peer-reviewed]` |

Princeton GEO study, course/37. Three things follow, and all three are commercially useful:

1. **All three are writing, not markup.** No schema, no llms.txt, no crawler configuration.
2. **All three are forms of verifiable specificity.** A quote has an attributable source, a
   statistic is checkable, a citation points somewhere. Each gives a synthesis engine something
   concrete it can safely repeat *with attribution*.
3. **This is the ceiling of what is proven.** Everything past it is practitioner correlation, and
   an entire tooling category is built selling everything except these three.

---

## The rewriting pass

Run in this order. `authority.py --areas aeo` measures each one.

### 1. Answer first (BLUF)

State the conclusion in the first sentence, then explain. A section that builds to its conclusion
is a section whose conclusion never gets extracted.

> **Before:** "Renaissance faires have a long history in New England, dating back to..."
> **After:** "Example Faire is the largest renaissance faire in its region, running
> weekends from September 5 to October 25 on a 200-acre wooded site outside the city."

`aeo.answer_first` returns `review` with the first 60 words quoted. A script cannot tell a
conclusion from a preamble; read it.

### 2. Define the entity in the first 40-60 words

Say what the thing *is* before discussing it. Retrieval needs to know what it has found.

### 3. One expert quote, named, with a credential

Not "experts say". A named person with a stated credential, quoted directly. **If you are the
expert, quote yourself with your credential attached** - that is also the E-E-A-T argument.

`aeo.expert_quote` fails at zero quotations and returns `review` when a quotation exists without
an adjacent proper noun and credential token. It never auto-passes, because the difference
between an attributed quote and "experts say" is precisely what the study measured.

### 4. Three specific statistics, each sourced

"Most visitors enjoy it" is unusable. "526 reviews at a 3.6 average" is quotable. **Where the
number came from matters as much as the number** - an unsourced figure is not safely repeatable.

### 5. Inline citations, linking out

Link to where each claim came from. The instinct to hoard link equity works directly against
citation, and the equity being protected is worth less than the citation being forgone.

### 6. Self-contained units of 134-167 words

Each chunk should survive being pulled out alone, because being pulled out alone is exactly what
retrieval does. `aeo.answer_unit_length` fails over 250 words and flags under 134 as a stub.

### 7. No back-references

A section opening "As we discussed earlier, this approach..." is incoherent once extracted.
`aeo.unit_standalone` fails on these and it is a free, mechanical fix.

### 8. One question per heading, phrased as people ask it

Headings are strong retrieval anchors, and a heading matching a fan-out sub-query is a direct hit.
Fan-out is 5-11 sub-queries typically, 10-20 on deeper analysis.

### 9. A comparison table where the topic supports one

Genuinely one of the most extractable formats that exists. An engine answering "X vs Y" can lift a
well-built table nearly verbatim. `aeo.comparison_table` **fails** when absent and the target
query contains "vs", "versus", "best" or "compare".

### 10. Accurate `dateModified`, refreshed inside 90 days

Recency is a real selection input, and Perplexity deprioritises content over 90 days old. A date
change with no content change is not a refresh; that pattern is recognised and does not work.

---

## The tension worth knowing

course/39 notes an apparent conflict: 134-167 word answer units against Claude's preference for
long-form definitive guides. The resolution is not to pick one. It is **self-contained units
*within* comprehensive long-form pieces** - the page is long, each section stands alone.

Do not fragment a topic into ten thin pages to hit the word band. That works against you on
Claude and against topical coverage generally.

---

## What this mode must refuse

- **Schema as a citation lever.** Ahrefs: no uplift across 1,885 pages. Google's May 2026
  guidance: structured data is not required for AI Overviews. Route schema to `seo-technical` for
  rich results and entity clarity.
- **llms.txt as a deliverable.** See `what-not-to-do.md`.
- **"AI-optimized content" as a separate product.** The Princeton modifiers describe better
  writing, which is what good content already did.
- **A word-count target.** There isn't one. Answer coverage is the real question.
- **Any citation guarantee.**

---

## Where the ceiling actually is

Do the three Princeton modifiers. Structure for extraction. Build topical coverage (course/36),
entity clarity (course/40) and mentions (course/34). Keep the technical foundations sound so you
get crawled at all.

That is the entire defensible playbook, and it is much shorter than the category's marketing
implies. **The shortness is the point** - and saying so is the most commercially valuable thing
in this tier, because it is what a client cannot get from a vendor selling AI-visibility software.
