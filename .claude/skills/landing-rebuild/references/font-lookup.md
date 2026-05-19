# Font Lookup Table

When Framer's `--font-selector` decodes to a known family, map it to a real CDN URL. For Google Fonts, prefer `next/font/google` (better performance — Next handles subsetting and preload). For non-Google fonts, use a CSS `@import` in `globals.css`.

## Common Framer fonts

| Family | Source | next/font support? | Import method |
|---|---|---|---|
| Satoshi | Fontshare | No | `@import url('https://api.fontshare.com/v2/css?f[]=satoshi@300,400,500,600,700,900&display=swap');` |
| Cabinet Grotesk | Fontshare | No | `@import url('https://api.fontshare.com/v2/css?f[]=cabinet-grotesk@400,500,700,900&display=swap');` |
| General Sans | Fontshare | No | `@import url('https://api.fontshare.com/v2/css?f[]=general-sans@400,500,600,700&display=swap');` |
| Clash Display | Fontshare | No | `@import url('https://api.fontshare.com/v2/css?f[]=clash-display@400,500,600,700&display=swap');` |
| Boska | Fontshare | No | `@import url('https://api.fontshare.com/v2/css?f[]=boska@400,500,700,900&display=swap');` |
| Inter | Google Fonts | Yes | `import { Inter } from 'next/font/google'` |
| Manrope | Google Fonts | Yes | `import { Manrope } from 'next/font/google'` |
| Outfit | Google Fonts | Yes | `import { Outfit } from 'next/font/google'` |
| Plus Jakarta Sans | Google Fonts | Yes | `import { Plus_Jakarta_Sans } from 'next/font/google'` |
| Space Grotesk | Google Fonts | Yes | `import { Space_Grotesk } from 'next/font/google'` |
| Space Mono | Google Fonts | Yes | `import { Space_Mono } from 'next/font/google'` |
| Syne | Google Fonts | Yes | `import { Syne } from 'next/font/google'` |
| DM Sans | Google Fonts | Yes | `import { DM_Sans } from 'next/font/google'` |
| Playfair Display | Google Fonts | Yes | `import { Playfair_Display } from 'next/font/google'` |
| Instrument Serif | Google Fonts | Yes | `import { Instrument_Serif } from 'next/font/google'` |
| Cormorant Garamond | Google Fonts | Yes | `import { Cormorant_Garamond } from 'next/font/google'` |
| EB Garamond | Google Fonts | Yes | `import { EB_Garamond } from 'next/font/google'` |
| JetBrains Mono | Google Fonts | Yes | `import { JetBrains_Mono } from 'next/font/google'` |
| Geist | Google Fonts | Yes | `import { Geist, Geist_Mono } from 'next/font/google'` |

## When the font is unknown / custom

If `parse_design.py` decodes a `--font-selector` to something not in this table:

1. Search Google Fonts: `https://fonts.google.com/?query=<name>`
2. Search Fontshare: `https://www.fontshare.com/?q=<name>`
3. If neither has it, pick a close substitute from this table and document the swap in SPEC.md (e.g., "Source used 'Author', substituted with 'Manrope'").

Do NOT add fonts via `<link>` tags in `layout.tsx` — use `next/font` (preferred) or `@import` in `globals.css`. Loading via `<link>` defeats Next's font optimization.

## CSS `@import` placement

For Fontshare imports, the `@import` URL **must come BEFORE** `@import "tailwindcss"` in `globals.css`. Next 16's CSS optimizer will silently drop @imports that appear after other rules. See `nextjs-gotchas.md`.

Example correct order in `globals.css`:
```css
@import url('https://api.fontshare.com/v2/css?f[]=satoshi@300,600&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital@1&display=swap');
@import "tailwindcss";

:root {
  --font-satoshi: 'Satoshi', sans-serif;
  --font-serif: 'Playfair Display', serif;
}

body { font-family: var(--font-satoshi); }
```
