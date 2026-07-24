# Output Spec (shared by all 4 templates)

Every template emits **exactly this structure**, so the four candidate sets are comparable.
The *method* of getting here differs per template; the *shape* does not. Word limits and
counts come from the client's main voice file (`clients/<client>.md`) — read them there,
don't hardcode. The numbers below are the Brenda defaults.

---

## Input

- One full podcast transcript (~25 min). Format: `Speaker (MM:SS)` line, then a paragraph.
  Timestamps sit at the **start of each paragraph** — use them to mark segment start/end.
- The client's main voice file.

## Output: one markdown file per template

Save to `output/<client>/<episode-slug>/<NN>-<template-name>.md`.

### File header

```
# <Episode title> — Candidate Set <NN>: <Template name>
**Client:** <name>  ·  **Method:** <one-line description of this template's angle>
**Episode:** <slug>  ·  **Generated:** <date>

> One-paragraph note: how this template chose segments and shaped hooks (so the reviewer
> can tell the four approaches apart at a glance).
```

### Then a Segment Ranking table (Template 05)

The full rank from Template 05 Step 1, so the reviewer sees how every candidate scored. Lists
EVERY candidate considered (shipped and cut), gated on the two guardrails, scored 1-5 on the four
criteria. This block becomes the **Report tab** of the Google Doc.

```
## Segment Ranking

| Rank | Segment (label · timestamp) | Complete | Resonate | Conviction | Concise | Total | Ship? | Note |
|------|------------------------------|----------|----------|-----------|---------|-------|-------|------|
| 1 | "<label>" · <start>-<end> | 5 | 5 | 5 | 4 | 19 | Yes | <one-line reason> |
```

Guardrails (both must pass or Ship? = No): complete standalone thought; offers a solution, not
just a problem. Count is **quality-gated, not fixed**: ship every row at or above the voice file's
quality bar, never pad to a number, never cut a bar-clearer. The bar and the duration guide live
in the voice file.

### Then the segments (count is quality-gated, not fixed). Each segment block:

```
## Segment <n> — "<short label>"  ·  <start>-<end> (~<duration>)
**Pillar:** Feel Secure | Grow with Ease | Belong Fully
**Why this segment:** <1-2 sentences tying it to a recruitment pain/desire — the selection rationale>
**Transcript excerpt:** "<the actual quotable lines the clip is cut from>"

### Text hooks (5) — on-video overlays, <hook word limit>
1. <hook> (recommended)
2. <hook> (2nd option)
3. <hook>
4. <hook>
5. <hook>

Mark your top pick `(recommended)` and runner-up `(2nd option)` — the markers can sit on any
two of the five. The editor reviews from a shortlist, not a flat list.

### Captions (3, A/B) — <caption word limit>, self-contained, platform noted

**The label sits alone on its own line, then the caption body is written as its own
blank-line-separated short paragraphs** (1-3 sentences each, per the cadence rule below) —
never one dense run-on line. The tabbed Google Doc exporter (`md_to_gdoc.py --tabs`) turns a
bold label with nothing after it into its own bold paragraph, and blank-line-separated text
below it into separate spaced paragraphs. A caption written as `- **A (...):** <full text>`
on one line does not get split apart by the exporter — it renders as a single wall-of-text
paragraph with the label buried inside it. Follow this shape exactly:

```
**A (<platform/angle>):**

<opening line, on its own>

<1-3 sentence body paragraph>

<CTA line or closing thought, on its own>

**B (<platform/angle>):**

<same paragraph-broken shape>

**C (<platform/angle>):**

<same paragraph-broken shape>
```

### Long-form posts (3-5) — LinkedIn / Facebook, <post word limit>

Format each post for its platform's native reading behavior:

**LinkedIn:** Open with the most interesting sentence (bold claim, specific moment, or short
question — never a scene-setter). Punchy opener and CTA, one idea per line; the body writes
in short 1-3 sentence paragraphs, not one sentence per line throughout — vary cadence so it
reads as a person talking, not a list. White space, no link in body. ~150-300 words.
Optimize for dwell.

**Facebook:** Conversational opening, slightly more narrative. Same cadence rule as LinkedIn
above. Still use line breaks — no walls of text. ~100-250 words.

**Both platforms:** end every post with a specific, experience-based question the reader can
answer in one sentence ("What's the toughest deal situation you've navigated?") — never a
generic "Thoughts?" / "What do you think?".

**Same rule as captions above: the label sits alone on its own line, then the post body is
its own blank-line-separated short paragraphs** — never one dense run-on line, and never a
numbered-list item with the whole post crammed after the colon (the exporter cannot split
that back apart). Follow this shape:

```
**LinkedIn:**

<opening line — the most interesting sentence, on its own>

<1-3 sentence body paragraph>

<1-3 sentence body paragraph>

<CTA question, on its own>

**Facebook:**

<same paragraph-broken shape>

**LinkedIn:**

<same paragraph-broken shape, if a 3rd post>
```

---

## Hard rules for every template

- **Stand-alone test:** every hook, caption, and post must make sense without the episode.
  No "listen to the full episode" as the *only* CTA.
- **Recruitment lens:** the implied reader is the ICP agent (see voice file), and the
  implied ask is "come build your business here."
- **Voice fidelity:** obey the absence signals in the voice file (no em dashes, no buzzwords,
  no emojis unless the `[Red knob]` is ON, no generic motivation).
- **Captions must differ by angle**, not be three rewordings of one idea (they're for A/B).
- **Real timestamps** from the transcript, not invented.
- Hooks ≠ captions ≠ posts. A hook is a 3-second overlay; a caption is the post body; a
  long-form post is a thought-leadership piece. Don't blur them.
