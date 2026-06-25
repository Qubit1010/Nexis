# Per-post input — LinkedIn-Template-4 (numbered pattern catalogue)

Numbered pattern format. The whole infographic is ONE 1080x1350 image: a bold title with key words
in orange and the NexusPoint logo top-right, then 4-6 full-width numbered rows. Each row has a
colored number box on the left, a category label + pattern name + description + pill tags in the
center, and a schematic diagram on the right. Best for: "N patterns for X", architecture guides,
design pattern references, methodology breakdowns, "how X works" explainers.

Build the Gem once from `gem.md` (attach both Knowledge images). Then per post:

1. Write a bold 1-2 line title. Decide which 1-2 key words to highlight in orange.
2. Define 4-6 patterns — each needs: category label (2-4 words, all-caps), pattern name, 2-3
   sentence description, 3-4 use-case tag pills, and a diagram description.
3. Paste the single prompt below into the Gem. It renders the whole infographic in one image.

Unlike the carousel, there is no per-slide sequence. One prompt = one complete infographic.

---

## SINGLE PROMPT (renders the entire infographic)

```
Generate ONE complete LinkedIn infographic as a single 1080x1350 image (4:5 portrait), matching the Knowledge reference exactly. Do NOT make a carousel, a slide deck, or multiple images. One image only.

TITLE (top, ultra-heavy bold grotesque, left-aligned, 1-2 lines):
Line 1: "<first line>"
Line 2: "<second line, if needed>"
Highlight these specific words in orange (#E85D1A): <list accent words>
All other title words in black (#1A1A1A).

BRAND: place the NexusPoint logo (from Knowledge) ~120-150px tall at the top-right of the title block. Draw a thin horizontal separator line below the title block.

LAYOUT: <N> full-width numbered rows stacked below the title, all equal height. Each row: solid accent-colored number box on the left (bold white number), category label + pattern name + description + pill tags in the center-left, schematic diagram on the right. Warm cream background (#FAF6F0) throughout. Thin row separators (#E8E0D5).

---

PATTERN 01 (accent: orange #E85D1A):
NUMBER BOX: "01" white bold on orange
CATEGORY LABEL: "<2-4 words all-caps>"
PATTERN NAME: "<1-3 words bold>"
DESCRIPTION: "<2-3 sentences: what it is + how it works>"
TAGS: "<Tag 1>" | "<Tag 2>" | "<Tag 3>" [| "<Tag 4>"]
DIAGRAM: <describe the flowchart — e.g. "2 nodes connected left to right: Generator → output → Verifier, with a dashed feedback arrow looping back labeled reject/accept">

PATTERN 02 (accent: teal #0D9B8C):
NUMBER BOX: "02" white bold on teal
CATEGORY LABEL: "<category>"
PATTERN NAME: "<name>"
DESCRIPTION: "<description>"
TAGS: "<Tag 1>" | "<Tag 2>" | "<Tag 3>"
DIAGRAM: <describe the flowchart>

PATTERN 03 (accent: purple #5C5EA7):
NUMBER BOX: "03" white bold on purple
CATEGORY LABEL: "<category>"
PATTERN NAME: "<name>"
DESCRIPTION: "<description>"
TAGS: "<Tag 1>" | "<Tag 2>" | "<Tag 3>"
DIAGRAM: <describe the flowchart>

PATTERN 04 (accent: amber #E8A020):
NUMBER BOX: "04" white bold on amber
CATEGORY LABEL: "<category>"
PATTERN NAME: "<name>"
DESCRIPTION: "<description>"
TAGS: "<Tag 1>" | "<Tag 2>" | "<Tag 3>"
DIAGRAM: <describe the flowchart>

PATTERN 05 (accent: rose #C43059):
NUMBER BOX: "05" white bold on rose
CATEGORY LABEL: "<category>"
PATTERN NAME: "<name>"
DESCRIPTION: "<description>"
TAGS: "<Tag 1>" | "<Tag 2>" | "<Tag 3>"
DIAGRAM: <describe the flowchart>

[Add PATTERN 06 block with accent cycling back to orange #E85D1A if needed]

---

RULES: warm cream background (#FAF6F0) throughout; all rows equal height; number boxes form a fixed-width left column; diagrams schematic only, no screenshots; 3-6 labeled nodes max per diagram; use-case tags as rounded pills on one line; all text legible at 1080x1350; no emojis; no em dashes.
One image only.
```

---

Notes:
- Fix the result with: `regenerate, same layout, change [X]` (re-renders the whole infographic).
- 4-6 patterns. Fewer than 4 feels thin; more than 6 makes rows too short to read.
- Category labels answer "when does this apply?" in 2-4 uppercase words.
- Keep descriptions tight, 2-3 sentences. The diagram carries the visual weight on the right.
- Tags are concrete use cases (e.g. "Code review", "Parallel checks"), not abstract labels.
- Diagrams: flowchart nodes with arrows. Name each node. Keep it to 3-6 nodes total.
- See `example-post.md` for a fully filled example.
