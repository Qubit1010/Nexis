# Bold Variant — Luxury Dark

After-hours, high-end. Think Aesop, Off-White press kits, Tesla product pages at night, $$$$ Michelin restaurant sites. Rich blacks, gold restraint, slow choreography.

## Aesthetic principles
- Deep, slightly-warm black background (NOT pure `#000`)
- Champagne/gold accent used sparingly as the only chromatic note
- Wide-tracked uppercase for everything chrome-related (nav, labels, CTAs)
- Slow, deliberate motion — fades and reveals over 600-900ms
- Photography is dark, moody, high-contrast — not bright stock
- Generous breathing room. Components feel "lit" by spotlight against the dark surface

## Color palette
- `paper` (bg): `#0c0c0d` (rich warm black)
- `surface`: `#161617` (one step up from bg, used for cards)
- `ink`: `#f3ede2` (warm off-white)
- `muted`: `rgba(243,237,226,0.55)`
- `rule`: `rgba(243,237,226,0.12)`
- `accent`: `#c9a36e` (champagne gold) — links, hover states, key emphasis only

## Typography
- **Display:** Cormorant Garamond 300 (Google Font) OR Tenor Sans — thin elegant serif, large
- **Body:** Inter 300 OR Manrope 300 — light weight, lots of leading
- **Labels:** Inter 500 UPPERCASE 11px tracking `[0.25em]`

Headlines lean into airiness — `font-weight: 300`, `letter-spacing: -1px`, sizes up to 6xl/7xl.

## Layout language
- Hero: centered or slightly-left, oversized thin serif headline floating in dark space. Image (if any) sits behind with a subtle radial vignette
- Sections separated by generous vertical padding (24-32 of leading-relaxed)
- Services: cards on `surface` with a 1px gold border on hover, slight elevation
- Work: full-bleed images with hover reveal — image stays muted until hovered, then fades to color
- Testimonials: pull-quote style, oversized italic serif against dark, attribution in champagne small caps
- Footer: minimal, gold rule above, tiny tracked caps

## Hover/interaction
- Slow opacity/scale (600-800ms)
- Images: from `grayscale(0.6) brightness(0.7)` to full color on hover
- Buttons: 1px gold border, fills with gold + dark text on hover, ease 500ms
- Cursor-following spotlights are okay (subtle, low-opacity radial behind cursor)

## Anti-patterns (do NOT do)
- Bright/saturated colors anywhere
- Pure `#000` background (feels cheap)
- Sans-serif headlines
- Sharp, fast micro-interactions
- Rounded buttons with thick borders
- More than one accent color
