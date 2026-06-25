# Per-post input — Instagram-Template-2 (one detailed prompt per slide)

Two visual registers: **cinematic dark** for cover + CTA, **editorial cream** for body slides.
Drive Gemini one slide at a time — paste CONTEXT once, then one detailed prompt per slide.

Build the Gem once from `gem.md` (attach the 4 Knowledge images). Then per post:

1. Paste **CONTEXT** (sets the story + identity, no image generated).
2. Paste **COVER** — get slide 1 (cinematic dark, film grain, pill CTA).
3. Paste one **BODY** prompt per middle slide (cream dot grid, screenshot visual). Increment numbers.
4. Paste **CTA** for the last slide (cinematic dark, comment trigger).

Attach any reference screenshot or UI mockup right before the body slide that should feature it.

---

## CONTEXT (paste first, no image)

```
We are building an <N>-slide Instagram carousel in the Template-2 style (match the Knowledge reference images). I will send ONE detailed prompt per slide; generate ONE 1080x1350 image per prompt. Do not generate anything yet, do not tile slides, do not build a slide deck.

Topic: <one line on what the carousel is about>
Source / notes (keep every slide consistent with this): <paste the article / framework / key points>
Handle: @<HANDLE>
Comment trigger (used in CTA): "<KEYWORD>"

Reply with a one-line confirmation and a numbered slide plan, then wait for my per-slide prompts.
```

---

## COVER (slide 1 — cinematic dark)

```
Slide 1 of <N> — COVER. Generate ONE 1080x1350 image only.
Style: full-bleed cinematic photo, deep red/maroon color grade, heavy film grain. Subject: <describe a person, crowd, environment, or object that matches the post topic>.
Handle (small, white, centered near top): "@<HANDLE>"
Pre-line (small italic, white, centered): "<intro phrase, e.g. 'How To' / 'The' / 'Why'>"
Giant condensed-heavy-sans headline, white, 2-3 lines each ~85% slide width, tight leading:
"<LINE 1>"
"<LINE 2>"
optional "<LINE 3>"
Italic calligraphic sub-line, white, below the headline: "<For Brands / For Founders / In 5 Steps / etc.>"
Bottom pill (white rounded rectangle, black uppercase text + arrow): "<ACTION LABEL> ->"
No footer, no slide number. One image only.
```

---

## BODY (repeat for each middle slide — increment slide number and step label)

```
Slide <N> of <TOTAL> — BODY. Generate ONE 1080x1350 image only.
Style: warm cream background (#F2EDE3) with a fine uniform dot grid. No header, no handle, no branding.
Headline (top-left, 2-3 lines, heavy bold sans for main words + italic serif for the key accented word):
"<bold part> *<italic word or phrase>*"
Body paragraph (black, regular sans, left-aligned, max ~20 words): "<one concrete step, instruction, or insight>"
Hand-drawn curved arrow (black, organic) pointing from the text zone down to the visual.
Optional handwritten uppercase label near the visual: "<LABEL>" (omit if not needed)
Visual (lower half, floating with soft drop shadow): <describe the screenshot, UI mockup, or diagram to render; e.g. "a clean diagram showing..." or "a screenshot of [tool] showing...">
No footer, no page number, no pill. One image only.
```

---

## CTA (last slide — cinematic dark)

```
Slide <N> of <N> — CTA. Generate ONE 1080x1350 image only.
Style: full-bleed cinematic photo — different scene from the cover (crowd overhead, dark texture, abstract environment). Same deep red/maroon color grade and heavy film grain.
Handle (small, white, centered near top): "@<HANDLE>"
Pre-lines (small, centered, white): "<teaser line 1, e.g. 'want to know'>" / "<teaser line 2, e.g. 'how to build it?'>"
Giant condensed-heavy-sans, centered, white with light teal tint: "<ACTION WORD e.g. COMMENT>"
Large italic serif in quotation marks, teal tint, centered below the action word: '"<KEYWORD>"'
Outro (small, centered, white/italic, 1-2 lines): "<payoff — what they get by commenting / follow @<HANDLE> for more>"
No pill, no page number. One image only.
```

---

Notes:
- Fix any slide with: `regenerate slide N, same style, change <X>`.
- The dark cover/CTA bookends are what make the cream body slides land with contrast. Keep the photo subjects different.
- See `example-post.md` for a fully filled 6-slide set.
