# Prompt craft — the dimensions

This file is a set of **dials, not designs.** It exists so a prompt can be composed from scratch
with precision, and it is deliberately organised by dimension rather than by finished look. The
moment it starts containing layouts, it has become the template library this skill was built to
avoid, and the outputs will start converging on a house style.

Read it when a concept needs building out, or when a style register has to be turned into words a
model can act on.

---

## 1. Find the argument before the picture

A prompt is only as good as the thing it is trying to say. Before any visual vocabulary, get this:

**What would a reader disagree with?** Not the subject, the claim. "A marketing brief" is a
subject. "The brief is the machine, discipline is not" is a claim, and a claim has shape: an input,
a mechanism, an output.

Three questions that reliably turn a topic into a drawable claim:

- **What changes?** Before and after, chaos and order, scattered and routed. Change is the easiest
  thing to draw and the easiest to read.
- **What is the mechanism?** If the topic describes a process with named parts, the parts and their
  relationship *are* the image.
- **What is the one number?** A real figure from the source anchors an image and makes it specific
  to this piece rather than reusable filler. Never invent one to get the effect.

## 2. Choose a metaphor with parts

The strongest concepts are **mechanisms**, because a mechanism can be read. A mood cannot.

Families that carry meaning, offered as starting points to depart from rather than a menu to pick
from:

| Family | Reads as |
|---|---|
| Routing and switching | one input becoming many outputs, deliberately |
| Assembly line or conveyor | sequence, and what happens at each stage |
| Filling or accumulation | progress against a total, compounding |
| Balance, scale, gauge | comparison, and the reading that means nothing |
| Nested containment | layers, and the one that is missing or incomplete |
| Diverging paths | a choice and its consequence |
| Signal against noise | the thing that matters inside the thing that does not |
| Growth from a seed | one input, sustained, becoming structure |

**The test:** if the topic were swapped for an unrelated one and the image would still work, the
metaphor is decoration. Start again.

**The other test:** if this is structurally the same image as the last one produced, change it. No
ledger enforces this. It is a matter of noticing.

## 3. Style registers, translated

The register the user picks is an abstraction. Models need concrete words. These are vocabularies
to draw from and recombine, not four fixed looks.

**Minimal and restrained**
Flat shapes, generous negative space, a single accent, thin consistent linework, one or two type
weights, no texture. Words that carry it: *clean geometric*, *flat vector*, *generous negative
space*, *restrained*, *single accent colour*, *orthographic*, *precise thin linework*. Fails when it
becomes empty rather than quiet, so it needs one element with real presence.

**Editorial illustration**
The register of a good magazine or a premium software blog. Conceptual rather than literal, colour
doing real work, a visible point of view. Words: *editorial illustration*, *conceptual*, *bold
colour-blocked shapes*, *subtle grain texture*, *considered composition*, *print-like*. This is
usually the right default for an article-accompanying image.

**Bold and maximalist**
Saturation, density, energy, layering, scale contrast. Words: *vivid*, *high contrast*, *dynamic
diagonal composition*, *layered depth*, *dramatic scale shift*, *energetic*. The risk is noise, so
pair it with one clear focal point or it reads as chaos rather than intensity.

**Photographic or 3D render**
Real-world optics. Words: *shallow depth of field*, *f/1.8*, *soft directional window light*,
*shot on medium-format*, *pronounced grain*, *studio backdrop*, *macro detail*, or for render:
*soft studio lighting*, *matte materials*, *subtle ambient occlusion*. Note that this brand's own
doctrine prefers diagrams over photographs, so choosing this for Aleem's own content is a
deliberate departure worth naming.

## 4. Composition dials

Set these consciously rather than letting the model decide:

- **Shot type** — extreme close-up, macro, medium, wide, establishing. The single biggest lever on
  how the image feels.
- **Camera position** — eye level, low angle looking up, top-down flat lay, three-quarter.
- **Where the subject sits** — centred and symmetrical reads as stable and formal; off-centre with
  weight on one side reads as dynamic; rule-of-thirds is the safe middle.
- **Where the empty space is** — say it explicitly if a headline is going to be laid over the image
  later. "Clear negative space in the upper third" is a real instruction.
- **Depth** — foreground, midground, background as separate named layers, or deliberately flat.
- **Reading direction** — left to right for before and after, top to bottom for a hierarchy or
  pipeline, centre-out for a hub.

## 5. Light and colour

**Light** carries mood more than colour does. Named options: soft diffused, hard directional with
defined shadows, rim lighting, backlit and silhouetted, flat even light with no shadow (correct for
most flat-vector work), golden low sun, cool overcast.

**Colour approaches**, once the direction is chosen:

- **Anchored** — one dominant hue plus one accent, everything else neutral. Reliable, and the
  closest to how the brand system already works.
- **Analogous** — neighbours on the wheel, harmonious, calm.
- **Complementary** — opposites, high tension, best used sparingly on the focal point.
- **Progression** — colour shifting across the frame to carry a sequence or a transition. Strong
  when the concept is a change over stages.

State colours as **named hues plus a hex where precision matters.** Models handle "deep teal
(#0F766E)" better than "teal", and hexes are required whenever the brand palette is in play.

## 6. Text inside the image

Current models render text well (see `model-playbooks.md`), so the constraint is design, not
capability.

- Put the literal string **in quotes** in the prompt, and say where it sits and what weight it is.
- Keep it to a headline and, at most, a few labels. Paragraphs are unreadable at feed scale
  regardless of whether the model spells them correctly.
- If the design needs precise typography in a specific typeface, generate the art without the type
  and set the type afterwards. That is a legitimate answer, not a failure.

## 7. The kill list

These make an image read as machine-made stock, instantly. Never reach for them, and steer away if
a user's description implies one:

- Glowing brains, humanoid robots, robot hands touching screens, brains made of circuitry
- Circuit-board textures used as generic "tech" wallpaper
- Blue holographic HUD overlays, floating translucent UI panels, binary rain
- Handshakes, lightbulb-equals-idea, jigsaw pieces fitting, ladders and staircases to success
- Arbitrary lens flare, glow, bloom, drop shadows used as decoration
- Faux-3D isometric where flat would carry the same information
- Stock-photo people in offices pointing at charts

The underlying principle: **anything that could illustrate any topic is illustrating none of them.**

## 8. Assembling the prompt

Once the dials are set, order the pieces the way the target model wants them
(`model-playbooks.md`), and make every clause a decision rather than an adjective. A useful check
before emitting: read each phrase and ask whether a different, defensible choice existed. If not,
the phrase is filler. "High quality, beautiful, 4k, masterpiece" fails this on all four counts and
should never appear.
