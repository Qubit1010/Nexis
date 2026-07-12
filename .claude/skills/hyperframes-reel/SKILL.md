---
name: hyperframes-reel
description: >
  Turn an infographic post (caption + source + optional image) into a flagship 9:16 motion-graphics
  reel — dark cinematic style, narrated in Aleem's cloned voice, in the spirit of the ElevenLabs
  inspiration film. Works two ways: RECLONE an existing old render from its source Doc, or build FRESH
  from a post — both run the same pipeline. This is the HyperFrames-engine alternative to the Remotion
  reel-creator: it DESIGNS a unique reel per post (invents the beat structure AND a never-repeated
  signature motif from the content) while holding a fixed visual genome (charcoal canvas, tech-blue
  voltage, QuicheSans/Urbanist, the motion doctrine). Use this whenever the user wants a "hyperframes
  reel", a "motion-graphics reel", a reel "like the ElevenLabs video / the inspiration", a "cinematic
  / premium reel", to "reclone" a video into the premium style, or says "make a reel with
  hyperframes", "turn this post into a motion reel", "reel in the ElevenLabs style", even if they
  don't name HyperFrames. For the established Remotion 6-scene reel pipeline use reel-creator instead;
  use this when the ask is the flowing, continuous-motion, premium style or explicitly HyperFrames.
---

# HyperFrames Reel

Turn one infographic post into a **9:16 cinematic motion-graphics reel** using the HyperFrames engine,
narrated in Aleem's cloned voice. It is a second visual engine parallel to `reel-creator` (Remotion):
same job, different look. Where reel-creator runs a fixed 6-scene template, this **designs a unique
reel per post** in the style of the inspiration film (`docs/Reel-Inspiration-Motion-Graphics.mp4`) —
flowing, near-continuous motion.

## Two entry modes, one method

- **Reclone mode** — recreate an existing old render (e.g. an item in
  `SM Content/Months/July/Videos/reclone/<slug>.mp4`) from its source Google Doc, with the premium
  HyperFrames look. Back up the old file before overwriting.
- **Fresh-from-post mode** — build a brand-new reel from a post (Doc, caption + source, or schedule
  row). Pick a new kebab-case slug.

Both run the **identical** pipeline and both produce a per-post-unique reel under the same fixed
genome. The concrete, batch-proven, step-by-step recipe (Doc extraction, verify-before-reuse,
scaffold, parallel voice, build, duration-sync, render, QA-frame gate, mux, deliver) lives in
**`references/production-workflow.md` — follow it for any reclone or fresh build.** This SKILL.md is
the doctrine; that file is the runbook.

## The one idea: a genome, not a template

**Read `references/reel-genome.md` first, every time.** It is the persisted DNA — what the inspiration
is, the motion doctrine, and the blueprint palette. The rule that governs everything here:

- **CONSTANT (the genome):** the `nexis-reel` frame preset (charcoal canvas, tech-blue voltage,
  QuicheSans/Urbanist), the motion doctrine (easing, speed, build/breathe/resolve, ≤1 hard cut,
  continuous spine), and the aesthetic bar (fill the frame, scale+blur depth, one focal per moment).
  These make every reel feel like it came from the same studio. (The gradient orb is a genome
  *device*, not a mandate — most reels drop it and let voltage live in the signature; use it only when
  a post wants a central anchor.)
- **FREE (per post):** the entire structure — how many beats, their order, which idea leads, which
  devices appear, and above all **the signature motif** (the central object/world the reel is built
  around). You **read the post and compose an original storyboard for it.** Two different posts must
  produce two structurally different reels.

**The signature is the uniqueness lever, and it must never repeat.** Each reel gets one central visual
device invented from the post's own subject (an OS badge, a severed perimeter + chip, a breaking UI vs
a connector hub, a panel that transforms, a text document under a validation gate...). Before you
design, **read `references/signature-ledger.md`** — it lists every signature already used and how to
pick a fresh one; **after you ship, append your new signature to it.** That ledger is what keeps the
batch feeling bespoke rather than same-y.

If you ever catch yourself reaching for "beat 1 is always the logo, beat 6 is always the stat," stop —
that is a template, and templates are exactly what this skill exists to avoid. Let the story decide
the structure; a device earns a place only when the content calls for it (genome §3, §4).

## What you need (inputs)

1. **Caption / copy** — the post's text. Required.
2. **Source / research** — where the post came from (article, repo, benchmark, Aleem's take). Grounds
   the script and any numbers in real specifics. Required (ask if missing).
3. **Infographic image** — optional but preferred; becomes a UI/panel moment. Can be dropped in later.

Same house rules as reel-creator (the spoken copy): first person, hook in the first 3s, ~90–110 words
for ~40–45s, **no em dashes**, **no agency name / no university mention** in the spoken copy (the logo
sting at the end is fine, it's not spoken), soft CTA to close. See reel-creator's
`references/voice-script.md` for the script craft — reuse it; only the visual engine differs here.

---

## Phase A — Design the reel (the creative part)

This is where the skill earns its name. Work in a HyperFrames project at `videos/<slug>/` (pick a
short kebab-case slug from the topic).

1. **Read the post and `references/reel-genome.md`.** Find the one idea, the hook, and what the
   content actually contains — a number worth a count-up? a system worth a flow graph? a "too much →
   here's the fix" tension worth the one hard cut? a list? Let that inventory decide the devices.
2. **Draft the energy curve, not a beat list.** Build → climax → resolve (genome §1, §4). Decide
   where the peak is and let the outro resolve to the brand lockup. Beats hold ~3–5s; 6–9 beats for a
   40–45s reel is typical, but the count is yours to choose per post.
3. **Write the voice script** (reel-creator's `voice-script.md` method) and split it per beat — one
   `voiceText` slice per beat. Save it as reel-engine `content.json` for the voice bridge (Phase C).
   **If a `content.json` already exists** for the slug (old renders leave them behind), verify it
   against the source before reusing — accurate + on-topic + non-empty `voiceScript` → reuse as-is;
   empty script, wrong topic, or stale numbers → rewrite from the real source. (production-workflow
   Step 1.)
4. **Compose the storyboard** — assign each beat a device from the genome §3 palette (only what the
   story needs), in whatever order the story wants. This is HyperFrames' Step 3 + Step 4: write
   `STORYBOARD.md` (format `1080x1920`) with a time-coded shot sequence per frame, picking blueprints
   from `../hyperframes/hyperframes-animation/blueprints-index.md` and motion from
   `rules-index.md` — do not invent motion names. Thread a continuous-camera / morph spine so the
   reel reads as one flowing piece with ≤1 hard cut.

Follow the HyperFrames method docs for the mechanics (don't duplicate them here):
`../hyperframes/product-launch-video/references/story-design.md` (story/hook/beats),
`.../references/visual-design.md` (the time-coded shot sequence + `## Video direction`),
`.../references/motion-language.md` (motion doctrine), and
`../hyperframes/hyperframes-core/references/storyboard-format.md`.

**Gate:** `STORYBOARD.md` (1080x1920) exists with a per-beat shot sequence; the structure was
composed from THIS post (not a fixed template); a per-beat `content.json` is written for the voice.

---

## Phase B — Build the visuals (HyperFrames, silent)

**Proven method: one hand-authored `videos/<slug>/index.html` with a single GSAP timeline.** Not the
per-frame sub-agent flow — across the built batch, a single self-contained file (genome CSS + custom
signature classes + one paused timeline registered on `window.__timelines["main"]`) is faster, fully
deterministic, and gives exact control over the signature motif. Copy an existing reel's `index.html`
as the skeleton and re-skin the scene bodies. Full mechanics (track-index rule, the seekable-timeline
requirement, scene-start constants, background through-line) are in **`references/production-workflow.md`
Step 5** — read it before building.

The load-bearing rule while building: **every element visible at the same time needs a unique
`data-track-index`** (elements in different, non-overlapping scenes may reuse indices). Violating it
throws `overlapping_clips_same_track` at lint. Animate on the seekable timeline (`tl.fromTo(...)`,
never a bare `gsap.to()`) or it won't scrub in the render.

1. **Scaffold** by copying an existing reel's shell (fonts, `.hyperframes`, config) + a fresh
   `meta.json` — see production-workflow Step 2. (Fonts must be staged or the render falls to a
   geometric sans.)
2. **Write `index.html`** — genome CSS, per-signature custom classes, one timeline. Captions: skip by
   default (inspiration style); only build them via `references/voice-music-bridge.md` if the user
   explicitly wants on-screen word sync.
3. **Lint + check:** `cd videos/<slug> && npx hyperframes lint && npx hyperframes check`. Fix all
   **errors**; `timeline_track_too_dense` is advisory. The contrast pass may warn on intentionally
   faint decorative elements — those are fine. A `check_runtime_failure: Navigation timeout` is a
   transient flake; re-run.
4. **Render SILENT** in the background with ffmpeg on PATH:
   `export PATH="/c/tmp/hf-ffmpeg-bin:$PATH"` then
   `npx hyperframes render --skill=product-launch-video --quality high --output renders/reel-silent.mp4`
   (`run_in_background: true` — a ~40s reel renders past the Bash 120s cap).

**Gate:** `renders/reel-silent.mp4` exists, is 1080×1920, passes lint/check, and reads in the genome's
look (dark canvas, blue voltage, continuous motion, ≤1 hard cut).

### The QA-frame gate (mandatory before muxing)

Lint/check pass compositions that still have **layout bugs** (text overflowing a box, colliding
elements, a beat that reads wrong). **Extract a still per beat and look at every one before you mux.**
Use reel-engine's ffmpeg-static binary directly (Remotion's ffprobe.exe fails standalone with a
`swscale-8.dll` error):

```bash
FFMPEG=projects/reel-engine/node_modules/ffmpeg-static/ffmpeg.exe
for t in 3 7 11 15 18 24 27 31 34 38; do   # ~1 per beat, extra on the signature beat
  "$FFMPEG" -y -loglevel error -ss $t -i renders/reel-silent.mp4 -frames:v 1 <scratch>/f_$t.png
done
```

Read each frame. This gate has caught real bugs lint missed (e.g. ai-workspace's punch text
overflowing its box → fixed to a bare full-screen slam). Fix the HTML, re-render silent, re-inspect;
proceed only when every beat reads clean.

---

## Phase C — Voice + music bridge (reel-engine audio onto the silent reel)

HyperFrames can't produce Aleem's OmniVoice clone, so reel-engine owns all audio. This is the one real
integration — full detail in `references/voice-music-bridge.md`; the essence:

1. **Generate the cloned voice.** Put the Phase-A `content.json` (with `voiceScript` + per-beat
   `scenes[].voiceText`) at `projects/reel-engine/public/reels/<slug>/content.json`, then:
   `cd projects/reel-engine && .venv/Scripts/python.exe scripts/generate_voice.py <slug>`
   → writes `voiceover.wav` + `chunks.json` (per-beat audio durations).
2. **Sync visuals to the voice.** Set each `STORYBOARD.md` frame's `duration` to its beat's
   voice-chunk length from `chunks.json`, then rebuild + re-render the silent reel (Phase B.3–B.5) so
   the visuals land on the voice. (Do this once the voice exists; on the first pass you can estimate
   durations from word counts and re-sync here.)
3. **Mux voice + ducked music** onto the silent reel with the skill's ungated bridge (reel-engine's
   `add_music.mjs` refuses to run without its own render stamp). **Batch default: track
   `6-track-mirostar-rap` at `--volume 0.20`** (unless the user asks for a different track/level):
   `node .claude/skills/hyperframes-reel/scripts/mux_audio.mjs --video videos/<slug>/renders/reel-silent.mp4 --voice projects/reel-engine/public/reels/<slug>/voiceover.wav --music projects/reel-engine/background-music/6-track-mirostar-rap.mp3 --volume 0.20 --out videos/<slug>/renders/reel.mp4`
   Voice at full level; music at the given base with a 0.8s fade-in / 2s fade-out, ducked further in
   voice-silent gaps. Sanity-check the bridge anytime with `node .../mux_audio.mjs --selfcheck`.
   Then verify the final file with ffmpeg-static (`-hide_banner -i <file>` → ~9:16 1080x1920, h264 +
   aac, duration ≈ voice length).

**Gate:** `videos/<slug>/renders/reel.mp4` exists — 9:16, ~40–45s, voice-synced, music ducked under.

**Deliver (reclone):** back up the old render (`cp reclone/<slug>.mp4 reclone/<slug>-original-<tag>.mp4`)
before overwriting `reclone/<slug>.mp4`. **Append the signature you used to `references/signature-ledger.md`.**

---

## Verify (the creativity + quality check)

- **Genome holds:** dark charcoal canvas (not the inspiration's light), tech-blue voltage, the orb
  reads, QuicheSans/Urbanist, continuous motion with ≤1 hard cut. Run the preset's Pre-Render
  Self-Audit (in `nexis-reel/FRAME.md`) and the motion doctrine checklist (genome §2b).
- **Creativity:** the structure was composed from this post. If you built two reels, confirm they are
  structurally different (different beats/order/blueprints), not one template refilled.
- **Deliver** `renders/reel.mp4` plus a one-line summary (length, that it's brand-styled + voice-synced
  + ducked music) and a one-line note on the structure you invented and why it fit the post.

## Reference files

- `references/production-workflow.md` — **the runbook.** The exact batch-proven step-by-step for any
  reclone or fresh build: Doc extraction, verify-before-reuse, scaffold, parallel voice, single-file
  build, duration-sync, render, QA-frame gate, mux, deliver. Read it before building.
- `references/signature-ledger.md` — **read before designing, append after shipping.** Every signature
  motif already used + how to pick a fresh one. This is what keeps each reel unique.
- `references/reel-genome.md` — **read first, every reel.** The DNA: inspiration cores, motion
  doctrine, blueprint palette, and how to compose a reel from a post.
- `references/voice-music-bridge.md` — the exact `content.json` shape `generate_voice.py` needs, the
  duration-sync step, the mux command, and the optional on-screen-caption path.
- `nexis-reel` preset — `../hyperframes/hyperframes-creative/frame-presets/nexis-reel/FRAME.md`
  (the brand skin; owns the look). Motion doctrine:
  `../hyperframes/hyperframes-creative/references/motion-principles.md` (read in full before building
  frames — the load-bearing GSAP rules live there).
- `scripts/mux_audio.mjs` — the audio bridge (voice full + ducked music onto the silent reel).

## Gotchas

- **ffmpeg must be on PATH for the render, and the build matters.** `npx hyperframes render` needs
  both `ffmpeg` and `ffprobe` on PATH. Remotion's bundled ffmpeg v7
  (`projects/reel-engine/node_modules/@remotion/compositor-win32-x64-msvc/`) **rejects** HyperFrames'
  `pad=ceil(iw/2)*2:...` filter string ("No option name near..."). Fix: make a combined bin dir with
  reel-engine's **ffmpeg-static v6** (`node_modules/ffmpeg-static/ffmpeg.exe`, which parses the filter)
  plus Remotion's `ffprobe.exe`, and prepend it: `export PATH="/c/tmp/hf-ffmpeg-bin:$PATH"` before the
  render. (The skill's `mux_audio.mjs` only uses ffmpeg-static and is unaffected.) Proven on the
  kw-plugins reel.
- **Bash-tool 2-min limit vs. a ~90s render.** A full 37s reel renders in ~90s; run the render with
  `run_in_background: true` so the tool's own 120s cap doesn't kill it mid-capture.
- **Don't remix the preset onto dark-brand tokens.** build-frame's role mapping assumes a light
  canvas; run it with no `tokens.json` so the `nexis-reel` palette passes through (Phase B.2).
- **Everything must attach to the seekable timeline** (`tl.fromTo(...)`, never a bare `gsap.to()`), or
  it won't scrub in the render (motion-principles.md, load-bearing GSAP rules).
- **Unique `data-track-index` per simultaneously-visible element.** Two elements on the same track
  index visible at the same time throw `overlapping_clips_same_track`. Give each scene's concurrent
  elements consecutive unique indices; different (non-overlapping) scenes may reuse them.
- **Use ffmpeg-static directly for QA frame grabs.** Remotion's `ffprobe.exe` in the combined bin dir
  fails standalone with `swscale-8.dll: cannot open shared object file`. Grab frames with
  `projects/reel-engine/node_modules/ffmpeg-static/ffmpeg.exe -ss <t> -i <mp4> -frames:v 1 out.png`.
- **Prefix-safe duration-sync edits.** When `replace_all`-ing raw `data-duration`/`data-start` values,
  order replacements so no old value is a prefix of one you just created (replace `"7.5"` before
  `"7"`; replace `"5"` before creating `"5.407"`), or the short match corrupts the long one.
- **impeccable hook findings are intentional.** The `.volt` gradient-text and dark-glow box-shadows are
  load-bearing genome brand-skin elements — leave them unchanged, no `impeccable: ignore` comments, no
  persisted exception (unless the user explicitly asks to suppress). The hook auto-suppresses after ~6
  edits to the same file.
- **Fonts.** QuicheSans + Urbanist aren't in the HyperFrames embedded set. Stage the `.woff2` from
  `projects/reel-engine` into the project (`assets/fonts/`) and add `@font-face`, or it falls to a
  geometric sans (never a serif). Copying an existing reel's shell (production-workflow Step 2) carries
  them automatically. See `nexis-reel/FRAME.md` Known Gaps.
- **9:16 composition risk.** The inspiration is landscape. In vertical, stack focal moments
  top/bottom and keep one focal element per beat, filling the frame (genome §2b, preset Aspect-Ratio
  Behavior). The QA-frame gate is where composition problems surface — always run it.
