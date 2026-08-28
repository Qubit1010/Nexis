---
name: seo-foundation
description: "Use to BUILD or REVIEW a client's SEO foundation - the keyword and search layer of their strategy. Execution skill that produces the artifact, not the advice skill. Triggers on: SEO foundation, SEO strategy for a client, keyword research, find keywords, keyword list, seed keywords, long-tail keywords, question keywords, search volume, keyword difficulty, search intent, intent classification, informational/commercial/transactional intent, SERP analysis, read the SERP, analyse page one, 'who ranks for X', SERP competitors, competitor keywords, 'who are we competing with in search', keyword clustering, topic clusters, cluster these keywords, keyword mapping, keyword map, map keywords to pages, cannibalization, 'are my pages competing with each other', content plan from keywords, pillar page plan, topical map, 'what should we write about', 'what pages should we build', 'they have no SEO', 'review their keyword strategy', 'audit their keyword research', SEO onboarding for a new client. Works from a client's strategic-foundation and audience-persona files when they exist, or from just a business name plus a URL. Runs real discovery: Google Autocomplete harvesting, People Also Ask, related searches, live SERP reads, SERP-overlap clustering, and site crawling. Outputs a 6-tab Google Sheet (Keyword Master, Clusters, Keyword Map, SERP Analysis, Competitors, Cannibalization) plus a written foundation report. Reads difficulty off live SERPs instead of quoting vendor difficulty scores, and says 'not measured' rather than inventing a search volume. Tier 1 only. For SEO THEORY, diagnosis, benchmarks or the course use seo-advisor; for the client's BUSINESS strategy, ICP or persona use strategic-foundation; to WRITE an article use blog-writer; to crawl and score technical health use seo-technical or website-audit-system."
argument-hint: [client name, URL, or client-projects slug - or "review" plus an existing keyword sheet]
---

# SEO Foundation

Builds or reviews the **search layer** of a client's strategy: what their customers
actually search, which of those searches are winnable, how those searches group into
pages, and which page owns each group.

Two jobs:

1. **Build** a foundation from whatever exists, down to just a business name and a URL.
2. **Review** an existing keyword list or content plan, scored, with the gaps ranked.

The output is a working artifact, not a memo: a 6-tab Google Sheet plus a written report.

## Where this sits

`seo-advisor` knows things. This skill does things. Same advisor-to-executor split as
`strategic-foundation` to this.

```
strategic-foundation  ->  seo-foundation  ->  seo-onpage  ->  blog-writer / content-engine
  who the customer is      what they search      whether the page      the actual pages
  and how they talk        and which page wins   delivers on it
```

`strategic-foundation`'s persona ends with "No keyword research was done here, on purpose."
This skill is the thing that was deferred.

## Operating principles (read once)

- **The SERP is the source of truth, not a tool score.** Keyword difficulty is a vendor
  invention with no counterpart at Google, and two tools report volumes up to **30x** apart
  for the same word `[practitioner]`. Difficulty is read off live page one, which is free
  and more accurate. This is not a workaround for lacking a paid tool; it is the method.
- **Never invent a number.** There is no free search-volume API in 2026. The Volume column
  stays empty and labelled "not measured" unless a human pastes real figures in. An
  invented volume silently poisons every priority score downstream.
- **Say what you could not establish.** Some signals genuinely are not observable from the
  data sources here - AI Overview presence is the big one. Report `unknown` and tell the
  user how to check it. A confident wrong answer is worse than an honest gap.
- **Scripts propose, you decide.** The scripts measure what is mechanical (domain
  diversity, UGC on page one, SERP overlap). Whether a page truly answers a query, and
  whether the client could be *clearly* better, are judgment calls that stay with you.
- **Relevance beats winnability.** A rankable keyword that attracts people who will never
  buy is a cost, not an asset.

## Boundaries / handoffs

| Hand off to | For |
|---|---|
| **seo-advisor** | Theory, benchmarks, diagnosis ("traffic dropped", "is SEO dead"), the 42-section course, and anything on-page, technical, off-page or AI-search. It owns the cited 320-source corpus. Cross-cite it, never restate its numbers as if they were measured here. |
| **strategic-foundation** | The client's business strategy, ICP, market sizing, or the audience persona itself. This skill consumes that output; it does not produce it. |
| **seo-onpage** | Whether the page a cluster maps to is actually any good - titles, metas, headings, content quality, internal links, media, E-E-A-T - and the full on-page audit. It is Tier 2 and picks up exactly where this skill stops. |
| **blog-writer** | Writing an actual article against a cluster from the map. |
| **content-engine** / **post-creator** | Turning the map into a running content system: `content-engine` BUILDs the hooks and format set, `post-creator` runs the schedule. |
| **website-audit-system** | Crawling and scoring the site's technical and performance health. |
| **research** / **web-scraper** | Community language mining and competitor site extraction. This skill calls both directly. |

State the handoff when you make it. Do not silently stop.

## Context to load first

Read `references/method.md` first - it is the pipeline and is near-always what you need.
Then load the mode reference below. **Max 3 reference files per invocation.**

---

## Mode Detection

| Mode | Trigger keywords | Load |
|---|---|---|
| **build** (default) | "SEO foundation for X", "keyword research for X", "they have no SEO", "what should they rank for", a client name or URL | `method.md` |
| **review** | "review their keyword strategy", "audit this keyword list", "is this content plan any good", or an existing keyword sheet is supplied | `review-rubric.md` |
| **intent** | "what's the intent of X", "classify these keywords", "is this commercial or informational" | `intent-taxonomy.md` |
| **serp** | "who ranks for X", "read this SERP", "can we win this keyword", "how hard is X" | `serp-read.md` |
| **cluster** | "cluster these keywords", "group these", "which page should own X", "keyword map", "are we cannibalizing" | `clustering-and-mapping.md` |
| **competitors** | "who are our search competitors", "who owns page one", "competitor keywords" | `competitor-discovery.md` |

If the ask spans two modes, do the primary first and offer the second. A request that
starts as one keyword usually wants the whole foundation - check before running 200 SERPs.

---

## Workflow

The full pipeline is in `references/method.md`. Phases 0-8, in order. Summary:

| Phase | What happens | Who does it |
|---|---|---|
| 0 | Resolve inputs - find the client's strategic foundation and persona | you |
| 1 | Harvest the persona's question list and vocabulary | you |
| 2 | SERP-competitor discovery + reconcile against business competitors | `collect.py competitors` |
| 3 | Collect 200+ candidates across six layers | `collect.py expand` + you |
| 4 | Intent classification + the SERP read | `serp_features.py` + you |
| 5 | Score Relevance and Intent value, 1-5 | you |
| 6 | Cluster by SERP overlap | `cluster.py` + you |
| 7 | Map clusters to URLs, find cannibalization | you + site crawl |
| 8 | Ship the Sheet and the report | `push_sheet.py` |

**Before phase 3, tell the user the cost.** Each keyword costs one Serper credit at phase
4. A 200-keyword project is roughly 210 credits. Say the number and get a nod before
spending it.

**Checkpoint after phase 5.** Show the top 30 by priority before clustering 200 rows. If
the ranking is wrong, everything downstream is wrong, and this is the cheapest place to
catch it.

## Deliverables

**A 6-tab Google Sheet** via `push_sheet.py` - schemas in `references/sheet-schemas.md`.

**A markdown report** at `client-projects/<slug>/09-seo-foundation.md`, numbered to sit
alongside `07-strategic-foundation.md` and `08-audience-persona.md`. Structure:

```
0. What we know, and how we know it   (Fact | Source | Confidence, then an honest gap list)
1. The search landscape
2. Who actually owns page one          (incl. the search-vs-business competitor delta)
3. Intent breakdown
4. Priority clusters
5. The keyword map
6. Cannibalization found
7. Measurement baseline
8. First 90 days
What we could not establish
```

Google Doc and PDF are not built by default. Offer them if asked - the Doc via
`tools/gdocs/save_content.py`, the PDF via `seo-advisor/scripts/seo_pdf.py`.

---

## Scripts

All run unsandboxed (they need real network). Keys come from the repo `.env` automatically.

```bash
python scripts/serp.py "query" [--urls] [--refresh]          # one raw SERP, cached
python scripts/autocomplete.py "seed" [--json]               # free, no key, no credits
python scripts/collect.py expand --seeds "a,b" [--skip-serp] # candidates
python scripts/collect.py competitors --seeds "a,b,c" --business-competitors "x.com"
python scripts/serp_features.py --file queries.txt --out serp.json --client-domain acme.com
python scripts/cluster.py --file queries.txt --out clusters.json
python scripts/push_sheet.py --payload payload.json --validate-only   # no title needed
python scripts/push_sheet.py --payload payload.json --title "SEO Foundation - Acme"
```

**Always pass `--client-domain`.** It marks the queries the client already ranks for,
which changes the question from "can we win this" to "are we defending it". On the
verification run it reframed 7 of 10 queries, and without it those would have been planned
as new content the client already has.

Every script has `--selftest`. Run it when something looks wrong - `autocomplete.py
--selftest` in particular distinguishes "the undocumented endpoint changed" from "this seed
has no suggestions", which look identical otherwise.

**The cache is what makes iteration free.** SERPs are cached in `.cache/serp/` keyed on
query only, so re-scoring, re-clustering and re-running after a fix cost zero credits, and
two clients in the same niche share fetches. Pass `--refresh` only when you actually want
fresh results. Every script prints its credit spend to stderr.

**Serper key status:** as of 2026-08-06, `SERPER_API_KEY` (the first key) is exhausted and
rotation falls through to `SERPER_API_KEY_2`. Budget accordingly, and check the printed
cost line rather than assuming a large free allowance.

---

## Edge Cases

| Scenario | Action |
|---|---|
| No strategic foundation or persona exists | Offer to run `strategic-foundation` first - the persona is what makes these keywords theirs rather than generic. If declined, proceed from the site and mark the report `Confidence: Partial`. |
| Client has no website yet | Everything still works except phase 7 mapping. Produce clusters with planned URLs, all status "needs creating". Say the map is a build plan, not an audit. |
| Client insists on search volume | Explain the 30x variance, then offer the honest options: paste Ubersuggest free-tier figures into the Volume column, or wire Google Ads Keyword Planner (needs an Ads account with spend for exact numbers, not ranges). Never estimate. |
| A keyword returns no SERP | It is dropped from clustering and reported in `queries_dropped_no_serp`. Zero results is a real signal - usually a typo or a query nobody makes. |
| Fewer than 200 candidates | Say so rather than proceeding quietly. Add seeds, or bring in the judgment layers (community mining, competitor vocabulary, AI fan-out) that the script cannot do alone. |
| Every cluster is a singleton | The threshold is too strict for this niche, or the candidates are too varied. Try `--threshold 2` and re-read the borderline pairs. Do not just accept 200 clusters. |
| A URL appears twice in the map | That *is* the cannibalization finding. `push_sheet.py` blocks the write. Resolve it - Consolidate (merge + 301) beats Differentiate beats Prune - and record it on the Cannibalization tab. |
| Asked for AI Overview presence | Not returned by Serper at all (verified across query types). Report `unknown` and tell them to check in incognito. Do not infer it from the answer box. |
| Asked to include on-page, technical, or link work | Out of scope by design. Produce the foundation, then hand off - **`seo-onpage` for the on-page and content execution (Tier 2)**, `seo-advisor` for the strategy, `website-audit-system` for the crawl. |
| Client's business competitors are absent from page one | A finding, not an error. It usually means they compete on relationships or paid, not search, and the search opening may be larger than they think. |

---

## Reference Map

```
references/
├── method.md                  # THE PIPELINE: phases 0-8 end to end. Load this first.
├── intent-taxonomy.md         # the six intents, trigger words, SERP signals, page types
├── serp-read.md               # manual difficulty read + click availability + what is unknowable
├── scoring.md                 # the 1-5 rubrics, the priority formula, the sort order
├── clustering-and-mapping.md  # SERP-overlap clustering, the 8-column map, cannibalization
├── competitor-discovery.md    # SERP competitors vs business competitors
├── sheet-schemas.md           # exact tab and column definitions + the payload shape
├── review-rubric.md           # REVIEW MODE: the 7-row scorecard
└── what-not-to-do.md          # the kill list - read before delivering
```

Numbers cited as `[sN]` resolve via `seo-advisor/_research/sources.json`. This skill
deliberately has no corpus of its own: it executes the method that corpus already
established, and duplicating 320 sources would only let the two drift apart.

## Writing Rules

- **Internal (to Aleem):** direct, analytical, no fluff. Bullets over paragraphs.
- **Client-facing:** authoritative and plain. Write like an operator, not a tool vendor.
- **No emojis. No em dashes in body text** (headings may use them). Commas or periods.
- **Never mention NexusPoint or Aleem** inside the client's foundation. It is their
  document, in their language.
- **Every number resolves** to a measurement made here, an `[sN]` citation, or a named
  assumption. If it does none of those, cut it.
