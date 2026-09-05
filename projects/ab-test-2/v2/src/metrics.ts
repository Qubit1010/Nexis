/**
 * The measurement layer.
 *
 * Everything here exists to answer one question honestly: is the drafting getting better
 * or worse as the prompt changes? The hard part is not computing a percentage, it is
 * refusing to report one when the number cannot support the claim.
 */

/** Minimum reviews on BOTH sides before a head-to-head will name a winner. */
export const MIN_N_FOR_VERDICT = 5;

/** z for a two-sided 95% interval. */
const Z95 = 1.959963984540054;

// --------------------------------------------------------------------------------------
// Edit distance
// --------------------------------------------------------------------------------------

/** Split into comparable word tokens. Case-folded so capitalisation is not an "edit". */
export function tokenize(text: string): string[] {
  return text.toLowerCase().split(/\s+/).filter((w) => w.length > 0);
}

/** Word-level Levenshtein distance, two-row rolling implementation. */
export function levenshtein(a: string[], b: string[]): number {
  if (a.length === 0) return b.length;
  if (b.length === 0) return a.length;

  let prev = new Array<number>(b.length + 1);
  let curr = new Array<number>(b.length + 1);
  for (let j = 0; j <= b.length; j++) prev[j] = j;

  for (let i = 1; i <= a.length; i++) {
    curr[0] = i;
    for (let j = 1; j <= b.length; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      curr[j] = Math.min(curr[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost);
    }
    const swap = prev;
    prev = curr;
    curr = swap;
  }
  return prev[b.length];
}

/**
 * How much of the draft the user rewrote, 0..1.
 *
 * 0.0 = kept verbatim. 1.0 = nothing of the draft survived. This is the revealed-preference
 * signal: it costs the user nothing to produce and it is far harder to fool yourself with
 * than a thumbs-up, because it is a record of what you actually did rather than what you
 * said you thought.
 */
export function editRatio(draft: string, final: string): number {
  const a = tokenize(draft);
  const b = tokenize(final);
  if (a.length === 0 && b.length === 0) return 0;
  const denom = Math.max(a.length, b.length);
  return clamp01(levenshtein(a, b) / denom);
}

function clamp01(n: number): number {
  return Math.min(1, Math.max(0, n));
}

// --------------------------------------------------------------------------------------
// Proportions
// --------------------------------------------------------------------------------------

export type Interval = { low: number; high: number };

/**
 * Wilson score interval for a binomial proportion.
 *
 * Used instead of the normal approximation because at the sample sizes this tool actually
 * sees (n = 5..30) the normal approximation is badly wrong near 0 and 1, and would happily
 * report a confidence bound below 0% or above 100%.
 */
export function wilson(successes: number, n: number, z: number = Z95): Interval {
  if (n <= 0) return { low: 0, high: 1 };
  const p = successes / n;
  const z2 = z * z;
  const denom = 1 + z2 / n;
  const center = (p + z2 / (2 * n)) / denom;
  const half = (z / denom) * Math.sqrt((p * (1 - p)) / n + z2 / (4 * n * n));
  return { low: clamp01(center - half), high: clamp01(center + half) };
}

export function median(values: number[]): number | null {
  if (values.length === 0) return null;
  const s = [...values].sort((x, y) => x - y);
  const mid = Math.floor(s.length / 2);
  return s.length % 2 === 0 ? (s[mid - 1] + s[mid]) / 2 : s[mid];
}

// --------------------------------------------------------------------------------------
// Head-to-head
// --------------------------------------------------------------------------------------

export type VerdictLabel = 'better' | 'worse' | 'no detectable difference' | 'not enough data';

export type Comparison = {
  verdict: VerdictLabel;
  reason: string;
  a: { n: number; approval: number | null; interval: Interval; median_edit_ratio: number | null };
  b: { n: number; approval: number | null; interval: Interval; median_edit_ratio: number | null };
};

export type SideInput = {
  good: number;
  n: number;
  edit_ratios: number[];
};

/**
 * Compare version B against baseline A.
 *
 * Deliberately conservative. It declares a difference only when the two Wilson intervals
 * do not overlap, which is a stricter bar than a bare difference in point estimates and
 * roughly comparable to a two-proportion test at this scale. Below MIN_N_FOR_VERDICT on
 * either side it declines outright rather than rendering a number that looks like a result.
 */
export function compare(a: SideInput, b: SideInput): Comparison {
  const aStats = side(a);
  const bStats = side(b);

  if (a.n < MIN_N_FOR_VERDICT || b.n < MIN_N_FOR_VERDICT) {
    const short = [
      a.n < MIN_N_FOR_VERDICT ? `baseline has ${a.n}` : null,
      b.n < MIN_N_FOR_VERDICT ? `candidate has ${b.n}` : null,
    ].filter(Boolean).join(' and ');
    return {
      verdict: 'not enough data',
      reason: `Needs at least ${MIN_N_FOR_VERDICT} reviewed drafts on each side; ${short}. Rate more drafts, or run the bench.`,
      a: aStats,
      b: bStats,
    };
  }

  if (bStats.interval.low > aStats.interval.high) {
    return {
      verdict: 'better',
      reason: `Candidate approval interval (${pct(bStats.interval.low)}-${pct(bStats.interval.high)}) sits entirely above the baseline's (${pct(aStats.interval.low)}-${pct(aStats.interval.high)}).`,
      a: aStats,
      b: bStats,
    };
  }

  if (bStats.interval.high < aStats.interval.low) {
    return {
      verdict: 'worse',
      reason: `Candidate approval interval (${pct(bStats.interval.low)}-${pct(bStats.interval.high)}) sits entirely below the baseline's (${pct(aStats.interval.low)}-${pct(aStats.interval.high)}).`,
      a: aStats,
      b: bStats,
    };
  }

  return {
    verdict: 'no detectable difference',
    reason: `The 95% approval intervals overlap, so the gap between ${pct(aStats.approval ?? 0)} and ${pct(bStats.approval ?? 0)} is within noise at n=${a.n} and n=${b.n}. Collect more reviews before acting on it.`,
    a: aStats,
    b: bStats,
  };
}

function side(s: SideInput) {
  return {
    n: s.n,
    approval: s.n > 0 ? s.good / s.n : null,
    interval: wilson(s.good, s.n),
    median_edit_ratio: median(s.edit_ratios),
  };
}

function pct(n: number): string {
  return `${Math.round(n * 100)}%`;
}
