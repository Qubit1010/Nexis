/**
 * render.mjs <slug>  — render gate.
 *
 * Refuses to render unless scripts/preflight.py has PASSED for this slug and the
 * captions/timeline/voiceover on disk are exactly what it passed (sha256 match).
 * This is what stops audio/caption defects from reaching the finished video.
 *
 *   node scripts/render.mjs <slug>
 */
import path from "path";
import fs from "fs";
import crypto from "crypto";
import { fileURLToPath } from "url";
import { spawnSync } from "child_process";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, "..");

const slug = process.argv[2];
if (!slug) {
  console.error("Usage: node scripts/render.mjs <slug>");
  process.exit(1);
}

const dir = path.join(ROOT, "public", "reels", slug);
const sha = (p) =>
  fs.existsSync(p) ? crypto.createHash("sha256").update(fs.readFileSync(p)).digest("hex") : null;

const markPath = path.join(dir, "preflight.json");
if (!fs.existsSync(markPath)) {
  console.error(
    `✗ render gate: no preflight.json for "${slug}".\n` +
    `  Run the QA gate first:  .venv/Scripts/python.exe scripts/preflight.py ${slug} --fix`
  );
  process.exit(1);
}
const mark = JSON.parse(fs.readFileSync(markPath, "utf8"));
if (!mark.passed) {
  console.error(`✗ render gate: preflight did NOT pass for "${slug}". Resolve the FAILs and re-run preflight --fix.`);
  process.exit(1);
}
const checks = [
  ["captions_sha", "captions.json"],
  ["timeline_sha", "timeline.json"],
  ["wav_sha256", "voiceover.wav"],
];
const provenance = {};
for (const [field, file] of checks) {
  const cur = sha(path.join(dir, file));
  if (mark[field] && mark[field] !== cur) {
    console.error(
      `✗ render gate: ${file} changed since preflight passed.\n` +
      `  Re-run:  .venv/Scripts/python.exe scripts/preflight.py ${slug} --fix`
    );
    process.exit(1);
  }
  provenance[field] = cur;
}

console.log(`✓ render gate: ${slug} passed preflight — rendering.`);
const out = `out/${slug}.mp4`;
// Pass props via a temp JSON file — inline --props JSON gets mangled by Windows quoting.
const propsPath = path.join(dir, ".render-props.json");
fs.writeFileSync(propsPath, JSON.stringify({ slug }));
const r = spawnSync(
  "npx",
  ["remotion", "render", "Reel", out, `--props=${propsPath}`],
  { cwd: ROOT, stdio: "inherit", shell: process.platform === "win32" }
);
fs.rmSync(propsPath, { force: true });
if (r.status === 0) {
  // Stamp the video with the exact inputs it was built from, so add_music.mjs
  // can refuse to mux onto a video that predates a newer preflight pass.
  fs.writeFileSync(path.join(ROOT, "out", `${slug}.render.json`), JSON.stringify(provenance, null, 2));
}
process.exit(r.status ?? 1);
