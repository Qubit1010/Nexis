import { randomUUID } from 'node:crypto';
import { getDb } from './db';
import type { Bands, Rule, RuleField, RuleInput, RuleOperator, RuleValue } from '@/types';

interface RuleRow {
  id: string;
  label: string;
  field: string;
  operator: string;
  value: string;
  points: number;
  enabled: number;
  position: number;
}

function parseValue(raw: string): RuleValue {
  try {
    const parsed: unknown = JSON.parse(raw);
    if (typeof parsed === 'number' || typeof parsed === 'string') return parsed;
    if (Array.isArray(parsed)) return parsed.map(String);
  } catch {
    // A hand-edited database row can hold a bare string. Treat it as one.
  }
  return raw;
}

function toRule(row: RuleRow): Rule {
  return {
    id: row.id,
    label: row.label,
    field: row.field as RuleField,
    operator: row.operator as RuleOperator,
    value: parseValue(row.value),
    points: row.points,
    enabled: row.enabled === 1,
    position: row.position,
  };
}

export function listRules(): Rule[] {
  const rows = getDb()
    .prepare('SELECT * FROM rules ORDER BY position ASC')
    .all() as unknown as RuleRow[];
  return rows.map(toRule);
}

export function getBands(): Bands {
  const rows = getDb()
    .prepare("SELECT key, value FROM settings WHERE key IN ('band_hot', 'band_warm')")
    .all() as unknown as { key: string; value: string }[];
  const lookup = new Map(rows.map((row) => [row.key, Number(row.value)]));
  return {
    hot: lookup.get('band_hot') ?? 70,
    warm: lookup.get('band_warm') ?? 40,
  };
}

export function setBands(bands: Bands): void {
  const statement = getDb().prepare(
    'INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value',
  );
  statement.run('band_hot', String(bands.hot));
  statement.run('band_warm', String(bands.warm));
}

/**
 * Replaces the whole rule set. Identity is not preserved across a save: the editor submits
 * an ordered list, and array position becomes `position`. That keeps reordering and
 * deletion trivial, at the cost of losing rule ids, which nothing else references.
 */
export function replaceRules(inputs: RuleInput[]): void {
  const db = getDb();
  db.prepare('DELETE FROM rules').run();
  const insert = db.prepare(
    'INSERT INTO rules (id, label, field, operator, value, points, enabled, position) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
  );
  inputs.forEach((rule, index) => {
    insert.run(
      randomUUID(),
      rule.label,
      rule.field,
      rule.operator,
      JSON.stringify(rule.value),
      rule.points,
      rule.enabled ? 1 : 0,
      index,
    );
  });
}
