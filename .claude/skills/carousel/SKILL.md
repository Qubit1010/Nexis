---
name: carousel
description: >
  Fills one of six fixed Instagram carousel templates (statue editorial, film-grain cover,
  tool showcase, grid-paper tutorial, repo showcase, kraft zine) into per-slide Gemini prompts
  after an approval gate. Use only when a template is named or a past carousel look is wanted
  again ("template 8", "same as last time"). For a fresh design per post, instagram-carousel-studio.
---

# Instagram Carousel

## Templates (preferred path)

Reusable design templates live in `references/<Template>/`. Each has a `design-structure.md`
(the spec), a `gem.md` (a Gemini Gem to build once), and an `input-prompt.md` (the per-post fill).

- **Instagram-Template-1** (`references/Instagram-Template-1/`) — blue-gradient statue cover +
  terracotta editorial body slides. Source images in `docs/Instagram-Template-1/`.
- **Instagram-Template-2** (`references/Instagram-Template-2/`) — cinematic dark film-grain cover
  + CTA (deep navy/blue photo, agency brand blue #A6DAFF to #00B7FF) with clean cream dot-grid body slides. Mixed bold-sans + italic-serif
  headlines, hand-drawn arrow annotations, screenshot visuals. Comment-to-DM CTA mechanic.
  Source images in `docs/Instagram-Template-2/`.
- **Instagram-Template-6** (`references/Instagram-Template-6/`) — resource/tool showcase format.
  Soft sage-gradient cover with dark forest-green wave. Dark charcoal body slides: device mockup
  screenshot (upper half) + two structured info cards (name/category/creator + description) + metric
  pill. Dark-gradient CTA with dotted-border pixelated keyword pill and "Comment -> DM" mechanic.
  Best for: top-N tool lists, GitHub repo showcases, AI skill packs, plugins, frameworks.
  Source images in `docs/Instagram-Template-6/`.
- **Instagram-Template-8** (`references/Instagram-Template-8/`) — step-by-step build/tutorial
  format. Off-white grid-paper background throughout. Cover: dashed pill kicker, 3-line headline
  with a terracotta accent word, browser-mockup preview bleeding off the bottom. One overview slide
  lists 3-5 stacked colored file/item cards. Numbered step slides are threaded by a single vertical
  color-gradient progress rail (blue -> purple -> orange -> green) with a phase-colored step badge,
  a "PHASE N · NAME" pill, and a cream copy-paste prompt box with a sunburst icon + send button.
  CTA is centered with a comment-pill mechanic and an identity chip. Best for: "how I built X"
  walkthroughs, AI workflow tutorials, and any process breakdown with real copy-paste prompts.
  Source images in `docs/SM-Posts-Templates/Instagram-Template-8/`.
- **Instagram-Template-10** (`references/Instagram-Template-10/`) — GitHub repo / plugin showcase
  format. Two visual registers: cinematic dark navy cover with a large 3D icon/symbol built fresh per
  topic (never a generic mascot) + multicolor heavy headline (pink + amber + white); cream dot-grid editorial body slides with ultra-heavy black
  headline, inline screenshot embed, "Why it matters" body text, two tag pills, and an italic serif
  punchline quote. Cream CTA with massive stacked all-caps "COMMENT [KEYWORD] FOR THE [PAYOFF]."
  mechanic. No handle on body or CTA -- identity only on the cover. Best for: curated plugin lists,
  GitHub repo roundups, open-source tool showcases where each item has a URL and a metric.
  Source images in `docs/Instagram-Template-10/`.
- **Instagram-Template-11** (`references/Instagram-Template-11/`) — vintage kraft-paper zine
  tutorial format. Magazine masthead (date/handle/page) top and bottom of every slide, warm tan
  paper texture, masking-tape motif, hand-drawn rust arrows/annotations, and a giant faded ghost
  numeral behind each step headline. Cover has a taped terminal mockup; overview slide explains the
  product; numbered step slides pick from four visual variants (terminal demo, provider/option grid,
  hub/connection diagram, stacked capability cards) matched to what each step shows; closes on a
  numbered "Pro Tips" checklist and/or a "Why X Over Others" comparison list, then a "Save This"
  CTA with a ghost-logo watermark. Best for: dev-tool setup guides, CLI/product walkthroughs, AI
  agent tutorials with real commands and terminal output.
  Source images in `docs/SM-Posts-Templates/Instagram-Template-11/`.

When a template fits the user's ask, recommend it: tell them to build the Gem once from `gem.md`
(attach the Knowledge images), then use `input-prompt.md` per post so Gemini renders the slides
in that exact look, one slide at a time (cover first, then "next" for each following slide).

**When no template fits, or the user wants something new, hand off to
`instagram-carousel-studio`.** Since 2026-09-25 it is the default for Instagram carousels: it
invents a series concept per post and keeps the set consistent with a shared style block. The
generic custom-design flow that used to live here (a fixed prompt skeleton with pixel sizes and
a "no watermarks" list) was retired in its favour.

## Auto-start on load

When this skill triggers, go straight to Step 1. Do not summarise.

## Step 1. Gather inputs

Ask for the **post description** (the angle) and the **source** (article, research note,
framework, URL), and confirm which template. If the user has not named one, recommend the best
fit from the list above, or hand off to `instagram-carousel-studio` if none fits.

## Step 2. Map the content into the template

Read the template's `input-prompt.md` and map the content into its blocks (CONTEXT, COVER,
BODY slides, CTA, or whatever that template defines), respecting its counts. Present the mapping
as a slide-by-slide list: each slide's headline and body text, and which template block it fills.

Tell the user:

> Here is the slide map. Tell me what to change, or say "generate" when you are happy.

Wait for approval. Regenerating a full carousel set is expensive, and fixing the map is cheap.

## Step 3. Output the filled blocks

Once approved, output the template's blocks filled with the approved text, each in its own code
block, numbered, in the order `input-prompt.md` defines. Tell the user to paste them into the
template's Gem one at a time, cover first.

## Rules

- Always gate on user approval of the slide map before outputting prompts.
- Keep each template's own ratio, palette and rules exactly as its files define them.
- No emojis. No em dashes - use commas or periods instead.
- CTA is value-native (save / comment-to-DM), never a bare "follow me".
- No template fits, or the user wants a one-off look: `instagram-carousel-studio`. A single
  freeform image: `image-prompt-generator`.
