# Per-post input — LinkedIn-Template-10 (flat numbered card grid)

Flat numbered card format. The whole infographic is ONE 1080x1350 image: a large center-aligned
display title (big orange numeral + bold black words + small orange asterisk above), then 12 equal
white cards in a 3-column x 4-row grid. Each card has an orange circle badge (top-left, number
01-12), a bold card title, 2-3 sentence body copy (left), and a hand-drawn sketch illustration
(right). Tool logos optional bottom-right. Best for: "N things worth knowing", "N moves worth
stealing", feature showcases, tactic catalogues, capability rundowns.

Build the Gem once from `gem.md` (attach both Knowledge images). Then per post:

1. Decide the count (typically 12, can be 9) and write a punchy 2-4 word title.
2. Write 12 card entries (or 9 for a 3x3 grid). Each card: badge number, bold title, 2-3
   sentences, illustration note, optional tool logos.
3. Paste the single prompt below into the Gem. It renders the whole infographic in one image.

---

## SINGLE PROMPT (renders the entire infographic)

```
Generate ONE complete LinkedIn infographic as a single 1080x1350 image (4:5 portrait), matching the Knowledge reference exactly. Do NOT make a carousel, a slide deck, or multiple images. One image only.

TITLE BLOCK (center-aligned):
Decorative element: small orange asterisk/sunburst icon, centered, above the numeral.
Large numeral: "<COUNT>" in very large bold display type, accent orange (#D96B32), center-aligned.
Title line(s): "<TITLE WORDS>" in bold black (#1A1A1A), same display scale, center-aligned.
  (Numeral and first 1-2 title words on the same line; remaining words on line 2 if needed.)

BRAND: place the NexusPoint logo (from Knowledge) ~80-100px tall at the top-right corner of the full canvas.

PAGE BACKGROUND: #FAF6F0 (warm off-white) throughout.

CARD GRID: 12 equal white cards in a 3-column x 4-row grid, thin rounded grey borders (#E8E4DC),
white fill (#FFFFFF), equal gaps between all cards.

---

CARD 01:
BADGE: "01" (orange circle #D96B32, white text)
TITLE: "<2-4 word bold card title>"
BODY:
  "<sentence 1>"
  "<sentence 2>"
  "<sentence 3 (optional)>"
ILLUSTRATION: <brief sketch description, e.g. "hand-drawn browser window with text lines, GitHub logo overlay">
LOGOS: <comma-separated brand logos, or "none">

CARD 02:
BADGE: "02"
TITLE: "<title>"
BODY:
  "<sentence 1>"
  "<sentence 2>"
  "<sentence 3 (optional)>"
ILLUSTRATION: <sketch description>
LOGOS: <logos or "none">

CARD 03:
BADGE: "03"
TITLE: "<title>"
BODY:
  "<sentence 1>"
  "<sentence 2>"
  "<sentence 3 (optional)>"
ILLUSTRATION: <sketch description>
LOGOS: <logos or "none">

CARD 04:
BADGE: "04"
TITLE: "<title>"
BODY:
  "<sentence 1>"
  "<sentence 2>"
  "<sentence 3 (optional)>"
ILLUSTRATION: <sketch description>
LOGOS: <logos or "none">

CARD 05:
BADGE: "05"
TITLE: "<title>"
BODY:
  "<sentence 1>"
  "<sentence 2>"
  "<sentence 3 (optional)>"
ILLUSTRATION: <sketch description>
LOGOS: <logos or "none">

CARD 06:
BADGE: "06"
TITLE: "<title>"
BODY:
  "<sentence 1>"
  "<sentence 2>"
  "<sentence 3 (optional)>"
ILLUSTRATION: <sketch description>
LOGOS: <logos or "none">

CARD 07:
BADGE: "07"
TITLE: "<title>"
BODY:
  "<sentence 1>"
  "<sentence 2>"
  "<sentence 3 (optional)>"
ILLUSTRATION: <sketch description>
LOGOS: <logos or "none">

CARD 08:
BADGE: "08"
TITLE: "<title>"
BODY:
  "<sentence 1>"
  "<sentence 2>"
  "<sentence 3 (optional)>"
ILLUSTRATION: <sketch description>
LOGOS: <logos or "none">

CARD 09:
BADGE: "09"
TITLE: "<title>"
BODY:
  "<sentence 1>"
  "<sentence 2>"
  "<sentence 3 (optional)>"
ILLUSTRATION: <sketch description>
LOGOS: <logos or "none">

CARD 10:
BADGE: "10"
TITLE: "<title>"
BODY:
  "<sentence 1>"
  "<sentence 2>"
  "<sentence 3 (optional)>"
ILLUSTRATION: <sketch description>
LOGOS: <logos or "none">

CARD 11:
BADGE: "11"
TITLE: "<title>"
BODY:
  "<sentence 1>"
  "<sentence 2>"
  "<sentence 3 (optional)>"
ILLUSTRATION: <sketch description>
LOGOS: <logos or "none">

CARD 12:
BADGE: "12"
TITLE: "<title>"
BODY:
  "<sentence 1>"
  "<sentence 2>"
  "<sentence 3 (optional)>"
ILLUSTRATION: <sketch description>
LOGOS: <logos or "none">

---

RULES: warm off-white background (#FAF6F0); white cards with thin grey border (#E8E4DC); all
badges orange circles (#D96B32) with white bold number inside; card titles bold black (#1A1A1A);
body copy dark grey (#555555), 2-3 plain sentences (no bullet points); illustration is hand-drawn
outline wireframe style — thin dark lines, no fills; brand logos real and full-color, small,
bottom-right only; all text legible at 1080x1350; no emojis; no em dashes.
One image only.
```

---

Notes:
- Fix the result with: `regenerate, same layout, change [X]` (re-renders the whole infographic).
- Count is typically 12 (3x4 grid). 9 cards (3x3) also works — just use CARD 01-09.
- Illustration note is brief direction to Gemini: "hand-drawn terminal with code lines" or
  "sketch of a spreadsheet grid with rows, Excel logo overlay". Keep it concise.
- Logos are real brand logos only. Leave as "none" for abstract concepts.
- Body copy: 2-3 plain sentences, no bullet points. Short and punchy — reads in 3 seconds.
- Card titles: 2-4 words, all-caps or title case. Parallel structure makes the grid scan better.
- See `example-post.md` for a fully filled example.
