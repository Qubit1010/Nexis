import { randomUUID } from 'node:crypto';
import { getDb } from './db';
import { getBands, listRules } from './rules';
import { scoreLead } from './scoring';
import type {
  Band,
  BreakdownEntry,
  Lead,
  LeadStatus,
  ScorableLead,
  StatusCounts,
} from '@/types';

interface LeadRow {
  id: string;
  name: string;
  email: string;
  company: string;
  budget: number;
  timeline: string;
  services: string;
  needs: string;
  source: string;
  status: string;
  score: number;
  band: string;
  breakdown: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

function parseJsonArray<T>(raw: string): T[] {
  try {
    const parsed: unknown = JSON.parse(raw);
    return Array.isArray(parsed) ? (parsed as T[]) : [];
  } catch {
    return [];
  }
}

function toLead(row: LeadRow): Lead {
  return {
    id: row.id,
    name: row.name,
    email: row.email,
    company: row.company,
    budget: row.budget,
    timeline: row.timeline,
    services: parseJsonArray<string>(row.services),
    needs: row.needs,
    source: row.source,
    status: row.status as LeadStatus,
    score: row.score,
    band: row.band as Band,
    breakdown: parseJsonArray<BreakdownEntry>(row.breakdown),
    notes: row.notes,
    createdAt: row.created_at,
    updatedAt: row.updated_at,
  };
}

function toScorable(row: LeadRow): ScorableLead {
  return {
    name: row.name,
    email: row.email,
    company: row.company,
    budget: row.budget,
    timeline: row.timeline,
    services: parseJsonArray<string>(row.services),
    needs: row.needs,
    source: row.source,
  };
}

export function createLead(input: ScorableLead): Lead {
  const now = new Date().toISOString();
  const id = randomUUID();
  const { score, band, breakdown } = scoreLead(input, listRules(), getBands());

  getDb()
    .prepare(
      "INSERT INTO leads (id, name, email, company, budget, timeline, services, needs, source, status, score, band, breakdown, notes, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'new', ?, ?, ?, '', ?, ?)",
    )
    .run(
      id,
      input.name,
      input.email,
      input.company,
      input.budget,
      input.timeline,
      JSON.stringify(input.services),
      input.needs,
      input.source,
      score,
      band,
      JSON.stringify(breakdown),
      now,
      now,
    );

  return getLead(id) as Lead;
}

export interface LeadFilter {
  status?: string;
  band?: string;
  sort?: string;
  order?: string;
  q?: string;
}

/** Column whitelist. The sort key arrives in a query string, so it is never interpolated raw. */
const SORT_COLUMNS: Record<string, string> = {
  score: 'score',
  created_at: 'created_at',
  name: 'name',
};

export function listLeads(filter: LeadFilter = {}): Lead[] {
  const where: string[] = [];
  const params: (string | number)[] = [];

  if (filter.status && filter.status !== 'all') {
    where.push('status = ?');
    params.push(filter.status);
  }
  if (filter.band && filter.band !== 'all') {
    where.push('band = ?');
    params.push(filter.band);
  }
  if (filter.q) {
    const needle = '%' + filter.q.toLowerCase() + '%';
    where.push(
      '(LOWER(name) LIKE ? OR LOWER(company) LIKE ? OR LOWER(email) LIKE ? OR LOWER(needs) LIKE ?)',
    );
    params.push(needle, needle, needle, needle);
  }

  const column = SORT_COLUMNS[filter.sort ?? 'score'] ?? 'score';
  const direction = filter.order === 'asc' ? 'ASC' : 'DESC';
  const clause = where.length > 0 ? 'WHERE ' + where.join(' AND ') : '';

  const rows = getDb()
    .prepare(
      'SELECT * FROM leads ' + clause + ' ORDER BY ' + column + ' ' + direction + ', created_at DESC',
    )
    .all(...params) as unknown as LeadRow[];

  return rows.map(toLead);
}

function getLead(id: string): Lead | null {
  const row = getDb().prepare('SELECT * FROM leads WHERE id = ?').get(id) as
    | unknown
    | undefined;
  return row ? toLead(row as LeadRow) : null;
}

export function updateLead(
  id: string,
  patch: { status?: LeadStatus; notes?: string },
): Lead | null {
  if (!getLead(id)) return null;

  const sets: string[] = [];
  const params: (string | number)[] = [];

  if (patch.status !== undefined) {
    sets.push('status = ?');
    params.push(patch.status);
  }
  if (patch.notes !== undefined) {
    sets.push('notes = ?');
    params.push(patch.notes);
  }
  if (sets.length === 0) return getLead(id);

  sets.push('updated_at = ?');
  params.push(new Date().toISOString(), id);

  getDb()
    .prepare('UPDATE leads SET ' + sets.join(', ') + ' WHERE id = ?')
    .run(...params);

  return getLead(id);
}

export function deleteLead(id: string): boolean {
  const result = getDb().prepare('DELETE FROM leads WHERE id = ?').run(id);
  return Number(result.changes) > 0;
}

export function countsByStatus(): StatusCounts {
  const rows = getDb()
    .prepare('SELECT status, COUNT(*) AS n FROM leads GROUP BY status')
    .all() as unknown as { status: string; n: number }[];

  const counts: StatusCounts = { all: 0, new: 0, contacted: 0, qualified: 0, dead: 0 };
  for (const row of rows) {
    counts.all += row.n;
    if (row.status in counts) counts[row.status as LeadStatus] = row.n;
  }
  return counts;
}

/**
 * Rewrites score, band and breakdown for every lead from the current rules.
 * The dashboard sorts on the stored score column, so those three fields are derived data
 * that must be refreshed whenever the rules change. Returns how many rows were touched.
 */
export function rescoreAll(): number {
  const rules = listRules();
  const bands = getBands();
  const db = getDb();

  const rows = db.prepare('SELECT * FROM leads').all() as unknown as LeadRow[];
  const update = db.prepare(
    'UPDATE leads SET score = ?, band = ?, breakdown = ?, updated_at = ? WHERE id = ?',
  );
  const now = new Date().toISOString();

  for (const row of rows) {
    const { score, band, breakdown } = scoreLead(toScorable(row), rules, bands);
    update.run(score, band, JSON.stringify(breakdown), now, row.id);
  }

  return rows.length;
}
