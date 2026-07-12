---
name: shorts-creator
description: >
  Convert a topic - a Weekly Posting Schedule row or a topic named ad hoc - into a small
  sequence of 9:16 Instagram Reels/Shorts image prompts: a cover, 1-2 content frames, and a
  CTA, each rendered in NexusPoint's dark branded template. Use this skill whenever the user
  says "make a short", "turn this into a short", "instagram short", "shorts for [topic]",
  "short image prompt", "reel cover images", or wants a quick vertical teaser sequence for
  Reels/Shorts - distinct from `carousel`'s 4:5 feed carousels and `reel-creator`'s full
  rendered voice-synced video pipeline. Always gates on approval of the drafted copy before
  emitting prompts, and always carries NexusPoint branding (a deliberate, scoped exception to
  the no-agency-mention rule for personal-brand content - shorts are a distinct, always
  agency-attributed lane).
---

# Shorts Creator

Turns a topic into a short, punchy sequence of vertical (9:16) image prompts for an
Instagram Reel/Short - a cover, one or two content frames, and a CTA. Same scope as
`linkedin-infographics` and `carousel`: this skill ends at a paste-ready Gemini prompt.
Image generation stays manual, and there is no video rendering here - that is
`reel-creator`'s job (full Remotion + voice-clone + Whisper pipeline for 40-50s reels). A
"short" from this skill is a handful of static frames Aleem posts as a Reel/Short slideshow
or teaser sequence, not a rendered video.

Unlike Aleem's personal LinkedIn/IG feed content, shorts always carry NexusPoint branding
(logo, wordmark, brand colors) - see "Branding" under Rules.

## Templates (preferred path)

Reusable design templates live in `references/<Template>/`. Each has a `design-structure.md`
(the spec), a `gem.md` (a Gemini Gem to build once), an `input-prompt.md` (the per-short
fill), and an `example-post.md` (a worked example) - the same 4-file convention as
`linkedin-infographics`/`carousel`.

- **Instagram-Short-Template-1** (`references/Instagram-Short-Template-1/`) - dark near-black
  canvas, NexusPoint logo + circuit-node accents top-left, tracked-out eyebrow label, large
  bold white headline, gray subtitle, a diagonal blue gradient stripe running through every
  frame as the connective brand motif, and a rounded blue-outlined URL pill on the CTA frame.
  Best for: any topic short - product drops, case studies, quick takes, lead-magnet promos.
  Source image in `docs/Instagram-Short-Template-1/` (save Aleem's reference cover there).

When a template fits (it is the only one so far), tell Aleem to build the Gem once from
`gem.md` (attach the Knowledge image), then use `input-prompt.md` per short so Gemini renders
each frame in that exact look, one frame at a time (cover first, then "next" for each
following frame).

## Setup notes (read once per session)

- The sheet-driven path in Step 1 shells out to `schedule.py`, which needs real network for
  its `gws` calls - run those commands with sandbox disabled (`dangerouslyDisableSandbox:
  true`), same as `post-creator`. The ad hoc path needs none of this.
- If `schedule.py` returns a gws auth error: tell Aleem to run `gws auth login` (account
  `hassanaleem86@gmail.com`) and stop until he confirms. Never drive the browser.

## Auto-start on load

When this skill triggers, go straight to Step 1. Do not summarise.

## Step 1. Pick a topic

Two paths - both valid, use whichever fits how Aleem asked:

- **From the schedule sheet**: `python .claude/skills/post-creator/scripts/schedule.py get
  --row <N>` for a known row, or `find --topic "<name>"` to search by topic. This is the same
  script `post-creator` uses - reused unchanged, no sheet or script changes needed.
- **Ad hoc**: Aleem just names a topic in chat. No sheet row required - treat the topic plus
  whatever detail he gives as the full brief, the same way `research.py` already accepts a
  bare `--topic`/`--description` independent of the sheet.

If a sheet row's `post_type` is a Reel, that row still belongs to `reel-creator` - confirm
with Aleem before making a short out of it instead (he may genuinely want both).

## Step 2. Draft the short's copy

Write, for each frame:

- **Eyebrow label** (2-4 tracked-out words, e.g. "NEW DROP", "CASE STUDY", "QUICK TAKE")
- **Headline** (cover) - short and punchy, 2-4 lines, the hook
- **Subtitle** (cover) - one supporting line
- **Content line(s)** - one idea per content frame: a single bold statement, plus an optional
  short supporting label (a stat, category, or one-line elaboration)
- **CTA text** - the URL or a short action phrase (e.g. "Comment GUIDE")

Keep this light. Do not run Exa research or NotebookLM synthesis by default - a short is a
teaser, not a sourced post, and most topics are already fully specified by the schedule row
or by what Aleem says. Only reach for research if the topic needs a fact you do not already
know and Aleem has not given it, and ask before running
`.claude/skills/post-creator/scripts/research.py` for it. Copy follows
`.claude/skills/content-engine/references/voice-principles.md` tone rules: no em dashes, no
emojis, no "As an AI".

## Step 3. Checkpoint

Show Aleem the drafted copy for every frame (eyebrow/headline/subtitle, each content frame's
line, CTA text) and the frame count, before writing any prompts. Wait for explicit approval
or changes. This is the one gate in this flow - a wrong short is cheap to regenerate compared
to a dense infographic or a rendered reel, but the copy is still worth a look before prompts
go out, and it replaces any inner approval gate the template files might otherwise imply.

## Step 4. Emit the frame prompts

Once approved, fill the template's `input-prompt.md` with the approved copy and print each
frame's prompt as its own code block, in order: CONTEXT (no image) -> COVER -> CONTENT
(repeat 1-2x) -> CTA. Tell Aleem to paste them one at a time into the Gem named in `gem.md`,
waiting for each image before sending the next block.

## Step 5. Optional write-back

Only if Step 1 used a sheet row and Aleem wants it tracked:
`python .claude/skills/post-creator/scripts/schedule.py write --row <N> --status Draft`.
There is no Doc-save step here - unlike `post-creator`'s six-tab Google Doc, a short's output
is the prompts themselves, kept in chat. Skip this step entirely for ad hoc topics.

## Onboarding a new template (Phase A)

When Aleem supplies a NEW reference short (image in `docs/Instagram-Short-Template-N/`):

1. Read the image. Extract its design DNA: canvas (should stay 1080x1920, 9:16), brand
   chrome placement, headline/subtitle treatment, the motif that ties frames together,
   palette (hex), type stack.
2. Create `references/Instagram-Short-Template-N/` with the same 4 files as Template 1.
3. Add the new template to the "Templates" list above.
4. Leave the source image in `docs/` (it is the Gem's Knowledge attachment, not copied into
   the skill).

## Rules

- Always gate on approval of the drafted copy before outputting frame prompts.
- 1080x1920 px, 9:16 vertical, every frame. Deliberately different from `carousel`/
  `linkedin-infographics`'s 4:5 (1080x1350) - shorts are Reels/Shorts-native, not feed posts.
- 3-4 frames total: cover + 1-2 content frames + CTA. If a topic needs more than 2 content
  frames to land, it wants `carousel`, not a short.
- **Branding**: every frame - cover, content, and CTA - carries the NexusPoint logo
  (`brand-assets/logos/nexuspoint-logo.png`) and the dark background/diagonal-stripe motif.
  This is a deliberate, scoped exception to the standing rule against naming NexusPoint in
  personal-brand LinkedIn/IG content - shorts are a distinct, always-agency-attributed lane,
  not personal feed content.
- No emojis. No em dashes - use commas or periods instead. This covers everything you write in
  this flow, not just the frame copy - the Step 3 checkpoint and any reasoning you show your
  work with follow the same rule, the same way `communication-style.md`'s no-em-dash rule
  applies to internal communication, not just published content.
- Keep the template palette and motif consistent across every frame in a sequence so it reads
  as one short, not disconnected images.
