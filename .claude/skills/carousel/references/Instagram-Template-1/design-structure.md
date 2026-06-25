# Instagram-Template-1 — Design Structure

Canonical spec extracted from the 4 reference carousels in `docs/Instagram-Template-1/`
(cover `450010`, body `451022` + `455001`, end/CTA `456001`). Source-template identity
("CHASE AI" / "@chase.ai") is stripped and replaced with `ALEEM · NEXUSPOINT` / `@{{HANDLE}}`.
This file is the source of truth for `gem.md` and `input-prompt.md`.

## Global

- **Canvas:** 1080 x 1350 px, 4:5 aspect ratio. Every slide.
- **Slide order:** Cover (1) -> Body (2..N-1) -> End/CTA (N).
- **Generation protocol:** one slide per image, generated one at a time (cover first, then one per "next"). Never a slide deck and never a tiled grid of all slides in one image. See `gem.md` OUTPUT FORMAT.
- **Tone:** modern, editorial, high contrast, premium. Reads in under 2 seconds per slide.
- **Identity swap:** header brand text is always `ALEEM · NEXUSPOINT`; CTA handle is `@{{HANDLE}}`.
  Never the words "Chase" / "chase.ai" or any source-template name.

## Palette (keep exactly, do not brand-override)

| Token | Hex | Use |
|---|---|---|
| Cover blue (top) | `#1E6FD9` | cover background gradient top |
| Cover blue (bottom) | `#114E9E` | cover background gradient bottom |
| Terracotta base | `#A85842` | body + end background |
| Terracotta shade | `#8E4634` | background vignette / lower edge |
| Cream | `#F0E6DC` | headline highlight words, body text, pill text on dark |
| Ink | `#1A1410` | headline contrast words, pill fill, stacked CTA words |
| Statue marble | `#E9E4DC` | cover hero subject |
| Accent object | `#C0593C` | cover 3D symbolic object (terracotta burst) |

## Type stack

- **Cover headline:** condensed heavy sans, all-caps-feel, tight leading, soft drop shadow. White.
  (Match: a condensed heavy grotesque.)
- **Cover subtitle:** italic serif, small relative to headline. White.
- **Body / End headline:** heavy rounded geometric sans, 2-3 lines, ends in a period. Words alternate
  cream and ink for emphasis. (Match: a bold rounded grotesque like Clash Display / Gilroy Heavy.)
- **Body paragraph:** clean neutral grotesque, cream, key phrases set bold. (Match: Inter / Helvetica Neue.)
- **Metadata header + footer + pill label:** monospace, letter-spaced, uppercase.
  (Match: Space Mono / JetBrains Mono.)

## Slide anatomy

### Cover (slide 1)
- **Background:** saturated blue vertical gradient (`#1E6FD9` -> `#114E9E`).
- **Hero:** one photoreal subject (sculpture, object, or figure) that fits the post topic, holding or
  presenting a **3D symbolic object** representing the topic (the reference uses a marble Roman statue
  holding a terracotta multi-spoke burst). Subject bleeds off the top/right edge.
- **Kicker:** small uppercase line near center-left (e.g. `TOP 5`, `THE`, `5 WAYS`). Optional.
- **Headline:** giant condensed heavy white sans, 2 lines, tight leading, soft shadow. The hook, max 8 words.
- **Subtitle:** italic serif word/phrase under the headline (e.g. `Plugins`).
- **No** metadata header, no footer, no provider name on the cover.

### Body (slides 2 .. N-1)
- **Background:** terracotta paper texture (`#A85842`) with subtle grain + vignette.
- **Metadata header** (top, monospace, letter-spaced): `JUN ©2026 · ALEEM · NEXUSPOINT · 02 / 07`
  (month + year follow the post date; right token is current page / total).
- **Ticket pill:** black rounded bar with notched ends, white uppercase label, e.g. `POINT 01 / TOPIC`
  (source template used `PLUGIN 01 / GRAPHIFY`; relabel to the post's taxonomy).
- **Headline:** heavy rounded sans, 2-3 lines, mixing cream + ink words, ends in a period. Max ~8 words.
- **Paragraph:** cream body text, key phrases bold. Max ~15 words of substance, skimmable.
- **Taped visual:** a polaroid-style framed image (white border, two short strips of "tape" at corners,
  slight rotation) holding the supporting screenshot / diagram / infographic. Omit if no visual fits;
  then let the headline + paragraph breathe.
- **Footer:** monospace page number left (`02 / 07`), `SWIPE →` right.

### End / CTA (slide N)
- **Background + metadata header + footer:** same as body, page token = `NN / NN` (last).
- **Pill:** black ticket pill with a forward-looking label (e.g. `BUILD YOUR NEXT PROJECT`, `START HERE`).
- **Statement:** huge stacked one-word-per-line phrase, alternating cream/ink, each word ends in a period
  (reference: `save.` / `share.` / `follow.`). Value-native, not a bare "follow me".
- **Summary line + handle:** one or two lines summarizing the value, ending with `Follow @{{HANDLE}} for more.`
- Same footer as body.

## Content rules (inherited from SKILL.md)

- Cover hook: max 8 words. Body headline: max ~8 words. Body paragraph: max ~15 words.
- CTA is value-native (save / share / comment-to-DM), never a bare "follow me".
- No emojis. No em dashes (use commas or periods).
- Keep palette + layout identical across the set so it reads as one carousel.
