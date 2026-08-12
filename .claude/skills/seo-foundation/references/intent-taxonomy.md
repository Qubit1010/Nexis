# Search Intent - the six types

Intent mismatch costs an estimated **35-40% of content effectiveness** `[practitioner]`
[s287], and it behaves like a ceiling rather than a penalty: a service page targeting a
query where page one is ten listicles does not rank badly, it does not rank.

Most courses teach four intents. This uses six. **Local** and **Generative AI intent** were
added because both now carry real volume and neither behaves like the other four.

---

## The six

| Intent | The user wants | Trigger words | What ranks | Page to build |
|---|---|---|---|---|
| **Informational** | to know | how to, what is, why, guide, tutorial, examples | blog posts, guides, videos | article, how-to, explainer |
| **Navigational** | to go somewhere specific | brand names, "login", product names | the brand's own pages | your own brand pages - rank #1 or lose control of your name |
| **Commercial investigation** | to compare before deciding | best, top, review, vs, comparison, alternatives | listicles, comparisons, review sites | comparison page, "best X for Y", alternatives page |
| **Transactional** | to act now | buy, price, cost, quote, hire, book, near me, discount | product/service/category pages | service or product page with a clear next step |
| **Local** | a provider near them | near me, in [city], "open now", [service] [city] | map pack, local directories, local service pages | location or service-area page, plus a Google Business Profile |
| **Generative AI intent** | a synthesised answer to a complex question | long conversational phrasings, multi-part questions | AI Overviews, answer engines | self-contained extractable answer blocks inside a deeper page |

**Commercial investigation is usually the highest-value and least-served bucket.** High-intent
mid-volume terms are reported to convert **5-10x** better than broad informational ones
`[practitioner]` [s127]. When a client has one obvious gap, it is almost always this one -
they have service pages for transactional and blog posts for informational, and nothing for
the comparison stage where the decision actually gets made.

### On Generative AI intent

Roughly **37.5%** of ChatGPT queries are generative in shape `[practitioner, single source]`
[s247] - treat that number as directional. What matters operationally is that these queries
average **70-80 words** against 3-4 for traditional search [s110], return **zero volume in
every tool**, and get expanded into **5-11 sub-queries** before being answered [s271, s121].

You cannot find these in a keyword tool. You find them by asking an answer engine what
sub-queries it would run, and by reading how customers phrase things in communities.

---

## Classifying: read the SERP, not the words

Trigger words suggest an intent. The SERP decides it. Where they disagree, the SERP is
right, because it is Google's own answer to what the query means.

Run `serp_features.py` and read `dominant_content_type` and `content_type_mix`:

1. **What page type dominates?** Count them. Eight of ten listicles means commercial
   investigation, and a service page cannot rank there whatever you write.
2. **Which features are present?** A map pack means local. Heavy PAA means the question
   layer matters. Shopping results mean transactional.
3. **Who ranks?** Brands only versus independents is your real difficulty read, not a score.
4. **What shape are the titles?** "Best X for Y" versus "How to X" versus a bare product name.

**Worked example.** "crm software" looks informational by its words. Page one is dominated
by vendor homepages and comparison listicles, so it is commercial investigation, and an
explainer article aimed at it will underperform however good it is.

**Split intent.** Some SERPs genuinely mix - half listicles, half product pages. Google is
hedging because searchers want different things. Note it, pick the dominant half, and say
in the report why the other half was not chosen. Do not build one page trying to serve both.

---

## Intent to page type

| Intent | Page | Primary measure of success |
|---|---|---|
| Informational | article, guide, FAQ | rankings, assisted conversions, AI citations |
| Navigational | brand pages | owning position 1 for your own name |
| Commercial investigation | comparison, "best X", alternatives | enquiries, demo requests |
| Transactional | service, product, pricing, contact | direct conversions |
| Local | location and service-area pages | map pack presence, calls, direction requests |
| Generative AI | extractable blocks inside deeper pages | citations and mentions in AI answers |

---

## The rule that makes clustering work

> **One search intent = one page = one keyword cluster.**

Two queries with the same intent belong on one page no matter how differently they are
worded. Two queries with different intents need two pages even when the words are nearly
identical. This is why clusters form from **shared SERP results rather than shared
vocabulary** - see `clustering-and-mapping.md`.

---

## Mapping the persona's four buckets onto these six

`strategic-foundation`'s persona groups questions into Informational, Commercial
investigation, Transactional, and Post-purchase.

- The first three map straight across.
- **Post-purchase** has no slot here. Those questions are usually Informational for search
  purposes, and they matter for retention and support content rather than acquisition. Keep
  them, tag them Informational, and score their Intent value low unless the client sells
  renewals or add-ons.
- **Local** and **Generative AI intent** have no persona equivalent. Add Local if the client
  serves a geography; derive the AI bucket from fan-out and community phrasing in Phase 3.

Citations `[sN]` resolve via `seo-advisor/_research/sources.json`.
