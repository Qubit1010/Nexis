/**
 * Builds a demo database so the measurement surfaces have something to show without an
 * hour of clicking.
 *
 * The ratings it writes are SYNTHETIC. They come from a stand-in "taste" function, not
 * from a person. It writes to its own file (data/demo.db) so it can never contaminate the
 * real one, and every run says so on stdout.
 *
 *   node scripts/demo.ts
 *   DB_PATH=./data/demo.db npm start
 */
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { rmSync } from 'node:fs';
import { openDb } from '../src/db.ts';
import * as svc from '../src/service.ts';
import { mockProvider } from '../src/providers/mock.ts';
import { seedIfEmpty } from '../src/seed.ts';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const DB_PATH = process.env.DEMO_DB_PATH ?? join(ROOT, 'data', 'demo.db');

for (const suffix of ['', '-wal', '-shm']) {
  try { rmSync(DB_PATH + suffix); } catch { /* not there, fine */ }
}

const db = openDb(DB_PATH);
const provider = mockProvider();
seedIfEmpty(db);

const V1 = svc.getActivePrompt(db)!;

const V2 = svc.createPrompt(db, {
  label: 'v2 asks a question',
  system_prompt: `${V1.system_prompt}\n\nAlways end with one specific discovery question.`,
});

const V3 = svc.createPrompt(db, {
  label: 'v3 shorter, proposes a call',
  system_prompt: `${V1.system_prompt}\n\nBe brief. Ask one discovery question, then propose a call.`,
});

/**
 * Stand-in for a human judgement, so the demo has a signal instead of noise.
 * A draft is "good" if it asks something and is not sprawling.
 */
function syntheticVerdict(text: string): 'good' | 'bad' {
  const asks = text.includes('?');
  const tight = text.split(/\s+/).length < 90;
  return asks && tight ? 'good' : 'bad';
}

/** Stand-in for editing: leave a good draft alone, rewrite a chunk of a bad one. */
function syntheticFinalText(text: string, verdict: 'good' | 'bad'): string {
  if (verdict === 'good') return text;
  const words = text.split(' ');
  const cut = Math.floor(words.length / 2);
  return [...words.slice(0, cut), 'rewrote', 'the', 'rest', 'of', 'this', 'myself'].join(' ');
}

let rated = 0;
for (const version of [V1, V2, V3]) {
  const { drafts } = await svc.runBench(db, provider, version.id);
  for (const d of drafts) {
    const verdict = syntheticVerdict(d.text);
    svc.saveReview(db, {
      draftId: d.id,
      verdict,
      finalText: syntheticFinalText(d.text, verdict),
      note: 'synthetic demo rating',
    });
    rated++;
  }
}

svc.activatePrompt(db, V3.id);

const board = svc.scoreboard(db, 'bench');
const pct = (n: number | null) => (n === null ? '  --' : `${String(Math.round(n * 100)).padStart(3)}%`);

console.log('');
console.log(`  Demo database written to ${DB_PATH}`);
console.log(`  ${rated} bench drafts rated. THE RATINGS ARE SYNTHETIC, not a real judgement.`);
console.log('');
console.log('  version                        n   approval   95% interval    median edit');
console.log('  ' + '-'.repeat(74));
for (const v of board) {
  const ci = `${pct(v.interval.low)} to ${pct(v.interval.high)}`;
  console.log(
    `  ${v.label.padEnd(28)} ${String(v.reviewed).padStart(2)}     ${pct(v.approval)}   ${ci.padEnd(15)} ${
      v.median_edit_ratio === null ? '--' : v.median_edit_ratio.toFixed(2)
    }`,
  );
}

console.log('');
for (const [a, b] of [[V1, V2], [V2, V3], [V1, V3]] as const) {
  const c = svc.comparison(db, a.id, b.id, 'bench');
  console.log(`  ${a.label}  ->  ${b.label}`);
  console.log(`    ${c.verdict}: ${c.reason}`);
}
console.log('');
console.log(`  Browse it with:  DB_PATH=${DB_PATH} npm start`);
console.log('');

db.close();
