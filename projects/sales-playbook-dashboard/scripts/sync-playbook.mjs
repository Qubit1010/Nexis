// Sync the canonical sales-playbook files into ./prompts/sales-playbook so the
// API route can read them at runtime (and so they deploy to Vercel, which can't
// reach ../../.claude/skills/ at runtime).
//
// Run after editing the playbook:  npm run sync-playbook
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SKILL_ROOT = path.resolve(__dirname, "../../../.claude/skills/sales-playbook");
const DEST_ROOT = path.resolve(__dirname, "../prompts/sales-playbook");

// The exact files the dashboard's system prompt needs. Keep in sync with route.ts.
const FILES = [
  "SKILL.md",
  "frameworks/opener-archetypes.md",
  "frameworks/objection-riffs.md",
  "frameworks/objection-psychology.md",
  "frameworks/hormozi-selling-principles.md",
  "frameworks/voss-calibrated-questions.md",
  "references/what-not-to-do.md",
  "references/worked-example-linkedin.md",
  "references/worked-example-instagram.md",
  "offer/proof-bank.md",
  "offer/ai-automation-positioning.md",
  "offer/agency-to-agency-positioning.md",
  "scripts/linkedin-cold-dm-sequence.md",
  "scripts/instagram-cold-dm-sequence.md",
  "scripts/live-conversation-playbook.md",
];

if (!fs.existsSync(SKILL_ROOT)) {
  console.error(`Canonical sales-playbook not found at:\n  ${SKILL_ROOT}`);
  process.exit(1);
}

let copied = 0;
const missing = [];
for (const rel of FILES) {
  const src = path.join(SKILL_ROOT, rel);
  const dest = path.join(DEST_ROOT, rel);
  if (!fs.existsSync(src)) {
    missing.push(rel);
    continue;
  }
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.copyFileSync(src, dest);
  copied++;
}

console.log(`Synced ${copied}/${FILES.length} playbook files into prompts/sales-playbook`);
if (missing.length) {
  console.error(`Missing from canonical skill (NOT copied):\n  - ${missing.join("\n  - ")}`);
  process.exit(1);
}
