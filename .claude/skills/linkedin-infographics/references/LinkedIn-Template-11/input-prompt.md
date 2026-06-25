# Per-post input — LinkedIn-Template-11 (two-column hybrid)

Two-column hybrid format. The whole infographic is ONE 1080x1350 image:
- **Title block:** large bold title with one key phrase in an inline coral pill, italic subtitle,
  NexusPoint logo top-right.
- **Definition row:** 3 boxes spanning full width, each defining a core concept.
- **Left column (~65%):** dark navy section header + 4-6 numbered rows. Each row has an orange
  badge, bold title, description, italic tagline, and a sketch illustration.
- **Right column (~35%):** dark navy sidebar header + 3-4 cards. Each card has an icon, bold title,
  and description.
- **Footer bar:** warm amber-beige pill banner with a quote and follow CTA.

Best for: "How I use X in my daily workflow", "N ways I use X", personal workflow breakdowns,
tool tutorials with best practices, practitioner-voice walkthroughs.

Build the Gem once from `gem.md` (attach both Knowledge images). Then per post:

1. Write the title — identify the key phrase (2-4 words) to put in the coral pill.
2. Write 3 definition boxes — one per core concept, "X =" format.
3. Write 4-6 numbered items for the left column (title + 2-sentence description + italic tagline + illustration note).
4. Write 3-4 sidebar cards for the right column (icon + title + 2-3 sentences).
5. Write a footer quote and CTA line.
6. Paste the single prompt below into the Gem. It renders the whole infographic in one image.

---

## SINGLE PROMPT (renders the entire infographic)

```
Generate ONE complete LinkedIn infographic as a single 1080x1350 image (4:5 portrait), matching the Knowledge reference exactly. Do NOT make a carousel, a slide deck, or multiple images. One image only.

TITLE (large bold display, left-aligned):
Full title: "<full title text>"
Pill phrase: wrap "<key phrase>" in an inline coral rounded pill (bg #F07560, white text). All other words bold black (#1A1A1A).
SUBTITLE (italic, grey, in parentheses): "(<subtitle text>)"

BRAND: place the NexusPoint logo (from Knowledge) ~80-100px tall at the top-right of the title block.

PAGE BACKGROUND: #FAF6F0 (warm off-white) throughout.

---

DEFINITION ROW (3 equal boxes, full canvas width, thin amber left-border #E8A020 on each):

BOX 1:
ICON: <icon description, e.g. "robot head">
LABEL: "<Term> ="
DEFINITION: "<1-2 sentence plain-English definition>"

BOX 2:
ICON: <icon description>
LABEL: "<Term> ="
DEFINITION: "<1-2 sentence definition>"

BOX 3:
ICON: <icon description>
LABEL: "<Term> ="
DEFINITION: "<1-2 sentence definition>"

---

LEFT COLUMN (~65% width):

SECTION HEADER (dark navy #1C2B3A, white text): "<N> Ways I Use <Subject>"

ITEM 1:
BADGE: "1" (orange circle #E85D1A, white)
TITLE: "<2-4 word bold title>"
DESCRIPTION: "<1-2 sentences>"
TAGLINE (italic, orange #E85D1A): "<Short punchy phrase. Ends with a period.>"
ILLUSTRATION: <hand-drawn sketch description>

ITEM 2:
BADGE: "2"
TITLE: "<title>"
DESCRIPTION: "<1-2 sentences>"
TAGLINE: "<tagline.>"
ILLUSTRATION: <sketch description>

ITEM 3:
BADGE: "3"
TITLE: "<title>"
DESCRIPTION: "<1-2 sentences>"
TAGLINE: "<tagline.>"
ILLUSTRATION: <sketch description>

ITEM 4:
BADGE: "4"
TITLE: "<title>"
DESCRIPTION: "<1-2 sentences>"
TAGLINE: "<tagline.>"
ILLUSTRATION: <sketch description>

ITEM 5:
BADGE: "5"
TITLE: "<title>"
DESCRIPTION: "<1-2 sentences>"
TAGLINE: "<tagline.>"
ILLUSTRATION: <sketch description>

[ITEM 6 — include only if there is a 6th use case, otherwise stop at ITEM 5]
ITEM 6:
BADGE: "6"
TITLE: "<title>"
DESCRIPTION: "<1-2 sentences>"
TAGLINE: "<tagline.>"
ILLUSTRATION: <sketch description>

---

RIGHT COLUMN (~35% width):

SIDEBAR HEADER (dark navy #1C2B3A, white text, gold star icon left): "Best Practices for <Subject>"

CARD 1:
ICON: <flat icon description, e.g. "folder">
TITLE: "<3-6 word title>"
DESCRIPTION: "<2-3 sentences of practical advice>"

CARD 2:
ICON: <icon description>
TITLE: "<title>"
DESCRIPTION: "<2-3 sentences>"

CARD 3:
ICON: <icon description>
TITLE: "<title>"
DESCRIPTION: "<2-3 sentences>"

[CARD 4 — include only if there is a 4th best practice]
CARD 4:
ICON: <icon description>
TITLE: "<title>"
DESCRIPTION: "<2-3 sentences>"

---

FOOTER BAR (full width, warm amber-beige #F5E8D0, rounded pill/banner shape):
QUOTE: "heart icon — <1 punchy sentence about the tool's value>"
CTA: "<Follow for more [topic] strategies>"

---

RULES: warm off-white page (#FAF6F0); two-column layout — left ~65%, right ~35%; definition row and footer bar span full width; section headers dark navy (#1C2B3A) with white text; orange badges (#E85D1A) with white numbers; italic taglines in orange (#E85D1A); sidebar icons in orange (#E85D1A); sketch illustrations hand-drawn outline style (thin dark lines, no fill); thin horizontal dividers between all items and cards; all text legible at 1080x1350; no emojis in body; no em dashes.
One image only.
```

---

Notes:
- Fix the result with: `regenerate, same layout, change [X]` (re-renders the whole infographic).
- Pill phrase is the most important visual element — choose 2-4 words that are the "hook" of the post.
- Taglines are the second most important: short, italic, orange. They should be memorable standalone phrases.
- Illustration notes are brief direction: "hand-drawn folder tree with arrows" or "sketch of a chat UI with paper airplane icon."
- Sidebar cards are practical advice, not definitions. They complement the numbered list.
- Footer CTA is the only place for a follow/subscribe line — keep it there.
- 5 numbered items is the sweet spot. 4 or 6 also work.
- See `example-post.md` for a fully filled example.
