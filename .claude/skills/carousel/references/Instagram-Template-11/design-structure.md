# Instagram-Template-11 — Design Structure

Canonical spec extracted from the 10-slide reference carousel in
`docs/SM-Posts-Templates/Instagram-Template-11/` (files `1782407385174` cover through `1782407394168` CTA).
Source-template identity ("@fullstackparody", "Hermes Agent", "JUNE 2026") is stripped and replaced
with `@{{HANDLE}}` / the post's own topic / the current month-year. This file is the source of truth
for `gem.md` and `input-prompt.md`.

## Global

- **Canvas:** 1080 x 1350 px, 4:5 aspect ratio. Every slide.
- **Slide order:** Cover (1) -> Body-Overview (2) -> Body-Step (3..N-2, one per step, mixed visual variants) -> Body-Tips (N-1) -> CTA (N). Body-Why (a checklist/comparison slide) can replace or sit alongside Body-Tips if the content calls for "why this over alternatives" instead of "pro tips" — pick whichever fits, or use both if there are enough slides.
- **Generation protocol:** one slide per image, one at a time. Never tiled, never a deck. See `gem.md` OUTPUT FORMAT.
- **Template purpose:** vintage-print / zine-style product tutorial. A magazine masthead runs top and bottom of every slide (except CTA has no bottom bar). Ideal for tool setup guides, CLI/product walkthroughs, "how X works" breakdowns with a install-and-configure arc, and dev-tool or AI-product tutorials.
- **Tone:** vintage editorial print, warm and tactile (kraft paper, masking tape, hand-drawn red annotations) crossed with technical precision (real terminal output, real command syntax). Playful but credible.
- **Background (every slide):** warm kraft-paper tan (`#DFC9A4`) with visible paper-fiber grain/noise texture, uniform across all slides.
- **Masthead (top, every slide):** thin black rule below a text row: `[MONTH YEAR]` (left, small bold uppercase) — `@{{HANDLE}}` (center, small bold) — `NN/TOTAL` (right, small bold uppercase).
- **Footer (bottom, every slide except CTA):** thin black rule above a text row: `NN/TOTAL` (left, small bold uppercase) — `SWIPE ->` (right, small bold uppercase). The CTA (last slide) has no footer bar.
- **Recurring motifs:** masking-tape strips (semi-transparent warm grey/beige with faint woven texture) pinning terminal mockups, icon cards, and CTA corners at slight rotations; hand-drawn rust-red arrows, circles, underlines, and small "spark" hash marks annotating specific UI details; a giant faded outline numeral (matching the current step) bleeding off the right edge behind body-step headlines.

## Palette

| Token | Hex | Use |
|---|---|---|
| Kraft paper bg | `#DFC9A4` | base background, all slides |
| Ink black | `#1A1512` | headlines, body text, masthead/footer text |
| Rust accent | `#C8542E` | accent headline word/phrase, hand-drawn annotations, numbered badges, icons |
| Ghost accent | `#E3B79A` | giant faded step numeral, faded CTA logo watermark |
| Grey text | `#5C5348` | secondary/description text |
| Card cream | `#F2E9DC` | icon cards, list cards, terminal-adjacent info cards |
| Card border | `#C9B896` | thin card stroke where visible |
| Terminal bg | `#161616` | terminal window fill |
| Terminal green | `#4AE24A` | terminal command/output text |
| Terminal white | `#E8E8E8` | terminal secondary output text |
| Terminal grey | `#8A8A8A` | terminal muted metadata line |
| Black badge fill | `#1A1512` | stamped category/step badges |
| Black badge text | `#F2E9DC` | badge label text |
| Tape | `#C9BFA8` at ~70% opacity | masking-tape strips |

## Type stack

- **Masthead/footer text:** small bold uppercase sans or monospace, ink black, tight letter-spacing.
- **Badge label (TUTORIAL, STEP NN, OVERVIEW, TIPS, WHY):** bold uppercase monospace, cream text on a black stamped rounded-rect badge, slightly rough/inked edge.
- **Headline (all major slides):** huge heavy bold grotesque sans, ink black, tight leading. Match: Archivo Black, Anton, Founders Grotesk Bold. One word or phrase per headline recolored rust `#C8542E`.
- **Cover product-name accent line:** heavy bold serif italic display, rust colored. Match: Playfair Display Black Italic, Canela Bold Italic — distinct from the sans headline, used only for the cover's product-name line.
- **Body/description text:** clean regular sans, ink black or grey, mixed with bold spans for emphasis and inline monospace chips for literal commands.
- **Inline command chip:** monospace, set on a small black or cream rounded-rect background, e.g. `hermes gateway setup`.
- **Terminal text:** monospace (JetBrains Mono, Fira Code) — green for commands/success lines, white for output, grey for muted metadata.
- **Hand-drawn captions/annotations:** casual handwritten/script font, rust colored. Match: Caveat, Kalam, Gochi Hand.
- **Numbered badge (Tips slide):** bold sans/monospace, white, centered in a filled rust circle.
- **Icon-card label:** bold sans, ink black, centered below each icon.

## Slide anatomy

### Cover (slide 1)
- Masthead: `[MONTH YEAR]` / `@{{HANDLE}}` / `01/[TOTAL]`.
- Black stamped badge, top-center-left: `TUTORIAL` (or adaptable: "GUIDE", "WALKTHROUGH").
- Headline: 2 lines heavy bold black sans (the product/topic name split across lines), then one line in heavy serif italic rust (a continuation word, e.g. product category or tagline word).
- Subheadline: one line, bold black, states what the carousel delivers (e.g. "The Complete Setup Guide").
- Small hand-drawn rust arrow curving down from the subheadline toward the terminal mockup.
- **Terminal mockup:** dark rounded window (`#161616`), two masking-tape strips pinning its top corners at slight angles, title bar showing the tool name, macOS-style traffic-light dots (red/amber/green). Inside: a dashed multicolor wireframe line-art icon/logo (rust/amber/purple/blue dashed strokes) on the left, an ASCII-style dashed wordmark + version tag on the right, a thin green divider rule, 1-2 key-value status lines (monospace green label + white value), another divider, and a blinking-cursor prompt line at the bottom.
- Footer: `01/[TOTAL]` / `SWIPE ->`.

### Body-Overview (slide 2)
- Masthead + footer with the running page count.
- Black stamped badge: `OVERVIEW`.
- Headline: 2 lines, mostly black bold sans with one word/phrase in rust (typically the product name).
- Body copy: 2 short paragraphs, regular black/grey with bold black emphasis spans — what the product/topic is and does.
- One stat callout line: bold rust number + regular black continuation (e.g. "180k+ GitHub stars in under 4 months.").
- **Bottom row:** 3 hand-drawn icon + caption pairs side by side — a simple rust-outline icon (circular arrows, speech bubble + clock, lightning bolt, or topic-appropriate equivalents) above a short handwritten rust caption with an underline.

### Body-Step (slides 3..N-2, repeat one per step — four visual variants, pick whichever fits the step's content)
Shared elements on every Body-Step slide:
- **Giant ghost numeral:** the step number rendered huge and faint (`#E3B79A`, textured), bleeding off the right edge of the canvas behind the headline.
- **Black stamped badge, top-left:** `STEP NN`.
- **Headline:** 1-2 lines, heavy bold black sans, one word/phrase in rust.
- **Instruction line(s):** 1-3 lines regular black/grey, may include an inline monospace command chip.
- **Optional hand-drawn annotation:** a rust arrow/circle/underline pointing at the key detail, with a short handwritten caption.

Pick ONE visual-zone variant per step slide, matching what the step actually demonstrates:

**Variant A — Terminal demo** (installing, running a command, first interaction):
- Below the instruction line: a dark terminal mockup (same style as cover), masking-taped at one or two corners, showing the literal command being run, a progress bar or checklist output, and a success line. A hand-drawn circle/arrow calls out the line that confirms success, with a caption like "one command, that's it" or "if you see this, you're set".

**Variant B — Provider/option grid** (choosing between several named options — models, integrations, plans):
- Below the instruction line: a 2-row x 3-col grid of small rounded cream cards, each masking-taped at a slight rotation, containing a small colored dot (top-left), a centered brand/topic icon, and a bold label below. A hand-drawn arrow calls out one card with a caption (e.g. "swap anytime, zero config changes"). Optional "+N more [options]" line beneath the grid.

**Variant C — Hub/connection diagram** (integrations, platforms, "connect it to X"):
- Below the instruction line: a radial diagram — a small oval/pill at the center holding the product name in rust handwritten script, with hand-drawn rust arrows radiating out to 5-6 small masking-taped icon cards (platform/integration logos + label) arranged around it. A short handwritten caption sits beneath the diagram (e.g. "talk to your agent from anywhere").

**Variant D — Stacked capability cards** (skills, plugins, extensible features):
- Below the instruction line: 3 stacked horizontal cream cards, each masking-taped at an alternating corner, containing an icon, a bold monospace-style command/name label, a short grey description, and a trailing chevron. A curved hand-drawn rust arrow connects the stack to a caption (e.g. "it also creates its own skills"). Below the stack: a small terminal snippet card showing a discovery/browse command and its result count.

### Body-Tips (one slide, numbered checklist)
- Masthead + footer.
- Black stamped badge: `TIPS`.
- Headline: "Pro Tips" or equivalent, mixed black + one rust word.
- **Stacked list:** 4 horizontal cream rounded cards, masking-taped at the seams between them (implying a connected stack), each containing: a filled rust circle with a bold white number, a 2-line instruction (bold black inline command/keyword + regular black continuation), and a small hand-drawn rust icon on the right illustrating the tip.

### Body-Why (optional slide, comparison checklist — use instead of or alongside Tips)
- Masthead + footer.
- Black stamped badge: `WHY`.
- Headline: "Why [Product] Over Others?" or equivalent, mixed black + one rust word.
- **Vertical list:** 4 rows, each: a rust-outlined circular checkmark icon, a bold black feature title, a regular grey description line (1-2 lines), and a small rust hand-drawn icon on the right. Rows separated by a thin dashed rule. A curly-brace/bracket line on the far left visually connects all four rows into one set.

### CTA (last slide)
- Masthead only: `[MONTH YEAR]` / `@{{HANDLE}}` / `NN/[TOTAL]`. No footer bar.
- **Background watermark:** a faint, very-low-contrast full outline-art version of the cover's mascot/logo, centered behind the headline.
- **Headline:** giant, 3 lines, centered-left or centered: line 1 in rust ("Save"), lines 2-3 in black ("This for" / "Later") — or the equivalent action phrase for the post's CTA. Small hand-drawn rust arrows point inward at the headline from both sides.
- **Subheadline:** one line, regular grey, centered (e.g. "Follow for more [TOPIC] tutorials").
- **Black pill:** `@{{HANDLE}}`, bold cream text, centered.
- **Bottom row:** 3 small hand-drawn rust icons (bookmark, send/share, heart) separated by thin vertical dividers, centered.
- Masking-tape strips pinned at all four corners of the canvas.

## Content rules

- Masthead date should be adaptable to the actual post month/year; page counts must match the real total slide count.
- Cover headline: product/topic name only, no more than 3 short lines total including the serif accent line.
- Body-Overview: exactly 3 icon+caption pairs at the bottom, each 1-3 words.
- Body-Step: pick the variant (A/B/C/D) that matches what the step is actually showing — never force a mismatched visual (e.g. don't use the provider grid for a single-command install step).
- Body-Step headline: max ~4 words. Instruction line: max ~20 words, may include one inline command chip.
- Body-Tips: exactly 4 rows, each a single actionable tip with one bolded command/keyword.
- Body-Why: exactly 4 rows, each a short feature title + one-sentence proof.
- CTA: 3-line action headline, one concrete subheadline reason to follow, real handle.
- Every terminal mockup must show real, plausible command syntax and output — never placeholder lorem ipsum.
- No emojis. No em dashes (use commas or periods).
