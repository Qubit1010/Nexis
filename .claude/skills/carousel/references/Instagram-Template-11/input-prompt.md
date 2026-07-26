# Per-post input — Instagram-Template-11 (one detailed prompt per slide)

Vintage kraft-paper zine tutorial format. Cover states the product/topic, an overview slide explains
what it is, numbered step slides (pick a terminal / grid / hub-diagram / stacked-cards variant per
step) walk through setup or usage, a pro-tips or why-this checklist slide adds depth, and a "save
this" CTA closes it out. Best used for: dev-tool setup guides, CLI/product walkthroughs, "how X
works" breakdowns, AI/automation tutorials with real commands.

Build the Gem once from `gem.md` (attach the 10 Knowledge images). Then per post:

1. Paste **CONTEXT** (sets the topic + step plan + identity, no image generated).
2. Paste **COVER** — the masthead title card with the taped terminal mockup.
3. Paste **BODY-OVERVIEW** — the what-is-this slide.
4. Paste one **BODY-STEP** prompt per step, picking the variant (A/B/C/D) that fits.
5. Paste **BODY-TIPS** and/or **BODY-WHY** as needed.
6. Paste **CTA** for the last slide.

---

## CONTEXT (paste first, no image)

```
We are building an <N>-slide Instagram carousel in the Template-11 style (match the Knowledge reference images). I will send ONE detailed prompt per slide; generate ONE 1080x1350 image per prompt. Do not generate anything yet, do not tile slides, do not build a slide deck.

Topic: <the product/tool/workflow this tutorial covers>
Handle: @<HANDLE>
Month/year for masthead: <e.g. "JULY 2026">
Step plan (name -> variant):
  Step 01: "<STEP NAME>" -> Variant <A terminal / B grid / C hub / D stacked cards>
  Step 02: "<STEP NAME>" -> Variant <...>
  (repeat per step)
Closing slide(s): <Tips / Why / both>
Total slides: <N>

Reply with a one-line confirmation and a numbered slide plan naming each step's variant, then wait for my per-slide prompts.
```

---

## COVER (slide 1)

```
Slide 1 of <N> -- COVER. Generate ONE 1080x1350 image only.
Background: kraft-paper tan (#DFC9A4) with visible paper-fiber grain.
Masthead: "<MONTH YEAR>" (left, small bold uppercase) / "@<HANDLE>" (center) / "01/<TOTAL>" (right). Thin black rule below.
Black stamped badge: "TUTORIAL" (or "<ADAPTABLE CATEGORY WORD>")
Headline (huge heavy bold black sans, 2 lines): "<LINE 1>" / "<LINE 2>"
Accent line (heavy serif italic, rust #C8542E, one line below headline): "<PRODUCT/TOPIC CONTINUATION WORD>"
Subheadline (one line, bold black): "<what this guide delivers, e.g. 'The Complete Setup Guide'>"
Hand-drawn rust arrow curving down toward the terminal mockup.
Terminal mockup: dark rounded window (#161616), masking-taped at the top two corners, title bar text "<tool-name>", macOS traffic-light dots. Inside: a dashed multicolor wireframe icon/logo on the left representing <topic>, an ASCII-style dashed wordmark + version tag on the right, a green divider rule, key-value status lines ("<Label>: <value>"), another divider, and a blinking cursor prompt line.
Footer: "01/<TOTAL>" (left) / "SWIPE ->" (right).
One image only.
```

---

## BODY-OVERVIEW (slide 2)

```
Slide 2 of <N> -- BODY-OVERVIEW. Generate ONE 1080x1350 image only.
Background: kraft-paper tan, same as cover. Masthead + footer with page "02/<TOTAL>".
Black stamped badge: "OVERVIEW"
Headline (2 lines, mixed black + one rust phrase): "<HEADLINE e.g. 'What is [PRODUCT]?'>"
Body paragraph 1 (regular black/grey, bold emphasis spans): "<what it is and who made it>"
Body paragraph 2 (regular black/grey, bold emphasis spans): "<what it does, 2-3 lines>"
Stat callout (bold rust number + regular black continuation): "<e.g. '180k+ GitHub stars in under 4 months.'>"
Bottom row: 3 hand-drawn rust-outline icon + handwritten caption pairs, side by side: "<ICON 1 concept>" / "<CAPTION 1>", "<ICON 2 concept>" / "<CAPTION 2>", "<ICON 3 concept>" / "<CAPTION 3>"
One image only.
```

---

## BODY-STEP — VARIANT A: Terminal demo (repeat per step using this variant)

```
Slide <N> of <TOTAL> -- BODY-STEP (Variant A: terminal demo). Generate ONE 1080x1350 image only.
Background: kraft-paper tan, same as cover. Masthead + footer with page "<NN>/<TOTAL>".
Giant faint ghost numeral "<STEP NUMBER>" (#E3B79A, textured) bleeding off the right edge behind the headline.
Black stamped badge: "STEP <NN>"
Headline (1-2 lines, mixed black + one rust word): "<STEP HEADLINE, e.g. 'Install'>"
Instruction (1-3 lines, regular black/grey, may include an inline monospace command chip): "<what to do>"
Terminal mockup: dark window (#161616), masking-taped at one or two corners, showing: "$ <literal command>", then output lines (progress bar or checklist, monospace green/white), ending in a success line.
Hand-drawn rust circle/arrow calling out the success line, with a handwritten caption: "<e.g. 'one command, that's it'>"
One image only.
```

---

## BODY-STEP — VARIANT B: Provider/option grid (repeat per step using this variant)

```
Slide <N> of <TOTAL> -- BODY-STEP (Variant B: option grid). Generate ONE 1080x1350 image only.
Background: kraft-paper tan, same as cover. Masthead + footer with page "<NN>/<TOTAL>".
Giant faint ghost numeral "<STEP NUMBER>" bleeding off the right edge behind the headline.
Black stamped badge: "STEP <NN>"
Headline (1-2 lines, mixed black + one rust word): "<STEP HEADLINE, e.g. 'Pick Your X'>"
Instruction (1-2 lines, may include an inline monospace command chip): "<what to do>"
Grid: 2 rows x 3 columns of small rounded cream cards (#F2E9DC), each masking-taped at a slight rotation, containing a small colored dot (top-left), a centered brand/topic icon, and a bold label below: "<OPTION 1>", "<OPTION 2>", "<OPTION 3>", "<OPTION 4>", "<OPTION 5>", "<OPTION 6>"
Hand-drawn rust arrow calling out one card, with a handwritten caption: "<e.g. 'swap anytime, zero config changes'>"
Optional line beneath the grid: "+ <N> more <options>"
One image only.
```

---

## BODY-STEP — VARIANT C: Hub/connection diagram (repeat per step using this variant)

```
Slide <N> of <TOTAL> -- BODY-STEP (Variant C: hub diagram). Generate ONE 1080x1350 image only.
Background: kraft-paper tan, same as cover. Masthead + footer with page "<NN>/<TOTAL>".
Giant faint ghost numeral "<STEP NUMBER>" bleeding off the right edge behind the headline.
Black stamped badge: "STEP <NN>"
Headline (1-2 lines, mixed black + one rust word): "<STEP HEADLINE, e.g. 'Go Beyond the Terminal'>"
Instruction (1-2 lines, may include an inline monospace command chip): "<what to do>"
Radial diagram: small center oval/pill containing "<PRODUCT NAME>" in rust handwritten script, with hand-drawn rust arrows radiating out to <5-6> small masking-taped icon cards arranged around it, each a platform/integration logo + label: "<INTEGRATION 1>", "<INTEGRATION 2>", "<INTEGRATION 3>", "<INTEGRATION 4>", "<INTEGRATION 5>"
Handwritten caption beneath the diagram: "<e.g. 'talk to your agent from anywhere'>"
One image only.
```

---

## BODY-STEP — VARIANT D: Stacked capability cards (repeat per step using this variant)

```
Slide <N> of <TOTAL> -- BODY-STEP (Variant D: stacked cards). Generate ONE 1080x1350 image only.
Background: kraft-paper tan, same as cover. Masthead + footer with page "<NN>/<TOTAL>".
Giant faint ghost numeral "<STEP NUMBER>" bleeding off the right edge behind the headline.
Black stamped badge: "STEP <NN>"
Headline (1-2 lines, mixed black + one rust word): "<STEP HEADLINE, e.g. 'Supercharge with X'>"
Instruction (1-2 lines): "<what this feature does>"
3 stacked horizontal cream cards (#F2E9DC), masking-taped at alternating corners, each: icon + bold command/name-style label + short grey description + trailing chevron: "<ITEM 1>", "<ITEM 2>", "<ITEM 3>"
Curved hand-drawn rust arrow linking the stack to a handwritten caption: "<e.g. 'it also creates its own X'>"
Small terminal snippet card below: "$ <discovery command>" then a result line, e.g. "Found <N>+ <items> in the hub"
One image only.
```

---

## BODY-TIPS (numbered checklist slide)

```
Slide <N> of <TOTAL> -- BODY-TIPS. Generate ONE 1080x1350 image only.
Background: kraft-paper tan, same as cover. Masthead + footer with page "<NN>/<TOTAL>".
Black stamped badge: "TIPS"
Headline (mixed black + one rust word): "<e.g. 'Pro Tips'>"
4 stacked horizontal cream cards (#F2E9DC), masking-taped at the seams between them:
  1. Filled rust circle "1" + "<bold inline command/keyword> <regular continuation>" + small hand-drawn rust icon on the right
  2. Filled rust circle "2" + "<...>" + icon
  3. Filled rust circle "3" + "<...>" + icon
  4. Filled rust circle "4" + "<...>" + icon
One image only.
```

---

## BODY-WHY (comparison checklist slide, optional)

```
Slide <N> of <TOTAL> -- BODY-WHY. Generate ONE 1080x1350 image only.
Background: kraft-paper tan, same as cover. Masthead + footer with page "<NN>/<TOTAL>".
Black stamped badge: "WHY"
Headline (mixed black + one rust word): "Why <PRODUCT> Over Others?"
4-row checklist, each row: rust-outlined circular checkmark + bold black feature title + regular grey description (1-2 lines) + small hand-drawn rust icon on the right:
  1. "<FEATURE 1>" -- "<description>"
  2. "<FEATURE 2>" -- "<description>"
  3. "<FEATURE 3>" -- "<description>"
  4. "<FEATURE 4>" -- "<description>"
Rows separated by a thin dashed rule. A curly-brace/bracket line on the far left connects all four rows.
One image only.
```

---

## CTA (last slide)

```
Slide <N> of <N> -- CTA. Generate ONE 1080x1350 image only.
Background: kraft-paper tan. Masthead only ("<MONTH YEAR>" / "@<HANDLE>" / "<N>/<N>"), no footer bar.
Faint full ghost-logo watermark (very low contrast, #E3B79A tint) centered behind the headline, echoing the cover's icon/wordmark.
Headline (giant, 3 lines, centered): "<LINE 1>" in rust + "<LINE 2>" / "<LINE 3>" in black. Small hand-drawn rust arrows pointing inward at the headline from both sides.
Subheadline (one line, grey, centered): "<e.g. 'Follow for more [TOPIC] tutorials'>"
Black pill, centered, bold cream text: "@<HANDLE>"
Bottom row, centered: 3 small hand-drawn rust icons (bookmark, send, heart) separated by thin dividers.
Masking-tape strips pinned at all four corners of the canvas.
One image only.
```

---

Notes:
- Fix any slide with: `regenerate slide N, same style, change <X>`.
- Match the Body-Step variant to what the step actually shows — don't force a provider grid onto a single-command install step, or a terminal mockup onto a multi-platform integration step.
- Every terminal mockup needs real, plausible command syntax and output, never lorem ipsum.
- Keep the ghost-numeral and badge accurate to the real step number and running page count.
- See `example-post.md` for a fully filled 9-slide set.
