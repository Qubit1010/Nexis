/**
 * add_music.mjs <slug> [trackQuery] [--volume 0.25]
 *
 * Mixes a background-music track UNDER the rendered reel voiceover and writes
 * out/<slug>-music.mp4. The voice stays at full level; the music sits quietly
 * beneath it with a short fade-in and a fade-out at the end.
 *
 *   node scripts/add_music.mjs content-curation                 # default track + 25%
 *   node scripts/add_music.mjs content-curation gr0za           # pick a track by name
 *   node scripts/add_music.mjs content-curation "1000" --volume 0.2
 *
 * Tracks live in projects/reel-engine/background-music/ (mp3/wav/m4a/flac/ogg).
 * Default volume is 25% (the house level for reels).
 */
import path from "path";
import fs from "fs";
import crypto from "crypto";
import { fileURLToPath } from "url";
import { execFileSync, spawnSync } from "child_process";
import ffmpegPath from "ffmpeg-static";

const DEFAULT_VOLUME = 0.25;
const FADE_IN = 0.8;   // seconds
const FADE_OUT = 2.0;  // seconds
const AUDIO_EXT = [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac"];

// Music ducking during voice-silent scene gaps. When the narrator pauses between
// scenes there is no voice to mask the music, so a phrase in the track pops out
// right before the next word ("weird sound before the next word"). We detect those
// pauses from the actual voiceover and dip the music there so it never swells in a gap.
const DUCK_GAIN = 0.15;    // music multiplier during a gap (15% of its level)
const DUCK_FADE = 0.15;    // seconds to ramp the dip in/out (click-free)
const DUCK_MIN_GAP = 0.30; // only duck silences at least this long (skips word pauses)
const DUCK_NOISE_DB = -50; // below this is treated as silence (gaps are ~ -inf dB)
const DUCK_PAD = 0.28;     // widen each gap by this on both sides — the music swells
                           // that pop out sit just OUTSIDE the detected silence (the
                           // voice tail/onset keeps the edges above the threshold), so
                           // the duck must reach into them. Ducking under the voice's
                           // own tail/onset is harmless (music belongs under the voice).

// Detect interior voice-silent gaps in the voiceover via ffmpeg silencedetect.
function detectGaps(voicePath, durationS) {
  if (!fs.existsSync(voicePath)) return [];
  const det = spawnSync(
    ffmpegPath,
    ["-hide_banner", "-i", voicePath, "-af", `silencedetect=noise=${DUCK_NOISE_DB}dB:d=${DUCK_MIN_GAP}`, "-f", "null", "-"],
    { encoding: "utf8" }
  );
  const log = `${det.stderr || ""}`;
  const starts = [...log.matchAll(/silence_start:\s*([-\d.]+)/g)].map((m) => parseFloat(m[1]));
  const ends = [...log.matchAll(/silence_end:\s*([\d.]+)/g)].map((m) => parseFloat(m[1]));
  const gaps = [];
  for (let i = 0; i < starts.length; i++) {
    const a = starts[i];
    const b = i < ends.length ? ends[i] : durationS; // trailing silence runs to end
    // Keep only interior gaps; the fade-in/out already handle the head/tail.
    if (b - a >= DUCK_MIN_GAP && a > FADE_IN + 0.1 && b < durationS - FADE_OUT - 0.1) {
      // Pad outward to catch the music swells that sit just past the silence edges,
      // clamped to stay inside the fade-in/out regions.
      const pa = Math.max(FADE_IN + 0.05, a - DUCK_PAD);
      const pb = Math.min(durationS - FADE_OUT - 0.05, b + DUCK_PAD);
      gaps.push([pa, pb]);
    }
  }
  return gaps;
}

// Build an ffmpeg volume expression (eval=frame, variable t) that holds the music
// at `base` and dips to base*DUCK_GAIN across each gap with trapezoidal fades.
function duckVolumeExpr(base, gaps) {
  if (!gaps.length) return `${base}`;
  const factors = gaps.map(([a, b]) => {
    const f = Math.min(DUCK_FADE, (b - a) / 2 - 0.01);
    const g = DUCK_GAIN.toFixed(3);
    const d = (1 - DUCK_GAIN).toFixed(3);
    return (
      `(if(between(t,${a.toFixed(3)},${b.toFixed(3)}),` +
      `if(lt(t,${(a + f).toFixed(3)}),1-${d}*(t-${a.toFixed(3)})/${f.toFixed(3)},` +
      `if(gt(t,${(b - f).toFixed(3)}),1-${d}*(${b.toFixed(3)}-t)/${f.toFixed(3)},${g})),1))`
    );
  });
  return `${base}*${factors.join("*")}`;
}

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, "..");
const MUSIC_DIR = path.join(ROOT, "background-music");

const argv = process.argv.slice(2);
const volIdx = argv.indexOf("--volume");
const volume = volIdx !== -1 ? parseFloat(argv[volIdx + 1]) : DEFAULT_VOLUME;
const positional = argv.filter((a, i) => !a.startsWith("--") && argv[i - 1] !== "--volume");
const slug = positional[0];
const trackQuery = positional[1];

if (!slug) {
  console.error("Usage: node scripts/add_music.mjs <slug> [trackQuery] [--volume 0.25]");
  process.exit(1);
}

const videoPath = path.join(ROOT, "out", `${slug}.mp4`);
if (!fs.existsSync(videoPath)) {
  console.error(`Missing ${videoPath}. Render the reel first.`);
  process.exit(1);
}

// Provenance guard: refuse to mux music onto a video that wasn't rendered from
// the current preflight-passed files (captions/timeline/wav). render.mjs stamps
// out/<slug>.render.json with the hashes it built from; if those don't match the
// current preflight.json, the video is stale and must be re-rendered first.
{
  const sha = (p) =>
    fs.existsSync(p) ? crypto.createHash("sha256").update(fs.readFileSync(p)).digest("hex") : null;
  const stampPath = path.join(ROOT, "out", `${slug}.render.json`);
  const markPath = path.join(ROOT, "public", "reels", slug, "preflight.json");
  if (!fs.existsSync(stampPath)) {
    console.error(
      `✗ ${slug}.mp4 has no render stamp (out/${slug}.render.json) — it predates the render gate.\n` +
      `  Re-render it:  node scripts/render.mjs ${slug}`
    );
    process.exit(1);
  }
  if (fs.existsSync(markPath)) {
    const stamp = JSON.parse(fs.readFileSync(stampPath, "utf8"));
    const mark = JSON.parse(fs.readFileSync(markPath, "utf8"));
    const fields = ["captions_sha", "timeline_sha", "wav_sha256"];
    const stale = fields.some((f) => mark[f] && stamp[f] !== mark[f]);
    if (stale) {
      console.error(
        `✗ ${slug}.mp4 is stale: it was rendered from older files than the current preflight pass.\n` +
        `  Re-render before adding music:  node scripts/render.mjs ${slug}`
      );
      process.exit(1);
    }
  }
}

if (!fs.existsSync(MUSIC_DIR)) {
  console.error(`Missing ${MUSIC_DIR}. Add background tracks there first.`);
  process.exit(1);
}
const tracks = fs
  .readdirSync(MUSIC_DIR)
  .filter((f) => AUDIO_EXT.includes(path.extname(f).toLowerCase()))
  .sort();
if (tracks.length === 0) {
  console.error(`No audio tracks in ${MUSIC_DIR}.`);
  process.exit(1);
}

let track;
if (trackQuery) {
  track = tracks.find((t) => t.toLowerCase().includes(trackQuery.toLowerCase()));
  if (!track) {
    console.error(`No track matching "${trackQuery}". Available:\n  ${tracks.join("\n  ")}`);
    process.exit(1);
  }
} else {
  track = tracks[0]; // deterministic default; pass a trackQuery to choose another
}
const trackPath = path.join(MUSIC_DIR, track);

// Reel duration: prefer the aligned timeline, else probe the mp4.
let durationS;
const timelinePath = path.join(ROOT, "public", "reels", slug, "timeline.json");
if (fs.existsSync(timelinePath)) {
  const t = JSON.parse(fs.readFileSync(timelinePath, "utf8"));
  if (t.durationMs) durationS = t.durationMs / 1000;
}
if (!durationS) {
  const out = execFileSync(ffmpegPath, ["-i", videoPath], { encoding: "utf8", stdio: ["ignore", "ignore", "pipe"] });
  const m = out.match(/Duration:\s*(\d+):(\d+):(\d+\.\d+)/);
  if (m) durationS = (+m[1]) * 3600 + (+m[2]) * 60 + parseFloat(m[3]);
}
if (!durationS) {
  console.error("Could not determine reel duration.");
  process.exit(1);
}

const fadeOutStart = Math.max(0, durationS - FADE_OUT).toFixed(2);
const outPath = path.join(ROOT, "out", `${slug}-music.mp4`);

const voicePath = path.join(ROOT, "public", "reels", slug, "voiceover.wav");
const gaps = detectGaps(voicePath, durationS);
const volExpr = duckVolumeExpr(volume, gaps);
const duckNote = gaps.length
  ? ` (ducking music in ${gaps.length} scene gap${gaps.length > 1 ? "s" : ""} to ${Math.round(DUCK_GAIN * 100)}%)`
  : "";

console.log(`→ Mixing "${track}" under ${slug}.mp4 at ${Math.round(volume * 100)}% (${durationS.toFixed(1)}s)${duckNote}...`);
execFileSync(
  ffmpegPath,
  [
    "-i", videoPath,
    "-i", trackPath,
    "-filter_complex",
    `[1:a]afade=t=in:st=0:d=${FADE_IN},afade=t=out:st=${fadeOutStart}:d=${FADE_OUT},` +
      `volume=eval=frame:volume='${volExpr}'[bg];` +
      `[0:a][bg]amix=inputs=2:duration=first:normalize=0[a]`,
    "-map", "0:v", "-map", "[a]",
    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
    "-shortest", outPath, "-y",
  ],
  { stdio: "ignore" }
);
console.log(`✓ Wrote out/${slug}-music.mp4`);
