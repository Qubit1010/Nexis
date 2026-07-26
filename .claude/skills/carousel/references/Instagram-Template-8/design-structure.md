# Instagram-Template-8 — Design Structure

Canonical spec extracted from the reference carousels in
`docs/SM-Posts-Templates/Instagram-Template-8/` (`Cover.png`, `Body (1).png` .. `Body (4).png`, `Last.png`).
Source-template identity ("Charlie Hills", "charliehills.ai", "charliehills.substack.com") is stripped
and replaced with `@{{HANDLE}}`. This file is the source of truth for `gem.md` and `input-prompt.md`.

## Global

- **Canvas:** 1080 x 1350 px, 4:5 aspect ratio. Every slide.
- **Slide order:** Cover (1) -> Body-Overview (2) -> Body-Step (3..N-1) -> CTA (N).
- **Generation protocol:** one slide per image, one at a time. Never tiled, never a deck. See `gem.md` OUTPUT FORMAT.
- **Template purpose:** step-by-step build/tutorial format. Cover states the build + the result. One overview slide lists the "ingredients" (files, tools, principles). Every following body slide is one numbered step, grouped into phases, each ending in a copy-paste prompt box. Ideal for "how I built X" walkthroughs, AI workflow tutorials, and process breakdowns.
- **Tone:** clean, editorial-technical, warm-neutral. Reads like a well-designed changelog or build log, not a hype post.
- **Background (every slide):** off-white paper (`#FDFCFA`) with a faint uniform square grid (`#ECE8E0`), very light, purely textural.
- **Identity:** an author identity chip (circular avatar + bold name + "." + handle/site) appears on Cover (below the subheadline), top-right of Body-Overview, and centered at the bottom of the CTA. Body-Step slides carry no identity chip, only the progress rail.

## Palette

| Token | Hex | Use |
|---|---|---|
| Page bg | `#FDFCFA` | base background, all slides |
| Grid lines | `#ECE8E0` | faint background square grid |
| Ink navy | `#12192B` | headlines, primary text |
| Grey text | `#6B7280` | secondary/description text |
| Terracotta accent | `#D97757` | kicker labels, highlighted headline word, decorative dots/icons |
| Card bg | `#FFFFFF` | white card fill (overview list cards, step cards) |
| Card border | `#E6E1D8` | thin warm-grey card stroke |
| Cream prompt bg | `#F7EFD3` | "paste this" prompt box fill |
| Prompt icon/button orange | `#E8744A` | sunburst icon + send-arrow circle inside prompt boxes |
| Badge blue | `#4A90D9` | step badge / file badge — phase 1 |
| Badge purple | `#A78BFA` | step badge / file badge — phase 2 |
| Badge orange | `#F0923B` | step badge / file badge — phase 3 |
| Badge green | `#5FBF7A` | step badge / file badge — phase 4+ / final |
| CTA pill fill | `#12192B` | CTA keyword pill background |
| CTA pill text | `#FFFFFF` | CTA keyword pill text |

## Type stack

- **Kicker / eyebrow labels:** small uppercase monospace, letter-spaced. Match: Space Mono, JetBrains Mono. Terracotta on cover pill, grey or terracotta elsewhere.
- **Headline (cover, body-overview, CTA):** heavy bold sans, ink navy. Match: Inter Black, General Sans Bold, Söhne Bold. One phrase per headline gets the terracotta accent color (or terracotta italic on CTA).
- **Subheadline / description:** same sans family, mixed weight — bold navy spans for emphasis, regular grey for connective text.
- **Identity name:** bold sans, small, navy. **Identity handle/site:** regular sans, small, grey. Same pill, separated by ".".
- **Overview card label (filename/category):** bold monospace inside a colored badge, white text. Match: JetBrains Mono Bold.
- **Overview card body:** same sans as headline, mixed bold navy + regular grey, one line.
- **Step badge number:** bold monospace, white, centered inside a small colored rounded-square.
- **Phase pill label:** small uppercase monospace, grey, on a light grey pill.
- **Step headline:** heavy bold sans, navy, 1-2 lines.
- **Step body paragraph:** regular sans grey with bold navy emphasis spans, 2-4 lines.
- **Prompt box label ("PASTE THIS...")**: small uppercase monospace, terracotta or grey.
- **Prompt box text:** regular sans, dark charcoal, with bold spans for emphasis, inside the cream box.
- **CTA keyword (inside pill):** bold uppercase sans, white, on the dark navy pill.

## Slide anatomy

### Cover (slide 1)
- **Background:** off-white grid paper. Decorative accents: a thin dashed vertical squiggly line threading down the right side with 3-4 small solid terracotta/red dots marking bends (a "journey path" motif); a faint diagonal grid-fold watermark shape in the top-right corner. Both purely decorative, low-contrast.
- **Top-left:** dashed-border pill badge, terracotta uppercase monospace text: "`<BUILD CONTEXT>` · `<SITE/HANDLE>`" (e.g. "BUILT IN ONE EVENING · CHARLIEHILLS.AI").
- **Headline:** giant heavy bold sans, ink navy, 3 lines, left-aligned, one word/phrase per headline in terracotta (e.g. "How to Build a Website with **Claude**").
- **Subheadline:** 2 lines below the headline, mixed bold navy (lead phrase) + regular grey (rest) — states the concrete payoff (e.g. "Three markdown files and nine steps that strip the AI look out completely.").
- **Identity chip:** rounded pill, white fill, thin border, left-aligned below the subheadline — circular avatar + bold name + "." + grey handle/site.
- **Bottom:** a browser-window screenshot mockup (rounded top corners, macOS-style traffic-light dots + URL bar) previewing the actual site/result being discussed, cropped off at the very bottom edge of the canvas so it bleeds beyond the frame.

### Body-Overview (slide 2)
- **Background:** off-white grid paper.
- **Top-left:** small uppercase monospace kicker, terracotta (the topic label, e.g. "WEBSITE BUILD").
- **Top-right:** identity chip (avatar + bold name + "." + grey handle/site), same pill style as cover.
- **Headline:** bold navy sans, 1-2 lines, one phrase in terracotta (e.g. "Three files run the **whole build**").
- **Description:** 1-2 lines below, mixed regular grey + bold navy emphasis.
- **Stacked list cards:** 3-5 vertically stacked full-width rounded white cards (thin `#E6E1D8` border, soft shadow), each:
  - Left: small colored rounded-rectangle badge with a folder icon + bold monospace label (a filename or item name), one distinct flat color per card (blue / purple / orange / green from the palette).
  - Right of badge, same row: bold navy lead phrase + regular grey continuation describing what that item covers.
  - A short dotted connector line with a small terracotta dot links consecutive cards vertically, implying sequence.

### Body-Step (slides 3..N-1, repeat one per step)
- **Left edge:** a vertical gradient progress rail (thin line) running the full height of the canvas, part of one continuous rail spanning every step slide in the carousel — color transitions from blue (`#4A90D9`) near the start, through purple (`#A78BFA`) and orange (`#F0923B`), to green (`#5FBF7A`) at the final step. Small hollow circles mark each step position along the rail; the circle for the current slide's step is filled/highlighted.
- **Top edge:** a thin sliver of the previous card or identity chip peeks in, cropped off at the very top of the canvas — implies continuous vertical scroll along the rail.
- **Main card:** one large rounded white card (thin border, soft shadow), containing:
  - **Top-left:** small colored rounded-square badge with the step number (bold white monospace on a flat fill — color matches the step's phase: blue/purple/orange/green).
  - **Top-right, same row:** small grey pill, uppercase monospace: "PHASE `<N>` · `<PHASE NAME>`" (e.g. "PHASE 1 · THE FILES").
  - **Headline:** bold navy sans, 1-2 lines, short instruction (e.g. "Write the facts file").
  - **Body paragraph:** regular grey sans with bold navy emphasis spans, 2-4 lines, explaining the step.
  - **Small label:** uppercase monospace, e.g. "PASTE THIS · `<TOOL>`" (the surface the prompt is pasted into, e.g. "CLAUDE CHAT").
  - **Prompt box:** rounded cream (`#F7EFD3`) box containing a small terracotta sunburst/asterisk icon top-left, the literal copy-paste prompt text (regular dark sans with bold emphasis spans) filling the box, and a small circular orange send-arrow button bottom-right (chat-input mockup).

### CTA (last slide)
- **Background:** off-white grid paper, clean and centered, no cards.
- **Center top:** terracotta sunburst/asterisk icon, larger than the prompt-box version, centered.
- **Headline:** heavy bold navy sans, 2-3 lines, centered, one word in terracotta italic (e.g. "free").
- **Description:** 1-2 lines below, regular grey, centered.
- **CTA line:** single centered line mixing: regular navy "Comment" + a dark navy rounded-rect pill with bold white uppercase keyword + regular navy "and I'll send it over."
- **Bottom:** identity chip (avatar + bold name + "." + grey handle/site), centered.

## Content rules

- Cover kicker: short build-context phrase + site/handle, max ~6 words.
- Cover headline: 3 lines max, one accented word/phrase.
- Cover subheadline: one concrete, specific payoff sentence, max ~20 words.
- Body-Overview: 3-5 list cards, each a distinct colored badge + one short descriptive line (max ~15 words).
- Body-Step headline: max ~6 words, imperative or descriptive.
- Body-Step body paragraph: max ~30 words, plain language, 1-2 bolded emphasis spans.
- Prompt box text: a literal, ready-to-paste instruction written in first person to the AI tool — specific, not generic.
- Phase names and colors are adaptable but must stay consistent across all step slides in one carousel (same phase = same color = same pill label).
- CTA keyword: one uppercase word. CTA payoff: concrete and specific ("I'll send it over", "I'll DM you the checklist").
- No emojis. No em dashes (use commas or periods).
