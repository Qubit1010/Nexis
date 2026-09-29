# Keeping a carousel looking like one set

A carousel is six to ten separate image generations that have to read as one object. Image
models do not remember a look between generations on their own, and Google names "character
consistency across edits" among Nano Banana's open limitations (see
`../image-prompt-generator/references/model-playbooks.md`). So consistency here is engineered,
never assumed.

Researched 2026-09-25. `[vendor]` is the model maker's own documentation. `[practitioner]` is a
third-party guide with no primary confirmation found.

---

## What the evidence says

| Finding | Tier | Source |
|---|---|---|
| A reusable "character anchor" keeps visual continuity across scenes and pages while the environment and narrative vary | `[vendor]` | OpenAI prompting guide, section 6.4 |
| Repeat the preserve list on each iteration to reduce drift | `[vendor]` | OpenAI prompting guide, section 2 |
| "Same style as before" can lean on context, but re-specify critical details when they start to drift | `[vendor]` | OpenAI prompting guide, section 2 |
| For a sequence, define the narrative as clear visual beats, one per panel | `[vendor]` | OpenAI prompting guide, section 4.7 |
| Dense in-image text wants the highest quality setting | `[vendor]` | OpenAI prompting guide, sections 4.1 and 4.10 |
| Nano Banana Pro takes 6 to 14 reference images depending on the surface, and keeps multiple characters consistent | `[vendor]` | Google, Nano Banana Pro prompting tips |
| Stay in the same conversation thread for related images | `[practitioner]` | Leonardo, Morphic Nano Banana guides |
| Attach the first image of a series as a reference for the rest | `[practitioner]` | Prompt Architects, series style guide |

## The protocol this skill uses

**1. A series style block, verbatim on every slide.** One paragraph that fixes the world, the
palette in hex, the type, the frame (margins, where the slide counter and handle sit) and the
recurring motif. It leads every slide prompt, character for character. This is the vendor's
"character anchor" and "repeat the preserve list" applied to a whole slide. The lint's `set`
mode checks that it is identical on every slide and that no slide introduces a colour the block
did not declare.

**2. One beat per slide.** Each slide prompt after the style block describes only what is new
on that slide: its scene in the world and its exact text. The vendor's comic guidance is the
model for this.

**3. Generation order, stated in the output.** Generate the cover first. Keep every later slide
in the same chat, and attach the approved cover (and later, the previous slide) as a reference
image with "match the style of the attached slide exactly". If a slide drifts, regenerate that
one slide with the drift named and the style block restated, rather than restarting the set.

## What is deliberately not offered

**Panoramic carousels**, where one continuous image runs across slide edges, are a real
Instagram technique but a poor fit for separate generations. The seam has to line up to the
pixel across two independent renders, which the consistency tools above cannot guarantee. A
single wide render sliced afterwards does not work either: six 4:5 slides side by side is a
4.8:1 strip, wider than the 21:9 maximum Gemini lists. If Aleem wants one, it belongs in a
design tool with the generated art as a layer, and this skill should say so.

## Instagram facts that constrain the set

| Fact | Tier | Source |
|---|---|---|
| Up to 20 slides per carousel | `[practitioner]`, consistent across sources | Sprout Social, Storrito |
| The first slide sets the aspect ratio for the whole carousel | `[practitioner]`, consistent across sources | Sprout Social, Kapwing |
| 4:5 portrait is the default and longest-proven carousel ratio | `[practitioner]` | Contentdrips, Instacarousel |
| A 3:4 carousel option exists as of 2026 | `[practitioner]`, **one source only, unconfirmed** | Instacarousel |

No first-party Instagram help page was retrieved for these, so treat the numbers as current
convention rather than platform guarantee. Default to 4:5 and offer 3:4 only if Aleem asks.

## Sources

- OpenAI, GPT image models prompting guide (vendor):
  https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide
- Google, Nano Banana Pro prompting tips (vendor):
  https://blog.google/products-and-platforms/products/gemini/prompting-tips-nano-banana-pro/
- Leonardo, Nano Banana prompt guide (practitioner): https://leonardo.ai/news/nano-banana-prompt-guide
- Morphic, Nano Banana Pro guide (practitioner): https://morphic.com/resources/how-to/nano-banana-pro-guide
- Prompt Architects, keeping one visual style across a series (practitioner):
  https://prompt-architects.com/blog/473-keeping-one-visual-style-across-a-whole-series
- Sprout Social, Instagram carousel guide (practitioner): https://sproutsocial.com/insights/instagram-carousel/
- Storrito, Instagram's 20-slide limit (practitioner):
  https://storrito.com/resources/how-instagrams-20-slide-carousels-work-and-what-the-new-limits-are/
- Kapwing, posting different sizes (practitioner):
  https://www.kapwing.com/resources/how-to-post-multiple-images-with-different-sizes-to-instagram/
- Contentdrips, carousel size 2026 (practitioner):
  https://contentdrips.com/blog/2026/05/instagram-carousel-size-format/
- Instacarousel, carousel dimensions 2026 (practitioner, sole source for 3:4):
  https://instacarousel.com/blog/instagram-carousel-size-dimensions-2026/

**Refresh trigger:** if a set generated with this protocol drifts visibly between slides on a
current model, or Instagram changes the slide limit or ratios, re-run this pass.
