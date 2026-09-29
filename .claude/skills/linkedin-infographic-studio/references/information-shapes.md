# Information shapes

The shape is **how the units in a post relate to each other**. It decides the structure of the
infographic. It says nothing about how the infographic looks. That is the visual world's job
(`visual-worlds.md`), and keeping the two apart is what stops this skill turning into a template
library: a sequence can be drawn as a transit line, a recipe, a relay race or a circuit, and all
four are the same shape.

Read the post, list its units, then ask what a reader has to be able to *read off* the picture.
That requirement is the shape.

Unit budgets below are **house heuristics** from the seven fixed templates this repo already ran
(4 to 12 content units per image, cut rather than shrink). No source measures how much text
current image models render accurately at feed size, so treat them as starting points, not limits.

---

| Shape | Signal in the post | What the viewer must read off | Units | How it goes wrong |
|---|---|---|---|---|
| **Sequence** | steps, stages, "first... then", a how-to | order, and what happens at each stop | 3-8 | Steps drawn as equal boxes with arrows, so nothing says which step is the hard one |
| **Cycle** | loops, feedback, "repeat", flywheel | that the end feeds the start | 3-6 | Drawn as a sequence with a return arrow, so the loop reads as an afterthought |
| **Comparison** | "X vs Y", two tools, two approaches | where the sides differ, attribute by attribute | 2-3 sides, 3-7 rows | Two columns of prose with no aligned rows, so the reader cannot compare |
| **Transformation** | before/after, old way/new way, mistake/fix | the change, and what caused it | 2 states, 3-6 pairs | Before and after given equal weight, so the argument (the after) has no pull |
| **Levels** | maturity, beginner to advanced, tiers, stages of adoption | where the reader is now and what the next level asks | 3-5 | Levels that differ only in label, with nothing that grows or narrows between them |
| **Catalogue** | "N tools", "N ways", a list grouped by type | the grouping, then the items inside it | 6-12 | Twelve identical tiles, which is the bento grid the template skill already makes |
| **Anatomy** | "what's inside X", parts of a system, components | parts, and where each sits in the whole | 4-8 parts | Parts listed beside a picture instead of pinned onto it |
| **Funnel** | narrowing, drop-off, pipeline stages with loss | how much survives each stage | 3-6 | A decorative funnel with no quantities, so it narrows for no reason |
| **Matrix** | two axes, "it depends on A and B", 2x2 | which quadrant a case falls in, and why | 4 quadrants | Quadrants filled with text but the axes left unlabelled |
| **Timeline** | dates, history, "since 2023", a roadmap | when, and the gap between events | 4-8 | Evenly spaced events when the real gaps are the point |
| **Decision** | "if X then Y", choosing between options, triage | the question at each fork and where each answer leads | 2-4 forks | Branches that never end in an action |
| **Spectrum** | a range, "somewhere between", trade-off sliders | where things sit between two poles | 3-7 points | Points spaced evenly because nobody placed them deliberately |
| **Stat-led** | one number carries the post | the number, then what it means | 1 hero + 2-4 support | The hero number the same size as the supporting ones |
| **Network** | ecosystem, "how these connect", integrations | which nodes connect, and which node is central | 5-10 nodes | Every node connected to every other, so the hub disappears |

---

## Compound shapes

Many posts carry two shapes: a sequence where each stage has a stat, a comparison where each side
is itself a list, levels with a tool catalogue per level. Pick the **primary** shape for the
structure of the whole image and let the **secondary** shape live inside each unit. The failure is
giving both equal structural weight, which produces a grid of grids that reads as neither.

## Density

- **Scannable** (roughly 4-6 units, one line each): the post makes one argument and the image
  should land it in a glance. Most opinion and story posts.
- **Reference** (roughly 7-12 units, a label and a line each): the post is something people save.
  Tool lists, frameworks, checklists, cheat sheets.

Infer which from the post and state it in the blueprint. When the source holds more than a
reference sheet can carry, cut to the strongest units and say which were cut, or hand off to
`carousel` or `content-production` (LinkedIn document carousel) when every unit genuinely matters.

## The accent subject

Whatever the shape, one element is the point: the hard step, the winning side, the level most
readers are stuck at, the hub. In brand mode it is the only thing carrying `#02A1E1`. In a
colourful palette it is the most saturated or the only contrasting hue. If you cannot name the
accent subject, you have not found the argument yet. Go back to the post.
