/**
 * Opt-in demo data, so the Scoreboard can be seen working before you have rated anything real.
 *
 * This is NOT run automatically. Fabricated ratings in your real database would corrupt the
 * one measurement this app exists to provide, so it refuses to touch a database that already
 * has enquiries in it unless you pass --force, and it writes to a separate file by default.
 *
 *   npm run seed:demo                 -> data/demo.db
 *   REPLYLAB_DB=data/demo.db npm start
 */

import path from 'node:path';

import { PROJECT_ROOT, loadConfig } from '../server/config.ts';
import {
  createEnquiry,
  createPromptVersion,
  getActivePromptVersion,
  insertDraft,
  openDb,
  updateDraft,
} from '../server/db.ts';
import { createStubProvider } from '../server/providers.ts';
import { measureEdit } from '../server/text.ts';

const force = process.argv.includes('--force');
const config = loadConfig();

// Resolved against the project root, not the shell's cwd, so this always writes where it says.
// Defaults to a separate file from the real database.
const dbPath = path.resolve(PROJECT_ROOT, process.env.REPLYLAB_DB ?? 'data/demo.db');

const db = openDb(dbPath);

const existing = db.prepare('SELECT COUNT(*) AS n FROM enquiries').get() as { n: number };
if (existing.n > 0 && !force) {
  console.error(
    `[seed] ${dbPath} already has ${existing.n} enquiries. Refusing to add demo data on top of ` +
      'real data. Pass --force if you are sure, or delete the file first.',
  );
  process.exit(1);
}

const provider = createStubProvider(config.model);

const ENQUIRIES: Array<[string, string]> = [
  [
    'Website redesign for a dental group',
    'Hi, we run three dental clinics and our site is eight years old. Bookings come through a phone line and we lose a lot of them. What would a rebuild plus online booking cost, and how quickly could you start?',
  ],
  [
    'Need help automating our invoicing',
    'We are a small logistics firm. Invoices are made by hand in Excel and it eats about a day a week. Can you build something that pulls from our job sheets automatically?',
  ],
  [
    'Quote for a Shopify store',
    'Looking to move off Etsy onto our own Shopify store. About 200 products. Do you do migrations and what do you charge?',
  ],
  [
    'AI chatbot for customer support',
    'We get the same 20 questions over and over. Is a chatbot worth it for a company our size, about 40 staff? What is realistic here and what is hype?',
  ],
  [
    'Urgent: site down after plugin update',
    'Our WordPress site went white after an update this morning. We are losing orders. Can you look at it today?',
  ],
  [
    'Ongoing retainer enquiry',
    'We have a site already but nobody maintaining it. Do you do monthly retainers, and what would be included?',
  ],
];

// Three prompt versions with a deliberate shape: v2 is a real improvement, v3 overcorrects.
// That is the interesting case for a scoreboard, not a straight line up.
const VERSIONS: Array<{ label: string; prompt: string; goodRate: number }> = [
  { label: 'Starting voice', prompt: 'seeded', goodRate: 0.5 },
  {
    label: 'Answer the question first',
    prompt: `You are drafting replies to inbound client enquiries as me.

Lead with a direct answer to what they actually asked. No preamble, no "hope you are well".
Short sentences. Name a concrete next step. Never invent prices or timelines - ask instead.
Sign off as "Aleem".`,
    goodRate: 0.83,
  },
  {
    label: 'Much shorter, always ask budget',
    prompt: `You are drafting replies to inbound client enquiries as me.

Maximum three sentences. Always ask about budget in the first reply. Be blunt.
Sign off as "Aleem".`,
    goodRate: 0.42,
  },
];

/** Strips the stub scaffolding and tightens an opening: the kind of small pass a good draft gets. */
function lightEdit(text: string): string {
  return text
    .split('\n')
    .filter((line) => !line.startsWith('[STUB') && !line.startsWith('(stub fingerprint'))
    .join('\n')
    .trim()
    .replace('Thanks for reaching out about this.', 'Thanks for getting in touch.')
    .replace('Appreciate you getting in touch.', 'Thanks for the note.');
}

/** A full rewrite: what a bad draft gets, where almost nothing of the original survives. */
function heavyEdit(subject: string): string {
  return [
    'Hi,',
    '',
    `Thanks for the note about ${subject.toLowerCase()}. Short answer: yes, this is squarely something we do.`,
    '',
    'Two things would let me give you a real number instead of a range: your rough timeline, and',
    'whether you have a budget in mind. Send those over and I will come back with a concrete plan.',
    '',
    'Best,',
    'Aleem',
  ].join('\n');
}

const enquiryIds = ENQUIRIES.map(([subject, body]) => createEnquiry(db, subject, body).id);

let seeded = 0;
let ratedCount = 0;

for (const [index, spec] of VERSIONS.entries()) {
  const version =
    index === 0 ? getActivePromptVersion(db) : createPromptVersion(db, spec.prompt, spec.label);

  // Deterministic pseudo-random so a re-seed produces the same demo picture.
  let counter = index * 97 + 13;
  const next = () => {
    counter = (counter * 1103515245 + 12345) % 2147483648;
    return counter / 2147483648;
  };

  for (const enquiryId of enquiryIds) {
    const enquiry = db.prepare('SELECT subject, body FROM enquiries WHERE id = ?').get(enquiryId) as {
      subject: string;
      body: string;
    };

    const result = await provider.draft({
      systemPrompt: index === 0 ? version.systemPrompt : spec.prompt,
      subject: enquiry.subject,
      body: enquiry.body,
    });

    const draft = insertDraft(db, {
      enquiryId,
      promptVersionId: version.id,
      provider: 'stub',
      model: config.model,
      generatedText: result.text,
      inputTokens: null,
      outputTokens: null,
      latencyMs: 900 + Math.floor(next() * 2200),
    });
    seeded += 1;

    const rating = next() < spec.goodRate ? 'good' : 'bad';
    updateDraft(db, draft.id, { rating });
    ratedCount += 1;

    // A good draft gets a light touch-up, a bad one gets rewritten. Both produce text a
    // human could plausibly have written, because this text is what you actually see in the
    // draft pane. This is what gives the "Kept" column something to say.
    const edited = rating === 'good' ? lightEdit(result.text) : heavyEdit(enquiry.subject);
    const measure = measureEdit(result.text, edited);
    updateDraft(db, draft.id, {
      editedText: edited,
      editDistance: measure.distance,
      editBaseWords: measure.baseWords,
    });
  }
}

// Leave the middle version active, so the app opens on the one that actually scored best.
const best = db.prepare('SELECT id FROM prompt_versions WHERE version = 2').get() as { id: number };
db.prepare('UPDATE prompt_versions SET is_active = 0').run();
db.prepare('UPDATE prompt_versions SET is_active = 1 WHERE id = ?').run(best.id);

db.close();

console.log(`[seed] wrote ${dbPath}`);
console.log(`[seed] ${enquiryIds.length} enquiries, ${seeded} drafts, ${ratedCount} ratings, 3 prompt versions`);
console.log('[seed] all drafts are stub text, and all ratings are fabricated demo data');
console.log('[seed] run it with:  REPLYLAB_DB=data/demo.db npm start');
