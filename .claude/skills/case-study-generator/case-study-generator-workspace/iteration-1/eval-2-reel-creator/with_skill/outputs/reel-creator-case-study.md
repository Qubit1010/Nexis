# Reel Creator: How NexusPoint Built an Automated Motion-Graphics Engine That Turns Static Posts Into Voice-Synced Reels

**Category:** Internal AI System / Content Production
**Built by:** NexusPoint
**Powered by:** Remotion 4.0 (React), OmniVoice (ElevenLabs), Whisper (medium.en), ffmpeg, Python, Node.js

---

## The Problem

Anyone running content on Instagram and LinkedIn knows the dynamic: video reels outperform static posts by a wide margin, but producing reels is slow, expensive, and inconsistent. A single 45-second motion-graphics reel takes a video editor 2-3 hours -- scripting, recording voiceover, timing scene transitions, syncing captions, and mixing audio. At that rate, even one reel per week is a slog. Two per week is a part-time job.

Most creators give up and post static images, or they batch a few reels every couple of months and go silent between drops. Neither option works for building a consistent content presence.

Four specific problems:

1. **Static posts underperform.** NexusPoint had 130+ infographic posts sitting as flat images on Instagram and LinkedIn. The information was solid -- the presentation was forgettable. A static infographic gets scrolled past. The same content as a motion-graphics reel with voiceover gets watched and shared.
2. **Manual video editing is a bottleneck.** Producing one reel meant: write a script, record voiceover in ElevenLabs, open a video editor, import assets, manually time scene transitions to the audio, add captions frame by frame, mix background music, and export. Even for someone fast, that is 2-3 hours per reel. At that cost, the ROI math kills consistency.
3. **Voice sync is the hard part.** The difference between a reel that looks amateur and one that looks professional is whether the captions and scene cuts land exactly on the spoken words. Manual sync means scrubbing a timeline and nudging keyframes -- tedious, error-prone, and the first thing that gets sloppy when you are rushing.
4. **No repeatable pipeline.** One-off reels do not scale. If every reel is a bespoke creative project with no shared structure, you cannot improve the process, you cannot reuse assets, and you cannot hand it off to anyone else. You either do it yourself or it does not get done.

NexusPoint built the Reel Creator to replace all of that.

---

## What It Is

The Reel Creator is a two-phase CLI pipeline that converts an infographic post (caption + image + source) into a 40-50 second, 9:16 vertical motion-graphics reel -- with an ElevenLabs voiceover, TikTok-style synced captions, animated stat counters, scene transitions timed to the audio, and background music mixed under the voice at 25%. The entire pipeline runs from command line with zero manual video editing.

By the end of a run, the reel has:
- A 6-scene branded animation (intro, problem, solution, stats, punch, outro)
- An ElevenLabs cloned-voice voiceover synced to every scene cut
- Word-level captions timed to the audio with correct spelling and casing
- 2-3 animated stat counters with count-up animation
- The infographic image as the solution scene hero, slow-zoomed and panned
- Background music mixed under the voice at 25% with fade in/out and silence-gap ducking
- A brand intro with the NexusPoint circuit-N logo and CTA outro
- A QA gate that auto-fixes caption, audio, and timeline defects before render

One infographic post. One command. One finished reel.

---

## Phase A -- Author the Script and Scene Data

Phase A is the creative layer. You provide a post -- the infographic image, the caption, and the source material -- and the skill authors the voice script and scene configuration.

### Step 1 -- Write the Voice Script

The voice script is the craft of the reel. The skill follows a strict method documented in the skill's reference files:

- **40-50 seconds target, ~90-110 spoken words.** ElevenLabs at the tuned speed of 0.82x reads at roughly 2.2 words per second. A 100-word script lands near 45 seconds. Over 115 words risks blowing past 50 seconds.
- **Hook in the first 3 seconds.** No throat-clearing, no "Hey everyone." The first line is a sharp question or a payoff: "What if you could cut your AI's workload by 58%?" or "Most cold emails die before they even reach the inbox."
- **First person, conversational.** The voiceover sounds like the founder talking, not a corporate VO. Personal brand, not agency brand.
- **6-beat arc.** Hook (the problem), pain (why it matters), solution (what fixes it), proof (stats and benchmarks), punch (the one-line payoff), and CTA (follow for more).
- **No em dashes, no agency name, no university mention in spoken copy.** Hard brand-voice rules enforced by the validator.
- **Ends on a soft CTA** -- "Follow for more" plus a curiosity line that teases the next post.

### Step 2 -- Split Into Scenes

The reel is 6 native scenes in a fixed order. Each scene gets a `voiceText` slice of the full script. Concatenating `scenes[].voiceText` in order must equal `voiceScript` exactly, character for character -- this is what lets Whisper anchor each scene to the correct segment of the spoken audio later.

| Scene | Role | Visual |
|-------|------|--------|
| `intro` | Hook | Kinetic headline with the brand blue accent word, kicker tag |
| `problem` | The pain | Headline + optional flickering keyword chips (e.g., "open rates," "spam," "no replies") |
| `solution` | The fix | Slow zoom/pan over the infographic image |
| `stats` | Proof | 2-3 stacked stat cards with count-up animation |
| `punch` | The payoff | One bold line + accent rule |
| `outro` | CTA | CTA line + pill button + logo sting |

### Step 3 -- Write and Validate content.json

The scene data is written to `content.json` following a strict schema. Headlines are display copy, not the spoken line -- punchy, 3-6 words, with one word wrapped in asterisks for the brand blue accent: `"Cut your AI's workload by *58%*"`. Stats are the centerpiece: 2-3 real numbers from the source as `{value, suffix, label}` objects.

A validator script checks everything before Phase B:
```
node scripts/validate_content.mjs <slug>
```

It catches: voiceText concatenation mismatches, em dashes, agency/university mentions in spoken text, word count outside the 90-130 range, invalid scene types or order, and non-numeric stat values. Fix anything it flags before moving on.

---

## Phase B -- Generate Voice, Align, Preflight, Render, Add Music

Phase B is the automated production pipeline. Five steps run sequentially from the command line. No manual video editing at any point.

### Step 1 -- Generate the Voiceover

A Python script synthesizes the `voiceScript` in Aleem's cloned voice (OmniVoice) and writes the finished `voiceover.wav`:

```
python scripts/generate_voice.py <slug>
```

The tuned recipe is baked into defaults: per-scene chunking (each scene synthesized separately for natural period pauses between scenes), 0.82x speed, 48 inference steps, onset-protected seams at scene boundaries, and a heavy+warm post-process (-0.6 semitones pitch shift, low-shelf EQ, loudness normalization). It also writes `chunks.json` with the exact scene boundaries, which preflight uses to compute scene cuts.

The skill also supports an ElevenLabs fallback: drop a manual `voiceover.mp3` in the reel folder and the pipeline prefers it. Hard-to-pronounce words (e.g., "Claude" -> "Clawd") are handled upstream by a `pronunciation.json` file at synthesis time, so the audio is correct and captions keep the real spelling.

### Step 2 -- Transcribe and Align

A Node.js script converts the voiceover to 16kHz WAV, runs Whisper (`@remotion/install-whisper-cpp`) for word-level timestamps, and writes `captions.json` plus a provisional `timeline.json`:

```
node scripts/prepare.mjs <slug>
```

It defaults to the `medium.en` model for higher accuracy on the processed cloned voice. First run downloads Whisper and the model (a few minutes, one time).

### Step 3 -- Preflight QA Gate

This is the quality engineering layer. A Python script aligns the ground-truth script against the Whisper transcript and fixes everything that used to need hand correction after render:

```
python scripts/preflight.py <slug> --fix
```

It performs four automated corrections:

- **Rebuilds captions from the script.** Whisper sometimes gets words wrong -- "Claude" becomes "Cloud," "AI" gets split, "Cowork" becomes "car work." Preflight replaces the Whisper captions with the ground-truth script text while keeping the correct word-level timestamps. Spelling and casing are always right.
- **Trims phantom words.** Whisper occasionally hallucinates filler words at scene boundaries ("Yes," "Thus," "The" during silence). Preflight detects and removes these audible ghosts.
- **Restores dropped tails.** Sometimes "Follow for more" gets lost at the end. Preflight detects a missing tail and extends the timeline so it is not clipped.
- **Recomputes scene cuts from chunks.json.** Exact boundaries from the synthesis step, not approximate alignment, so every scene transition lands precisely.

Preflight writes `preflight.json` as the gate marker. It exits non-zero if anything is unresolved, which blocks the next step.

### Step 4 -- Render (Gated)

The render script refuses to run unless `preflight.json` says PASSED and the on-disk captions, timeline, and WAV still match what preflight approved (SHA-256 check):

```
node scripts/render.mjs <slug>
```

This prevents the old workflow where you would render, spot a defect, re-render, spot another defect, and waste time chasing ghosts. The gate means you see problems in seconds (preflight) instead of minutes (full render). On success it stamps `out/<slug>.render.json` with the input hashes it built from.

### Step 5 -- Add Background Music

Every reel gets background music mixed under the voice:

```
node scripts/add_music.mjs <slug>
```

The music sits at 25% volume with 0.8s fade-in and 2s fade-out. It automatically ducks to 15% during voice-silent scene gaps (detected via ffmpeg `silencedetect`, padded +/-0.28s), so a music phrase never pops out when the narration pauses. The voice-only render is preserved; the music version is the final deliverable: `out/<slug>-music.mp4`.

---

## What's Built and Working

| Feature | Status |
|---------|--------|
| 6-scene native animation composition (intro, problem, solution, stats, punch, outro) | Live |
| Brand design system (tech-blue gradient, Quiche Sans + Urbanist fonts, circuit-N logo) | Live |
| Cloned-voice voiceover generation (OmniVoice, per-scene chunking) | Live |
| ElevenLabs mp3 fallback | Live |
| Whisper transcription with word-level timestamps (medium.en) | Live |
| TikTok-style synced caption rendering | Live |
| Animated stat counters with count-up animation | Live |
| Infographic image slow-zoom/pan in solution scene | Live |
| Animated node-graph fallback (no infographic needed) | Live |
| Keyword chip animation in problem scene | Live |
| Content validator (voiceText, em dashes, brand voice, word count, scenes) | Live |
| Preflight QA gate (caption rebuild, phantom trim, tail restore, scene cuts) | Live |
| Gated render (blocks unless preflight passed + content hashes match) | Live |
| Background music mix at 25% with silence-gap ducking | Live |
| Pronunciation.json for hard-to-say words | Live |
| Font inlining as base64 (prevents render hangs) | Live |
| Per-reel folder structure (public/reels/<slug>/) | Live |
| Render stamp for music-to-video content matching | Live |
| Multi-reel support (CodeGraph, RAG Chunking, Cold Email Mistakes, Hermes Agent) | Live |

---

## Cost Breakdown

The Reel Creator is designed to be nearly free per run. Most of the pipeline is local compute:

| Step | Service | Cost per Reel |
|------|---------|---------------|
| Voice synthesis | OmniVoice (cloned voice, local) | Free |
| ElevenLabs fallback | ElevenLabs (optional) | ~$0.10 - $0.30 per generation |
| Transcription | Whisper (local, medium.en) | Free |
| Preflight QA | Python (local) | Free |
| Render | Remotion (local Chromium) | Free |
| Music mixing | ffmpeg (local) | Free |
| **Total (standard run)** | | **~$0.00** |
| **Total (ElevenLabs fallback)** | | **~$0.10 - $0.30** |

The only cost is the optional ElevenLabs fallback when Aleem wants hand-tuned studio-quality delivery instead of the cloned voice. At the standard cloned-voice pipeline, the marginal cost of another reel is zero -- just compute time (~2-3 minutes end to end on a modern machine).

Compared to a video editor at $50-100 per reel, the system pays for itself after the first reel.

---

## The Architecture

**Video engine:** Remotion 4.0.471 (React 19, TypeScript) -- renders 9:16 vertical video at 30fps
**Voice synthesis:** OmniVoice (cloned voice, Python) with ElevenLabs fallback
**Transcription:** Whisper cpp (`@remotion/install-whisper-cpp`, medium.en model) -- word-level timestamps
**Audio processing:** ffmpeg (conversion, music mixing, silence detection)
**Validation:** Node.js validator (schema + brand voice rules)
**QA gate:** Python preflight pipeline (caption rebuild, phantom detection, tail restore, scene cut computation)
**Fonts:** Quiche Sans + Urbanist, inlined as base64 data URIs to prevent render hangs
**Brand:** tech-blue gradient (#208EC7 -> #1F5B99), charcoal (#232323), NexusPoint circuit-N logo

**Pipeline commands:**
```
validate_content.mjs <slug>     -> Phase A: validate content.json
generate_voice.py <slug>        -> Phase B: synthesize cloned-voice voiceover.wav
prepare.mjs <slug>              -> Phase B: transcribe -> captions.json + provisional timeline.json
preflight.py <slug> --fix       -> Phase B: QA gate -- fix captions/audio/timeline, write preflight.json
render.mjs <slug>               -> Phase B: render (gated) -> out/<slug>.mp4
add_music.mjs <slug>            -> Phase B: mix background music at 25% -> out/<slug>-music.mp4
```

**Per-reel data:** `public/reels/<slug>/content.json` (script + scenes), `infographic.png` (post image), `voiceover.wav` (synthesized), `captions.json` (Whisper output), `chunks.json` (scene boundaries), `timeline.json` (scene cuts), `preflight.json` (gate marker), `pronunciation.json` (hard words)

---

## End-to-End Walkthrough

Here is what a full reel run looks like, using the CodeGraph reel as an example:

1. Aleem drops an infographic post: a visual about how CodeGraph reduces AI workload by 58%. It has a caption, a source article, and the infographic PNG.

2. Phase A begins. The skill reads the caption and source, picks the slug `codegraph`, and writes a 105-word voice script following the 6-beat arc. Hook: "What if you could cut your AI's workload by 58% without writing a single line of extra code?" It splits the script into 6 scenes, each with a headline and `voiceText` slice. The stats scene pulls two real numbers from the source: 58% workload reduction and 40% fewer tokens.

3. `validate_content.mjs codegraph` passes on the first run. voiceText concatenation matches voiceScript exactly. No em dashes. Word count is 105 -- inside the 90-130 range. All 6 scenes are valid. The infographic is already in the reel folder.

4. Phase B begins. `generate_voice.py codegraph` synthesizes the voiceover in the cloned voice. Per-scene chunking gives natural pauses between scenes. The tuned 0.82x speed lands the audio at 48.1 seconds. `chunks.json` records the exact scene boundaries.

5. `prepare.mjs codegraph` converts to 16kHz WAV, runs Whisper medium.en, and writes word-level captions. The provisional timeline estimates scene cuts from word counts.

6. `preflight.py codegraph --fix` runs the QA gate. It detects "Cloud" in the Whisper captions where "Claude" should be -- fixed from the ground-truth script. No phantom words detected. Tail is intact. Scene cuts are recomputed from chunks.json. PASSED.

7. `render.mjs codegraph` checks the preflight gate, reads the aligned timeline, and renders a 48.3-second 9:16 mp4. The composition reads `timeline.json` for exact scene durations and `captions.json` for word-level caption timing.

8. `add_music.mjs codegraph` picks the first background music track, mixes it at 25% under the voice, ducks to 15% during the two silent scene gaps, fades in over 0.8s and out over 2s. Final deliverable: `out/codegraph-music.mp4`.

Total time: roughly 3 minutes from voice generation to final music mix. Total cost: zero.

---

## The Prospect Takeaway

The Reel Creator is NexusPoint's internal content production engine. Every infographic post in the backlog -- 130+ and counting -- is one command away from becoming a finished motion-graphics reel. The same system has produced reels on CodeGraph, RAG Chunking, Cold Email Mistakes, and Hermes Agent, each with the same brand identity and production quality.

The architecture is not specific to tech content or NexusPoint's brand. The animation composition, voice pipeline, caption sync, and QA gate are a general-purpose short-form video engine. The same system works for:

- **E-commerce brands** turning product photos into 40s feature highlight reels with synced voiceover and animated price/rating cards
- **SaaS companies** converting blog posts and feature launches into motion-graphics explainers with stat-driven proof scenes
- **Real estate agencies** animating property photos with voiceover walkthroughs and spec overlays (sq ft, bedrooms, price)
- **Consulting firms** turning framework diagrams and case studies into thought-leadership reels with pull-quote animations
- **Coaches and course creators** converting lesson snippets and testimonials into short-form social proof reels

Any business with a backlog of static content and a brand voice can run this. Different brand kit. Different voice. Different content. Same pipeline.

If your content team is still manually editing short-form video -- timing captions frame by frame, re-rendering to fix misspellings, and burning hours per reel -- this is what replacing that looks like.

---

*Built and maintained by NexusPoint. Last updated: June 2026.*