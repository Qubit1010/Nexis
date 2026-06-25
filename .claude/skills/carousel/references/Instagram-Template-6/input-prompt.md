# Per-post input — Instagram-Template-6 (one detailed prompt per slide)

Resource/tool showcase format. Each body slide = one named resource with a screenshot, structured
info cards, and a metric. Best used for: top-N tool lists, GitHub repo showcases, AI skill packs,
plugins, frameworks, or any content where each slide presents one specific resource.

Build the Gem once from `gem.md` (attach the 4 Knowledge images). Then per post:

1. Paste **CONTEXT** (sets the series + identity, no image generated).
2. Paste **COVER** — the carousel title card.
3. Paste one **BODY** prompt per resource slide. Each body slide = one tool/resource.
4. Paste **CTA** for the last slide.

Attach a screenshot of the resource (website, GitHub, app) in the chat right before each body slide.

---

## CONTEXT (paste first, no image)

```
We are building an <N>-slide Instagram carousel in the Template-6 style (match the Knowledge reference images). I will send ONE detailed prompt per slide; generate ONE 1080x1350 image per prompt. Do not generate anything yet, do not tile slides, do not build a slide deck.

Topic: <what the carousel is showcasing — e.g. "Top 4 AI automation tools for agencies">
Each body slide presents one resource with a device mockup screenshot, name/category/creator info cards, and a metric.
Handle: @<HANDLE>
Comment trigger (used in CTA): "<KEYWORD>"
Category label for cover top bar: "<CATEGORY e.g. AI TOOLS / AUTOMATION / DESIGN>"

Reply with a one-line confirmation and a numbered slide plan, then wait for my per-slide prompts.
```

---

## COVER (slide 1)

```
Slide 1 of <N> — COVER. Generate ONE 1080x1350 image only.
Style: rounded card frame (~32px corners). Soft sage/teal gradient background (#A8C4BC at top) with a large dark forest-green (#2D4A3E) organic arc/wave shape sweeping across the bottom ~35% of the canvas.
Top bar: left = small circular badge icon + "@<HANDLE>" monospace grey; right = "<CATEGORY>" uppercase monospace grey.
Center headline (heavy bold rounded sans, white, 2 lines, centered): "<LINE 1>" / "<LINE 2>"
Sub-label (casual handwritten, near-black, centered below headline): "<Collection / Starter Pack / for founders / etc.>"
Below sub-label: finger-point/swipe icon + "Swipe for start" in casual handwritten, near-black.
Bottom bar: left = "SUBSCRIBE FOR MORE" monospace grey; right = "SAVE FOR LATER ->" + bookmark icon monospace grey.
One image only.
```

---

## BODY (repeat for each resource slide, increment slide number)

```
Slide <N> of <TOTAL> — BODY. Generate ONE 1080x1350 image only.
Style: rounded card frame. Dark charcoal (#1A1A1C) background.
Top bar: left = "<RESOURCE URL e.g. GITHUB.COM/USER/REPO or TOOL.COM>" uppercase monospace grey; right = "SWIPE ->" + finger icon monospace grey.
Hero (upper ~55%): large dark rounded device/iPad mockup frame, centered, containing a screenshot of <describe what the screenshot shows: the tool homepage / GitHub README / app interface>.
Info cards (lower ~45%): two side-by-side rounded dark cards (#242426):
  Left card:
    "<NAME LABEL e.g. TOOL NAME / SKILL NAME>" grey monospace label
    "<RESOURCE NAME>" bold white large
    "<CATEGORY LABEL e.g. CATEGORY / TYPE>" grey monospace label
    "<CATEGORY VALUE>" regular white
    "<CREATOR LABEL e.g. AUTHOR / CREATOR / TEAM>" grey monospace label
    "<CREATOR NAME(S)>" regular white
  Right card:
    "DESCRIPTION" grey monospace label
    "<description, ~25 words, regular light grey text>"
Below cards: "<METRIC LABEL e.g. GITHUB STARS / USERS / PRICE / RATING>" grey monospace label on left; "<VALUE>" in dark rounded pill with relevant icon on right.
One image only.
```

---

## CTA (last slide)

```
Slide <N> of <N> — CTA. Generate ONE 1080x1350 image only.
Style: rounded card frame. Vertical gradient from near-black (#0D0D0F) at top to dark slate/blue-grey (#2A3850) at bottom.
Top-left: small circular badge icon.
Center upper: "<TEASER QUESTION e.g. Want all the links?>" in casual handwritten font, white, centered, 1-2 lines.
Center: "Comment" in casual handwritten + small curved arrow pointing down, white.
Large pill (rounded rectangle, dotted/pixelated border, #E8E8E8 fill): "<KEYWORD>" in retro pixelated LCD monospace font, near-black.
Below pill: "and we'll DM you <PAYOFF>" in casual handwritten, white, large, centered, 2-3 lines.
Dashed separator line full width.
Below separator: "Follow @<HANDLE> for more" + globe icon + "@<HANDLE>" underlined, casual handwritten, white.
Bottom bar: left = "SUBSCRIBE FOR MORE" monospace grey; right = "SWIPE ->" monospace grey.
One image only.
```

---

Notes:
- Fix any slide with: `regenerate slide N, same style, change <X>`.
- Attach a real screenshot of each tool before its BODY prompt for the most accurate device mockup.
- The BODY info card labels are fully flexible -- swap SKILL NAME / AUTHOR to TOOL NAME / CREATOR, PRICE / PLATFORM, etc. to match your content type.
- See `example-post.md` for a fully filled 6-slide set.
