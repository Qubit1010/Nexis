# Bold Variant — Swiss Minimal

Information design discipline. The International Typographic Style — Müller-Brockmann, Hofmann, Helvetica-era Vignelli. Every element earns its place. Whitespace is structural, not decorative.

## Aesthetic principles
- Strict modular grid (12-col on desktop, snapped) visible as a faint guide in some sections
- Almost no color — black, white, one neutral gray. Optionally one bold flat accent (red `#e3262f` or signal yellow `#ffd400`) used at <5% surface
- Geometric sans-serif throughout — no serif anywhere
- Left-aligned, ranged-left text. Symmetry is rare; rational asymmetry rules
- Heavy use of small UPPERCASE labels with wide tracking as section markers
- Numbers and metadata treated as design — large numerals, tabular figures

## Color palette
- `paper`: `#ffffff` (pure)
- `ink`: `#0a0a0a` (near-black)
- `muted`: `#6b6b6b` (neutral gray)
- `rule`: `#e5e5e5` (hairline)
- `accent`: `#e3262f` (signal red) OR `#ffd400` (signal yellow) — pick one, use sparingly

## Typography
- **Display:** Inter Tight 600/700 OR Neue Haas Grotesk OR Helvetica Neue — tightly tracked, near-uppercase or sentence
- **Body:** Inter 400, 16-17px, tight `leading-snug`
- **Labels:** Inter 600 UPPERCASE 11px, tracking `[0.2em]`

No italics. No serifs. No display weights above 700.

## Layout language
- Hero: large headline ranged-left, set against generous top whitespace. Small metadata block (date, location, "01 / 06") in the top corner.
- Sections: a strong horizontal rule + small uppercase label introduces every section
- Services/Work: tabular grid with clear column headers, like an index. Numbered rows.
- Process: numbered ordered list, monospaced numerals (`01`, `02`...) ranged-left, body text in a strict 6-col offset
- Footer: 4-column index of sitemap + colophon, all small caps, separated by 1px rules

## Hover/interaction
- Minimal. Underline, color swap, or 1px to accent-thick border
- 150-200ms ease — fast, surgical
- No motion outside of `prefers-reduced-motion: no-preference`

## Anti-patterns (do NOT do)
- Drop shadows
- Gradients
- Rounded corners > 4px
- Multiple accent colors
- Decorative illustrations or icons that aren't pictograms
- Centered everything
