import { DatabaseSync } from 'node:sqlite';
import { mkdirSync } from 'node:fs';
import { dirname } from 'node:path';

export type Verdict = 'good' | 'bad';

export type PromptVersion = {
  id: number;
  label: string;
  system_prompt: string;
  created_at: string;
  is_active: number;
};

export type Enquiry = {
  id: number;
  subject: string;
  body: string;
  sender: string | null;
  in_bench: number;
  created_at: string;
};

export type Draft = {
  id: number;
  enquiry_id: number;
  prompt_version_id: number;
  text: string;
  provider: string;
  model: string;
  input_tokens: number | null;
  output_tokens: number | null;
  cost_usd: number | null;
  latency_ms: number;
  bench_run_id: number | null;
  created_at: string;
};

const SCHEMA = `
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS prompt_versions (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  label         TEXT    NOT NULL,
  system_prompt TEXT    NOT NULL,
  created_at    TEXT    NOT NULL,
  is_active     INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS enquiries (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  subject    TEXT    NOT NULL,
  body       TEXT    NOT NULL,
  sender     TEXT,
  in_bench   INTEGER NOT NULL DEFAULT 0,
  created_at TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS bench_runs (
  id                INTEGER PRIMARY KEY AUTOINCREMENT,
  prompt_version_id INTEGER NOT NULL REFERENCES prompt_versions(id),
  created_at        TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS drafts (
  id                INTEGER PRIMARY KEY AUTOINCREMENT,
  enquiry_id        INTEGER NOT NULL REFERENCES enquiries(id) ON DELETE CASCADE,
  prompt_version_id INTEGER NOT NULL REFERENCES prompt_versions(id),
  text              TEXT    NOT NULL,
  provider          TEXT    NOT NULL,
  model             TEXT    NOT NULL,
  input_tokens      INTEGER,
  output_tokens     INTEGER,
  cost_usd          REAL,
  latency_ms        INTEGER NOT NULL,
  bench_run_id      INTEGER REFERENCES bench_runs(id) ON DELETE SET NULL,
  created_at        TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS reviews (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  draft_id   INTEGER NOT NULL UNIQUE REFERENCES drafts(id) ON DELETE CASCADE,
  verdict    TEXT    NOT NULL CHECK (verdict IN ('good','bad')),
  final_text TEXT    NOT NULL,
  edit_ratio REAL    NOT NULL,
  note       TEXT,
  created_at TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_drafts_version ON drafts(prompt_version_id);
CREATE INDEX IF NOT EXISTS idx_drafts_enquiry ON drafts(enquiry_id);
CREATE INDEX IF NOT EXISTS idx_drafts_bench   ON drafts(bench_run_id);
CREATE INDEX IF NOT EXISTS idx_reviews_draft  ON reviews(draft_id);
`;

/**
 * Open (and if needed create) the database. Pass ':memory:' for tests.
 * WAL is skipped for in-memory databases, where it is meaningless.
 */
export function openDb(path: string): DatabaseSync {
  if (path !== ':memory:') mkdirSync(dirname(path), { recursive: true });
  const db = new DatabaseSync(path);
  const schema = path === ':memory:'
    ? SCHEMA.replace('PRAGMA journal_mode = WAL;', '')
    : SCHEMA;
  db.exec(schema);
  return db;
}

export function nowIso(): string {
  return new Date().toISOString();
}
