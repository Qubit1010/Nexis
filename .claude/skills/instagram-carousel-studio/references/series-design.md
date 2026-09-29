# Designing the series

A carousel is the only visual format with a narrative dimension: each slide has to earn the
swipe. This file covers what makes a sequence work and how a visual world stretches across it.
It is dials and a method, not layouts, for the same reason as the infographic skill's
`visual-worlds.md`: a layout library becomes a house look within a month.

The structure rules below come from `content-advisor/references/format-specs/visual.md`, which
cites them. Most are `[K]` (craft convention from practitioner teaching), so they are
technique, not evidence. Read that file if a question goes beyond what is summarised here.

---

## 1. The arc

| Slide | Job | Fails when |
|---|---|---|
| **Cover** | One specific promise, legible at thumbnail size. A named outcome or claim, never a topic title | It is a title ("AI tips") instead of a claim, or it needs the caption to make sense |
| **Body** | One idea per slide, each ending on a line that makes the next slide worth opening | A slide exists only to set up the next one. That is the most common reason people drop at slide 2 |
| **Recap** (optional) | The whole idea on one slide, for the person who saves | It repeats body copy word for word instead of compressing it |
| **CTA** | One ask. "Save this" or a comment keyword beats a bare follow ask | It asks for three things, or it is the only slide with substance |

**Length: 7 slides at most, by Aleem's decision (2026-09-25).** For reference, content-advisor
reports 6 to 10 as the sweet spot with a steep completion drop past roughly 12 `[K]`, and Instagram
allows 20 `[practitioner]`. The cap sits at the tight end of that range on purpose: fewer, denser
slides, so every beat has to earn its place. Enough slides for the idea and no more. If the
idea needs more, it probably wants a different format.

**Breadcrumbs:** each body slide can end on a short line that teases the next, rather than a
bare "next". Use them where the sequence has real momentum, not as filler on every slide.

## 2. Genome and beats

Split every concept into two parts before writing a word of the brief.

- **The genome** is what stays fixed on every slide: the world, the palette, the type, the frame
  (margins, slide counter, handle position) and one recurring motif. It becomes the series style
  block (`series-consistency.md`). If the genome is thin, the slides drift apart. If it is too
  detailed, every slide looks identical and swiping feels pointless.
- **The beats** are what changes per slide: where in the world this slide stands, what object or
  scene carries its idea, and its text. A good beat looks different at a glance from the slide
  before it, while obviously belonging to the same set.

**The test:** put slide 3 next to slide 6. They should read as two pages of one thing, and as two
different pages.

## 3. Worlds that unfold

The infographic skill needs a world that works in one glance. A carousel needs a world that
**moves**: one where the next slide is the next place, page, step or object in the same world.
Families that naturally unfold, as seeds to depart from:

| Family | How it unfolds | Suits |
|---|---|---|
| A journey or route | each slide is the next leg or stop | sequences, processes |
| Pages of a document | each slide is the next page of a field guide, manual, case file, logbook | catalogues, how-tos |
| A comic or storyboard | each slide is the next panel of one scene | before/after, stories |
| A collection, one item at a time | each slide is the next card, specimen, exhibit, tool on a wall | lists of N |
| A teardown | each slide removes one more layer of the same object | anatomy, "what's inside" |
| Rooms or floors | each slide is the next room of one building | levels, hierarchies |
| A timeline | each slide is the next date on the same ruler | history, roadmaps |
| A match or contest | each slide is the next round | comparisons |

Borrow the specific world from the post's own domain first, as the infographic skill does. A post
about hiring unfolds as a candidate's file, one page per stage. A post about pricing unfolds as a
receipt printing line by line.

The kill list in `../linkedin-infographic-studio/references/visual-worlds.md` applies here too,
plus one carousel-specific failure: **the same card layout recoloured on every slide.** That is
a slide deck, not a carousel, and it is what the template skill already produces.

## 4. Text budget

No source measures how much rendered text current image models keep accurate at feed size. The
house convention, from the template skill and content-advisor's "fails when frames are
text-dense":

- **Cover:** the promise in about eight words, plus the handle.
- **Body:** a headline of up to about eight words and one or two short lines, roughly thirty
  words per slide at most. The lint's `set` mode warns above forty quoted words per slide.
- **CTA:** one ask, one keyword if it uses a comment trigger.

These are heuristics. If a slide needs more, split it into two slides before shrinking the type.

## 5. The frame

Decide these once, write them into the style block, and never vary them between slides:

- Where the slide counter sits ("3/8" style) and whether it appears on the cover.
- Where the handle `@aleem_uh` sits. Default: small on the cover and the CTA only, so body slides
  stay clean. State it in the brief so Aleem can change it.
- One generous margin on every edge, the same on every slide, so no text sits near a crop line.
- The recurring motif, the one element that appears on every slide and ties them together (a
  route line that continues, a page edge, a ruler, a card border).
