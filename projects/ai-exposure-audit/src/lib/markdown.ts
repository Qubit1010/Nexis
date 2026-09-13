import { computeAudit, exposureBand } from "./scoring";
import type { Audit, PriceBook, Rubric, Source } from "./types";

/**
 * The deliverable. A repriced service menu, not a slide deck.
 *
 * Markdown rather than PDF so it feeds the pandoc and Google Docs pipelines that
 * already exist in Nexis, and so the consultant can edit it before it goes out.
 *
 * Rule enforced throughout: no number appears without either an evidence tier and a
 * source, or an explicit statement that it is judgment.
 */
export function renderAuditMarkdown(
  audit: Audit,
  rubric: Rubric,
  pricebook: PriceBook,
  sources: Record<string, Source>
): string {
  const result = computeAudit(audit.lines, audit.weights);
  const out: string[] = [];

  const cite = (ids: string[]) =>
    ids
      .map((id) => {
        const s = sources[id];
        return s ? `[${s.publisher}](${s.url})` : `UNRESOLVED SOURCE (${id})`;
      })
      .join(", ");

  out.push(`# AI Exposure Audit: ${audit.business.name}`);
  out.push("");
  out.push(
    `Generated ${new Date().toISOString().slice(0, 10)} | Rubric v${audit.rubric_version} | Price book v${audit.pricebook_version}`
  );
  out.push("");

  /* ---- headline ---- */
  out.push("## The number");
  out.push("");
  if (result.exposed_revenue_pct === null) {
    out.push(
      "**Not calculable.** No service line is fully scored, so there is no exposed-revenue figure. Nothing has been estimated in its place."
    );
  } else {
    out.push(
      `**${result.exposed_revenue_pct.toFixed(1)}% of revenue sits in service lines exposed to AI substitution.**`
    );
    out.push("");
    out.push(
      `This is the sum of each line's revenue share multiplied by its exposure score. The per-line arithmetic is below, so the figure can be checked by hand.`
    );
    out.push("");
    out.push(
      `It speaks for ${result.scored_revenue_pct.toFixed(1)} of the ${result.total_revenue_pct.toFixed(1)} percentage points of revenue entered.`
    );
  }
  out.push("");

  if (result.warnings.length > 0) {
    out.push("> **Read this before quoting the number above.**");
    for (const w of result.warnings) out.push(`> - ${w}`);
    out.push("");
  }

  /* ---- how it was measured ---- */
  out.push("## How this was measured");
  out.push("");
  out.push(
    `Each service line is scored 1-5 on five dimensions. Every dimension is oriented so 5 means maximum exposure. A score is normalised as \`(score - 1) / 4\`, weighted, and summed.`
  );
  out.push("");
  out.push("| Dimension | Weight | Evidence | Sources |");
  out.push("|---|---|---|---|");
  const weightTotal = Object.values(audit.weights).reduce((a, b) => a + b, 0);
  for (const d of rubric.dimensions) {
    const w = ((audit.weights[d.id] ?? 0) / weightTotal) * 100;
    out.push(
      `| **${d.name}** | ${w.toFixed(0)}% | \`${d.evidence_tier}\` | ${cite(d.sources)} |`
    );
  }
  out.push("");
  out.push(`**On the weights.** ${rubric.weights_disclaimer}`);
  out.push("");

  /* ---- the ledger ---- */
  out.push("## Exposure by revenue line");
  out.push("");
  out.push("| Service line | Share of book | Exposure | Contribution | Band |");
  out.push("|---|---|---|---|---|");
  const ordered = [...audit.lines].sort((a, b) => {
    const ra = result.lines.find((r) => r.line_id === a.id)?.contribution ?? -1;
    const rb = result.lines.find((r) => r.line_id === b.id)?.contribution ?? -1;
    return rb - ra;
  });
  for (const line of ordered) {
    const r = result.lines.find((x) => x.line_id === line.id);
    if (!r || r.exposure === null) {
      out.push(
        `| ${line.name} | ${line.revenue_share_pct}% | not scored | not scored | not scored |`
      );
      continue;
    }
    out.push(
      `| ${line.name} | ${line.revenue_share_pct}% | ${(r.exposure * 100).toFixed(0)}% | ${(r.contribution as number).toFixed(1)} pts | ${exposureBand(r.exposure)} |`
    );
  }
  out.push("");
  out.push(
    "Contribution is the share of the whole book this line puts at risk: revenue share multiplied by exposure. The contributions sum to the headline number."
  );
  out.push("");

  /* ---- per-line detail ---- */
  out.push("## Line by line");
  out.push("");
  for (const line of ordered) {
    const r = result.lines.find((x) => x.line_id === line.id);
    out.push(`### ${line.name}`);
    out.push("");
    out.push(
      `${line.revenue_share_pct}% of revenue | priced ${line.pricing_model}${
        line.typical_price ? ` at about ${line.typical_price}` : ""
      }`
    );
    out.push("");
    if (line.deliverable_description) {
      out.push(`_${line.deliverable_description}_`);
      out.push("");
    }
    if (!r || r.exposure === null) {
      out.push(
        `**Not scored.** ${r?.missing_dimensions.length ?? 5} dimension(s) have no score, so no exposure figure is given for this line.`
      );
      out.push("");
      continue;
    }
    out.push("| Dimension | Score | Source of score | Reasoning |");
    out.push("|---|---|---|---|");
    for (const d of rubric.dimensions) {
      const s = line.scores[d.id];
      if (!s) continue;
      out.push(
        `| ${d.name} | **${s.value}/5** | \`${s.provenance}\` | ${s.reasoning.replace(/\|/g, "\\|")} |`
      );
    }
    out.push("");

    if (line.replacement) {
      const arch = pricebook.archetypes.find((a) => a.id === line.replacement?.archetype_id);
      if (arch) {
        const anchor = arch.anchor_ref
          ? pricebook.anchors.find((a) => a.id === arch.anchor_ref)
          : null;
        out.push(`**Move to: ${arch.name}.** ${arch.what_changes}`);
        out.push("");
        if (anchor) {
          out.push(
            `Price anchor: **${anchor.display}** \`${anchor.evidence_tier}\` (${cite(anchor.sources)})`
          );
        } else {
          out.push(
            `Price anchor: **none exists in the research.** ${arch.evidence_note} Price this from your own book, not from this document.`
          );
        }
        out.push("");
        if (line.replacement.rationale) {
          out.push(line.replacement.rationale);
          out.push("");
        }
      }
    }
  }

  /* ---- repriced menu ---- */
  const repriced = audit.lines.filter((l) => l.replacement);
  if (repriced.length > 0) {
    out.push("## Repriced service menu");
    out.push("");
    out.push(`> **${pricebook.global_caveat}**`);
    out.push("");
    out.push("| Line | Priced today | Move to | New anchor |");
    out.push("|---|---|---|---|");
    for (const line of repriced) {
      const arch = pricebook.archetypes.find((a) => a.id === line.replacement?.archetype_id);
      const anchor = arch?.anchor_ref
        ? pricebook.anchors.find((a) => a.id === arch.anchor_ref)
        : null;
      out.push(
        `| ${line.name} | ${line.pricing_model}${
          line.typical_price ? `, about ${line.typical_price}` : ""
        } | ${arch?.name ?? "not mapped"} | ${anchor ? anchor.display : "no documented anchor"} |`
      );
    }
    out.push("");
  }

  /* ---- honesty section ---- */
  out.push("## What this audit does not know");
  out.push("");
  out.push(
    "- **No source anywhere gives a numeric AI-substitution risk for a named service line.** The scores here are structured judgment against a sourced rubric, not a measurement. They are reproducible and arguable, which is the point, but they are not data."
  );
  out.push(
    "- **The dimension weights are judgment.** No study establishes how much each dimension contributes to substitution risk. Change them and the headline number changes."
  );
  out.push(
    `- **The entire price book traces to one source.** ${pricebook.global_caveat}`
  );
  out.push(
    "- Market-level figures are real and cited. Applying them to this specific business is inference."
  );
  out.push("");

  /* ---- sources ---- */
  out.push("## Sources");
  out.push("");
  const used = new Set<string>();
  for (const d of rubric.dimensions) d.sources.forEach((s) => used.add(s));
  for (const a of pricebook.anchors) a.sources.forEach((s) => used.add(s));
  for (const a of pricebook.archetypes) a.sources.forEach((s) => used.add(s));
  for (const id of [...used].sort()) {
    const s = sources[id];
    if (!s) {
      out.push(`- \`${id}\` UNRESOLVED. Any claim resting on this is unsourced.`);
      continue;
    }
    out.push(
      `- **${s.publisher}**, [${s.title}](${s.url}) (${s.kind})${s.caveat ? ` **${s.caveat}**` : ""}`
    );
  }
  out.push("");

  return out.join("\n");
}
