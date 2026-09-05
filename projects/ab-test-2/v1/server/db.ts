import { DatabaseSync } from 'node:sqlite';
import { mkdirSync } from 'node:fs';
import path from 'node:path';

import { estimateCostUsd } from './pricing.ts';

export type Db = DatabaseSync;

export const DEFAULT_SYSTEM_PROMPT = `You are drafting replies to inbound client enquiries on my behalf. You are writing as me, not about me.

Voice:
- Direct and warm. Confident without being stiff. Write like a sharp founder, not a corporate template.
- Short sentences. Say it in one line if one line will do.
- No fluff, no preamble, no "I hope this email finds you well".
- No emojis. No em dashes - use commas or periods.
- Plain words over jargon. Never oversell.

Substance:
- Answer the actual question they asked before anything else.
- If the enquiry is vague, ask at most two specific questions that would change the answer.
- Where it fits, name a concrete next step: a call, a scoped proposal, a timeline.
- Never invent prices, dates, case studies, or capabilities. If something needs a number I have
  not given you, ask for what you need instead of guessing.

Format:
- Greeting, three to five short paragraphs, sign off as "Aleem".
- Output only the reply body. No subject line, no commentary, no explanation of your choices.`;

const SCHEMA = `
CREATE TABLE IF NOT EXISTS prompt_versions (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  version       INTEGER NOT NULL UNIQUE,
  label         TEXT    NOT NULL,
  system_prompt TEXT    NOT NULL,
  created_at    TEXT    NOT NULL,
  is_active     INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS enquiries (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  subject    TEXT NOT NULL,
  body       TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS drafts (
  id                INTEGER PRIMARY KEY AUTOINCREMENT,
  enquiry_id        INTEGER NOT NULL REFERENCES enquiries(id)       ON DELETE CASCADE,
  prompt_version_id INTEGER NOT NULL REFERENCES prompt_versions(id) ON DELETE RESTRICT,
  provider          TEXT    NOT NULL,
  model             TEXT    NOT NULL,
  generated_text    TEXT    NOT NULL,
  edited_text       TEXT,
  rating            TEXT CHECK (rating IN ('good', 'bad')),
  edit_distance     INTEGER,
  edit_base_words   INTEGER,
  input_tokens      INTEGER,
  output_tokens     INTEGER,
  latency_ms        INTEGER,
  created_at        TEXT NOT NULL,
  rated_at          TEXT
);

CREATE INDEX IF NOT EXISTS idx_drafts_enquiry ON drafts(enquiry_id);
CREATE INDEX IF NOT EXISTS idx_drafts_version ON drafts(prompt_version_id);
`;

export function openDb(dbPath: string): Db {
  if (dbPath !== ':memory:') {
    mkdirSync(path.dirname(dbPath), { recursive: true });
  }
  const db = new DatabaseSync(dbPath);
  db.exec('PRAGMA journal_mode = WAL;');
  db.exec('PRAGMA foreign_keys = ON;');
  db.exec(SCHEMA);
  seedFirstPromptVersion(db);
  return db;
}

function seedFirstPromptVersion(db: Db): void {
  const row = db.prepare('SELECT COUNT(*) AS n FROM prompt_versions').get() as { n: number };
  if (row.n > 0) return;
  db.prepare(
    `INSERT INTO prompt_versions (version, label, system_prompt, created_at, is_active)
     VALUES (1, ?, ?, ?, 1)`,
  ).run('Starting voice', DEFAULT_SYSTEM_PROMPT, now());
}

export function now(): string {
  return new Date().toISOString();
}

function toId(value: number | bigint): number {
  return Number(value);
}

// --------------------------------------------------------------------------------------
// Types
// --------------------------------------------------------------------------------------

export type PromptVersion = {
  id: number;
  version: number;
  label: string;
  systemPrompt: string;
  createdAt: string;
  isActive: boolean;
};

export type Enquiry = {
  id: number;
  subject: string;
  body: string;
  createdAt: string;
};

export type EnquirySummary = {
  id: number;
  subject: string;
  bodyPreview: string;
  createdAt: string;
  draftCount: number;
  latestRating: 'good' | 'bad' | null;
};

export type Draft = {
  id: number;
  enquiryId: number;
  promptVersionId: number;
  promptVersion: number;
  provider: string;
  model: string;
  generatedText: string;
  editedText: string | null;
  rating: 'good' | 'bad' | null;
  editDistance: number | null;
  editBaseWords: number | null;
  keepRatio: number | null;
  inputTokens: number | null;
  outputTokens: number | null;
  latencyMs: number | null;
  costUsd: number | null;
  createdAt: string;
  ratedAt: string | null;
};

type PromptRow = {
  id: number;
  version: number;
  label: string;
  system_prompt: string;
  created_at: string;
  is_active: number;
};

type DraftRow = {
  id: number;
  enquiry_id: number;
  prompt_version_id: number;
  prompt_version: number;
  provider: string;
  model: string;
  generated_text: string;
  edited_text: string | null;
  rating: string | null;
  edit_distance: number | null;
  edit_base_words: number | null;
  input_tokens: number | null;
  output_tokens: number | null;
  latency_ms: number | null;
  created_at: string;
  rated_at: string | null;
};

function mapPrompt(row: PromptRow): PromptVersion {
  return {
    id: row.id,
    version: row.version,
    label: row.label,
    systemPrompt: row.system_prompt,
    createdAt: row.created_at,
    isActive: row.is_active === 1,
  };
}

function mapDraft(row: DraftRow): Draft {
  const keepRatio =
    row.edit_distance !== null && row.edit_base_words !== null && row.edit_base_words > 0
      ? Math.max(0, 1 - row.edit_distance / row.edit_base_words)
      : row.edit_distance === 0
        ? 1
        : null;

  return {
    id: row.id,
    enquiryId: row.enquiry_id,
    promptVersionId: row.prompt_version_id,
    promptVersion: row.prompt_version,
    provider: row.provider,
    model: row.model,
    generatedText: row.generated_text,
    editedText: row.edited_text,
    rating: row.rating === 'good' || row.rating === 'bad' ? row.rating : null,
    editDistance: row.edit_distance,
    editBaseWords: row.edit_base_words,
    keepRatio,
    inputTokens: row.input_tokens,
    outputTokens: row.output_tokens,
    latencyMs: row.latency_ms,
    costUsd: estimateCostUsd(row.input_tokens, row.output_tokens),
    createdAt: row.created_at,
    ratedAt: row.rated_at,
  };
}

const DRAFT_SELECT = `
  SELECT d.*, pv.version AS prompt_version
  FROM drafts d
  JOIN prompt_versions pv ON pv.id = d.prompt_version_id
`;

// --------------------------------------------------------------------------------------
// Prompt versions (append-only; only is_active is ever updated)
// --------------------------------------------------------------------------------------

export function listPromptVersions(db: Db): PromptVersion[] {
  const rows = db
    .prepare('SELECT * FROM prompt_versions ORDER BY version DESC')
    .all() as PromptRow[];
  return rows.map(mapPrompt);
}

export function getPromptVersion(db: Db, id: number): PromptVersion | null {
  const row = db.prepare('SELECT * FROM prompt_versions WHERE id = ?').get(id) as
    | PromptRow
    | undefined;
  return row ? mapPrompt(row) : null;
}

export function getActivePromptVersion(db: Db): PromptVersion {
  const row = db
    .prepare('SELECT * FROM prompt_versions WHERE is_active = 1 ORDER BY version DESC LIMIT 1')
    .get() as PromptRow | undefined;
  if (!row) throw new Error('No active prompt version. The database was not seeded correctly.');
  return mapPrompt(row);
}

export function createPromptVersion(db: Db, systemPrompt: string, label?: string): PromptVersion {
  const maxRow = db.prepare('SELECT COALESCE(MAX(version), 0) AS v FROM prompt_versions').get() as {
    v: number;
  };
  const nextVersion = maxRow.v + 1;
  const finalLabel = label && label.trim().length > 0 ? label.trim() : `Version ${nextVersion}`;

  db.exec('BEGIN');
  try {
    db.prepare('UPDATE prompt_versions SET is_active = 0').run();
    const result = db
      .prepare(
        `INSERT INTO prompt_versions (version, label, system_prompt, created_at, is_active)
         VALUES (?, ?, ?, ?, 1)`,
      )
      .run(nextVersion, finalLabel, systemPrompt, now());
    db.exec('COMMIT');
    return getPromptVersion(db, toId(result.lastInsertRowid)) as PromptVersion;
  } catch (error) {
    db.exec('ROLLBACK');
    throw error;
  }
}

export function activatePromptVersion(db: Db, id: number): PromptVersion | null {
  const existing = getPromptVersion(db, id);
  if (!existing) return null;

  db.exec('BEGIN');
  try {
    db.prepare('UPDATE prompt_versions SET is_active = 0').run();
    db.prepare('UPDATE prompt_versions SET is_active = 1 WHERE id = ?').run(id);
    db.exec('COMMIT');
  } catch (error) {
    db.exec('ROLLBACK');
    throw error;
  }
  return getPromptVersion(db, id);
}

// --------------------------------------------------------------------------------------
// Enquiries
// --------------------------------------------------------------------------------------

export function createEnquiry(db: Db, subject: string, body: string): Enquiry {
  const result = db
    .prepare('INSERT INTO enquiries (subject, body, created_at) VALUES (?, ?, ?)')
    .run(subject, body, now());
  return getEnquiry(db, toId(result.lastInsertRowid)) as Enquiry;
}

export function getEnquiry(db: Db, id: number): Enquiry | null {
  const row = db.prepare('SELECT * FROM enquiries WHERE id = ?').get(id) as
    | { id: number; subject: string; body: string; created_at: string }
    | undefined;
  if (!row) return null;
  return { id: row.id, subject: row.subject, body: row.body, createdAt: row.created_at };
}

export function listEnquiries(db: Db): EnquirySummary[] {
  const rows = db
    .prepare(
      `SELECT e.id, e.subject, e.body, e.created_at,
              (SELECT COUNT(*) FROM drafts d WHERE d.enquiry_id = e.id) AS draft_count,
              (SELECT d.rating FROM drafts d WHERE d.enquiry_id = e.id
                 ORDER BY d.id DESC LIMIT 1) AS latest_rating
       FROM enquiries e
       ORDER BY e.id DESC`,
    )
    .all() as Array<{
    id: number;
    subject: string;
    body: string;
    created_at: string;
    draft_count: number;
    latest_rating: string | null;
  }>;

  return rows.map((row) => ({
    id: row.id,
    subject: row.subject,
    bodyPreview: row.body.replace(/\s+/g, ' ').trim().slice(0, 140),
    createdAt: row.created_at,
    draftCount: row.draft_count,
    latestRating: row.latest_rating === 'good' || row.latest_rating === 'bad' ? row.latest_rating : null,
  }));
}

// --------------------------------------------------------------------------------------
// Drafts
// --------------------------------------------------------------------------------------

export type NewDraft = {
  enquiryId: number;
  promptVersionId: number;
  provider: string;
  model: string;
  generatedText: string;
  inputTokens: number | null;
  outputTokens: number | null;
  latencyMs: number;
};

export function insertDraft(db: Db, draft: NewDraft): Draft {
  const result = db
    .prepare(
      `INSERT INTO drafts
         (enquiry_id, prompt_version_id, provider, model, generated_text,
          input_tokens, output_tokens, latency_ms, created_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    )
    .run(
      draft.enquiryId,
      draft.promptVersionId,
      draft.provider,
      draft.model,
      draft.generatedText,
      draft.inputTokens,
      draft.outputTokens,
      draft.latencyMs,
      now(),
    );
  return getDraft(db, toId(result.lastInsertRowid)) as Draft;
}

export function getDraft(db: Db, id: number): Draft | null {
  const row = db.prepare(`${DRAFT_SELECT} WHERE d.id = ?`).get(id) as DraftRow | undefined;
  return row ? mapDraft(row) : null;
}

export function listDraftsForEnquiry(db: Db, enquiryId: number): Draft[] {
  const rows = db
    .prepare(`${DRAFT_SELECT} WHERE d.enquiry_id = ? ORDER BY d.id DESC`)
    .all(enquiryId) as DraftRow[];
  return rows.map(mapDraft);
}

export type DraftUpdate = {
  editedText?: string;
  editDistance?: number;
  editBaseWords?: number;
  rating?: 'good' | 'bad' | null;
};

/**
 * Note what this cannot do: there is no path that writes generated_text. The model's original
 * output is immutable, because it is the baseline the edit-distance signal is measured against.
 */
export function updateDraft(db: Db, id: number, update: DraftUpdate): Draft | null {
  const existing = getDraft(db, id);
  if (!existing) return null;

  if (update.editedText !== undefined) {
    db.prepare(
      'UPDATE drafts SET edited_text = ?, edit_distance = ?, edit_base_words = ? WHERE id = ?',
    ).run(update.editedText, update.editDistance ?? null, update.editBaseWords ?? null, id);
  }

  if (update.rating !== undefined) {
    db.prepare('UPDATE drafts SET rating = ?, rated_at = ? WHERE id = ?').run(
      update.rating,
      update.rating === null ? null : now(),
      id,
    );
  }

  return getDraft(db, id);
}
