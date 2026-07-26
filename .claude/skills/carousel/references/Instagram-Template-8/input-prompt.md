# Per-post input — Instagram-Template-8 (one detailed prompt per slide)

Step-by-step build/tutorial format. Cover states the build + result, one overview slide lists the
"ingredients" (files/tools/principles), then every step gets its own numbered card threaded by a
color-gradient progress rail, ending in a copy-paste prompt box. Best used for: "how I built X"
walkthroughs, AI workflow tutorials, process breakdowns with concrete copy-paste prompts.

Build the Gem once from `gem.md` (attach the 6 Knowledge images). Then per post:

1. Paste **CONTEXT** (sets the series + identity + phases, no image generated).
2. Paste **COVER** — the title card with the browser-mockup preview.
3. Paste **BODY-OVERVIEW** — the ingredients/files list card.
4. Paste one **BODY-STEP** prompt per step, incrementing the step number and phase as needed.
5. Paste **CTA** for the last slide.

---

## CONTEXT (paste first, no image)

```
We are building an <N>-slide Instagram carousel in the Template-8 style (match the Knowledge reference images). I will send ONE detailed prompt per slide; generate ONE 1080x1350 image per prompt. Do not generate anything yet, do not tile slides, do not build a slide deck.

Topic: <what was built and how, e.g. "How I built a website with Claude in one evening, nine steps">
Handle / site: @<HANDLE> · <SITE OR HANDLE URL>
Phases (name -> badge color, consistent across all step slides):
  Phase 1: "<PHASE 1 NAME>" -> blue (#4A90D9)
  Phase 2: "<PHASE 2 NAME>" -> purple (#A78BFA)
  Phase 3: "<PHASE 3 NAME>" -> orange (#F0923B)
  (add Phase 4 -> green (#5FBF7A) if needed)
Total steps: <N>
Comment trigger (used in CTA): "<KEYWORD>"
CTA payoff: "<what they receive, e.g. the full 9-step guide with every prompt>"
Total slides: <N>

Reply with a one-line confirmation and a numbered slide plan, then wait for my per-slide prompts.
```

---

## COVER (slide 1)

```
Slide 1 of <N> -- COVER. Generate ONE 1080x1350 image only.
Background: off-white grid-paper (#FDFCFA with faint #ECE8E0 grid). Decorative dashed squiggly line with small terracotta dots on the right side; faint diagonal grid-fold watermark top-right corner.
Top-left: dashed-border pill, terracotta uppercase monospace: "<BUILD CONTEXT e.g. BUILT IN ONE EVENING> · <SITE/HANDLE>"
Headline (giant heavy bold navy sans, 3 lines, left-aligned, tight leading): "<LINE 1>" / "<LINE 2>" / "<LINE 3 with one word in terracotta #D97757>"
Subheadline (2 lines below, mixed bold navy lead-in + regular grey rest): "<concrete payoff sentence, e.g. 'Three markdown files and nine steps that strip the AI look out completely.'>"
Identity chip (white pill, thin border, left-aligned below subheadline): avatar + bold navy name "<NAME>" + "." + grey "<HANDLE/SITE>"
Bottom: browser-window screenshot mockup (rounded top corners, macOS traffic-light dots, URL bar) previewing <describe the actual result being shown>, cropped off at the bottom edge of the canvas.
One image only.
```

---

## BODY-OVERVIEW (slide 2, no image)

```
Slide 2 of <N> -- BODY-OVERVIEW. Generate ONE 1080x1350 image only.
Background: off-white grid-paper, same as cover.
Top-left: uppercase monospace kicker, terracotta: "<TOPIC KICKER e.g. WEBSITE BUILD>"
Top-right: identity chip (avatar + bold navy name + "." + grey handle/site).
Headline (bold navy, 1-2 lines, one phrase in terracotta): "<HEADLINE e.g. 'Three files run the whole build'>"
Description (1-2 lines, mixed regular grey + bold navy emphasis): "<description sentence>"
Stacked list cards (<N, 3-5> full-width white rounded cards, thin border #E6E1D8, soft shadow), each:
  - "<ITEM 1 NAME>" bold monospace white inside a [blue/purple/orange/green] rounded badge with a folder icon -- "<bold navy lead phrase>. <regular grey continuation>"
  (repeat per card, one distinct badge color per card)
Small dotted connector line with a terracotta dot between each pair of cards.
One image only.
```

---

## BODY-STEP (repeat for each step, increment step number/phase)

```
Slide <N> of <TOTAL> -- BODY-STEP. Generate ONE 1080x1350 image only.
Background: off-white grid-paper, same as cover.
Left edge: vertical gradient progress rail (thin line, blue #4A90D9 -> purple #A78BFA -> orange #F0923B -> green #5FBF7A across the full step sequence), small hollow circles marking each step, the circle for THIS step filled/highlighted at its position in the sequence.
Top edge: a thin cropped sliver of the previous slide's content peeking in at the very top, implying continuity.
Main card: large white rounded card, thin border, soft shadow.
Top-left: colored rounded-square badge (color = current phase), bold white monospace step number "<NN>".
Top-right, same row: grey pill, uppercase monospace: "PHASE <N> · <PHASE NAME>"
Headline (bold navy, 1-2 lines): "<short instruction, e.g. 'Write the facts file'>"
Body paragraph (regular grey with 1-2 bold navy emphasis spans, 2-4 lines): "<what to do and why, plain language>"
Small uppercase monospace label: "PASTE THIS · <TOOL e.g. CLAUDE CHAT>"
Prompt box: cream rounded box (#F7EFD3), small terracotta sunburst icon top-left, prompt text (regular dark sans with bold emphasis spans) filling the box: "<the literal, specific, ready-to-paste prompt>", small orange circular send-arrow button bottom-right.
One image only.
```

---

## CTA (last slide)

```
Slide <N> of <N> -- CTA. Generate ONE 1080x1350 image only.
Background: off-white grid-paper, no cards, centered composition.
Center top: terracotta sunburst/asterisk icon, centered.
Headline (heavy bold navy, 2-3 lines, centered, one word in terracotta italic): "<HEADLINE e.g. 'The exact nine steps and every prompt,'> <ITALIC WORD e.g. 'free'>"
Description (1-2 lines, grey, centered): "<what they'll receive, in plain terms>"
CTA line (centered, one line mixing): plain navy "Comment" + dark navy rounded pill with bold white uppercase "<KEYWORD>" + plain navy "and I'll send it over."
Bottom: identity chip, centered -- avatar + bold navy name + "." + grey handle/site.
One image only.
```

---

Notes:
- Fix any slide with: `regenerate slide N, same style, change <X>`.
- Keep phase names and badge colors identical across every BODY-STEP slide in one carousel — the rail and pills are a single continuous system across the whole post.
- Prompt-box text must be a real, specific, copy-pasteable instruction, not a paraphrase of the step.
- See `example-post.md` for a fully filled 9-step set.
