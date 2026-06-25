# Instagram-Template-2 — Design Structure

Canonical spec extracted from the reference carousels in `docs/Instagram-Template-2/`
(cover `583230`, body `584231` / `585230` / `586227` / `587230` / `588226`, CTA `589283`).
Source-template identity ("@itsdesignare") is stripped and replaced with `@{{HANDLE}}`.
This file is the source of truth for `gem.md` and `input-prompt.md`.

## Global

- **Canvas:** 1080 x 1350 px, 4:5 aspect ratio. Every slide.
- **Slide order:** Cover (1) -> Body (2..N-1) -> CTA (N).
- **Generation protocol:** one slide per image, generated one at a time. Never tiled, never a deck. See `gem.md` OUTPUT FORMAT.
- **Two visual registers:**
  - **Cinematic Dark** (cover + CTA): full-bleed photo, deep red/maroon color grade, heavy film grain.
  - **Editorial Light** (body): warm cream background with fine dot grid, clean typographic layout.
- **Tone:** editorial, cinematic, high-contrast. Dark bookends, clean interior. Stops the scroll.
- **Identity:** `@{{HANDLE}}` centered near the very top of cover and CTA slides only. Body slides carry no branding strip or header.

## Palette

| Token | Hex | Use |
|---|---|---|
| Cream bg | `#F2EDE3` | body background |
| Dot grid | `#E0D9CE` | body dot texture |
| Near-black | `#0D0D0D` | body headlines + paragraph text |
| White | `#FFFFFF` | cover/CTA headlines, pill text |
| Teal accent | `#B8DDE0` | CTA action word + quoted keyword tint |
| Pill fill | `#FFFFFF` | cover bottom pill |
| Pill text | `#0D0D0D` | cover pill label |
| Cinematic shadows | `#1A0808` | cover/CTA photo color grade base |

## Type stack

- **Cover main lines:** extra-condensed heavy sans, all-caps, white, massive (each line ~85% slide width). Match: Bebas Neue, Impact, or any ultra-condensed heavy grotesque.
- **Cover sub-line:** flowing italic script or calligraphic serif, large, white. Match: Playfair Display Italic, or a high-contrast calligraphic script.
- **Body headline — bold part:** heavy bold extended sans, black, large, left-aligned. Match: Anton, or a bold condensed grotesque.
- **Body headline — italic accent:** elegant italic serif mixed into the same headline, same scale. Match: Playfair Display Italic. Typically the key term or punchline word.
- **Body paragraph:** clean regular sans, black. Match: Inter, Helvetica Neue.
- **Handwritten annotation:** rough uppercase marker/handwritten font, black. Appears near the visual.
- **CTA pre-line + outro:** small, regular-weight, centered, white.
- **CTA action word:** same extra-condensed heavy sans as cover, giant, white with light teal tint.
- **CTA quoted keyword:** large italic serif in quotation marks, same teal tint.
- **Handle:** small, regular-weight, centered at top, white (cover + CTA only).

## Slide anatomy

### Cover (slide 1)
- **Background:** full-bleed cinematic photo, deep red/maroon dominant color grade, heavy film grain overlay. Subject should fit the post topic (person, crowd, environment, symbolic object).
- **Handle:** `@{{HANDLE}}` — small, white, centered ~60-80px from the top edge.
- **Pre-line (optional):** small italic intro phrase centered above the main headline ("How To", "The", "Why", etc.).
- **Giant headline:** 2-3 lines of extra-condensed heavy sans, white, each line filling ~85% of the slide width. The hook. Tight leading.
- **Italic script sub-line:** one phrase in flowing calligraphic/italic serif, white, below the main headline block (e.g. "For Brands", "For Founders", "In 5 Steps").
- **Bottom pill:** white rounded rectangle, black uppercase text + arrow (e.g. "OUR WORKFLOW ->"), centered near the bottom.
- No metadata header, no footer, no slide number.

### Body (slides 2..N-1)
- **Background:** warm cream (#F2EDE3) with a fine uniform dot-grid pattern throughout.
- **No header, no handle, no footer, no branding on body slides.**
- **Layout:** upper ~50% is the text zone (headline + body paragraph); lower ~50% is the visual zone.
- **Headline (top-left):** 2-3 lines, mixing heavy bold sans for the main words and elegant italic serif for one key word or phrase. Black. E.g.: `Create your` / `design in` / `*Figma*`. The italic word is usually a tool name, technique, or concept.
- **Body paragraph:** regular clean sans, black, left-aligned, 2-4 lines, max ~20 words. One concrete step, instruction, or insight per slide.
- **Hand-drawn arrow:** black organic curved arrow pointing from the text zone down to the visual. Adds energy and movement.
- **Handwritten label (optional):** rough uppercase handwritten/marker text near the visual (e.g. "ACCEPT OR MAKE CHANGES"). Omit if not needed.
- **Visual (lower half):** app screenshot, UI mockup, or diagram floating with a soft drop shadow. Either single full-width or two-up side by side. Shows the actual tool, output, or concept.
- No pill, no page number, no ticket badge.

### CTA / Close (slide N)
- **Background:** full-bleed cinematic photo — a different scene from the cover (crowd overhead, abstract environment, texture). Same deep-red color grade + film grain.
- **Handle:** `@{{HANDLE}}` — small, white, centered near the top.
- **Pre-lines:** 1-2 small centered lines, white, conversational teaser (e.g. "want to know / how do we scale it?").
- **Action word:** giant extra-condensed heavy sans, centered, white with light teal tint. This is the comment trigger instruction (e.g. "COMMENT").
- **Quoted keyword:** large italic serif in quotation marks, teal tint, centered below the action word (e.g. `"SCALE"`). This is the word the user comments.
- **Outro:** 1-2 small centered lines, white, italic or regular — the payoff line ("to learn how to... / follow @{{HANDLE}} for more").
- No pill. No page number. Pure conversion.

## Content rules

- Cover: max ~10 words across all headline lines. Sub-line adds flavor, not information.
- Body headline: max ~8 words total. Body paragraph: max ~20 words. One idea per slide.
- CTA comment trigger: one action word + one quoted keyword. Outro: one-line payoff.
- No emojis. No em dashes (use commas or periods).
- Cover and CTA photographic subjects should be thematically linked but visually distinct scenes.
- Body slides are always cream. Never mix cinematic and cream on the same slide.
