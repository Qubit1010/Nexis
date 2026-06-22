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
import { fileURLToPath } from "url";
import { execFileSync } from "child_process";
import ffmpegPath from "ffmpeg-static";

const DEFAULT_VOLUME = 0.25;
const FADE_IN = 0.8;   // seconds
const FADE_OUT = 2.0;  // seconds
const AUDIO_EXT = [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac"];

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

console.log(`→ Mixing "${track}" under ${slug}.mp4 at ${Math.round(volume * 100)}% (${durationS.toFixed(1)}s)...`);
execFileSync(
  ffmpegPath,
  [
    "-i", videoPath,
    "-i", trackPath,
    "-filter_complex",
    `[1:a]volume=${volume},afade=t=in:st=0:d=${FADE_IN},afade=t=out:st=${fadeOutStart}:d=${FADE_OUT}[bg];` +
      `[0:a][bg]amix=inputs=2:duration=first:normalize=0[a]`,
    "-map", "0:v", "-map", "[a]",
    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
    "-shortest", outPath, "-y",
  ],
  { stdio: "ignore" }
);
console.log(`✓ Wrote out/${slug}-music.mp4`);
