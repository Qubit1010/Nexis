# LinkedIn-Template-1 — Design Structure

Canonical spec extracted from the reference infographic in
`docs/LinkedIn-Template-1/LinkedIn-Template-1.jpg`.
This file is the source of truth for `gem.md` and `input-prompt.md`.

The reference has no baked-in handle or footer, so there is no source identity to strip.
An optional `@{{HANDLE}}` / name footer slot is added for the user to fill or leave blank.

## Global

- **Canvas:** 1080 x 1350 px, 4:5 portrait. The whole infographic is ONE image.
- **Format:** single dense bento/masonry grid of category cards under a bold title. This is NOT a
  multi-slide carousel. The entire graphic renders in one image. See `gem.md` OUTPUT FORMAT.
- **Template purpose:** "N ways / N tools / N tactics" round-up infographics. Each card groups one
  category and shows the tools (with real brand logos) or items in that category plus a one-line
  explanation. Ideal for "11 AI tools by use case", "8 ways to X", framework breakdowns, tool stacks.
- **Tone:** clean, editorial, scannable. Reads like a polished reference chart, not an ad.
- **Density rule:** keep total cards to what stays legible at 1080x1350. 9-12 cards is the sweet spot.
  Fewer items per card = larger, more readable logos and text.

## Layout

### Title block (top ~12% of canvas)
- Large heavy bold black sans headline, left-aligned, 1-2 lines.
  Example: "11 Ways to Increase Productivity with AI".
- A short **teal/mint vertical accent bar** sits immediately to the LEFT of the title's first line.
- The number in the title ("11") can be the same black as the rest, or accented — keep it simple,
  matching the reference (all black).

### Bento grid (remaining ~88%)
- A masonry grid of rounded cards filling the canvas below the title with even gutters.
- Rows mix card counts: **three-up rows** and **two-up rows** where a wider card spans the
  space freed by a narrower neighbour. Reference layout (4 rows):
  - **Row 1 (3-up):** small + small + small
  - **Row 2 (2-up):** one narrow card + one WIDE card (the wide card holds more logos)
  - **Row 3 (3-up):** small + small + small
  - **Row 4 (3-up):** small + small + small
- Put categories with MORE tools (3+ logos) in the WIDE cards; single-logo categories go in narrow cards.
- All cards share the same corner radius, border, and fill. Heights align per row.

## Card anatomy (repeated)

- **Black pill header**, centered at the card's top edge: a rounded black pill with white bold
  text = the category name. One featured category (typically the first) uses **teal text** instead
  of white inside the same black pill.
- **Brand logos**: the real, full-color logos of the tools in that category, centered in the card
  body, evenly spaced. Single-tool cards show one large logo/wordmark; multi-tool cards show 2-3.
- **Tool-name labels**: small grey text under each logo when the logo alone is not self-evident
  (e.g. "Otter.ai", "Fireflies", "granola", "Cursor", "Claude Code", "reclaimai", "motion").
  Omit the label when the logo already contains the name as a wordmark (e.g. "perplexity", "replit").
- **Description**: 1-2 lines of small dark-grey regular sans at the bottom of the card, explaining
  what the category / tools do. Plain language, no jargon.
- **Card styling**: warm off-white / ivory fill, ~16px rounded corners, thin light-grey border.

## Palette (canonical, brand-overridable)

| Token | Hex | Use |
|---|---|---|
| Page bg | `#F2F2F0` | light warm grey page background |
| Card bg | `#FBF7F1` | warm ivory card fill |
| Card border | `#E6E2DA` | thin card stroke |
| Pill fill | `#111111` | black category pill |
| Pill text | `#FFFFFF` | category text inside pill |
| Accent | `#14B8A6` | teal/mint — title accent bar + featured pill text |
| Title ink | `#141414` | headline + heading text |
| Description text | `#5A5A5A` | card description lines |
| Tool-name labels | `#6E6E6E` | small grey labels under logos |

## Type stack

- **Title:** heavy bold grotesque (Inter Bold / Helvetica Now Bold / similar), large, left-aligned.
- **Pill text:** bold sans, white (or teal for the featured card), centered.
- **Tool-name labels:** small regular sans, grey.
- **Description:** regular sans, dark grey, 1-2 lines.

## Identity

- **NexusPoint logo:** always placed small (~80-100px tall) at the **top-right** of the page, in the
  margin area above the card grid. Attach `brand-assets/logos/nexuspoint-logo.png` as a Knowledge
  file in the Gem.
- **No handle or footer:** do not add any `@name` or text at the bottom of the infographic.

## Content rules

- Title: one line if it fits, else two. Keep the "N" count accurate to the number of cards/categories.
- Category pill: 1-3 words, the use case ("General", "Meetings", "App Building", "Workflow Automation").
- Per card: 1-3 tools max for legibility (wide cards can hold 3). Use real brand names + logos.
- Description: one crisp sentence (max ~12 words), plain English.
- Logos must be the real, recognizable brand marks in full color, not invented icons.
- All text must be legible at 1080x1350 — if it would be too small, cut items, don't shrink text.
- No emojis. No em dashes (use commas or periods).
