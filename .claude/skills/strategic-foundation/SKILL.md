---
name: strategic-foundation
description: "Use to BUILD, AUDIT or FIX a client's business strategy foundation, or to produce a standalone AUDIENCE PERSONA for content and search. Three modes: build from scratch, score an existing one against a 7-dimension rubric, or persona only. Works from a doc, a URL, or just a business name it researches. Writes 07-strategic-foundation.md and 08-audience-persona.md, which most downstream client skills consume rather than re-deriving. Say 'who are we writing for', 'define their ICP', 'audit their positioning', 'what words do their customers use'. Hands the persona vocabulary off to seo-foundation and content-strategy. For brand positioning and personality use brand-strategy; for NexusPoint's own strategy rather than a client's, sales-playbook."
argument-hint: [client name, URL, doc, or brief - or paste their existing strategy to review]
---

# Strategic Foundation

Builds or audits the strategic foundation of a **client's** business: mission, vision and
values, target customer, market, competitive position, UVP, and business model with a
financial view.

Two jobs:

1. **Build** a foundation from whatever the client gave you, however thin.
2. **Review** an existing one, scored, with the gaps ranked and the broken pieces rewritten.

It also produces an **audience persona** as a standalone companion artifact, built for
content and search rather than for segmentation, and designed to hand off to `seo-advisor`,
`blog-writer` and `content-engine`.

All of it runs on the same cited corpus. Lead with the answer, ground it in the research, and
never invent a number.

## Operating principles (read once)

- **Evidence-backed, not memory-backed.** Business strategy has a loud practitioner layer
  and a quiet empirical one, and a general model will confidently reproduce the loud one.
  `references/foundation-scoreboard.md` is the scoreboard;
  `references/research-synthesis.md` is the cited evidence behind it.
- **Source tier is not optional.** Every load-bearing claim carries **[confirmed]**
  (peer-reviewed or primary data) or **[practitioner]** (a consultancy making a case for a
  methodology it sells). The corpus is 69 confirmed against 181 practitioner. When a claim
  is practitioner-tier, say so.
- **Refuse the numbers you do not have.** No CAC, LTV, LTV:CAC ratio, gross margin
  benchmark, runway figure or sector TAM exists in this corpus. Saying "I do not have a
  sourced figure for that" is the correct answer and is most of this skill's value over a
  generic answer.
- **Client-reported is not verified.** Founders overshoot realized revenue by ~22% on
  average `[C]` [s64] and their survival expectations barely separate survivors from exits
  `[C]` [s67]. Label and discount their figures.
- **Surface contested evidence, do not resolve it.** Differentiation (Q5) and mission-to-
  performance (Q1) are genuinely disputed. A cleaner deliverable is not worth a false
  consensus.
- **Lead with the recommendation.** The pick, the one number behind it, the tradeoff.

## Boundaries / handoffs (important)

**strategic-foundation owns** the client's whole-business strategy layer: who they serve,
what market, against whom, why them, and how the model makes money. It produces the
document. It does not run the marketing, write the pitch, or build the software.

| Hand off to | For |
|---|---|
| *(no owning skill)* | Channel mix, offer and pricing, paid ads, email and lifecycle, and cross-channel measurement. No current skill covers these. Say so plainly rather than improvising. |
| **proposal-generator** | Turning a finished foundation into a priced engagement offer. |
| **ai-use-case-generator** | The AI automation layer that sits on top of the business model. |
| **discovery-call-prep** | Prepping a conversation with the prospect, not building the deliverable. |
| **seo-advisor** | Turning the persona's question list into keyword clusters, intent mapping and an AEO/GEO plan. It owns the search mechanics (fan-out, intent classification, AI citation) on its own 320-source corpus. Cross-cite it, never restate its numbers. |
| **blog-writer** / **content-engine** / **post-creator** | Writing content from the persona. This skill produces the persona, not the articles. |
| **website-audit-system** | Auditing their site rather than their strategy. |
| **developer-advisor** | Anything about what to build or which stack. |
| **research** / **web-scraper** | Live market research and site extraction. This skill calls both directly. |

State the handoff when you make it. Do not silently stop.

## Context to load first

Read `references/foundation-scoreboard.md` first, near-always useful. Then the mode
reference below. Go to `references/research-synthesis.md` when you need the evidence or the
caveat behind a claim. **Max 3 reference files per invocation.**

---

## Mode Detection

| Mode | Trigger keywords | Load |
|------|-----------------|------|
| **build** (default) | "strategic foundation for X", "develop their strategy", "they have no strategy", "define their mission/UVP/customer", a brief, doc or URL with no existing strategy | `build-playbook.md` |
| **review** | "review/audit their strategy", "critique this business plan", "is this any good", "what's missing", or an existing strategy doc is supplied | `review-rubric.md` |
| **persona** | "buyer persona", "audience persona", "customer persona", "who are we writing for", "audience research", "what language do their customers use", "persona for content/SEO" | `persona-playbook.md` |
| **section** | "just the UVP", "only the market sizing", "size this market", "who is their customer", "competitor analysis only" | `build-playbook.md` (the one section) |
| **advise** | "how do I write a mission statement", "what is TAM SAM SOM", "should they differentiate", a how-to question with no client attached | scoreboard + the named synthesis section |

If ambiguous between two modes, pick the more specific one. If the ask spans two, handle the
primary first, then offer the second. **If a supplied document turns out to be mostly goals
rather than strategy, review mode says so and offers to switch to build** (see the handoff
rule at the end of `review-rubric.md`).

---

## Workflow

### Step 1: Parse and classify
Extract: **mode**, **the client** (name, URL, industry, geography), **what was supplied**
(doc, file, URL, paste, or nothing), and **scope** (whole foundation vs one section).

Resolve the input using the table in `build-playbook.md` Step 1. Partial input is enough. If
too vague to act on, ask ONE question. Not several.

### Step 2: Load context and references
Scoreboard first, then the mode reference. Pull evidence and caveats from
`research-synthesis.md` when a claim needs to be defensible.

### Step 3: Gather what you do not know
Live market, competitor and trend research through the `research` skill; business facts
through `web-scraper`. Then, and only then, ask the client the 2 to 4 questions you could
not infer, batched through `AskUserQuestion` in one round.

### Step 4: Ground in research (not memory)
- Lead with the concrete number, then the tier, then what it means for this client.
- Keep the two citation types distinct: `[sN]` for methodology evidence from the locked
  corpus, a plain URL for a live fact about this client's market.
- **Live fallback:** on a gap, follow `references/notebook-live-query.md`, present the cited
  answer, then append it to `research-synthesis.md` under "Live Query Additions".
- If there is genuinely no evidence, say so. Never fill the gap with a plausible number.

### Step 5: Run the kill list, then deliver
Run the whole output through `references/what-not-to-do.md` before showing it. Every number
must resolve to `[sN]`, a live source URL, "client-reported", or a named assumption. Save as
markdown. Offer a Google Doc or PDF only if asked.

---

## Writing Rules

- **Internal (to Aleem):** direct, analytical, no fluff. Bullets over paragraphs.
- **Client-facing:** authoritative yet natural. Write like an operator who has run a
  business, not a consultancy selling a framework.
- **No emojis. No em dashes in body text** (headings may use them). Use commas or periods.
- **Be concrete:** name the number, the segment, the competitor, the assumption.
- **Never mention NexusPoint or Aleem** inside the client's strategy document. It is the
  client's foundation, written in their language, not an agency artifact.
- **The fiction rule, above all others:** no invented client-specific figure, ever. Market
  sizes show their arithmetic. Financials show structure plus sourced benchmarks plus named
  assumptions. A gap stated honestly beats a number that cannot be defended when the client
  asks where it came from.

---

## Edge Cases

| Scenario | Action |
|----------|--------|
| Only a business name, no URL | `research --mode entity` to find them, then crawl. If still nothing, ask for the URL. Never invent a plausible company. |
| Client brief contradicts their website | Report both in Section 0 with sources, flag the contradiction, and ask which is current. Do not silently pick one. |
| Client asks for a market size you cannot source | Build bottom-up from what is knowable and show every assumption. Never quote an unsourced total. |
| Client asks for CAC/LTV/margin benchmarks | Not in the corpus. Give the formula, ask for their actuals, or offer a live research pass. Do not estimate. |
| "What's our realistic revenue next year?" | Structure and scenarios from their own inputs, labelled client-reported and discounted `[C]` [s64]. Not a single confident figure. |
| Existing strategy is really just goals | Score it honestly (row 1 Missing), say there is not enough to audit, offer build mode. |
| Client pushes back on a Weak score | Quote their own wording and the criterion. If they are right, change it; if not, hold it. |
| Business is pre-revenue with no data | Legitimate output is mostly Section 0 gaps and Section 7 assumptions. Say plainly it is a hypothesis set awaiting validation. |
| Asked to make the market look bigger | Decline. Explain that investors judge clarity of customer and route to market, not the number `[P]` [s74]. |
| Tempted to cite "90% of startups fail" | Do not. Use ~78-80% one-year establishment survival `[C]` [s8]. |
| Asked for a persona with no customer data available | Build it, mark nearly every line `[assumption]`, and label it Hypothesis at the top. Never invent verbatim quotes to fill the language section. |
| Asked whether the persona will improve rankings or conversions | No evidence in this corpus supports that. The measured benefit is faster user understanding `[C]` [s255]; the search payoff is inferred from the vocabulary gap `[C]` [s260], not proven. |
| Persona request that slides into keyword research | Produce the persona and its question list, then hand off to `seo-advisor`. Do not build keyword clusters here. |

---

## Reference Map

```
references/
├── research-synthesis.md      # MASTER: Q1-Q8 cited synthesis + "Live Query Additions"
│     Q1 mission/vision/values      Q2 market research + sizing
│     Q3 target customer            Q4 competitive + industry structure
│     Q5 positioning + UVP          Q6 business model + revenue
│     Q7 financial forecast         Q8 strategy diagnosis (review mode)
│     Q9 persona effectiveness      Q10 audience language + search intent
├── foundation-scoreboard.md   # DEFAULT LOAD: the numbers, number first then implication
│                              #   + an explicit list of numbers this corpus does NOT have
├── build-playbook.md          # BUILD MODE: input resolution, the 8-section deliverable
├── review-rubric.md           # REVIEW MODE: the 7-row scorecard + reading order
├── persona-playbook.md        # PERSONA MODE: the audience artifact for content + search
│                              #   language mining, evidence markers, handoff to seo-advisor
├── what-not-to-do.md          # kill list: refused numbers, method failures, framework honesty
└── notebook-live-query.md     # LIVE FALLBACK: self-research via the research skill
_research/                     # audit trail: gather.py, sources.json (250), passes/q1-q15
evals/                         # evals.json + trigger_evals.json
```

**On scripts:** there are deliberately none. Every mechanical step reuses an existing entry
point (`extract_proposal.py` for Docs, `to-markdown/convert.py` for files,
`web-scraper/scrape.py` for sites, `research.py` for market research), and input dispatch is
a table the model reads rather than a script to maintain. Do not add a `resolve_input.py`.

**Useful:** `python _research/gather.py verify` checks that every `[sN]` in `references/`
still resolves after any corpus refresh. Run it before trusting a citation.

Sibling skills: **proposal-generator** (the
offer), **ai-use-case-generator** (the automation layer), **research** / **web-scraper**
(gathering), **discovery-call-prep** (the conversation).

---

## The corpus

**275 sources** from 380 deduped, across **17 deep passes** of the in-repo `research` skill
(Exa + Tavily + Serper + Jina fused, content-extracted), junk-filtered for social and UGC,
capped at 5 per domain so no consultancy blog dominates.

**Six of the fifteen passes are remedial.** The first eight returned 10 confirmed-tier
sources with 9 of them in one pass: the broad, natural phrasing of a strategy question
retrieves explainer and consultancy content, because that is what dominates these keywords
commercially. Re-asking the same six subjects in the register the academic literature uses
(empirical, meta-analysis, named constructs) retrieved a non-overlapping set and lifted the
corpus to 69 confirmed. A fifteenth pass was added when competitive analysis was still left
with a single confirmed source.

**79 confirmed against 196 practitioner.** Every section carries 4 to 11 peer-reviewed
sources. That ratio is the most important fact about this corpus: business strategy advice
is mostly consultant opinion, and the reference files preserve that distinction rather than
flattening it.

Two later passes (Q9, Q10) added the persona capability. They exist because the standard
persona template leads with demographics while Q3 finds demographic bases fail to predict
behaviour, and that conflict needed resolving with evidence rather than by preference. The
answer is that a persona is an alignment artifact with a measured benefit `[C]` [s255], not
a prediction instrument, so it aligns writers and never chooses segments.

To refresh: `python _research/gather.py run`, then `extract`, then **`verify`** before
trusting any citation. `extract` preserves existing indices, so a refresh appends new sources
and never renumbers, which keeps every `[sN]` already written in `references/` pointing at
the same source.
