# Background music

Tracks mixed under reel voiceovers by `scripts/add_music.mjs`. Drop audio files
here (mp3/wav/m4a/flac/ogg). The audio itself is gitignored (binary/licensed);
this README is the tracked manifest — list new tracks as you add them.

## House setting

Background music plays **under** the voice at **25% volume** (the voice stays at
full level), with a 0.8s fade-in and a 2s fade-out at the end. This is the
default in `add_music.mjs`.

## Usage

```bash
cd projects/reel-engine
node scripts/add_music.mjs <slug>                 # default track + 25%
node scripts/add_music.mjs <slug> gr0za           # pick a track by name substring
node scripts/add_music.mjs <slug> "1000" --volume 0.2
```

Writes `out/<slug>-music.mp4` (keeps the voice-only `out/<slug>.mp4`).
`npm run music -- <slug>` is a shortcut.

## Current tracks

- `1000 Handz - Universal.mp3`
- `gr0za-beat.mp3`
