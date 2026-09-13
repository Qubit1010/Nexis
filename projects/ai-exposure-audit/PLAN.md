# AI Exposure Audit — PLAN

MVP idea #3 from `references/mvp-shortlist-business-2026-08-30.md` (composite 4.15).
A fixed-price ($5,000 documented market rate) diagnostic that tells a service business
which revenue lines AI is about to take, what share of the book that is, and what to
move to. Audit #1 runs on NexusPoint itself.

## Approach

A consultant-operated instrument, not a self-serve SaaS. Aleem drives it during a
discovery call while the client watches their exposure number climb. The LLM proposes
scores; Aleem adjusts any of them live and the number moves.

**Local SQLite persistence.** Audits are stored in `data/audits.db`, a local file, so they
survive a cache clear and can be compared across agencies once there are several. Chosen
over Supabase Postgres because a live discovery call is exactly when a network round-trip
must not fail, and client revenue splits belong on Aleem's machine rather than a hosted
database. All data access sits behind `src/lib/db.ts` so a Postgres swap is contained if
this is ever deployed.

**This puts real revenue data back on disk inside a public repo.** `data/` is gitignored
and `git status` is checked before any commit. That guardrail is now load-bearing rather
than structural.

## Stack

Verified live against npm and the provider APIs on 2026-09-05.

| Layer | Choice | Why |
|---|---|---|
| Framework | Next.js 16.3.4, App Router | Smallest single artifact that renders a UI and holds an LLM key server-side |
| Language | TypeScript 5 | The weighting arithmetic is the product; a sign error there corrupts the headline number silently |
| Styling | Tailwind 4, no component library | Three views. A library's defaults are the generic look this must avoid on screen during a $5,000 conversation |
| Persistence | SQLite via `better-sqlite3` 13.0.3, file at `data/audits.db` | Local, no network dependency mid-call, already proven in this repo. Preferred over built-in `node:sqlite`, which still warns "experimental, might change at any time" |
| Tests | Vitest | Scoring math only |
| LLM | `@anthropic-ai/sdk` 0.124.0, `openai` 7.10.0 | Three-leg fallback |

No auth, no ORM, no PDF library. Raw parameterized SQL behind one module.

Schema:

```
audits(id, business_name, headcount, avg_project_value, positioning,
       weights_json, rubric_version, pricebook_version, created_at, updated_at)
service_lines(id, audit_id, name, revenue_share_pct, deliverable_description,
              pricing_model, typical_price, replacement_json, sort_order)
scores(id, line_id, dimension, value, reasoning, provenance)
```

Scores are a real table rather than a JSON column so cross-audit questions stay
answerable later ("what does web design score on judgment thinness across every agency
we have audited").

**Model IDs, each verified live against the provider's own model list:**

1. `claude-sonnet-5` (Anthropic direct) — primary. Scoring six lines is a Sonnet-tier
   reasoning task; Opus is overkill.
2. `gpt-5.2` (OpenAI direct) — second. Needs `max_completion_tokens` and
   `reasoning_effort`, not `max_tokens`.
3. `anthropic/claude-sonnet-5` (OpenRouter) — third, since the repo's direct Anthropic
   and OpenAI keys are both known to run dry.

If all three fail the route throws. It never returns a degraded or partial score.

## The rubric

Lives in `data/rubric.v1.json`, not in a prompt. Versioned filename; every audit records
which version scored it. Five dimensions, each 1-5, **all oriented so 5 = maximum
exposure** so no inversion flag exists anywhere in the math.

| # | Dimension | 5 means | Evidence tier |
|---|---|---|---|
| 1 | Output determinism | Deliverable is fully templatable | documented, directional |
| 2 | Client self-service | Buyer can do it themselves today with a mainstream tool | documented, directional |
| 3 | Judgment thinness | Almost no taste, strategy or orchestration in the value | documented, directional |
| 4 | Artifact billing | Paid for a deliverable, not a business result you are on the hook for | practitioner |
| 5 | Price anchor erosion | Rate visibly falling, clients asking for the AI discount | documented |

Dimensions 3 and 4 are renamed from the approved plan's "judgment density" and
"accountability surface", which were marked inverted while the scale said 5 = exposed.
That ambiguity would have produced a sign bug, a confused scoring prompt, or both.

Each dimension carries per-score anchor text, an evidence tier, and source citations.
`data/pricebook.v1.json` carries the five price anchors with the single-source caveat
attached to each, not buried in a footnote.

## The math

```
n_d       = (score_d - 1) / 4                → [0,1]
exposure  = Σ (weight_d × n_d)               → [0,1]
exposed % = Σ_lines (revenue_share_pct × exposure_line)
```

Per-line contributions are shown, so the headline number is reproducible by hand.

**Weights are unsourced.** No study says output determinism is 30% of substitution risk.
They are sliders, defaulting to equal (0.2 each), with the UI saying plainly that they
are judgment, not a measured finding.

## Evidence tiers

Every number in the output is one of `documented`, `practitioner`, or `judgment`, with
its source, rendered as a visible badge. No unlabelled numbers anywhere. A score the
consultant changed is marked `llm-adjusted`; a score entered by hand is `manual`.

## Repriced menu

Each exposed line maps to a replacement archetype with a price anchor:

| Archetype | Anchor |
|---|---|
| Accountable delivery | 15-20% risk premium |
| Outcome ownership | $5,000 per workflow saving 10+ hrs/wk |
| Strategy / positioning | No documented anchor, flagged as such |
| Productized AI line | Agent setup $20K, license $2K/mo, audit gateway $5K |

Output is a side-by-side current vs repriced menu, exported as Markdown (which feeds the
repo's existing pandoc→PDF and md→Google Doc pipelines) plus a print stylesheet.

## Design direction

Instrument, not dashboard. Dark, dense, typographic, closer to a financial terminal than
a marketing site: the exposure number is the largest thing on screen, per-line
contributions read as a ledger, evidence badges are quiet monospace tags. It has to look
like a measuring device that happens to be showing you bad news, because that is what
justifies the price.

## Deliberately not building

- Auth and multi-tenancy. One operator.
- A hosted database. Local SQLite file, no network dependency during a client call.
- An ORM. Three tables and raw parameterized SQL behind one module.
- A PDF library. Print stylesheet plus the existing pandoc pipeline.
- A component library. Three views, and defaults look generic.
- The quick/deep two-mode split from `website-audit-system`. That skill needs a free tier
  because quick mode is a cold-outreach giveaway. Here the paid artifact is the product;
  a free lead-magnet tier is a separate decision after three paid runs.
- Client self-serve intake.

## Build order

1. `rubric/rubric.v1.json` + `rubric/pricebook.v1.json`, scoring math, Vitest. The rubric
   is the product; prove the arithmetic before any pixel.
2. SQLite schema, `src/lib/db.ts`, audit CRUD routes.
3. Intake UI wired to persistence, plus JSON export for handoff.
4. `/api/score` with the three-leg fallback and loud failure.
5. Scoring review: editable scores, reasoning, provenance, live weight sliders, headline
   number with visible per-line contributions.
6. Repriced menu, Markdown export, print stylesheet.
7. Run audit #1 on NexusPoint using the `context/work.md` service table.
8. Review pass, fix, verify.

Note: `rubric/` is tracked in git because the rubric is the product. `data/` holds the
SQLite file and is gitignored because it holds real client revenue figures.

## Risks

| Risk | Reality |
|---|---|
| The rubric is unvalidated | The biggest risk by far. It is the product and nothing has tested it. Audit #1 is the real test; if the output reads generic or wrong, the rubric gets fixed before anyone is charged. |
| LLM scores sycophantically | Describe a line favourably and it will under-score exposure. Mitigated by forcing per-dimension evidence and by the human review step. |
| Single-source price book | All four anchors trace to one agency blog. Stated on the face of the output. |
| Keys run dry | Three-leg fallback, loud failure, manual scoring always available. |

## Verification before this is called done

1. App installs, starts, and the full intake → score → menu flow is walked in a browser.
2. Audit #1 on NexusPoint; exposed-revenue figure reproducible by hand from the per-line
   contributions shown.
3. Every number in the report carries a tier flag and source, or is labelled judgment.
4. Deliberately broken LLM key fails loudly, never emits a plausible-looking score.
5. Changing a weight slider moves the headline number.
6. `git status` clean of real revenue data before any commit.
7. Vitest passes, `next build` succeeds.
