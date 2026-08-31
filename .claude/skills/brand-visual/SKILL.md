---
name: brand-visual
description: "Use to BUILD or AUDIT what a brand looks like, as a written specification: colour system, typography, logo direction, spacing, imagery, applications, accessibility and design tokens. Also assembles the full brand guidelines manual. Computes real WCAG contrast ratios rather than asserting a palette is accessible. Writes client-projects/<slug>/15-brand-visual-identity.md. For positioning and personality use brand-strategy; for voice and naming, brand-voice; for explaining branding, branding-advisor; for building actual UI, ui-ux-pro-max."
argument-hint: [client name, URL, brand book, or client-projects slug - optionally "audit" or "assemble"]
---

# Brand Visual Identity

Builds or audits the visual system as a written specification, and assembles the brand
guidelines manual.

**`branding-advisor` knows things. This skill does things.** If the ask is "explain this to me"
rather than "do this for a client", route there.

---

## Where this sits

```
brand-strategy       ->  brand-voice      ->  brand-visual
  13-brand-strategy       14-brand-voice       15-brand-visual-identity
  who the brand is        how it sounds        what it looks like
                                               16-brand-guidelines (assembled from 13+14+15)
                                                     |
                                    +----------------+----------------+
                                    v                                 v
                          taste-skill:brandkit              ui-design-system
                            (both ARCHIVED                   2026-08-27)
```

It is the visual system **and nothing else**. It writes the spec; `brandkit` draws.

---

## Operating principles (read once)

- **Specify, do not describe.** Hex values, type scales, computed ratios, licence status. "A
  modern, clean look" is a mood board.
- **Measure the current state, do not read it.** Sample live hex values and loaded fonts. The
  brand book and the website disagree more often than not, and that divergence is a finding.
- **Compute contrast, never assert it.** It is arithmetic on relative luminance. A palette
  called accessible without a number is not audited.
- **Every decision traces to `13`.** A colour chosen because it looks good is a preference.
- **Redesign has a cost.** Replacing a mark discards accumulated recognition, and the most
  loyal customers react worst `[C]` [s29]. Keep, refine or replace is a defended decision.
- **Consistency is a questioned dogma** `[C]` [s46], and whether guidelines produce it is only
  anecdotally evidenced `[P]` [s178]. Write for the people who will use the document.

---

## Boundaries / handoffs (important)

| Hand off to | For |
|---|---|
| `branding-advisor` | Explaining a concept, fact-checking a claim, rebrand triage |
| `brand-strategy` | Positioning, personality, promise, story, values |
| `brand-voice` | Voice, tone, messaging, naming, taglines |
| *(archived)* | `taste-skill:brandkit` generated logo boards, identity decks and brand imagery. Archived 2026-08-27 to `archives/cleanup-2026-08-27/skills/`. No current skill covers this |
| *(archived)* | `ui-design-system` turned an approved palette into dev token files. Archived 2026-08-27 to `archives/cleanup-2026-08-27/skills/`. Write tokens inline in the spec instead |
| `ui-ux-pro-max` | Designing an actual product UI, not the brand system |
| `senior-frontend` / `nexis-builder` | Implementing a site or app |
| `linkedin-infographics` / `carousel` / `shorts-creator` | Individual branded content pieces |

State the handoff when you make it. Do not silently stop.

---

## Context to load first

Always: `references/method.md` (build) or `references/review-rubric.md` (audit).

Then `references/report-structure.md` when writing, and
`.claude/skills/branding-advisor/references/what-not-to-do.md` before delivering.

**Max 3 reference files per invocation.**

---

## Mode Detection

| Mode | Trigger keywords | Load |
|---|---|---|
| **build** (default) | "visual identity for", "colour system", "typography", "logo direction" | `method.md` |
| **audit** | "audit", "review this brand book", "our branding looks dated", existing assets supplied | `review-rubric.md` |
| **assemble** | "brand guidelines", "the manual", "put it all together" | `report-structure.md` assembly section |
| **accessibility** | "contrast", "WCAG", "our colours fail", "accessible palette" | `method.md` Phase 8 |
| **tokens** | "design tokens", "give the devs the values" | `method.md` Phase 9 |

If ambiguous, pick the more specific. **Assemble requires `13`, `14` and `15` to exist**: if
any is missing, say which and offer to build it rather than inventing the section.

---

## Workflow

Full detail in `method.md`. In short:

1. **Resolve the input** into text.
2. **Record the current state as measured fact**: sampled hex values, loaded fonts, logo file
   formats, where the identity already breaks.
3. **Read upstream**: `13` for traits and position, `14` for register.
4. **Set the direction**, naming which trait each decision serves.
5. **Logo**: keep, refine or replace, defended. Hand imagery to `brandkit`.
6. **Colour**: candidates from `ui-ux-pro-max --domain color`, roles and usage rules.
7. **Typography**: candidates from `--domain typography`, plus scale, weights, fallbacks,
   licence check.
8. **Space, imagery, applications.**
9. **Accessibility, computed.** Every real pair, reported as numbers.
10. **Tokens** from `design_token_generator.py`, checked and overridden where they fight the
    palette.
11. **Kill list, write the file, assemble the manual if asked.**

---

## Writing Rules

**Internal:** direct, bullets, lead with the recommendation.

**Client-facing:** operator, not consultancy. **Never mention NexusPoint or Aleem** in the
document, including in `16-brand-guidelines.md`.

Both: no emojis, no em dashes in body text. Every colour has a role and a rule. Every contrast
claim has a number.

---

## Edge Cases

| Scenario | Action |
|---|---|
| Brand book and live site disagree | Record both. The divergence is a finding, and the live site is the truth |
| Client has raster-only logo files | Hard constraint. Say so early; it changes what is deliverable |
| Brand colour fails AA for body text | Supply an accessible variant for text, keep the original for large display. Never silently drop it, never ship it failing |
| Client asks for the 80% colour statistic | No traceable primary source `[P]` [s144] [s147]. Give what is established instead `[C]` [s107] [s104] |
| Client asks whether serif or sans is more legible | Genuinely contested. No universal rule. Do not invent one |
| Asked for font licensing cost | Verify per foundry. Never quote from memory. Say what was and was not checked |
| Asked what a new logo is worth in revenue | No traceable ROI study exists. Direction only |
| Asked to generate the actual logo or brand board | Say `taste-skill:brandkit` was archived 2026-08-27 and no current skill generates imagery. This skill writes the spec |
| Token generator output fights the palette | Override and record why. It derives algorithmically from one hex and is a starting scale |
| Assemble requested but `14` is missing | Say which document is missing and offer `brand-voice`. Do not invent the voice section |
| `13`, `14` and `15` disagree during assembly | Stop and fix the source document. Never reconcile silently in the manual |
| Client says the guidelines are ignored | Governance finding, not a design one `[C]` [s45] [s50]. A better PDF will not fix it |

---

## Reference Map

```
references/
├── method.md             THE PIPELINE, phases 0-10, including the runnable WCAG contrast
│                         formula (Phase 8) and the consistency caveat
├── review-rubric.md      Audit mode: 7-row scorecard, sample-the-site-first reading order
└── report-structure.md   Deliverable section order for 15-brand-visual-identity.md, each
                          section with its "fails when" test, plus the 16-brand-guidelines.md
                          assembly rules
```

No `_research/` here on purpose. `[sN]` resolves via
`.claude/skills/branding-advisor/_research/sources.json`, 260 sources, 132 confirmed. Run
`branding-advisor/_research/gather.py verify` after any citation edit; it checks this skill's
`references/` too.

Accessibility is deliberately **not** cited to `[sN]`. WCAG is a standard, not a research
finding, and the corpus does not cover it.
