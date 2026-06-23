# Voiceover: cloned voice (OmniVoice) — default, with ElevenLabs fallback

The reel voiceover is generated automatically in a **cloned voice** using
[OmniVoice](https://github.com/k2-fsa/OmniVoice) (k2-fsa), a zero-shot
voice-cloning TTS model. This removes the old manual ElevenLabs recording step:
once `content.json` is written and validated, generate the voiceover and go
straight to Phase B.

ElevenLabs is still a fallback — see the bottom of this file.

## One-time setup

Already installed once into an isolated venv at `projects/reel-engine/.venv`:

```bash
cd projects/reel-engine
python -m venv .venv
.venv/Scripts/python.exe -m pip install torch==2.8.0+cu128 torchaudio==2.8.0+cu128 --extra-index-url https://download.pytorch.org/whl/cu128
.venv/Scripts/python.exe -m pip install omnivoice soundfile
```

Hardware here: NVIDIA GTX 1060 6GB. The script uses CUDA (fp16) when available
and falls back to CPU (fp32) automatically. Model weights download from
HuggingFace on first run.

### Reference clip (the voice to clone)

Put a clean **3-10s** clip of the target voice at `projects/reel-engine/voice/aleem-ref.wav`
(one or two sentences, no music/noise). An optional `aleem-ref.txt` with the
exact transcript improves fidelity; if absent, OmniVoice auto-transcribes it.
Override per-run with `--ref PATH --ref-text "..."` or env vars
`REEL_VOICE_REF` / `REEL_VOICE_REF_TEXT`. See `voice/README.md`.

To test before a real clip exists, point `--ref` at any existing reel's
voiceover (e.g. `public/reels/codegraph/voiceover.mp3`).

## Generate the voiceover

After `content.json` passes the validator:

```bash
cd projects/reel-engine
node scripts/validate_content.mjs <slug>          # gate first
python scripts/generate_voice.py <slug>           # writes voiceover.wav + chunks.json
node scripts/prepare.mjs <slug>                   # transcribe (prefers mp3, else wav)
.venv/Scripts/python.exe scripts/preflight.py <slug> --fix   # QA gate: fix + must PASS
node scripts/render.mjs <slug>                    # gated render
```

`generate_voice.py` also writes `public/reels/<slug>/chunks.json` (per-scene audio
spans) which preflight uses for exact scene anchoring + seam-phantom windows.

### Pronunciation map (say hard words right at the source)

`generate_voice.py` respells mapped words for the **TTS input only** before
synthesis, so the clone pronounces them correctly (the cloned voice otherwise says
"Claude" as "code/cloud" and collapses "Claude Code" into "code code"). Display text
and captions keep the real spelling. The map is built-in `{"Claude":"Clawd"}` merged
with `scripts/pronunciation.json` — add an entry there for any new word the clone
mangles, then regenerate. `validate_content.mjs` warns when the script contains a
mapped word so you know it'll be respelled.

(`npm run voice -- <slug>` is a shortcut for the python call.)

`generate_voice.py` writes the **finished** `voiceover.wav` — the locked voice
recipe is baked into the defaults, so no separate audio step is needed:

- **per-scene chunking** — each scene's sentences synthesize together, so periods
  get the model's own natural pause and full word pronunciation. This avoids the
  two artifacts that per-sentence chunking caused: clipped/half-spoken word onsets
  and **phantom filler words** ("This", "Just", "Yes") prepended to tiny isolated
  chunks.
- **0.82 speed, 48 decoding steps** — measured natural pace, cleaner audio.
- **onset-protected seams** — a silent pad + fade ramps over silence (never over
  speech), with a fade-out into each gap, so pauses flow without hiccups.
- **heavy + warm post-process** — −0.6 semitone pitch (tempo preserved), low-shelf
  depth, gentle presence, loudness normalization.

## Tuning the cloned voice

Biggest lever is the **reference clip**: 3-10s, clean, in the style you want.
Then the `generate_voice.py` flags (all default to the locked recipe):

| Flag | Default | What it does | When to change |
|------|---------|--------------|----------------|
| `--pitch-semitones N` | -0.6 | Heaviness (negative = deeper) | -0.8/-1.0 heavier; 0 for natural pitch |
| `--bass-db N` | 3.8 | Low-end depth/warmth | Up for more depth, down if muddy |
| `--loudness-lufs N` | -14.5 | Output loudness | Lower number = louder |
| `--no-post` | (off) | Skip pitch/EQ/loudness entirely | For the raw cloned voice |
| `--speed N` | 0.82 | Speaking pace | Lower = slower; raise if a long script runs over 50s |
| `--num-step N` | 48 | Decoding steps (quality vs speed) | 64 cleaner; 32 faster drafts |
| `--guidance N` | 2.0 | How closely it sticks to your voice | 2.5-3.0 closer; ~1.5 if forced |
| `--temperature N` | 0.0 | Expressiveness (0 = consistent) | 0.3-0.7 livelier |
| `--chunk` | scene | Text splitting | `sentence` for longer forced pauses (watch for phantom fillers); `none` single pass |
| `--gap N` | 0.42 | Silence between scene chunks | Longer = bigger pauses |
| `--language` | English | Language hint | Leave as English |
| `--no-denoise` | (off) | Skip reference denoising | Only if clip is studio-clean |

Other levers (edit the `generate()` call): `duration` (exact seconds), `instruct`
(voice *design* by attributes), `create_voice_clone_prompt()` (precompute the ref).

## Length, quality, captions

- Target 40-50s. Per-scene reads a bit tight; lower `--speed` (e.g. 0.78) to
  stretch, or trim the script if it runs over.
- Whisper re-transcribes in `prepare.mjs`, so captions/scene cuts stay synced
  regardless of how the voice was produced. On the heavier/processed voice Whisper
  mis-hears more often (e.g. "Claude"→"Cloud", a number word, or a filler at a
  gap). Use `--model medium.en` on prepare for better accuracy, then fix any
  remaining tokens in `captions.json` (preserve the timing fields) and re-render.

## ElevenLabs fallback (studio quality)

For a reel where you want hand-tuned ElevenLabs delivery, skip
`generate_voice.py` and drop a `voiceover.mp3` into `public/reels/<slug>/`.
`prepare.mjs` is **mp3-first**: if `voiceover.mp3` exists it transcribes that and
(re)writes `voiceover.wav` from it, so the render (which plays the wav) stays in
sync. A stale generated wav is overwritten. Everything downstream is identical.
