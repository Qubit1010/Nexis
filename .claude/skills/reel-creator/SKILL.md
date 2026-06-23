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

## Phase B — Generate voice, align, preflight (QA gate), render, add music

Five steps, all run here. The voice and music settings are **locked house defaults**
(tuned + approved 2026-06-22) — just run the commands; only reach for flags to deviate.
The **preflight gate** (added 2026-06-22) auto-fixes the caption/audio/timeline defects
that used to need hand-fixing after render, and **blocks the render** until the reel
passes — so don't skip it and don't render with raw `remotion render`; use `render.mjs`.

```bash
cd projects/reel-engine
python scripts/generate_voice.py <slug>                       # cloned-voice voiceover.wav + chunks.json (scene offsets)
node scripts/prepare.mjs <slug>                               # transcribe -> captions.json + PROVISIONAL timeline (medium.en)
.venv/Scripts/python.exe scripts/preflight.py <slug> --fix    # QA GATE: fix captions/audio/timeline; must print PASSED
node scripts/render.mjs <slug>                                # render (refuses unless preflight PASSED) -> out/<slug>.mp4
node scripts/add_music.mjs <slug>                             # mix background music at 25% -> out/<slug>-music.mp4
```

**1. Voice — `generate_voice.py`.** Synthesizes `voiceScript` in Aleem's cloned
voice (`voice/aleem-ref.wav`) and writes the FINISHED `voiceover.wav`. The tuned
recipe is baked into the defaults: per-scene chunking (natural period pauses, and
it avoids the phantom filler words + clipped onsets that per-sentence chunking
caused), 0.82 speed, 48 steps, onset-protected seams, and a heavy+warm
post-process (−0.6 st pitch + low-shelf + loudness). Tune via `--speed`,
`--pitch-semitones`, `--bass-db`, or `--no-post`. **ElevenLabs fallback:** drop a
manual `voiceover.mp3` in the folder and `prepare.mjs` (mp3-first) uses it instead.
Full detail in `references/voice-cloning.md`.

**2. Align — `prepare.mjs`.** Converts the voiceover to 16kHz wav, runs Whisper for
word-level timestamps, writes `captions.json`, and a **provisional** `timeline.json`
(`aligned:false`). It **defaults to `--model medium.en`** (more accurate on the
processed cloned voice). preflight writes the authoritative timeline. First run
downloads Whisper + model; first render downloads a headless Chromium.

**3. Preflight — `preflight.py --fix` (the QA gate).** This replaces the old manual
caption/audio cleanup. It aligns the ground-truth script (`voiceScript`) against the
Whisper transcript and: **rebuilds captions from the script** (so spelling/casing are
always right — fixes "Claude"→"Cloud", "AI" splits, "Cowork"→"car work", CODCODES,
lowercasing in one move), **trims audible phantom words** at the head/seams (drops the
silent hallucinations like "Yes"/"Thus"/"The"), **restores a dropped "Follow for more"
tail** and extends the timeline so it isn't clipped, and **recomputes scene cuts from
`chunks.json`** (exact). It **triple-checks** text+audio+sync and writes `preflight.json`
(the gate marker); it exits non-zero (blocking the render) if anything is unresolved.
A suspected **garbled first word** ("Ahh" onset) is auto-trimmed only when unambiguous,
otherwise flagged — pass `--fix-head` to force the trim. Use `--dry-run` to preview
mutations, `--restore` to revert from `.bak`. Pronunciation of hard words ("Claude"→
"Clawd") is handled upstream by `scripts/pronunciation.json` at synthesis time, so the
audio is right and captions keep the real spelling. See [[reference_reel_preflight_gate]].

**4. Render — `render.mjs` (gated).** Refuses to render unless `preflight.json` says
PASSED and the on-disk captions/timeline/wav still match what preflight passed
(sha256). Use this, not raw `remotion render`. Reads `timeline.json` for duration+cuts.
On success it stamps `out/<slug>.render.json` with the input hashes it built from.

**5. Music — `add_music.mjs` (standard on every reel).** Mixes a `background-music/`
track UNDER the voice at **25%** (voice full, 0.8s fade-in + 2s fade-out) →
`out/<slug>-music.mp4`. Default picks the first track; pass a name to choose
(`add_music.mjs <slug> gr0za`) or `--volume`. The voice-only `out/<slug>.mp4` is kept.
It auto-**ducks the music to 15% during voice-silent scene gaps** (via ffmpeg
`silencedetect`, padded ±0.28s) so a music phrase never pops out when the narration
pauses — that exposed-music swell is the "weird sound before the next word", and it
lives in the music layer, so a re-render won't fix it (re-run `add_music`). It also
**refuses to mux onto a stale video** (the render stamp must match `preflight.json`).
See [[feedback_reel_background_music]].

Verify before declaring done (preflight now enforces most of this automatically):

- **Length** target 40-50s. Default speed 0.82 reads a bit tight (~36s for ~95 words).
  To stretch, lower it (`--speed 0.78`); if a long script runs over 50s, raise it
  (`--speed 0.95`) or trim the script.
- **Preflight PASSED** — if it FAILs, read the report: a mid-speech voiced phantom means
  a real word is missing from the script; a no-speech tail means the script/audio drift.
  Fix the cause and re-run; never bypass the gate by editing the marker.
- **New hard-to-say word** mis-pronounced by the clone → add it to
  `scripts/pronunciation.json` (e.g. `"Anthropic":"An-thropic"`) and regenerate the voice.

Deliver `out/<slug>-music.mp4` (the music version is the final) plus a one-line
summary (length, brand-styled + voice-synced + background music).

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
