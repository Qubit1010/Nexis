/**
 * Word-level edit distance between what the model wrote and what the user sent.
 *
 * This is the second quality signal, and the only one that costs the user nothing to
 * produce. A thumbs-up is one bit; "you rewrote 40% of the words" is denser and arrives
 * whether or not they remember to click anything.
 *
 * Word-level rather than character-level on purpose: drafts are a few hundred words, so
 * the DP stays small, and "words changed" is a number a human can reason about.
 */

export function tokenizeWords(text: string): string[] {
  return text
    .trim()
    .split(/\s+/)
    .filter((w) => w.length > 0);
}

/** Levenshtein distance over word arrays, two-row DP. */
export function wordEditDistance(a: string[], b: string[]): number {
  if (a.length === 0) return b.length;
  if (b.length === 0) return a.length;

  let previous = new Array<number>(b.length + 1);
  let current = new Array<number>(b.length + 1);

  for (let j = 0; j <= b.length; j += 1) previous[j] = j;

  for (let i = 1; i <= a.length; i += 1) {
    current[0] = i;
    for (let j = 1; j <= b.length; j += 1) {
      const substitution = (previous[j - 1] as number) + (a[i - 1] === b[j - 1] ? 0 : 1);
      const deletion = (previous[j] as number) + 1;
      const insertion = (current[j - 1] as number) + 1;
      current[j] = Math.min(substitution, deletion, insertion);
    }
    const swap = previous;
    previous = current;
    current = swap;
  }

  return previous[b.length] as number;
}

export type EditMeasure = {
  /** Words changed between the generated draft and the user's edited version. */
  distance: number;
  /** Denominator: the longer of the two word counts. */
  baseWords: number;
  /** 1.0 = sent untouched, 0.0 = rewritten from nothing. */
  keepRatio: number;
};

export function measureEdit(generated: string, edited: string): EditMeasure {
  const a = tokenizeWords(generated);
  const b = tokenizeWords(edited);
  const baseWords = Math.max(a.length, b.length);
  const distance = wordEditDistance(a, b);
  const keepRatio = baseWords === 0 ? 1 : Math.max(0, 1 - distance / baseWords);
  return { distance, baseWords, keepRatio };
}

export function median(values: number[]): number | null {
  if (values.length === 0) return null;
  const sorted = [...values].sort((x, y) => x - y);
  const mid = Math.floor(sorted.length / 2);
  if (sorted.length % 2 === 1) return sorted[mid] as number;
  return ((sorted[mid - 1] as number) + (sorted[mid] as number)) / 2;
}
