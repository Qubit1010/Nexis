import { DatabaseSync } from 'node:sqlite';
import { mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { randomUUID } from 'node:crypto';

const SCHEMA = `
CREATE TABLE IF NOT EXISTS leads (
  id          TEXT PRIMARY KEY,
  name        TEXT NOT NULL,
  email       TEXT NOT NULL,
  company     TEXT NOT NULL DEFAULT '',
  budget      INTEGER NOT NULL,
  timeline    TEXT NOT NULL,
  services    TEXT NOT NULL DEFAULT '[]',
  needs       TEXT NOT NULL,
  source      TEXT NOT NULL DEFAULT '',
  status      TEXT NOT NULL DEFAULT 'new',
  score       INTEGER NOT NULL DEFAULT 0,
  band        TEXT NOT NULL DEFAULT 'cold',
  breakdown   TEXT NOT NULL DEFAULT '[]',
  notes       TEXT NOT NULL DEFAULT '',
  created_at  TEXT NOT NULL,
  updated_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_leads_score  ON leads (score DESC);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads (status);

CREATE TABLE IF NOT EXISTS rules (
  id       TEXT PRIMARY KEY,
  label    TEXT NOT NULL,
  field    TEXT NOT NULL,
  operator TEXT NOT NULL,
  value    TEXT NOT NULL,
  points   INTEGER NOT NULL,
  enabled  INTEGER NOT NULL DEFAULT 1,
  position INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
`;

/**
 * The default rule set, seeded once so the tool qualifies leads before anyone
 * configures it. Every one of these is editable in the dashboard.
 */
const DEFAULT_RULES: ReadonlyArray<{
  label: string;
  field: string;
  operator: string;
  value: unknown;
  points: number;
}> = [
  { label: 'Budget $10k or more', field: 'budget', operator: 'gte', value: 10000, points: 35 },
  { label: 'Budget $5k or more', field: 'budget', operator: 'gte', value: 5000, points: 20 },
  { label: 'Budget under $1k', field: 'budget', operator: 'lte', value: 999, points: -15 },
  { label: 'Ready to start now', field: 'timeline', operator: 'eq', value: 'asap', points: 20 },
  { label: 'Starting within a month', field: 'timeline', operator: 'eq', value: '1_month', points: 12 },
  { label: 'Only exploring', field: 'timeline', operator: 'eq', value: 'exploring', points: -12 },
  { label: 'Wants AI automation', field: 'services', operator: 'contains', value: 'ai-automation', points: 15 },
  { label: 'Wants a custom app', field: 'services', operator: 'contains', value: 'web-app', points: 8 },
  { label: 'Has a company', field: 'company', operator: 'present', value: '', points: 8 },
  { label: 'Personal email domain', field: 'email', operator: 'contains', value: 'gmail.com', points: -5 },
  { label: 'Mentions automation', field: 'needs', operator: 'contains', value: 'automat', points: 5 },
];

const DEFAULT_BANDS = { hot: 70, warm: 40 };

let instance: DatabaseSync | null = null;
let instancePath: string | null = null;

function databasePath(): string {
  const configured = process.env.LEADQ_DB_PATH?.trim();
  if (configured) return configured === ':memory:' ? configured : resolve(configured);
  return resolve(process.cwd(), 'data', 'leads.db');
}

function seed(db: DatabaseSync): void {
  const existing = db.prepare('SELECT COUNT(*) AS n FROM rules').get() as { n: number };
  if (existing.n > 0) return;

  const insert = db.prepare(
    `INSERT INTO rules (id, label, field, operator, value, points, enabled, position)
     VALUES (?, ?, ?, ?, ?, ?, 1, ?)`,
  );
  DEFAULT_RULES.forEach((rule, index) => {
    insert.run(
      randomUUID(),
      rule.label,
      rule.field,
      rule.operator,
      JSON.stringify(rule.value),
      rule.points,
      index,
    );
  });

  const setting = db.prepare('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)');
  setting.run('band_hot', String(DEFAULT_BANDS.hot));
  setting.run('band_warm', String(DEFAULT_BANDS.warm));
}

/**
 * Lazy singleton. The schema is idempotent, so opening an existing file is a no-op;
 * there is no deployed history to migrate from yet, which is why there is no migration
 * runner. Reopens automatically if LEADQ_DB_PATH changes, which is what the tests rely on.
 */
export function getDb(): DatabaseSync {
  const path = databasePath();
  if (instance && instancePath === path) return instance;
  if (instance) instance.close();

  if (path !== ':memory:') mkdirSync(dirname(path), { recursive: true });

  const db = new DatabaseSync(path);
  db.exec('PRAGMA journal_mode = WAL');
  db.exec('PRAGMA foreign_keys = ON');
  db.exec(SCHEMA);
  seed(db);

  instance = db;
  instancePath = path;
  return db;
}

/** Test helper. Closes the handle so a temp file can be deleted on Windows. */
export function closeDb(): void {
  instance?.close();
  instance = null;
  instancePath = null;
}
