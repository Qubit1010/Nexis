# Per-post input -- Instagram-Template-10 (one detailed prompt per slide)

GitHub repo / tool showcase format. Each body slide = one named item with a screenshot, punchy
headline, "Why it matters" summary, two tag pills, and an italic serif punchline.
Best used for: top-N plugin lists, GitHub repo roundups, open-source tool showcases, curated
resource lists where each item has a URL and a star count or metric.

Build the Gem once from `gem.md` (attach the 4 Knowledge images). Then per post:

1. Paste **CONTEXT** (sets the series + identity, no image generated).
2. Paste **COVER** -- the cinematic dark title card with 3D mascot.
3. Paste one **BODY** prompt per item slide. Each body slide = one tool/repo/plugin.
4. Paste **CTA** for the last slide.

Attach a screenshot of each item's GitHub page (or homepage) right before each BODY prompt.

---

## CONTEXT (paste first, no image)

```
We are building an <N>-slide Instagram carousel in the Template-10 style (match the Knowledge reference images). I will send ONE detailed prompt per slide; generate ONE 1080x1350 image per prompt. Do not generate anything yet, do not tile slides, do not build a slide deck.

Topic: <what the carousel showcases, e.g. "Top 4 open-source AI automation repos for agencies">
Each body slide presents one <ITEM TYPE: plugin / repo / tool / skill / resource> with a screenshot, punchy headline, "Why it matters" body text, two tag pills, and an italic serif punchline.
Handle: @<HANDLE>
Comment trigger (used in CTA): "<KEYWORD>"
CTA payoff: "<what they receive, e.g. the full list with install guides>"
Total slides: <N>

Reply with a one-line confirmation and a numbered slide plan, then wait for my per-slide prompts.
```

---

## COVER (slide 1)

```
Slide 1 of <N> -- COVER. Generate ONE 1080x1350 image only.
Background: deep navy (#080E1C), no gradient -- flat dark.
Center: large 3D fluffy/plush mascot character adapted to <TOPIC> -- warm orange studio lighting from below, subtle sparkle particles, fills upper ~60% of canvas.
<Describe the mascot: e.g. "a soft rounded robot with glowing circuit-board eyes" or "a fluffy cube creature with lightning-bolt pupils" -- match the plush/3D aesthetic of the Knowledge cover.>
Top-right: "01 / <N> ->" small white monospace.
Bottom headline (ultra-heavy bold sans, 2 lines, left-aligned):
  Line 1: "<PINK WORD>" in hot pink (#FF4D8C) + " <AMBER WORD(S)>" in warm amber (#FFA031) + " <WHITE WORD(S)>" in white -- all same heavy font, same line.
  Line 2: "<REST OF HEADLINE>" in white, ultra-heavy.
Bottom-left: "@<HANDLE>" small white uppercase monospace.
Bottom-right: "SAVE FOR LATER" small white uppercase monospace.
One image only.
```

---

## BODY (repeat for each item slide, increment slide number)

```
Slide <N> of <TOTAL> -- BODY. Generate ONE 1080x1350 image only.
Background: warm cream (#F5F0E8) with subtle square dot grid.
Top-left: solid orange (#E85D2F) bookmark ribbon icon.
Top-right: "<NN> / <TOTAL>" orange monospace.
Ghost number: giant "<NN>" (the item number) in barely-visible muted cream (#EDE8E0), positioned top-right background, ~30% canvas height -- decorative only.
Kicker line: "<ITEM TYPE> <NN>" in orange semi-bold sans + "  <ITEM NAME>" in dark regular sans.
Headline: "<PUNCHY DECLARATIVE SENTENCE ENDING WITH ! OR .>" -- ultra-heavy black sans, 2-3 lines, very large, left-aligned.
URL line: "<GITHUB.COM/USER/REPO  *  STAR COUNT>" or "<TOOL.COM>" in small uppercase monospace, dark.
Screenshot: full-width rectangular embed of <describe what the screenshot shows: GitHub repo page / homepage / app UI>.
Body text: "Why it matters: <one plain-language sentence>." regular dark sans.
Tags: two rounded-rectangle pill tags side by side -- "<TAG 1>" and "<TAG 2>" -- white fill, thin dark border.
Italic quote: "<pithy one-liner in italic serif, rephrasing the headline>" at bottom.
One image only.
```

---

## CTA (last slide)

```
Slide <N> of <N> -- CTA. Generate ONE 1080x1350 image only.
Background: warm cream (#F5F0E8) with dot grid.
Top-left: orange bookmark ribbon icon.
Top-right: "<N> / <N>" orange monospace.
Center (upper, massive, stacked, all-caps, centered):
  "COMMENT" -- ultra-heavy near-black (#1A1A1A).
  "<KEYWORD>" -- ultra-heavy orange italic (#E85D2F).
  "FOR THE <PAYOFF TITLE>." -- ultra-heavy orange italic, 1-2 lines.
Center (lower): "<PAYOFF DETAIL -- what they receive when they comment>" in heavy bold dark sans, centered, 1-2 lines.
Bottom-right: "SWIPE ->" small dark monospace.
No handle, no bottom-left text.
One image only.
```

---

Notes:
- Fix any slide with: `regenerate slide N, same style, change <X>`.
- Attach a real screenshot of each item before its BODY prompt for the most accurate embed.
- The BODY kicker label is fully flexible -- swap "PLUGIN" to "REPO", "TOOL", "SKILL", "RESOURCE", etc.
- The cover mascot should be adapted to the post topic -- a fluffy robot for AI tools, a plush cursor for code tools, a soft lock for security tools, etc.
- See `example-post.md` for a fully filled 6-slide set.
