# Per-post input -- LinkedIn-Template-2 (tiered horizontal bands infographic)

Progression/comparison format. The whole infographic is ONE 1080x1350 image: a bold title +
subtitle, then three stacked horizontal bands (lightest to darkest green) each with a left metric,
a center flowchart, and a right three-point explanation, plus a full-width tools footer. Best for:
level guides, maturity frameworks, "3 approaches to X", beginner-to-advanced progressions.

Build the Gem once from `gem.md` (attach both Knowledge images). Then per post:

1. Define the TITLE, SUBTITLE, and three TIERS — simplest at top, most advanced at bottom.
2. For each tier: the metric label, a diagram description, and the three explanation points.
3. List the TOOLS for the bottom section (3-6 per column).
4. Paste the single prompt below into the Gem. It renders the whole infographic in one image.

Unlike the carousel, there is no per-slide sequence. One prompt = one complete infographic.

---

## SINGLE PROMPT (renders the entire infographic)

```
Generate ONE complete LinkedIn infographic as a single 1080x1350 image (4:5 portrait), matching the Knowledge reference exactly. Do NOT make a carousel, a slide deck, or multiple images. One image only.

TITLE (top-left, ultra-heavy bold black sans):
"<Title — e.g. '3 Levels of AI Automation'>"

SUBTITLE (below title, smaller regular sans, dark grey):
"<Subtitle — e.g. 'The guide every business owner needs to choose the right approach'>"

LAYOUT: three full-width horizontal bands stacked top to bottom, graduating from very light mint (top) to medium green (middle) to sage green (bottom). Each band has: a bold metric label to the left, a schematic flowchart in the center, and a three-point explanation panel on the right. Below all three bands, a full-width light-green tools section.

---

TIER 1 (top band — lightest green #E8F5E3):
METRIC: "<outcome/metric — e.g. '10x Faster Prototype'>"
TIER NAME: "<tier label — e.g. 'Vibe-Coding'>"
LEVEL BADGE: "Level: <audience — e.g. 'Non-Tech'>"
DIAGRAM: <describe the flowchart — e.g. "4 circular steps connected in a loop: 1. Describe Vision → 2. Generate Interface → 3. Working Code → 4. Test & Iterate">
EXPLANATION:
  1 What is <Tier Name>: <one-sentence definition>
  2 How it works: <one-sentence mechanism>
  3 When to use it: <one-sentence use case>

TIER 2 (middle band — medium green #B8DDB0):
METRIC: "<outcome/metric>"
TIER NAME: "<tier label>"
LEVEL BADGE: "Level: <audience>"
DIAGRAM: <describe the flowchart/dependency diagram>
EXPLANATION:
  1 What is <Tier Name>: <one-sentence definition>
  2 How it works: <one-sentence mechanism>
  3 When to use it: <one-sentence use case>

TIER 3 (bottom band — sage green #8CC484):
METRIC: "<outcome/metric>"
TIER NAME: "<tier label>"
LEVEL BADGE: "Level: <audience>"
DIAGRAM: <describe the flowchart/dependency diagram>
EXPLANATION:
  1 What is <Tier Name>: <one-sentence definition>
  2 How it works: <one-sentence mechanism>
  3 When to use it: <one-sentence use case>

---

TOOLS SECTION (full-width light-green strip at the bottom):
Header: "Tools and Products to Use"
Column 1 — <Tier 1 name>: <Tool A>, <Tool B>, <Tool C> [list real brand names]
Column 2 — <Tier 2 name>: <Tool D>, <Tool E>, <Tool F>
Column 3 — <Tier 3 name>: <Tool G>, <Tool H>, <Tool I>

---

BRANDING: place the NexusPoint logo (from Knowledge) small (~80-100px tall) at the top-right of the title block. No handle or footer at the bottom.
RULES: graduated green bands (lightest top, darkest bottom); schematic diagrams only, not screenshots; real brand logos in full color in the tools section; all text legible at 1080x1350; no emojis; no em dashes.
One image only.
```

---

Notes:
- Fix the result with: `regenerate, same layout, change [X]` (re-renders the whole infographic).
- Three tiers only — the template is not designed for 2 or 4.
- Top tier = simplest/most accessible (lightest color). Bottom tier = most advanced (darkest).
- Keep diagram descriptions simple and schematic — flowchart nodes/arrows, not detailed diagrams.
- 3-6 tools per column in the footer keeps logos legible.
- See `example-post.md` for a fully filled example.
