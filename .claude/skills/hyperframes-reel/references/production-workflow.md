# Production Workflow (batch-proven)

The exact end-to-end recipe used to build the reels in `videos/` (ai-os, claude-code-stack,
claude-cowork, local-ai, claude-code-automation, ai-workspace, skillopt). It supersedes the
sub-agent frame-worker flow described in older SKILL.md drafts: **each reel is a single,
hand-authored `videos/<slug>/index.html` with one GSAP timeline** — no per-frame sub-agents, no
`compositions/frames/`, no `build-frame.mjs`/`assemble-index.mjs`. The genome look is reproduced
directly in that file's CSS. This is faster, fully deterministic, and gives exact control over the
signature motif.

## Two entry modes, one method

- **Reclone mode** — recreate an existing old render sitting in a staging folder (e.g.
  `SM Content/Months/July/Videos/reclone/<slug>.mp4`). The slug already exists; the source post is a
  Google Doc. Back up the old file before overwriting.
- **Fresh-from-post mode** — build a brand-new reel from a post (Google Doc, caption + source, or a
  schedule row). No prior render to back up; pick a new kebab-case slug.

Everything after "get the content" is identical. Both produce a per-post-unique reel under the same
fixed genome.

## Step 0 — Get the source content

If the post is a **Google Doc** (the usual case), it often has multiple tabs (LinkedIn / Instagram /
Source / carousel). Pull all tabs:

```bash
gws docs documents get --params '{"documentId": "<ID>", "includeTabsContent": true}' > /c/tmp/<slug>-doc.json
```

Parse with the reel-engine venv (handles the BOM + the stray `Using keyring backend:` first line):

```python
# .venv/Scripts/python.exe
import json
with open(r'C:\tmp\<slug>-doc.json', encoding='utf-8-sig') as f:
    lines = f.readlines()
start = next(i for i,l in enumerate(lines) if l.strip().startswith('{'))
doc = json.loads(''.join(lines[start:]))
# doc['tabs'][*]['documentTab']['body']['content'] → paragraph.elements[].textRun.content
# the "Source" tab is the research/ground-truth; LinkedIn/Instagram tabs are the post copy
```

The **Source tab is ground truth** for numbers/claims; the LinkedIn/Instagram tabs give the voice and
the hook.

## Step 1 — content.json: verify before reuse

A reel-engine `content.json` may already exist at
`projects/reel-engine/public/reels/<slug>/content.json` (old Remotion renders left them behind).
**Do not blindly reuse it.** Read it and check its `voiceScript` + scene claims against the actual
source Doc:

- **Accurate + on-topic + non-empty `voiceScript`** → reuse as-is (local-ai, ai-workspace, skillopt
  all reused cleanly).
- **Empty `voiceScript`, wrong topic, or stale numbers** → write a fresh `content.json` from the real
  Doc text (claude-code-automation had an empty script + mismatched topic and needed a full rewrite).

The `content.json` shape `generate_voice.py` needs is in `voice-music-bridge.md`. House voice rules:
first person, hook in the first 3s, ~90-110 words, no em dashes, no spoken agency/university mention,
soft CTA close. Keep `scenes[].voiceText` as clean per-beat slices — those become the chunk timings.

## Step 2 — Scaffold the project (copy, don't init)

Fastest reliable scaffold is to copy an existing reel's shell (fonts, `.hyperframes`, config) and drop
in a fresh `meta.json`:

```bash
SRC=videos/ai-os ; DST=videos/<slug>
mkdir -p "$DST/renders"
cp -r "$SRC/.hyperframes" "$SRC/.impeccable" "$SRC/assets" "$SRC/AGENTS.md" "$SRC/CLAUDE.md" \
      "$SRC/frame.md" "$SRC/hyperframes.json" "$SRC/package.json" "$DST/"
echo '{"id":"<slug>","name":"<slug>","createdAt":"<ISO>"}' > "$DST/meta.json"
```

`assets/fonts/` carries QuicheSans + Urbanist `.woff2` — the `@font-face` block in `index.html`
references them. Without these the render falls to a geometric sans.

## Step 3 — Kick off the voice IN PARALLEL

Voice generation is the long pole and runs independently of the visual build. Start it in the
background as soon as `content.json` is ready, then design/build while it runs:

```bash
cd projects/reel-engine && .venv/Scripts/python.exe scripts/generate_voice.py <slug>
# → public/reels/<slug>/voiceover.wav + chunks.json  (per-scene startMs/endMs, 420ms inter-chunk gap)
```

(Run with `run_in_background: true`; it takes a couple minutes.)

## Step 4 — Phase A: STORYBOARD.md (the creative gate)

Read `signature-ledger.md`, pick a signature no prior reel used (method in that file), then write
`videos/<slug>/STORYBOARD.md` (format `1080x1920`): the story composed from THIS post, an explicit
"deliberately different from [prior reels]" paragraph, and a per-beat shot sequence. 6 beats is the
proven cadence (hook / tension / signature-peak / proof-or-stats / punch / outro), but let the post
decide. Default **0 hard cuts**; one allowed only for a real sever/break beat.

## Step 5 — Phase B: build index.html (single file, one timeline)

Write `videos/<slug>/index.html` directly. The reliable structure (copy an existing reel's file as the
skeleton and re-skin the scene bodies):

- **Head:** the `@font-face` block, the genome CSS (`.bg-base/.bg-grid/.bg-wash`, `.kicker/.display/
  .volt/.sub/.pill/.handle`), then per-signature custom classes.
- **Root:** `<div id="root" data-composition-id="main" data-start="0" data-duration="<END>" ...>`.
- **Each timed element** needs `class="clip"` + `data-start` + `data-duration` + **a unique
  `data-track-index`**. See the track-index rule below — it is the #1 source of lint errors.
- **One GSAP timeline**, paused, registered on `window.__timelines["main"]`. Define scene-start
  constants `const S1=0, S2=..., ... END=...;` and place every tween relative to them. Animate on the
  **seekable** timeline (`tl.fromTo(...)`, never a bare `gsap.to()`), or it won't scrub in the render.
- **Background is a through-line** (tracks 0/1/2, full duration); the wash drifts beat-to-beat for a
  continuous spine.

**Track-index rule (load-bearing):** every element visible *at the same time* needs its own unique
`data-track-index`. Elements in *different scenes* (non-overlapping time) may reuse indices. Assign
each scene's simultaneous elements consecutive indices (e.g. scene uses 5..15). Violating this throws
`overlapping_clips_same_track` at lint. Static children *inside* a `clip` parent (doc lines, box
labels) don't need their own attributes — they inherit the parent's visibility, and you can still
animate them by selector with GSAP.

**The orb is optional.** The genome lists a gradient orb, but most of these reels dropped it
(claude-code-stack, claude-cowork, claude-code-automation, skillopt have none) and let voltage live in
the signature device, the kinetic keyword, and the CTA. Use the orb only if the post wants a central
anchor; never force it.

Then lint + full check:

```bash
cd videos/<slug> && npx hyperframes lint && npx hyperframes check
```

`timeline_track_too_dense` warnings are advisory (fine to ship). Fix all **errors**. `check` also runs
a WCAG-AA contrast pass — fix real low-contrast text, but intentionally-faint decorative elements
(e.g. skillopt's near-invisible "?" that signals an opaque black box) are legitimately left as-is.
An occasional `check_runtime_failure: Navigation timeout` is a transient flake — just re-run.

## Step 6 — Phase C part 1: sync durations from chunks.json

Once `chunks.json` exists, set each scene's start to its chunk `startMs/1000` and its duration to the
next scene's start minus its own (so visuals hold through the inter-chunk gap). Update: the JS
`S1..S6/END` constants **and** every element's `data-start`/`data-duration`, then re-`check`.

When doing this with `Edit(replace_all=...)` on the raw attribute strings, order the replacements so no
old value is a **prefix** of a value you just created (e.g. replace `data-duration="7.5"` before
`data-duration="7"`, and `data-duration="5"` before creating `5.407`). Otherwise the shorter match
corrupts the longer one.

## Step 7 — Phase B render: silent, in background, ffmpeg on PATH

```bash
export PATH="/c/tmp/hf-ffmpeg-bin:$PATH"   # ffmpeg-static v6 + Remotion's ffprobe.exe (see SKILL Gotchas)
cd videos/<slug> && npx hyperframes render --skill=product-launch-video --quality high \
  --output renders/reel-silent.mp4
```

Run with `run_in_background: true` (a ~40s reel renders in ~2min, past the Bash 120s cap).

## Step 8 — QA-frame gate (mandatory — catches what lint can't)

Lint/check pass compositions that still have **layout bugs** (text overflowing a box, elements
colliding, a beat that reads wrong). Always extract still frames at each beat and *look* at them
before muxing. Use reel-engine's **ffmpeg-static binary directly** for frame grabs — Remotion's
ffprobe.exe fails standalone with a `swscale-8.dll` error:

```bash
FFMPEG=projects/reel-engine/node_modules/ffmpeg-static/ffmpeg.exe
for t in 3 7 11 15 18 24 27 31 34 38; do   # ~1 per beat, extra on the signature beat
  "$FFMPEG" -y -loglevel error -ss $t -i renders/reel-silent.mp4 -frames:v 1 <scratch>/f_$t.png
done
```

Read every frame. Bugs this gate has caught that lint missed: ai-workspace's punch text overflowing
its panel/seam box (fixed by dropping the box for a bare full-screen slam + a thin voltage underline);
claude-code-stack visual bugs; and track-collision fallout. If you find a bug, fix the HTML, re-render
silent, re-inspect. Only proceed once every beat reads clean.

**impeccable hook:** the PostToolUse hook flags `.volt` gradient-text and the dark-glow box-shadows on
every reel. These are intentional, load-bearing genome brand-skin elements — leave them unchanged, no
`impeccable: ignore` comments, no persisted exception (the user has not asked to suppress them). The
hook auto-suppresses after ~6 edits to the same file.

## Step 9 — Phase C part 2: mux voice + ducked music

Established default track + level for this batch: `6-track-mirostar-rap` at `--volume 0.20`.

```bash
node .claude/skills/hyperframes-reel/scripts/mux_audio.mjs \
  --video videos/<slug>/renders/reel-silent.mp4 \
  --voice projects/reel-engine/public/reels/<slug>/voiceover.wav \
  --music projects/reel-engine/background-music/6-track-mirostar-rap.mp3 \
  --volume 0.20 \
  --out   videos/<slug>/renders/reel.mp4
```

Voice full; music at the given base, ducked further in voice-silent gaps, 0.8s fade-in / 2s fade-out.
Verify the final file with ffmpeg-static (`-hide_banner -i <file>` → confirm ~9:16 1080x1920, h264 +
aac, duration ≈ the voice length).

## Step 10 — Deliver

- **Reclone mode:** back up the old render first (`cp reclone/<slug>.mp4 reclone/<slug>-original-june.mp4`),
  then copy the new `reel.mp4` over `reclone/<slug>.mp4`.
- **Fresh mode:** copy `reel.mp4` wherever the user wants it.
- **Append a row to `signature-ledger.md`** for the signature you just used.
- Report: signature motif, why it's structurally distinct from the prior reels, and final specs
  (duration, 1080x1920, h264/aac, voice + music @ 0.20).

Then apply the repo's closeout/push prompt rule.
