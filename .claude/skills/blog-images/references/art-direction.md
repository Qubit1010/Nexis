# Art direction contract

Every value here comes from `agency/personal-brand-visual-identity.md`, extracted from the live
aleemuh.com CSS. This file is the operational restatement, not a second opinion. If the two
disagree, the identity file wins.

**These images illustrate the personal brand, not the agency.** NexusPoint's palette lives in
`agency/15-brand-visual-identity.md` and shares no hex values with this one. Agency-attributed
lanes (`shorts-creator`, `carousel` Template-2, `hyperframes-reel`) use that. This one does not.

## The governing sentence

> "Diagrams over photographs. This brand sells systems, and a system is better drawn than
> photographed. Diagrams use the palette, the mono face for labels, and the accent for the single
> element under discussion." — `15` §6

That is the whole brief. Everything below implements it.

## Palette

| Role | Hex | Use |
|---|---|---|
| Ground | `#000000` | The canvas. Always. Pure black, the site goes fully dark on OLED |
| Surface | `#101010` | Panels, cards, containers |
| Line | `#1D1E1F` | Hairlines and very subtle dividers |
| **Accent** | `#02A1E1` | **The single subject under discussion.** 7.19:1, safe for text |
| Accent hover | `#0289BF` | Deeper blue, secondary illustration weight. 5.33:1 |
| Text high | `#FFFFFF` | Headlines, primary labels |
| Text secondary | `#CCCCCC` | Body labels, captions. 13.08:1 |
| Text muted | `#8A8A8A` | Metadata, sub-labels. 6.08:1 |
| Border / non-text UI | `#5A5A5A` | Strokes, dividers. 3.04:1. **Never text.** |
| Success | `#4ADE80` | |
| Warning | `#FBBF24` | |
| Error | `#F87171` | Failure markers |

`#CCCCCC`, `#8A8A8A` and `#5A5A5A` are **derived**, not taken from the site: aleemuh.com builds
its greys from white at low opacity, which CSS can do and an SVG palette gate cannot. The
derivation and the contrast maths are in the identity file.

**`#475569` stays banned.** It measures 2.71:1 and fails the body, large-text and non-text UI
floors at once. `render.py` refuses any SVG containing it, and refuses any off-palette hex.

## The accent rule, stated precisely

**One accent *subject* per image, not one accent *shape*.**

A subject can carry several marks that belong to it: a panel border, the nodes inside it, and the
lines joining them are one subject if they are one idea. Two unrelated things both in `#02A1E1` is
the failure. If a reader cannot say in one phrase what the accent is pointing at, the hierarchy has
failed.

Everything not under discussion is `#5A5A5A` stroke on `#101010` fill. Contrast carries the meaning.

## Type

- **Urbanist** for all human-readable labels. Bold 700 for headings and node labels, Regular 400 for body. OFL licensed, already in the repo at `projects/reel-engine/public/fonts/`.
- **Mono system stack** (`ui-monospace, Consolas, monospace`) for anything that should read as machine-produced: numbers, step indices, counts, file names, category eyebrows.
- Never a third family.

Sizes that survive at blog width: title 42, subtitle 20, section heading 19, body 17, node label 17, eyebrow 14. Do not go below 14 in a 1200-wide image.

## What this brand's diagrams never do

Directly from `15` §6 plus the failure modes that make AI-made diagrams recognisable:

- No gradients as decoration. No glow, no neon bloom, no drop shadows.
- No isometric or faux-3D. Flat, orthographic, honest.
- No stock photography, no glowing brains, no robot hands, no circuit-board textures.
- No decorative iconography that carries no information.
- No text below 14px, and no text in `#5A5A5A`.
- No more than one accent subject.

## Composition

Canvas 1200 wide. Margin 72 left and right. Title block top, diagram middle, a thin `#5A5A5A`
divider at 0.4 opacity above a mono footer line carrying one real number.

The footer number is not decoration. It is the article's own measured fact, and it is what makes
the image specific to this article rather than reusable filler.
