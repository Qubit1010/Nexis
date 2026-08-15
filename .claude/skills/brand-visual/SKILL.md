---
name: brand-visual
description: >
  Use to BUILD or AUDIT what a brand looks like, as a written specification: colour system,
  typography, logo direction, spacing and layout, imagery direction, applications,
  accessibility, and design tokens. Also assembles the single brand guidelines manual from the
  strategy, voice and visual documents. This is the execution skill that produces the artifact,
  not the advice skill.
  Triggers on: visual identity, brand visual identity, corporate visual identity, brand
  guidelines, brand book, brand manual, style guide, brand style guide, design system for the
  brand, design tokens, colour system, color palette, brand colours, primary and secondary
  colours, typography, brand typeface, font pairing, type scale, font licensing, logo
  direction, logo concept, logo system, logo variants, clear space, logo misuse, wordmark,
  keep or replace the logo, refresh the logo, visual direction, art direction, imagery
  guidelines, brand applications, contrast ratio, WCAG, accessible palette, our colours fail
  contrast, assemble the brand guidelines, build the brand manual, audit their visual identity,
  review this brand book, their branding looks dated, looks different on every platform.
  Works from whatever exists: a live website it samples actual hex values and loaded fonts
  from, a PDF or DOCX brand book, a Google Doc, logo files, or a client-projects slug. Consumes
  13-brand-strategy.md and 14-brand-voice.md so every visual decision traces to a personality
  trait or a position.
  Outputs client-projects/<slug>/15-brand-visual-identity.md and, on request,
  16-brand-guidelines.md assembled from 13, 14 and 15. Measures rather than asserts: it
  computes WCAG contrast ratios for every real foreground and background pair instead of
  claiming a palette is accessible, samples live values instead of trusting the brand book, and
  reuses ui-ux-pro-max's palette and typography data plus ui-design-system's token generator
  rather than inventing from scratch.
  Numbers cited as [sN] resolve via branding-advisor's corpus. It refuses the "colour increases
  brand recognition by 80%" claim, which has no traceable primary source, asserts no
  serif-versus-sans legibility rule because the evidence is genuinely contested, quotes no font
  licensing costs it has not verified, and gives no logo-change ROI figure because none exists.
  Scope is deliberately the visual system only. For positioning, personality, promise or story
  use brand-strategy. For voice, messaging, naming or taglines use brand-voice. For generating
  actual logo imagery, brand boards or identity decks use taste-skill:brandkit. For explaining
  or diagnosing branding use branding-advisor. For building a website or app UI use
  ui-ux-pro-max, senior-frontend or nexis-builder.
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
                          (the actual imagery)              (dev tokens)
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
| `taste-skill:brandkit` | Generating logo boards, identity decks, brand imagery |
| `ui-design-system` | Turning the approved palette into dev token files |
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
| Asked to generate the actual logo or brand board | Route to `taste-skill:brandkit`. This skill writes the spec |
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
