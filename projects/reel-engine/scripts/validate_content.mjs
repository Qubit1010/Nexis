/**
 * validate_content.mjs <slug>
 *
 * Validates public/reels/<slug>/content.json BEFORE the script is handed to
 * ElevenLabs. Catches the mistakes that silently break a render or the brand
 * voice: scene-text drift, em dashes, agency/academia mentions, bad word count,
 * wrong scene set, non-numeric stats.
 *
 * Exit 0 = OK (warnings allowed). Exit 1 = at least one hard error; fix before
 * recording the voiceover.
 */
import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, "..");

const slug = process.argv[2];
if (!slug) {
  console.error("Usage: node scripts/validate_content.mjs <slug>");
  process.exit(1);
}

const contentPath = path.join(ROOT, "public", "reels", slug, "content.json");
if (!fs.existsSync(contentPath)) {
  console.error(`Missing ${contentPath}`);
  process.exit(1);
}

const errors = [];
const warnings = [];
const err = (m) => errors.push(m);
const warn = (m) => warnings.push(m);

let content;
try {
  content = JSON.parse(fs.readFileSync(contentPath, "utf8"));
} catch (e) {
  console.error(`content.json is not valid JSON: ${e.message}`);
  process.exit(1);
}

const collapse = (s) => (s || "").replace(/\s+/g, " ").trim();

// 1. slug matches folder
if (content.slug !== slug) {
  err(`slug field ("${content.slug}") does not match folder ("${slug}").`);
}

// 2. voiceScript present
const script = content.voiceScript || "";
if (!script.trim()) err("voiceScript is empty.");

// 3. scene set + order
const EXPECTED = ["intro", "problem", "solution", "stats", "punch", "outro"];
const scenes = Array.isArray(content.scenes) ? content.scenes : [];
const types = scenes.map((s) => s.type);
if (types.join(",") !== EXPECTED.join(",")) {
  err(`scenes must be exactly [${EXPECTED.join(", ")}] in order. Got [${types.join(", ")}].`);
}

// 4. concatenated voiceText must equal voiceScript (whitespace-tolerant)
const joined = collapse(scenes.map((s) => s.voiceText || "").join(" "));
const target = collapse(script);
if (joined !== target) {
  err("scenes[].voiceText concatenated does not equal voiceScript. Sync will be wrong.");
  // Show the first place they diverge to make the fix easy.
  const a = joined.split(" ");
  const b = target.split(" ");
  const n = Math.min(a.length, b.length);
  let i = 0;
  while (i < n && a[i] === b[i]) i++;
  const ctx = (arr) => arr.slice(Math.max(0, i - 3), i + 3).join(" ");
  err(`  first divergence near word ${i + 1}:`);
  err(`    voiceText : ...${ctx(a)}...`);
  err(`    voiceScript: ...${ctx(b)}...`);
}

// 5. word count (warning only — length misses the target, it doesn't break a render).
// Observed ElevenLabs pace on CodeGraph was ~2.1 words/sec (125 words -> 59s), so we
// size against ~2.2 wps, not the optimistic 2.6-2.8. Push hard toward ~100.
const words = target.split(" ").filter(Boolean);
const wc = words.length;
if (wc < 80) warn(`voiceScript is ${wc} words — short. May land under 40s. (target ~100)`);
else if (wc > 115) warn(`voiceScript is ${wc} words — likely to exceed 50s (ElevenLabs reads ~2.1 wps). Trim toward ~100, or plan to speed the audio ~1.15x.`);
else if (wc > 105) warn(`voiceScript is ${wc} words — near the 50s ceiling. Consider trimming a sentence.`);

// 6. no em dash in spoken text
if (/[—―]/.test(script)) err("voiceScript contains an em dash. Use commas or periods.");
if (/–/.test(script)) warn("voiceScript contains an en dash (–). Prefer a comma or period.");

// 6b. hard-to-pronounce words covered by scripts/pronunciation.json (FYI: they'll be
// respelled for the TTS at synthesis time; display + captions keep the real spelling).
try {
  const pronPath = path.join(__dirname, "pronunciation.json");
  if (fs.existsSync(pronPath)) {
    const pron = JSON.parse(fs.readFileSync(pronPath, "utf8"));
    for (const key of Object.keys(pron)) {
      if (new RegExp(`\\b${key.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`, "i").test(script)) {
        warn(`voiceScript contains "${key}" — will be spoken via the pronunciation map as "${pron[key]}" (captions stay "${key}").`);
      }
    }
  }
} catch { /* non-fatal */ }

// 7. no agency / academia mentions in spoken text
const lower = script.toLowerCase();
const hardBanned = ["nexuspoint", "nexus point", "iqra", "bsai"];
for (const t of hardBanned) {
  if (lower.includes(t)) err(`voiceScript mentions "${t}" — never name the agency or his university in spoken copy.`);
}
const softBanned = ["my university", "my degree", "my semester", "b.sc", "bachelor"];
for (const t of softBanned) {
  if (lower.includes(t)) warn(`voiceScript contains "${t}" — check this isn't a self-reference to his studies.`);
}

// 8. stats values numeric
const statsScene = scenes.find((s) => s.type === "stats");
if (statsScene) {
  const stats = Array.isArray(statsScene.stats) ? statsScene.stats : [];
  if (stats.length === 0) warn("stats scene has no stats[] — it will render empty.");
  stats.forEach((st, i) => {
    if (typeof st.value !== "number") err(`stats[${i}].value must be a number (got ${JSON.stringify(st.value)}).`);
    if (!st.label) warn(`stats[${i}] has no label.`);
  });
} else if (types.includes("stats")) {
  // covered by order check
}

// 9. solution asset sanity
const solution = scenes.find((s) => s.type === "solution");
if (solution && solution.asset && solution.asset !== "infographic.png") {
  warn(`solution.asset is "${solution.asset}" — the engine expects "infographic.png".`);
}

// ---- report ----
const rel = path.relative(ROOT, contentPath);
console.log(`\nValidating ${rel}  (${wc} words ≈ ${(wc / 2.2).toFixed(0)}s at ElevenLabs pace)\n`);

if (warnings.length) {
  console.log("Warnings:");
  warnings.forEach((w) => console.log(`  ! ${w}`));
  console.log("");
}
if (errors.length) {
  console.log("Errors:");
  errors.forEach((e) => console.log(`  ✗ ${e}`));
  console.log(`\n${errors.length} error(s). Fix before recording the voiceover.\n`);
  process.exit(1);
}

console.log("✓ content.json is valid. Safe to hand the script to ElevenLabs.\n");
