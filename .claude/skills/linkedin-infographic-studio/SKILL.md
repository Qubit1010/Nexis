---
name: linkedin-infographic-studio
description: Designs a fresh LinkedIn infographic for each post instead of filling a template. Finds the content's shape, invents a visual concept that fits it, asks every run for Aleem's brand palette or something unique and colourful, gates on a content blueprint, then writes one prompt for Gemini or ChatGPT. The default for LinkedIn infographics. A named template goes to linkedin-infographics, a non-infographic image to image-prompt-generator.
---

# LinkedIn Infographic Studio

Turns a LinkedIn post, and the source behind it, into **one infographic image prompt** designed
from scratch for that post. The output is text: a blueprint for approval, then one prompt. This
skill never calls an image API and never claims an image was made.

## Why this exists

`linkedin-infographics` pours every post into one of seven fixed layouts. After enough posts
they all looked like the same seven posters, and Aleem asked for something that works like
`image-prompt-generator` but for infographics: creative each time, shaped by the post.

So this skill sits between its two siblings. From the template skill it keeps the infographic
discipline: dense but legible text, a clear reading path, and an approval gate, because a wrong
infographic costs a full re-render. From `image-prompt-generator` it takes composing from
scratch and a prompt that works in any tool. Two rules make it different from both:

- **The content picks the structure.** A process becomes a path, a comparison becomes facing
  sides, a hierarchy becomes levels. Structure comes from reading the post, never from a layout
  on file. Do not open `linkedin-infographics/references/` for inspiration. That is the
  convergence this skill exists to avoid.
- **No two infographics share a visual world.** `references/concept-ledger.md` records every one.
  Read it before proposing concepts and append to it after emitting.

## Auto-start on load

Go straight to Step 1. Do not summarise the skill back.

## Step 1. Read the post

Input is a post, a post description, a source (article, notes, research file, NotebookLM
summary), or a path to one. Read files in full. Pull out:

- **The argument.** What the reader should walk away believing, in one sentence. It usually
  becomes the headline, and it decides the accent subject.
- **The units.** The discrete things the image has to carry: steps, tools, levels, mistakes,
  numbers. Count them.
- **The shape.** How the units relate. `references/information-shapes.md` lists the shapes, their
  unit budgets and how each goes wrong. Read it every time; picking the shape is the step that
  most decides whether the image works.
- **Real numbers and where they came from.** Only numbers present in the source go in the image.
- **Density.** Scannable or reference, inferred from the post's intent and the unit count.

Then read the last ten rows of `references/concept-ledger.md`, so the concepts you propose do not
repeat a recent visual world.

## Step 2. One question round

One `AskUserQuestion` call with two questions, your recommendation first and marked
`(Recommended)`. Aleem asked to be offered the colour choice every time, so ask it even when the
answer seems obvious.

**Colour**

| Option | What it means |
|---|---|
| My brand | Personal palette: black ground, `#02A1E1` on the one accent subject, white and greys. No logo, no name |
| Unique and colourful | A palette invented for this post, usually borrowed from its visual world |
| Brand-anchored | Black and `#02A1E1` lead, plus two supporting hues for categories |

Recommend from the topic and the ledger, and say why in the option description. A technical post
about systems reads native in the brand. If the last few rows were all brand, variety is a fair
reason to suggest colour.

**Concept**

Three concepts invented for this post. Each option is a visual world plus how the content maps
onto it, concrete enough to picture: *"Shipping label: the five parts of a good automation brief
as the fields of a parcel label, with the success metric printed as the barcode every scanner
downstream has to read."* The
three must be different worlds, not one world in three colours, and none may reuse a world from
the recent ledger. `references/visual-worlds.md` has the method for inventing them and the kill
list of worlds that read as AI-generated.

Everything else is inferred and stated in the blueprint, where one line corrects it: format,
density, text volume, register, signature line.

**When the answers conflict, say so.** The usual one is "my brand, but make it pop". Brand-strict
is one blue on black by design, and those two asks cannot both be met. Name the conflict in one
line and recommend brand-anchored rather than quietly splitting the difference.

## Step 3. The blueprint, then stop

Present, in this order:

1. **Concept line.** One or two sentences: what the image shows and what it argues.
2. **Palette.** Every hex with its role (ground, surface, ink, accent subject, category hues).
   Brand modes read the hexes live from `agency/personal-brand-visual-identity.md`, never from
   memory. Colourful mode: check each text and fill pair with
   `python .claude/skills/linkedin-infographic-studio/scripts/lint_prompt.py contrast "<text>" "<fill>"`
   and change any pair below 4.5:1 for body text or 3:1 for a large headline.
3. **Layout.** Format, the reading path, and the zones from top to bottom with a rough share of
   the height each takes.
4. **The exact text, zone by zone.** Headline, subtitle, every unit's label and line, each number
   with where it came from. This is the copy that will be rendered, so it is what Aleem edits.
5. **Stated defaults.** Format (vertical 4:5 portrait unless the post needs otherwise), density,
   total word count, register, and that there is no signature line ("add my name" puts
   "Aleem Ul Hassan" small at the foot).

End with: *"Tweak anything, or say 'generate'."* Then wait. The gate is here because the expensive
failure is a re-render caused by wrong copy or a wrong structure, and both are one line to fix at
this point.

## Step 4. Write, lint, emit

Read `../image-prompt-generator/references/model-playbooks.md` before writing. Its five rules are
what make one prompt work in Gemini, ChatGPT and elsewhere: positive framing only, the ratio in
words, subject before style, literal text in quotes with its typography described, the palette
in hex. They apply here unchanged.

Assemble the prompt in this order, as flowing sections rather than a keyword list:

1. **What it is.** One single infographic image, vertical 4:5 portrait, for a LinkedIn feed,
   drawn as the chosen world in the chosen register. State "one single image" positively.
2. **Canvas and palette.** Ground, surfaces, ink, accent subject and category hues, each as a
   named colour plus hex.
3. **Typography.** Headline, label and caption styles by character and weight.
4. **Zones, top to bottom.** For each zone: where it sits, how it is drawn in the world, and its
   exact text in quotes. The accent subject is called out as the one element carrying the accent.
5. **Finish.** Spacing, margins, line weights, light, and that every word is crisp and legible at
   feed size.

Save the prompt to the scratchpad and lint it:

```
python .claude/skills/linkedin-infographic-studio/scripts/lint_prompt.py check <file> --mode brand|anchored|colourful
```

It checks positive framing (outside quoted text), em dashes, emojis, pixel sizes, tool flags and
model names, the ratio in words, filler adjectives, agency or university names, the retired
`#475569`, brand hexes in brand modes, and the quoted word count. Fix and re-run until the last
line reads `LINT PASS`. `LINT DID NOT RUN` is not a pass. If the script cannot run at all, say so
plainly and do not describe the prompt as checked.

One check the script cannot do: **the swap test.** Put a different topic into the concept. If the
image would still work, the world is decoration. Rewrite before emitting.

Then output, in one message:

1. **Concept line.**
2. **The prompt**, in one code block.
3. **Paste note.** Best in Gemini (Nano Banana Pro) or ChatGPT image generation, both of which
   render dense text well. Midjourney is the weakest of the three at text, so it is a poor fit for
   an infographic. To fix a render, describe the change positively and restate that layout and
   text stay the same.
4. **A caveat only if one applies,** for example the lint's text-budget warning.

Finally append one row to `references/concept-ledger.md`: date, topic, shape, visual world, colour
mode with lead hexes, register.

## Text budget

No source measures how many rendered words current image models keep accurate at feed size, so
there is no benchmark here, only house experience. The seven fixed templates ran 4 to 12 units
with a label and one or two lines each, and the lint warns above roughly 260 quoted words. Keep
unit lines to about fourteen words. If the content needs more, cut the weakest units and say which
ones, or hand off to a multi-slide format.

## Inside post-creator (headless)

When `post-creator` calls this skill, its step-5 checkpoint is the one gate, so skip the question
round and this skill's own gate:

- Run Step 1 on the row's Simplified Source and description.
- Pick the recommended concept. Colour defaults to **brand** unless the row or Aleem says
  otherwise.
- At post-creator's checkpoint show: the concept line, the colour mode, the other two concepts in
  one line each, and the exact text by zone. Aleem can switch concept or colour there in a line.
- After his OK, run Step 4 and put the prompt in the Doc's `LinkedIn - Infographics Prompt` tab.
  Append the ledger row.

## When the input is thin or broken

- **A topic with no angle or source.** Say what is missing and offer two or three angles. Do not
  invent units or numbers and present them as Aleem's.
- **More units than fit.** Cut to the strongest and list what was cut, or hand off to
  `instagram-carousel-studio` or `content-production` (LinkedIn document carousel) when every unit
  has to appear.
- **A number the image needs but the source lacks.** Build the concept without it. An image strips
  the hedging surrounding prose would carry, so it is the worst place to launder a guess.
- **A path that does not resolve.** Say so and stop. Never reconstruct what the file might say.
- **"Use template 4", "bento like last time".** Hand off to `linkedin-infographics`.

## Rules

- **One prompt, one image.** Never a carousel or a variant set.
- **Personal brand.** No NexusPoint name or logo and no university, per `.claude/rules/`. The
  lint enforces it.
- **No emojis and no em dashes** anywhere this skill writes, the prompt included.
- **Never invent a statistic.** Every number traces to the source Aleem gave.
- **Named tools may show their real logos,** small and beside the label. Models approximate logos,
  so the label text carries the identity, never the logo alone.
- **No photorealistic depictions of real, named people.** Offer an illustration or an object.

## Boundaries

| Hand off to | For |
|---|---|
| `linkedin-infographics` | A named template, or the same fixed layout as a past post |
| `image-prompt-generator` | A single image that argues one idea with little text: a poster, a hero, a thumbnail |
| `instagram-carousel-studio` | A multi-slide Instagram set, designed fresh per post in a different world from this infographic |
| `content-production` | A LinkedIn document carousel or other multi-page format |
| `blog-images` | SVG diagrams rendered to real PNGs, where exact labels must be guaranteed |
| `brand-visual` | Changing the palette itself. This skill reads the identity file, it never edits it |

## Reference files

- `references/information-shapes.md`: the shapes, what the viewer must read off each, unit
  budgets and failure modes. Read every run.
- `references/visual-worlds.md`: inventing the visual world, the kill list, style registers,
  typography, and building brand, anchored and colourful palettes. Read when proposing concepts.
- `references/concept-ledger.md`: every infographic shipped, plus the template skill's seven
  layouts as permanently off limits. Read before proposing, append after emitting.
- `scripts/lint_prompt.py`: `check` lints a drafted prompt, `contrast` measures a colour pair.
  `set` lints a whole carousel and is used by `instagram-carousel-studio`, which also reads this
  skill's `information-shapes.md` and `visual-worlds.md`. Moving or renaming them breaks it.
- `../image-prompt-generator/references/model-playbooks.md`: the universal prompt contract and
  the vendor evidence behind it.
