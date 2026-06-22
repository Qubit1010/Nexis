---
name: reel-creator
description: >-
  Turn a NexusPoint infographic post (Instagram/LinkedIn) into a 40-50s vertical
  motion-graphics reel with a brand-styled, voice-synced animation via the Remotion
  reel-engine. Use this whenever Aleem wants to convert a post, carousel, or
  infographic into a short video/reel, repurpose a static post into motion, or
  generate the voice script + scene data for a reel. The voiceover is generated
  automatically in a cloned voice (OmniVoice), with manual ElevenLabs as a
  fallback. Trigger on "make a reel", "turn this post into a reel", "reel from
  this infographic", "convert my post to a video", "animate this post",
  "voiceover script for a reel", or when the user drops an infographic + caption
  + source and asks for a reel. Also use it to render a reel ("render the <slug>
  reel", "generate the voiceover"). Handles both phases: writing the script +
  content.json, and generating the voice + driving transcription + render.
---

# Reel Creator

Converts a NexusPoint infographic post into a 9:16 motion-graphics reel with a
voiceover synced to brand animation. It is the generator/orchestrator in front of
the `projects/reel-engine/` Remotion codebase — this skill writes the script and
scene data, the engine renders the video.

Aleem has 130+ infographic posts that underperform as static images. The job is to
turn any of them into a punchy reel **fast and repeatably**, on brand, with the
voice exactly synced to the visuals.

## The flow: end-to-end, no manual handoff

The voiceover is generated automatically in a **cloned voice** via OmniVoice, so
the whole pipeline runs without leaving the skill. Two phases, both done here:

- **Phase A — Author**: write the voice script + `content.json`, validate it.
- **Phase B — Voice + Render**: generate the cloned-voice voiceover, transcribe +
  align, render the mp4.

ElevenLabs is a **fallback**: if Aleem wants hand-tuned studio delivery for a
given reel, he drops a `voiceover.mp3` into the reel folder and `prepare.mjs`
prefers it. See `references/voice-cloning.md`.

Figure out which phase you're in from what the user gives you. A new post (image +
caption + source) → Phase A then straight into B. "Render the X reel / regenerate
the voiceover" → Phase B.

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

### Step 5. Drop in the infographic, then go to Phase B

Make sure `infographic.png` (the post image) is in
`projects/reel-engine/public/reels/<slug>/` if it wasn't added already. No manual
recording is needed — Phase B generates the voiceover. If you want to preview the
look first, run `npm run studio` and set the composition's `slug` prop (timing is
estimated from word counts until aligned).

---

## Phase B — Generate voice, align, render

```bash
cd projects/reel-engine
python scripts/generate_voice.py <slug>       # FINISHED cloned-voice voiceover.wav (baked recipe); see references/voice-cloning.md
node scripts/prepare.mjs <slug> --model medium.en   # transcribe + align; medium.en = better captions on the processed voice
npx remotion render Reel out/<slug>.mp4 --props='{"slug":"<slug>"}'
node scripts/add_music.mjs <slug>             # mix background music under the voice at 25% -> out/<slug>-music.mp4
```

**Background music is standard on reels.** After render, run `add_music.mjs` to mix
a track from `background-music/` under the voice at **25%** (voice stays full, 0.8s
fade-in + 2s fade-out). Default picks the first track; pass a name to choose
(`node scripts/add_music.mjs <slug> gr0za`) or `--volume` to adjust. The
voice-only `out/<slug>.mp4` is kept; the deliverable is `out/<slug>-music.mp4`.

`generate_voice.py` outputs the finished voice (per-scene chunking for natural
pauses, heavy+warm profile baked in) — no separate audio step. Tune or disable
via flags (`--pitch-semitones`, `--bass-db`, `--no-post`, `--speed`); see
`references/voice-cloning.md`.

`generate_voice.py` synthesizes `voiceScript` in the cloned reference voice
(`projects/reel-engine/voice/aleem-ref.wav`) and writes `voiceover.wav`. For a
studio-quality reel instead, skip that step and drop a manual `voiceover.mp3` in
the folder — `prepare.mjs` is **mp3-first** and uses it over the generated wav.

`prepare.mjs` converts the voiceover to 16kHz wav, runs Whisper for word-level
timestamps, writes the captions, and anchors each scene to the first two words of
its `voiceText`. The render reads the aligned `timeline.json` and sets duration
from it. First `prepare.mjs` run downloads Whisper + model (a few minutes, once);
first render downloads a headless Chromium (once).

After render, verify before declaring done:

- **Length** target 40-50s. Default speed is 0.82 (per-scene reads a bit tight, ~36s
  for ~95 words). To stretch, regenerate at a lower speed (`--speed 0.78`); if a long
  script runs over 50s, raise it (`--speed 0.95`) or trim the script.
- **Sync** — spoken words land on the matching captions/scene cuts (scrub a few points).
- **Whisper mis-hears** — more frequent on the heavier/processed voice. Run prepare
  with `--model medium.en` first; then fix any wrong caption word in `captions.json`
  (preserve the timing fields) and re-render — no need to re-run Whisper. Common
  ones: "Claude"→"Cloud", number words, or a filler word at a scene gap.

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
- `references/voice-cloning.md` — the OmniVoice cloned-voice voiceover: setup, the
  reference clip, `generate_voice.py` flags, length tuning, and the ElevenLabs
  mp3 fallback. **Read in Phase B before generating the voice.**

## Gotchas worth knowing

- The reel-engine already solved a nasty font-loading render hang by inlining fonts
  as base64 — don't touch `src/fonts.ts` / `src/fonts-data.ts`. See
  [[reference_remotion_font_loading]] and [[project_reel_engine]] for state.
- One reel = one folder under `public/reels/<slug>/`. New reels need no code change;
  the composition is data-driven by the `slug` prop.
- Keep `out/` renders; don't delete prior reels.
