import type {
  Band,
  Bands,
  BreakdownEntry,
  Rule,
  RuleValue,
  ScorableLead,
  ScoreResult,
} from '@/types';

const MIN_SCORE = 0;
const MAX_SCORE = 100;

type FieldValue = number | string | string[];

function fieldValue(lead: ScorableLead, field: Rule['field']): FieldValue {
  switch (field) {
    case 'budget':
      return lead.budget;
    case 'services':
      return lead.services;
    case 'timeline':
      return lead.timeline;
    case 'needs':
      return lead.needs;
    case 'company':
      return lead.company;
    case 'source':
      return lead.source;
    case 'email':
      return lead.email;
  }
}

function norm(value: unknown): string {
  return String(value ?? '').trim().toLowerCase();
}

function toNumber(value: unknown): number | null {
  if (typeof value === 'number') return Number.isFinite(value) ? value : null;
  if (typeof value === 'string' && value.trim() !== '') {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
}

/** Every field flattened to a comparable list of normalized strings. */
function toList(value: FieldValue | RuleValue): string[] {
  if (Array.isArray(value)) return value.map(norm).filter((entry) => entry !== '');
  const single = norm(value);
  return single === '' ? [] : [single];
}

function isPresent(value: FieldValue): boolean {
  if (Array.isArray(value)) return value.length > 0;
  if (typeof value === 'number') return value > 0;
  return norm(value) !== '';
}

/**
 * Whether a single rule fires for a lead.
 *
 * Semantics are intentionally forgiving in one direction only: an operator that cannot
 * apply to a field's type (`gte` on free text, `contains` on a number) returns false
 * rather than throwing, so a badly configured rule can never take the dashboard down.
 */
export function matches(rule: Rule, lead: ScorableLead): boolean {
  const field = fieldValue(lead, rule.field);

  switch (rule.operator) {
    case 'present':
      return isPresent(field);

    case 'absent':
      return !isPresent(field);

    case 'gte':
    case 'lte': {
      const left = toNumber(Array.isArray(field) ? field.length : field);
      const right = toNumber(rule.value);
      if (left === null || right === null) return false;
      return rule.operator === 'gte' ? left >= right : left <= right;
    }

    case 'eq':
    case 'neq': {
      const left = toNumber(field);
      const right = toNumber(rule.value);
      const equal =
        left !== null && right !== null && !Array.isArray(field)
          ? left === right
          : toList(field).includes(norm(rule.value));
      return rule.operator === 'eq' ? equal : !equal;
    }

    case 'contains': {
      const needle = norm(rule.value);
      if (needle === '') return false;
      if (Array.isArray(field)) return toList(field).includes(needle);
      if (typeof field === 'number') return false;
      return norm(field).includes(needle);
    }

    case 'in': {
      const candidates = toList(rule.value);
      if (candidates.length === 0) return false;
      return toList(field).some((entry) => candidates.includes(entry));
    }
  }
}

export function bandFor(score: number, bands: Bands): Band {
  if (score >= bands.hot) return 'hot';
  if (score >= bands.warm) return 'warm';
  return 'cold';
}

export function clampScore(total: number): number {
  return Math.max(MIN_SCORE, Math.min(MAX_SCORE, Math.round(total)));
}

/**
 * The whole qualification engine. Pure: no database, no request, no framework.
 * Disabled rules are skipped. Only rules that fire appear in the breakdown, which is
 * what the dashboard renders as the scoring receipt.
 */
export function scoreLead(lead: ScorableLead, rules: Rule[], bands: Bands): ScoreResult {
  const breakdown: BreakdownEntry[] = [];
  let total = 0;

  for (const rule of rules) {
    if (!rule.enabled) continue;
    if (!matches(rule, lead)) continue;
    total += rule.points;
    breakdown.push({ ruleId: rule.id, label: rule.label, points: rule.points });
  }

  const score = clampScore(total);
  return { score, band: bandFor(score, bands), breakdown };
}
