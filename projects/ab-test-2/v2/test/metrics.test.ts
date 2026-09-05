import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import {
  MIN_N_FOR_VERDICT,
  compare,
  editRatio,
  levenshtein,
  median,
  tokenize,
  wilson,
} from '../src/metrics.ts';

describe('editRatio', () => {
  test('identical text scores 0', () => {
    assert.equal(editRatio('Hi Dana, thanks for reaching out.', 'Hi Dana, thanks for reaching out.'), 0);
  });

  test('ignores capitalisation and whitespace shape', () => {
    assert.equal(editRatio('Hi   Dana,\n\nthanks', 'hi Dana, thanks'), 0);
  });

  test('a total rewrite scores 1', () => {
    assert.equal(editRatio('alpha beta gamma', 'delta epsilon zeta'), 1);
  });

  test('one word changed in four scores 0.25', () => {
    assert.equal(editRatio('one two three four', 'one two three five'), 0.25);
  });

  test('normalises by the longer side, so additions count', () => {
    // 4 words kept, 4 appended: distance 4 over max length 8.
    assert.equal(editRatio('one two three four', 'one two three four five six seven eight'), 0.5);
  });

  test('is bounded to 0..1 for any pair', () => {
    const pairs: Array<[string, string]> = [
      ['', ''],
      ['', 'something here'],
      ['something here', ''],
      ['a', 'a b c d e f g'],
    ];
    for (const [a, b] of pairs) {
      const r = editRatio(a, b);
      assert.ok(r >= 0 && r <= 1, `${r} out of range for ${JSON.stringify([a, b])}`);
    }
  });

  test('empty against empty is 0, not NaN', () => {
    assert.equal(editRatio('', ''), 0);
    assert.equal(editRatio('   \n  ', ''), 0);
  });
});

describe('levenshtein', () => {
  test('handles empty sides', () => {
    assert.equal(levenshtein([], ['a', 'b']), 2);
    assert.equal(levenshtein(['a', 'b'], []), 2);
    assert.equal(levenshtein([], []), 0);
  });

  test('is symmetric', () => {
    const a = tokenize('the quick brown fox jumps');
    const b = tokenize('the slow brown dog jumps over');
    assert.equal(levenshtein(a, b), levenshtein(b, a));
  });

  test('counts a single substitution as 1', () => {
    assert.equal(levenshtein(['a', 'b', 'c'], ['a', 'x', 'c']), 1);
  });
});

describe('wilson', () => {
  test('brackets the point estimate', () => {
    const i = wilson(7, 10);
    assert.ok(i.low < 0.7 && i.high > 0.7);
  });

  test('stays inside 0..1 at the extremes, where the normal approximation would not', () => {
    const allGood = wilson(5, 5);
    assert.ok(allGood.high <= 1, 'upper bound must not exceed 1');
    assert.ok(allGood.low > 0 && allGood.low < 1);

    const allBad = wilson(0, 5);
    assert.ok(allBad.low >= 0, 'lower bound must not fall below 0');
    assert.ok(allBad.high > 0);
  });

  test('narrows as n grows', () => {
    const small = wilson(6, 10);
    const large = wilson(60, 100);
    assert.ok(large.high - large.low < small.high - small.low);
  });

  test('n = 0 returns the fully uninformative interval', () => {
    assert.deepEqual(wilson(0, 0), { low: 0, high: 1 });
  });
});

describe('median', () => {
  test('odd and even lengths', () => {
    assert.equal(median([3, 1, 2]), 2);
    assert.equal(median([4, 1, 3, 2]), 2.5);
  });

  test('empty is null rather than 0, so "no data" cannot read as "perfect"', () => {
    assert.equal(median([]), null);
  });

  test('does not mutate its input', () => {
    const input = [3, 1, 2];
    median(input);
    assert.deepEqual(input, [3, 1, 2]);
  });
});

describe('compare', () => {
  const side = (good: number, n: number, ratios: number[] = []) => ({
    good,
    n,
    edit_ratios: ratios.length ? ratios : new Array(n).fill(0.2),
  });

  test('refuses a verdict below the minimum sample on either side', () => {
    const c = compare(side(4, 4), side(20, 20));
    assert.equal(c.verdict, 'not enough data');
    assert.match(c.reason, /at least 5/);
  });

  test('the minimum applies to the candidate too', () => {
    assert.equal(compare(side(20, 20), side(4, 4)).verdict, 'not enough data');
  });

  test('a small edge on small samples is reported as noise, not a win', () => {
    // 5/8 vs 4/8: the naive reading is "62% beats 50%". The intervals overlap heavily.
    const c = compare(side(4, 8), side(5, 8));
    assert.equal(c.verdict, 'no detectable difference');
    assert.match(c.reason, /overlap/);
  });

  test('names a winner only when the intervals separate', () => {
    const c = compare(side(2, 40), side(38, 40));
    assert.equal(c.verdict, 'better');
  });

  test('detects a regression', () => {
    const c = compare(side(38, 40), side(2, 40));
    assert.equal(c.verdict, 'worse');
  });

  test('carries both sides stats through regardless of verdict', () => {
    const c = compare(side(3, 6, [0.1, 0.1, 0.5, 0.5, 0.3, 0.3]), side(5, 6));
    assert.equal(c.a.n, 6);
    assert.equal(c.a.approval, 0.5);
    assert.equal(c.a.median_edit_ratio, 0.3);
    assert.equal(c.b.approval, 5 / 6);
  });

  test('MIN_N_FOR_VERDICT is exposed so the UI states the same threshold', () => {
    assert.equal(typeof MIN_N_FOR_VERDICT, 'number');
    assert.ok(MIN_N_FOR_VERDICT >= 2);
  });
});
