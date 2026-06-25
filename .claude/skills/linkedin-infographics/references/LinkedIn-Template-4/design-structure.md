# LinkedIn-Template-4 — Design Structure

Canonical spec extracted from the reference infographic in
`docs/LinkedIn-Template-4/LinkedIn-Template-4.jpg`.
This file is the source of truth for `gem.md` and `input-prompt.md`.

Source brand identity stripped (Claude logo removed). NexusPoint logo replaces it top-right per brand rule.

## Global

- **Canvas:** 1080 x 1350 px, 4:5 portrait. The whole infographic is ONE image.
- **Format:** numbered pattern catalogue. A bold title block at the top, then 4-6 full-width
  numbered rows stacked vertically, one per pattern/item. NOT a bento card grid, NOT horizontal
  tier bands.
- **Template purpose:** "N patterns for X", design pattern references, methodology breakdowns,
  architecture guides, "how X works" explainers, comparison catalogues. Best for 4-6 items where
  each needs a name, short description, 3-4 use-case tags, and a flowchart/diagram.
- **Tone:** technical, authoritative, educational. Reads like a sharp engineering reference card.

## Layout

### Title block (top ~15% of canvas)

- **Main title:** ultra-heavy bold grotesque (Inter Black / Montserrat Black), very large,
  left-aligned, 1-2 lines. Key words highlighted in the row-01 accent (orange #E85D1A); remaining
  words in black (#1A1A1A). Example: "HOW TO" (black) + "COORDINATE" (orange) / "MULTIPLE AI AGENTS" (black).
- **Brand logo:** source logo stripped. Place NexusPoint logo (~120-150px tall) top-right,
  vertically centered in the title block.
- **Separator:** a thin horizontal rule (1-2px, orange or dark) separating the title block from the
  pattern rows below.

### Numbered pattern rows (~85% of canvas)

4-6 rows stacked directly below the title. Each row is the same height (equal division of the
remaining canvas). Page background is warm cream (#FAF6F0) throughout; rows are separated by thin
1-2px lines (#E8E0D5).

**Left zone — Number box (~12% width)**
- Solid filled rectangle the full height of the row, accent color for that row.
- Large bold white number ("01", "02" ...) centered in the box.

**Center zone — Text block (~48% width)**
Left-to-right layout inside this zone:
- **Category label** (top): small all-caps, letter-spaced, accent color. 2-4 words.
  Answers "when does this apply?" — e.g. "QUALITY-CRITICAL OUTPUT".
- **Pattern name** (below label): extra-bold large sans, accent color. 1-3 words.
  The canonical name of the pattern — e.g. "GENERATOR-VERIFIER".
- **Description** (body): regular sans, dark (#222222), 2-3 sentences, medium size.
  What the pattern is and how it works, in plain language.
- **Use-case tags** (bottom): 3-4 rounded pill tags on one line, left-aligned.
  Pill bg: #EDE8E0, text: #333333, small font. Concrete use cases (e.g. "Code generation",
  "Fact-checking", "Compliance checks").

**Right zone — Diagram (~40% width)**
- A schematic flowchart or node diagram illustrating the pattern's architecture.
- Accent color for node fills or outlines and key arrows.
- 3-6 labeled nodes max. Clean, minimal connectors with thin arrows and short labels.
- Sits on the row's cream background. No extra panel border.

### Per-row accent colors (canonical order, cycle if >5)

| Row | Accent | Hex |
|-----|--------|-----|
| 01 | Orange | #E85D1A |
| 02 | Teal | #0D9B8C |
| 03 | Purple | #5C5EA7 |
| 04 | Amber | #E8A020 |
| 05 | Rose | #C43059 |
| 06+ | cycle from 01 | — |

## Palette

| Token | Hex | Use |
|---|---|---|
| Page / row background | `#FAF6F0` | warm cream throughout |
| Row separator | `#E8E0D5` | thin 1-2px line between rows |
| Title ink (non-accent) | `#1A1A1A` | main title words not highlighted |
| Body text | `#222222` | description paragraphs |
| Category label | accent per row | small-caps header |
| Pattern name | accent per row | bold main heading |
| Number box fill | accent per row | solid left column |
| Number text | `#FFFFFF` | white, bold, centered in box |
| Tag pill bg | `#EDE8E0` | use-case pill background |
| Tag pill text | `#333333` | use-case pill text |
| Diagram nodes | accent per row | fills or outlines |
| Diagram labels | `#1A1A1A` | node text |

## Type stack

- **Title:** ultra-heavy grotesque (Inter Black / Montserrat Black), very large. Accent words in
  orange #E85D1A; remaining words in #1A1A1A.
- **Category label:** small all-caps, letter-spaced, accent color, regular/medium weight.
- **Pattern name:** extra-bold sans, accent color, large.
- **Description body:** regular sans, #222222, medium size, tight line height.
- **Tag pills:** small regular sans, #333333.
- **Number in box:** bold/extra-bold sans, white, very large.
- **Diagram labels:** small regular or medium sans, #1A1A1A.

## Structural rules

- 4-6 patterns. Fewer than 4 feels thin; more than 6 makes rows too short to read.
- Number boxes form a fixed-width aligned left column across all rows.
- All rows are the same height (equal division of the canvas minus the title block).
- Diagrams stay within the right zone and within the row's height — do not overflow.
- Use-case tags on one line, left-aligned, 3-4 max. If a tag is long, use fewer.

## Identity

- **NexusPoint logo:** ~120-150px tall, top-right of the title block, replacing the source logo.
  Attach `brand-assets/logos/nexuspoint-logo.png` as a Knowledge file in the Gem.
- **No handle or footer** at the bottom.
