# Reference voice (OmniVoice cloning)

`scripts/generate_voice.py` clones a voice from a short reference clip to
synthesize reel voiceovers. Drop the reference here:

- `aleem-ref.wav` — a clean **3-10 second** clip of the target voice. One or two
  sentences, no background noise/music, natural pace. WAV preferred (any sample
  rate; mono or stereo is fine).
- `aleem-ref.txt` — *optional* transcript of exactly what's said in the clip.
  If omitted, OmniVoice auto-transcribes it with Whisper.

Override the location per-run with `--ref PATH --ref-text "..."` or the env vars
`REEL_VOICE_REF` / `REEL_VOICE_REF_TEXT`.

To test before recording a real clip, point `--ref` at any existing reel's
voiceover, e.g. `public/reels/codegraph/voiceover.mp3`, then swap in a real
clip later.

The `.wav` clip is gitignored (binary, personal); this README and any `.txt`
transcript are tracked.
