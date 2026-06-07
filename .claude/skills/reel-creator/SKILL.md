---
name: reel-creator
description: >-
  Turn a NexusPoint infographic post (Instagram/LinkedIn) into a 40-50s vertical
  motion-graphics reel with a brand-styled, voice-synced animation via the Remotion
  reel-engine. Use this whenever Aleem wants to convert a post, carousel, or
  infographic into a short video/reel, repurpose a static post into motion, or
  generate the ElevenLabs voice script + scene data for a reel. Trigger on
  "make a reel", "turn this post into a reel", "reel from this infographic",
  "convert my post to a video", "animate this post", "voiceover script for a reel",
  or when the user drops an infographic + caption + source and asks for a reel.
  Also use it to render a reel once the user has recorded the voiceover ("render
  the <slug> reel", "the voiceover is ready"). Handles both phases: writing the
  script + content.json, and driving transcription + render after the mp3 exists.
---

# Reel Creator

Converts a NexusPoint infographic post into a 9:16 motion-graphics reel with an
ElevenLabs voiceover synced to brand animation. It is the generator/orchestrator
in front of the `projects/reel-engine/` Remotion codebase — this skill writes the
script and scene data, the engine renders the video.

Aleem has 130+ infographic posts that underperform as static images. The job is to
turn any of them into a punchy reel **fast and repeatably**, on brand, with the
voice exactly synced to the visuals.

## The split: one ElevenLabs step is manual

The voice is recorded by Aleem in the ElevenLabs UI, so the workflow has a human
handoff in the middle. The skill therefore runs in **two phases**:

- **Phase A — Author** (you do this): write the voice script + `content.json`,
  validate it, and hand Aleem the script to paste into ElevenLabs.
- **Phase B — Render** (you do this once the mp3 exists): transcribe + align +
  render the mp4.

Figure out which phase you're in from what the user gives you. A new post (image +
caption + source) → Phase A. "The voiceover is ready / render the X reel" → Phase B.

## Inputs you need (Phase A)

1. **Infographic** — the post image (a screenshot/PNG). Optional but strongly
   preferred; without it the Solution scene uses an animated node-graph fallback.
2. **Caption** — the post's caption/copy.
3. **Source / research** — where the post came from (article, repo, benchmark,
   the user's own take). This grounds the script in real specifics, not fluff.

If any are missing, ask — but don't over-ask. Caption + source is enough to draft;
the infographic can be dropped in later before render.

---

## Phase A — Author the script + content.json

### Step 1. Pick a slug

Short, kebab-case, derived from the topic (`codegraph`, `rag-chunking`,
`cold-email-mistakes`). This names the folder `projects/reel-engine/public/reels/<slug>/`.

### Step 2. Write the voice script

This is the craft of the skill. Read `references/voice-script.md` for the full
method (hook formulas, the 6-beat arc, length math, brand-voice rules, worked
examples). The non-negotiables, summarized:

- **40-50s, ~90-110 spoken words.** ElevenLabs read the CodeGraph script at ~2.1
  words/sec (125 words ran 59s, over target), so size against ~2.2 wps: ~100 words
  lands near 45s. Over ~115 words risks blowing past 50s. When unsure, cut.
- **Hook in the first 3 seconds.** Lead with the payoff or a sharp question
  ("What if you could cut your AI's workload by 58%?"). No throat-clearing.
- **First person, conversational.** Aleem talking, not a corporate VO.
- **No em dashes.** Use commas or periods. (Em dashes corrupt downstream and break
  the house style. This is a hard rule — see [[feedback_google_docs_encoding]].)
- **No agency name, no university/BSAI mention in the spoken copy.** This is
  personal-brand content. Never say "NexusPoint" or reference his degree. (The
  visual logo sting at the end is brand identity and stays — it is not spoken.)
  See [[feedback_content_no_agency_or_academia]].
- **End on a soft CTA**, usually "Follow for more" plus a curiosity line.

### Step 3. Split the script into scenes

The reel is **6 native scenes** in a fixed order. Each scene gets a `voiceText`
slice of the full script. **Concatenating `scenes[].voiceText` in order MUST equal
`voiceScript` exactly, character for character** — this is what lets Whisper anchor
each scene to the spoken audio. The validator enforces it.

| Scene | Role | Visual it drives | Key fields |
|-------|------|------------------|------------|
| `intro` | Hook | Kinetic headline + kicker tag | `headline`, `sub` (kicker) |
| `problem` | The pain | Headline + optional flickering keyword chips | `headline`, `sub`, `chips[]` |
| `solution` | The fix | Slow zoom/pan over the **infographic** | `headline`, `asset:"infographic.png"` |
| `stats` | Proof | Stacked count-up stat cards | `headline` (kicker), `stats[]` |
| `punch` | The payoff line | One bold line + accent rule | `headline` |
| `outro` | CTA | CTA line + pill button + logo sting | `cta`, top-level `handle` |

Field rules and the headline `*accent*` syntax are in `references/content-json.md`.
Read it before writing the JSON. Two things to get right every time:

- **Headlines are display copy, not the spoken line.** Punchy, 3-6 words. Wrap the
  one word you want in brand blue with asterisks: `"Cut your AI's workload by *58%*"`.
- **Stats are the centerpiece.** Pull 2-3 real numbers from the source into
  `stats[]` as `{value, suffix, label}`. If the post has no numbers, a stats scene
  still works with qualitative cards, but real benchmarks hit hardest.
- **chips** dramatize the problem and must fit the topic. Code post →
  `["grep","glob","read"]`. Email post → `["open rates","spam","no replies"]`.
  Non-technical or no good fit → omit `chips` entirely (clean headline + sub).

### Step 4. Write and validate content.json

Write to `projects/reel-engine/public/reels/<slug>/content.json` following the
schema. Then **always run the validator** — it catches the mistakes that silently
break a render or the brand voice:

```bash
cd projects/reel-engine && node scripts/validate_content.mjs <slug>
```

It checks: voiceText concatenation equals voiceScript, no em dashes, no agency/
university mention in spoken text, word count in the 90-130 range, valid scene
types/order, and that stats are numeric. Fix anything it flags before handing off.

### Step 5. Hand the script to Aleem for ElevenLabs

Give him the final `voiceScript` as a clean copy-paste block, plus the two files to
drop in `projects/reel-engine/public/reels/<slug>/`:

- `voiceover.mp3` — exported from ElevenLabs after pasting the script.
- `infographic.png` — the post image (if not already added).

Tell him to come back with "the <slug> voiceover is ready" to trigger Phase B. If
he wants to preview the look before recording, he can run `npm run studio` and set
the composition's `slug` prop (timing is estimated from word counts until aligned).

---

## Phase B — Transcribe, align, render

Run once `voiceover.mp3` (and ideally `infographic.png`) are in the reel folder.

```bash
cd projects/reel-engine
node scripts/prepare.mjs <slug>          # transcribe + align; writes captions.json + timeline.json
npx remotion render Reel out/<slug>.mp4 --props='{"slug":"<slug>"}'
```

`prepare.mjs` converts the mp3 to 16kHz wav, runs Whisper for word-level
timestamps, writes the captions, and anchors each scene to the first two words of
its `voiceText`. The render reads the aligned `timeline.json` and sets duration
from it. First `prepare.mjs` run downloads Whisper + model (a few minutes, once);
first render downloads a headless Chromium (once).

After render, verify before declaring done:

- **Length** is in the 40-50s target. If the VO came back long (the CodeGraph one
  ran 59s), offer to either tighten the script and re-record, or speed the audio
  ~1.1-1.2x with pitch preserved before re-running prepare:
  `ffmpeg -i voiceover.mp3 -filter:a "atempo=1.15" -y voiceover.mp3`
- **Sync** — spoken words land on the matching captions/scene cuts (scrub a few points).
- **Whisper mis-hears** — it occasionally mistranscribes a word (it turned
  "auto-syncs" into "sinks" on CodeGraph). If a caption word is wrong, fix it in
  `captions.json` (preserve the timing fields) and re-render; no need to re-run Whisper.

Deliver the path to `out/<slug>.mp4` and a one-line summary (length, that it's
brand-styled + synced).

---

## Reference files

- `references/voice-script.md` — how to write the 40-50s script: hook formulas, the
  6-beat arc, length math, brand-voice rules, full worked example. **Read in Phase A
  before writing the script.**
- `references/content-json.md` — the `content.json` schema: every scene type, its
  fields, the `*accent*` headline syntax, the voiceText-equals-voiceScript rule, and
  a complete annotated example. **Read in Phase A before writing the JSON.**

## Gotchas worth knowing

- The reel-engine already solved a nasty font-loading render hang by inlining fonts
  as base64 — don't touch `src/fonts.ts` / `src/fonts-data.ts`. See
  [[reference_remotion_font_loading]] and [[project_reel_engine]] for state.
- One reel = one folder under `public/reels/<slug>/`. New reels need no code change;
  the composition is data-driven by the `slug` prop.
- Keep `out/` renders; don't delete prior reels.
