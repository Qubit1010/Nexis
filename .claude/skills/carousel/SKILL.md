---
name: carousel
description: >
  Generate a branded Instagram carousel from a post description + source. Builds a slide-by-slide
  design brief, waits for approval, then outputs per-slide Gemini image-generation prompts at
  1080x1350 (4:5). Use this skill whenever the user says "carousel", "build a carousel",
  "turn this into a carousel", "instagram carousel", or wants multi-slide Instagram content from
  a post, source, or framework. Always includes an approval gate between brief and prompt output.
---

# Instagram Carousel

## Templates (preferred path)

Reusable design templates live in `references/<Template>/`. Each has a `design-structure.md`
(the spec), a `gem.md` (a Gemini Gem to build once), and an `input-prompt.md` (the per-post fill).

- **Instagram-Template-1** (`references/Instagram-Template-1/`) — blue-gradient statue cover +
  terracotta editorial body slides. Source images in `docs/Instagram-Template-1/`.
- **Instagram-Template-2** (`references/Instagram-Template-2/`) — cinematic dark film-grain cover
  + CTA (deep red/maroon photo) with clean cream dot-grid body slides. Mixed bold-sans + italic-serif
  headlines, hand-drawn arrow annotations, screenshot visuals. Comment-to-DM CTA mechanic.
  Source images in `docs/Instagram-Template-2/`.
- **Instagram-Template-6** (`references/Instagram-Template-6/`) — resource/tool showcase format.
  Soft sage-gradient cover with dark forest-green wave. Dark charcoal body slides: device mockup
  screenshot (upper half) + two structured info cards (name/category/creator + description) + metric
  pill. Dark-gradient CTA with dotted-border pixelated keyword pill and "Comment -> DM" mechanic.
  Best for: top-N tool lists, GitHub repo showcases, AI skill packs, plugins, frameworks.
  Source images in `docs/Instagram-Template-6/`.
- **Instagram-Template-10** (`references/Instagram-Template-10/`) — GitHub repo / plugin showcase
  format. Two visual registers: cinematic dark navy cover with a large 3D plush mascot + multicolor
  heavy headline (pink + amber + white); cream dot-grid editorial body slides with ultra-heavy black
  headline, inline screenshot embed, "Why it matters" body text, two tag pills, and an italic serif
  punchline quote. Cream CTA with massive stacked all-caps "COMMENT [KEYWORD] FOR THE [PAYOFF]."
  mechanic. No handle on body or CTA -- identity only on the cover. Best for: curated plugin lists,
  GitHub repo roundups, open-source tool showcases where each item has a URL and a metric.
  Source images in `docs/Instagram-Template-10/`.

When a template fits the user's ask, recommend it: tell them to build the Gem once from `gem.md`
(attach the 4 Knowledge images), then use `input-prompt.md` per post so Gemini renders the slides
in that exact look, one slide at a time (cover first, then "next" for each following slide). The inline brief + per-slide prompt flow below (Steps 1-4) is the fallback when
no template applies or the user wants a one-off custom design.

## Auto-start on load

When this skill triggers, go straight to Step 1. Do not summarise.

## Step 1. Gather inputs

Ask:

> Paste the **post description** (what the post is about, your angle) and the **source** (the article,
> newsletter section, research note, framework, or URL you want to pull from). Both make a better
  carousel than either alone.

Wait for the content, then call AskUserQuestion:

```json
[
  {
    "question": "Brand style?",
    "header": "Style",
    "multiSelect": false,
    "options": [
      {"label": "Pull from brand-kit.md", "description": "Use the colours and typography in my project brand file if it exists"},
      {"label": "I will type brand colours", "description": "I will paste hex codes and font preferences"},
      {"label": "Suggest for me", "description": "Pick a palette and typography based on the content"}
    ]
  },
  {
    "question": "Number of slides?",
    "header": "Slides",
    "multiSelect": false,
    "options": [
      {"label": "6 slides", "description": "Concise, fast read, strong for saves"},
      {"label": "8 slides", "description": "Standard Instagram carousel length"},
      {"label": "10 slides", "description": "Deep-dive carousel"}
    ]
  }
]
```

## Step 2. Build the design brief

Analyse the post description + source and produce a slide-by-slide brief. Instagram carousels
live or die on the cover hook and skim-ability - every slide must read in under 2 seconds.

- **Slide 1 (Cover)**: hook only, max 8 words, stops the scroll, stands alone as a thumbnail.
- **Slides 2 to N-1 (Body)**: one idea per slide. Single label headline + one-sentence
  elaboration. Max 15 words of body. Skimmable.
- **Slide N (CTA)**: value-native CTA. "Save this if you're building one" beats "follow me".
  Optional comment-to-DM trigger ("comment X and I'll send it").

For each slide include:

- Slide number
- Headline (max 8 words)
- Body text (max 15 words; cover slide has body omitted, hook only)
- Visual suggestion (icon, colour block, illustration, diagram)

Tell the user:

> Here is the design brief. Tell me what to change, or say "generate" when you are happy.

Wait for approval. Do not proceed until the user explicitly approves. This gate exists because
regenerating a full carousel set is expensive - it is cheaper to fix the brief than the slides.

## Step 3. Output per-slide prompts

Once approved, output one Gemini image generation prompt per slide, each in its own code block,
numbered clearly.

Every prompt follows this structure:

```
Act as an expert graphic designer. Create an Instagram carousel slide at 1080x1350 pixels (4:5 aspect ratio).

Brand style:
- Primary colour: [HEX]
- Secondary colour: [HEX]
- Accent colour: [HEX]
- Typography: [bold industrial headline font, clean geometric body font]
- Aesthetic: modern, authoritative, high contrast

Slide [N of M]: [slide purpose]

Content:
- Headline: "[headline text]"
- Body: "[body text]"
- Visual element: [specific visual suggestion]

Layout instructions:
- [Headline placement and size]
- [Body placement and size]
- [Visual placement]
- [Background treatment]

Constraints:
- Vertical 4:5 aspect ratio at exactly 1080x1350 pixels
- No watermarks, no logos unless specified above
- Maintain visual consistency with the other slides in the set
```

Tell the user:

> Paste each prompt into a new Gemini chat with Create Image enabled and Nano Banana selected.
> Generate slides one at a time for maximum control over consistency.

## Step 4. Offer one-shot alternative

After the per-slide prompts, offer:

> Want a single combined prompt that generates the full carousel in one shot? Faster but less
  visual consistency. Say "combine" and I will rewrite.

## Rules

- Always gate on user approval of the brief before outputting image prompts.
- 1080x1350 pixels per slide, 4:5 aspect ratio. No other aspect ratio.
- Maximum 15 words of body text per body slide. The cover is hook only, max 8 words. Readability
  loses on the feed.
- Keep the brand style identical across every slide prompt so the set looks like one carousel.
- Cover (1) and CTA (last) must be visually distinct from body slides.
- No emojis. No em dashes - use commas or periods instead.
- CTA is value-native (save / comment-to-DM), never a bare "follow me".
- If brand-kit.md exists in the project, read it and use its exact hex codes and typography.
