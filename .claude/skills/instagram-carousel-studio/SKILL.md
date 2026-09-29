---
name: instagram-carousel-studio
description: Designs a fresh Instagram carousel for each post instead of filling a template. Invents a visual world that unfolds slide by slide, asks every run for Aleem's brand palette or something unique and colourful, gates on a slide-by-slide brief, then writes one prompt per slide built to stay consistent as a set. The default for Instagram carousels. A named template goes to carousel, a single image to image-prompt-generator.
---

# Instagram Carousel Studio

Turns a post, and the source behind it, into **a set of slide prompts** for one Instagram
carousel, designed from scratch for that post. The output is text: a brief for approval, then one
prompt per slide. This skill never calls an image API and never claims a slide was made.

## Why this exists

`carousel` pours every post into one of six fixed templates, and its fallback for anything else
was a generic prompt skeleton. Aleem asked for the carousel equivalent of
`linkedin-infographic-studio`: creative each time, shaped by the post.

A carousel adds two problems a single infographic does not have, and they are what this skill is
really for:

- **The set has to look like one object.** Six to ten separate generations drift apart unless the
  look is pinned down and restated on every slide. Image models do not remember a style between
  generations on their own. `references/series-consistency.md` has the researched protocol.
- **The set has to move.** Each slide has to earn the swipe. That needs a world that unfolds, the
  next page, stop, panel or layer of the same thing, not one layout recoloured per slide.

Two rules carry over from the infographic skill unchanged: the content picks the structure, and
no two carousels share a visual world. Do not open `carousel/references/` for inspiration.

## Auto-start on load

Go straight to Step 1. Do not summarise the skill back.

## Step 1. Read the post

Input is a post, a description, a source (article, notes, research file, NotebookLM summary) or
a path to one. Read files in full. Pull out:

- **The promise.** What the cover commits to, as a specific claim or outcome. Not a topic.
- **The beats.** The ideas that each earn a slide, in order. Count them. Cut any beat that only
  sets up the next one.
- **The shape.** How the beats relate: a sequence, a catalogue, a comparison, a transformation.
  `../linkedin-infographic-studio/references/information-shapes.md` has the shapes and how each
  goes wrong.
- **Real numbers and where they came from.** Only numbers present in the source go on a slide.
- **The slide count.** At most **7 slides**, Aleem's cap (2026-09-25): a cover, a CTA and up to
  five slides between them. A recap slide only earns one of those five when the post is something
  people save. If the beats do not fit, merge or cut them (see "More beats than a carousel holds").

Then read `references/concept-ledger.md` (last ten rows) and any row in
`../linkedin-infographic-studio/references/concept-ledger.md` for this same post. A world used
for this post on LinkedIn is off limits here.

## Step 2. One question round

One `AskUserQuestion` call with two questions, your recommendation first and marked
`(Recommended)`. Aleem asked to be offered the colour choice every time, so ask it even when the
answer seems obvious.

**Colour**

| Option | What it means |
|---|---|
| My brand | Personal palette: black ground, `#02A1E1` on the one accent subject per slide, white and greys. No logo, no agency name |
| Unique and colourful | A palette invented for this post, usually borrowed from its visual world |
| Brand-anchored | Black and `#02A1E1` lead, plus two supporting hues |

Recommend from the topic and both ledgers, and say why in the option description.

**Concept**

Three series concepts invented for this post. Each option names the world, the recurring motif
and how it unfolds across the slides, concrete enough to picture: *"Parcel tracking: the post's
five stages as scans on one shipment's journey, a new stamp on the same label each slide, and the
cover is the label before it ships."* The three must be different worlds, and none may repeat a
world from either ledger. `references/series-design.md` covers worlds that unfold;
`../linkedin-infographic-studio/references/visual-worlds.md` has the method for inventing worlds,
the kill list, registers and palette building.

Everything else is inferred and stated in the brief: slide count, ratio, handle placement, the
CTA mechanic.

**When the answers conflict, say so.** "My brand, but make it pop" cannot be met by brand-strict,
which is one blue on black by design. Name it in one line and recommend brand-anchored.

## Step 3. The brief, then stop

Present, in this order:

1. **Concept line.** What the set shows, how it unfolds, and what it argues.
2. **The genome.** What stays fixed on every slide: the world, the palette (every hex with its
   role), the type, the frame (margins, slide counter, handle) and the recurring motif. Brand
   modes read the hexes live from `agency/personal-brand-visual-identity.md`. Colourful mode:
   check each text and fill pair with
   `python .claude/skills/linkedin-infographic-studio/scripts/lint_prompt.py contrast "<text>" "<fill>"`.
3. **Slide by slide.** A table with the slide number, its role (cover, body, recap, CTA), its
   beat in the world (what is drawn), and its exact text. Numbers carry their source.
4. **Stated defaults.** Slide count, vertical 4:5 portrait, handle `@aleem_uh` small on the cover
   and CTA only, the CTA mechanic (save, or a comment keyword), total word count.

End with: *"Tweak anything, or say 'generate'."* Then wait. Regenerating a whole set is the most
expensive failure in any of the image skills, and a wrong beat or a wrong genome is one line to
fix here.

## Step 4. Write, lint, emit

Read `../image-prompt-generator/references/model-playbooks.md` before writing. Its five rules
(positive framing, ratio in words, subject before style, quoted text with its typography, hex
palette) apply to every slide prompt.

**The series style block.** One paragraph, written once, that leads every slide prompt word for
word. It carries the whole genome: that this is one slide of a single Instagram carousel in a
vertical 4:5 portrait format, the world, every hex with its role, the type, the frame and the
motif. Keeping it identical is how the set stays consistent, so do not paraphrase it between
slides, even slightly.

**Each slide prompt** is the style block, a blank line, then that slide's beat: its role, what
is drawn and where, and its exact text in quotes, with the one accent subject named.

Write the whole set to one scratchpad file, each slide starting with a line `### SLIDE <n>
(<role>)`, and lint it:

```
python .claude/skills/linkedin-infographic-studio/scripts/lint_prompt.py set <file> --mode brand|anchored|colourful --max-slides 7
```

`set` runs every single-prompt check on each slide, then checks the series: the style block is
present and identical on every slide, no slide uses a hex the style block did not declare, and
the count is within the 7-slide cap. Fix and re-run until the last line reads `LINT PASS`.
`LINT DID NOT RUN` is not a pass, and if the script cannot run, say so rather than calling the
set checked.

Two checks the script cannot do. **The swap test:** put a different topic into the concept; if
the set still works, the world is decoration. **The pair test:** picture slide 3 beside slide 6;
they should read as two pages of one thing, and as two different pages.

Then output, in one message:

1. **Concept line.**
2. **How to generate it**, in three lines: generate slide 1 first; keep every later slide in the
   same chat; attach the approved cover (then the previous slide) as a reference image and say
   "match the style of the attached slide exactly". If one slide drifts, regenerate only that
   slide and restate the style block. Best in Gemini (Nano Banana Pro) or ChatGPT image
   generation; Midjourney is the weakest at text.
3. **The slide prompts**, one code block each, labelled `Slide 1 of N (cover)` and so on. Leave
   out the `### SLIDE` marker lines, which exist only for the lint.
4. **A caveat only if one applies,** such as a text-budget warning from the lint.

Finally append one row to `references/concept-ledger.md`.

## Inside post-creator (headless)

When `post-creator` calls this skill, its step-5 checkpoint is the one gate:

- Run Step 1 on the row's Simplified Source and description.
- Pick the recommended concept. Colour defaults to **brand** unless the row or Aleem says
  otherwise. Check both ledgers as usual, including the LinkedIn infographic this same run may
  have just designed.
- At post-creator's checkpoint show: the concept line, the colour mode, the other two concepts in
  one line each, and the slide-by-slide text. Aleem can switch concept or colour there.
- After his OK, run Step 4 and put the slide prompts in the Doc's `Instagram - Carousel Prompt`
  tab. Append the ledger row.

## When the input is thin or broken

- **A topic with no angle or source.** Offer two or three angles. Do not invent beats or numbers.
- **More beats than a carousel holds.** Five slides between cover and CTA is the room. Merge
  related beats onto one slide or cut to the strongest, and say which in the brief. If the post
  genuinely needs more, suggest splitting it into two carousels rather than breaking the cap.
- **A number the post needs but the source lacks.** Build the slide without it.
- **A path that does not resolve.** Say so and stop.
- **"Template 8", "same as last time".** Hand off to `carousel`.
- **A panoramic carousel** (one image running across slide edges). Explain why separate
  generations cannot line up the seams (`references/series-consistency.md`), and offer a set
  where the motif continues across slides without needing a pixel-perfect join.

## Rules

- **One carousel per run,** one prompt per slide, never a single combined prompt for the set.
- **Personal brand.** No NexusPoint name or logo and no university. The handle `@aleem_uh` is
  fine. The lint enforces the rest.
- **No emojis and no em dashes** anywhere this skill writes, prompts included.
- **Never invent a statistic.** Every number traces to the source Aleem gave.
- **No photorealistic depictions of real, named people.**

## Boundaries

| Hand off to | For |
|---|---|
| `carousel` | A named template, or the same look as a past set |
| `linkedin-infographic-studio` | One dense infographic for LinkedIn |
| `image-prompt-generator` | A single image with little text |
| `content-production` | A LinkedIn document carousel (a PDF, not an image set) |
| `shorts-creator` | 9:16 Reels or Shorts frames |
| `content-engine` | The caption that goes with the carousel |

## Reference files

- `references/series-design.md`: the arc, genome and beats, worlds that unfold, text budget and
  the frame. Read every run.
- `references/series-consistency.md`: the researched protocol for keeping the set consistent,
  Instagram's constraints, and why panoramic sets are not offered.
- `references/concept-ledger.md`: every set shipped, plus the template skill's six looks as off
  limits. Read before proposing, append after emitting.
- `../linkedin-infographic-studio/references/information-shapes.md` and `visual-worlds.md`:
  shapes, world invention, the kill list, registers and palettes. Shared with the infographic
  skill rather than copied.
- `../linkedin-infographic-studio/scripts/lint_prompt.py`: `set` lints the whole carousel,
  `contrast` measures a colour pair.
- `../image-prompt-generator/references/model-playbooks.md`: the universal prompt contract.
