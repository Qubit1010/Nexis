# Test post — "How I Built My Ops Dashboard with Claude Code" (one detailed prompt per slide)

Fully filled 6-slide set for testing the Gem (mirrors the 6 reference images: Cover, Body-Overview,
two Body-Step slides from Phase 1, one Body-Step slide from the final phase, and CTA). Build the Gem
from `gem.md` first (attach the 6 Knowledge images). Then paste the blocks below one at a time,
waiting for each image. Handle is `@aleem_uh`.

---

## STEP 0 — CONTEXT (paste first, no image)

```
We are building a 6-slide Instagram carousel in the Template-8 style (match the Knowledge reference images). I will send ONE detailed prompt per slide; generate ONE 1080x1350 image per prompt. Do not generate anything yet, do not tile slides, do not build a slide deck.

Topic: How I built my weekly ops dashboard with Claude Code in one weekend, seven steps.
Handle / site: @aleem_uh · nexus-point.co
Phases (name -> badge color, consistent across all step slides):
  Phase 1: "THE SPEC" -> blue (#4A90D9)
  Phase 2: "THE BUILD" -> purple (#A78BFA)
  Phase 3: "THE POLISH" -> orange (#F0923B)
Total steps: 7
Comment trigger: "DASHBOARD"
CTA payoff: the full 7-step guide with every prompt I used
Total slides: 6

Reply with a one-line confirmation and a numbered slide plan, then wait for my per-slide prompts.
```

---

## STEP 1 — COVER

```
Slide 1 of 6 -- COVER. Generate ONE 1080x1350 image only.
Background: off-white grid-paper (#FDFCFA with faint #ECE8E0 grid). Decorative dashed squiggly line with small terracotta dots on the right side; faint diagonal grid-fold watermark top-right corner.
Top-left: dashed-border pill, terracotta uppercase monospace: "BUILT IN ONE WEEKEND · NEXUS-POINT.CO"
Headline (giant heavy bold navy sans, 3 lines, left-aligned, tight leading): "How I Built" / "My Ops Dashboard" / "with **Claude Code**" (Claude Code in terracotta #D97757)
Subheadline (2 lines below, mixed bold navy lead-in + regular grey rest): "Seven steps and zero manual reporting. Every prompt I used, no code written by hand."
Identity chip (white pill, thin border, left-aligned below subheadline): avatar + bold navy "Aleem Ul Hassan" + "." + grey "@aleem_uh"
Bottom: browser-window screenshot mockup (rounded top corners, macOS traffic-light dots, URL bar) previewing a dark operator-console dashboard with weekly metrics tiles, cropped off at the bottom edge of the canvas.
One image only.
```

---

## STEP 2 — BODY-OVERVIEW

```
Slide 2 of 6 -- BODY-OVERVIEW. Generate ONE 1080x1350 image only.
Background: off-white grid-paper, same as cover.
Top-left: uppercase monospace kicker, terracotta: "OPS DASHBOARD"
Top-right: identity chip (avatar + bold navy "Aleem Ul Hassan" + "." + grey "@aleem_uh").
Headline (bold navy, 1-2 lines, one phrase in terracotta): "Three inputs run the **whole dashboard**"
Description (1-2 lines, mixed regular grey + bold navy emphasis): "Claude Code reads all three every run. When a number looks wrong, you fix the source, never the chart."
Stacked list cards (3 full-width white rounded cards, thin border #E6E1D8, soft shadow):
  - "SOURCES.md" bold monospace white inside a blue rounded badge with a folder icon -- "**Where the data lives.** Sheet IDs, API keys, refresh cadence."
  - "METRICS.md" bold monospace white inside a purple rounded badge with a folder icon -- "**What gets tracked.** Every KPI, its formula, its target."
  - "LAYOUT.md" bold monospace white inside an orange rounded badge with a folder icon -- "**The look.** Tiles, charts, colors, every decision logged."
Small dotted connector line with a terracotta dot between each pair of cards.
One image only.
```

---

## STEP 3 — BODY-STEP (Step 01, Phase 1)

```
Slide 3 of 6 -- BODY-STEP. Generate ONE 1080x1350 image only.
Background: off-white grid-paper, same as cover.
Left edge: vertical gradient progress rail (thin line, blue #4A90D9 -> purple #A78BFA -> orange #F0923B across the full 7-step sequence), small hollow circles marking each step, the circle for step 1 (near the top) filled/highlighted.
Top edge: a thin cropped sliver of the identity chip from the overview slide peeking in at the very top.
Main card: large white rounded card, thin border, soft shadow.
Top-left: blue rounded-square badge, bold white monospace step number "01".
Top-right, same row: grey pill, uppercase monospace: "PHASE 1 · THE SPEC"
Headline (bold navy, 1-2 lines): "Write the sources file"
Body paragraph (regular grey with bold navy emphasis, 2-4 lines): "Claude Code doesn't know your stack. **Give it exact sheet IDs and API scopes**, nothing implied."
Small uppercase monospace label: "PASTE THIS · CLAUDE CODE"
Prompt box: cream rounded box (#F7EFD3), small terracotta sunburst icon top-left, prompt text (regular dark sans with bold emphasis spans) filling the box: "I need SOURCES.md holding every data source this dashboard pulls from. **Ask me one source at a time** — sheet ID, refresh cadence, auth method — until you could rebuild the connection from the file alone.", small orange circular send-arrow button bottom-right.
One image only.
```

---

## STEP 4 — BODY-STEP (Step 02, Phase 1)

```
Slide 4 of 6 -- BODY-STEP. Generate ONE 1080x1350 image only.
Background: off-white grid-paper, same as cover.
Left edge: vertical gradient progress rail, same as prior slide, circle for step 2 filled/highlighted, one position further down.
Top edge: thin cropped sliver of the prior card peeking in at the very top.
Main card: large white rounded card, thin border, soft shadow.
Top-left: blue rounded-square badge, bold white monospace step number "02".
Top-right, same row: grey pill, uppercase monospace: "PHASE 1 · THE SPEC"
Headline (bold navy, 1-2 lines): "Define every metric"
Body paragraph (regular grey with bold navy emphasis, 2-4 lines): "Make a folder, open Claude Code there. **You name the KPI, Claude drafts the formula** and flags anything ambiguous."
Small uppercase monospace label: "PASTE THIS"
Prompt box: cream rounded box (#F7EFD3), small terracotta sunburst icon top-left, prompt text: "Read SOURCES.md. Propose the KPIs this dashboard should track, then walk me through each one asking **what counts and what doesn't**. Draft the final formula into METRICS.md before building anything.", small orange circular send-arrow button bottom-right.
One image only.
```

---

## STEP 5 — BODY-STEP (Step 07, Phase 3, final step)

```
Slide 5 of 6 -- BODY-STEP. Generate ONE 1080x1350 image only.
Background: off-white grid-paper, same as cover.
Left edge: vertical gradient progress rail, now near the orange end of the gradient, the final circle filled/highlighted at the bottom of the rail.
Top edge: thin cropped sliver of the prior card peeking in at the very top.
Main card: large white rounded card, thin border, soft shadow.
Top-left: orange rounded-square badge, bold white monospace step number "07".
Top-right, same row: grey pill, uppercase monospace: "PHASE 3 · THE POLISH"
Headline (bold navy, 1-2 lines): "The taste pass"
Body paragraph (regular grey with bold navy emphasis, 2-4 lines): "Mine had **three tiles fighting for the same red**. Fix: one accent color per section. Works better with a design-taste skill installed."
Small uppercase monospace label: "PASTE THIS · BEFORE SHIPPING"
Prompt box: cream rounded box (#F7EFD3), small terracotta sunburst icon top-left, prompt text: "What would the taste critic say?", small orange circular send-arrow button bottom-right.
One image only.
```

---

## STEP 6 — CTA

```
Slide 6 of 6 -- CTA. Generate ONE 1080x1350 image only.
Background: off-white grid-paper, no cards, centered composition.
Center top: terracotta sunburst/asterisk icon, centered.
Headline (heavy bold navy, 2-3 lines, centered, one word in terracotta italic): "All seven steps and every prompt," / "*free*"
Description (1-2 lines, grey, centered): "The full build guide, every prompt ready to paste."
CTA line (centered, one line mixing): plain navy "Comment" + dark navy rounded pill with bold white uppercase "DASHBOARD" + plain navy "and I'll send it over."
Bottom: identity chip, centered -- avatar + bold navy "Aleem Ul Hassan" + "." + grey "@aleem_uh"
One image only.
```

---

Fix any slide with: `regenerate slide N, same style, change <X>`.
