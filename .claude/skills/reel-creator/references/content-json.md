# content.json Schema Reference

`content.json` is the single per-reel input you author. It lives at
`projects/reel-engine/public/reels/<slug>/content.json` and drives the whole
composition. The engine is data-driven by the `slug` prop, so a new reel needs no
code change — just this file plus the user's `voiceover.mp3` and `infographic.png`.

The TypeScript source of truth is `projects/reel-engine/src/types.ts`. This file
explains how to fill it correctly.

## Top-level shape

```jsonc
{
  "slug": "codegraph",            // matches the folder name; kebab-case
  "platform": "instagram",        // "instagram" | "linkedin" | string (informational)
  "title": "CodeGraph",           // human label
  "voiceScript": "full script ...",  // EXACT text Aleem pastes into ElevenLabs
  "scenes": [ /* 6 scenes, fixed order */ ],
  "source": "where this came from + key facts",  // grounding, not rendered
  "handle": "@nexuspoint"         // optional; shown faint in the outro
}
```

## The one rule that makes sync work

**`scenes[].voiceText` concatenated in order (joined with a single space) must equal
`voiceScript` exactly.** Whisper transcribes the recorded audio, then `prepare.mjs`
anchors each scene to the first two words of its `voiceText` in the transcript. If
the concatenation drifts from `voiceScript` — a dropped word, different punctuation
that changes wording, a missing scene slice — the alignment silently lands scene cuts
in the wrong place.

Practical way to get it right: write `voiceScript` first as one flowing paragraph,
then cut it into six contiguous slices for the scenes. Don't paraphrase the slices.
The validator reconstructs `voiceScript` from the slices and fails on mismatch (it
compares loosely on whitespace, but keep the words identical).

## The six scenes (fixed order)

Order is always: `intro → problem → solution → stats → punch → outro`. Each scene
object is `{ id, type, voiceText, ...fields }`. `id` can equal `type`.

### intro — the hook
```jsonc
{ "id": "intro", "type": "intro",
  "voiceText": "What if you could cut your AI's workload by 58%?",
  "headline": "Cut your AI's workload by *58%*",  // big display headline
  "sub": "AI Coding Agents" }                      // small kicker tag above it
```
- `headline`: 3-6 word display line. Not the spoken sentence — a tight visual title.
- `sub`: a short uppercase-style kicker shown as a pill. Defaults to "AI Engineering"
  if omitted. Use it to set the topic ("AI Coding Agents", "Cold Email", "RAG").

### problem — the pain
```jsonc
{ "id": "problem", "type": "problem",
  "voiceText": "When I run agents on a big codebase, they burn tokens scanning files...",
  "headline": "AI agents *blindly* scan your code",
  "sub": "burning time and tokens",                 // blue accent line under headline
  "chips": ["grep", "glob", "read"] }               // optional flickering keyword chips
```
- `chips`: short keyword/command tags that dramatize the pain. **Make them fit the
  topic.** Code post → `["grep","glob","read"]`. Cold email post →
  `["open rates","spam","no reply"]`. Design post → `["bounce","confused","no clicks"]`.
- `sub`: optional one-line amplifier in brand blue.
- **`problemVariant`** picks the treatment so the pain beat doesn't look identical in
  every reel — choose per post like you choose the solution visual:
  - `"chips"` (default): flickering keyword pills. Good for commands / short symptoms.
  - `"crossout"`: a struck-through list of the `chips` items (coral X + strike). Good
    for "here's what's broken" pains (e.g. robotic voices, actor fees, one language).
  - `"glitch"`: a glitching headline (RGB-split jitter). Good for drift / breakdown /
    chaos / "it falls apart" topics.
  All three read the same fields (`headline`, `sub`, `chips`); `crossout` uses `chips`
  as its line items, `glitch` ignores `chips` (headline + sub only). Pick the one that
  matches the post's pain, and vary it across reels so the library doesn't feel samey.

### solution — the fix (infographic moment)

Two visual modes. Default pans the raw image; `"funnel"` rebuilds the infographic as
native motion graphics. Prefer the native rebuild when the infographic's core is a
funnel/pyramid/step-flow — it looks far better than panning a flat screenshot, and
it stays fully on-brand.

**Default — pan the image:**
```jsonc
{ "id": "solution", "type": "solution",
  "voiceText": "So I started using X. It indexes everything into one map...",
  "headline": "One pre-indexed *map* of your code",
  "asset": "infographic.png" }
```
- Slowly zooms and pans down the post's `infographic.png` inside a device frame — the
  one moment the original post art is on screen. Keep `asset` as `"infographic.png"`.
- If no infographic is supplied, the scene falls back to an animated node-graph.

**Native funnel — rebuild the infographic as motion:**
```jsonc
{ "id": "solution", "type": "solution",
  "voiceText": "So I started using X...",
  "headline": "Built for *growth* marketers",
  "visual": "funnel",
  "funnel": [
    { "name": "Awareness",         "goal": "Get discovered" },
    { "name": "Consideration",     "goal": "Educate prospects" },
    { "name": "Intent",            "goal": "Production + integration" },
    { "name": "Conversion",        "goal": "Move users to paid" },
    { "name": "Retention & Scale", "goal": "Scale, stay compliant" }
  ] }
```
- `visual: "funnel"` swaps the image pan for an animated funnel built from `funnel[]`:
  stages stack and taper toward the bottom, numbered like the source art, in a
  bright-to-deep blue ramp (on-brand, not the source's rainbow).
- Keep `goal` lines SHORT (2-3 words) — they render on one line inside the bar, and
  the lower (narrower) bars have limited width. Long stage names like
  "Retention & Scale" are fine; long goals will get tight.
- 3-6 stages works; 5 is the sweet spot. The headline should describe the funnel
  (e.g. the infographic's own subtitle), not the spoken product line, since the
  funnel visual and the spoken `voiceText` may cover different angles.
- Still keep `asset: "infographic.png"` set — it's harmless and preserves the raw
  image for reference/fallback.

**Native roadmap — rebuild a phased / step infographic as motion:**
```jsonc
{ "id": "solution", "type": "solution",
  "voiceText": "So I started using X...",
  "headline": "Zero to an *operating system*",
  "visual": "roadmap",
  "roadmap": [
    { "name": "Context", "goal": "Define boundaries" },
    { "name": "Fire",    "goal": "Trigger workflows" },
    { "name": "Extend",  "goal": "Wire in your tools" },
    { "name": "Scale",   "goal": "Build the org chart" }
  ] }
```
- `visual: "roadmap"` renders a vertical phased path from `roadmap[]`: a blue spine
  draws downward while numbered phase nodes pop in sequence, each with a card.
- Use when the infographic is a journey/roadmap/phase sequence (e.g. a 4-phase or
  12-step process). Collapse a long step list down to its 3-5 top-level phases — the
  reel can't show 12 steps legibly in a few seconds.
- Same short-text rule as the funnel: keep `name` and `goal` to a few words each
  (they render on one line; row height is fixed).

**Native layers — rebuild a layered / stack infographic as motion:**
```jsonc
{ "id": "solution", "type": "solution",
  "voiceText": "...",
  "headline": "Five layers, one *team*",
  "visual": "layers",
  "layers": [
    { "name": "Runtime",    "goal": "Local daemon + config" },
    { "name": "Identity",   "goal": "Persistent named agents" },
    { "name": "Execution",  "goal": "Task lifecycle" },
    { "name": "Delegation", "goal": "Squads + skills" },
    { "name": "Automation", "goal": "Scheduled autopilots" }
  ] }
```
- `visual: "layers"` renders equal-width slabs with a 3D thickness edge, stacked and
  dropping into place in sequence. Same short-text rule (`name` + `goal`, one line each).

**Choosing a solution visual:** funnel → marketing/sales funnels, pyramids, narrowing
stages. roadmap → phased journeys, step-by-step processes, timelines. layers → stacked
architectures, "Layer 1...N", tiers. Otherwise pan the raw `infographic.png`. A native
rebuild beats a flat pan whenever the infographic's core is a funnel, sequence, or stack.

**Multi-word accents:** headline `*...*` spans can cover more than one word, e.g.
`"An *org chart* for your AI"` or `"Zero to an *operating system*"`. Still accent only
one phrase per headline.

### stats — the proof (centerpiece)
```jsonc
{ "id": "stats", "type": "stats",
  "voiceText": "58% fewer tool calls, 47% fewer tokens, 22% faster.",
  "headline": "Real benchmark gains",               // used as the kicker tag
  "stats": [
    { "value": 58, "suffix": "%", "label": "fewer tool calls" },
    { "value": 47, "suffix": "%", "label": "fewer tokens used" },
    { "value": 22, "suffix": "%", "label": "faster problem solving" }
  ] }
```
- `stats[]`: 2-3 items. Each is `{ value (number), suffix?, prefix?, label }`. They
  animate as count-ups, stacked and staggered.
- `value` MUST be numeric (the count-up animates to it). Use `prefix`/`suffix` for
  units: `{ value: 3, prefix: "$", suffix: "M", label: "pipeline added" }`.
- Say the numbers in `voiceText` in the **same order** as `stats[]` so the spoken
  audio matches the cards lighting up.
- `headline` here is rendered as the small kicker above the cards (defaults to
  "The Numbers").

### punch — the payoff line
```jsonc
{ "id": "punch", "type": "punch",
  "voiceText": "Your AI should drive outcomes, not inflate your bill.",
  "headline": "AI should drive *outcomes*",
  "punchVariant": "rule" }
```
- One bold display line — the reframe / "why it matters".
- **`punchVariant`** picks the treatment so the payoff beat varies across reels:
  - `"rule"` (default): a thin accent bar above the headline (editorial).
  - `"quote"`: an oversized quotation mark above the line (reads as a mantra/principle).
  - `"spotlight"`: a soft radial glow behind the line (cinematic emphasis, no rule).
  Choose per post and vary it across reels (like `problemVariant`).

### outro — the CTA
```jsonc
{ "id": "outro", "type": "outro",
  "voiceText": "If your agents feel slow, this is worth a look. Follow for more.",
  "cta": "Ready to make your AI faster and leaner?" }
```
- `cta`: the on-screen question. Below it: a "Follow for more" pill button + the
  NexusPoint logo sting + the `handle` (if set at top level).

## The `*accent*` headline syntax

In any `headline`, wrap exactly the word(s) you want rendered in brand blue (with a
glow) in single asterisks: `"Cut your AI's workload by *58%*"`. Use it on the one
word that carries the punch — usually the number or the key verb. Don't accent more
than one phrase per headline; the contrast is the point.

## Validation checklist (the validator enforces these)

- `scenes[].voiceText` joined == `voiceScript` (whitespace-tolerant).
- `voiceScript` word count ~90-110 (target ~100; over ~115 warns — ElevenLabs reads ~2.1 wps).
- No em dash (`—`) anywhere in spoken text.
- No "nexuspoint" / "iqra" / "bsai" / "university" in spoken text.
- Exactly the six scene types present, in order.
- Every `stats[].value` is a number.
- `slug` matches the folder name.

Run it: `cd projects/reel-engine && node scripts/validate_content.mjs <slug>`
