# Bold Variant — Editorial (Recommended default)

Magazine-grade. The website as printed object. Pulls from luxury fashion publications (W, AnOther, Wallpaper*), modernist art books, and high-end interview magazines.

## Aesthetic principles
- Confident pairing of a high-contrast display serif with a refined sans body
- Generous whitespace as a deliberate design element, not waste
- Asymmetric layouts — copy doesn't always start at the same left margin
- Pull-quotes, drop caps, oversized italic phrases used as visual punctuation
- Subtle paper texture or soft cream background instead of pure white (or rich black instead of pure black if dark)
- Photography treated as art, not stock — full-bleed plates, captioned, framed with extra padding rather than hard cropped

## Color palette (default light variant)
- `paper`: `#f5f1ea` (warm cream)
- `ink`: `#1a1a1a` (rich near-black)
- `muted`: `rgba(26,26,26,0.55)`
- `rule`: `rgba(26,26,26,0.15)` (thin hairline dividers)
- `accent`: `#8b1d24` (deep burgundy/oxblood — used in pull quotes and select hover states)

For dark editorial: `paper` becomes `#161310`, `ink` becomes `#f3ede2`, accent stays `#c9a36e` (champagne) or `#8b1d24` (burgundy).

## Typography
- **Display:** Playfair Display 400 italic or 800 regular, OR Instrument Serif (free Google Font that nails this aesthetic) — used for headlines AND pull quotes
- **Body:** Inter 300/400, or Manrope 300/400 — clean refined sans
- **Captions/credits:** Inter 500 italic at 11-12px, treated as photo credit footnotes

Big tracking-tight serif headlines (`tracking-[-2px]`), looser body (`leading-relaxed`).

## Layout language
- Two-column body text in the about/long-form sections (don't force this everywhere, just where prose lives)
- Pull quotes: oversized italic serif, set in the margin or breaking a column
- Hero: full-bleed image with title TYPESET OVER IT in serif, NOT below it. Treat the page like a magazine cover.
- Services/Process: alternating left/right offsets per item, like a magazine spread. Each item gets a small numbered roman numeral (I, II, III).
- Footer feels like an imprint colophon: tiny capped uppercase, single rule above

## Hover/interaction
- Subtle, slow (400-700ms ease)
- Links: underline animates from left on hover
- Image hover: slight grayscale → color, or vice versa
- No bouncing or scale-up

## Anti-patterns (do NOT do)
- Multiple colored accents
- Sharp shadow drops
- Square/blocky buttons
- Centered hero with single CTA pill
- Monospace anywhere
