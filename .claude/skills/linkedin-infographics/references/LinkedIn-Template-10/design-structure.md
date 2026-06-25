# LinkedIn-Template-10 — Design Structure

Canonical spec extracted from the reference infographic in
`docs/LinkedIn-Template-10/LinkedIn-Template-10.jpg`.
Source brand identity stripped (Claude asterisk icon, all "Claude" references removed).
NexusPoint logo replaces source branding per brand rule.

## Global

- **Canvas:** 1080 x 1350 px, 4:5 portrait. The whole infographic is ONE image.
- **Format:** flat 3-column numbered card grid. A large center-aligned display title, then 12
  equal cards in a 3-column x 4-row grid. No phases, no horizontal bands, no numbered list rows —
  just a clean three-column tile layout where every card is independent.
- **Template purpose:** feature showcases, capability rundowns, "N things worth knowing", "N moves
  worth stealing", tactic catalogues, tool capability explainers, "plays to steal", "things you
  didn't know you could do with X". Each item needs: a number, a 2-4 word bold title, 2-3 punchy
  sentences, and an illustration.
- **Tone:** discovery-oriented, punchy, educational. Reads like a cheat-sheet of underused
  features or high-leverage tactics.

## Layout

### Title block (top ~12% of canvas)

- **Decorative icon:** small orange asterisk/sunburst icon, centered, directly above the numeral.
- **Large numeral:** very large bold display grotesque, center-aligned, accent orange (#D96B32).
  Represents the item count. Sits on the same line as the first key word(s) of the title.
- **Title words:** bold heavy grotesque, same scale, center-aligned, black (#1A1A1A). 2-4 words,
  can span 1-2 lines after the numeral.
- **Layout example:**
  ```
       ✳  (orange asterisk, centered)
   12 Things
  Worth Knowing
  ```
- The numeral is on the first title line alongside 1-2 words; remaining words wrap to line 2.
- No subtitle line. No horizontal divider.
- **NexusPoint logo:** ~80-100px tall, top-right corner of the full canvas (in the margin above
  the card grid). Small and unobtrusive.

### Card grid (3 columns x 4 rows = 12 cards)

- All 12 cards equal width and equal height.
- Cards have thin light-grey rounded border and white fill.
- Small consistent gap between all cards.
- NO phase groupings, NO colored section headers, NO row labels.

### Card anatomy (per card)

**Number badge (top-left corner of card)**
- Small filled circle, accent orange (#D96B32), white bold number inside ("01", "02" ... "12").
- Positioned top-left, inline with the card title.

**Card title (top, beside the badge)**
- 2-4 words, bold grotesque, black (#1A1A1A).
- All-caps or title case (reference uses a mix — prefer 2-line ALLCAPS in the reference, e.g.
  "BUILD WEBSITES / WITHOUT CODING").
- Occupies the left ~60% of the card top section.

**Body copy (middle-left, ~60% card width)**
- 2-3 short sentences, small regular sans, dark grey (#555555).
- Each sentence is 1 line or very short. Reads like rapid-fire observations.
- No bullet points — plain sentences separated by line breaks.

**Illustration (right side, ~40% card width, top-to-middle)**
- A simple hand-drawn-style outline wireframe illustrating the concept.
- Line art / sketch style: thin dark grey lines on white, no fills, no solid icon blocks.
- Examples: browser window with content, phone screen, command terminal, spreadsheet grid,
  flowchart nodes, chat UI bubble, calendar with recurring arrow, brain/network graph, document
  with chart.
- Optional small brand logo overlay on top of the sketch (e.g. GitHub logo, Excel X, Gemini G).

**Tool logos (bottom-right of card, optional)**
- Real full-color brand logos where directly relevant (GitHub, Slack, Gmail, Notion, Excel, Canva,
  Google Drive, etc.).
- Small (~24-32px). 1-4 logos per card maximum. Only include if the card is about a specific tool.

## Palette

| Token | Hex | Use |
|---|---|---|
| Page background | `#FAF6F0` | warm off-white throughout |
| Card background | `#FFFFFF` | card fill |
| Card border | `#E8E4DC` | thin rounded-rect border |
| Title numeral | `#D96B32` | the large count numeral |
| Decorative icon | `#D96B32` | asterisk above numeral |
| Badge background | `#D96B32` | circle badge in every card |
| Badge text | `#FFFFFF` | number inside badge |
| Card title | `#1A1A1A` | card heading |
| Body text | `#555555` | card body copy |
| Illustration lines | `#333333` | sketch art lines |

## Type stack

- **Title numeral:** very large bold/black display grotesque, accent orange #D96B32.
- **Title words:** bold/black display grotesque, same scale, black #1A1A1A. Center-aligned.
- **Card title:** bold grotesque, medium-large, black #1A1A1A.
- **Body text:** regular sans, small-medium, dark grey #555555.
- **Badge number:** bold sans, white #FFFFFF, small.

## Structural rules

- Exactly 12 cards in a 3-column x 4-row grid. All cards equal width. All rows equal height.
- Orange circle badge top-left of every card, white number inside.
- Sketch/wireframe illustration in the top-right area of every card.
- Body copy on the left side of the card, flows from the title down.
- Tool logos bottom-right inside the card (optional, only where relevant).
- Cards are flat and independent — no hierarchy, phases, or groupings.
- Title numeral is very large and orange; title words are bold and black; both center-aligned.
- Decorative asterisk is centered above the numeral — it is decorative, not a bullet.

## Identity

- **NexusPoint logo:** ~80-100px tall, top-right corner of the infographic, above the card grid.
  Attach `brand-assets/logos/nexuspoint-logo.png` as a Knowledge file in the Gem.
- **No handle or footer** at the bottom.
