# Instagram-Template-6 — Design Structure

Canonical spec extracted from the reference carousels in `docs/Instagram-Template-6/`
(cover `508521`, body `509518` / `510519` / `513524`, CTA `516524`).
Source-template identity ("@craftwork.design") is stripped and replaced with `@{{HANDLE}}`.
This file is the source of truth for `gem.md` and `input-prompt.md`.

## Global

- **Canvas:** 1080 x 1350 px, 4:5 aspect ratio. Every slide.
- **Frame:** Every slide has **rounded outer corners** (~32px radius) and sits inside a very thin dark stroke/shadow, giving the appearance of an app card or device screenshot. This rounded frame is part of every image.
- **Slide order:** Cover (1) -> Body (2..N-1) -> CTA (N).
- **Generation protocol:** one slide per image, one at a time. Never tiled, never a deck. See `gem.md` OUTPUT FORMAT.
- **Template purpose:** Resource showcase / tool card format. Ideal for "top N tools", GitHub repos, AI skills, plugins, or any content where each body slide presents one named resource with metadata.
- **Tone:** clean, app-native, modern dark UI. Reads like a polished product showcase, not editorial content.
- **Identity:** `@{{HANDLE}}` in top-left bar of the cover slide. CTA uses a circular badge icon top-left. Never "@craftwork.design" or any source-template name.

## Palette

| Token | Hex | Use |
|---|---|---|
| Cover gradient top | `#A8C4BC` | cover background top (muted sage/teal) |
| Cover gradient mid | `#7A9E96` | cover background center |
| Cover wave | `#2D4A3E` | dark forest green organic arc shape at bottom ~35% of cover |
| Body bg | `#1A1A1C` | body slide background (dark charcoal) |
| Body card bg | `#242426` | info card fill (slightly lighter than body bg) |
| Body label text | `#8A8A8E` | metadata labels (SKILL NAME, CATEGORY, etc.) |
| Body value text | `#FFFFFF` | metadata values |
| Body body text | `#C8C8CC` | description card body text |
| Metric pill bg | `#2E2E30` | GitHub stars / metric pill fill |
| CTA gradient top | `#0D0D0F` | CTA background top (near-black) |
| CTA gradient bottom | `#2A3850` | CTA background bottom (dark slate/blue-grey) |
| CTA pill fill | `#E8E8E8` | large keyword pill background |
| CTA pill text | `#1A1A1C` | keyword text (pixelated/LCD font) |
| White | `#FFFFFF` | cover headline, CTA handwritten text |
| Near-black | `#1C1C1C` | cover sub-label, cover handwritten |
| Grey label | `#6E6E73` | top bar text on cover + body |

## Type stack

- **Cover headline:** heavy bold rounded sans, white, large, centered. Match: Nunito ExtraBold, Figtree Bold, or any heavy rounded grotesque.
- **Cover sub-label + CTA text:** casual rounded handwritten/display font. Match: Caveat, Patrick Hand, or any friendly rounded handwritten. Used on cover ("Collection", "Swipe for start") and ALL of the CTA slide.
- **Top bar + bottom bar labels:** small uppercase monospace, letter-spaced, muted grey. Match: Space Mono, JetBrains Mono.
- **Body card label (SKILL NAME, CATEGORY, AUTHOR, DESCRIPTION, GITHUB STARS):** small uppercase monospace, muted grey (#8A8A8E).
- **Body card title:** heavy bold rounded sans, white, large (same family as cover headline).
- **Body card value text:** regular rounded sans, white, medium.
- **Body card description:** regular sans, light grey (#C8C8CC), smaller.
- **CTA keyword (inside pill):** monospace pixelated/LCD retro font (like Silkscreen, Press Start 2P, or a dotted-matrix font). Near-black.

## Slide anatomy

### Cover (slide 1)
- **Canvas:** rounded corners (~32px), dark near-black thin border visible behind the rounded frame.
- **Background:** smooth two-tone gradient -- sage/teal (#A8C4BC) at top blending to mid-teal (#7A9E96), with a large organic arc/wave shape in dark forest green (#2D4A3E) sweeping across the bottom ~35% of the canvas.
- **Top navigation bar (full width):**
  - Left: small circular badge icon + `@{{HANDLE}}` in small monospace grey
  - Right: `[CATEGORY LABEL]` in small uppercase monospace grey (e.g. "AI TOOLS", "DESIGN ASSETS")
- **Center:** giant bold rounded sans headline, white, 2 lines, centered (the carousel topic, e.g. "AI automation tools").
- **Center sub-label:** casual handwritten font, near-black, centered below the headline (e.g. "Collection", "Starter Pack", "for founders").
- **Bottom center:** small finger-point/swipe icon + "Swipe for start" in casual handwritten font.
- **Bottom navigation bar:**
  - Left: "SUBSCRIBE FOR MORE" in small uppercase monospace grey
  - Right: "SAVE FOR LATER ->" + bookmark icon in small uppercase monospace grey

### Body (slides 2..N-1)
- **Canvas:** same rounded corners. Dark charcoal background (#1A1A1C).
- **Top navigation bar:**
  - Left: resource URL or path (e.g. "GITHUB.COM/USER/REPO" or "TOOL.COM/FEATURE") in small uppercase monospace grey
  - Right: "SWIPE ->" + finger icon in small uppercase monospace grey
- **Hero zone (upper ~55%):** a large device mockup (rounded dark iPad/tablet frame) showing a screenshot of the resource, tool, or website. Centered, subtle drop shadow. The screenshot fills the frame.
- **Info zone (lower ~45%):** two side-by-side rounded dark cards (#242426):
  - **Left card:** stacked key-value pairs:
    - Label: "[NAME LABEL]" small uppercase monospace grey
    - Value: bold white title (the resource name)
    - Label: "[CATEGORY LABEL]" monospace grey
    - Value: regular white category
    - Label: "[CREATOR LABEL]" monospace grey
    - Value: regular white creator name(s)
  - **Right card:** stacked:
    - Label: "DESCRIPTION" monospace grey
    - Value: body text in light grey (#C8C8CC), regular weight, 3-5 lines
- **Metric row (below the two cards):** full-width row with a label ("GITHUB STARS", "PRICE", "RATING", etc.) in monospace grey on the left and the metric value in a small dark rounded pill (with a relevant icon, e.g. star) on the right.
- No bottom navigation bar on body slides.

### CTA (slide N)
- **Canvas:** same rounded corners. Vertical gradient from near-black (#0D0D0F) at top to dark blue-grey (#2A3850) at bottom.
- **Top-left:** small circular badge icon (no handle text).
- **Center (upper):** "Want all the [VALUE]?" or similar teaser in casual handwritten font, white, centered.
- **Center:** "Comment" in casual handwritten font + small curved arrow icon pointing down, white.
- **Large keyword pill:** rounded rectangle with a dotted/pixelated border, light grey fill (#E8E8E8), keyword text in retro pixelated/LCD monospace font, near-black. This is the word users comment.
- **Below pill:** "and we'll DM you [PAYOFF]" in casual handwritten font, white, large, centered (2-3 lines).
- **Dashed separator line** across the full width.
- **Below separator:** casual handwritten text "Follow @{{HANDLE}} for more" + globe or link icon + handle in underline style.
- **Bottom navigation bar:**
  - Left: "SUBSCRIBE FOR MORE" small uppercase monospace grey
  - Right: "SWIPE ->" + finger icon small uppercase monospace grey

## Content rules

- Cover headline: 2-3 words max per line, 2 lines. Sub-label: 1-3 words, handwritten.
- Body: one resource per slide. Info cards are structured data, not prose. Description max ~30 words.
- CTA keyword: one uppercase word or short phrase. The comment trigger.
- No emojis. No em dashes (use commas or periods).
- Resource URL in top bar matches what is shown in the screenshot.
- Metric label and value should be real or plausible (GitHub stars, price, user count, rating).
