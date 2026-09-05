/** Everything that touches the leads table. Kept apart from the routes so the routes stay thin. */

import type { DB } from './db.ts';
import { getRules, getThresholds } from './db.ts';
import { scoreLead } from './scoring.ts';
import type { ScorableLead } from './scoring.ts';
import type { LeadSubmission } from './schemas.ts';
import { SORTABLE } from './schemas.ts';

export type LeadRow = {
  id: number; created_at: string; updated_at: string;
  name: string; email: string; company: string;
  budget: number; timeline: number; needs: string; message: string;
  score: number; band: string; score_breakdown: string;
  status: string; notes: string;
};

export type Lead = Omit<LeadRow, 'needs' | 'score_breakdown'> & {
  needs: string[];
  score_breakdown: { rule_id: number; label: string; points: number; matched: boolean }[];
};

const parseJson = <T>(raw: string, fallback: T): T => {
  try {
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
};

export const hydrate = (row: LeadRow): Lead => ({
  ...row,
  needs: parseJson<string[]>(row.needs, []),
  score_breakdown: parseJson<Lead['score_breakdown']>(row.score_breakdown, []),
});

export function insertLead(db: DB, input: LeadSubmission): Lead {
  const scorable: ScorableLead = {
    budget: input.budget,
    timeline: input.timeline,
    needs: input.needs,
    company: input.company,
    message: input.message,
    email: input.email,
  };
  const result = scoreLead(scorable, getRules(db), getThresholds(db));
  const now = new Date().toISOString();

  const info = db
    .prepare(
      `INSERT INTO leads
        (created_at, updated_at, name, email, company, budget, timeline, needs, message,
         score, band, score_breakdown, status, notes)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'new', '')`,
    )
    .run(
      now, now, input.name, input.email, input.company, input.budget, input.timeline,
      JSON.stringify(input.needs), input.message,
      result.score, result.band, JSON.stringify(result.breakdown),
    );

  return getLead(db, Number(info.lastInsertRowid))!;
}

export function getLead(db: DB, id: number): Lead | null {
  const row = db.prepare('SELECT * FROM leads WHERE id = ?').get(id) as LeadRow | undefined;
  return row ? hydrate(row) : null;
}

export type ListFilters = {
  status?: string; band?: string; q?: string;
  sort: (typeof SORTABLE)[number]; dir: 'asc' | 'desc'; limit: number;
};

export function listLeads(db: DB, f: ListFilters): Lead[] {
  const where: string[] = [];
  const params: (string | number)[] = [];

  if (f.status) { where.push('status = ?'); params.push(f.status); }
  if (f.band) { where.push('band = ?'); params.push(f.band); }
  if (f.q) {
    where.push('(name LIKE ? OR email LIKE ? OR company LIKE ? OR message LIKE ?)');
    const like = `%${f.q}%`;
    params.push(like, like, like, like);
  }

  // Both interpolated fragments come from a closed allowlist, never from raw input.
  const col = SORTABLE.includes(f.sort) ? f.sort : 'score';
  const dir = f.dir === 'asc' ? 'ASC' : 'DESC';
  const clause = where.length ? `WHERE ${where.join(' AND ')}` : '';

  const rows = db
    .prepare(`SELECT * FROM leads ${clause} ORDER BY ${col} ${dir}, id DESC LIMIT ?`)
    .all(...params, f.limit) as LeadRow[];
  return rows.map(hydrate);
}

export function updateLead(db: DB, id: number, patch: { status?: string; notes?: string }): Lead | null {
  if (!getLead(db, id)) return null;
  const sets: string[] = ['updated_at = ?'];
  const params: (string | number)[] = [new Date().toISOString()];
  if (patch.status !== undefined) { sets.push('status = ?'); params.push(patch.status); }
  if (patch.notes !== undefined) { sets.push('notes = ?'); params.push(patch.notes); }
  db.prepare(`UPDATE leads SET ${sets.join(', ')} WHERE id = ?`).run(...params, id);
  return getLead(db, id);
}

export function deleteLead(db: DB, id: number): boolean {
  return db.prepare('DELETE FROM leads WHERE id = ?').run(id).changes > 0;
}

/**
 * Re-run every lead through the current rules. This is the point of storing rules as data:
 * change a rule, and the pipeline you already have re-ranks itself.
 */
export function rescoreAll(db: DB): { rescored: number; changed: number } {
  const rules = getRules(db);
  const thresholds = getThresholds(db);
  const rows = db.prepare('SELECT * FROM leads').all() as LeadRow[];
  const update = db.prepare(
    'UPDATE leads SET score = ?, band = ?, score_breakdown = ? WHERE id = ?',
  );

  let changed = 0;
  db.exec('BEGIN');
  try {
    for (const row of rows) {
      const lead = hydrate(row);
      const result = scoreLead(lead, rules, thresholds);
      if (result.score !== row.score || result.band !== row.band) changed++;
      update.run(result.score, result.band, JSON.stringify(result.breakdown), row.id);
    }
    db.exec('COMMIT');
  } catch (err) {
    db.exec('ROLLBACK');
    throw err;
  }
  return { rescored: rows.length, changed };
}

export function stats(db: DB): Record<string, number> {
  const byStatus = db
    .prepare('SELECT status, COUNT(*) AS n FROM leads GROUP BY status')
    .all() as { status: string; n: number }[];
  const byBand = db
    .prepare('SELECT band, COUNT(*) AS n FROM leads GROUP BY band')
    .all() as { band: string; n: number }[];
  const out: Record<string, number> = {
    total: 0, new: 0, contacted: 0, qualified: 0, dead: 0, hot: 0, warm: 0, cold: 0,
  };
  let total = 0;
  for (const r of byStatus) { out[r.status] = r.n; total += r.n; }
  for (const r of byBand) out[r.band] = r.n;
  out.total = total;
  return out;
}
