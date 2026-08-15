# Deliverable Structure — `15-brand-visual-identity.md`

Section order for the visual identity specification.

**This document is the written spec, not the artwork.** It defines the system precisely enough
that a designer can execute it and a developer can build it. Imagery generation hands off to
`taste-skill:brandkit`. Keep that boundary: a spec that gestures at a "modern, clean look"
without hex values, type scales and measured contrast ratios is a mood board, not a
deliverable.

---

## 0. What we know

The house opener. `| Fact | Source | Confidence |`, what we examined (site, existing assets,
old brand PDF), what the client stated, what came from `13-brand-strategy.md`.

Record the **current-state facts** here: existing hex values sampled from their site, fonts
currently loaded, logo file formats they actually possess. Much of an identity engagement is
discovering the client does not have the assets they think they have.

**Fails when** it describes their current identity from impression rather than from measurement.

---

## 1. Visual direction

The idea the system expresses, in a paragraph, traced back to the brand strategy. Which
personality trait and which position each visual decision serves.

Every later section refers back here. A colour chosen because it looks good is a preference; a
colour chosen because the brand is positioned against a category of loud competitors is a
decision.

**Fails when** it is a list of style adjectives. "Modern, clean, professional" describes most
of the internet.

---

## 2. Logo direction

The concept routes, with reasoning. For each route: the idea, why it fits the positioning,
the construction logic, and how it behaves as an icon.

Also required:
- **Clear space and minimum sizes**, stated in absolute units.
- **Variants needed**: primary, stacked, icon-only, single-colour, reversed.
- **Misuse**: the specific ways this mark will get broken. Stretched, recoloured, placed on a
  busy photo, rebuilt in PowerPoint.

Hand off to `taste-skill:brandkit` for the actual boards and marks. State the handoff.

If they have an existing logo, this section decides **keep, refine, or replace** and defends
it. Replacement discards accumulated recognition, which is a real cost and must be weighed
rather than assumed away. See `what-not-to-do.md`.

**Fails when** it recommends a full redesign by reflex, or describes a mark so vaguely that
three designers would produce three unrelated things.

---

## 3. Colour system

Roles first, values second. A palette without roles is a swatch collection.

| Role | Requirement |
|---|---|
| Primary | The brand colour. Where it is and is not used. |
| Secondary | Support. Explicitly not a second primary. |
| Accent | Sparingly, for action. Usually one. |
| Neutrals | The full grey ramp doing most of the actual work. |
| Semantic | Success, warning, error, info. |

For each: hex, and **where it is used and where it must not be**. A primary that can go
anywhere ends up everywhere and the identity flattens.

Query `ui-ux-pro-max/scripts/search.py --domain color` for candidates rather than inventing
from scratch, then justify the choice against section 1.

**Every foreground and background pair a user can actually encounter gets a measured contrast
ratio.** Measured, not estimated. See section 8.

**Fails when** the palette has five colours of equal weight, when neutrals are an
afterthought, or when contrast is asserted rather than computed.

---

## 4. Typography

The pairing, the scale, and the constraints.

- **Display and body faces**, with why each fits the direction. Query
  `ui-ux-pro-max/scripts/search.py --domain typography` for candidates.
- **Type scale**: named steps with sizes and line heights. State the ratio used.
- **Weights actually needed.** Every extra weight is a real page-weight cost, so list only
  what the system uses.
- **Fallback stack** for each face.
- **Licensing status.** Web, desktop, and app use are licensed separately and a client can be
  genuinely non-compliant without knowing. State what was checked and what was not. Do not
  state a licensing cost that was not looked up.

**Fails when** it names two fonts and stops. A pairing without a scale, weights, fallbacks and
a licence check is not implementable.

---

## 5. Space, layout and grid

Spacing scale, grid, breakpoints, corner radii, border weights, elevation. The invisible layer
that makes an identity feel coherent across surfaces that share no content.

**Fails when** it is omitted. This is the most commonly skipped section and the most common
reason a brand looks consistent in the deck and inconsistent in production.

---

## 6. Imagery and art direction

What pictures this brand uses: subject, treatment, crop, colour handling, and what it never
uses. Include a stock-photography position, since that is where most identities visibly break.

If they cannot commission photography, say so and design a system that survives without it.

**Fails when** it describes an ideal image library the client will never produce.

---

## 7. Applications

Where the system shows up and what changes in each: website, social profiles and posts, email,
documents and proposals, print, signage, packaging, merchandise. Only the surfaces they
actually use.

**Fails when** it shows a business card and a billboard for a business that sells software.

---

## 8. Accessibility

Non-negotiable, and measured.

- Contrast ratios for **every** text and UI pair, against WCAG AA as the floor. Report the
  computed number, not a pass or fail alone.
- Colour must never be the only carrier of meaning.
- Minimum type sizes and touch targets.
- Focus states defined, not left to the browser.

Where a brand colour fails contrast, **fix it here** by supplying an accessible variant for
text use while keeping the original for large display use. Do not quietly drop the brand
colour, and do not ship an inaccessible one.

**Fails when** contrast is claimed without a number.

---

## 9. Design tokens

The system as code, generated rather than hand-typed:

```
python .claude/skills/ui-design-system/scripts/design_token_generator.py "<primary-hex>" modern json
```

Also available: `css`, `scss`. **Never `summary`**: it prints emoji, which violates the house
style rule.

Treat the output as a **starting scale, not the answer**. It derives tints and shades
algorithmically from one hex, so check the generated steps against the roles in section 3 and
override any that fight the palette. Record what was overridden and why.

**Fails when** generated output is shipped unchecked, or when the tokens and section 3
disagree.

---

## 10. What we could not establish

Assets we could not obtain, licences we could not verify, decisions blocked on the client.

---

## The assembled document — `16-brand-guidelines.md`

When the client wants the single guidelines manual, assemble from `13`, `14` and `15` in the
order a designer or writer reads:

1. The brand in one page (from 13 §1)
2. Positioning, personality, promise, story, values (13 §2-6)
3. Voice, tone, messaging, vocabulary (14 §2-6)
4. Logo (15 §2)
5. Colour (15 §3)
6. Typography (15 §4)
7. Space and layout (15 §5)
8. Imagery (15 §6)
9. Applications (15 §7)
10. Accessibility (15 §8)
11. Tokens and asset index (15 §9)

Rules for assembly:

- **Do not re-derive anything.** Pull the finished sections. If 13, 14 and 15 disagree, stop
  and fix the source document rather than reconciling silently in the assembly.
- **Drop the internal scaffolding.** Section 0 tables, assumption lists and "what we could not
  establish" belong in the working documents, not in the client's manual. Carry any genuinely
  unresolved item into a short closing "Open decisions" page instead.
- **Never mention NexusPoint or Aleem** anywhere in it.
- Offer the Google Doc via `content-engine/scripts/save_content.py` and the PDF via
  `seo-advisor/scripts/seo_pdf.py`. Neither is built by default.

**Fails when** the assembly is a concatenation. The manual has one voice and one audience;
three documents stapled together read as three documents stapled together.
