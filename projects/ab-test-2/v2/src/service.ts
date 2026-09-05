import type { DatabaseSync } from 'node:sqlite';
import { nowIso } from './db.ts';
import type { Draft, Enquiry, PromptVersion, Verdict } from './db.ts';
import { compare, editRatio, median, wilson } from './metrics.ts';
import type { Comparison, Interval } from './metrics.ts';
import type { Provider } from './providers/index.ts';

/** Which drafts a rollup should count. */
export type Scope = 'all' | 'bench' | 'live';

function scopeClause(scope: Scope): string {
  if (scope === 'bench') return 'AND d.bench_run_id IS NOT NULL';
  if (scope === 'live') return 'AND d.bench_run_id IS NULL';
  return '';
}

// --------------------------------------------------------------------------------------
// Prompt versions
// --------------------------------------------------------------------------------------

export function listPrompts(db: DatabaseSync): PromptVersion[] {
  return db.prepare('SELECT * FROM prompt_versions ORDER BY id ASC').all() as PromptVersion[];
}

export function getPrompt(db: DatabaseSync, id: number): PromptVersion | null {
  return (db.prepare('SELECT * FROM prompt_versions WHERE id = ?').get(id) as PromptVersion) ?? null;
}

export function getActivePrompt(db: DatabaseSync): PromptVersion | null {
  return (
    (db
      .prepare('SELECT * FROM prompt_versions WHERE is_active = 1 ORDER BY id DESC LIMIT 1')
      .get() as PromptVersion) ?? null
  );
}

/**
 * Prompt versions are immutable. "Editing the prompt" creates a new row, so every draft's
 * attribution to the exact text that produced it stays true forever.
 */
export function createPrompt(
  db: DatabaseSync,
  input: { label: string; system_prompt: string; activate?: boolean },
): PromptVersion {
  const activate = input.activate !== false;
  const res = db
    .prepare(
      'INSERT INTO prompt_versions (label, system_prompt, created_at, is_active) VALUES (?, ?, ?, 0)',
    )
    .run(input.label, input.system_prompt, nowIso());
  const id = Number(res.lastInsertRowid);
  if (activate) activatePrompt(db, id);
  return getPrompt(db, id)!;
}

export function activatePrompt(db: DatabaseSync, id: number): PromptVersion | null {
  const existing = getPrompt(db, id);
  if (!existing) return null;
  db.prepare('UPDATE prompt_versions SET is_active = 0 WHERE is_active = 1').run();
  db.prepare('UPDATE prompt_versions SET is_active = 1 WHERE id = ?').run(id);
  return getPrompt(db, id);
}

// --------------------------------------------------------------------------------------
// Enquiries
// --------------------------------------------------------------------------------------

export type EnquiryRow = Enquiry & { draft_count: number; reviewed_count: number };

export function listEnquiries(db: DatabaseSync): EnquiryRow[] {
  return db
    .prepare(
      `SELECT e.*,
              (SELECT COUNT(*) FROM drafts d WHERE d.enquiry_id = e.id) AS draft_count,
              (SELECT COUNT(*) FROM drafts d JOIN reviews r ON r.draft_id = d.id
                WHERE d.enquiry_id = e.id) AS reviewed_count
         FROM enquiries e
        ORDER BY e.id DESC`,
    )
    .all() as EnquiryRow[];
}

export function getEnquiry(db: DatabaseSync, id: number): Enquiry | null {
  return (db.prepare('SELECT * FROM enquiries WHERE id = ?').get(id) as Enquiry) ?? null;
}

export function createEnquiry(
  db: DatabaseSync,
  input: { subject: string; body: string; sender?: string | null; in_bench?: boolean },
): Enquiry {
  const res = db
    .prepare(
      'INSERT INTO enquiries (subject, body, sender, in_bench, created_at) VALUES (?, ?, ?, ?, ?)',
    )
    .run(input.subject, input.body, input.sender ?? null, input.in_bench ? 1 : 0, nowIso());
  return getEnquiry(db, Number(res.lastInsertRowid))!;
}

export function setBenchMembership(db: DatabaseSync, id: number, inBench: boolean): Enquiry | null {
  if (!getEnquiry(db, id)) return null;
  db.prepare('UPDATE enquiries SET in_bench = ? WHERE id = ?').run(inBench ? 1 : 0, id);
  return getEnquiry(db, id);
}

// --------------------------------------------------------------------------------------
// Drafts
// --------------------------------------------------------------------------------------

export type DraftWithReview = Draft & {
  prompt_label: string;
  verdict: Verdict | null;
  final_text: string | null;
  edit_ratio: number | null;
  note: string | null;
};

export function listDrafts(db: DatabaseSync, enquiryId: number): DraftWithReview[] {
  return db
    .prepare(
      `SELECT d.*, p.label AS prompt_label,
              r.verdict, r.final_text, r.edit_ratio, r.note
         FROM drafts d
         JOIN prompt_versions p ON p.id = d.prompt_version_id
         LEFT JOIN reviews r ON r.draft_id = d.id
        WHERE d.enquiry_id = ?
        ORDER BY d.id DESC`,
    )
    .all(enquiryId) as DraftWithReview[];
}

export function getDraft(db: DatabaseSync, id: number): Draft | null {
  return (db.prepare('SELECT * FROM drafts WHERE id = ?').get(id) as Draft) ?? null;
}

export async function generateDraft(
  db: DatabaseSync,
  provider: Provider,
  input: { enquiryId: number; promptVersionId?: number; benchRunId?: number },
): Promise<DraftWithReview> {
  const enquiry = getEnquiry(db, input.enquiryId);
  if (!enquiry) throw new NotFound('enquiry not found');

  const version = input.promptVersionId
    ? getPrompt(db, input.promptVersionId)
    : getActivePrompt(db);
  if (!version) throw new NotFound('prompt version not found');

  const result = await provider.draft({
    systemPrompt: version.system_prompt,
    subject: enquiry.subject,
    body: enquiry.body,
    sender: enquiry.sender,
  });

  const res = db
    .prepare(
      `INSERT INTO drafts
         (enquiry_id, prompt_version_id, text, provider, model,
          input_tokens, output_tokens, cost_usd, latency_ms, bench_run_id, created_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    )
    .run(
      enquiry.id,
      version.id,
      result.text,
      result.provider,
      result.model,
      result.inputTokens,
      result.outputTokens,
      result.costUsd,
      result.latencyMs,
      input.benchRunId ?? null,
      nowIso(),
    );

  const id = Number(res.lastInsertRowid);
  return db
    .prepare(
      `SELECT d.*, p.label AS prompt_label, NULL AS verdict, NULL AS final_text,
              NULL AS edit_ratio, NULL AS note
         FROM drafts d JOIN prompt_versions p ON p.id = d.prompt_version_id
        WHERE d.id = ?`,
    )
    .get(id) as DraftWithReview;
}

// --------------------------------------------------------------------------------------
// Reviews
// --------------------------------------------------------------------------------------

export type Review = {
  id: number;
  draft_id: number;
  verdict: Verdict;
  final_text: string;
  edit_ratio: number;
  note: string | null;
  created_at: string;
};

/**
 * Record a judgement. The edit ratio is computed here from the draft as served versus the
 * text the user kept, rather than trusted from the client, so the second signal cannot be
 * spoofed or accidentally mis-sent by the frontend.
 *
 * Re-rating an already-rated draft overwrites it. Changing your mind is legitimate, and
 * duplicate rows would double-count in every rollup.
 */
export function saveReview(
  db: DatabaseSync,
  input: { draftId: number; verdict: Verdict; finalText: string; note?: string | null },
): Review {
  const draft = getDraft(db, input.draftId);
  if (!draft) throw new NotFound('draft not found');

  const ratio = editRatio(draft.text, input.finalText);
  db.prepare(
    `INSERT INTO reviews (draft_id, verdict, final_text, edit_ratio, note, created_at)
     VALUES (?, ?, ?, ?, ?, ?)
     ON CONFLICT(draft_id) DO UPDATE SET
       verdict = excluded.verdict,
       final_text = excluded.final_text,
       edit_ratio = excluded.edit_ratio,
       note = excluded.note,
       created_at = excluded.created_at`,
  ).run(input.draftId, input.verdict, input.finalText, ratio, input.note ?? null, nowIso());

  return db.prepare('SELECT * FROM reviews WHERE draft_id = ?').get(input.draftId) as Review;
}

// --------------------------------------------------------------------------------------
// Scoreboard
// --------------------------------------------------------------------------------------

export type VersionStats = {
  prompt_version_id: number;
  label: string;
  created_at: string;
  is_active: boolean;
  drafts_total: number;
  reviewed: number;
  good: number;
  bad: number;
  approval: number | null;
  interval: Interval;
  median_edit_ratio: number | null;
  kept_verbatim: number;
  providers: string[];
  /** True when this version's reviewed drafts mix offline-mock and live output. */
  mixed_providers: boolean;
  cost_usd: number | null;
};

type ReviewedRow = {
  prompt_version_id: number;
  verdict: Verdict;
  edit_ratio: number;
  provider: string;
};

function reviewedRows(db: DatabaseSync, scope: Scope): ReviewedRow[] {
  return db
    .prepare(
      `SELECT d.prompt_version_id, d.provider, r.verdict, r.edit_ratio
         FROM drafts d JOIN reviews r ON r.draft_id = d.id
        WHERE 1=1 ${scopeClause(scope)}`,
    )
    .all() as ReviewedRow[];
}

export function scoreboard(db: DatabaseSync, scope: Scope = 'all'): VersionStats[] {
  const versions = listPrompts(db);
  const rows = reviewedRows(db, scope);

  const totals = db
    .prepare(
      `SELECT d.prompt_version_id AS vid, COUNT(*) AS n,
              SUM(COALESCE(d.cost_usd, 0)) AS cost,
              SUM(CASE WHEN d.cost_usd IS NULL THEN 1 ELSE 0 END) AS uncosted
         FROM drafts d WHERE 1=1 ${scopeClause(scope)}
        GROUP BY d.prompt_version_id`,
    )
    .all() as Array<{ vid: number; n: number; cost: number; uncosted: number }>;

  return versions.map((v) => {
    const mine = rows.filter((r) => r.prompt_version_id === v.id);
    const good = mine.filter((r) => r.verdict === 'good').length;
    const ratios = mine.map((r) => r.edit_ratio);
    const providers = [...new Set(mine.map((r) => r.provider))].sort();
    const total = totals.find((t) => t.vid === v.id);
    // Only report a cost when every draft in the group actually carried one, so an
    // offline run can never render as "$0.00 spent" and look like a measurement.
    const cost = total && total.uncosted === 0 ? total.cost : null;

    return {
      prompt_version_id: v.id,
      label: v.label,
      created_at: v.created_at,
      is_active: v.is_active === 1,
      drafts_total: total?.n ?? 0,
      reviewed: mine.length,
      good,
      bad: mine.length - good,
      approval: mine.length > 0 ? good / mine.length : null,
      interval: wilson(good, mine.length),
      median_edit_ratio: median(ratios),
      kept_verbatim: ratios.filter((r) => r === 0).length,
      providers,
      mixed_providers: providers.length > 1,
      cost_usd: cost,
    };
  });
}

export function comparison(
  db: DatabaseSync,
  aId: number,
  bId: number,
  scope: Scope = 'all',
): Comparison {
  const rows = reviewedRows(db, scope);
  const sideFor = (id: number) => {
    const mine = rows.filter((r) => r.prompt_version_id === id);
    return {
      good: mine.filter((r) => r.verdict === 'good').length,
      n: mine.length,
      edit_ratios: mine.map((r) => r.edit_ratio),
    };
  };
  return compare(sideFor(aId), sideFor(bId));
}

// --------------------------------------------------------------------------------------
// Bench
// --------------------------------------------------------------------------------------

export type BenchRun = { id: number; prompt_version_id: number; created_at: string };

export function listBenchRuns(
  db: DatabaseSync,
): Array<BenchRun & { label: string; drafts: number }> {
  return db
    .prepare(
      `SELECT b.*, p.label,
              (SELECT COUNT(*) FROM drafts d WHERE d.bench_run_id = b.id) AS drafts
         FROM bench_runs b JOIN prompt_versions p ON p.id = b.prompt_version_id
        ORDER BY b.id DESC`,
    )
    .all() as Array<BenchRun & { label: string; drafts: number }>;
}

export function benchEnquiries(db: DatabaseSync): Enquiry[] {
  return db
    .prepare('SELECT * FROM enquiries WHERE in_bench = 1 ORDER BY id ASC')
    .all() as Enquiry[];
}

/**
 * Draft every bench enquiry with one prompt version.
 *
 * This is the surface that actually answers "is my prompt getting better". The live
 * scoreboard is confounded by which enquiries happened to arrive that week; the bench
 * holds the inputs identical so the only thing that varied is the prompt.
 */
export async function runBench(
  db: DatabaseSync,
  provider: Provider,
  promptVersionId: number,
): Promise<{ run: BenchRun; drafts: DraftWithReview[] }> {
  const version = getPrompt(db, promptVersionId);
  if (!version) throw new NotFound('prompt version not found');

  const set = benchEnquiries(db);
  if (set.length === 0) {
    throw new BadRequest('the bench is empty; flag some enquiries into it first');
  }

  const res = db
    .prepare('INSERT INTO bench_runs (prompt_version_id, created_at) VALUES (?, ?)')
    .run(promptVersionId, nowIso());
  const runId = Number(res.lastInsertRowid);

  const drafts: DraftWithReview[] = [];
  for (const e of set) {
    drafts.push(
      await generateDraft(db, provider, {
        enquiryId: e.id,
        promptVersionId,
        benchRunId: runId,
      }),
    );
  }

  return {
    run: db.prepare('SELECT * FROM bench_runs WHERE id = ?').get(runId) as BenchRun,
    drafts,
  };
}

export function benchRunDrafts(
  db: DatabaseSync,
  runId: number,
): Array<DraftWithReview & { subject: string }> {
  return db
    .prepare(
      `SELECT d.*, p.label AS prompt_label, e.subject,
              r.verdict, r.final_text, r.edit_ratio, r.note
         FROM drafts d
         JOIN prompt_versions p ON p.id = d.prompt_version_id
         JOIN enquiries e ON e.id = d.enquiry_id
         LEFT JOIN reviews r ON r.draft_id = d.id
        WHERE d.bench_run_id = ?
        ORDER BY d.id ASC`,
    )
    .all(runId) as Array<DraftWithReview & { subject: string }>;
}

// --------------------------------------------------------------------------------------

export class NotFound extends Error {}
export class BadRequest extends Error {}
