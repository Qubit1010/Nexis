# Voice + Music Bridge

HyperFrames renders the reel **silent**; reel-engine owns **all audio** (it has Aleem's OmniVoice
clone, which HyperFrames' HeyGen/local TTS cannot produce). This is the one real integration between
the two engines. Three moving parts: generate the voice, sync the visuals to it, mux voice + music.

## 1. Generate the cloned voice

`generate_voice.py` reads a reel-engine `content.json` and synthesizes the cloned voice, chunked
per beat. It needs only two fields — **not** reel-engine's fixed 6-scene reel schema, so beat ids are
free:

```jsonc
// projects/reel-engine/public/reels/<slug>/content.json
{
  "voiceScript": "The full spoken script, exactly as narrated, start to end.",
  "scenes": [
    { "id": "hook",        "voiceText": "The full spoken script, " },
    { "id": "problem",     "voiceText": "exactly as narrated, " },
    { "id": "payoff",      "voiceText": "start to end." }
  ]
}
```

**Hard rule:** concatenating `scenes[].voiceText` in order must equal `voiceScript` **character for
character** — that is what lets the per-beat chunk offsets line up with the audio. One `scenes` entry
per storyboard beat; the `id` is your beat name (it flows through to `chunks.json` as `sceneId`).

Do **not** run reel-engine's `validate_content.mjs` here — it enforces the 6 fixed reel scene types
(intro/problem/solution/stats/punch/outro), which don't apply to a per-post HyperFrames reel. The
only house-voice checks that still apply are the spoken-copy rules (no em dashes, no agency/university
mention, ~90–110 words); apply them by hand when writing the script.

Then:

```bash
cd projects/reel-engine
.venv/Scripts/python.exe scripts/generate_voice.py <slug>
```

Outputs into `public/reels/<slug>/`:
- `voiceover.wav` (24 kHz, finished — post-processed heavy+warm, the house default).
- `chunks.json` — per-beat audio spans:
  `{ "sampleRate": 24000, "gapMs": 420, "scenes": [ { "sceneId, "startMs", "endMs", ... } ] }`.
  **Per-beat duration = `endMs − startMs`** (seconds = `/1000`).

Length/tuning flags (`--speed`, `--pitch-semitones`, `--no-post`, …) are documented in reel-creator's
`references/voice-cloning.md`. Default speed 0.82 reads a touch tight; lower it to stretch.

## 2. Sync the visuals to the voice

The visuals must land on the narration. Set each `STORYBOARD.md` frame's `duration` to its beat's
voice-chunk length from `chunks.json` (`(endMs − startMs)/1000`, round to a sensible frame boundary),
then rebuild + re-render the silent reel (SKILL Phase B.3–B.5).

On the **first** pass you can estimate beat durations from word counts to get a rough cut, then
regenerate the voice and re-sync here for the final. reel-engine already proves this pattern
(`chunks.json` drives its scene cuts); the difference is you hand the durations to HyperFrames'
storyboard rather than to Remotion.

> HyperFrames' own `audio.mjs sync-durations` is for its HeyGen `audio_meta.json` — it won't read
> reel-engine's `chunks.json`. Set the storyboard durations directly from `chunks.json` instead.

## 3. Mux voice + ducked music

reel-engine's `add_music.mjs` refuses to run without its own render stamp (it guards against muxing
onto a stale Remotion render), so the skill ships an **ungated** port that works on any mp4:

```bash
node .claude/skills/hyperframes-reel/scripts/mux_audio.mjs \
  --video videos/<slug>/renders/reel-silent.mp4 \
  --voice projects/reel-engine/public/reels/<slug>/voiceover.wav \
  --music projects/reel-engine/background-music/<track>.mp3 \
  --out   videos/<slug>/renders/reel.mp4
```

- Voice at full level; music at 25% (`--volume` to change), 0.8s fade-in / 2s fade-out.
- Music **ducks to 15%** during voice-silent gaps (silencedetect + a per-gap volume envelope, ported
  verbatim from `add_music.mjs`) so a music phrase never swells when the narration pauses.
- ffmpeg: uses reel-engine's bundled `ffmpeg-static` automatically; override with `--ffmpeg <path>`.
- Sanity-check the bridge without real assets: `node .../mux_audio.mjs --selfcheck`.

Pick a `<track>` from `projects/reel-engine/background-music/` (any `.mp3`).

## Optional — on-screen word-synced captions

The inspiration film has **no captions**, so the skill skips them by default. If the user explicitly
wants word-synced captions, transcribe the voiceover and feed HyperFrames' caption pipeline:

1. `cd projects/reel-engine && node scripts/prepare.mjs <slug>` → `captions.json` (word timestamps).
2. Hand-build HyperFrames' frame-keyed `audio_meta.json`
   (`{ "voices": [ { "frame": "NN", "path": "...", "duration_s": N, "words": [...] } ] }`) from
   `captions.json`, then run `<PLV>/scripts/captions.mjs build`. The `nexis-reel` preset already ships
   a dark caption skin (`caption-skin.html`) that build-frame stages into the project.

This is the "tighter" path in the plan; default to the no-caption primary path unless asked.
