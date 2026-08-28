# Art direction contract

Every value here comes from `client-projects/nexuspoint/15-brand-visual-identity.md`. This file is
the operational restatement, not a second opinion. If the two disagree, `15` wins.

## The governing sentence

> "Diagrams over photographs. This brand sells systems, and a system is better drawn than
> photographed. Diagrams use the palette, the mono face for labels, and the accent for the single
> element under discussion." — `15` §6

That is the whole brief. Everything below implements it.

## Palette

| Role | Hex | Use |
|---|---|---|
| Ground | `#02040A` | The canvas. Always. |
| Deep surface | `#06090F` | A third depth, only where two are not enough |
| Raised surface | `#0B0F17` | Panels, cards, containers |
| Secondary | `#00B7FF` | The brand hue. Key illustration only, never small text |
| **Accent** | `#A6DAFF` | **The single subject under discussion** |
| Accent light | `#BAE6FD` | Hover/active derivatives only |
| Text high | `#F1F5F9` | Headlines, primary labels |
| Text mid | `#CBD5E1` | Body labels, captions |
| Text muted | `#94A3B8` | Metadata, sub-labels. 8.00:1 on ground |
| Border / non-text UI | `#64748B` | Strokes, dividers. 4.31:1. **Never text.** |
| Success | `#4ADE80` | 11.4:1 |
| Warning | `#FBBF24` | 12.6:1 |
| Error | `#F87171` | 7.6:1. Failure markers |

**`#475569` is retired.** It measures 2.71:1 and fails the body, large-text and non-text UI floors
at once. `render.py` refuses any SVG containing it, and refuses any off-palette hex.

## The accent rule, stated precisely

**One accent *subject* per image, not one accent *shape*.**

A subject can carry several marks that belong to it: a panel border, the nodes inside it, and the
lines joining them are one subject if they are one idea. Two unrelated things both in `#A6DAFF` is
the failure. If a reader cannot say in one phrase what the accent is pointing at, the hierarchy has
failed.

Everything not under discussion is `#64748B` stroke on `#0B0F17` fill. Contrast carries the meaning.

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
- No text below 14px, and no text in `#64748B`.
- No more than one accent subject.

## Composition

Canvas 1200 wide. Margin 72 left and right. Title block top, diagram middle, a thin `#64748B`
divider at 0.4 opacity above a mono footer line carrying one real number.

The footer number is not decoration. It is the article's own measured fact, and it is what makes
the image specific to this article rather than reusable filler.
