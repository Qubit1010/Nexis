# LinkedIn-Template-9 — Design Structure

Canonical spec extracted from the reference infographic in
`docs/LinkedIn-Template-9/LinkedIn-Template-9.jpg`.
This file is the source of truth for `gem.md` and `input-prompt.md`.

Source brand identity stripped (Claude logo removed). NexusPoint logo replaces it top-right per brand rule.

## Global

- **Canvas:** 1080 x 1350 px, 4:5 portrait. The whole infographic is ONE image.
- **Format:** phased roadmap grid. A title block, an optional full-width hero/intro step, then
  3-4 phase sections each containing a colored phase header bar and a 3-column feature card grid.
  Typically 9-12 total cards (3 per phase). NOT a bento grid, NOT horizontal tier bands, NOT a
  numbered list.
- **Template purpose:** product/feature roadmaps, "N steps to X", phased learning paths, "how to
  get started with X", feature catalogues grouped by theme, onboarding guides, workflow tutorials.
  Each step/card needs: a name, a 1-2 sentence description, and an example action or prompt.
- **Tone:** approachable-technical, educational, hands-on. Reads like a cheat-sheet or playbook.

## Layout

### Title block (top ~10% of canvas)

- **Main title:** large-to-very-large bold grotesque, left-aligned, 1-2 lines. One or two key words
  in accent orange (#E85D1A); remaining words in black (#1A1A1A). Article words ("The", "A") may be
  thinner weight.
  Example: "The **Claude Code** Roadmap" (bold orange on "Claude Code", regular black on "The" and
  "Roadmap").
- **Subtitle:** small regular sans, dark grey, 1 line below the title.
  Example: "12 steps. Install to autopilot. Real prompts inside."
- **NexusPoint logo:** ~100-120px tall, top-right, vertically centered in the title block.
- **Page background:** white or very near-white (#FAFAF8).

### Hero step / Step 00 (optional, full-width, ~8% of canvas)

A full-width strip below the title block. Contains:
- A small orange pill label "STEP 00" on the left.
- Step name + subtitle in the same line ("CLI · install once, then run anywhere").
- A card spanning ~70% of the width: step number badge (orange), step name, icon, brief description,
  and a terminal/command example on the right side.

This section is optional. Skip it if the content does not have a standalone intro step.

### Phase sections (3-4 phases, stacked, filling ~80% of canvas)

Each phase section contains:

**Phase header bar (~5% height per phase)**
- Full-width colored pill/label bar. Contains:
  - "PHASE 0N" text (left, white, small, pill-shaped badge or inline).
  - Phase name (left, white, bold, all-caps or title case): e.g. "CONTEXT".
  - Phase subtitle (right or inline, white, small, regular): e.g. "what Claude knows about you".
- Background: solid phase accent color (see Palette below).

**3-column card grid (~20% height per phase)**
- Three equal-width cards side by side, one per step in this phase.
- Cards sit on the page background (white), with a light grey border and rounded corners.

### Card anatomy (per card)

**Header strip (top of card, full card width)**
- Solid phase accent color background.
- Left: small rounded step number badge (white text, accent bg or slightly darker) + step name in
  white bold sans.
- Right: a small flat icon representing the step (optional, white or light).

**Body (card center)**
- 1-2 sentences, regular sans, dark (#222222), describing what the step/feature is and what it does.
- Short and punchy. No jargon.

**Action example box (card bottom)**
- Small label above the box: "PASTE INTO CLAUDE" or "TYPE IN CLAUDE" or equivalent (small, bold,
  accent color).
- A light-grey rounded box (#F4F4F2) containing the example prompt or action text in dark monospace
  or regular sans.
- A small circular arrow/copy icon at the bottom-right of the box.

### Phase accent colors (canonical)

| Phase | Name | Hex |
|-------|------|-----|
| 01 | blue | #3A88C5 |
| 02 | orange | #E85D1A |
| 03 | purple | #7055A0 |
| 04 | teal-green | #2DAA84 |

If more than 4 phases, cycle. If fewer, pick from the top.

## Palette

| Token | Hex | Use |
|---|---|---|
| Page background | `#FAFAF8` | near-white, throughout |
| Card background | `#FFFFFF` | card fill |
| Card border | `#E5E5E5` | thin rounded-rect border |
| Title ink | `#1A1A1A` | non-accent title words |
| Title accent | `#E85D1A` | highlighted title words |
| Subtitle / body | `#333333` | subtitle and card body text |
| Phase header bg | accent per phase | colored bar |
| Phase header text | `#FFFFFF` | all text in phase header |
| Card header bg | accent per phase | card header strip |
| Card header text | `#FFFFFF` | step name in card header |
| Action label | accent per phase | "PASTE INTO CLAUDE" label |
| Action box bg | `#F4F4F2` | example prompt box |
| Action box text | `#2A2A2A` | example prompt text |

## Type stack

- **Title main words:** bold/heavy grotesque (Inter Bold / Montserrat Bold), large. Accent words
  in orange #E85D1A.
- **Title article words:** regular or light grotesque, same size as main words.
- **Subtitle:** small regular sans, dark grey.
- **Phase header label:** white bold sans, "PHASE 0N" small.
- **Phase name:** white extra-bold sans, medium-large, all-caps or title case.
- **Phase subtitle:** white regular sans, small.
- **Step number badge:** white bold sans, small, inside a rounded badge.
- **Step name (card header):** white bold sans, medium.
- **Card body:** regular sans, #333333, small-medium.
- **Action label:** bold sans, accent color, very small all-caps.
- **Action text:** regular or monospace, #2A2A2A, small.

## Structural rules

- 3-4 phases. Each phase has exactly 3 cards. Total steps: 9-12.
- Phase header bar spans full card-grid width.
- All cards within a phase are the same height and equal width (3-column grid).
- The action example box is always at the bottom of each card.
- Cards do not overflow their phase section height.
- Hero step (Step 00) is optional. Include it when there is a prerequisite setup step.

## Identity

- **NexusPoint logo:** ~100-120px tall, top-right of the title block.
  Attach `brand-assets/logos/nexuspoint-logo.png` as a Knowledge file in the Gem.
- **No handle or footer** at the bottom.
