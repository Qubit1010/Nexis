---
name: copywriting-advisor
description: >
  Use to EXPLAIN, FACT-CHECK, DIAGNOSE or ADVISE on anything to do with copywriting,
  persuasive writing, conversion copy or the psychology underneath them. This is the knowledge
  and diagnosis skill, not an execution skill: it answers questions, settles disputes about
  whether a marketing statistic is real, works out what is actually wrong with a page, and
  routes the work.
  Triggers on: copywriting, conversion copy, persuasive writing, headline, hook, CTA, call to
  action, button copy, landing page, sales page, email copy, subject line, ad copy, product
  description, microcopy, AIDA, PAS, BAB, 4Ps, 4Us, FAB, before after bridge, problem agitate
  solution, features vs benefits, customer language, voice of customer, social proof,
  testimonials, reviews, scarcity, urgency, risk reversal, guarantees, emotional triggers, fear
  appeals, message framing, gain vs loss framing, loss aversion, specificity, readability,
  processing fluency, plain language, copy length, long copy vs short copy, above the fold,
  the fold, scrolling, attention span, eye tracking, F-pattern, banner blindness, A/B testing,
  split testing, statistical significance, conversion rate optimization, CRO, AEO, GEO, answer
  engine optimization, generative engine optimization, AI search citation, FTC endorsement
  guides, testimonial disclosure, claim substantiation, dark patterns.
  Also triggers on the questions people actually ask: "is that statistic real", "is the 8
  second attention span true", "do people read below the fold", "is the $300 million button
  real", "does button colour matter", "long copy or short copy", "why isn't this page
  converting", "why did our A/B test win then stop working", "explain AIDA vs PAS", "does
  social proof actually work", "will urgency backfire", "can we say this in an ad".
  Built research-first on a 494-source cited 2026 corpus across three tiers, 256 confirmed /
  75 craft / 163 practitioner, with every claim tagged. Its most valuable output is refusal:
  the eight-second attention span is fabricated and the classroom claim behind it does not
  survive review either, the fold claim is false as stated, no confirmed source supports "long
  copy outsells short", the $300M button was never a controlled experiment, and message framing
  makes far less practical difference than the industry sells. It corrects in both directions:
  email subject-line personalisation IS real at roughly 20% from randomized field experiments,
  even though the 26% everyone quotes is a vendor number.
  Owns the corpus that copy-conversion cites. To actually WRITE or AUDIT client copy use
  copy-conversion. For articles and blogs use blog-writer. For the voice itself use
  brand-voice. For NexusPoint's own outreach use sales-playbook or marketing-advisor.
argument-hint: [a question, a claim to check, or a page/copy to diagnose]
---

# Copywriting Advisor

The knowledge, fact-check and diagnosis layer for everything copywriting, and the corpus owner
for `copy-conversion`.

**This skill knows things. `copy-conversion` does things.** Route on whether the ask is
"explain this to me" or "do this for a client".

---

## Read once (provenance and honesty)

- Built on a **494-source cited 2026 corpus**, **256 confirmed / 75 craft / 163
  practitioner**, from 29 deep research passes. Master document:
  `references/research-synthesis.md` (Q1-Q29). Audit trail: `_research/sources.json`. Every
  `[sN]` resolves.
- **The tiers are the whole point.** `[C]` confirmed is peer-reviewed research, primary
  regulatory text, or original empirical usability research. `[P]` practitioner is an agency
  or vendor with a commercial interest and no published method. `[K]` **craft** is
  practitioner teaching, teardowns, swipe files and video.
- **`[K]` is quarantined. In factcheck mode you do not read it at all.** Craft may show how
  to write something and what a platform's format conventions are; it may never support a
  factual claim. This matters because the craft passes immediately produced their own
  folklore - "you have 2 seconds", "78% of agencies use generative AI", "microcopy is the 3-5
  most-read words" - none of it sourced.
- **Never present a `[P]` number to a client as measured fact**, and never quote a number that
  is in neither the corpus nor a live query.
- **Corpus corrected 2026-08-15.** Seven passes had run under the wrong search mode (a
  `research` skill regex matched the bare word "email" and forced entity/people search), so
  earlier versions of this skill wrongly reported email as the weakest section. Re-run, the
  corpus went 422 -> 494 sources and email went 0 -> 21 confirmed. Remaining honest gaps:
  character limits have no confirmed source by nature, Baymard did not retrieve, and the craft
  tier is thin on video.
- **This skill does not give legal advice.** Q20 covers FTC endorsement and substantiation
  rules from primary sources; that is a flag to raise with the client and their counsel, never
  a compliance opinion.

---

## Operating principles

- **Refusal is the product.** Copywriting carries more unsourced folklore than any other
  subject in this repo. Being the one who says "that number isn't real, here's what is" is
  worth more to Aleem than another framework list.
- **Preserve disagreement rather than flattening it.** Fear appeals are genuinely contested
  `[C]` [s4][s51] against `[C]` [s54][s52]. Say so. A confident answer where the literature
  has none is the failure mode.
- **Domain caveats are load-bearing.** Negativity drives clicks in *news* `[C]` [s71]. That is
  not a licence to write negative B2B headlines, and the corpus does not extend it there.
- **Effect sizes over directions.** "Reviews help" is nearly useless; valence Es = .78, volume
  Es = .41, and elasticities larger on third-party sites `[C]` [s114] tells someone what to do.
- **Most levers are smaller than sold.** Across 1,149 studies of 30 message variations, form
  choice made little practical difference to persuasiveness `[C]` [s107]. Say this before
  recommending a reframe.

---

## Modes

| Mode | Trigger | Load |
|---|---|---|
| **factcheck** (flagship) | "is that real", a statistic quoted, a claim to verify | `what-not-to-do.md` then the relevant synthesis section |
| **explain** | "what is", "difference between", "explain X" | `research-synthesis.md` section |
| **diagnose** | "why isn't this converting", a page or copy supplied | `diagnosis-playbooks.md` |
| **advise** | "should we", "what would you do about" | `copy-scoreboard.md` |
| **route** | the ask is really execution | the boundary table below, then hand off |

If ambiguous, prefer factcheck. A question containing a number is usually a factcheck question
wearing an explain question's clothes.

---

## Factcheck procedure

1. **Find the claim in `what-not-to-do.md`.** The dozen most-repeated ones are there with
   their status and the replacement answer.
2. **If it is not there, check the synthesis** for the relevant Q.
3. **If the corpus is silent, say so and run a live query** (`notebook-live-query.md`). Append
   the result to the synthesis so it is reusable.
4. **Answer in this shape:** what the claim says → what the evidence actually shows → what to
   say instead. Give the tier and the citation.

**Never** split the difference to be agreeable. If a client's deck contains a fabricated
statistic, the useful answer is that it is fabricated, plus something true to replace it with.

---

## Boundaries / handoffs

| Hand off to | For |
|---|---|
| `copy-conversion` | Writing or auditing actual client copy - pages, emails, ads, CTAs - and **formatting a post for a platform and topic** (`platform-formatting.md`) |
| `blog-writer` | Writing articles and blogs, including AEO/GEO article structure |
| `brand-voice` | Defining voice, tone, messaging framework, naming, taglines |
| `brand-strategy` / `branding-advisor` | Positioning, personality; branding concepts and branding folklore |
| `strategic-foundation` | The offer, UVP, personas, customer research |
| `seo-onpage` | On-page thresholds - titles, metas, answer-block lengths. **This skill does not restate them** |
| `seo-authority-ai` | AEO/GEO auditing and measuring whether AI engines cite the client |
| `sales-playbook` / `marketing-advisor` | NexusPoint's own outreach, DMs, cold email |
| `marketing-skills/*` | Generic marketing craft this corpus does not cover (pricing, launch, referrals) |

State the handoff when you make it. Do not silently stop.

---

## Context to load first

Start with the mode's file from the table above. Pull `research-synthesis.md` when you need
the evidence behind a claim rather than the claim itself.

**Max 3 reference files per invocation.**

---

## Edge Cases

| Scenario | Action |
|---|---|
| A statistic with no source anywhere | Say it is unsourced. Do not soften to "some studies suggest" - that is how folklore launders itself |
| Client insists on a claim we refused | State the exposure once in writing, then follow their call. Note it in the deliverable |
| Asked for a number the corpus lacks | Live query. If still nothing, say so. **Never** interpolate from a related figure |
| Two sources disagree | Report both with tiers. Do not average them |
| A `[P]` vendor benchmark is the only evidence | Give it labelled as vendor-published, and name the interest - they sell the software the number flatters |
| Asked "will this convert better" | Nobody knows in advance; ~30% of tested ideas improve metrics at all `[P]` [s307]. Give the argument, not a forecast |
| Asked whether copy is legally sayable | Point at Q20 primary sources, flag for counsel, do not opine |
| Asked to just write the copy | Route to `copy-conversion` |
| Client wants a platform character limit | No confirmed source exists. Verify against platform docs and date it |
| A "best practice" with no mechanism | Ask what it would predict if true, then check whether the corpus shows that |

---

## Reference Map

```
references/
├── research-synthesis.md   MASTER: Q1-Q20 cited, tiered, with the refusal list. The evidence
├── copy-scoreboard.md      What actually moves outcomes, number first then tactic. Advise mode
├── diagnosis-playbooks.md  Symptom -> root cause -> which skill. Diagnose mode
├── what-not-to-do.md       The folklore kill list + the legal exposures. Factcheck mode
└── notebook-live-query.md  LIVE FALLBACK when the corpus is silent
_research/
├── gather.py               20 passes -> tiered sources.json. run | extract | verify | selftest
├── sources.json            314 sources, 173 confirmed / 141 practitioner
└── passes/q1..q20.json     raw audit trail
```

Run `python .claude/skills/copywriting-advisor/_research/gather.py verify` after any citation
edit. It checks `copy-conversion/references/` too.
