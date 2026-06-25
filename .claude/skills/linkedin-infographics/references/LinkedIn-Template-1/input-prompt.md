# Per-post input -- LinkedIn-Template-1 (one single-image infographic)

Bento-grid round-up format. The whole infographic is ONE 1080x1350 image: a bold title with a teal
accent bar, then a masonry grid of ivory cards, each with a black category pill, real brand logos,
and a one-line description. Best for "N tools by use case", "N ways to X", tool stacks, framework
breakdowns.

Build the Gem once from `gem.md` (attach the Knowledge image). Then per post:

1. Decide the TITLE and the CARDS (one per category). Aim for 9-12 cards.
2. Mark which cards are WIDE (the ones with 3 tools) vs NARROW (1 tool), and how rows group.
3. Paste the single prompt below into the Gem. It renders the whole infographic in one image.

Unlike the carousel, there is no per-slide sequence. One prompt = one complete infographic.

---

## SINGLE PROMPT (renders the entire infographic)

```
Generate ONE complete LinkedIn infographic as a single 1080x1350 image (4:5 portrait), matching the Knowledge reference exactly. Do NOT make a carousel, a slide deck, or multiple images. One image only.

TITLE (top-left, heavy bold black sans, with a short teal vertical accent bar to its left):
"<N> Ways to <OUTCOME>"   e.g. "11 Ways to Increase Productivity with AI"

LAYOUT: a bento/masonry grid of warm-ivory rounded cards (thin grey border, ~16px radius) on a light warm-grey page. Mix three-up and two-up rows; put the cards that have 3 logos in WIDE slots that span the space, single-logo cards in NARROW slots. Even gutters, aligned row heights.

Each card = a black rounded pill at the top with the category name in white bold text (centered), then the real full-color brand logos of that category's tools (with a small grey label under a logo only when the logo isn't self-evident), then a 1-2 line small grey description at the bottom.

CARDS (render every one inside the single image):

1. PILL: "<Category 1>"  [FEATURED — use teal pill text]
   LOGOS: <Tool A>, <Tool B>
   DESC: "<one-line plain-English description>"

2. PILL: "<Category 2>"
   LOGOS: <Tool C>
   DESC: "<one-line description>"

3. PILL: "<Category 3>"
   LOGOS: <Tool D>, <Tool E>, <Tool F>   [WIDE card]
   DESC: "<one-line description>"

<...repeat the numbered CARD block for each category, ~9-12 total. Tag the 3-logo ones [WIDE].>

BRANDING: place the NexusPoint logo (from Knowledge) small (~80-100px tall) at the top-right of the page, above the card grid. No handle or footer at the bottom.
RULES: real recognizable brand logos in full color; all text legible at 1080x1350; ivory cards, black pills, teal accent only on the title bar and the one featured pill; no emojis; no em dashes.
One image only.
```

---

Notes:
- Fix the result with: `regenerate, same layout, change <X>` (re-renders the whole infographic).
- 9-12 cards is the legibility sweet spot. More than that = shrink-to-illegible; cut items instead.
- Wide cards (3 logos) balance the grid against narrow single-logo cards — always include a couple.
- The featured (teal-text) pill is optional; default it to the first card.
- See `example-post.md` for a fully filled example.
