# Instagram-Short-Template-1 — Design Structure

Canonical spec extracted from the one reference cover Aleem shared (a "Free Guide" promo for
"The Claude Practical Playbook"), stored in `docs/Instagram-Short-Template-1/`. That
reference is a finished COVER frame; the CONTENT and CTA frame specs below extrapolate the
same visual language (dark background, diagonal stripe, logo, wordmark) since no reference
image exists yet for those two frame types - treat them as a first draft and adjust once
Aleem sees the first generated set. This file is the source of truth for `gem.md` and
`input-prompt.md`.

## Global

- **Canvas:** 1080 x 1920 px, 9:16 aspect ratio. Every frame. Native Instagram Reels/Shorts
  vertical - deliberately different from `carousel`/`linkedin-infographics`'s 4:5 (1080x1350).
- **Frame sequence:** COVER (1) -> CONTENT (2, optionally 3) -> CTA (last).
- **Generation protocol:** one frame per image, one at a time. Never tiled, never a deck. See
  `gem.md` OUTPUT FORMAT.
- **Template purpose:** a quick vertical teaser sequence for any topic - product drops, case
  studies, quick takes, lead-magnet promos. Not a full carousel (the `carousel` skill handles
  longer multi-slide breakdowns) and not a rendered video (`reel-creator` handles that).
- **Tone:** dark, high-contrast, confident. Bold display type does most of the work, with
  minimal ornamentation beyond the diagonal stripe motif.
- **Branding (always on, every frame):** NexusPoint "N" logomark top-left with small
  circuit-node accent dots/lines trailing from it, and the "NexusPoint" wordmark centered at
  the bottom. This is a deliberate exception to Aleem's usual no-agency-mention rule for
  personal content - shorts are a distinct, always-agency-attributed lane.

## Palette

| Token | Hex | Use |
|---|---|---|
| Background | `#141414` | near-black base, every frame |
| Headline white | `#FFFFFF` | headline, CTA pill text |
| Subtitle gray | `#9A9A9A` | subtitle line, wordmark footer |
| Eyebrow white | `#FFFFFF` | tracked-out eyebrow label |
| Stripe light | `#4FA3F7` | diagonal gradient stripe, lighter end |
| Stripe dark | `#1C5FA8` | diagonal gradient stripe, darker end |
| CTA pill fill | `#141414` | CTA pill background (matches base, sits on the stripe) |
| CTA pill border | `#4FA3F7` | CTA pill outline |

## Type stack

- **Eyebrow label:** small, bold, all-caps, wide letter-spacing, white. Match: Inter Bold or
  Helvetica Now Bold, tracked out.
- **Headline:** very large, heavy weight, tight line-height, white, left-aligned. Match:
  Inter ExtraBold, Helvetica Now Display Bold, or a similar heavy grotesque.
- **Subtitle:** medium weight, gray, comfortable line-height, left-aligned. Match: Inter
  Regular/Medium.
- **CTA pill text:** bold, white, centered. Same family as the headline.
- **Wordmark:** medium weight, gray, small, centered. Same family as the subtitle.

## Frame anatomy

### Cover (frame 1)
- **Background:** solid near-black (`#141414`).
- **Top-left:** NexusPoint "N" logomark (white) with circuit-node accent dots/lines.
- **Below logo:** small tracked-out all-caps eyebrow label, white (e.g. "NEW DROP").
- **Center-left, below eyebrow:** large bold white headline, 2-4 lines, left-aligned (the
  hook - what the short is about).
- **Below headline:** one gray subtitle line, smaller, left-aligned (the one-sentence
  elaboration).
- **Lower-middle:** diagonal blue gradient stripe (light `#4FA3F7` to dark `#1C5FA8`) sweeping
  from bottom-left to upper-right, crossing behind/beside the text block.
- **Bottom center:** "NexusPoint" wordmark, small, gray.
- No CTA pill on the cover - it is hook-only, the pill belongs on the CTA frame.

### Content (frame 2, optionally frame 3)
- **Background:** same near-black base, same diagonal stripe motif (keeps the sequence
  visually continuous), same logo top-left and wordmark footer.
- **Center:** one bold white statement per frame (the single idea this frame carries), sized
  large but shorter than the cover headline - this is one point, not a hook.
- **Below the statement (optional):** one short supporting label or stat, gray, smaller - use
  only if the point needs a number or category tag to land.
- Content frames do not repeat the cover's eyebrow label - keep any frame-number cue minimal
  (e.g. a small "02" near the logo) if one is needed at all.

### CTA (last frame)
- **Background:** same near-black base and diagonal stripe, stripe brought forward/enlarged
  slightly so the pill can sit on it.
- **Center:** rounded-rectangle pill, near-black fill, blue outline (`#4FA3F7`), bold white
  text - the URL or the short action phrase (e.g. "Comment GUIDE").
- **Below pill (optional):** one short line, gray, stating the payoff (what they get).
- **Bottom center:** "NexusPoint" wordmark, same as every frame.

## Content rules

- Headline: 2-4 lines, keep each line short enough to read in under a second.
- Subtitle: one sentence, plain language.
- Content frame statement: one idea, short enough to read at a glance - this is a frame
  someone sees for a second or two in a Reel, not a paragraph.
- CTA pill text: one URL or one short action phrase, nothing longer.
- No emojis. No em dashes (use commas or periods).
- Keep the diagonal stripe motif and background consistent across every frame - it is what
  makes the sequence read as one short instead of unrelated images.
