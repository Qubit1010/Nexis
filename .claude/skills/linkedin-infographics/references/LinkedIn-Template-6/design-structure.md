# LinkedIn-Template-6 — Design Structure

Canonical spec extracted from the reference infographic in
`docs/SM-Posts-Templates/LinkedIn-Template-6/LinkedIn-Template-6.jpg`. Source had no baked-in
handle or branding to strip; NexusPoint logo is added top-right per the skill's standing identity rule.

## Global

- **Canvas:** 1080 x 1350 px, 4:5 portrait. The whole infographic is ONE image.
- **Format:** vertical funnel diagram. A single continuous funnel shape (stacked tapering cylinder
  bands, each stage narrower than the one above) runs down the center of the canvas. Each stage is
  flanked left and right by data callout panels. NOT a card grid, NOT a bento layout, NOT horizontal
  bands of equal width.
- **Template purpose:** N-stage funnel, pipeline, or journey breakdowns where each stage needs both
  "where this happens" data and "what to do" strategy attached. Best for: marketing funnels, sales
  pipelines, customer journey maps, hiring/onboarding funnels, product-led-growth funnels, any
  narrowing-stage process with metrics and tactics per stage.
- **Tone:** analytical, dense, reference-sheet quality. Reads like a strategist's whiteboard cleaned
  up for a slide, not a casual social graphic.
- **Frame:** the entire canvas is bordered by a thin solid black rule (~2px) on all four edges, giving
  the infographic a "printed sheet" feel.
- **Page background:** very light lavender-white (`#F6F5F9`), flat, throughout.

## Layout (top to bottom)

### Section 1 — Title block (~10% of canvas, top)

- **Main title:** large bold black sans, centered, wide letter-tracking (generous space between
  words), one line (wrap to two only if the title is long). e.g. "The Content Marketing Funnel".
- **Subtitle stamp:** a pale-grey rounded-rectangle pill with a thin black border, centered directly
  below the title, bold black text inside — a "freshness" or context stamp (e.g. "Updated for 2026").
- **Flow arrows:** three short thick downward chevron/arrow marks in deep teal-green (`#1F4B3F`),
  centered below the stamp, pointing down into the top of the funnel — signals "this is what flows in."
- **NexusPoint logo:** small, top-right corner of the title block, per standing identity rule.

### Section 2 — The funnel (repeats once per stage, 4-6 stages, ~85% of canvas)

The funnel is ONE continuous tapering shape running down the center of the canvas — each stage's
band is drawn as a shaded cylinder segment (a flat-color top ellipse cap for the 3D-cylinder
illusion, a solid-color body, tapering to match the top width of the stage below it) so the whole
stack reads as a single funnel silhouette, not separate disconnected shapes. Each stage gets its
own flat color (see palette) and is progressively narrower than the stage above.

**Inside each band, centered:**
- A small black rounded-square badge with a bold white stage number (not zero-padded).
- The stage name in bold black, same line as the badge.
- Below that, an italic black tagline (short, 3-6 words) stating the goal of that stage.

**Flanking each band, at the same vertical position:**
- **Left side (two stacked mini-panels):**
  - `ONLINE LOCATION:` panel — a bold-black label on a pale color-tinted highlight background
    (tint matches that stage's funnel color, very light), followed by exactly 3 bullet lines
    (black right-pointing triangle bullet + short black text) naming where this stage's activity
    happens (channels, platforms, content types).
  - `KPIS:` panel — same highlight-label style, a different pale tint, followed by exactly 3 bullet
    lines naming the metrics that matter at this stage.
- **Right side (one panel):**
  - `STRATEGY:` panel — bold-black label on a pale color-tinted highlight (matching that stage's
    color), followed by exactly 3 bullet lines (black right-pointing triangle bullet + short black
    text) naming concrete tactics for that stage.
- A thin dashed horizontal divider spans the full canvas width between one stage's row and the next.

## Palette

| Token | Hex | Use |
|---|---|---|
| Page background | `#F6F5F9` | flat background, whole canvas |
| Outer frame | `#1A1A1A` | thin border rule around the entire canvas |
| Title ink | `#1A1A1A` | title, stage names, bullet text, panel labels |
| Subtitle stamp bg | `#ECEBF0` | pill background behind the subtitle stamp |
| Subtitle stamp border | `#1A1A1A` | thin border on the stamp pill |
| Flow arrows | `#1F4B3F` | the three downward chevrons under the title |
| Stage 1 color (top, widest) | `#D6E24B` (top ellipse tint `#E4EC7C`) | funnel band 1 |
| Stage 2 color | `#F0B93E` (top ellipse tint `#F5CD6E`) | funnel band 2 |
| Stage 3 color | `#EF8B3D` (top ellipse tint `#F3A868`) | funnel band 3 |
| Stage 4 color | `#9A87DA` (top ellipse tint `#B3A5E4`) | funnel band 4 |
| Stage 5 color (bottom, narrowest) | `#EC6FA6` (top ellipse tint `#F191BE`) | funnel band 5 |
| Stage badge bg | `#1A1A1A` | number badge inside each band |
| Stage badge text | `#FFFFFF` | number inside the badge |
| Stage tagline | `#1A1A1A` | italic goal line inside each band |
| Panel highlight tint (per stage) | pale tint of that stage's color, ~25% opacity over page bg | `ONLINE LOCATION:` / `KPIS:` / `STRATEGY:` label backgrounds |
| Bullet arrow + text | `#1A1A1A` | all bullet lines in every panel |
| Divider | `#1A1A1A` at low opacity, dashed | horizontal rule between stage rows |

## Type stack

- **Title:** bold black sans, large, wide tracking, centered.
- **Subtitle stamp:** bold black sans, small-medium, centered inside the pill.
- **Stage name:** bold black sans, large, inline with the number badge.
- **Stage number:** bold white sans, medium, inside the black badge.
- **Stage tagline:** italic black sans, medium, centered.
- **Panel label (ONLINE LOCATION: / KPIS: / STRATEGY:):** bold black sans, small-medium, uppercase, on its own tinted highlight strip.
- **Bullet text:** regular black sans, small, tight leading.

## Structural rules

- 4-6 stages. Each stage must be visibly narrower than the one above it — the funnel silhouette is
  the whole point; bands must taper, never stay equal width.
- Every stage needs: a distinct flat color, a number badge, a name, an italic tagline, an
  `ONLINE LOCATION:` panel (3 bullets), a `KPIS:` panel (3 bullets), and a `STRATEGY:` panel (3 bullets).
- Left side always carries `ONLINE LOCATION:` + `KPIS:` stacked. Right side always carries `STRATEGY:`
  alone. Do not swap sides or merge panels.
- Panel highlight tints must visually key to their stage's funnel color (a pale/light version of it),
  so a reader can trace a stage's color from the funnel band out to its side panels at a glance.
- Bullets are always exactly 3 per panel, short phrases (not full sentences), each prefixed with a
  black right-pointing triangle bullet.
- Thin dashed dividers separate each stage's full row (band + both side panels) from the next.
- The outer black frame border must appear on every render — it is part of the template's identity.

## Identity

- **NexusPoint logo:** small, top-right of the title block. Attach
  `brand-assets/logos/nexuspoint-logo.png` as a Knowledge file in the Gem. Do not stretch or recolor it.
- No handle, no footer, no CTA bar in this template — it is a pure reference/data sheet.
