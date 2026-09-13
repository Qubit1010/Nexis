import {
  type AuditResult,
  type DimensionId,
  type LineExposure,
  type ServiceLine,
  type Weights,
  DIMENSION_IDS,
} from "./types";

/**
 * The whole model, in one place.
 *
 *   n_d       = (score_d - 1) / 4          -> [0,1]
 *   exposure  = sum(weight_d * n_d)        -> [0,1]
 *   exposed % = sum(revenue_share * exposure)
 *
 * Every dimension is oriented so 5 = maximum exposure, so there is no inversion
 * anywhere. If a dimension ever needs inverting, fix its name and its anchors in
 * the rubric instead of adding a sign flip here.
 */

/** Maps a 1-5 score onto [0,1]. A 1 contributes nothing; a 5 contributes fully. */
export function normalizeScore(value: number): number {
  return (value - 1) / 4;
}

/**
 * Weights are user-editable, so they arrive arbitrary. Normalize to sum 1 so the
 * exposure stays on [0,1] whatever the sliders say. All-zero weights are refused
 * rather than silently treated as equal.
 */
export function normalizeWeights(weights: Weights): Weights {
  const total = DIMENSION_IDS.reduce((sum, d) => sum + (weights[d] ?? 0), 0);
  if (total <= 0) {
    throw new Error(
      "Weights sum to zero. At least one dimension must carry weight for an exposure score to mean anything."
    );
  }
  const out = {} as Weights;
  for (const d of DIMENSION_IDS) {
    out[d] = (weights[d] ?? 0) / total;
  }
  return out;
}

/**
 * Exposure for one line. Returns null when any dimension is unscored: a partial
 * exposure number is worse than no number, because it looks like a measurement.
 */
export function computeLineExposure(line: ServiceLine, weights: Weights): LineExposure {
  const normalizedWeights = normalizeWeights(weights);
  const missing: DimensionId[] = [];
  const normalized: Partial<Record<DimensionId, number>> = {};

  for (const d of DIMENSION_IDS) {
    const score = line.scores[d];
    if (!score) {
      missing.push(d);
      continue;
    }
    normalized[d] = normalizeScore(score.value);
  }

  if (missing.length > 0) {
    return {
      line_id: line.id,
      exposure: null,
      contribution: null,
      missing_dimensions: missing,
      normalized,
    };
  }

  const exposure = DIMENSION_IDS.reduce(
    (sum, d) => sum + normalizedWeights[d] * (normalized[d] as number),
    0
  );

  return {
    line_id: line.id,
    exposure,
    contribution: (line.revenue_share_pct / 100) * exposure * 100,
    missing_dimensions: [],
    normalized,
  };
}

/**
 * Roll the lines up into the headline number.
 *
 * Deliberately does NOT rescale revenue shares that fail to sum to 100. Silently
 * normalizing would hide a data-entry error behind a confident number, which is
 * the exact failure this product exists to avoid. It warns instead.
 */
export function computeAudit(lines: ServiceLine[], weights: Weights): AuditResult {
  const warnings: string[] = [];
  const lineResults = lines.map((line) => computeLineExposure(line, weights));

  const totalRevenuePct = lines.reduce((sum, l) => sum + l.revenue_share_pct, 0);
  if (lines.length > 0 && Math.abs(totalRevenuePct - 100) > 0.5) {
    warnings.push(
      `Revenue shares sum to ${totalRevenuePct.toFixed(1)}%, not 100%. The exposed-revenue figure is stated against the book as entered and is not rescaled.`
    );
  }

  const scoredLines = lineResults.filter((r) => r.exposure !== null);
  const unscoredCount = lineResults.length - scoredLines.length;
  if (unscoredCount > 0) {
    warnings.push(
      `${unscoredCount} of ${lineResults.length} lines are not fully scored and are excluded from the headline number.`
    );
  }

  const scoredRevenuePct = lines
    .filter((l) => {
      const r = lineResults.find((x) => x.line_id === l.id);
      return r?.exposure !== null && r !== undefined;
    })
    .reduce((sum, l) => sum + l.revenue_share_pct, 0);

  const exposedRevenuePct =
    scoredLines.length > 0
      ? scoredLines.reduce((sum, r) => sum + (r.contribution as number), 0)
      : null;

  return {
    lines: lineResults,
    exposed_revenue_pct: exposedRevenuePct,
    scored_revenue_pct: scoredRevenuePct,
    total_revenue_pct: totalRevenuePct,
    warnings,
    complete: lines.length > 0 && unscoredCount === 0,
  };
}

/** Bands used for wording, not for maths. Judgment, and labelled as such in the UI. */
export function exposureBand(exposure: number): "low" | "moderate" | "high" | "severe" {
  if (exposure < 0.25) return "low";
  if (exposure < 0.5) return "moderate";
  if (exposure < 0.75) return "high";
  return "severe";
}
