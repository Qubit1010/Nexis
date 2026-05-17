# Bold Variant — Brutalist

Raw, sharp, no apologies. Function-first. Treats design as information density and structural honesty rather than polish. Inspired by Wim Crouwel's grid systems and early-web bareness, modernized.

## Aesthetic principles
- Sharp edges only — `border-radius: 0` everywhere except where geometry demands it
- Heavy use of black/white contrast with ONE vivid accent (acid green, hot magenta, electric blue — pick one and use it sparingly)
- Visible grid: thin (1px) borders dividing sections and cards
- Oversized numbered labels (`01`, `02`) treated as decorative structural elements
- Monospace font for labels/captions to signal "system / data / engineered"
- Minimal motion: no fluffy spring animations. Either sharp scale on hover or nothing.

## Color palette
- `ink`: `#000000`
- `paper`: `#ffffff`
- `accent`: `#adff00` (acid green) — used at <10% of total surface area
- `muted`: `rgba(255,255,255,0.45)`
- `border`: `rgba(255,255,255,0.12)`

## Typography
- **Display:** Syne (Google Fonts, weight 800) — geometric, unmistakable, ALL CAPS for headlines
- **Body:** Syne 400 (or Space Grotesk 400)
- **Labels/captions:** Space Mono 400/700 — monospaced, treated as code

Tighter tracking on headlines (`tracking-[-2px]`), loose tracking on uppercase labels (`tracking-[3px]`).

## Layout language
- Section headers: small monospaced overline + 1px hairline rule across the full width
- Cards/items: separated by 1px dividers, NOT spacing. Tight grid.
- Hero: oversized headline that breaks the column grid. Portrait as a hard-cropped rectangle with a sharp accent bar.
- Process: horizontal 5-column grid of equal cells, NOT an accordion. Each cell self-contained.
- Testimonials: 1px grid of cards, monospaced metadata on each.
- Background grid lines as a faint overlay (8% opacity) suggesting graph paper

## Hover/interaction
- Hover: invert (white on color accent, or accent slides up from bottom)
- Buttons: rectangular, 1px border, hover fills with accent
- No drop shadows. Depth comes from contrast.

## Anti-patterns (do NOT do)
- Soft shadows
- Rounded corners
- Gradient backgrounds  
- Sans-serif italic
- Centered hero with pill button
