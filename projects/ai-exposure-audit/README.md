# AI Exposure Audit

A fixed-price diagnostic for service businesses: which revenue lines AI is about to take,
what share of the book that represents, and what to move them to.

Built from idea #3 in `references/mvp-shortlist-business-2026-08-30.md` (composite 4.15).
The documented market price for this product is **$5,000**.

## Run it

```bash
npm install
cp .env.example .env.local     # add at least one LLM key
npm run dev                    # http://localhost:3000
```

```bash
npm test                       # scoring math + rendered deliverable
npm run build
```

## What it is

A consultant-operated instrument, not a self-serve app. You drive it during a discovery call
while the client watches their exposure number climb. The LLM proposes every score; you
override any of them live and the number moves.

Four views: revenue lines and their scores, the weights, the repriced menu, and the method
with every source behind it.

## The model

Each service line is scored 1-5 on five dimensions. **Every dimension is oriented so 5 means
maximum exposure**, so there is no inversion anywhere in the maths. If a dimension name ever
reads opposite to its scale, the name is wrong, not the scale.

| Dimension | 5 means | Evidence |
|---|---|---|
| Output determinism | Deliverable is fully templatable | documented |
| Client self-service | Buyer can do it themselves today with a mainstream tool | documented |
| Judgment thinness | Almost no taste, strategy or orchestration in the value | documented |
| Artifact billing | Paid for a deliverable, not a business result you are on the hook for | practitioner |
| Price anchor erosion | Rate visibly falling, clients asking for the AI discount | documented |

```
n_d       = (score_d - 1) / 4        -> [0,1]
exposure  = sum(weight_d * n_d)      -> [0,1]
exposed % = sum(revenue_share * exposure)
```

Per-line contributions are shown so the headline is reproducible by hand.

## What it refuses to do

This is the part that makes it sellable, so do not quietly remove any of it.

- **It never emits a number it cannot trace.** Every figure carries an evidence tier
  (`documented` / `practitioner` / `judgment`) and a source, or is labelled judgment.
- **No source anywhere gives a numeric AI-substitution risk for a named service line.** The
  scores are structured judgment against a sourced rubric. The report says so on its face.
- **The weights are unsourced**, so they are sliders rather than a hidden constant, and the
  UI says they are judgment.
- **A partly scored line returns `null`, not a partial number.** A plausible-looking figure
  is worse than a missing one.
- **Revenue shares that do not sum to 100 are flagged, not silently rescaled.**
- **If every LLM provider fails, scoring throws.** It never returns a degraded or defaulted
  score. Manual scoring still works with no key at all.
- **The whole price book traces to one agency blog.** Every anchor says so.

## Layout

```
rubric/          The product. Tracked in git.
  rubric.v1.json      dimensions, 1-5 anchors, evidence tiers, citations
  pricebook.v1.json   price anchors and replacement archetypes
  sources.json        every citation the other two files resolve against
src/lib/
  scoring.ts     the maths, and the only place it lives
  scorer.ts      builds the prompt from the rubric, validates the response strictly
  llm.ts         three-leg provider fallback
  db.ts          all SQL. Swap this file to move to Postgres.
  markdown.ts    the deliverable
data/            SQLite. Gitignored: real client revenue figures.
```

## Providers

Tried in order, each verified live against the provider's own model list on 2026-09-05:

1. `claude-sonnet-5` (Anthropic)
2. `gpt-5.2` (OpenAI) — uses `max_completion_tokens` and `reasoning_effort`, not `max_tokens`
3. `anthropic/claude-sonnet-5` (OpenRouter)

## Data handling

Nexis is a **public repo**. `data/` and `.env.local` are gitignored. The test fixture is a
fictional agency, not real client data. Check `git status` before committing after running a
real audit.

## Exporting

Export markdown, then use the repo's existing pipelines: pandoc for PDF, or
`md -> docx -> gws drive upload` for a Google Doc. Print goes through a print stylesheet, so
there is no PDF dependency here.
