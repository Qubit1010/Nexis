# The kill list

Read before delivering. Every entry is something this skill could easily say, that would be
wrong, and that a client or a competitor could catch.

---

## 1. Never report a citation rate from fewer than three runs

`push_sheet.py` blocks it, but the reasoning has to survive the person who reaches for `--force`.

Measured here 2026-08-08, two ChatGPT runs of one prompt seconds apart:

| | run 1 | run 2 |
|---|---|---|
| named first | **HubSpot** | **Pipedrive** |
| sources returned | **0** | **50** |
| cited-domain overlap | **Jaccard 0.00** | |

arXiv 2604.07585 decomposed 12,933 responses: within-prompt resampling is **34.8%** of total
variance, brand-in-context 29.6%, query language 26.5%, and **brand identity - the thing being
measured - is 1.5%.**

**Never say:** "You are not cited by ChatGPT."
**Say:** "Across three runs of four prompts, you were cited in two of twelve."

## 2. Never render a rate as a bare percentage

"33%" from three samples implies a precision that does not exist. At 2 of 3 the 95% Wilson
interval is **[0.208, 0.939]**. The format is **"cited in 2 of 3 runs"**, always.

And never compare those rates month over month at n=3. Two intervals that wide overlap almost
completely; a change from 1/3 to 2/3 is not a trend, it is the same measurement twice.

## 3. Never collapse "not cited", "not sampled" and "not retrievable"

Three different findings with three different fixes:

| Finding | What it means | Fix |
|---|---|---|
| not retrievable | robots.txt blocks the bot, or the raw HTML is empty | tier 1, free, usually minutes |
| not sampled | nobody measured | run `aivis.py` |
| not cited | measured, and the engine chose someone else | the actual work |

## 4. Never collapse "named" and "cited"

A live measurement on a client's renaissance faire: **named in 3 of 3 AI Overview runs, cited in 1 of 3**,
with Tripadvisor cited instead. Being recommended by name while a third party gets the link is a
real, specific, fixable finding. One boolean would have hidden it.

## 5. Never sell llms.txt

No engine honors it. Google explicitly ignores it and has compared it to the keywords meta tag.
Adoption is ~10% of domains across a 300,000-site sample. There is no measured citation benefit.

course/40 treats charging for it as the clearest available test of whether an SEO provider is
reading evidence or reading marketing.

**Also do not bill for removing one.** If a client already has an llms.txt, the correct action is
none. Leaving it costs nothing.

## 6. Never claim schema causes AI citation

Ahrefs found **no uplift across 1,885 pages**. SearchAtlas found no correlation. Google's own May
2026 guidance says structured data is **not required** to appear in AI Overviews. Vendors claim
30-40% gains; the causal tests do not find it.

Implement schema through `seo-technical` for rich-result eligibility and entity clarity. Never as
a GEO tactic, and never in the same sentence as a citation promise.

## 7. Never state r = 0.664 as causal

Branded web mentions correlate with AI Overview citation at **r = 0.664**; backlinks at
**r = 0.218**. `[practitioner, correlational]`. It is the strongest argument for mention work and
it is still a correlation. Brands that get mentioned a lot are also brands that are good.

**Say:** "mentions correlate about three times more strongly than backlinks."
**Never:** "mentions cause citation."

## 8. Never quote 58% as an average

CTR drops **up to 58%** when an AI Overview is present. course/38 is explicit that this is a
**ceiling, not an average**. Informational queries lose most; transactional, navigational and
complex-commercial lose far less. Quoting it as typical overstates the damage and gets caught.

## 9. Never quote the 520% photos figure

"100+ photos get 520% more calls" traces to vendor research citing Google, not to a Google
publication. course/35 flags it. There are plenty of defensible local numbers; use those.

## 10. Never present a DR-qualified prospect list

There is no free backlink index. Referring domains, DR/DA, traffic estimates, anchor distribution
and toxicity all return `unknown`, and `push_sheet.py` invariant 4 blocks any link-prospect row
carrying such a number without a named source.

**This skill produces a prospect list, never a qualified one.** Say that in the report. Then point
at the reclamation queue, which is real, free to build, and converts at 30-50%.

## 11. Never guarantee an AI citation

Nobody controls selection. The systems change monthly. Fan-out is non-deterministic and the
overlap between ranking and citation collapsed from 92% to ~38% in under a year, and to 14-17% in
AI Mode. Anyone guaranteeing this is mistaken or lying.

## 12. Never block retrieval bots as a default

OAI-SearchBot, ChatGPT-User, Claude-SearchBot and PerplexityBot are how a page gets **cited**.
GPTBot, ClaudeBot and CCBot are **training**. Blocking the first set to stop the second is the
single most expensive misconfiguration in this tier: it forfeits the citations and keeps the
scraping.

And never present robots.txt as enforcement. It is a request. Real enforcement is WAF or
server-level rules, evaluated before robots.txt is read.

## 13. Never let the Findings tab fill with markup

The gravitational pull toward schema, llms.txt and meta-level fixes is enormous because they are
easy to check, easy to fix and easy to bill. If the Findings tab is mostly markup items, the skill
has failed at its own thesis. The tier order and invariant 3 exist to prevent it structurally;
notice when you are fighting them.

## 14. Never rewrite a page that no engine may fetch

Tier 1 before tier 4. Adding expert quotes to five pages behind a `Disallow: /` for
OAI-SearchBot is work the client pays for and no engine ever sees.

## 15. Never state a fan-out number as observed

Query fan-out is **5-11 sub-queries typically**, 10-20 on deeper analysis. Those come from the
corpus, not from measurement - the actor returns an empty `queryFanOut` on AI Overviews. The PAA
join in `coverage.paa_answered` is a **free proxy**, and the report must call it a proxy.
