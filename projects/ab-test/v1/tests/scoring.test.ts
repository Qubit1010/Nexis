import { describe, expect, it } from 'vitest';
import { bandFor, clampScore, matches, scoreLead } from '@/lib/scoring';
import type { Bands, Rule, RuleField, RuleOperator, RuleValue, ScorableLead } from '@/types';

const BANDS: Bands = { hot: 70, warm: 40 };

function lead(overrides: Partial<ScorableLead> = {}): ScorableLead {
  return {
    name: 'Dana Reyes',
    email: 'dana@acme.io',
    company: 'Acme',
    budget: 10000,
    timeline: 'asap',
    services: ['ai-automation', 'web-app'],
    needs: 'We need our intake automated end to end.',
    source: 'referral',
    ...overrides,
  };
}

let counter = 0;
function rule(
  field: RuleField,
  operator: RuleOperator,
  value: RuleValue,
  points = 10,
  enabled = true,
): Rule {
  counter += 1;
  return {
    id: 'rule-' + counter,
    label: field + ' ' + operator,
    field,
    operator,
    value,
    points,
    enabled,
    position: counter,
  };
}

describe('matches - numeric operators', () => {
  it('gte fires at and above the threshold', () => {
    expect(matches(rule('budget', 'gte', 10000), lead())).toBe(true);
    expect(matches(rule('budget', 'gte', 5000), lead())).toBe(true);
    expect(matches(rule('budget', 'gte', 25000), lead())).toBe(false);
  });

  it('lte fires at and below the threshold', () => {
    expect(matches(rule('budget', 'lte', 999), lead({ budget: 0 }))).toBe(true);
    expect(matches(rule('budget', 'lte', 999), lead({ budget: 1000 }))).toBe(false);
  });

  it('coerces a numeric operand stored as a string', () => {
    expect(matches(rule('budget', 'gte', '5000'), lead())).toBe(true);
  });

  it('counts list length when a numeric operator is used on an array field', () => {
    expect(matches(rule('services', 'gte', 2), lead())).toBe(true);
    expect(matches(rule('services', 'gte', 3), lead())).toBe(false);
  });
});

describe('matches - equality operators', () => {
  it('eq compares strings case-insensitively', () => {
    expect(matches(rule('timeline', 'eq', 'asap'), lead())).toBe(true);
    expect(matches(rule('timeline', 'eq', 'ASAP'), lead())).toBe(true);
    expect(matches(rule('timeline', 'eq', 'exploring'), lead())).toBe(false);
  });

  it('eq compares numbers numerically, not as text', () => {
    expect(matches(rule('budget', 'eq', 10000), lead())).toBe(true);
    expect(matches(rule('budget', 'eq', 10001), lead())).toBe(false);
  });

  it('neq is the exact negation of eq', () => {
    const target = lead();
    for (const value of ['asap', 'exploring', '']) {
      const eq = matches(rule('timeline', 'eq', value), target);
      const neq = matches(rule('timeline', 'neq', value), target);
      expect(neq).toBe(!eq);
    }
  });
});

describe('matches - text and list operators', () => {
  it('contains does a case-insensitive substring match on text', () => {
    expect(matches(rule('needs', 'contains', 'automat'), lead())).toBe(true);
    expect(matches(rule('needs', 'contains', 'AUTOMAT'), lead())).toBe(true);
    expect(matches(rule('needs', 'contains', 'shopify'), lead())).toBe(false);
  });

  it('contains does membership on a list field, not substring', () => {
    expect(matches(rule('services', 'contains', 'ai-automation'), lead())).toBe(true);
    expect(matches(rule('services', 'contains', 'ai-'), lead())).toBe(false);
  });

  it('contains never fires on a number field', () => {
    expect(matches(rule('budget', 'contains', '10000'), lead())).toBe(false);
  });

  it('contains with an empty operand never fires', () => {
    expect(matches(rule('needs', 'contains', ''), lead())).toBe(false);
  });

  it('in matches when the field intersects the candidate list', () => {
    expect(matches(rule('timeline', 'in', ['asap', '1_month']), lead())).toBe(true);
    expect(matches(rule('timeline', 'in', ['exploring']), lead())).toBe(false);
    expect(matches(rule('services', 'in', ['cms', 'web-app']), lead())).toBe(true);
    expect(matches(rule('services', 'in', ['cms', 'data']), lead())).toBe(false);
  });

  it('in with an empty list never fires', () => {
    expect(matches(rule('timeline', 'in', []), lead())).toBe(false);
  });
});

describe('matches - presence', () => {
  it('present is true for a filled field, false for an empty one', () => {
    expect(matches(rule('company', 'present', ''), lead())).toBe(true);
    expect(matches(rule('company', 'present', ''), lead({ company: '' }))).toBe(false);
    expect(matches(rule('company', 'present', ''), lead({ company: '   ' }))).toBe(false);
  });

  it('absent is the complement of present', () => {
    expect(matches(rule('company', 'absent', ''), lead({ company: '' }))).toBe(true);
    expect(matches(rule('company', 'absent', ''), lead())).toBe(false);
  });

  it('treats an empty list as absent and a zero budget as absent', () => {
    expect(matches(rule('services', 'absent', ''), lead({ services: [] }))).toBe(true);
    expect(matches(rule('budget', 'present', ''), lead({ budget: 0 }))).toBe(false);
  });
});

describe('matches - malformed rules never throw', () => {
  it('returns false for an operator that cannot apply to the field', () => {
    expect(matches(rule('needs', 'gte', 5), lead())).toBe(false);
    expect(matches(rule('budget', 'in', ['asap']), lead())).toBe(false);
    expect(matches(rule('timeline', 'gte', 'not-a-number'), lead())).toBe(false);
  });
});

describe('bandFor', () => {
  it('places a score in the right band, inclusive at each threshold', () => {
    expect(bandFor(70, BANDS)).toBe('hot');
    expect(bandFor(69, BANDS)).toBe('warm');
    expect(bandFor(40, BANDS)).toBe('warm');
    expect(bandFor(39, BANDS)).toBe('cold');
    expect(bandFor(0, BANDS)).toBe('cold');
  });
});

describe('clampScore', () => {
  it('holds the score inside 0 to 100', () => {
    expect(clampScore(-40)).toBe(0);
    expect(clampScore(180)).toBe(100);
    expect(clampScore(55)).toBe(55);
  });
});

describe('scoreLead', () => {
  it('sums the points of every rule that fires', () => {
    const result = scoreLead(
      lead(),
      [rule('budget', 'gte', 5000, 20), rule('timeline', 'eq', 'asap', 15)],
      BANDS,
    );
    expect(result.score).toBe(35);
    expect(result.band).toBe('cold');
  });

  it('applies negative points and floors the total at zero', () => {
    const result = scoreLead(
      lead({ budget: 0, timeline: 'exploring' }),
      [rule('budget', 'lte', 999, -15), rule('timeline', 'eq', 'exploring', -12)],
      BANDS,
    );
    expect(result.score).toBe(0);
    expect(result.band).toBe('cold');
    expect(result.breakdown).toHaveLength(2);
  });

  it('caps the total at 100 even when the rules sum higher', () => {
    const result = scoreLead(
      lead(),
      [
        rule('budget', 'gte', 5000, 60),
        rule('timeline', 'eq', 'asap', 60),
        rule('company', 'present', '', 60),
      ],
      BANDS,
    );
    expect(result.score).toBe(100);
    expect(result.band).toBe('hot');
  });

  it('skips disabled rules entirely, including in the breakdown', () => {
    const result = scoreLead(
      lead(),
      [rule('budget', 'gte', 5000, 20), rule('timeline', 'eq', 'asap', 50, false)],
      BANDS,
    );
    expect(result.score).toBe(20);
    expect(result.breakdown).toHaveLength(1);
    expect(result.breakdown[0]?.points).toBe(20);
  });

  it('lists only the rules that fired, with their label and points', () => {
    const fires = rule('budget', 'gte', 5000, 20);
    fires.label = 'Budget $5k or more';
    const misses = rule('timeline', 'eq', 'exploring', 30);

    const result = scoreLead(lead(), [fires, misses], BANDS);

    expect(result.breakdown).toEqual([
      { ruleId: fires.id, label: 'Budget $5k or more', points: 20 },
    ]);
  });

  it('scores zero with an empty rule set rather than failing', () => {
    const result = scoreLead(lead(), [], BANDS);
    expect(result).toEqual({ score: 0, band: 'cold', breakdown: [] });
  });

  it('stacks tiered rules, which is why the breakdown exists', () => {
    const result = scoreLead(
      lead({ budget: 10000 }),
      [rule('budget', 'gte', 10000, 35), rule('budget', 'gte', 5000, 20)],
      BANDS,
    );
    expect(result.score).toBe(55);
    expect(result.breakdown).toHaveLength(2);
  });
});
