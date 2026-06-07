/**
 * prepare.mjs <slug> [--model base.en]
 *
 * Turns a recorded ElevenLabs voiceover into perfectly-synced reel data:
 *   1. Convert public/reels/<slug>/voiceover.mp3 -> 16kHz mono wav (ffmpeg-static)
 *   2. Transcribe with Whisper (word-level timestamps)
 *   3. Write captions.json (drives the TikTok-style captions)
 *   4. Align each scene to the spoken audio -> timeline.json (drives scene cuts)
 *
 * Run AFTER you have dropped voiceover.mp3 into the reel folder, then render.
 */
import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import { execFileSync } from "child_process";
import ffmpegPath from "ffmpeg-static";
import {
  downloadWhisperModel,
  installWhisperCpp,
  transcribe,
  toCaptions,
} from "@remotion/install-whisper-cpp";

const FPS = 30; // must match src/brand.ts VIDEO.fps
const WHISPER_VERSION = "1.5.5";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, "..");

const slug = process.argv[2];
if (!slug) {
  console.error("Usage: node scripts/prepare.mjs <slug> [--model base.en]");
  process.exit(1);
}
const modelArgIdx = process.argv.indexOf("--model");
const model = modelArgIdx !== -1 ? process.argv[modelArgIdx + 1] : "base.en";

const reelDir = path.join(ROOT, "public", "reels", slug);
const mp3Path = path.join(reelDir, "voiceover.mp3");
const wavPath = path.join(reelDir, "voiceover.16k.wav");
const contentPath = path.join(reelDir, "content.json");
const captionsPath = path.join(reelDir, "captions.json");
const timelinePath = path.join(reelDir, "timeline.json");

if (!fs.existsSync(mp3Path)) {
  console.error(`Missing ${mp3Path}. Drop your ElevenLabs voiceover.mp3 there first.`);
  process.exit(1);
}
if (!fs.existsSync(contentPath)) {
  console.error(`Missing ${contentPath}.`);
  process.exit(1);
}

const norm = (s) =>
  s
    .toLowerCase()
    .replace(/[^a-z0-9']/g, " ")
    .replace(/\s+/g, " ")
    .trim();

const main = async () => {
  // 1. mp3 -> 16kHz mono wav
  console.log("→ Converting audio to 16kHz wav...");
  execFileSync(ffmpegPath, ["-i", mp3Path, "-ar", "16000", "-ac", "1", wavPath, "-y"], {
    stdio: "ignore",
  });

  // 2. Whisper
  const whisperDir = path.join(ROOT, "whisper.cpp");
  console.log("→ Ensuring Whisper.cpp + model (first run downloads, can take a few minutes)...");
  await installWhisperCpp({ to: whisperDir, version: WHISPER_VERSION });
  await downloadWhisperModel({ model, folder: whisperDir });

  console.log("→ Transcribing...");
  const whisperCppOutput = await transcribe({
    model,
    whisperPath: whisperDir,
    whisperCppVersion: WHISPER_VERSION,
    inputPath: wavPath,
    tokenLevelTimestamps: true,
  });

  // 3. captions.json
  const { captions } = toCaptions({ whisperCppOutput });
  fs.writeFileSync(captionsPath, JSON.stringify(captions, null, 2));
  console.log(`✓ Wrote ${path.relative(ROOT, captionsPath)} (${captions.length} words)`);

  // 4. Align scenes to spoken audio
  const content = JSON.parse(fs.readFileSync(contentPath, "utf8"));
  const words = captions
    .map((c) => ({ w: norm(c.text), startMs: c.startMs, endMs: c.endMs }))
    .filter((c) => c.w.length > 0);

  const lastEndMs = words.length ? words[words.length - 1].endMs : 0;
  const durationMs = Math.ceil(lastEndMs + 600); // small tail so audio never clips
  const durationInFrames = Math.ceil((durationMs / 1000) * FPS);

  // Anchor each scene (after the first) on the first 2 words of its voiceText.
  let cursor = 0;
  const startMsForScene = content.scenes.map((scene, i) => {
    if (i === 0) return 0;
    const tokens = norm(scene.voiceText).split(" ").filter(Boolean);
    const a = tokens[0];
    const b = tokens[1];
    for (let j = cursor; j < words.length - 1; j++) {
      if (words[j].w === a && (!b || words[j + 1].w === b)) {
        cursor = j;
        return words[j].startMs;
      }
    }
    // Fallback: proportional by cumulative word count if anchor not found.
    const wc = content.scenes.slice(0, i).reduce((s, sc) => s + norm(sc.voiceText).split(" ").filter(Boolean).length, 0);
    const idx = Math.min(words.length - 1, wc);
    return words[idx] ? words[idx].startMs : 0;
  });

  const scenes = content.scenes.map((scene, i) => {
    const startFrame = Math.round((startMsForScene[i] / 1000) * FPS);
    const endFrame =
      i < content.scenes.length - 1
        ? Math.round((startMsForScene[i + 1] / 1000) * FPS)
        : durationInFrames;
    return { sceneId: scene.id, startFrame, endFrame };
  });

  const timeline = { fps: FPS, durationInFrames, durationMs, aligned: true, scenes };
  fs.writeFileSync(timelinePath, JSON.stringify(timeline, null, 2));
  console.log(`✓ Wrote ${path.relative(ROOT, timelinePath)} (${(durationMs / 1000).toFixed(1)}s, ${scenes.length} scenes)`);

  // Clean up the intermediate wav.
  fs.rmSync(wavPath, { force: true });
  console.log("\nDone. Now render:");
  console.log(`  npx remotion render Reel out/${slug}.mp4 --props='{"slug":"${slug}"}'`);
};

main().catch((err) => {
  console.error("prepare.mjs failed:", err);
  process.exit(1);
});
