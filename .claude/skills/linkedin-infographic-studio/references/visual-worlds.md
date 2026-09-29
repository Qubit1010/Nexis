# Visual worlds, style and colour

This file is **dials and a method, not designs.** It exists so each infographic can be invented
from its own content. The day it starts holding finished layouts, it has become the template
library this skill replaced, and the output will converge on a house look within a month.

---

## 1. What a visual world is

A visual world is a real object or system whose **own structure already encodes the shape**, so
the metaphor carries information instead of decorating it.

- A transit map already means "stops in order, with interchanges". Put a sequence on it and the
  reader knows how to read it before reading a word.
- A spec sheet already means "the same attributes, measured side by side". A comparison fits it.
- A specimen drawer already means "a collection, sorted into kinds". A catalogue fits it.

**The mapping test:** name what each part of the world stands for. Stations are steps, the
interchange is the handoff, the terminus is the outcome. If a part of the world maps to nothing,
or a unit has nowhere to live, the world is wrong for this content.

**The swap test:** replace the topic with an unrelated one. If the image would still work, the
world is decoration. Start again.

## 2. Where good worlds come from

In order of how reliably they produce something unswappable:

1. **The subject's own domain.** A post about AI for restaurants lives on a kitchen ticket rail.
   A post about hiring lives on a job board or a scouting report. A post about pricing lives on a
   receipt or a menu board. Borrowing the world from the domain makes it impossible to reuse.
2. **The reader's working day.** Things founders and operators handle constantly: an invoice, a
   calendar week, a boarding pass, a dashboard gauge, a shipping label, a sticky-note wall, a
   terminal window, a changelog, an org chart, a receipt, a checklist on a clipboard.
3. **A well-known designed system.** Transit maps, periodic tables, field guides, instruction
   manuals, board games, trading cards, nutrition labels, weather maps, blueprints, sheet music,
   a stock ticker, a scoreboard, a museum label, a seed packet.

These are seeds to depart from, not a menu. The best world is usually one you would not have
listed in advance because it came out of this specific post.

**World intensity is a dial.** Full immersion (the whole infographic *is* a board game) is
memorable but costs legibility. A structural nod (a clean layout whose connector lines are drawn
as a transit line with station dots) keeps text easy to read. Dense reference sheets want the
nod. Scannable opinion pieces can afford immersion.

## 3. Kill list

These read as "AI-generated infographic" on sight. Steer away, even when the post seems to invite
them:

- **A grid of identical rounded cards.** This is the bento look the template skill already
  produces and the single most common AI infographic. A grid is fine when the world is a grid (a
  periodic table, a specimen drawer, a calendar). A grid of interchangeable tiles is not a world.
- Glowing brains, humanoid robots, robot hands, circuit-board wallpaper, holographic HUD panels.
- Rockets for growth, lightbulbs for ideas, puzzle pieces for fit, gears for process, targets for
  goals, a summit flag for success, an iceberg for "hidden", a staircase for progress.
- Purple-to-blue gradients on dark with neon glow, the default "tech" palette.
- Isometric 3D blocks where a flat diagram carries the same information.
- Icon soup: a generic icon beside every line, adding nothing the label did not say.

## 4. Style register

Pick one and describe it in concrete words, because "modern and clean" is not an instruction a
model can act on.

| Register | Words that carry it | Suits |
|---|---|---|
| Flat vector, Swiss | flat geometric shapes, strict grid, bold grotesque type, generous white space | reference sheets, anything dense |
| Editorial illustration | conceptual illustration, colour-blocked shapes, subtle print grain, magazine spread | opinion posts, one strong argument |
| Technical drawing | blueprint linework, thin precise strokes, annotation callouts, dimension lines | anatomy, systems, how it works |
| Hand-made | sketchnote marker lines, paper texture, hand-lettered labels | process and story posts, a warmer register |
| Print and retro | risograph two-colour overprint, halftone dots, vintage manual or poster | catalogues, playful takes |
| Tactile 3D | matte clay or paper-cut layers, soft studio light, shallow depth | scannable posts with few words |
| Interface | a realistic app, terminal or dashboard screen, crisp UI type | posts about software and workflows |

Dense text wants a flatter register. The more texture and depth, the fewer words it can carry
legibly.

## 5. Typography

Name the type by character, not by font file, since the image model will not have the font:
"a heavy condensed grotesque for the headline, a clean geometric sans for labels, a monospace for
numbers". Set a clear hierarchy of at most three levels: headline, unit labels, supporting lines.
The headline should be readable at thumbnail size, because that is how the feed first shows it.

## 6. Colour

### Brand (strict)

Read `agency/personal-brand-visual-identity.md` live. Pure black ground `#000000`, `#101010`
surfaces, `#1D1E1F` hairlines, white `#FFFFFF` headline, `#CCCCCC` labels, `#8A8A8A` captions,
`#5A5A5A` for non-text UI only. `#02A1E1` marks **the one accent subject** and nothing else.
Text sitting on a `#02A1E1` fill must be black, because white on it is 2.92:1 and fails.

### Brand-anchored

The same black ground and the same single `#02A1E1` accent subject, plus two supporting hues for
categories or states. Choose supporting hues that sit well beside cyan on black (a warm amber,
a soft coral, a mint) and keep them less saturated than the accent so the hierarchy survives.

### Unique and colourful

Invent the palette for this post. A palette that belongs to the world is the strongest: a transit
map has its line colours, a seed packet its botanical inks, a risograph its two overprint inks.
Otherwise build it from a logic:

- **Ground**: light (cream, paper, pale tint) or dark (deep ink, not pure black, which is the
  brand's). Light grounds carry dense text more easily.
- **Ink**: one near-black or near-white for body text.
- **Hues**: three to five, with a reason. Analogous for calm, complementary for tension, a
  progression across the image when the shape is a sequence or levels.
- **Accent subject**: the most saturated hue, or the one that contrasts with everything else.

Check every text and fill pair before it goes in the blueprint:

```
python .claude/skills/linkedin-infographic-studio/scripts/lint_prompt.py contrast "<text hex>" "<fill hex>"
```

4.5:1 for body text, 3:1 for large headlines. Change the pair until it passes, rather than noting
the failure. Then check the ledger: a colourful palette should not repeat the previous colourful
row's ground and lead hue.
