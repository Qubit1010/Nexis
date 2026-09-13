---
name: image-prompt-generator
description: Writes one universal image-generation prompt from any topic, composed fresh for the subject instead of filled into a template, and phrased to work in ChatGPT, Gemini, Midjourney or anywhere else without rewriting. Asks colour, style and format first. Say "image prompt for X", "poster prompt for X". For fixed-layout social sets use carousel, linkedin-infographics or shorts-creator; for authored SVG diagrams, blog-images.
---

# Image Prompt Generator

Turns a topic, a pasted brief, or a finished article into **one image-generation prompt**, written
for whichever model the user is actually going to paste it into. The output is text. This skill
never calls an image API and never renders a file.

## Why this exists, and the one rule that defines it

Three sibling skills already emit image prompts, and all three map content into a **fixed
pre-authored layout**: `linkedin-infographics` (bento grid), `carousel` (slide set),
`shorts-creator` (9:16 branded frames). They are the right tool when the user wants that exact
look again.

This skill exists for the other case, and it was created the day Aleem was offered a template for a
blog poster and said: *"I dont want to use existing templates just use your own imagination."*

**So: never reach into another skill's `references/*Template*` directory, and never build a house
template of your own.** Compose the concept from scratch for the topic in front of you.
`references/prompt-craft.md` gives you *dimensions* to compose along, deliberately not layouts. If
you ever catch yourself producing structurally the same image for two different topics, the skill
has failed at the only thing that makes it distinct.

## Auto-start on load

Go straight to Step 1. Do not summarise the skill back to the user.

## Step 1. Read the input and form a recommendation

The input is a topic, a description, a pasted brief, or a path to an article. If it is a file, read
it. What you are looking for:

- **The one thing the image should argue**, not the subject it is about. "AI automation" is a
  subject. "The brief is the machine, not the discipline" is an argument, and it is drawable.
- **A concrete anchor** — a number, an object, a before/after, a process with named stages. Images
  that argue something specific beat images that decorate a theme.
- **Where it is going** — a LinkedIn feed post, a blog hero, a client deck, an ad. This drives
  format and how much visual noise is acceptable.

Then form an opinion on all four interview axes below *before* asking. The interview confirms your
reading; it is not a blank questionnaire handed to the user. If you have no opinion, you have not
read the input closely enough.

## Step 2. The interview — one batched round

Ask all three axes in a **single `AskUserQuestion` call**, with your inferred pick listed first and
marked `(Recommended)`. One round, usually one or two clicks, every time.

There is deliberately **no "which model" question**. The prompt this skill writes is universal, so
asking would be asking the user to make a choice that changes nothing.

| Axis | Options to offer |
|---|---|
| **Colour** | Brand-strict · Brand-anchored · Free palette for the topic · A palette the user names |
| **Style register** | Minimal and restrained · Editorial illustration · Bold and maximalist · Photographic or 3D render |
| **Format** | 1:1 square · 4:5 portrait feed · 9:16 vertical · 16:9 wide |

Tailor the option *descriptions* to the actual topic so the choice is concrete. "Editorial
illustration" means little on its own; "editorial illustration, the brief drawn as a machine that
sorts chaos into order" is a decision the user can actually make.

**Do not add a fourth question.** These three change the output structurally. Everything else you
infer and *state*, so it can be corrected in one line:

- **Text inside the image** — default to a short headline or a few labels at most. Current models
  handle text far better than they used to (see `model-playbooks.md`), so the old "avoid all text"
  advice is retired. Dense paragraphs are still a bad idea, for legibility reasons rather than
  model ones.
- **Literal or conceptual** — inferred from the topic and declared in the concept line.
- **Mood, lighting, detail density** — these ride on the style register.

### When the answers conflict, say so

The most common collision: **brand-strict plus "make it colourful."** Both brand systems are a
black ground with a single blue accent, by design. Those two asks cannot both be honoured.
Name the conflict in one line and recommend brand-anchored, which keeps the brand hue as the anchor
and lets the rest of the palette open up. Silently splitting the difference produces the muddy
middle that satisfies neither.

## Step 3. Read the palette, if the answer calls for it

Only when the user picks **brand-strict** or **brand-anchored**, read the palette. **Which file
depends on whose brand it is, and getting this wrong is the likeliest mistake in this step:**

| The work is | Read | Ground | Accent |
|---|---|---|---|
| Aleem's own blog, LinkedIn, Instagram, aleemuh.com | `agency/personal-brand-visual-identity.md` | `#000000` | `#02A1E1` |
| NexusPoint, agency or client-facing | `agency/15-brand-visual-identity.md` §3 | `#02040A` | `#A6DAFF` |

They share no hex values, so mixing them is immediately visible. Most requests here are personal
brand, so default to that file unless the work is explicitly agency or client.

Read the hexes live rather than copying them into this skill. That is not fussiness: this repo has
already run three conflicting palettes at once (the agency file documents them), and a copied-out
table here would quietly become one more.

Two things to carry through:

- In the **agency** palette, `#475569` is **retired** (2.71:1, fails every floor). Never emit it.
- The **personal** palette has no muted grey of its own. Use the two derived values that file
  names (`#8A8A8A` text, `#5A5A5A` non-text UI) rather than inventing one.
- The accent is for the single subject under discussion. If more than one thing in the image carries
  it, the hierarchy has failed.

## Step 4. Compose the concept

Invent the visual metaphor for this topic. A good one is a **mechanism, not a mood**: something with
parts that relate, so a viewer can read the argument off the picture. Chaos resolving into order,
one input fanning into many outputs, a level scale, a filling grid, a dashed ring where a layer
should be solid.

Check the concept against three failure modes before writing the prompt:

- **Decoration.** If swapping the topic for a different one would leave the image unchanged, it is
  filler. Start again.
- **Cliché.** Glowing brains, robot hands, humanoid robots at desks, circuit-board textures, blue
  holographic HUDs. These read as "AI-generated stock" instantly.
- **Repetition.** If it is the same structure you used for the last topic, change it.

## Step 5. Emit

Output in this order, in one message. There is **no stop-and-wait approval gate** here, and that is
deliberate: the sibling skills gate because regenerating a dense infographic is expensive, whereas
regenerating a prompt costs nothing. The interview already captured the expensive decisions. If a
future editor is tempted to add a gate, this paragraph is why they should not.

1. **Concept line.** One or two sentences: what the image shows and what it argues. This is what the
   user redirects against if the metaphor is wrong.
2. **One prompt**, in a single code block, built to the universal contract in
   `references/model-playbooks.md`. One prompt, not one per model. It should paste into ChatGPT,
   Gemini, Midjourney or anything else and work without editing.
3. **The fix line.** How to iterate, in one sentence: describe the change as what you want to see
   rather than what you want removed, and restate the composition so it does not drift.
4. **A caveat only if it applies** — for example, if the image carries enough text that legibility
   is the binding constraint, or the format is unusual enough that some tools will letterbox it.

Do not append a Midjourney parameter strip, a pixel-dimension line, or a "for ChatGPT use this
instead" variant. If a user is on Midjourney and wants flags, they can add `--ar` themselves; the
prompt body is already correct for it.

## Before you emit, check these

A prompt cannot be validated by looking at it, which is exactly why these need checking rather than
assuming. Each one is a specific, answerable question, so "I checked" and "I did not check" are
distinguishable. Run them against the drafted prompt:

- **Positive framing only, with no exceptions.** The prompt must contain no "no X", "without X",
  "avoid X" or "not X" anywhere. This is the single rule that makes one prompt work everywhere, and
  it is the easiest to break by reflex. Every exclusion has to be rewritten as the desired state:
  "a clean unbroken background" rather than "no watermark", "an empty street" rather than "no cars".
- **No model-specific syntax.** No `--ar`, no `--no`, no `--style`, no pixel dimensions, no
  "gpt-image" or "Nano Banana" mentioned in the prompt body. Any of these means it stopped being
  universal.
- **Aspect ratio stated in words**, as "vertical 4:5 portrait" or "wide 16:9", never as pixels or a
  flag. Every tool understands the words; only some understand the other two.
- **If brand colours were chosen, real hexes from the right identity file appear**: the personal
  file for Aleem's own work, `15` §3 for agency or client work. `#475569` appears in neither.
- **The swap test.** Substitute a different topic into the concept. If the image would still work,
  it is decoration. Rewrite before emitting, do not ship it and hope.
- **No invented facts.** Every number or claim rendered in the image traces to the user's source.

If a check fails, fix the prompt. Do not emit it with a note apologising for the flaw.

## When the input is thin or broken

- **A one-word topic with no angle.** Say what is missing and offer two or three candidate angles
  to pick from. Do not invent a claim and present it as though it came from the user.
- **A file path that does not resolve.** Say so and stop. Never reconstruct what you assume the
  article said.
- **A topic that needs a number you were not given.** Build the concept without it. The rule against
  invented statistics is absolute, and an image is a uniquely bad place to launder a guess, because
  it strips the hedging that surrounding prose would have carried.
- **A request for a sequence rather than one image.** Name the right skill and hand off.

## Rules

- **One prompt, one image.** Not a carousel, not a deck, not a variant set. If the topic genuinely
  needs a sequence, say so and hand off to `carousel` or `shorts-creator`.
- **No agency branding in personal-brand work.** Never put "NexusPoint", a logo, or Aleem's
  university into a prompt for his own LinkedIn, Instagram or blog imagery. Client work uses the
  client's brand, and `shorts-creator` is a deliberate agency-attributed exception. This one is not.
- **No emojis. No em dashes** in anything you write here, prompt included. Commas or periods.
- **Never invent a statistic** to put in an image. If a number appears, it comes from the source the
  user gave you.
- **Refuse photorealistic depictions of real, named people.** Offer an illustration or an object.

## Boundaries

| Hand off to | For |
|---|---|
| `linkedin-infographics` | A dense bento-grid infographic in an established template |
| `carousel` | A multi-slide Instagram set |
| `shorts-creator` | 9:16 Reels/Shorts frames, agency-branded |
| `blog-images` | Authored SVG diagrams rendered to real PNGs, where exact labels are the payload |
| `brand-visual` | Changing the palette or type system. This skill consumes both identity files, it does not amend them |

## Reference files

- `references/model-playbooks.md` — the universal contract: the five rules that make one prompt
  work on every model, each with the per-model evidence behind it. Read it before writing.
- `references/prompt-craft.md` — the composable dimensions and the vocabulary for each. Read when
  the concept needs building out, or when a style register needs translating into concrete words.
