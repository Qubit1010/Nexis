import { describe, expect, it } from "vitest";
import {
  computeAudit,
  computeLineExposure,
  exposureBand,
  normalizeScore,
  normalizeWeights,
} from "../src/lib/scoring";
import {
  DIMENSION_IDS,
  type DimensionId,
  type ScoreValue,
  type ServiceLine,
  type Weights,
} from "../src/lib/types";

const EQUAL_WEIGHTS: Weights = {
  output_determinism: 0.2,
  client_self_service: 0.2,
  judgment_thinness: 0.2,
  artifact_billing: 0.2,
  price_anchor_erosion: 0.2,
};

function line(
  id: string,
  revenueSharePct: number,
  scores: Partial<Record<DimensionId, ScoreValue>>
): ServiceLine {
  return {
    id,
    name: id,
    revenue_share_pct: revenueSharePct,
    deliverable_description: "",
    pricing_model: "fixed",
    typical_price: null,
    scores: Object.fromEntries(
      Object.entries(scores).map(([d, v]) => [
        d,
        { value: v as ScoreValue, reasoning: "test", provenance: "manual" as const },
      ])
    ),
    replacement: null,
    sort_order: 0,
  };
}

function allDims(value: ScoreValue): Partial<Record<DimensionId, ScoreValue>> {
  return Object.fromEntries(DIMENSION_IDS.map((d) => [d, value]));
}

describe("normalizeScore", () => {
  it("maps the 1-5 scale onto 0-1", () => {
    expect(normalizeScore(1)).toBe(0);
    expect(normalizeScore(3)).toBe(0.5);
    expect(normalizeScore(5)).toBe(1);
  });

  it("is monotonic, so a higher score never means less exposure", () => {
    for (let v = 1; v < 5; v++) {
      expect(normalizeScore(v + 1)).toBeGreaterThan(normalizeScore(v));
    }
  });
});

describe("normalizeWeights", () => {
  it("rescales arbitrary slider values to sum to 1", () => {
    const w = normalizeWeights({
      output_determinism: 2,
      client_self_service: 2,
      judgment_thinness: 2,
      artifact_billing: 2,
      price_anchor_erosion: 2,
    });
    expect(Object.values(w).reduce((a, b) => a + b, 0)).toBeCloseTo(1, 10);
    expect(w.output_determinism).toBeCloseTo(0.2, 10);
  });

  it("preserves relative emphasis", () => {
    const w = normalizeWeights({
      output_determinism: 6,
      client_self_service: 1,
      judgment_thinness: 1,
      artifact_billing: 1,
      price_anchor_erosion: 1,
    });
    expect(w.output_determinism).toBeCloseTo(0.6, 10);
    expect(w.client_self_service).toBeCloseTo(0.1, 10);
  });

  it("refuses all-zero weights rather than silently treating them as equal", () => {
    expect(() =>
      normalizeWeights({
        output_determinism: 0,
        client_self_service: 0,
        judgment_thinness: 0,
        artifact_billing: 0,
        price_anchor_erosion: 0,
      })
    ).toThrow(/sum to zero/i);
  });
});

describe("computeLineExposure", () => {
  it("scores an all-1s line at zero exposure", () => {
    const r = computeLineExposure(line("a", 100, allDims(1)), EQUAL_WEIGHTS);
    expect(r.exposure).toBe(0);
    expect(r.contribution).toBe(0);
  });

  it("scores an all-5s line at full exposure", () => {
    const r = computeLineExposure(line("a", 100, allDims(5)), EQUAL_WEIGHTS);
    expect(r.exposure).toBeCloseTo(1, 10);
    expect(r.contribution).toBeCloseTo(100, 10);
  });

  it("scores an all-3s line at exactly half", () => {
    const r = computeLineExposure(line("a", 60, allDims(3)), EQUAL_WEIGHTS);
    expect(r.exposure).toBeCloseTo(0.5, 10);
    expect(r.contribution).toBeCloseTo(30, 10);
  });

  it("returns null rather than a partial number when a dimension is unscored", () => {
    const r = computeLineExposure(
      line("a", 50, { output_determinism: 5, client_self_service: 5 }),
      EQUAL_WEIGHTS
    );
    expect(r.exposure).toBeNull();
    expect(r.contribution).toBeNull();
    expect(r.missing_dimensions).toHaveLength(3);
  });

  it("has no inverted dimension: raising any single dimension raises exposure", () => {
    const base = computeLineExposure(line("a", 100, allDims(1)), EQUAL_WEIGHTS);
    for (const d of DIMENSION_IDS) {
      const bumped = computeLineExposure(
        line("a", 100, { ...allDims(1), [d]: 5 }),
        EQUAL_WEIGHTS
      );
      expect(
        bumped.exposure as number,
        `raising ${d} must raise exposure, not lower it`
      ).toBeGreaterThan(base.exposure as number);
    }
  });

  it("responds to weights: emphasising a dimension moves the score toward it", () => {
    const l = line("a", 100, { ...allDims(1), output_determinism: 5 });
    const even = computeLineExposure(l, EQUAL_WEIGHTS);
    const emphasised = computeLineExposure(l, {
      output_determinism: 0.6,
      client_self_service: 0.1,
      judgment_thinness: 0.1,
      artifact_billing: 0.1,
      price_anchor_erosion: 0.1,
    });
    expect(emphasised.exposure as number).toBeGreaterThan(even.exposure as number);
    expect(even.exposure).toBeCloseTo(0.2, 10);
    expect(emphasised.exposure).toBeCloseTo(0.6, 10);
  });
});

describe("computeAudit", () => {
  it("produces a headline number reproducible by hand from the contributions", () => {
    const lines = [
      line("web", 65, allDims(5)), // exposure 1.0 -> contributes 65
      line("strategy", 35, allDims(1)), // exposure 0.0 -> contributes 0
    ];
    const r = computeAudit(lines, EQUAL_WEIGHTS);
    expect(r.exposed_revenue_pct).toBeCloseTo(65, 10);

    const byHand = r.lines.reduce((s, l) => s + (l.contribution as number), 0);
    expect(r.exposed_revenue_pct).toBeCloseTo(byHand, 10);
    expect(r.complete).toBe(true);
    expect(r.warnings).toHaveLength(0);
  });

  it("warns when revenue shares do not sum to 100 and does not silently rescale", () => {
    const r = computeAudit([line("web", 60, allDims(5))], EQUAL_WEIGHTS);
    expect(r.total_revenue_pct).toBe(60);
    // 60% of the book at full exposure is 60 points, not 100.
    expect(r.exposed_revenue_pct).toBeCloseTo(60, 10);
    expect(r.warnings.some((w) => /sum to 60/i.test(w))).toBe(true);
  });

  it("excludes unscored lines from the headline and says so", () => {
    const lines = [
      line("web", 50, allDims(5)),
      line("unscored", 50, { output_determinism: 4 }),
    ];
    const r = computeAudit(lines, EQUAL_WEIGHTS);
    expect(r.exposed_revenue_pct).toBeCloseTo(50, 10);
    expect(r.scored_revenue_pct).toBe(50);
    expect(r.complete).toBe(false);
    expect(r.warnings.some((w) => /not fully scored/i.test(w))).toBe(true);
  });

  it("returns null rather than zero when nothing is scored", () => {
    const r = computeAudit([line("a", 100, {})], EQUAL_WEIGHTS);
    expect(r.exposed_revenue_pct).toBeNull();
    expect(r.complete).toBe(false);
  });

  it("handles an empty audit without inventing a number", () => {
    const r = computeAudit([], EQUAL_WEIGHTS);
    expect(r.exposed_revenue_pct).toBeNull();
    expect(r.complete).toBe(false);
  });

  it("never exceeds the total book", () => {
    const lines = [line("a", 40, allDims(5)), line("b", 60, allDims(5))];
    const r = computeAudit(lines, EQUAL_WEIGHTS);
    expect(r.exposed_revenue_pct).toBeCloseTo(100, 10);
    expect(r.exposed_revenue_pct as number).toBeLessThanOrEqual(r.total_revenue_pct);
  });
});

describe("exposureBand", () => {
  it("bands across the range", () => {
    expect(exposureBand(0.1)).toBe("low");
    expect(exposureBand(0.3)).toBe("moderate");
    expect(exposureBand(0.6)).toBe("high");
    expect(exposureBand(0.9)).toBe("severe");
  });
});
