# Reel Engine

Turns NexusPoint infographic posts into 9:16, 40-50s motion-graphics reels with
an ElevenLabs voiceover synced to brand-styled animation (Remotion).

Each reel is hybrid native scenes: branded intro -> problem -> brief infographic
hero -> animated stat counters -> punch line -> CTA + logo sting, with TikTok-style
captions that ride the exact word timings of the voiceover.

Brand: tech-blue gradient identity from `brand-assets/brand-guidelines.md`
(`#208EC7 -> #1F5B99`, charcoal `#232323`), Quiche Sans (display) + Urbanist (body),
NexusPoint circuit-N logo.

## Per-reel workflow

A reel lives in `public/reels/<slug>/`. Inputs you provide: `content.json`
(script + scenes), `infographic.png` (the post image), `voiceover.mp3` (from
ElevenLabs). Generated: `captions.json`, `timeline.json`.

1. **Write the content** — `public/reels/<slug>/content.json`
   (the `reel-creator` skill generates this from an infographic + caption + source).
   `scenes[].voiceText` concatenated in order must equal `voiceScript` exactly.

2. **Preview the visuals (optional, no audio needed)**
   ```bash
   npm run studio
   ```
   Set the composition's `slug` prop to your reel in the Studio sidebar. Timing is
   estimated from word counts until the audio is aligned.

3. **Record the voiceover** — paste `voiceScript` into ElevenLabs, export, and save
   the file as `public/reels/<slug>/voiceover.mp3`. Also drop the post's
   `infographic.png` into the same folder.

4. **Sync** — transcribe + align scenes to the audio:
   ```bash
   node scripts/prepare.mjs <slug>          # default model: base.en
   node scripts/prepare.mjs <slug> --model medium.en   # higher accuracy
   ```
   Writes `captions.json` and an aligned `timeline.json`.

5. **Render**
   ```bash
   npx remotion render Reel out/<slug>.mp4 --props='{"slug":"<slug>"}'
   ```

## How sync works

`scripts/prepare.mjs` converts the mp3 to 16kHz wav (via `ffmpeg-static`),
transcribes it with Whisper (`@remotion/install-whisper-cpp`, word-level
timestamps), writes word captions, then anchors each scene to the first two words
of its `voiceText` in the transcript. `Root.tsx#calculateMetadata` reads the
aligned `timeline.json` (falling back to a word-count estimate when absent) and
sets the composition duration from it.

## Notes

- First `prepare.mjs` run downloads Whisper + model (a few minutes, one time).
- First `remotion render` downloads a headless Chromium (one time).
- No infographic yet? The Solution scene shows an animated node-graph fallback.
