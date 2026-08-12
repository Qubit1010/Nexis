# The pipeline

Load this first. `checks.md` owns the thresholds; this file owns the order they run in and why.

## The tier order is derived, and says so

Tier 3 inherits course/21's stated pyramid. **Tier 4 has no explicit one**, so this skill derives
one from course/36's five-stage retrieval pipeline - interpretation, query fan-out, retrieval,
selection, synthesis - and labels it derived rather than presenting it as the course's own.

What makes it a real order rather than a preference is the same property seo-technical relies on:
**a failure at a lower layer invalidates the work above it.**

| Tier | Layer | Sections |
|---|---|---|
| 1 | Retrievability - AI crawler policy, Bing | 39, 40 |
| 2 | Entity clarity | 40 |
| 3 | Topical coverage | 36 |
| 4 | Extractability | 37, 38 |
| 5 | Mentions and platforms | 34 |
| 6 | Links | 32, 33 |
| 7 | Local *(promotes to tier 2 when applicable)* | 35 |
| 8 | Measurement | 41 |

Entity sits at tier 2 despite being slow to move precisely *because* it is slow: weeks to months,
so it starts first. Links sit at tier 6 not because they are unimportant but because they are the
most expensive per unit of movement (~$750 per earned link) and the least measurable here.

---

## Phase 0 - resolve inputs

Look for, in `client-projects/<slug>/`:

| File | What it gives you |
|---|---|
| `07-strategic-foundation.md` | what they sell, to whom, the positioning |
| `08-audience-persona.md` | **the buyer's actual vocabulary - this is the prompt set's raw material** |
| `09-seo-foundation.md` | the keyword map, cluster names, target URLs |
| `10-seo-onpage.md` | which pages are already good, the term gaps |
| `11-seo-technical.md` | rendering, indexation, schema - the tier-1 preconditions |

Also collect: the **brand string exactly as it would be written in prose**, plus aliases; the
founder's name; the domain; `gl`/`hl`; and whether local applies. Then check for
`seo-technical`'s result JSON, because `--schema-results` and `--render-results` turn three
`unknown` rows into real ones.

If none of that exists, the skill still runs from a URL plus a brand. Say the confidence is
Partial and why.

## Phase 1 - orientation and the prompt set

**Not skippable, and the highest-leverage twenty minutes in the pipeline.**

Write **10 buyer questions as full sentences of roughly 70-80 words.** This is not padding. AI
queries average 70-80 words against 3-4 for a traditional search - a 17 to 26x complexity
increase. A three-word prompt measures a surface real buyers never touch, and every downstream
number inherits that error.

Cover four shapes (course/39, and the funnel structure practitioners converge on):

| Shape | Example skeleton |
|---|---|
| Category | "I am trying to choose a *<category>* for *<situation>*, and I want to know which options are worth considering and why" |
| Comparison | "How does *<competitor>* compare to the alternatives for someone who *<constraint>*" |
| Use case | "I need to *<job to be done>* under *<constraint>*. What is the best way to do it and what should I watch out for" |
| Branded | "Is *<brand>* any good, what do they actually do, and what should I know before committing" |

**Freeze the set.** A prompt set that changes between measurements makes every comparison
meaningless. Store it next to the results.

Also settle here: 3-5 named competitors, and which engines the buyers plausibly use. For a local
consumer business that is AI Overviews and Gemini. For B2B services it is ChatGPT first, then
Perplexity.

## Phase 2 - retrievability and entity (tiers 1-2)

```bash
python scripts/authority.py <origin> --brand "<Brand>" --areas crawlers,entity \
  --schema-results <seo-technical schema.json> --out results/authority-1.json
```

Free. This is the half that decides whether anything else matters.

## Phase 3 - extractability (tier 4)

```bash
python scripts/authority.py <origin> --brand "<Brand>" --areas aeo \
  --pages <url1,url2,url3> --primary-query "<the query that page targets>" \
  --render-results <seo-technical render_diff.json> --out results/authority-2.json
```

Free - it reads `seo-onpage`'s page cache. Run it on the 3-8 pages that matter, not the whole
site. Always pass `--primary-query`: without it `aeo.comparison_table` cannot tell a comparative
query from an informational one and degrades to `review`.

## Phase 4 - CHECKPOINT: the retrieval verdict

**One line, presented before anything is spent.** It answers: *can these engines fetch, index and
resolve this business at all?*

It sits here for two reinforcing reasons. It is after everything free and before everything paid,
the cheapest place to catch a wrong diagnosis. And if the answer is "OAI-SearchBot is
disallowed", or "the raw HTML is empty", or "the site is not in Bing", then sampling citation
share is spending money to confirm something already known for free.

**The verdict is the spend gate.** Do not proceed to phase 6 on a failed tier 1 without saying
plainly that the sample will measure the consequence of a known defect.

## Phase 5 - coverage, mentions, links (tiers 3, 5, 6)

```bash
python scripts/authority.py <origin> --brand "<Brand>" --areas coverage,mentions \
  --queries "<q1,q2,q3>" --out results/authority-3.json
```

Serper-backed and mostly cache hits, since `seo-foundation` has usually already fetched these
SERPs. State the credit count before running if the queries are new.

Coverage joins PAA questions against the site's heading corpus. The unanswered list **is the
content queue** - hand it to `blog-writer` or `content-engine`.

## Phase 6 - AI visibility sampling (the only paid step)

```bash
python scripts/aivis.py --prompts prompts.txt --brand "<Brand>" --domain <domain> \
  --competitors "<a,b,c>" --engines aio --runs 3 --estimate      # always first
```

**Always `--estimate` first, and state the total and the remaining headroom in one sentence.**

| Tier | Engines | Cost shape |
|---|---|---|
| Default | `aio` (+ `ai_mode`) | ~$0.003/event. 10 prompts x 3 runs ≈ **$0.09**. A legitimate deliverable alone, and the one thing Serper structurally cannot see. |
| Opt-in | `chatgpt`, `perplexity`, `gemini`, `copilot` | **$0.20/event on FREE, $0.005 on BRONZE.** 40x. Quote it. |

`--runs` below 3 is refused. The script will not start a run it cannot finish, because a run that
dies at prompt 7 of 10 leaves three prompts at one sample - the exact non-measurement the whole
protocol exists to prevent.

## Phase 7 - local (only if applicable)

```bash
python scripts/authority.py <origin> --brand "<Brand>" --areas local --local \
  --city "<City>" --nap "<listing 1>|<listing 2>|<listing 3>" --out results/authority-4.json
```

If local does not apply, run it anyway with `--areas local` and no `--local`: the `pass` row is
recorded so nobody implements local work later without asking whether it applies.

## Phase 8 - ship

```bash
python scripts/push_sheet.py --from-results results/*.json --validate-only --out payload.json
# hand-fill the Findings tab in payload.json, then:
python scripts/push_sheet.py --payload payload.json --title "Authority and AI Visibility - <Client>"
```

`--from-results` deliberately leaves **Findings** empty. Auto-promoting every `fail` produces
exactly the forty-item export invariant 7 blocks. Rank by hand, at most five "this week".

Then write `client-projects/<slug>/12-seo-authority-ai.md` per `report-structure.md`.

---

## Cost model, in one place

| Step | Cost |
|---|---|
| Page fetches | free, cached in `seo-onpage/.cache/pages/` |
| robots.txt, llms.txt, Wikidata, sameAs resolution | free, no key |
| Knowledge Graph API | free at 100k/day **once enabled** - currently 403 `SERVICE_DISABLED` |
| SERPs (coverage, mentions, local) | Serper, ~1 credit per new query, 0 on a cache hit |
| Site crawl for the heading corpus | free |
| **AI Overviews / AI Mode** | **~$0.003/event** |
| **ChatGPT / Perplexity / Gemini / Copilot** | **$0.20/event FREE tier, $0.005 BRONZE** |

## Politeness and safety

- The crawl for the heading corpus is capped at 40 pages and obeys robots.txt.
- Mention resolution fetches at most 25 third-party pages, through `fetch_page.py`'s cache.
- Never fetch a page while impersonating an AI user-agent. It proves nothing a WAF would not
  also fake, and it is the kind of thing that ends up in a client's log review.
- `aivis.py` never runs without either `--estimate` or an explicit confirmation above $0.50.
