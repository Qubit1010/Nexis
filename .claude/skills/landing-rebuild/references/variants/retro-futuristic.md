# Bold Variant — Retro-Futuristic

80s/90s computing nostalgia filtered through modern web craft. Think Vercel ship promos, Linear's changelog, Teenage Engineering, Y2K terminal aesthetics, synthwave-but-tasteful. NOT "vaporwave neon mall" — restrained, premium retro.

## Aesthetic principles
- Dark navy/aubergine background with CRT-feel scanline overlay (very subtle, 4% opacity)
- One or two neon accents — magenta + cyan, or amber + green — used as glow, never flat fill
- Monospace dominant for ALL chrome (nav, labels, CTAs, captions)
- Pixel-perfect 1px borders with subtle glow (box-shadow w/ accent color, low opacity)
- ASCII-style decoration (`[ • ]`, `> >`, `——`) as section dividers
- Subtle screen flicker / chromatic aberration on hover

## Color palette
- `paper` (bg): `#0a0712` (deep aubergine-black)
- `surface`: `#16101f`
- `ink`: `#e8e6f0` (cool off-white)
- `muted`: `rgba(232,230,240,0.5)`
- `rule`: `rgba(232,230,240,0.1)`
- `accent-1`: `#ff2e88` (hot magenta)
- `accent-2`: `#3df1ff` (electric cyan)

Use the two accents complementarily — magenta for primary CTAs/highlights, cyan for secondary (links, hover underlines).

## Typography
- **Display:** JetBrains Mono 700 OR Departure Mono — monospaced bold UPPERCASE for headlines
- **Body:** IBM Plex Sans 400 OR Inter 400 — clean readable sans (gives the eye a break from mono)
- **Labels/code:** JetBrains Mono 400 — terminal feel

Headlines are tracking-tight (`-1px`), labels are tracking-wide UPPERCASE.

## Layout language
- Hero: terminal-style — small `[user@nexus ~]$ ./run` prompt at top, big mono headline, blinking cursor at end
- Section labels: `> 01. SERVICES` mono-prefixed, all-caps
- Services/Work cards: 1px border with magenta glow on hover (`box-shadow: 0 0 24px rgba(255,46,136,0.35)`)
- Process: numbered list with `[01]`, `[02]` mono prefixes, dashed-line connectors between items
- Testimonials: framed like terminal output — `> "quote here"` then `-- name, role` underneath
- Footer: ASCII-style horizontal rule, mono colophon

## Hover/interaction
- Glow intensifies on hover (box-shadow grows + accent border)
- Brief chromatic aberration on image hover (RGB split 2px, then snap back)
- Links: cyan underline + slight glow
- Buttons: 1px magenta border, hover fills with magenta on a black inset (`text` swaps to black)
- Cursor blink animation on focused inputs

## Anti-patterns (do NOT do)
- Vaporwave purple/pink gradients (cheesy)
- Synthwave sun + grid hero backdrops (overdone)
- Comic Sans, Press Start 2P, or other "obvious retro gaming" fonts — go mono instead
- Multiple competing neon colors — stick to magenta + cyan
- Skeuomorphic CRT bezels around the entire site
- Heavy noise/grain (subtle only — under 5% opacity)
