/**
 * The measurement layer. This is the part of the app that answers the actual question:
 * "is the drafting getting better or worse as I change the prompt?"
 *
 * The answer is only meaningful because prompt versions are immutable, so every rating is
 * permanently attached to the exact prompt text that produced the draft it rated.
 */

import type { Db } from './db.ts';
import { estimateCostUsd } from './pricing.ts';
import { median } from './text.ts';

/** Below this many ratings a version is reported as inconclusive, not as a score. */
export const MIN_SAMPLE = 5;

/** 95% two-sided normal quantile. */
const Z = 1.959963984540054;

export type Interval = { low: number; high: number };

/**
 * Wilson score interval for a binomial proportion.
 *
 * Used instead of a bare good-rate because a bare rate lies at small n: 1 good out of 1 is
 * not a 100% prompt, and the naive interval (Wald) is degenerate exactly there, returning a
 * width of zero. Wilson stays sane at the edges, which is where this app spends most of its
 * life. The UI draws this as a whisker so a thin sample visibly looks thin.
 */
export function wilsonInterval(successes: number, trials: number): Interval | null {
  if (trials <= 0) return null;
  const p = successes / trials;
  const z2 = Z * Z;
  const denominator = 1 + z2 / trials;
  const center = (p + z2 / (2 * trials)) / denominator;
  const margin =
    (Z / denominator) * Math.sqrt((p * (1 - p)) / trials + z2 / (4 * trials * trials));
  return {
    low: Math.max(0, center - margin),
    high: Math.min(1, center + margin),
  };
}

export type VersionStat = {
  promptVersionId: number;
  version: number;
  label: string;
  createdAt: string;
  isActive: boolean;
  drafts: number;
  rated: number;
  good: number;
  bad: number;
  goodRate: number | null;
  wilsonLow: number | null;
  wilsonHigh: number | null;
  enoughData: boolean;
  editedCount: number;
  medianKeepRatio: number | null;
  avgLatencyMs: number | null;
  totalCostUsd: number | null;
};

export type Totals = {
  enquiries: number;
  drafts: number;
  rated: number;
  versions: number;
  minSample: number;
};

export type Scoreboard = {
  versions: VersionStat[];
  totals: Totals;
};

type AggRow = {
  id: number;
  version: number;
  label: string;
  created_at: string;
  is_active: number;
  drafts: number;
  rated: number;
  good: number;
  bad: number;
  edited_count: number;
  avg_latency: number | null;
  input_tokens: number | null;
  output_tokens: number | null;
};

export function buildScoreboard(db: Db): Scoreboard {
  const rows = db
    .prepare(
      `SELECT pv.id, pv.version, pv.label, pv.created_at, pv.is_active,
              COUNT(d.id)                                            AS drafts,
              COALESCE(SUM(CASE WHEN d.rating IS NOT NULL THEN 1 ELSE 0 END), 0) AS rated,
              COALESCE(SUM(CASE WHEN d.rating = 'good'   THEN 1 ELSE 0 END), 0) AS good,
              COALESCE(SUM(CASE WHEN d.rating = 'bad'    THEN 1 ELSE 0 END), 0) AS bad,
              COALESCE(SUM(CASE WHEN d.edited_text IS NOT NULL THEN 1 ELSE 0 END), 0) AS edited_count,
              AVG(d.latency_ms)                                      AS avg_latency,
              SUM(d.input_tokens)                                    AS input_tokens,
              SUM(d.output_tokens)                                   AS output_tokens
       FROM prompt_versions pv
       LEFT JOIN drafts d ON d.prompt_version_id = pv.id
       GROUP BY pv.id
       ORDER BY pv.version DESC`,
    )
    .all() as AggRow[];

  const keepRatioRows = db
    .prepare(
      `SELECT prompt_version_id, edit_distance, edit_base_words
       FROM drafts
       WHERE edited_text IS NOT NULL AND edit_base_words IS NOT NULL AND edit_base_words > 0`,
    )
    .all() as Array<{ prompt_version_id: number; edit_distance: number; edit_base_words: number }>;

  const keepRatiosByVersion = new Map<number, number[]>();
  for (const row of keepRatioRows) {
    const ratio = Math.max(0, 1 - row.edit_distance / row.edit_base_words);
    const list = keepRatiosByVersion.get(row.prompt_version_id);
    if (list) list.push(ratio);
    else keepRatiosByVersion.set(row.prompt_version_id, [ratio]);
  }

  const versions: VersionStat[] = rows.map((row) => {
    const interval = wilsonInterval(row.good, row.rated);
    return {
      promptVersionId: row.id,
      version: row.version,
      label: row.label,
      createdAt: row.created_at,
      isActive: row.is_active === 1,
      drafts: row.drafts,
      rated: row.rated,
      good: row.good,
      bad: row.bad,
      goodRate: row.rated > 0 ? row.good / row.rated : null,
      wilsonLow: interval ? interval.low : null,
      wilsonHigh: interval ? interval.high : null,
      enoughData: row.rated >= MIN_SAMPLE,
      editedCount: row.edited_count,
      medianKeepRatio: median(keepRatiosByVersion.get(row.id) ?? []),
      avgLatencyMs: row.avg_latency === null ? null : Math.round(row.avg_latency),
      totalCostUsd: estimateCostUsd(row.input_tokens, row.output_tokens),
    };
  });

  const totalsRow = db
    .prepare(
      `SELECT (SELECT COUNT(*) FROM enquiries)                            AS enquiries,
              (SELECT COUNT(*) FROM drafts)                               AS drafts,
              (SELECT COUNT(*) FROM drafts WHERE rating IS NOT NULL)      AS rated,
              (SELECT COUNT(*) FROM prompt_versions)                      AS versions`,
    )
    .get() as { enquiries: number; drafts: number; rated: number; versions: number };

  return {
    versions,
    totals: { ...totalsRow, minSample: MIN_SAMPLE },
  };
}
