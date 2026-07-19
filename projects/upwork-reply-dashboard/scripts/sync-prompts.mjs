// Sync the prompt brain into ./prompts so the /api/draft route can read it at
// runtime (and so it deploys to Vercel, which can't reach ../../.claude/skills/).
// Pulls from TWO canonical skills: upwork-reply-drafter (own) + sales-playbook (reused
// frameworks). Run after editing either:  npm run sync-prompts
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SKILLS_ROOT = path.resolve(__dirname, "../../../.claude/skills");
const DEST_ROOT = path.resolve(__dirname, "../prompts");

// [skill folder, relative file] -> copied to prompts/<skill folder>/<relative file>.
// Keep in sync with the files route.ts loads.
const FILES = [
  ["upwork-reply-drafter", "SKILL.md"],
  ["upwork-reply-drafter", "references/situations.md"],
  ["upwork-reply-drafter", "references/upwork-mechanics.md"],
  ["upwork-reply-drafter", "references/research-synthesis.md"],
  ["sales-playbook", "frameworks/voss-calibrated-questions.md"],
  ["sales-playbook", "frameworks/objection-psychology.md"],
  ["sales-playbook", "frameworks/objection-riffs.md"],
  ["sales-playbook", "frameworks/hormozi-value-equation.md"],
  ["sales-playbook", "references/what-not-to-do.md"],
];

let copied = 0;
const missing = [];
for (const [skill, rel] of FILES) {
  const src = path.join(SKILLS_ROOT, skill, rel);
  const dest = path.join(DEST_ROOT, skill, rel);
  if (!fs.existsSync(src)) {
    missing.push(`${skill}/${rel}`);
    continue;
  }
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.copyFileSync(src, dest);
  copied++;
}

console.log(`Synced ${copied}/${FILES.length} prompt files into prompts/`);
if (missing.length) {
  console.error(`Missing from canonical skills (NOT copied):\n  - ${missing.join("\n  - ")}`);
  process.exit(1);
}
