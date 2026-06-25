# Per-post input — Instagram-Template-1 (one detailed prompt per slide)

Gemini won't reliably generate a whole carousel from one short prompt (it tiles them or builds a
deck). So drive it **one slide at a time**: paste the CONTEXT block once, then paste one detailed
slide prompt per image, waiting for each to render.

Build the Gem once from `gem.md` first (attach the 4 Knowledge images). Then per post:

1. Paste **CONTEXT** (sets the story + identity, generates nothing).
2. Paste **COVER**, get slide 1.
3. Paste the **BODY** prompt for each middle slide (increment the numbers), one at a time.
4. Paste **CTA** for the last slide.

Attach any reference screenshot/infographic in the chat right before the slide that should feature
it (it goes in the taped frame).

---

## CONTEXT (paste first, no image)

```
We are building an <N>-slide Instagram carousel in the template (match the Knowledge reference images). I will send ONE detailed prompt per slide; generate ONE 1080x1350 image per prompt. Do not generate anything yet, do not tile slides into one image, do not build a slide deck.

Topic: <one line on what the carousel is about>
Source / notes (keep every slide consistent with this): <paste the article / framework / research>
Identity: header always reads "ALEEM · NEXUSPOINT"; handle is "@<HANDLE>".

Reply with a one-line confirmation and a numbered slide plan, then wait for my per-slide prompts.
```

## COVER (slide 1)

```
Slide 1 of <N> — COVER. Generate ONE 1080x1350 image only.
Style: saturated blue vertical gradient background. A photoreal white marble statue/bust bleeding off the top-right, holding or beside a 3D terracotta symbolic object that represents <topic>.
Kicker (small uppercase, letter-spaced): "<KICKER>"
Headline (giant condensed heavy white sans, tight leading, soft drop shadow): "<HOOK, max 8 words>"
Subtitle (italic serif, white): "<one-line subtitle>"
No header, no footer, no page number. No emojis, no em dashes. One image only.
```

## BODY (repeat for each middle slide, increment 0N and the POINT number)

```
Slide 0N of <N> — BODY. Generate ONE 1080x1350 image only.
Style: terracotta paper-texture background, subtle grain and vignette.
Header (monospace, uppercase, letter-spaced): "<MON> ©<YEAR> · ALEEM · NEXUSPOINT · 0N / 0<N>"
Pill (black ticket pill with notched ends, white uppercase): "POINT 0X / <LABEL>"
Headline (heavy rounded sans, cream and ink words mixed, ends in a period): "<headline, max ~8 words>"
Body (cream, key phrases bold): "<one or two sentences, ~25 words max>"
Visual (taped polaroid frame: white border, two tape strips, slight rotation): <describe the screenshot/diagram, or "render a clean diagram of ..."; omit the frame if no visual fits>
Footer: "0N / 0<N>" left, "SWIPE ->" right.
No emojis, no em dashes. One image only.
```

## CTA (last slide)

```
Slide 0<N> of <N> — CTA. Generate ONE 1080x1350 image only.
Style: terracotta paper-texture background (same as body).
Header (monospace): "<MON> ©<YEAR> · ALEEM · NEXUSPOINT · 0<N> / 0<N>"
Pill (black ticket pill): "<FORWARD LABEL, e.g. BUILD YOUR NEXT PROJECT>"
Stacked statement (huge, ONE word per line, alternating cream/ink, each word ends with a period): "<word>." "<word>." "<word>."
Summary line (cream): "<one-line value summary>. Follow @<HANDLE> for more."
Footer: "0<N> / 0<N>" left.
No emojis, no em dashes. One image only.
```

---

Notes:
- Fix any slide with: `regenerate slide N, same style, change <X>`.
- Review the cover first; it carries the scroll-stop.
- See `example-post.md` for a fully filled set.
