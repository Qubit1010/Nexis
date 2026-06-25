# LinkedIn-Template-11 — Design Structure

Canonical spec extracted from the reference infographic in
`docs/LinkedIn-Template-11/LinkedIn-Template-11.jpg`.
Source brand identity stripped (coral pill content, "Claude" references, footer CTA removed).
NexusPoint logo replaces source branding per brand rule.

## Global

- **Canvas:** 1080 x 1350 px, 4:5 portrait. The whole infographic is ONE image.
- **Format:** two-column hybrid layout. Left column (~65% width): numbered "N Ways" vertical list.
  Right column (~35% width): "Best Practices" sidebar. Full-width definition row at top, full-width
  footer bar at bottom. NOT a bento grid, NOT horizontal bands, NOT a phase roadmap.
- **Template purpose:** "How I use X in my daily workflow", "N ways I use X", personal workflow
  breakdowns, tool tutorials with best practices, feature walkthroughs, "here's how I actually use
  this tool" posts. Best when you have 4-6 main points AND a separate set of 3-4 best practices.
- **Tone:** personal, educational, practical. First-person voice. Like a workflow breakdown from
  a practitioner, not a product page.

## Layout (5 sections, top to bottom)

### Section 1 — Title block (~12% of canvas, top)

- **Main title:** large bold display grotesque, left-aligned, 2-3 lines.
  - One key phrase (2-4 words) is highlighted in a **coral rounded pill** (white text inside,
    coral background #F07560). This pill sits inline in the title text, replacing those words.
  - All other title words: bold black (#1A1A1A).
  - Example: "How I Use [**Claude Cowork**] in My Daily Workflow" where "Claude Cowork" is the pill.
- **Subtitle:** small italic grey, 1 line, in parentheses. e.g. "(and why it's my #1 AI tool right now)"
- **NexusPoint logo:** ~80-100px tall, top-right of the title block.
- **Decorative sparkles:** optional small 4-pointed star icons scattered near the title, orange/gold.
- **Page background:** warm off-white (#FAF6F0) throughout.

### Section 2 — Definition row (full width, ~8% of canvas)

Three equal-width definition boxes side by side, spanning the full canvas width. Each box:
- Small orange icon (left, ~24px): a simple flat icon representing the concept.
- **Label** (bold, 1-2 words): the thing being defined (e.g. "Claude =", "Cowork =").
- Short **definition** (1-2 sentences): plain English, what it is.
- Left border: thin amber/orange vertical line accent (#E8A020).
- Background: same warm cream as the page, or very slightly darker warm beige.

### Section 3 — Left column: numbered list (~70% of remaining height, 65% width)

**Section header bar:**
- Full left-column width, dark navy background (#1C2B3A), white bold text.
- Format: "[N] Ways I Use [Subject]" — e.g. "5 Ways I Use Claude Code"

**Numbered rows (4-6 items, stacked with thin dividers between):**
Each row occupies about 16-20% of the column height. Anatomy:

- **Number badge (left edge):** large filled orange circle (#E85D1A), white bold number inside
  ("1", "2", "3"... not zero-padded). Badge ~44-50px diameter.
- **Title (right of badge, top):** bold grotesque, large, black (#1A1A1A). 1-2 lines.
  Often 2-4 words, sometimes an ampersand ("Research & Document Drafting").
- **Subtitle/description (below title):** 1-2 short sentences, regular sans, dark grey (#444444).
  Plain English, what this use does.
- **Italic tagline (below description):** italic, accent orange/coral (#E85D1A), short punchy
  phrase. e.g. "It handles the busywork." / "Pulls context + writes for you."
- **Sketch illustration (right side of row, ~30% row width):** hand-drawn outline wireframe,
  same sketch style as Template-10. Dark lines, no fill. Represents the concept visually.
- **Thin horizontal divider** between rows.

### Section 4 — Right column: sidebar (~70% of remaining height, 35% width)

**Sidebar header bar:**
- Full right-column width, dark navy background (#1C2B3A), white bold text.
- Includes a small gold/amber star icon left of the text.
- Format: "Best Practices for [Subject]"

**Sidebar cards (3-4 items, stacked with thin dividers):**
Each card:
- **Icon (top-left, ~24px):** flat orange/coral icon representing the topic (folder, brain,
  checklist, lightning bolt, calendar, etc.).
- **Title (right of icon, bold):** 3-6 words, bold black. 1-2 lines.
- **Description (below title):** 2-3 sentences, small regular sans, dark grey (#555555).
  Practical advice, not definitions.
- **Thin horizontal divider** between cards.

### Section 5 — Footer bar (full width, ~5% of canvas, bottom)

- Rounded pill/banner shape, warm amber-beige background (#F5E8D0).
- Small heart icon (left), italic quote text (center/left), italic follow CTA (right).
- Quote: 1 punchy sentence summarizing the tool's value.
- CTA: "Follow for more [topic] strategies" — this is the only place a CTA appears.
- No handle or @name. No footer outside this bar.

## Palette

| Token | Hex | Use |
|---|---|---|
| Page background | `#FAF6F0` | warm off-white throughout |
| Title pill background | `#F07560` | inline coral pill for key phrase |
| Title pill text | `#FFFFFF` | text inside the pill |
| Title ink | `#1A1A1A` | non-pill title words |
| Subtitle italic | `#666666` | parenthetical subtitle |
| Definition accent border | `#E8A020` | left border on definition boxes |
| Section header bg | `#1C2B3A` | dark navy bars |
| Section header text | `#FFFFFF` | text in navy bars |
| Number badge bg | `#E85D1A` | orange badge circles |
| Number badge text | `#FFFFFF` | number inside badge |
| Item title | `#1A1A1A` | numbered item headings |
| Item description | `#444444` | numbered item body |
| Item tagline | `#E85D1A` | italic accent taglines |
| Sidebar icon color | `#E85D1A` | icons in sidebar cards |
| Sidebar title | `#1A1A1A` | sidebar card headings |
| Sidebar description | `#555555` | sidebar card body |
| Footer bg | `#F5E8D0` | warm amber-beige banner |
| Footer text | `#333333` | quote and CTA |
| Illustration lines | `#333333` | sketch art lines |

## Type stack

- **Title main words:** bold/black display grotesque, large.
- **Title pill text:** bold sans, white, inside coral rounded pill.
- **Subtitle:** small italic sans, grey.
- **Definition label:** bold sans, black, medium.
- **Definition body:** regular sans, dark grey, small.
- **Section header:** bold sans, white, medium-large.
- **Item title:** bold grotesque, medium-large, black.
- **Item description:** regular sans, dark grey, small-medium.
- **Item tagline:** italic sans, orange/coral, small-medium.
- **Sidebar title:** bold sans, black, medium.
- **Sidebar description:** regular sans, dark grey, small.
- **Footer text:** italic sans, dark, small.

## Structural rules

- Two-column split: left ~65%, right ~35%. Both columns share the same height.
- Definition row spans full width (above both columns).
- Footer bar spans full width (below both columns).
- Left column section header + numbered rows stay within the left column — they do NOT span full width.
- Right column sidebar header + cards stay within the right column.
- 4-6 numbered items in the left column. 3-4 cards in the right sidebar.
- Every numbered item must have: badge, title, description, italic tagline, and sketch illustration.
- Every sidebar card must have: icon, title, description.
- Thin dividers between all list/card items.

## Identity

- **NexusPoint logo:** ~80-100px tall, top-right of the title block.
  Attach `brand-assets/logos/nexuspoint-logo.png` as a Knowledge file in the Gem.
- **No standalone handle or footer** outside the footer bar.
