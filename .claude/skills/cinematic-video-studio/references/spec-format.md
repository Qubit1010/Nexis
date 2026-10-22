# spec.json and video-profile.json

## spec.json (one per film, in the film folder; paths relative to it)

```json
{
  "title": "Majlis Question v2",
  "profile": "../../../video-profile.json",
  "out": "concept-2-majlis-question-v2.mp4",
  "shots": [
    {"name": "black", "dur": 0.5},
    {"name": "m01", "dur": 5.0, "trans": ["fade", 0.5], "src": "clips/m01.mp4"},
    {"name": "m02", "dur": 5.5, "trans": ["cut"], "src": "clips/m02.mp4"},
    {"name": "doc1", "dur": 5.6, "trans": ["fade", 0.8], "src": "../../1-pearl-diver/v2/clips/s06.mp4", "slow": 0.9},
    {"name": "s05", "dur": 6.0, "trans": ["cut"], "src": "clips/s05.mp4", "zoom_tail": [3.8, 6.0, 0.5, 0.60, 0.62]},
    {"name": "end", "dur": 4.6, "trans": ["fade", 0.8], "end_card": {}}
  ],
  "lines": [
    {"file": "vo/line-01.mp3", "shot": "m02", "at": 0.5,
     "primary": "يدّه، شوفي…", "secondary": "Grandma, look…", "who": "Granddaughter"},
    {"file": "vo/line-07.mp3", "shot": "end", "at": 0.7}
  ],
  "cards": [
    {"shot": "m01", "from": 1.8, "to": 5.0, "kind": "title", "primary": "سؤال في المجلس", "secondary": "A QUESTION IN THE MAJLIS"},
    {"shot": "s07", "from": 1.6, "to": 5.6, "kind": "label", "primary": "PEPTIDE", "secondary": "ببتيد"},
    {"shot": "doc1", "from": 0.5, "to": 14.7, "kind": "placeholder", "heading": "…", "sub": "…",
     "note": "PLACEHOLDER …\nsecond line", "who": "…", "line_primary": "…", "line_secondary": "…"},
    {"shot": "s08", "from": 1.0, "to": 5.6, "kind": "html", "html": "<div class='lg'>…</div>", "css": ".lg{…}"}
  ],
  "score": {"swell_at": ["doc1", 0.4], "resolve_at": ["m07", 0.3],
            "heartbeat_from": ["s03", 0], "breath": false, "waves": false}
}
```

**Shots**
- `dur` is the seconds used.
- `trans` is how the shot enters: `["cut"]`, `["fade", s]`, `["fadewhite", s]`, or any ffmpeg
  xfade transition.
- `slow` stretches the clip.
- `start` skips into the source.
- `zoom_tail` = `[t0, t1, amount, cx, cy]` pushes in from t0 to t1, toward (cx, cy) as 0-1
  fractions of the frame. Use it to push into an object through a dissolve.
- `end_card: {}` renders the profile's end card. Optional `extra_primary`, `extra_secondary` and
  `qr: true` add a CTA (e.g. "Take the full quiz").
- A first shot named `black` gives a fade-up from black.

**Lines:** timed relative to their shot's start. Lines without `primary` play with no caption
(use this for the end card line, or a voice already shown on a card). Captions fade in and out
and never overlap the next line. `who` is a small speaker label.

**Cards:** times are relative to `shot`'s start and may run past it. Layouts are authored in a
720x1280 space; classes `.rtl`/`.ltr` and the `Brand` font family are available to `html` cards.

**Sound effects and music drop-outs (optional):**
```json
"sfx": [{"type": "ping", "shot": "c01", "at": 0.4}, {"type": "stamp", "shot": "q2", "at": 1.0, "gain": 0.8}],
"score": {"mute": [["c04", 0.2, 3.5]], ...}
```
SFX types: `ping` (phone notification), `stamp` (rubber stamp), `tick` (clock), `whoosh`
(swipe). They are synthesized, so they're licence-safe. `score.mute` silences the music between
two offsets of a shot, with short fades: use it to land a punchline or a reveal in silence.

**Score:** cue points are `[shot, offset]`. `swell_at` places an airy swell (e.g. into a science
world). `resolve_at` places the warm closing chord. `heartbeat_from` adds a soft heartbeat and
underwater rumble from there to `resolve_at`. `breath` and `waves` toggle the opening inhale,
the exhale on resolve, and the sea texture.

## video-profile.json (one per client, in the gitignored client folder)

Required: `brand.primary`, `brand.accent`, `brand.dark`, `brand.logo_png` (raster; old WebKit
ignores SVG sizing), `end_card.lines`, `end_card.footer`, `tag`. Recommended: `brand.font_latin_regular` /
`font_latin_bold` (ttf paths), `brand.font_rtl_family`, `higgsfield.workspace_id`,
`hard_rules`, `guardrails`, `characters` (element ids), `voices` (model, voice_id, pitch),
`reusable_footage`, `music`, `delivery`. Relative paths resolve from the profile's folder.
See `client-projects/primara/cure/video-profile.json` for a complete example.
