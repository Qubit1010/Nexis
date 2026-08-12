# MEASURE mode: the multi-run protocol

## Why this file exists

Because the obvious way to do this is wrong, and it is wrong in a way that looks right.

The obvious way: ask ChatGPT "what's the best X", see whether the client is named, write it down.
That produces a number, the number feels like data, and it is noise.

**Measured here, 2026-08-08.** Two ChatGPT runs of one prompt, seconds apart, same account:

| | run 1 | run 2 |
|---|---|---|
| named first | **HubSpot** | **Pipedrive** |
| sources returned | **0** | **50** |
| cited-domain Jaccard | \multicolumn{2}{c}{**0.00**} |

Two opposite, equally confident, equally worthless reports.

**arXiv 2604.07585, "Don't Measure Once" (Apr 2026)**, decomposed 12,933 LLM brand answers:

| Variance source | Share |
|---|---|
| within-prompt resampling | **34.8%** |
| brand-in-context interaction | 29.6% |
| query language | 26.5% |
| **brand identity itself** | **1.5%** |

The thing you are trying to measure is 1.5% of what moves. Everything else is instrument noise,
and the only defence is repetition.

---

## The protocol

1. **Freeze a prompt set.** 10-15 prompts, written once, stored with the results. A set that
   drifts between measurements makes every comparison meaningless.
2. **Write them at 70-80 words.** AI queries average 70-80 words against 3-4 for traditional
   search. A three-word prompt measures a surface real buyers never touch.
3. **Minimum 3 runs per prompt per engine.** `aivis.py` refuses fewer. 5 is better where budget
   allows.
4. **Score against the distribution**, never a single answer.
5. **Report n of N, never a percentage.**

### Prompt shapes

| Shape | Purpose | Skeleton |
|---|---|---|
| Category | are they in the consideration set at all | "I am trying to choose a *<category>* for *<situation>* and want to know which options are worth considering and why" |
| Comparison | do they survive a head-to-head | "How does *<competitor>* compare to the alternatives for someone who *<constraint>*" |
| Use case | do they own the job-to-be-done | "I need to *<job>* under *<constraint>*. What is the best way and what should I watch out for" |
| Branded | what does the engine say when asked directly | "Is *<brand>* any good, what do they actually do, and what should I know before committing" |

Branded prompts are the control. If a brand is not named on its own branded prompt, nothing
upstream matters yet and the finding is an entity problem, not a content problem.

---

## The three signals, never collapsed

| Signal | Question | Why separate |
|---|---|---|
| `cited` | is a URL on the client's domain in the citation list | the link, the traffic |
| `brand_named` | does the brand appear in the answer prose | course/38 treats this as real exposure feeding the course/34 mention effect |
| `competitors_cited` | who got the link instead | the actual competitive picture |

Plus a fourth state that is not a signal but a data condition: **`engine_cited_nobody`**. A run
returning zero sources is a different finding from a run citing five competitors, and the first
one says something about the query, not about the brand.

**A live example of why this matters.** A client's renaissance faire on AI Overviews, 3 runs of a
consumer prompt: **named in 3 of 3, cited in 1 of 3**, with `tripadvisor.com` cited instead. The
engine recommends them by name and sends the click to an aggregator. That is a specific,
fixable finding, and a single `cited` boolean would have reported it as a flat failure.

---

## Stability is per metric

The spike showed the three signals diverge sharply within one prompt: the brand *set* was
identical across runs while first-mention flipped and citations shared nothing.

| Metric | Typical stability | How much confidence it earns |
|---|---|---|
| `brand_named` | most stable | report it plainly |
| `cited` | unstable | report as n of N with the interval |
| `first_named` | least stable | treat as an observation, never a KPI |

`aivis.py` emits `stability_cited`, `stability_named` and `stability_first` separately. Do not
average them into one number.

---

## Reading the interval

At **n = 3 with 2 cited**, the 95% Wilson interval is **[0.208, 0.939]**.

That is the whole argument against month-over-month reporting at small n. Two intervals that
wide overlap almost entirely: a move from 1/3 to 2/3 is not improvement, it is the same
measurement twice. If a client wants a trend, the honest answers are more runs, more prompts, or
a longer interval between measurements - not a prettier chart.

---

## Engines and cost

One Apify actor covers every surface: `apify/google-search-scraper` (109M runs, actively
maintained). Verified 2026-08-08.

| Engine | `--engines` | FREE tier | BRONZE |
|---|---|---|---|
| Google AI Overview | `aio` | **$0.003** | $0.002 |
| Google AI Mode | `ai_mode` | $0.20 | $0.005 |
| ChatGPT | `chatgpt` | $0.20 | $0.005 |
| Perplexity | `perplexity` | $0.20 | $0.013 |
| Gemini | `gemini` | $0.20 | $0.005 |
| Copilot | `copilot` | $0.20 | $0.005 |

Plus `search-page-scraped` (~$0.0045) and `actor-start` (~$0.001) **per actor call**, and there
is one call per prompt x run x engine.

**The 40x cliff is the whole cost story.** A 10-prompt, 3-run, 4-engine protocol is ~**$24.50 on
FREE** against ~**$0.60 on BRONZE ($39/mo)**. All four of Aleem's Apify keys are FREE tier with a
$5/mo cap each, so the full protocol does not fit in the budget. `aivis.py` refuses to start
rather than dying halfway.

**Default to `aio`.** 10 prompts x 3 runs is about **$0.09**, and AI Overviews are the one
surface Serper structurally cannot see (verified across 5 query shapes: `aiOverview` is never
returned). That alone is a legitimate deliverable.

### Engine priority when budget is real

1. **AI Overviews** - largest reach, cheapest, appears on ~47% of results.
2. **ChatGPT** - largest assistant audience. Remember it retrieves from **Bing**, and ~90% of its
   citations come from pages ranked 21+ on Google.
3. **Perplexity** - citation-heavy, Reddit-heavy, and penalises content over 90 days old.
4. **Gemini / Copilot** - add last.

---

## What cannot be measured here

| Gap | Manual route |
|---|---|
| Whether a change *caused* a citation change | Nothing closes this. Report association, never causation. |
| Google's own view of AI performance | Search Console > Performance > AI Mode / AI Overviews. `[confirmed]`, first-party, free to the client. |
| AI referral traffic | GA4 with the custom channel regex in `checks.md`. Native AI Assistant channel **excludes AI Overviews**; server logs beat GA4 by 8-31%. |
| Query fan-out | Not returned by the actor. `coverage.paa_answered` is a **free proxy** and must be called one. |
| Personalisation and location effects | Not controllable. Fix `gl`/`hl` and say so. |
