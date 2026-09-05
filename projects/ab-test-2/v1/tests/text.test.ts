import { describe, expect, it } from 'vitest';

import { measureEdit, median, tokenizeWords, wordEditDistance } from '../server/text.ts';

describe('tokenizeWords', () => {
  it('splits on any whitespace and drops empties', () => {
    expect(tokenizeWords('  hello   there\n\nfriend  ')).toEqual(['hello', 'there', 'friend']);
  });

  it('returns an empty array for blank input', () => {
    expect(tokenizeWords('   \n  ')).toEqual([]);
  });
});

describe('wordEditDistance', () => {
  it('is zero for identical input', () => {
    expect(wordEditDistance(['a', 'b', 'c'], ['a', 'b', 'c'])).toBe(0);
  });

  it('counts a single substitution as one', () => {
    expect(wordEditDistance(['a', 'b', 'c'], ['a', 'x', 'c'])).toBe(1);
  });

  it('counts an insertion and a deletion as one each', () => {
    expect(wordEditDistance(['a', 'c'], ['a', 'b', 'c'])).toBe(1);
    expect(wordEditDistance(['a', 'b', 'c'], ['a', 'c'])).toBe(1);
  });

  it('falls back to length when one side is empty', () => {
    expect(wordEditDistance([], ['a', 'b'])).toBe(2);
    expect(wordEditDistance(['a', 'b', 'c'], [])).toBe(3);
  });

  it('is symmetric', () => {
    const a = 'the quick brown fox jumps'.split(' ');
    const b = 'the slow brown dog leaps over'.split(' ');
    expect(wordEditDistance(a, b)).toBe(wordEditDistance(b, a));
  });
});

describe('measureEdit', () => {
  it('reports a perfect keep ratio when the text is sent untouched', () => {
    const result = measureEdit('one two three', 'one two three');
    expect(result.distance).toBe(0);
    expect(result.keepRatio).toBe(1);
  });

  it('reports a keep ratio near zero for a full rewrite', () => {
    const result = measureEdit('alpha beta gamma delta', 'one two three four');
    expect(result.distance).toBe(4);
    expect(result.baseWords).toBe(4);
    expect(result.keepRatio).toBe(0);
  });

  it('scales with the share of words changed', () => {
    const result = measureEdit('a b c d e f g h i j', 'a b c d e f g h i X');
    expect(result.distance).toBe(1);
    expect(result.baseWords).toBe(10);
    expect(result.keepRatio).toBeCloseTo(0.9, 5);
  });

  it('never returns a negative keep ratio when the edit is longer than the original', () => {
    const result = measureEdit('short', 'a completely different and much longer reply entirely');
    expect(result.keepRatio).toBeGreaterThanOrEqual(0);
  });

  it('treats two empty strings as fully kept rather than dividing by zero', () => {
    expect(measureEdit('', '').keepRatio).toBe(1);
  });
});

describe('median', () => {
  it('returns null for an empty list', () => {
    expect(median([])).toBeNull();
  });

  it('returns the middle value for an odd count', () => {
    expect(median([3, 1, 2])).toBe(2);
  });

  it('averages the two middle values for an even count', () => {
    expect(median([1, 2, 3, 4])).toBe(2.5);
  });

  it('does not mutate the caller array', () => {
    const input = [3, 1, 2];
    median(input);
    expect(input).toEqual([3, 1, 2]);
  });
});
