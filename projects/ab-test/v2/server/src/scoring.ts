/**
 * The scoring engine.
 *
 * Pure: no database, no clock, no I/O. Given the answers, the rules and the thresholds it
 * returns the same result every time. That is the whole reason this file exists separately
 * from the routes, and it is why it can be tested exhaustively.
 */

import { SCORE_MAX, SCORE_MIN } from './catalog.ts';
import type { Band, RuleField, RuleOp } from './catalog.ts';

export type Rule = {
  id: number;
  label: string;
  field: RuleField;
  op: RuleOp;
  value: string;
  points: number;
  enabled: boolean;
  sort: number;
};

export type ScorableLead = {
  budget: number;
  timeline: number;
  needs: string[];
  company: string;
  message: string;
  email: string;
};

export type Thresholds = { hot_min: number; warm_min: number };

export type BreakdownEntry = {
  rule_id: number;
  label: string;
  points: number;
  matched: boolean;
};

export type ScoreResult = {
  score: number;
  raw: number;
  band: Band;
  breakdown: BreakdownEntry[];
};

const text = (v: unknown): string => (typeof v === 'string' ? v.toLowerCase() : '');

/** Does a single rule fire against this lead? Never throws: a malformed rule simply misses. */
export function ruleMatches(rule: Rule, lead: ScorableLead): boolean {
  switch (rule.field) {
    case 'budget':
    case 'timeline': {
      const actual = lead[rule.field];
      const want = Number(rule.value);
      if (!Number.isFinite(actual) || !Number.isFinite(want)) return false;
      if (rule.op === 'gte') return actual >= want;
      if (rule.op === 'lte') return actual <= want;
      if (rule.op === 'eq') return actual === want;
      return false;
    }
    case 'needs': {
      if (rule.op !== 'includes') return false;
      const needs = Array.isArray(lead.needs) ? lead.needs : [];
      return needs.includes(rule.value);
    }
    case 'company':
    case 'message':
    case 'email': {
      const haystack = text(lead[rule.field]);
      const needle = text(rule.value);
      // An empty needle would match everything, which is never what anyone means.
      if (needle === '') return false;
      const hit = haystack.includes(needle);
      if (rule.op === 'contains') return hit;
      if (rule.op === 'not_contains') return !hit;
      return false;
    }
    default:
      return false;
  }
}

export function bandFor(score: number, t: Thresholds): Band {
  if (score >= t.hot_min) return 'hot';
  if (score >= t.warm_min) return 'warm';
  return 'cold';
}

/**
 * Sum the points of every enabled rule that fires, clamp to 0-100, assign a band.
 *
 * `raw` is kept unclamped in the result so the UI can be honest when a lead has blown
 * through the ceiling rather than silently pretending it landed on exactly 100.
 */
export function scoreLead(lead: ScorableLead, rules: Rule[], thresholds: Thresholds): ScoreResult {
  const breakdown: BreakdownEntry[] = [];
  let raw = 0;

  for (const rule of rules) {
    if (!rule.enabled) continue;
    const matched = ruleMatches(rule, lead);
    if (matched) raw += rule.points;
    breakdown.push({ rule_id: rule.id, label: rule.label, points: rule.points, matched });
  }

  const score = Math.max(SCORE_MIN, Math.min(SCORE_MAX, Math.round(raw)));
  return { score, raw, band: bandFor(score, thresholds), breakdown };
}
