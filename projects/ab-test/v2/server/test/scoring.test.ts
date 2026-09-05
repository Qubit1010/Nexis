import { describe, expect, it } from 'vitest';
import { bandFor, ruleMatches, scoreLead } from '../src/scoring.ts';
import type { Rule, ScorableLead, Thresholds } from '../src/scoring.ts';

const lead = (over: Partial<ScorableLead> = {}): ScorableLead => ({
  budget: 3,
  timeline: 3,
  needs: ['website'],
  company: 'Northwind Trading',
  message: 'We need a new marketing site.',
  email: 'sam@northwind.com',
  ...over,
});

let nextId = 1;
const rule = (over: Partial<Rule> = {}): Rule => ({
  id: nextId++,
  label: 'rule',
  field: 'budget',
  op: 'gte',
  value: '3',
  points: 10,
  enabled: true,
  sort: 0,
  ...over,
});

const thresholds: Thresholds = { hot_min: 60, warm_min: 30 };

describe('ruleMatches - numeric fields', () => {
  it('gte matches at the boundary and above', () => {
    expect(ruleMatches(rule({ field: 'budget', op: 'gte', value: '3' }), lead({ budget: 3 }))).toBe(true);
    expect(ruleMatches(rule({ field: 'budget', op: 'gte', value: '3' }), lead({ budget: 5 }))).toBe(true);
    expect(ruleMatches(rule({ field: 'budget', op: 'gte', value: '3' }), lead({ budget: 2 }))).toBe(false);
  });

  it('lte matches at the boundary and below', () => {
    expect(ruleMatches(rule({ field: 'timeline', op: 'lte', value: '2' }), lead({ timeline: 2 }))).toBe(true);
    expect(ruleMatches(rule({ field: 'timeline', op: 'lte', value: '2' }), lead({ timeline: 1 }))).toBe(true);
    expect(ruleMatches(rule({ field: 'timeline', op: 'lte', value: '2' }), lead({ timeline: 3 }))).toBe(false);
  });

  it('eq is exact', () => {
    expect(ruleMatches(rule({ op: 'eq', value: '4' }), lead({ budget: 4 }))).toBe(true);
    expect(ruleMatches(rule({ op: 'eq', value: '4' }), lead({ budget: 5 }))).toBe(false);
  });

  it('does not fire when the rule value is not a number', () => {
    expect(ruleMatches(rule({ op: 'gte', value: 'lots' }), lead({ budget: 5 }))).toBe(false);
  });

  it('does not fire when a text operator is put on a numeric field', () => {
    expect(ruleMatches(rule({ field: 'budget', op: 'contains', value: '3' }), lead({ budget: 3 }))).toBe(false);
  });
});

describe('ruleMatches - needs', () => {
  it('includes matches a selected need', () => {
    const r = rule({ field: 'needs', op: 'includes', value: 'ai-automation' });
    expect(ruleMatches(r, lead({ needs: ['website', 'ai-automation'] }))).toBe(true);
    expect(ruleMatches(r, lead({ needs: ['website'] }))).toBe(false);
    expect(ruleMatches(r, lead({ needs: [] }))).toBe(false);
  });

  it('survives a needs value that is not an array', () => {
    const r = rule({ field: 'needs', op: 'includes', value: 'website' });
    expect(ruleMatches(r, { ...lead(), needs: null as unknown as string[] })).toBe(false);
  });
});

describe('ruleMatches - text fields', () => {
  it('contains is case insensitive', () => {
    const r = rule({ field: 'message', op: 'contains', value: 'MARKETING' });
    expect(ruleMatches(r, lead())).toBe(true);
  });

  it('not_contains is the exact inverse', () => {
    const hit = rule({ field: 'email', op: 'contains', value: '@gmail.' });
    const miss = rule({ field: 'email', op: 'not_contains', value: '@gmail.' });
    const gmail = lead({ email: 'sam@gmail.com' });
    expect(ruleMatches(hit, gmail)).toBe(true);
    expect(ruleMatches(miss, gmail)).toBe(false);
    expect(ruleMatches(hit, lead())).toBe(false);
    expect(ruleMatches(miss, lead())).toBe(true);
  });

  it('an empty needle never matches, rather than matching everything', () => {
    expect(ruleMatches(rule({ field: 'company', op: 'contains', value: '' }), lead())).toBe(false);
    expect(ruleMatches(rule({ field: 'company', op: 'not_contains', value: '' }), lead())).toBe(false);
  });

  it('does not fire when a numeric operator is put on a text field', () => {
    expect(ruleMatches(rule({ field: 'company', op: 'gte', value: '1' }), lead())).toBe(false);
  });
});

describe('scoreLead', () => {
  it('sums the points of every matching rule', () => {
    const rules = [
      rule({ field: 'budget', op: 'gte', value: '3', points: 30 }),
      rule({ field: 'timeline', op: 'gte', value: '3', points: 20 }),
      rule({ field: 'needs', op: 'includes', value: 'ai-automation', points: 25 }),
    ];
    expect(scoreLead(lead(), rules, thresholds).score).toBe(50);
  });

  it('applies negative points', () => {
    const rules = [
      rule({ field: 'budget', op: 'gte', value: '3', points: 40 }),
      rule({ field: 'email', op: 'contains', value: '@gmail.', points: -15 }),
    ];
    expect(scoreLead(lead({ email: 'a@gmail.com' }), rules, thresholds).score).toBe(25);
  });

  it('ignores disabled rules but still reports the raw total honestly', () => {
    const rules = [
      rule({ field: 'budget', op: 'gte', value: '3', points: 40 }),
      rule({ field: 'timeline', op: 'gte', value: '1', points: 40, enabled: false }),
    ];
    const result = scoreLead(lead(), rules, thresholds);
    expect(result.score).toBe(40);
    expect(result.breakdown).toHaveLength(1);
  });

  it('clamps to 100 but keeps the uncapped raw total', () => {
    const rules = [
      rule({ points: 80 }),
      rule({ field: 'timeline', op: 'gte', value: '1', points: 80 }),
    ];
    const result = scoreLead(lead(), rules, thresholds);
    expect(result.score).toBe(100);
    expect(result.raw).toBe(160);
  });

  it('clamps to 0 rather than going negative', () => {
    const rules = [rule({ points: -90 }), rule({ field: 'timeline', op: 'gte', value: '1', points: -90 })];
    const result = scoreLead(lead(), rules, thresholds);
    expect(result.score).toBe(0);
    expect(result.raw).toBe(-180);
  });

  it('records every evaluated rule in the breakdown, matched or not', () => {
    const rules = [
      rule({ label: 'fires', field: 'budget', op: 'gte', value: '3', points: 10 }),
      rule({ label: 'misses', field: 'budget', op: 'gte', value: '5', points: 10 }),
    ];
    const { breakdown } = scoreLead(lead(), rules, thresholds);
    expect(breakdown.map((b) => [b.label, b.matched])).toEqual([
      ['fires', true],
      ['misses', false],
    ]);
  });

  it('scores zero and stays cold with no rules at all', () => {
    const result = scoreLead(lead(), [], thresholds);
    expect(result).toMatchObject({ score: 0, raw: 0, band: 'cold', breakdown: [] });
  });

  it('is deterministic across repeated calls', () => {
    const rules = [rule({ points: 33 })];
    const a = scoreLead(lead(), rules, thresholds);
    const b = scoreLead(lead(), rules, thresholds);
    expect(a).toEqual(b);
  });
});

describe('bandFor', () => {
  it('places a score in the right band at each boundary', () => {
    expect(bandFor(60, thresholds)).toBe('hot');
    expect(bandFor(59, thresholds)).toBe('warm');
    expect(bandFor(30, thresholds)).toBe('warm');
    expect(bandFor(29, thresholds)).toBe('cold');
    expect(bandFor(0, thresholds)).toBe('cold');
  });

  it('follows the thresholds when they are moved', () => {
    const strict: Thresholds = { hot_min: 90, warm_min: 70 };
    expect(bandFor(85, strict)).toBe('warm');
    expect(bandFor(85, thresholds)).toBe('hot');
  });
});
