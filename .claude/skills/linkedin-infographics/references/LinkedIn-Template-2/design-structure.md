# LinkedIn-Template-2 — Design Structure

Canonical spec extracted from the reference infographic in
`docs/LinkedIn-Template-2/LinkedIn-Template-2.jpg`.
This file is the source of truth for `gem.md` and `input-prompt.md`.

No handle or watermark in the reference. NexusPoint logo placed top-right per brand rule.

## Global

- **Canvas:** 1080 x 1350 px, 4:5 portrait. The whole infographic is ONE image.
- **Format:** tiered horizontal band layout. NOT a flat bento card grid. Three stacked comparison
  bands (one per tier/level) run across the full width, each slightly darker green than the one
  above, then a full-width tools reference section at the bottom.
- **Template purpose:** progression frameworks, level comparisons, "beginner vs advanced" guides,
  "3 approaches to X", spectrum-of-complexity content. Ideal for: coding approaches, business
  maturity levels, product tiers, workflow complexity, adoption stages.
- **Tone:** executive-facing, authoritative, educational. Reads like a polished strategy slide.

## Layout

### Title block (top ~12% of canvas)
- **Main title:** ultra-heavy bold black sans, very large, left-aligned, 1 line.
  Example: "Agentic Coding in 2026"
- **Subtitle:** regular-weight sans, smaller, left-aligned, 1 line below the title, dark grey.
  Example: "The simple guide executives need to succeed with AI"
- **NexusPoint logo:** small (~80-100px tall) top-right, in the title block margin.

### Three tier bands (stacked, ~70% of canvas)
Each band occupies a full-width horizontal strip and contains three zones:

**Left zone — Metric label (~15% width)**
- Bold/semibold sans, left-aligned, 1-2 lines.
- A key outcome or metric for this tier. Example: "10x Faster Prototype", "25-30% Productivity".
- No background — floats on the page bg against the band edge.

**Center zone — Diagram (~40% width)**
- The visual/flow diagram for this tier. Can be:
  - A circular/step flowchart (numbered steps in rounded nodes connected by arrows).
  - A dependency/hierarchy diagram showing the building blocks.
  - A network of labeled nodes.
- Diagrams are fully contained inside the band's colored background area.
- Nodes use the band's color family; connectors are thin lines/arrows.

**Right zone — Explanation panel (~45% width)**
- A three-point structured list:
  - **1 What is [Tier]** — one bullet: the definition in plain language.
  - **2 How it works** — one bullet: the mechanism in one sentence.
  - **3 When to use it** — one bullet: the ideal use case / trigger condition.
- Above the list: the **tier name pill** (left) and **level badge** (right) on the same row.

### Tier pill + level badge (inside each band, top of right zone)
- **Tier name pill:** centered label with the tier name (e.g. "Vibe-Coding", "AI-Assisted",
  "Agentic"). Text on the band's background — not a distinct filled pill; it reads as a section
  header embedded in the band color.
- **Level badge:** right-aligned on the same row: "Level: Non-Tech" / "Level: Mid-Level" /
  "Level: Advanced". Small bold text on a slightly contrasting pill or plain.

### Bottom tools section (~18% of canvas)
- Full-width strip with a light green background.
- Header: "AI Tools and Products to Use" centered, bold sans, dark.
- Three equal columns, one per tier, each with:
  - Column header: tier name, bold sans, centered (e.g. "Vibe-Coding", "AI-Assisted", "Agentic Coding").
  - Real brand logos/wordmarks of the tools in that tier, arranged in a 2-3 row grid, centered.

## Palette (canonical, brand-overridable)

| Token | Hex | Use |
|---|---|---|
| Page bg | `#FFFFFF` | white page background |
| Band 1 bg | `#E8F5E3` | very light mint — top/easiest tier |
| Band 2 bg | `#B8DDB0` | medium green — mid tier |
| Band 3 bg | `#8CC484` | sage green — advanced/top tier |
| Tools section bg | `#D4EDD4` | light green bottom strip |
| Title ink | `#1A1A1A` | main title |
| Subtitle | `#555555` | subtitle line |
| Metric text | `#1A1A1A` | left metric labels |
| Body text | `#333333` | explanation bullets |
| Level badge text | `#1A1A1A` | "Level: X" label |

## Type stack

- **Title:** ultra-heavy bold grotesque (Inter Black / Montserrat Black / similar), very large.
- **Subtitle:** regular sans, smaller, dark grey.
- **Metric labels (left):** bold sans, medium-large, 1-2 lines.
- **Tier name:** bold sans, embedded in the band (not a distinct filled pill).
- **Level badge:** small bold sans, right-aligned.
- **Numbered point headers (1 What is / 2 How it works / 3 When to use it):** bold sans, dark.
- **Bullet descriptions:** regular sans, dark grey.
- **Tools column headers:** bold sans, centered.

## Structural rules

- Three tiers ONLY. The template is not designed for 2 or 4 tiers.
- Tier order = simplest/lowest at top (lightest color) to most complex/advanced at bottom (darkest).
- Each tier's left metric, center diagram, and right explanation must stay within the band's height.
- The bottom tools section always spans all three tier columns.
- Diagrams in the center zone should be simple and schematic — flowcharts, not detailed screenshots.

## Identity

- **NexusPoint logo:** always placed small (~80-100px tall) at the **top-right** of the title block.
  Attach `brand-assets/logos/nexuspoint-logo.png` as a Knowledge file in the Gem.
- **No handle or footer** at the bottom.
