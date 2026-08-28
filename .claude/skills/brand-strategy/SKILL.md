---
name: brand-strategy
description: "Use to BUILD or AUDIT the strategic core of a brand for a client or a founder: brand positioning, brand personality, brand archetype, brand promise, brand story, brand values, and what the brand deliberately rules out. Execution skill that produces the artifact, not the advice skill. Triggers on: build a brand strategy, brand strategy for, define their brand, brand identity for, develop the brand, brand positioning, positioning statement, brand personality, brand archetype, brand promise, brand story, brand narrative, founding story, brand values, brand essence, brand platform, brand pillars, brand DNA, 'who is this brand', 'what does this brand stand for', audit their brand, review this brand deck, critique this brand strategy, 'their brand is generic', 'we blend in with competitors', 'our brand has no direction', personal brand strategy, founder brand, 'build my founder brand', thought leadership positioning. Works from a Google Doc, a PDF or DOCX brand deck, pasted text, a website URL, a client-projects slug, or just a business name, which it resolves via research --mode entity. Consumes 07-strategic-foundation.md and 08-audience-persona.md when they exist rather than re-deriving them. Outputs client-projects/<slug>/13-brand-strategy.md with a fact table, confidence levels, an explicit 'what this rules out' section, and assumptions to validate; audit mode instead produces a Strong/Workable/Weak/Missing scorecard. Refuses invented brand statistics and presents archetypes as a creative device rather than evidence. Scope is the strategic core only. For voice, tone, messaging or taglines use brand-voice; for colour, typography, logo or the guidelines document use brand-visual; for UVP, market sizing, ICP or personas use strategic-foundation; for explaining or diagnosing branding use branding-advisor; for content pillars, cadence and channels use content-strategy."
argument-hint: [client name, URL, doc, or client-projects slug - optionally "audit" or "founder"]
---

# Brand Strategy

Builds or audits the strategic core of a brand: who it is, what it claims, what it promises,
and what it refuses.

**`branding-advisor` knows things. This skill does things.** If the ask is "explain this to me"
rather than "do this for a client", route there.

---

## Where this sits

```
strategic-foundation        the business: market, UVP, ICP
  (07, 08)                  |
                            v
brand-strategy       ->  brand-voice      ->  brand-visual
  13-brand-strategy       14-brand-voice       15-brand-visual-identity
  who the brand is        how it sounds        what it looks like
                                               16-brand-guidelines (assembled)
```

It is the strategic core **and nothing else**. Voice, colour, type and logo inherit from this
document and are produced by the siblings.

---

## Operating principles (read once)

- **Take the positioning, do not re-derive it.** If `07-strategic-foundation.md` exists, its
  market position and UVP are inputs. Contradicting it silently produces two client artifacts
  that disagree.
- **A brand strategy that rules nothing out is a description.** Section 7 is the test of
  everything above it.
- **Archetypes are a creative device, never evidence** `[P]` [s169]. Aaker's personality scale
  is genuinely peer-reviewed `[C]` [s69]. Do not blur them to borrow credibility.
- **Write the story true.** An invented or embellished origin is the highest-risk line in the
  document: client-facing, quotable, and checkable.
- **Distinctiveness before differentiation for small brands.** A brand nobody retrieves does
  not get to compete on its difference `[C]` [s7] [s1].

---

## Boundaries / handoffs (important)

| Hand off to | For |
|---|---|
| `branding-advisor` | Explaining a concept, fact-checking a statistic, diagnosing a symptom, rebrand triage |
| `strategic-foundation` | Market sizing, UVP, ICP, competitor analysis, audience personas |
| `brand-voice` | Voice spec, tone, messaging, vocabulary, naming, taglines |
| `brand-visual` | Colour, typography, logo direction, guidelines assembly |
| `content-strategy` | Content pillars, cadence, funnel and distribution for this client |
| *(archived)* | `taste-skill:brandkit` generated brand imagery and logo boards. Archived 2026-08-27 to `archives/cleanup-2026-08-27/skills/`. No current skill covers this |

State the handoff when you make it. Do not silently stop.

---

## Context to load first

Always: `references/method.md` (build) or `references/review-rubric.md` (audit).

Then `references/report-structure.md` when writing the document, and
`.claude/skills/branding-advisor/references/what-not-to-do.md` before delivering.

**Max 3 reference files per invocation.** Pull `[sN]` detail from `branding-advisor`'s
`research-synthesis.md` only when a specific claim needs its argument.

---

## Mode Detection

| Mode | Trigger keywords | Load |
|---|---|---|
| **build** (default) | "build a brand strategy", "define their brand", a brief with no existing brand doc | `method.md` |
| **audit** | "audit", "review", "critique", "is this any good", an existing deck supplied | `review-rubric.md` |
| **section** | "just the positioning", "only the brand story" | `method.md`, one phase |
| **founder** | "founder brand", "personal brand", "the CEO's brand" | `method.md` + its Subject: founder section |

If ambiguous, pick the more specific. If the ask spans two, do the primary first and offer the
second. **Founder is a subject modifier, not a separate mode**: it combines with build or
audit.

---

## Workflow

Full detail in `method.md`. In short:

1. **Resolve the input** into text (dispatch table in `method.md` Phase 0).
2. **Read `client-projects/<slug>/`** for `07` and `08` before thinking independently.
3. **See the category.** Research competitors, then run the five-site test: cover the logos and
   see whether you can tell the client apart. If not, that is the headline finding.
4. **Ask only what you cannot infer.** `AskUserQuestion`, batched, one round, 2-4 max.
5. **Position, then personality, promise, story, values.**
6. **Rule things out**, then re-read everything above asking "could a competitor say this?"
7. **Kill list, write the file, summarise, offer the next spoke.**

---

## Writing Rules

**Internal:** direct, bullets, lead with the recommendation.

**Client-facing:** operator, not consultancy. Explain evidence tiers in words, not `[C]`/`[P]`
symbols. **Never mention NexusPoint or Aleem** in the document.

Both: no emojis, no em dashes in body text. Every fact resolves to the section 0 table, an
`[sN]`, a live URL, or "client-reported". Anything else is an assumption and gets labelled.

---

## Edge Cases

| Scenario | Action |
|---|---|
| No `07-strategic-foundation.md` exists | Say so. Recommend running it first, or proceed with a labelled working position and list it for validation |
| The strategic foundation contradicts what the brand work suggests | Name the conflict explicitly, say which you changed and why. Never diverge silently |
| Client supplies only a name | Resolve via `research --mode entity`, then crawl. If nothing is found, ask for the URL rather than inventing a company |
| Client wants archetypes as the backbone | Use them, label them a creative device, never call them evidence-based |
| Client insists on a value or trait that costs nothing | Push back once with the trade-off test. If they keep it, keep it and note it. It is their brand |
| The "brand deck" turns out to be a services list or marketing plan | Say so, offer to switch from audit to build |
| Audit scores Strong across the board | Re-read looking for the choice being avoided. Universal Strong usually means the rubric was applied gently |
| The real problem is the offer, pricing or target customer | Route to `strategic-foundation`. Brand cannot fix an unsettled business |
| Asked for the logo, colours or the voice guide | Route to `brand-visual` or `brand-voice`. Do not produce them here |
| Founder brand, asked for evidence | One confirmed source `[C]` [s5]. Say the evidence base is thin and use the founder-story finding `[C]` [s91] |
| Asked to quote a brand statistic | Check the hub's kill list first. Most of the popular ones have no primary source |

---

## Reference Map

```
references/
├── method.md             THE PIPELINE, phases 0-7 + the founder variant. Load first in build
├── review-rubric.md      Audit mode: 7-row scorecard, reading order, then fix by leverage
└── report-structure.md   Deliverable section order for 13-brand-strategy.md, each section
                          with the "fails when" test
```

No `_research/` here on purpose. `[sN]` resolves via
`.claude/skills/branding-advisor/_research/sources.json`, 260 sources, 132 confirmed. This
skill executes the method that corpus established, and duplicating it would only let the two
drift apart. Run `branding-advisor/_research/gather.py verify` after any citation edit; it
checks this skill's `references/` too.
