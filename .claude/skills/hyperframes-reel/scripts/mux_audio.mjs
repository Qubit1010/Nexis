#!/usr/bin/env node
// mux_audio.mjs — the hyperframes-reel audio bridge.
//
// HyperFrames renders the reel SILENT; reel-engine synthesizes the cloned voice.
// This muxes them: lays the voiceover onto the silent mp4 at full level and mixes a
// background track UNDER it at 25% (0.8s fade-in + 2s fade-out), ducked to 15% during
// voice-silent gaps so a music phrase never swells when the narration pauses.
//
// This is the SAME ffmpeg approach as reel-engine's add_music.mjs (silencedetect →
// per-gap volume envelope), but ungated and path-explicit — add_music.mjs refuses to
// run without reel-engine's own render stamp, which a HyperFrames render doesn't have.
//
//   node mux_audio.mjs --video silent.mp4 --voice voiceover.wav --music track.mp3 \
//                      --out final.mp4 [--volume 0.25] [--ffmpeg <path>]
//   node mux_audio.mjs --selfcheck   # synthetic end-to-end check, no real assets needed
//
// ffmpeg: pass --ffmpeg, else FFMPEG env, else reel-engine's bundled ffmpeg-static, else "ffmpeg".

import { spawnSync, execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";
import os from "node:os";

const FADE_IN = 0.8; // s — music fade-in
const FADE_OUT = 2.0; // s — music fade-out
const DEFAULT_VOLUME = 0.25; // music base level (house reel level)
const DUCK_GAIN = 0.15; // music multiplier during a voice gap
const DUCK_FADE = 0.15; // s — ramp the dip in/out (click-free)
const DUCK_MIN_GAP = 0.3; // only duck silences at least this long (skips word pauses)
const DUCK_NOISE_DB = -50; // below this is treated as silence
const DUCK_PAD = 0.28; // widen each gap on both sides to catch edge swells

const arg = (name, def) => {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 && i + 1 < process.argv.length ? process.argv[i + 1] : def;
};
const has = (name) => process.argv.includes(`--${name}`);

function resolveFfmpeg() {
  const explicit = arg("ffmpeg", process.env.FFMPEG);
  if (explicit && existsSync(explicit)) return explicit;
  // reel-engine ships ffmpeg-static; reuse it rather than requiring a system install.
  const bundled = path.resolve(
    process.cwd(),
    "projects/reel-engine/node_modules/ffmpeg-static/ffmpeg.exe",
  );
  if (existsSync(bundled)) return bundled;
  const bundledNix = bundled.replace(/\.exe$/, "");
  if (existsSync(bundledNix)) return bundledNix;
  return "ffmpeg"; // fall back to PATH
}

function probeDuration(ffmpeg, file) {
  // ffmpeg prints "Duration: HH:MM:SS.xx" to stderr; no ffprobe dependency.
  const out = spawnSync(ffmpeg, ["-i", file], { encoding: "utf8" }).stderr || "";
  const m = out.match(/Duration:\s*(\d+):(\d+):([\d.]+)/);
  if (!m) throw new Error(`could not read duration of ${file}`);
  return +m[1] * 3600 + +m[2] * 60 + +m[3];
}

// Detect interior voice-silent gaps in the voiceover (ported from add_music.mjs).
function detectGaps(ffmpeg, voicePath, durationS) {
  if (!existsSync(voicePath)) return [];
  const log =
    spawnSync(
      ffmpeg,
      ["-hide_banner", "-i", voicePath, "-af", `silencedetect=noise=${DUCK_NOISE_DB}dB:d=${DUCK_MIN_GAP}`, "-f", "null", "-"],
      { encoding: "utf8" },
    ).stderr || "";
  const starts = [...log.matchAll(/silence_start:\s*([-\d.]+)/g)].map((m) => parseFloat(m[1]));
  const ends = [...log.matchAll(/silence_end:\s*([\d.]+)/g)].map((m) => parseFloat(m[1]));
  const gaps = [];
  for (let i = 0; i < starts.length; i++) {
    const a = starts[i];
    const b = i < ends.length ? ends[i] : durationS;
    if (b - a >= DUCK_MIN_GAP && a > FADE_IN + 0.1 && b < durationS - FADE_OUT - 0.1) {
      const pa = Math.max(FADE_IN + 0.05, a - DUCK_PAD);
      const pb = Math.min(durationS - FADE_OUT - 0.05, b + DUCK_PAD);
      gaps.push([pa, pb]);
    }
  }
  return gaps;
}

// Music volume expression: base level, dipping to base*DUCK_GAIN across each gap.
function duckVolumeExpr(base, gaps) {
  if (!gaps.length) return `${base}`;
  const d = (1 - DUCK_GAIN).toFixed(3);
  const g = DUCK_GAIN.toFixed(3);
  const factors = gaps.map(([a, b]) => {
    const f = Math.min(DUCK_FADE, (b - a) / 2 - 0.01);
    return (
      `(if(between(t,${a.toFixed(3)},${b.toFixed(3)}),` +
      `if(lt(t,${(a + f).toFixed(3)}),1-${d}*(t-${a.toFixed(3)})/${f.toFixed(3)},` +
      `if(gt(t,${(b - f).toFixed(3)}),1-${d}*(${b.toFixed(3)}-t)/${f.toFixed(3)},${g})),1))`
    );
  });
  return `${base}*${factors.join("*")}`;
}

function mux({ ffmpeg, video, voice, music, out, volume }) {
  const dur = probeDuration(ffmpeg, video);
  const fadeOutStart = Math.max(0, dur - FADE_OUT);
  const gaps = detectGaps(ffmpeg, voice, dur);
  const volExpr = duckVolumeExpr(volume, gaps);
  // [1]=voice full · [2]=music faded+ducked · amix onto the silent [0:v].
  execFileSync(
    ffmpeg,
    [
      "-i", video,
      "-i", voice,
      "-i", music,
      "-filter_complex",
      `[1:a]volume=1.0[vo];` +
        `[2:a]afade=t=in:st=0:d=${FADE_IN},afade=t=out:st=${fadeOutStart}:d=${FADE_OUT},` +
        `volume=eval=frame:volume='${volExpr}'[bg];` +
        `[vo][bg]amix=inputs=2:duration=first:normalize=0[a]`,
      "-map", "0:v", "-map", "[a]",
      "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
      "-shortest", out, "-y",
    ],
    { stdio: "ignore" },
  );
  return { dur, gaps: gaps.length };
}

function selfcheck() {
  const ffmpeg = resolveFfmpeg();
  const tmp = os.tmpdir();
  const video = path.join(tmp, "hf_reel_sc_video.mp4");
  const voice = path.join(tmp, "hf_reel_sc_voice.wav");
  const music = path.join(tmp, "hf_reel_sc_music.mp3");
  const out = path.join(tmp, "hf_reel_sc_out.mp4");
  // 3s SILENT video (color source, no audio) — mimics a HyperFrames render.
  execFileSync(ffmpeg, ["-f", "lavfi", "-i", "color=c=black:s=320x240:d=3", "-r", "30", video, "-y"], { stdio: "ignore" });
  // 3s voice = tone with a real gap in the middle (so ducking has something to find).
  execFileSync(ffmpeg, ["-f", "lavfi", "-i", "sine=f=220:d=1", "-f", "lavfi", "-i", "anullsrc=d=1", "-f", "lavfi", "-i", "sine=f=220:d=1", "-filter_complex", "[0][1][2]concat=n=3:v=0:a=1[a]", "-map", "[a]", voice, "-y"], { stdio: "ignore" });
  execFileSync(ffmpeg, ["-f", "lavfi", "-i", "sine=f=440:d=3", music, "-y"], { stdio: "ignore" });
  const { gaps } = mux({ ffmpeg, video, voice, music, out, volume: DEFAULT_VOLUME });
  // Assert: output exists and carries an audio stream.
  if (!existsSync(out)) throw new Error("selfcheck: no output written");
  const info = spawnSync(ffmpeg, ["-i", out], { encoding: "utf8" }).stderr || "";
  if (!/Audio:/.test(info)) throw new Error("selfcheck: output has no audio stream");
  console.log(`✓ mux_audio selfcheck passed (detected ${gaps} interior gap${gaps === 1 ? "" : "s"}, output has audio)`);
}

if (has("selfcheck")) {
  selfcheck();
} else {
  const video = arg("video");
  const voice = arg("voice");
  const music = arg("music");
  const out = arg("out");
  const volume = parseFloat(arg("volume", String(DEFAULT_VOLUME)));
  if (!video || !voice || !music || !out) {
    console.error("Usage: node mux_audio.mjs --video <mp4> --voice <wav> --music <mp3> --out <mp4> [--volume 0.25] [--ffmpeg <path>]");
    process.exit(1);
  }
  const ffmpeg = resolveFfmpeg();
  const { dur, gaps } = mux({ ffmpeg, video, voice, music, out, volume });
  console.log(`✓ Wrote ${out} — voice full + music at ${Math.round(volume * 100)}%${gaps ? `, ducked in ${gaps} gap${gaps === 1 ? "" : "s"}` : ""} (${dur.toFixed(1)}s)`);
}
