import { describe, expect, it } from "vitest";
import fs from "node:fs";
import path from "node:path";
import { computeAudit } from "../src/lib/scoring";
import { renderAuditMarkdown } from "../src/lib/markdown";
import type { Audit, PriceBook, Rubric, SourceRegistry } from "../src/lib/types";

/**
 * Runs a full audit through the real renderer. Guards the two claims the deliverable makes
 * about itself: the headline is reproducible by hand, and no number escapes without a tier
 * flag.
 *
 * The fixture is a fictional agency. Nexis is a public repo, so real client revenue splits
 * never land in a tracked file.
 */
const FIXTURE = path.join(__dirname, "fixtures", "sample-audit.json");
const RUBRIC_DIR = path.join(process.cwd(), "rubric");

const audit = JSON.parse(fs.readFileSync(FIXTURE, "utf-8")) as Audit;
const rubric = JSON.parse(fs.readFileSync(path.join(RUBRIC_DIR, "rubric.v1.json"), "utf-8")) as Rubric;
const pricebook = JSON.parse(
  fs.readFileSync(path.join(RUBRIC_DIR, "pricebook.v1.json"), "utf-8")
) as PriceBook;
const sources = (
  JSON.parse(fs.readFileSync(path.join(RUBRIC_DIR, "sources.json"), "utf-8")) as SourceRegistry
).sources;

describe("Sample audit end to end", () => {
  const result = computeAudit(audit.lines, audit.weights);

  it("is fully scored with shares summing to 100", () => {
    expect(result.complete).toBe(true);
    expect(result.total_revenue_pct).toBeCloseTo(100, 6);
    expect(result.warnings).toHaveLength(0);
  });

  it("headline equals the sum of the per-line contributions", () => {
    const byHand = result.lines.reduce((s, l) => s + (l.contribution as number), 0);
    expect(result.exposed_revenue_pct).toBeCloseTo(byHand, 10);
  });

  it("reproduces the headline from raw scores with no library help", () => {
    let total = 0;
    for (const line of audit.lines) {
      const values = Object.values(line.scores).map((s) => s!.value);
      expect(values).toHaveLength(5);
      const exposure = values.reduce((acc, v) => acc + 0.2 * ((v - 1) / 4), 0);
      total += line.revenue_share_pct * exposure;
    }
    expect(result.exposed_revenue_pct).toBeCloseTo(total, 8);
  });

  it("ranks the most templatable line highest on exposure", () => {
    const cms = audit.lines.find((l) => l.name === "CMS builds and migrations")!;
    const saas = audit.lines.find((l) => l.name === "Custom application builds")!;
    const cmsExp = result.lines.find((r) => r.line_id === cms.id)!.exposure as number;
    const saasExp = result.lines.find((r) => r.line_id === saas.id)!.exposure as number;
    expect(cmsExp).toBeGreaterThan(saasExp);
  });

  it("moves the headline when a weight changes", () => {
    const skewed = computeAudit(audit.lines, {
      output_determinism: 1,
      client_self_service: 0,
      judgment_thinness: 0,
      artifact_billing: 0,
      price_anchor_erosion: 0,
    });
    expect(skewed.exposed_revenue_pct).not.toBeCloseTo(
      result.exposed_revenue_pct as number,
      2
    );
  });

  describe("the rendered deliverable", () => {
    const md = renderAuditMarkdown(audit, rubric, pricebook, sources);

    it("leads with the exposed revenue figure", () => {
      expect(md).toContain(`${(result.exposed_revenue_pct as number).toFixed(1)}% of revenue`);
    });

    it("states what it does not know", () => {
      expect(md).toContain("What this audit does not know");
      expect(md).toMatch(/No source anywhere gives a numeric AI-substitution risk/);
      expect(md).toMatch(/weights are judgment/i);
    });

    it("carries the single-source caveat on the price book", () => {
      expect(md).toContain("single agency blog post");
    });

    it("gives every dimension an evidence tier", () => {
      for (const d of rubric.dimensions) {
        expect(md).toContain(`**${d.name}**`);
      }
      expect(md).toMatch(/`documented`/);
      expect(md).toMatch(/`practitioner`/);
    });

    it("labels the provenance of every score it prints", () => {
      const scoreRows = md.split("\n").filter((l) => /\*\*\d\/5\*\*/.test(l));
      expect(scoreRows.length).toBeGreaterThan(0);
      for (const row of scoreRows) {
        expect(row, `score row without provenance: ${row}`).toMatch(
          /`(llm|llm-adjusted|manual)`/
        );
      }
    });

    it("resolves every citation it emits", () => {
      expect(md).not.toContain("UNRESOLVED");
      expect(md).not.toContain("UNKNOWN SOURCE");
    });
  });
});
