import { DatabaseSync } from 'node:sqlite';
import { mkdirSync } from 'node:fs';
import { dirname } from 'node:path';
import type { Rule, Thresholds } from './scoring.ts';

export type DB = DatabaseSync;

const SCHEMA = `
CREATE TABLE IF NOT EXISTS leads (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at      TEXT    NOT NULL,
  updated_at      TEXT    NOT NULL,
  name            TEXT    NOT NULL,
  email           TEXT    NOT NULL,
  company         TEXT    NOT NULL DEFAULT '',
  budget          INTEGER NOT NULL,
  timeline        INTEGER NOT NULL,
  needs           TEXT    NOT NULL DEFAULT '[]',
  message         TEXT    NOT NULL DEFAULT '',
  score           INTEGER NOT NULL DEFAULT 0,
  band            TEXT    NOT NULL DEFAULT 'cold',
  score_breakdown TEXT    NOT NULL DEFAULT '[]',
  status          TEXT    NOT NULL DEFAULT 'new',
  notes           TEXT    NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_leads_score  ON leads(score DESC);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);

CREATE TABLE IF NOT EXISTS rules (
  id      INTEGER PRIMARY KEY AUTOINCREMENT,
  label   TEXT    NOT NULL,
  field   TEXT    NOT NULL,
  op      TEXT    NOT NULL,
  value   TEXT    NOT NULL,
  points  INTEGER NOT NULL,
  enabled INTEGER NOT NULL DEFAULT 1,
  sort    INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS settings (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
`;

/** The rule set a fresh install starts with. Editable immediately; this is just a sane floor. */
const DEFAULT_RULES: Omit<Rule, 'id'>[] = [
  { label: 'Budget $15k or more',            field: 'budget',   op: 'gte',          value: '4',              points: 30, enabled: true, sort: 10 },
  { label: 'Budget $5k - $15k',              field: 'budget',   op: 'eq',           value: '3',              points: 18, enabled: true, sort: 20 },
  { label: 'Budget under $1k',               field: 'budget',   op: 'lte',          value: '1',              points: -15, enabled: true, sort: 30 },
  { label: 'Ready to start within a month',  field: 'timeline', op: 'gte',          value: '4',              points: 25, enabled: true, sort: 40 },
  { label: 'No fixed start date',            field: 'timeline', op: 'lte',          value: '1',              points: -10, enabled: true, sort: 50 },
  { label: 'Wants AI automation',            field: 'needs',    op: 'includes',     value: 'ai-automation',  points: 20, enabled: true, sort: 60 },
  { label: 'Wants a custom web app',         field: 'needs',    op: 'includes',     value: 'web-app',        points: 12, enabled: true, sort: 70 },
  { label: 'Says the work is urgent',        field: 'message',  op: 'contains',     value: 'asap',           points: 8,  enabled: false, sort: 80 },
  { label: 'Reads like a student project',   field: 'message',  op: 'contains',     value: 'student',        points: -20, enabled: true, sort: 90 },
  { label: 'Free email domain (gmail)',      field: 'email',    op: 'contains',     value: '@gmail.',        points: -8, enabled: true, sort: 100 },
];

const DEFAULT_SETTINGS: Record<string, string> = { hot_min: '60', warm_min: '30' };

export function openDb(path: string): DB {
  if (path !== ':memory:') mkdirSync(dirname(path), { recursive: true });
  const db = new DatabaseSync(path);
  db.exec('PRAGMA journal_mode = WAL');
  db.exec('PRAGMA foreign_keys = ON');
  db.exec(SCHEMA);
  seed(db);
  return db;
}

function seed(db: DB): void {
  const setting = db.prepare('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)');
  for (const [k, v] of Object.entries(DEFAULT_SETTINGS)) setting.run(k, v);

  const count = db.prepare('SELECT COUNT(*) AS n FROM rules').get() as { n: number };
  if (count.n > 0) return;
  const insert = db.prepare(
    'INSERT INTO rules (label, field, op, value, points, enabled, sort) VALUES (?, ?, ?, ?, ?, ?, ?)',
  );
  for (const r of DEFAULT_RULES) {
    insert.run(r.label, r.field, r.op, r.value, r.points, r.enabled ? 1 : 0, r.sort);
  }
}

type RuleRow = {
  id: number; label: string; field: string; op: string;
  value: string; points: number; enabled: number; sort: number;
};

export function getRules(db: DB): Rule[] {
  const rows = db.prepare('SELECT * FROM rules ORDER BY sort ASC, id ASC').all() as RuleRow[];
  return rows.map((r) => ({ ...r, enabled: r.enabled === 1 }) as Rule);
}

export function getThresholds(db: DB): Thresholds {
  const rows = db.prepare('SELECT key, value FROM settings').all() as { key: string; value: string }[];
  const map = new Map(rows.map((r) => [r.key, r.value]));
  return {
    hot_min: Number(map.get('hot_min') ?? 60),
    warm_min: Number(map.get('warm_min') ?? 30),
  };
}

export function setSetting(db: DB, key: string, value: string): void {
  db.prepare(
    'INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value',
  ).run(key, value);
}
