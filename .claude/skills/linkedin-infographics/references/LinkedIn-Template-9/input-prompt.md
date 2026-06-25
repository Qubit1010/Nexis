# Per-post input — LinkedIn-Template-9 (phased roadmap grid)

Phased roadmap format. The whole infographic is ONE 1080x1350 image: a bold title with the
NexusPoint logo top-right, an optional full-width hero/intro step, then 3-4 phase sections each
with a colored header bar and 3 feature cards. Each card has a step number + name in an accent-
colored header strip, a 1-2 sentence body, and an action example box at the bottom. Best for:
"N steps to X", product/feature roadmaps, phased learning paths, onboarding guides, workflow
playbooks, feature catalogues grouped by theme.

Build the Gem once from `gem.md` (attach both Knowledge images). Then per post:

1. Write a bold title (1-2 key words in orange) and a subtitle.
2. Optionally write a hero step (Step 00) for any prerequisite or setup.
3. Define 3-4 phases, each with a name, subtitle, and exactly 3 step cards.
4. For each card: step name, 1-2 sentence description, action example (a real prompt or command).
5. Paste the single prompt below into the Gem. It renders the whole infographic in one image.

---

## SINGLE PROMPT (renders the entire infographic)

```
Generate ONE complete LinkedIn infographic as a single 1080x1350 image (4:5 portrait), matching the Knowledge reference exactly. Do NOT make a carousel, a slide deck, or multiple images. One image only.

TITLE (top, bold grotesque, left-aligned):
"<full title text>"
Highlight these words in orange (#E85D1A): <list accent words>
All other title words in black (#1A1A1A). Article words ("The", "A") in regular/light weight.

SUBTITLE: "<1 line subtitle — sets context for the roadmap>"

BRAND: place the NexusPoint logo (from Knowledge) ~100-120px tall at the top-right of the title block.

PAGE BACKGROUND: #FAFAF8 (near-white) throughout.

[HERO STEP — include only if there is a prerequisite/setup step, otherwise skip this block]
HERO STEP (full-width strip below title):
STEP NUMBER: "STEP 00"
STEP NAME: "<name>"
STEP SUBTITLE: "<2-4 word subtitle>"
DESCRIPTION: "<1 sentence>"
ACTION EXAMPLE: "<command or prompt>"

---

PHASE 01 (accent: blue #3A88C5):
PHASE LABEL: "PHASE 01"
PHASE NAME: "<1-2 word theme, all-caps>"
PHASE SUBTITLE: "<short phrase — what this phase covers>"

  CARD 01:
  STEP NUMBER: "01"
  STEP NAME: "<name>"
  BODY: "<1-2 sentences>"
  ACTION LABEL: "<PASTE INTO CLAUDE / TRY THIS / EXAMPLE>"
  ACTION TEXT: "<example prompt or command>"

  CARD 02:
  STEP NUMBER: "02"
  STEP NAME: "<name>"
  BODY: "<1-2 sentences>"
  ACTION LABEL: "<label>"
  ACTION TEXT: "<example>"

  CARD 03:
  STEP NUMBER: "03"
  STEP NAME: "<name>"
  BODY: "<1-2 sentences>"
  ACTION LABEL: "<label>"
  ACTION TEXT: "<example>"

PHASE 02 (accent: orange #E85D1A):
PHASE LABEL: "PHASE 02"
PHASE NAME: "<theme>"
PHASE SUBTITLE: "<short phrase>"

  CARD 04:
  STEP NUMBER: "04"
  STEP NAME: "<name>"
  BODY: "<1-2 sentences>"
  ACTION LABEL: "<label>"
  ACTION TEXT: "<example>"

  CARD 05:
  STEP NUMBER: "05"
  STEP NAME: "<name>"
  BODY: "<1-2 sentences>"
  ACTION LABEL: "<label>"
  ACTION TEXT: "<example>"

  CARD 06:
  STEP NUMBER: "06"
  STEP NAME: "<name>"
  BODY: "<1-2 sentences>"
  ACTION LABEL: "<label>"
  ACTION TEXT: "<example>"

PHASE 03 (accent: purple #7055A0):
PHASE LABEL: "PHASE 03"
PHASE NAME: "<theme>"
PHASE SUBTITLE: "<short phrase>"

  CARD 07:
  STEP NUMBER: "07"
  STEP NAME: "<name>"
  BODY: "<1-2 sentences>"
  ACTION LABEL: "<label>"
  ACTION TEXT: "<example>"

  CARD 08:
  STEP NUMBER: "08"
  STEP NAME: "<name>"
  BODY: "<1-2 sentences>"
  ACTION LABEL: "<label>"
  ACTION TEXT: "<example>"

  CARD 09:
  STEP NUMBER: "09"
  STEP NAME: "<name>"
  BODY: "<1-2 sentences>"
  ACTION LABEL: "<label>"
  ACTION TEXT: "<example>"

[PHASE 04 — include only if there is a 4th phase, otherwise stop at PHASE 03]
PHASE 04 (accent: teal-green #2DAA84):
PHASE LABEL: "PHASE 04"
PHASE NAME: "<theme>"
PHASE SUBTITLE: "<short phrase>"

  CARD 10:
  STEP NUMBER: "10"
  STEP NAME: "<name>"
  ...

  CARD 11 / CARD 12: (same structure)

---

RULES: near-white background (#FAFAF8); cards white (#FFFFFF) with thin grey border (#E5E5E5); phase header bars solid accent color, all text white; card header strips solid accent color, step name and number in white; action boxes light-grey (#F4F4F2) with small copy icon bottom-right; all text legible at 1080x1350; no emojis; no em dashes.
One image only.
```

---

Notes:
- Fix the result with: `regenerate, same layout, change [X]` (re-renders the whole infographic).
- 3-4 phases, exactly 3 cards per phase (9-12 total steps).
- Hero step (Step 00) is optional. Include it for setup/install steps or prerequisite actions.
- Action label can be anything: "PASTE INTO CLAUDE", "TRY THIS", "EXAMPLE", "SEND THIS", etc.
- Action text is the most valuable part of each card — make it a real, copy-paste-ready example.
- Keep body descriptions to 1-2 tight sentences. The action example carries the practical weight.
- See `example-post.md` for a fully filled example.
