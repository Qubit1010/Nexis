# The check contract

This file owns the thresholds. `authority.py` and `aivis.py` implement them. The contract is
one-directional: a number moves here first, then in the script. If they disagree, this file is
right and the script is a bug.

Every threshold traces to a section of seo-advisor's course, which carries its own evidence tier.
Those tiers are reproduced rather than flattened, because the difference between `[peer-reviewed]`
and `[practitioner, single vendor]` is the difference between a finding and a strong opinion, and
a client is entitled to know which one they are holding.

**Citation note.** seo-advisor's corpus is 320 sources, 18 confirmed against 302 practitioner.
`[sN]` indices are NOT portable between skills (blog-writer's 83-source corpus uses the same
notation for different sources) and in seo-advisor's `sources.json` the lookup is by the `index`
field, not list position - `sources[N-1]` is wrong for 256 of 320 entries. This skill therefore
cites `course/NN` plus the tier, which is stable. The one exception, named in full because it
wins arguments: **the Princeton GEO study, `[peer-reviewed]`, course/37.**

**Four verdicts.** `pass` / `fail` / `review` / `unknown`. `review` and `unknown` are first-class:
a judgment call and a missing credential are both real answers, and collapsing either into `pass`
is how an audit hands a client a confidently wrong document.

---

## The tier order

Tier 3 inherits course/21's stated pyramid. Tier 4 has no explicit one, so this skill **derives**
one from course/36's five-stage retrieval pipeline (interpretation, fan-out, retrieval, selection,
synthesis) and says so. The property that makes it a real order is the same as seo-technical's:
**a failure at a lower layer invalidates the work above it.**

| Tier | Layer | Sections | Why nothing above it matters until it holds |
|---|---|---|---|
| 1 | Retrievability | 39, 40 | Blocked or unindexed means not a candidate document at all |
| 2 | Entity clarity | 40 | An entity that cannot be resolved cannot be attributed |
| 3 | Topical coverage | 36 | Fan-out is unpredictable; one page catches one sub-query |
| 4 | Extractability | 37, 38 | In the candidate pool and never selected |
| 5 | Mentions and platforms | 34 | The selection correlate |
| 6 | Links | 32, 33 | Gets you into the pool. Expensive. |
| 7 | Local *(conditional)* | 35 | **Promotes to tier 2 when `local.applicable` passes** |
| 8 | Measurement | 41 | Built last, baselined first |

`push_sheet.py` blocks a write that inverts this order. Rewriting pages for extraction on a site
whose robots.txt forbids the retrieval bots is polishing something no engine may fetch.

---

## 1. Retrievability (tier 1) - course/39, 40

| Check | Threshold | Tier | Verdict rule |
|---|---|---|---|
| `ai.policy_inverted` | never block retrieval while allowing training | `[practitioner]` | **`fail`.** The exact inversion course/40 names, and the most expensive single mistake in this tier: it forfeits the citations while keeping the training scrape. Names both offending bots. |
| `ai.retrieval_bots_allowed` | OAI-SearchBot, ChatGPT-User, Claude-SearchBot, PerplexityBot all allowed | `[practitioner]` | `fail` if any is disallowed, naming which. Unambiguous - these are how you get cited. |
| `ai.training_bots_policy` | GPTBot, ClaudeBot, CCBot blocked | `[practitioner]` | **`review` always.** A business decision, not a defect. Evidence carries the asymmetry: Googlebot crawl-to-referral ~**5:1**, Anthropic's training crawler peaked at **70,900:1**. |
| `ai.google_extended_documented` | a deliberate, written decision | `[practitioner]` | `review`. Gemini training opt-out. **Does not affect Search ranking** - say so, because most people assume it does. |
| `ai.no_deprecated_agents` | no `anthropic-ai` | `[practitioner]` | `fail`. Deprecated; live agents are ClaudeBot and Claude-SearchBot. A config citing it is issuing broken instructions. Reads `crawl.fetch_robots()`. |
| `ai.robots_is_not_enforcement` | - | `[practitioner]` | `review` whenever any block is declared. robots.txt is a request, not a lock. Real enforcement is WAF or server-level IP rules, evaluated **before** robots.txt is read. |
| `ai.llms_txt` | - | `[practitioner]` | **Absent -> `pass`**, "correctly absent". **Present -> `review`**, "harmless, leave it, do not bill for it". **Never `fail`.** See the refusal below. |
| `bing.indexed` | present in Bing's index | `[practitioner]` | **`unknown`** with the manual route. course/39 calls this the highest-value ten minutes in the section, and it needs the client's own free account. |
| `bing.sitemap_submitted` | sitemap submitted to Bing | `[practitioner]` | `unknown`. Manual. IndexNow is free and needs no account. |

**Why Bing is tier 1 and not an afterthought.** ChatGPT retrieves from Bing's index. Roughly
**90% of its citations come from pages ranked 21+ on Google**, so Google position is close to
irrelevant there and Bing presence is a precondition. A site absent from Bing cannot be cited by
ChatGPT no matter how good the content is.

**The llms.txt refusal, stated once.** No engine honors it. Google explicitly ignores it and has
compared it to the keywords meta tag. Adoption is around **10% of domains** across a 300,000-site
sample. There is no measured citation benefit. The one genuine use is developer documentation for
coding assistants. course/40 treats charging for it as the clearest available test of whether an
SEO provider is reading evidence or reading marketing. **Do not sell it. Do not remove one that
already exists** - it costs nothing and removing it is also billable work with no benefit.

---

## 2. Entity clarity (tier 2) - course/40, 34

| Check | Threshold | Tier | Verdict rule |
|---|---|---|---|
| `entity.wikidata_qid` | a Q-number exists and is the right one | `[practitioner]` | `pass` on a match whose description fits. **`review` when a same-name or similar entity outranks it** - the disambiguation risk is real and measured: a live lookup for "Example Faire" returned *Bristol* Renaissance Faire first. `fail` if none and the brand plausibly qualifies. `unknown` on API error. Free, no key. |
| `entity.kg_recognized` | a KGMID plus a confidence score | `[practitioner]` | **`unknown` today** - the Knowledge Graph Search API is disabled on this Google Cloud project (verified 403 `SERVICE_DISABLED`). Carries the enable URL. Once enabled: `pass` with `resultScore`, `fail` on no match. Free at **100,000 calls/day**. |
| `entity.home_declared` | one canonical Entity Home with a stable `@id` | `[practitioner]` | `review`. Usually the About page. Which page is definitive is a judgment call. |
| `entity.sameas_present` | `sameAs` on Organization | `[practitioner]` | `fail` if Organization schema exists with no `sameAs`. Cross-references seo-technical's `schema.organization_sameas`. |
| `entity.sameas_resolve` | every `sameAs` URL returns 200 | measured here | `fail` on any 404 or redirect-to-homepage. Cheap, free, and nobody checks it - a `sameAs` pointing at a dead profile actively muddies the entity it is meant to clarify. |
| `entity.description_consistency` | one canonical one-sentence description, identical everywhere | `[practitioner]` | `review` with the variants side by side. Mechanical to gather, judgment to rule on. |
| `entity.founder_name_consistent` | identical spelling and format everywhere | `[practitioner]` | `review` with the variants. Trivial to fix, and it fragments the entity when wrong. |

**Recognition speed, fastest to slowest:** Wikidata, schema disambiguation, Knowledge Panel,
Wikipedia. Timeline is weeks to months, not days. Frame entity work as infrastructure, never as a
quick win.

---

## 3. Topical coverage (tier 3) - course/36

| Check | Threshold | Tier | Verdict rule |
|---|---|---|---|
| `coverage.paa_answered` | every PAA question on the target SERPs has an answering heading somewhere on the site | measured here | **`review` with the unanswered list - that list is the content queue.** PAA is free from cached Serper; matching it against the crawled heading corpus is mechanical. The closest free proxy to observable fan-out that exists. |
| `coverage.subquery_ratio` | **80%+** of observed sub-questions covered | `[practitioner]` | `review` always, with the fraction. **Sites with 80%+ topical coverage retain 85.4% of AI visibility.** That is the argument, not the measurement - "genuinely good coverage" is judgment. |
| `coverage.cluster_completeness` | pillar plus **8-15** cluster pages, bidirectionally linked | `[practitioner]` | Joins seo-foundation's keyword map. `fail` under 8 for a claimed pillar, `pass` 8-15, `review` above. |

**The numbers that make this tier make sense.** AI search compresses **200-500 candidate documents
down to 5-15 cited sources**. Fan-out is **5-11 sub-queries typically**, 10-20 on deeper analysis.
AI queries average **70-80 words against 3-4** for a traditional search. And the organic-to-citation
overlap collapsed from **92% in mid-2025 to ~38% in early 2026**, and **14-17% in AI Mode**. That
last number is why ranking is no longer a proxy for being cited, and why this skill exists.

---

## 4. Extractability (tier 4) - course/37, 38

**The only `[peer-reviewed]` evidence in the entire tier.** The Princeton GEO study found three
content changes that raise citation probability. All three are writing, not markup.

| Check | Threshold | Tier | Verdict rule |
|---|---|---|---|
| `aeo.expert_quote` | at least one quote from a **named person with a stated credential** | **`[peer-reviewed]` +41%** | `fail` at zero quotations. **`review`** when a quotation exists but carries no adjacent proper noun and credential token. **Never auto-`pass`** - "experts say" is precisely what the study distinguishes from an attributable quote. |
| `aeo.statistics` | **3+** specific numbers, each sourced | **`[peer-reviewed]` +30%** | `fail` under 3. `review` at 3+ when unsourced (a numeral with no citation link and no named source in the sentence). |
| `aeo.inline_citations` | outbound links to where each claim came from | **`[peer-reviewed]` +30%** | `fail` at zero outbound editorial links in the body, excluding nav, footer and social. The instinct being corrected is link-equity hoarding: the equity protected is worth less than the citation forgone. |
| `aeo.answer_first` | first sentence states the conclusion (BLUF) | `[practitioner]` | **`review` always**, first 60 words quoted. A script cannot tell a conclusion from a preamble. |
| `aeo.entity_defined_early` | the main entity defined in the first **40-60 words** | `[practitioner]` | `review` with the opening attached. |
| `aeo.answer_unit_length` | **134-167 words** between headings | `[practitioner]` | `pass` 134-167. `review` 168-250, and `review` under 134 (a stub is not a self-contained unit). `fail` over 250. |
| `aeo.unit_standalone` | no section opens with a back-reference | measured here | `fail` on a section whose first content words are "As we discussed", "As mentioned above", "This approach", a bare "These" or "It". Mechanical, free, and the exact failure marker course/36 names. |
| `aeo.question_headings` | one question per heading, phrased as people ask it | `[practitioner]` | `review`. Cross-references seo-onpage's `heading.question_ratio` when its results exist. |
| `aeo.comparison_table` | a table where the topic supports one | `[practitioner]` | `review` when a `<table>` exists. **`fail` when absent and the primary query contains "vs", "versus", "best" or "compare".** One of the most extractable formats that exists. |
| `aeo.freshness_90d` | priority pages updated within **90 days** | `[practitioner]` | `fail` past 90 days on a named priority page. Perplexity-specific: content over 90 days loses retrieval priority. |
| `aeo.datemodified_accurate` | an accurate `dateModified` | `[practitioner]` | Cross-reference to seo-technical's `schema.article_fields`. |
| `aeo.not_js_dependent` | body content present in raw HTML | `[practitioner]` | **Cross-reference only.** seo-technical's `render_diff.py` owns this. `unknown` with "run render_diff first" when no results are supplied. The highest-consequence check in the tier and it belongs to a sibling - say so loudly rather than quietly re-implementing it. |

### What the evidence does not support

Stated here because the gravitational pull toward these is the main way this skill could go bad.

- **Schema as an AI ranking or citation lever.** Ahrefs found **no uplift across 1,885 pages**;
  SearchAtlas found no correlation; Google's own May 2026 guidance says structured data is **not
  required** to appear in AI Overviews. Vendors report 30-40% gains. Causal tests do not find it.
  Implement schema for rich results and entity clarity, never as a GEO tactic.
- **llms.txt.** See tier 1.
- **"AI-optimized content" as a product.** There is no separate content type. The Princeton
  modifiers describe better writing.
- **Any guarantee of AI citation.** Nobody controls selection, the systems change monthly, and
  fan-out is non-deterministic.

---

## 5. Mentions and platforms (tier 5) - course/34

| Check | Threshold | Tier | Verdict rule |
|---|---|---|---|
| `mention.platform_count` | **4+** third-party platforms | `[practitioner, single vendor]` | `fail` under 4. Brands present on four or more third-party platforms are **2.8x more likely to be cited by ChatGPT**. **The own site is the anchor, not one of the four.** |
| `mention.unlinked_count` | every unlinked mention reclaimed | `[practitioner]` **30-50%** | `review` with the ranked queue. Not a defect - a work list. |
| `mention.platform_completeness` | profiles actually completed | `[practitioner]` | `review` per platform found. |
| `mention.branded_impressions` | tracked monthly, same day each month | `[practitioner]` | **`unknown` - Search Console not connected.** The cheapest honest measure of whether any off-page work is doing anything, and this skill cannot see it. |

**Platform shortlist** (course/34): LinkedIn company page and founder profile, Crunchbase,
G2/Capterra/Clutch, Wikipedia or Wikidata, editorially-vetted industry directories,
YouTube/podcast/conference speaker pages, Reddit/Quora communities.

**The valuable-vs-harmful directory test is editorial standards.** Clutch vets its listings; a
submit-your-URL directory does not. Bulk directory submission is zero value plus NAP-inconsistency
risk.

**Reclamation is the highest-converting tactic in the whole authority tier at 30-50%**, against
5-15% for broken link building. Discovery is a Serper query - `"brand" -site:domain` - then fetch
each result and resolve whether the mention already carries a link. The outreach is three
sentences naming the exact sentence, never a template.

---

## 6. Links (tier 6) - course/32, 33

**This is where the skill is most honest, and it is a position rather than an apology.**

| Check | Threshold | Tier | Verdict rule |
|---|---|---|---|
| `link.reclamation_queue` | reclaim before pursuing anything new | `[practitioner]` **30-50%** | **`review` with the ranked list. The one link check this skill can actually perform.** Ordered by the linking page's apparent editorial character, reported as an observation, never as a score. |
| `link.referring_domains` | baseline the count | `[practitioner]` | **`unknown`. No free source.** |
| `link.gap_vs_competitor` | the domains they have that you do not | `[practitioner]` | **`unknown`.** Needs a backlink index. |
| `link.dr_floor` | DR **30+** baseline, **50+** high-impact; **1,000+** monthly organic visits; Toxic Score under **45** | `[practitioner]` | **`unknown` for every prospect.** Vendor metrics with no free counterpart. |
| `link.anchor_distribution` | exact-match anchors under ~**20%** | `[practitioner]` | `unknown` without the profile. |
| `link.risky_patterns` | no PBN, reciprocal ring or marketplace footprint | `[practitioner]` | `unknown` without the profile. |

**An entire tier returning `unknown` is uncomfortable and correct.** No free backlink index exists;
seo-foundation's kill list already says so. This skill therefore produces a **prospect list, never
a qualified one**, and the report must say that in those words.

**Carry these anyway, because they are the client conversation:**
- **A DR 35 niche-relevant link beats a DR 70 unrelated one.** Relevance is checked first.
- Count **referring domains, not total backlinks**.
- **98% of sites on guest-post marketplaces are low quality** (DR under 40, under 10k traffic).
- The average earned digital PR link costs about **$750**.
- Reciprocal linking at small scale is not a penalty. Do not panic about three mutual links.

**And the reframe that makes this tier's honesty a strength rather than a gap:** branded web
mentions correlate with AI Overview citation at **r = 0.664**; backlinks at **r = 0.218**. Roughly
three times. `[practitioner, correlational]` - **never state it as causal.** Mention work is not a
consolation prize for being unable to measure links.

---

## 7. Local (tier 7, promotes to tier 2 when applicable) - course/35

| Check | Threshold | Tier | Verdict rule |
|---|---|---|---|
| `local.applicable` | a physical location or a defined service area | - | Gate. `pass` when not applicable, **recorded rather than omitted** so nobody implements it later. |
| `local.gbp_primary_category` | the most specific accurate option | `[practitioner]` | **`review`, checked first, every time.** The strongest single signal in local. One dropdown, thirty seconds. "Personal Injury Attorney" beats "Lawyer". |
| `local.reviews_volume` | **50+** in 12 months | `[practitioner, single vendor]` | `fail` under 50. 50+ reviews reported **3x** more likely to appear in AI recommendations. |
| `local.reviews_rating` | **4.5+** | `[practitioner, single vendor]` | `fail` under 4.5. A 4.5+ rating roughly **doubles** citation frequency. |
| `local.reviews_velocity` | **2-4 per week**; 5-15/month sustained six months moves **5-10 map positions** | `[practitioner]` | `unknown` without dated review data, `review` where scrapable. **Velocity beats total.** |
| `local.nap_consistent` | byte-identical across GBP, Bing Places, Apple Maps, Yelp, Facebook | `[practitioner]` | `review` with the variant table. **"St." vs "Street" is a real ranking problem**, as is a suite number present in one listing and absent in another. |
| `local.pages_unique` | genuinely unique location pages | `[practitioner]` | `fail` on high body overlap between location pages. That is doorway behaviour. |
| `local.gbp_completeness` | every field; **1-3 Posts weekly**; **8-12 Q&A** seeded; **10-25 photos** | `[practitioner]` | `unknown` without GBP access, `review` from the public profile. |
| `local.schema` | LocalBusiness, plus Service and FAQPage | `[practitioner]` | Cross-reference to seo-technical. **FAQ rich results sunset in May 2026; the markup still feeds answer engines.** FAQ-schema pages reported **4x** more likely to be cited in AI Overviews. Keep the markup, stop expecting the Google rich result. |
| `local.mobile_under_2s` | under 2s on mobile | `[practitioner]` | Cross-reference to seo-technical's `vitals.py`. |
| `local.three_surfaces` | map pack, local organic and AI recommendation assessed separately | `[practitioner]` | `review`. First two from Serper; the third only from `aivis.py`, else `unknown`. |

**Reported map pack weighting** `[practitioner, modeled estimates, not disclosed weights]`:
GBP signals **32%**, reviews **20%**, on-page **15%**, behavioural **9%**, links **8%**,
citations **6%**. GBP plus reviews is roughly half; citations are 6% - **the reverse of how most
local packages are sold.** **46% of all Google searches carry local intent.**

**Never quote the "100+ photos get 520% more calls" figure.** It traces to vendor research citing
Google, not to a Google publication. course/35 flags it explicitly.

---

## 8. Measurement (tier 8) - course/41

| Check | Threshold | Tier | Verdict rule |
|---|---|---|---|
| `measure.citation_baseline` | **3+ runs** per prompt per engine | arXiv 2604.07585 + course/39, 41 | `pass` only when `aivis.py` ran at `runs >= 3`. **`fail` if a single-run check was recorded as a measurement.** `unknown` if never run. |
| `measure.gsc_connected` | Search Console is the visibility layer | `[confirmed]` | **`unknown` - not connected.** Verified: `gws` exposes no Search Console service and no credential exists. |
| `measure.genai_report` | a Generative AI Performance baseline | `[confirmed, Google Search Central]` | `unknown`. First-party Google data on the exact surface this skill estimates, free to the client. |
| `measure.ga4_retention_14mo` | 14 months, not the 2-month default | `[practitioner]` | `unknown` without GA4. **The one irreversible setup step - it is not retroactive.** Do it first. |
| `measure.gsc_ga4_linked` | Admin > Product Links | `[practitioner]` | `unknown`. GA4 misclassifies **30-50%** of search traffic as Direct or Unassigned without it. |
| `measure.ai_channel_group` | the custom channel regex | `[practitioner]` | `unknown`. GA4's native AI Assistant channel **excludes AI Overviews**. Server logs beat GA4 by **8-31%** on AI referrals because of `rel="noreferrer"`. |

**The GA4 AI channel regex, verbatim:**

```
.*(chatgpt.com|openai.com|perplexity.ai|claude.ai|gemini.google.com|copilot.microsoft.com|you.com|grok.x.ai).*
```

**The defensible traffic line.** AI chatbots are **under 1% of total referrals today, rising
fast.** Graphite's 20% figure is contested. Gartner projects 25% of search volume moving to
chatbots by late 2026. Use the under-1% line with a client; it survives scrutiny.

**Numbers worth carrying into the report:** AI Overviews appear on **~47%** of results (Q1 2026);
**~60%** of searches end without a click; CTR drops **up to 58%** when an Overview is present -
**read that as a ceiling, never an average**, since informational queries lose most and
transactional far less. AI-referred traffic converts **4-5x** better than traditional search.

---

## The measurement rules that override everything

These come from a live spike, 2026-08-08, not from a source. Two ChatGPT runs of one prompt
seconds apart: run 1 named **HubSpot** first and returned **0 sources**; run 2 named **Pipedrive**
first and returned **50**; the cited-domain Jaccard overlap between them was **0.00**.

1. **Never report a citation rate from fewer than 3 runs.** `push_sheet.py` blocks it.
2. **Never render a rate without its run count.** "Cited in 2 of 3 runs", never "67%".
3. **Stability is per metric.** In that spike the brand *set* was identical across runs while
   first-mention flipped and citations shared nothing. `brand_named` earns more confidence than
   `cited`; `first_named` earns least. Report them separately.
4. **"The engine cited nobody" is not "the engine did not cite you."** A run returning zero
   sources is a different finding from a run citing five competitors.
5. **Never compare citation rates month over month at n=3.** At 2 of 3 the 95% Wilson interval is
   **[0.208, 0.939]**. That is not a trend line.
