# Reel Creator: How NexusPoint Built a Fully Automated Infographic-to-Reel Pipeline That Converts Static Posts into Voice-Synced Motion Graphics

**Category:** Content Production / Internal AI System
**Built by:** NexusPoint
**Powered by:** Remotion (React), ElevenLabs TTS, OmniVoice (voice cloning), OpenAI Whisper, FFmpeg, TypeScript, Python

---

## The Problem

Content creation is a volume game -- but video takes 10x the effort of a static post. Anyone with a backlog of written content faces the same wall: turning that library into video means hours per piece, and the manual workflow breaks at scale.

The default approach is to open a video editor, record a voiceover, manually place text on a timeline, tweak animations frame by frame, export, then realize the captions don't match the audio. One reel eats an afternoon. Ten reels eat a week. And when something needs updating, you start over.

Four specific problems:

1. **Friction.** Every reel requires bouncing between four or five tools -- script in a doc, voice recording in a TTS app, timeline in a video editor, captions in a subtitle tool. The context-switching alone kills speed.
2. **Sync drift.** Matching spoken words to on-screen text is precise work. Whisper transcriptions contain errors (wrong casing, hallucinated words, split terms like "AI" becoming "A I"), and manual fixes compound with every revision.
3. **Quality inconsistency.** Without a locked brand system, two reels from the same producer look different -- font weights shift, color hexes drift, animation timing varies. The tenth reel doesn't look like the first.
4. **No source-to-reel pipeline.** You have 130+ infographic posts sitting as static images. Each one contains a caption, data points, and a visual -- everything needed for a reel -- but there is no system that turns those three inputs into a finished mp4 without a person in the loop.

NexusPoint had the infographics. The bottleneck was the conversion.

---

## What It Is

The Reel Creator is a skill + engine system that converts any infographic post into a 40-50 second, 9:16 vertical motion-graphics reel with a cloned voiceover synced to brand animation -- in two automated phases with a mandatory QA gate between authoring and render.

It takes three inputs (post caption, source research, and infographic image) and produces one output: a finished mp4 with captions, voiceover, and background music, ready to publish.

Every reel it produces has:
- A 6-scene narrative arc: hook intro, problem framing, solution showcase, animated stat counters, punch line, and CTA + logo sting
- A cloned voiceover in the founder's voice (OmniVoice, 0.82x speed, warm post-processing) with ElevenLabs as a manual fallback
- Frame-accurate captions driven by the ground-truth script, not raw Whisper output -- so "Claude" never becomes "Cloud" and "AI" stays one word
- Brand-locked visuals: tech-blue gradient (#208EC7 to #1F5B99), Quiche Sans display type, Urbanist body, charcoal #232323, circuit-N logo
- Background music mixed at 25% under the voice, with automatic ducking to 15% during silent scene gaps
- A preflight QA report certifying that every caption, audio chunk, and scene cut is aligned before a single frame renders

One skill. Two commands: author then render. The engine handles everything in between.

---

## The Pipeline: 2 Phases, 6 Scenes

### Phase A -- Author the Script and Scenes

The skill takes the post's caption, source material, and infographic and authors two files: a voice script and a `content.json` scene definition.

**Step 1: Write the voice script.** The script follows a locked 6-beat narrative arc: hook, problem, solution, proof, punch, CTA. It is sized to ~90-110 words at ~2.2 words per second, landing near 45 seconds. The hook fires in the first 3 seconds -- no throat-clearing. Every word is first-person, conversational, with no em dashes, no agency name, and no academic credentials mentioned in the spoken copy. The voice is the founder talking, not a corporate VO.

**Step 2: Split into scenes and write content.json.** The script is sliced across 6 native scene types, each mapping to a specific visual component in the Remotion engine:

| Scene | Role | Visual | Key Fields |
|-------|------|--------|------------|
| `intro` | Hook | Kinetic headline + subhead | `headline`, `sub` |
| `problem` | Pain | Headline + optional keyword chips | `headline`, `sub`, `chips[]` |
| `solution` | Fix | Slow pan/zoom over infographic | `headline`, `asset` |
| `stats` | Proof | Stacked count-up stat cards | `headline`, `stats[]` |
| `punch` | Payoff | One bold line + accent rule | `headline` |
| `outro` | CTA | CTA pill + logo sting | `cta`, `handle` |

A critical constraint: concatenating every scene's `voiceText` slice must equal the full `voiceScript` exactly, character for character. This is what lets Whisper anchor every scene to the correct timestamp in the audio -- and the validator enforces it before the phase completes.

**Step 3: Validate.** A `validate_content.mjs` script checks: voiceText concatenation equals voiceScript, no em dashes, no agency/university mention in spoken text, word count in range, valid scene types and order, and numeric stats. Nothing proceeds until it passes.

### Phase B -- Voice, Align, Preflight, Render, Music

Five sequential steps, all automated. The voice is generated in a cloned voice by default; ElevenLabs is the fallback.

**Step 1: Generate voiceover.** `generate_voice.py` synthesizes the full voiceScript in the founder's cloned voice (OmniVoice, from a reference clip). The recipe is per-scene chunking -- not per-sentence -- which produces natural period pauses and avoids the phantom filler words and clipped onsets that per-sentence chunking caused. Parameters are locked: 0.82x speed, 48 steps, onset-protected seams, heavy+warm post-processing (-0.6 semitones pitch, low-shelf EQ, loudness normalization). Output: `voiceover.wav` plus `chunks.json` with exact scene offsets.

**Step 2: Transcribe and align.** `prepare.mjs` converts to 16kHz wav, runs OpenAI Whisper (`medium.en` model, more accurate on the processed cloned voice) for word-level timestamps, and writes `captions.json` with a provisional `timeline.json` (marked `aligned: false`). The first run downloads Whisper and the model; the first render downloads headless Chromium -- both one-time costs.

**Step 3: Preflight QA gate.** `preflight.py --fix` is the centerpiece quality step. It aligns the ground-truth script against the Whisper transcript and performs five fixes automatically:

1. **Rebuilds captions from the script** -- spelling and casing are always right because the source is the authored script, not the transcript. Fixes "Claude" to "Cloud", split "A I", "Cowork" to "car work", CODCODES, and lowercasing in one pass.
2. **Trims audible phantom words** at head and seams -- drops silent hallucinations like "Yes", "Thus", "The" that Whisper inserts.
3. **Restores dropped tails** -- extends the timeline when "Follow for more" is clipped, so the CTA is never cut off.
4. **Recomputes scene cuts from chunks.json** -- exact, not estimated from the transcript.
5. **Triple-checks text, audio, and sync** -- writes `preflight.json` as the gate marker. Exits non-zero (blocking render) if anything is unresolved.

A suspected garbled first word is auto-trimmed only when unambiguous; otherwise it is flagged. Pronunciation of hard words (e.g. "Claude" respelled as "Clawd") is handled upstream by `pronunciation.json` at synthesis time, so the audio is correct and captions keep the real spelling.

**Step 4: Render.** `render.mjs` is the gated render command. It refuses to run unless `preflight.json` says PASSED and the on-disk captions, timeline, and wav still match what preflight passed (SHA-256 verified). It reads `timeline.json` for duration and scene cuts, runs Remotion rendering, and stamps `out/<slug>.render.json` with the input hashes on success.

**Step 5: Add background music.** `add_music.mjs` mixes a background music track under the voice at 25% volume (0.8s fade-in, 2s fade-out), producing `out/<slug>-music.mp4`. It auto-ducks the music to 15% during voice-silent scene gaps (via FFmpeg `silencedetect`, padded plus or minus 0.28s) so a music phrase never pops out when narration pauses. It also refuses to mux onto a stale video -- the render stamp must match `preflight.json`. The voice-only version is kept alongside the music version.

---

## What's Built and Working

| Feature | Status |
|---------|--------|
| 6-scene narrative arc (intro, problem, solution, stats, punch, outro) | Live |
| Cloned voice synthesis via OmniVoice (per-scene chunking, warm post-process) | Live |
| ElevenLabs manual voiceover fallback | Live |
| Whisper `medium.en` transcription with word-level timestamps | Live |
| VoiceScript-to-voiceText concatenation validator | Live |
| Headline accent syntax (`*word*` renders in brand blue) | Live |
| Animated stat counters with count-up animation | Live |
| Infographic pan/zoom scene with image or node-graph fallback | Live |
| Brand-locked styling (gradient, fonts, colors, logo) | Live |
| Base64-inlined fonts (no render hangs from font loading) | Live |
| Preflight QA gate: caption rebuild from script (fixes all Whisper errors) | Live |
| Preflight QA gate: phantom word trimming at head and seams | Live |
| Preflight QA gate: dropped tail restoration | Live |
| Preflight QA gate: scene cut recomputation from chunks.json | Live |
| Preflight QA gate: triple-check text + audio + sync with SHA-256 gate | Live |
| Pronunciation dictionary for hard-to-say words | Live |
| Background music mixing at 25% with auto-ducking during gaps | Live |
| Gated render (blocks unless preflight passed) | Live |
| Data-driven composition (new reels = new folder, no code change) | Live |
| Content validator (em dashes, agency name, word count, scene order) | Live |

---

## Cost Breakdown

| Step | Service | Cost per Reel |
|------|---------|---------------|
| Voice synthesis | OmniVoice (cloned voice) | Ask for current pricing *(self-hosted/local, cost depends on model and API plan)* |
| Voice synthesis (fallback) | ElevenLabs TTS (~100 words, ~500 chars) | ~$0.15-0.30 |
| Transcription | OpenAI Whisper `medium.en` (local) | Free (runs on-device) |
| Rendering | Remotion (open source) | Free |
| Background music | `background-music/` library | Licensing varies by track *(ask for the current library source and cost)* |
| **Total per reel** | | **~$0.15-0.50 plus music licensing** |

The primary voice pipeline uses OmniVoice, which runs locally and eliminates the per-reel ElevenLabs cost for the standard path. The only recurring per-reel cost is the voice synthesis step; transcription, rendering, and preflight all run on local hardware with no API fees. At one reel per day, the monthly cost is well under $10-15.

---

## The Architecture

**Video engine:** Remotion (React) -- renders programmatic motion graphics to mp4 via headless Chromium
**Voice synthesis:** OmniVoice (Python) -- cloned voice with per-scene chunking and post-processing; ElevenLabs API as fallback
**Transcription:** OpenAI Whisper `medium.en` via `@remotion/install-whisper-cpp` -- word-level timestamps
**Audio processing:** FFmpeg -- format conversion, silence detection for music ducking, audio/video muxing
**Validation:** Node.js and Python scripts -- content schema validation, preflight QA gate with SHA-256 integrity checks
**Fonts:** Quiche Sans (display), Urbanist (body) -- inlined as base64 data URIs to prevent Chromium render hangs
**Brand:** #208EC7 to #1F5B99 gradient, charcoal #232323, circuit-N logo

**Commands:**
```
cd projects/reel-engine

# Phase A — Validate content.json before handing off
node scripts/validate_content.mjs <slug>

# Phase B — Full automated pipeline
python scripts/generate_voice.py <slug>                        # Cloned-voice voiceover.wav + chunks.json
node scripts/prepare.mjs <slug>                                 # Transcribe + provisional timeline
.venv/Scripts/python.exe scripts/preflight.py <slug> --fix      # QA gate: fix captions/audio/timeline (must PASS)
node scripts/render.mjs <slug>                                  # Gated render -> out/<slug>.mp4
node scripts/add_music.mjs <slug>                               # Mix music at 25% -> out/<slug>-music.mp4
```

**File structure per reel:**
```
public/reels/<slug>/
  content.json          # Script + scene definitions (authored by skill)
  infographic.png       # Source post image (input)
  voiceover.wav         # Synthesized voice (generated)
  voiceover.mp3         # ElevenLabs fallback (optional, input)
  captions.json         # Word-level captions from Whisper (generated)
  timeline.json         # Scene cuts and duration (generated, authoritative after preflight)
  chunks.json           # Scene audio boundaries (generated by voice synthesis)
  preflight.json        # QA gate marker with SHA-256 hashes (generated)
out/<slug>.mp4          # Voice-only render
out/<slug>-music.mp4    # Final: voice + background music
out/<slug>.render.json  # Render stamp with input hashes
```

---

## End-to-End Walkthrough

Here is what happens when someone runs the Reel Creator on a post titled "CodeGraph" -- an infographic about using knowledge graphs to reduce AI workload by 58%.

1. **Input lands.** The post caption, the source research (a benchmark paper), and the infographic PNG are handed to the skill. A slug is picked: `codegraph`.

2. **Script is authored.** The skill writes a 105-word voice script opening with "What if you could cut your AI's workload by 58%?" -- the hook fires in under 3 seconds. It hits all six beats: hook, the problem of fragmented codebases, CodeGraph as the solution, the 58% reduction number as the stat, a punch line about shipping faster, and "Follow for more" plus a curiosity line as the CTA.

3. **Scenes are split.** The 105 words are sliced across 6 scenes. The Solution scene points to `infographic.png`. Two stats are pulled from the source: `{value: 58, suffix: "%", label: "fewer tool calls"}` and `{value: 3.2, suffix: "x", label: "faster retrieval"}`. The validator runs and confirms: voiceText concat equals voiceScript, no violations. `content.json` is saved.

4. **Voiceover is generated.** `generate_voice.py codegraph` runs. It synthesizes the 105-word script in the cloned voice: per-scene chunking, 0.82x speed, 48 steps, warm post-processing. The output is a 46-second `voiceover.wav` plus `chunks.json` with exact scene boundaries.

5. **Transcription runs.** `prepare.mjs codegraph` converts to 16kHz wav, runs Whisper `medium.en`, and writes `captions.json` with word-level timestamps. The provisional `timeline.json` is marked `aligned: false`. Whisper transcribed "knowledge graph" correctly but split "AI" into "A I" and lowercased "CodeGraph" to "codegraph" -- standard Whisper artifacts.

6. **Preflight fixes everything.** `preflight.py codegraph --fix` aligns the ground-truth script against the transcript. It rebuilds captions from the authored script -- "AI" is one word, "CodeGraph" has the right casing. It detects and trims a phantom "So" at the head of the Problem scene that Whisper hallucinated. It restores the last two words of "Follow for more" that the transcript dropped. Scene cuts are recomputed from `chunks.json`. Triple-check passes. `preflight.json` is written with PASSED status and SHA-256 hashes of the captions, timeline, and wav.

7. **Render fires.** `render.mjs codegraph` checks `preflight.json` -- PASSED. Hashes match. It reads the authoritative `timeline.json` (46.2 seconds), renders all 6 scenes through Remotion with animated stat counters, caption overlays synced to word timestamps, and the infographic pan/zoom in the Solution scene. Chromium renders 1386 frames at 30fps. `out/codegraph.mp4` is written.

8. **Music is mixed.** `add_music.mjs codegraph` picks the first track from `background-music/`, mixes it at 25% volume under the voice with 0.8s fade-in and 2s fade-out. FFmpeg detects the silent scene gap between the Problem and Solution scenes and ducks the music to 15% there. `out/codegraph-music.mp4` is the final deliverable -- 46.2 seconds, voice-synced, brand-styled, with background music.

9. **Result.** A 46-second reel that took one command to author and one automated pipeline to produce. The infographic that was collecting dust as a static post is now a motion-graphics reel with captions, voiceover, and music -- ready for Instagram, YouTube Shorts, and TikTok.

---

## The Prospect Takeaway

The Reel Creator is NexusPoint's internal content production engine for short-form video. It turned a 130-post infographic backlog from a liability (hours of manual editing per post) into an asset (one command per reel).

The architecture behind it -- programmatic video rendering, cloned voice synthesis with chunked alignment, Whisper transcription anchored to a ground-truth script, and a preflight QA gate that auto-fixes transcription defects -- is not specific to infographic posts. The same system works for:

- **Product demos.** Feed in product screenshots, feature descriptions, and a script. The engine renders a synced walkthrough reel with highlighted features, animated callouts, and a CTA.
- **Client case studies.** Turn a written case study into a 60-second motion-graphics summary: problem slide, solution slide, stat counters for results, logo sting for the client brand.
- **Course and educational content.** Convert lesson scripts and diagrams into voice-synced explainer reels with animated keyword chips, step-by-step reveals, and caption overlays.
- **Real estate and property tours.** Input property photos, specs, and a narrated script. Output a synced walkthrough reel with stat cards for square footage, price, and features.
- **Event and conference promos.** Drop in speaker headshots, talk titles, and event branding. The engine renders a hype reel with speaker cards, animated schedule, and registration CTA.

Any business with a library of static content and a brand worth showing has the same bottleneck: video costs too much time to produce consistently. An engine that takes structured content in and outputs finished reels out -- with locked brand quality, synced captions, and a QA gate that catches every transcription error -- turns a per-piece editing bottleneck into a per-command pipeline.

---

*Built and maintained by NexusPoint. Last updated: June 2026.*
