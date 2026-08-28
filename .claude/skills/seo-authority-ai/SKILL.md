---
name: seo-authority-ai
description: "Use to BUILD or AUDIT a client's authority and AI-search visibility: whether answer engines can retrieve them, resolve who they are, and actually cite them. Execution skill that produces the artifact, not the advice skill. Triggers on: AEO, GEO, answer engine optimization, generative engine optimization, AI search, AI visibility, 'are we cited by ChatGPT', 'why isn't AI mentioning us', 'make this page citable', 'optimize for Perplexity', citation rate, citation share, AI Overviews, AI Mode, zero-click, query fan-out, extractable answers, answer blocks, answer-first, comparison table for AI, expert quotes, inline citations, topical coverage, entity SEO, entity home, Wikidata, Knowledge Panel, knowledge graph, sameAs, AI crawler control, GPTBot, ClaudeBot, CCBot, PerplexityBot, Google-Extended, 'should I block GPTBot', llms.txt, 'do I need llms.txt', backlinks, link building, link gap, referring domains, domain rating, anchor text, digital PR, brand mentions, unlinked mentions, 'who is talking about us', Crunchbase, G2, local SEO, Google Business Profile, map pack, NAP, reviews, measuring AI visibility, AI referral traffic. Works from a URL, a client-projects slug, or a page plus a brand name. Outputs a 6-tab Google Sheet plus a report at client-projects/<slug>/12-seo-authority-ai.md. Tier 4 only (course sections 32-42). For SEO THEORY, benchmarks, pricing or the course use seo-advisor; for KEYWORD research use seo-foundation; for on-page and content use seo-onpage; for crawling, indexation, schema or Core Web Vitals use seo-technical; to WRITE the article use blog-writer."
argument-hint: [URL, client-projects slug, or a page plus a brand - optionally "audit" / "optimize" / "measure"]
---

# SEO Authority and AI Search

Builds or audits the **authority and AI-visibility layer**: whether answer engines are allowed
to fetch the site, whether they can resolve who the business is, whether the content survives
being extracted, who is talking about them, and whether any of it results in a citation.

Two jobs:

1. **Optimize** a page (new or existing) so it can be retrieved, extracted and cited.
2. **Audit** a site's authority and AI visibility, producing a prioritized diagnosis.

The output is a working artifact: a 6-tab Google Sheet plus a written report.

## Where this sits

`seo-advisor` knows things. This skill does things. It is Tier 4 of the course - sections 32 to
42 - and nothing else. It is the last of the four executors.

```
seo-foundation  ->  seo-onpage  ->  seo-technical  ->  seo-authority-ai
what they search    is the page     can Google         can AI engines
and which page      any good        fetch and          retrieve, resolve
wins it                             render it          and cite it
```

## Operating principles (read once)

- **A single sample is not a measurement.** Measured 2026-08-08: two ChatGPT runs of one prompt,
  seconds apart, named different winners (HubSpot, then Pipedrive) and shared **zero** cited
  domains (Jaccard 0.00). arXiv 2604.07585 decomposed 12,933 answers: within-prompt resampling
  is **34.8%** of variance; brand identity is **1.5%**. `aivis.py` refuses under 3 runs and
  `push_sheet.py` blocks a rate that lacks its run count.
- **Stability is per metric, not per row.** In that same spike the brand *set* was identical
  across runs while first-mention flipped and citations shared nothing. Report `brand_named`
  with more confidence than `cited`, and `first_named` with least.
- **Three different findings, never collapsed.** "Not cited", "not sampled" and "not
  retrievable" mean different things. Collapsing them is how this skill would lie.
- **Retrievability before everything.** If the retrieval bots are blocked, or the page renders
  client-side and is empty raw, or the site is absent from Bing, then extraction work is
  theoretical. That is why the checkpoint is also the spend gate.
- **Say what has no free source.** There is no free backlink index. Referring domains, DR/DA,
  link gap, anchor distribution and toxicity all return `unknown`. This skill produces a
  prospect list, never a qualified one, and the report says so in those words.
- **The evidence ceiling is three writing changes.** Expert quotes **+41%**, statistics
  **+30%**, inline citations **+30%** (Princeton, `[peer-reviewed]`, course/37). Everything past
  those is practitioner correlation. Schema and llms.txt are not AI ranking levers and this
  skill refuses to sell them.

## Boundaries / handoffs

| Hand off to | For |
|---|---|
| **seo-advisor** | Theory, benchmarks, the 42-section course, SEO pricing and how to sell it (course/42's commercial half lives there, not here). It owns the cited 320-source corpus. Cross-cite it, never restate its numbers as if measured here. |
| **seo-technical** | Crawling, indexation, sitemaps, canonicals, redirects, JS rendering, Core Web Vitals, and **all schema/JSON-LD**. This skill reads `schema.py` and `render_diff.py` output and cross-references it. If the AI-bot policy needs rewriting, `emit.py` writes it. |
| **seo-onpage** | Titles, metas, headings, internal links, media, content inventory. Overlapping structural checks cross-reference rather than recompute. |
| **seo-foundation** | Keyword research and the keyword map. This skill consumes the map for coverage and prompt design. |
| **blog-writer** | Writing the article. This skill validates and fixes its extractability; it does not write the prose. |
| **website-audit-system** | A prospect-facing sales audit with a hook email. That is the cold-outreach motion; this is a paid client deliverable. |

State the handoff when you make it. Do not silently stop.

## Context to load first

Read `references/method.md` first, then the mode reference below. **Max 3 reference files per
invocation.**

---

## Mode Detection

| Mode | Trigger keywords | Load |
|---|---|---|
| **audit** (default) | "AI visibility audit", "authority audit", "are we cited by AI", a bare URL, a client slug | `method.md` + `report-structure.md` |
| **optimize** | "make this page citable", "AEO", "GEO", "optimize for ChatGPT", "restructure for extraction" | `method.md` + `aeo-geo.md` |
| **measure** | "citation share", "am I in AI Overviews", "track AI visibility", "who is cited instead of us" | `measurement.md` |
| **entity** | "entity SEO", "Wikidata", "Knowledge Panel", "KGMID", "sameAs", "should I block GPTBot", "llms.txt" | `entity-and-crawlers.md` |
| **mentions** | "unlinked mentions", "brand mentions", "digital PR", "link building", "link gap", "reclamation" | `authority.md` |
| **local** | "local SEO", "Google Business Profile", "GBP", "map pack", "NAP", "reviews" | `local.md` |

---

## Workflow

Full pipeline in `references/method.md`. Tier order is **derived** from course/36's retrieval
pipeline and stated as derived - see `references/checks.md`.

| Phase | What happens | Who | Cost |
|---|---|---|---|
| 0 | Resolve inputs: `07`-`11` in `client-projects/<slug>/`, keyword map, saved crawl graph, seo-technical results. Brand, aliases, founder, gl/hl, local yes/no | you | free |
| 1 | Orientation: the **10 buyer questions written as full 70-word sentences** | you | free |
| 2 | Retrievability + entity (tiers 1-2) | `authority.py --areas crawlers,entity` | free |
| 3 | Extractability (tier 4) | `authority.py --areas aeo` | free |
| 4 | **CHECKPOINT - the retrieval verdict** | you | free |
| 5 | Coverage, mentions, links (tiers 3, 5, 6) | `authority.py --areas coverage,mentions` | cached Serper |
| 6 | AI visibility sampling | `aivis.py` | **paid, quoted first** |
| 7 | Local, only if applicable | `authority.py --areas local` | cached Serper |
| 8 | Ship the Sheet and the report | `push_sheet.py` + you | Sheets |

**Phase 1 is not skippable.** The prompt set is the instrument. AI queries average **70-80
words** against 3-4 for a traditional search, so a three-word prompt measures a surface real
buyers never touch. Ten badly written prompts produce a measurement of nothing.

**The checkpoint is the spend gate, not just a review gate.** It answers one question: *can
these engines fetch, index and resolve this business at all?* If the answer is no, sampling
citation share is spending money to confirm a free finding.

**Cost.** Phases 0-5 and 7 are free. Phase 6 is the only paid step, in two tiers:
- **Default: AI Overviews + AI Mode.** ~$0.003/event. 10 prompts x 3 runs is about **$0.09**,
  and it is the one thing Serper structurally cannot see.
- **Opt-in: ChatGPT / Perplexity / Gemini / Copilot.** **$0.20/event on the FREE Apify tier**
  against **$0.005 on BRONZE** - a 40x gap. Always run `--estimate` first and state the total
  and the remaining headroom in the same sentence.

---

## Scripts

Run unsandboxed (real network). Keys come from the repo `.env`. Use bare `python` (3.12), not
`py -3`.

```bash
python scripts/authority.py https://acme.com --brand "Acme Ltd" \
    --areas crawlers,entity,aeo,coverage,mentions --out results/authority.json
python scripts/authority.py URL --brand X --areas local --local --city "Boston" \
    --nap "123 Main St., Boston MA|123 Main Street, Boston MA"
python scripts/aivis.py --prompts prompts.txt --brand "Acme" --domain acme.com \
    --engines aio --runs 3 --estimate          # cost + headroom, spends nothing
python scripts/aivis.py --prompts prompts.txt --brand "Acme" --domain acme.com \
    --engines aio --runs 3 --out results/aivis.json
python scripts/push_sheet.py --from-results results/*.json --validate-only
python scripts/push_sheet.py --payload payload.json --title "Authority and AI Visibility - Acme"
```

Pass `--schema-results` and `--render-results` (from `seo-technical`) whenever they exist:
without them `entity.sameas_*` and `aeo.not_js_dependent` return `unknown` rather than being
silently skipped.

Every script has a real `--selftest`. `authority.py` and `push_sheet.py` are fixture-based and
need no network; `aivis.py`'s asserts the refusal, the cost arithmetic and the matcher without
spending anything.

**The cache is what makes iteration free.** Pages come from `seo-onpage/.cache/pages/`, SERPs
from `seo-foundation/.cache/serp/` (re-reads cost 0 credits), and `aivis.py` caches per
`(engine, prompt, gl, run_index)` - the run index is in the key, so three runs stay three
samples and never collapse into one.

---

## Edge Cases

| Scenario | Action |
|---|---|
| Asked for a citation rate after one check | Refuse and explain. One run measured HubSpot winning with 0 sources; the next measured Pipedrive with 50. Offer `--runs 3` and the cost. |
| Budget will not cover the protocol | `aivis.py` refuses to start rather than dying halfway, because a half-sampled prompt set is worse than none. Offer `--engines aio`, fewer prompts, or the BRONZE upgrade with the 40x figure. |
| Client asks to block all AI crawlers | Present it as the business decision it is. Blocking retrieval bots forfeits citations while training bots are the ones consuming the bandwidth. Never block OAI-SearchBot, ChatGPT-User, Claude-SearchBot or PerplexityBot silently. |
| Asked to add or sell llms.txt | Decline the sale. No engine honors it, Google compares it to the keywords meta tag, adoption is ~10%. If one already exists, leave it - removing it is also billable work with no benefit. |
| Asked whether schema will get them cited | No. Ahrefs found no uplift across 1,885 pages and Google's May 2026 guidance says structured data is not required for AI Overviews. Implement schema for rich results and entity clarity via `seo-technical`, never as a GEO tactic. |
| Asked for a link gap or a DR-qualified prospect list | There is no free backlink index. Return `unknown`, produce the mention-reclamation queue instead, and say why that is not a downgrade: mentions correlate with AI Overview citation at r=0.664 against r=0.218 for backlinks. |
| Client is not local | Record `local.applicable` as a pass rather than omitting the area, so nobody implements local work later without asking whether it applies. |
| No Search Console | The normal state, and it caps what can be concluded. Branded impressions, the Generative AI Performance report and indexation ratios all return `not connected` with export steps. Never estimate them. |
| The page is JS-rendered and empty raw | That is the finding, and it is tier 1. Hand to `seo-technical`'s `render_diff.py`; a site can rank fine in Google and be structurally invisible to ChatGPT. |
| Wikidata returns a different entity first | `review`, not `pass`. Measured live: "Example Faire" returns *Bristol* Renaissance Faire above the correct entity. Disambiguation risk is real. |
| Audit finds only trivial issues | Say so. "Retrievable, resolvable, and simply not yet mentioned anywhere" is a legitimate finding, and inventing three fixes to look thorough is padding. |

---

## Reference Map

```
references/
├── method.md               # THE PIPELINE: phases 0-8, tier order, cost model. Load first.
├── checks.md               # THE CONTRACT: every id, threshold, course section, verdict rule
├── aeo-geo.md              # OPTIMIZE: the Princeton rewriting pass and the extraction contract
├── measurement.md          # MEASURE: the multi-run protocol, prompt design, the price table
├── entity-and-crawlers.md  # ENTITY: Wikidata/KG/sameAs + the 8-bot matrix + the llms.txt refusal
├── authority.md            # MENTIONS: reclamation, the 4-platform threshold, the link position
├── local.md                # LOCAL: GBP, reviews, NAP, the three surfaces
├── sheet-schemas.md        # 6 tabs, exact columns, the 7 blocking invariants
├── report-structure.md     # the deliverable's shape, including the 90-day roadmap
└── what-not-to-do.md       # the kill list. Read before delivering.
```

`course/NN` refers to `seo-advisor/references/course/NN-*.md`. This skill deliberately has no
corpus of its own: it executes the method that corpus established, and duplicating 320 sources
would only let the two drift apart.

**Cite `course/NN` plus the evidence tier, not `[sN]`.** `[sN]` is not portable between skills,
and in seo-advisor's `sources.json` it resolves by the `index` field, not array position
(`sources[N-1]` is wrong for 256 of 320 entries). The single exception, named in full because
it wins arguments: **the Princeton GEO study, `[peer-reviewed]`, course/37.**

## Writing Rules

- **Internal (to Aleem):** direct, analytical, no fluff. Bullets over paragraphs.
- **Client-facing:** authoritative and plain. Translate the jargon - "fan-out" means nothing to
  a client, "the engine silently asks eight follow-up questions and you answer two of them" does.
- **No emojis. No em dashes in body text** (headings may use them). Commas or periods.
- **Never mention NexusPoint or Aleem** inside the client's report. It is their document.
- **Never render a citation rate as a bare percentage.** "Cited in 2 of 3 runs" is the format.
  A percentage from three samples implies a precision that does not exist.
- **Tag the tier on every borrowed claim.** `[peer-reviewed]` is Princeton and nothing else in
  this tier. `[practitioner, correlational]` is r=0.664 and it is never causal. Map-pack weights
  are `[practitioner, modeled estimates]`. The "100+ photos, 520% more calls" figure is not
  quoted at all.
- **Every number resolves** to a measurement made here, a `course/NN` citation, or a named
  assumption. If it does none of those, cut it.
