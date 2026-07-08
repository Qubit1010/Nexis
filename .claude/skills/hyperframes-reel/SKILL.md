---
name: hyperframes-reel
description: >
  Turn an infographic post (caption + source + optional image) into a flagship 9:16 motion-graphics
  reel — dark cinematic style, narrated in Aleem's cloned voice, in the spirit of the ElevenLabs
  inspiration film. This is the HyperFrames-engine alternative to the Remotion reel-creator: it
  DESIGNS a unique reel per post (invents the beat structure from the content) while holding a fixed
  visual genome (charcoal canvas, tech-blue voltage, the gradient orb, the motion doctrine). Use this
  whenever the user wants a "hyperframes reel", a "motion-graphics reel", a reel "like the ElevenLabs
  video / the inspiration", a "cinematic / premium reel", or says "make a reel with hyperframes",
  "turn this post into a motion reel", "reel in the ElevenLabs style", even if they don't name
  HyperFrames. For the established Remotion 6-scene reel pipeline use reel-creator instead; use this
  when the ask is the flowing, continuous-motion, orb-anchored style or explicitly HyperFrames.
---

# HyperFrames Reel

Turn one infographic post into a **9:16 cinematic motion-graphics reel** using the HyperFrames engine,
narrated in Aleem's cloned voice. It is a second visual engine parallel to `reel-creator` (Remotion):
same job, different look. Where reel-creator runs a fixed 6-scene template, this **designs a unique
reel per post** in the style of the inspiration film (`docs/Reel-Inspiration-Motion-Graphics.mp4`) —
flowing, orb-anchored, near-continuous motion.

## The one idea: a genome, not a template

**Read `references/reel-genome.md` first, every time.** It is the persisted DNA — what the inspiration
is, the motion doctrine, and the blueprint palette. The rule that governs everything here:

- **CONSTANT (the genome):** the `nexis-reel` frame preset (charcoal canvas, tech-blue voltage, the
  gradient orb, QuicheSans/Urbanist), the motion doctrine (easing, speed, build/breathe/resolve, ≤1
  hard cut, continuous spine), and the aesthetic bar (fill the frame, scale+blur depth, one focal per
  moment). These make every reel feel like it came from the same studio.
- **FREE (per post):** the entire structure — how many beats, their order, which idea leads, which
  blueprints appear, whether there's a stat beat or a dark interlude. You **read the post and compose
  an original storyboard for it.** Two different posts must produce two structurally different reels.

If you ever catch yourself reaching for "beat 1 is always the logo, beat 6 is always the stat," stop —
that is a template, and templates are exactly what this skill exists to avoid. Let the story decide
the structure; a blueprint earns a place only when the content calls for it (genome §3, §4).

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

Ride the HyperFrames `product-launch-video` machinery — it already does frame presets, per-frame
sub-agent builds, captions, transitions, and rendering. The skill only overrides the preset (ours),
the format (9:16), and the audio (Phase C, not HeyGen). Let `<PLV>` =
`.claude/skills/hyperframes/product-launch-video`.

1. **Init** (if `videos/<slug>/hyperframes.json` is missing):
   `npx hyperframes init "videos/<slug>" --non-interactive --example=blank`
2. **Design system — our preset.** From the project dir, remix the `nexis-reel` preset into the
   project. **Run it with NO `capture/extracted/tokens.json` present** so the preset's palette passes
   through verbatim — the preset already carries the brand, and build-frame's remix assumes a
   light-canvas brand, so feeding it dark-brand tokens would invert the palette:
   `node <PLV>/scripts/build-frame.mjs --preset nexis-reel --hyperframes .`
3. **Build frames.** Dispatch one frame-worker per beat exactly as `<PLV>/SKILL.md` Step 5 describes
   (read `<PLV>/sub-agents/frame-worker.md`). Each worker reads `frame.md` (our preset), its
   `## Frame N` block, and the cited blueprint/rule bodies, and writes `compositions/frames/NN-*.html`.
   **The orb** is the one non-native element — build it in CSS per genome §3 (layered radial-gradient
   + blur, morphed on the seekable timeline via `ambient-glow-bloom` + `sine-wave-loop`).
   Then assemble: `node <PLV>/scripts/assemble-index.mjs --storyboard ./STORYBOARD.md --hyperframes .`
4. **Captions: skip by default.** The inspiration has none. Mark `captions: skipped (inspiration
   style)`. (Only build captions via the optional path in `references/voice-music-bridge.md` if the
   user explicitly wants on-screen word sync.)
5. **Transitions + checks + render SILENT.** Inject transitions, then lint/validate/inspect, then
   render with no audio track:
   `node <PLV>/scripts/transitions.mjs inject --storyboard ./STORYBOARD.md --hyperframes .`
   `npx hyperframes lint && npx hyperframes validate && npx hyperframes inspect`
   `npx hyperframes render --skill=product-launch-video --quality high --output renders/reel-silent.mp4`

**Gate:** `renders/reel-silent.mp4` exists, is 1080×1920, passes lint/validate/inspect, and reads in
the genome's look (dark canvas, blue voltage, the orb, continuous motion, ≤1 hard cut).

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
   `add_music.mjs` refuses to run without its own render stamp):
   `node .claude/skills/hyperframes-reel/scripts/mux_audio.mjs --video videos/<slug>/renders/reel-silent.mp4 --voice projects/reel-engine/public/reels/<slug>/voiceover.wav --music projects/reel-engine/background-music/<track>.mp3 --out videos/<slug>/renders/reel.mp4`
   Voice at full level; music at 25% with a 0.8s fade-in / 2s fade-out, ducked to 15% in voice-silent
   gaps. Sanity-check the bridge anytime with `node .../mux_audio.mjs --selfcheck`.

**Gate:** `videos/<slug>/renders/reel.mp4` exists — 9:16, ~40–45s, voice-synced, music ducked under.

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
- **The orb must attach to the seekable timeline** (`tl.to(...)`, never a bare `gsap.to()`), or it
  won't scrub in the render (motion-principles.md, load-bearing GSAP rules).
- **Fonts.** QuicheSans + Urbanist aren't in the HyperFrames embedded set. Stage the `.woff2` from
  `projects/reel-engine` into the project and add `@font-face`, or the frame-worker falls to a
  geometric sans (never a serif). See `nexis-reel/FRAME.md` Known Gaps.
- **9:16 composition risk.** The inspiration is landscape; the spatial-pan spine is landscape-native.
  In vertical, stack focal moments top/bottom and let the orb own the center (genome §2b, preset
  Aspect-Ratio Behavior). This is the biggest unknown — the render is the real test.
