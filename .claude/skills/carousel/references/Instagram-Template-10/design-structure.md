# Instagram-Template-10 — Design Structure

Canonical spec extracted from the reference carousels in `docs/Instagram-Template-10/`
(cover `287198`, body `288198` / `289194` / `290198`, CTA `293195`).
Source-template identity ("@SEBASTIANHARDY_") is stripped and replaced with `@{{HANDLE}}`.
This file is the source of truth for `gem.md` and `input-prompt.md`.

## Global

- **Canvas:** 1080 x 1350 px, 4:5 aspect ratio. Every slide.
- **Slide order:** Cover (1) -> Body (2..N-1) -> CTA (N).
- **Generation protocol:** one slide per image, one at a time. Never tiled, never a deck. See `gem.md` OUTPUT FORMAT.
- **Template purpose:** GitHub repo / tool / plugin showcase. Each body slide presents one named item with a screenshot, "Why it matters" summary, two tag pills, and an italic serif punchline. Ideal for "top N" lists of repos, tools, plugins, or open-source projects.
- **Tone:** editorial-dark cover with a crisp editorial-light body. Authoritative but conversational. Reads like a curated developer newsletter.
- **Identity:** `@{{HANDLE}}` appears ONLY on the cover, bottom-left. Body slides and CTA have no handle.

## Two Visual Registers

| Register | Slides | Background | Tone |
|---|---|---|---|
| **Cinematic Dark** | Cover only | Deep navy (#080E1C) | 3D mascot, multicolor headline |
| **Editorial Light** | Body + CTA | Warm cream (#F5F0E8) with dot grid | Structured editorial layout |

## Palette

| Token | Hex | Use |
|---|---|---|
| Cover bg | `#080E1C` | deep navy, near-black |
| Cover pink | `#FF4D8C` | cover headline accent 1 (e.g. kicker word "Top 5") |
| Cover amber | `#FFA031` | cover headline accent 2 (e.g. topic word "Claude Code") |
| Cover white | `#FFFFFF` | cover headline body + bottom bar text |
| Body bg | `#F5F0E8` | warm cream/parchment |
| Body dot grid | `#E8E3DB` | very subtle square dot grid overlaid on body bg |
| Body orange | `#E85D2F` | bookmark icon, page counter, kicker label |
| Body text | `#1A1A1A` | headline, body text |
| Body ghost | `#EDE8E0` | giant decorative ghost number (barely visible, top-right) |
| Body pill border | `#1A1A1A` | tag pill stroke |
| Body pill fill | `#FFFFFF` | tag pill background |
| CTA black | `#1A1A1A` | "COMMENT" and surrounding text |
| CTA orange | `#E85D2F` | italic action lines ("KEYWORD", "FOR THE PAYOFF.") |

## Type Stack

- **Cover headline:** very heavy expanded bold sans, all the same family. Match: Bebas Neue, Montserrat Black, Suisse Int'l Black. Multicolor words within same line.
- **Body headline:** ultra-heavy black sans, large, left-aligned, 2-3 lines. Same family as cover.
- **Body kicker:** "[ITEM TYPE] [NN]" — orange, semi-bold sans. "[ITEM NAME]" — dark, regular sans. Same row.
- **Body URL line:** small uppercase monospace, dark, letter-spaced (e.g. Space Mono).
- **Body text:** clean regular-weight sans, dark.
- **Body tag pills:** clean medium sans, small, dark.
- **Body italic quote:** italic serif, thin/elegant, contrasting with the heavy headline (e.g. Georgia italic or Playfair Display italic).
- **CTA action:** ultra-heavy all-caps bold sans — "COMMENT" in near-black, keyword + payoff lines in orange italic all-caps.
- **CTA body:** heavy bold sans, dark, centered.
- **Page counter + bottom bars:** small uppercase monospace, muted/dark.

## Slide Anatomy

### Cover (slide 1)

- **Background:** deep navy (#080E1C), no gradient needed — flat dark.
- **Center:** large 3D character illustration, centered/slightly upper center, filling ~50-60% of canvas height. The character is a fluffy/plush mascot adapted to the post topic, with warm studio lighting (warm orange glow from below), subtle sparkle particles.
- **Top-right:** page counter "01 / NN ->" in small white monospace.
- **Bottom:** two-line heavy sans headline, left-aligned or centered, spanning bottom ~25% of canvas:
  - Line 1: mixed-color words — pink accent for the kicker/number word, amber accent for the main topic word(s), white for the rest.
  - Line 2: full white.
- **Bottom-left:** "@{{HANDLE}}" in small white uppercase monospace.
- **Bottom-right:** "SAVE FOR LATER" in small white uppercase monospace.

### Body (slides 2..N-1)

- **Background:** warm cream (#F5F0E8) with a subtle square dot-grid texture across the full canvas.
- **Top-left:** solid orange bookmark/ribbon icon (~32x40px, bookmark shape with notch at bottom).
- **Top-right:** "NN / TOTAL" in orange monospace (same orange #E85D2F).
- **Decorative ghost number:** giant item number (01, 02, 03...) in very muted cream (#EDE8E0), positioned top-right background behind the counter, ~30-35% canvas height. Barely visible — purely decorative.
- **Kicker line:** "[ITEM TYPE] [NN]" in orange semi-bold sans + "  [ITEM NAME]" in dark regular sans, on one line. Example: "PLUGIN 01  CAVEMAN".
- **Headline:** very heavy black sans, 2-3 lines, large, left-aligned. A punchy single sentence. Ends with punctuation (exclamation or period).
- **URL line:** "GITHUB.COM/USER/REPO  ·  ★ [STARS]" or equivalent URL, in small uppercase monospace, dark. (or "TOOL.COM" if not a GitHub repo)
- **Screenshot:** full-width or near-full-width rectangular image of the GitHub repo page (or tool homepage), subtle rounded corners (~4px), very light shadow. No decorative frame — clean flat embed.
- **Body text:** "Why it matters: [one sentence]." in regular dark sans, left-aligned.
- **Tag pills:** 2 rounded-rectangle pill tags side by side, white fill (#FFFFFF), thin dark stroke (#1A1A1A), dark text, small font. Represent the use case or audience.
- **Italic serif quote:** 1 short italic serif line at bottom, left-aligned, lighter weight. A pithy re-statement of the headline in a different voice.
- **No footer / no handle** on body slides.

### CTA (slide N)

- **Background:** same cream (#F5F0E8) with dot grid.
- **Top-left:** orange bookmark icon (same as body slides).
- **Top-right:** "NN / NN" in orange monospace (final count).
- **Center (upper half):** massive stacked all-caps text, centered:
  - "COMMENT" — ultra-heavy black sans, very large.
  - `"[KEYWORD]"` — ultra-heavy orange italic all-caps sans, same size or slightly larger. The keyword users comment.
  - "FOR THE [PAYOFF]." — ultra-heavy orange italic all-caps sans, large, 1-2 lines.
- **Center (lower half):** bold dark sans body text, centered, 1-2 lines: what they'll receive when they comment.
- **Bottom-right:** "SWIPE ->" in small dark monospace.
- **No handle, no bottom-left text** on CTA.

## Content Rules

- Cover headline: 2 lines. Line 1 should include the colored accent words (kicker + topic). Line 2 = white completion.
- Body kicker item type: adaptable — "PLUGIN", "REPO", "TOOL", "SKILL", "RESOURCE", etc.
- Body headline: 1 punchy declarative sentence, max 10 words, ends with ! or .
- Body URL: use real or plausible GitHub/tool URL with star count if available.
- Body "Why it matters": one crisp sentence, plain English, no jargon.
- Tag pills: 2 words or short phrases describing the audience or use case.
- Italic serif quote: 1 short pithy line. Can be a paraphrase, a punchy version, or a quip.
- CTA keyword: one uppercase word (the thing people comment).
- CTA payoff: what they'll receive — short, specific, valuable.
- No emojis. No em dashes (use commas or periods).
