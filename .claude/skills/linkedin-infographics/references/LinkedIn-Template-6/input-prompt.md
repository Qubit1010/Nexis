# Per-post input — LinkedIn-Template-6 (funnel diagram)

Vertical funnel-diagram format. The whole infographic is ONE 1080x1350 image:
- **Title block:** bold centered title, a subtitle "freshness" stamp pill, three downward flow
  arrows, NexusPoint logo top-right.
- **The funnel:** one continuous tapering shape of 4-6 stacked stage bands, each a distinct color,
  each stage narrower than the last, each with a number badge + name + italic tagline.
- **Side panels per stage:** left = "Online Location" (3 bullets) + "KPIs" (3 bullets); right =
  "Strategy" (3 bullets). Panel highlight colors key to that stage's funnel color.

Best for: marketing/sales funnels, customer journey maps, hiring or onboarding pipelines,
product-led-growth funnels, any narrowing multi-stage process that needs both data and tactics
attached per stage.

Build the Gem once from `gem.md` (attach both Knowledge images). Then per post:

1. Write the title and subtitle stamp.
2. Define 4-6 stages, each narrower than the last, in the color order: lime, amber, orange, purple, pink (add teal for a 6th).
3. For each stage, write: name, italic tagline, 3 "online location" bullets, 3 KPI bullets, 3 strategy bullets.
4. Paste the single prompt below into the Gem. It renders the whole infographic in one image.

---

## SINGLE PROMPT (renders the entire infographic)

```
Generate ONE complete LinkedIn infographic as a single 1080x1350 image (4:5 portrait), matching the Knowledge reference exactly. Do NOT make a carousel, a slide deck, or multiple images. One image only.

FRAME: thin solid black border around all four edges of the canvas.
PAGE BACKGROUND: #F6F5F9 (very light lavender-white) throughout.

TITLE (large bold black, centered, wide letter-tracking): "<full title, e.g. 'The Content Marketing Funnel'>"
SUBTITLE STAMP (pale-grey rounded pill, thin black border, bold black text, centered below title): "<e.g. 'Updated for 2026'>"
FLOW ARROWS: three short thick downward chevrons in deep teal-green (#1F4B3F), centered below the stamp.
BRAND: place the NexusPoint logo (from Knowledge) small at the top-right of the title block.

---

THE FUNNEL (one continuous tapering shape, <N, 4-6> stages stacked top to bottom, each narrower than the one above):

STAGE 1 (widest, color #D6E24B with top-ellipse tint #E4EC7C):
BADGE: "1" (black rounded-square, white number)
NAME: "<Stage 1 name>"
TAGLINE (italic, black): "<short goal phrase, 3-6 words>"
LEFT PANEL "ONLINE LOCATION:" (pale-green-tint highlight label) -- 3 bullets:
  - "<bullet 1>"
  - "<bullet 2>"
  - "<bullet 3>"
LEFT PANEL "KPIS:" (pale-tint highlight label) -- 3 bullets:
  - "<bullet 1>"
  - "<bullet 2>"
  - "<bullet 3>"
RIGHT PANEL "STRATEGY:" (pale-tint highlight label) -- 3 bullets:
  - "<bullet 1>"
  - "<bullet 2>"
  - "<bullet 3>"

STAGE 2 (narrower than stage 1, color #F0B93E with top-ellipse tint #F5CD6E):
BADGE: "2"
NAME: "<Stage 2 name>"
TAGLINE: "<goal phrase>"
LEFT PANEL "ONLINE LOCATION:" -- 3 bullets: "<...>" / "<...>" / "<...>"
LEFT PANEL "KPIS:" -- 3 bullets: "<...>" / "<...>" / "<...>"
RIGHT PANEL "STRATEGY:" -- 3 bullets: "<...>" / "<...>" / "<...>"

STAGE 3 (narrower than stage 2, color #EF8B3D with top-ellipse tint #F3A868):
BADGE: "3"
NAME: "<Stage 3 name>"
TAGLINE: "<goal phrase>"
LEFT PANEL "ONLINE LOCATION:" -- 3 bullets: "<...>" / "<...>" / "<...>"
LEFT PANEL "KPIS:" -- 3 bullets: "<...>" / "<...>" / "<...>"
RIGHT PANEL "STRATEGY:" -- 3 bullets: "<...>" / "<...>" / "<...>"

STAGE 4 (narrower than stage 3, color #9A87DA with top-ellipse tint #B3A5E4):
BADGE: "4"
NAME: "<Stage 4 name>"
TAGLINE: "<goal phrase>"
LEFT PANEL "ONLINE LOCATION:" -- 3 bullets: "<...>" / "<...>" / "<...>"
LEFT PANEL "KPIS:" -- 3 bullets: "<...>" / "<...>" / "<...>"
RIGHT PANEL "STRATEGY:" -- 3 bullets: "<...>" / "<...>" / "<...>"

STAGE 5 (narrowest, color #EC6FA6 with top-ellipse tint #F191BE):
BADGE: "5"
NAME: "<Stage 5 name>"
TAGLINE: "<goal phrase>"
LEFT PANEL "ONLINE LOCATION:" -- 3 bullets: "<...>" / "<...>" / "<...>"
LEFT PANEL "KPIS:" -- 3 bullets: "<...>" / "<...>" / "<...>"
RIGHT PANEL "STRATEGY:" -- 3 bullets: "<...>" / "<...>" / "<...>"

[STAGE 6 -- include only if there is a 6th stage, color: deep teal, drop the narrowest stage above accordingly]

---

RULES: thin black frame around the whole canvas; flat #F6F5F9 background; funnel is ONE continuous tapering shape, each stage visibly narrower than the last; each band has a lighter-tint top ellipse for a 3D cylinder look; stage badges black with white numbers; taglines italic black; side-panel labels on pale tints matching their stage's color; exactly 3 short bullets per panel, each with a black right-pointing triangle bullet; thin dashed divider between each stage's full row; no handle, no footer, no CTA; all text legible at 1080x1350; no emojis; no em dashes.
One image only.
```

---

Notes:
- Fix the result with: `regenerate, same layout, change [X]` (re-renders the whole infographic).
- The taper is the most important visual element — each stage must read as visibly narrower than the one above it, or the funnel silhouette breaks.
- Bullets are short phrases, not sentences: "LinkedIn, X, YouTube" not "We post founder-led content on LinkedIn and X."
- Keep "Online Location" bullets about WHERE the activity happens (channels, content types, platforms) distinct from "KPIs" (what you measure) and "Strategy" (what you do).
- 5 stages is the sweet spot. 4 or 6 also work.
- See `example-post.md` for a fully filled example.
