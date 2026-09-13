"use client";

import { useState } from "react";
import { exposureBand } from "@/lib/scoring";
import {
  DIMENSION_IDS,
  type Audit,
  type AuditResult,
  type DimensionId,
  type PricingModel,
  type Rubric,
  type ScoreValue,
  type ServiceLine,
} from "@/lib/types";

const PRICING_MODELS: PricingModel[] = ["hourly", "fixed", "retainer", "outcome"];

const BAND_COLOR: Record<string, string> = {
  low: "var(--color-signal-low)",
  moderate: "var(--color-signal-moderate)",
  high: "var(--color-signal-high)",
  severe: "var(--color-signal-severe)",
};

function newLine(sortOrder: number): ServiceLine {
  return {
    id: crypto.randomUUID(),
    name: "",
    revenue_share_pct: 0,
    deliverable_description: "",
    pricing_model: "fixed",
    typical_price: null,
    scores: {},
    replacement: null,
    sort_order: sortOrder,
  };
}

export default function LinesPanel({
  audit,
  rubric,
  result,
  onLinesChange,
}: {
  audit: Audit;
  rubric: Rubric;
  result: AuditResult;
  onLinesChange: (update: (prev: ServiceLine[]) => ServiceLine[]) => void;
}) {
  const [scoring, setScoring] = useState(false);
  const [scoreError, setScoreError] = useState<string | null>(null);
  const [scoreInfo, setScoreInfo] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);

  function update(id: string, patch: Partial<ServiceLine>) {
    onLinesChange((lines) => lines.map((l) => (l.id === id ? { ...l, ...patch } : l)));
  }

  function setScore(lineId: string, dim: DimensionId, value: ScoreValue) {
    onLinesChange((lines) =>
      lines.map((l) => {
        if (l.id !== lineId) return l;
        const existing = l.scores[dim];
        return {
          ...l,
          scores: {
            ...l.scores,
            [dim]: {
              value,
              reasoning: existing?.reasoning ?? "",
              // An LLM score the consultant moved is neither pure LLM nor pure manual.
              provenance:
                existing?.provenance === "llm" || existing?.provenance === "llm-adjusted"
                  ? "llm-adjusted"
                  : "manual",
            },
          },
        };
      })
    );
  }

  async function scoreAll() {
    const scorable = audit.lines.filter((l) => l.name.trim());
    if (scorable.length === 0) {
      setScoreError("Name at least one service line before scoring.");
      return;
    }
    setScoring(true);
    setScoreError(null);
    setScoreInfo(null);
    try {
      const res = await fetch("/api/score", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          business: audit.business,
          lines: scorable.map((l) => ({
            id: l.id,
            name: l.name,
            deliverable_description: l.deliverable_description,
            pricing_model: l.pricing_model,
            typical_price: l.typical_price,
            revenue_share_pct: l.revenue_share_pct,
          })),
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error([data.error, data.hint].filter(Boolean).join(" "));
      }

      const byId = new Map<string, Record<DimensionId, { value: ScoreValue; reasoning: string }>>(
        data.lines.map((l: { line_id: string; scores: Record<DimensionId, { value: ScoreValue; reasoning: string }> }) => [
          l.line_id,
          l.scores,
        ])
      );

      // Merge into current lines, not the ones captured when the request started.
      onLinesChange((lines) =>
        lines.map((l) => {
          const scored = byId.get(l.id);
          if (!scored) return l;
          const scores: ServiceLine["scores"] = {};
          for (const d of DIMENSION_IDS) {
            scores[d] = {
              value: scored[d].value,
              reasoning: scored[d].reasoning,
              provenance: "llm",
            };
          }
          return { ...l, scores };
        })
      );
      setScoreInfo(`Scored ${data.lines.length} line(s) via ${data.provider} (${data.model}). Every score is editable below.`);
    } catch (err) {
      setScoreError(err instanceof Error ? err.message : String(err));
    } finally {
      setScoring(false);
    }
  }

  const ordered = [...audit.lines].sort((a, b) => {
    const ra = result.lines.find((r) => r.line_id === a.id)?.contribution ?? -1;
    const rb = result.lines.find((r) => r.line_id === b.id)?.contribution ?? -1;
    if (ra !== rb) return rb - ra;
    return a.sort_order - b.sort_order;
  });

  return (
    <section>
      <div className="no-print mb-6 flex flex-wrap items-center justify-between gap-3">
        <p className="max-w-md text-[12px] leading-relaxed text-bone-600">
          Describe what is actually delivered, not the label. Template installs and bespoke design
          systems both get called &quot;web design&quot; and score very differently.
        </p>
        <div className="flex gap-2">
          <button
            className="btn"
            onClick={() => onLinesChange((lines) => [...lines, newLine(lines.length)])}
          >
            Add line
          </button>
          <button className="btn btn-primary" onClick={scoreAll} disabled={scoring}>
            {scoring ? "Scoring..." : "Score all with AI"}
          </button>
        </div>
      </div>

      {scoreError && (
        <div className="no-print mb-6 rounded border border-signal-severe/40 bg-signal-severe/10 px-4 py-3">
          <p className="mb-1 text-[13px] font-medium text-signal-severe">Scoring failed.</p>
          <p className="text-[12px] leading-relaxed text-bone-300">{scoreError}</p>
          <p className="mt-2 text-[12px] text-bone-500">
            Nothing was guessed or defaulted. Existing scores are untouched, and you can score by
            hand below.
          </p>
        </div>
      )}
      {scoreInfo && (
        <div className="no-print mb-6 rounded border border-ink-600 bg-ink-850 px-4 py-3">
          <p className="text-[12px] text-bone-300">{scoreInfo}</p>
        </div>
      )}

      {audit.lines.length === 0 ? (
        <div className="rounded border border-dashed border-ink-600 px-6 py-14 text-center">
          <p className="text-sm text-bone-500">No revenue lines yet.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {ordered.map((line) => {
            const r = result.lines.find((x) => x.line_id === line.id);
            const band = r?.exposure !== null && r?.exposure !== undefined ? exposureBand(r.exposure) : null;
            const isOpen = expanded === line.id;

            return (
              <article
                key={line.id}
                className="print-block rounded border border-ink-700 bg-ink-850"
              >
                <div className="flex flex-wrap items-center gap-3 px-4 py-3">
                  <input
                    className="field flex-1 min-w-[180px]"
                    placeholder="Service line name"
                    value={line.name}
                    onChange={(e) => update(line.id, { name: e.target.value })}
                  />
                  <div className="flex items-center gap-1.5">
                    <input
                      type="number"
                      min={0}
                      max={100}
                      step={0.5}
                      className="field tabular w-20 text-right"
                      value={line.revenue_share_pct}
                      onChange={(e) =>
                        update(line.id, { revenue_share_pct: Number(e.target.value) || 0 })
                      }
                      aria-label="Share of revenue"
                    />
                    <span className="tabular text-[11px] text-bone-600">% of book</span>
                  </div>

                  <div className="ml-auto flex items-center gap-4">
                    {r?.exposure !== null && r?.exposure !== undefined ? (
                      <>
                        <div className="text-right">
                          <p className="tabular text-[9px] uppercase tracking-[0.12em] text-bone-600">
                            Exposure
                          </p>
                          <p
                            className="tabular text-lg font-semibold leading-tight"
                            style={{ color: BAND_COLOR[band as string] }}
                          >
                            {(r.exposure * 100).toFixed(0)}%
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="tabular text-[9px] uppercase tracking-[0.12em] text-bone-600">
                            Contributes
                          </p>
                          <p className="tabular text-lg font-semibold leading-tight text-bone-300">
                            {(r.contribution as number).toFixed(1)}
                          </p>
                        </div>
                      </>
                    ) : (
                      <span className="tag">
                        {r?.missing_dimensions.length ?? 5} unscored
                      </span>
                    )}
                    <button
                      className="btn no-print"
                      onClick={() => setExpanded(isOpen ? null : line.id)}
                    >
                      {isOpen ? "Close" : "Score"}
                    </button>
                    <button
                      className="btn no-print"
                      onClick={() => onLinesChange((lines) => lines.filter((l) => l.id !== line.id))}
                      aria-label={`Remove ${line.name || "line"}`}
                    >
                      &times;
                    </button>
                  </div>
                </div>

                {isOpen && (
                  <div className="border-t border-ink-700 px-4 py-4">
                    <div className="mb-5 grid gap-3 sm:grid-cols-[1fr_auto_auto]">
                      <textarea
                        className="field min-h-[68px] resize-y"
                        placeholder="What is actually delivered? The more concrete, the better the scoring."
                        value={line.deliverable_description}
                        onChange={(e) =>
                          update(line.id, { deliverable_description: e.target.value })
                        }
                      />
                      <select
                        className="field h-fit w-32"
                        value={line.pricing_model}
                        onChange={(e) =>
                          update(line.id, { pricing_model: e.target.value as PricingModel })
                        }
                        aria-label="Pricing model"
                      >
                        {PRICING_MODELS.map((m) => (
                          <option key={m} value={m}>
                            {m}
                          </option>
                        ))}
                      </select>
                      <input
                        type="number"
                        min={0}
                        className="field tabular h-fit w-32"
                        placeholder="Typical price"
                        value={line.typical_price ?? ""}
                        onChange={(e) =>
                          update(line.id, {
                            typical_price: e.target.value === "" ? null : Number(e.target.value),
                          })
                        }
                        aria-label="Typical price"
                      />
                    </div>

                    <div className="space-y-4">
                      {rubric.dimensions.map((d) => {
                        const s = line.scores[d.id];
                        return (
                          <div key={d.id} className="border-t border-ink-700 pt-3.5">
                            <div className="mb-2 flex flex-wrap items-center gap-2.5">
                              <span className="text-[13px] font-medium text-bone-100">
                                {d.name}
                              </span>
                              <span className={`tag tag-${d.evidence_tier}`}>
                                {d.evidence_tier}
                              </span>
                              {s && <span className="tag">{s.provenance}</span>}
                              <span className="ml-auto flex gap-1">
                                {([1, 2, 3, 4, 5] as ScoreValue[]).map((v) => (
                                  <button
                                    key={v}
                                    onClick={() => setScore(line.id, d.id, v)}
                                    title={d.anchors[String(v)]}
                                    className="tabular h-7 w-7 rounded border text-[12px] transition-colors"
                                    style={{
                                      borderColor:
                                        s?.value === v
                                          ? "var(--color-ember-500)"
                                          : "var(--color-ink-600)",
                                      background:
                                        s?.value === v ? "var(--color-ember-600)" : "transparent",
                                      color:
                                        s?.value === v ? "#fff" : "var(--color-bone-500)",
                                    }}
                                  >
                                    {v}
                                  </button>
                                ))}
                              </span>
                            </div>
                            <p className="mb-2 text-[12px] leading-relaxed text-bone-600">
                              {s ? d.anchors[String(s.value)] : d.question}
                            </p>
                            <textarea
                              className="field min-h-[52px] resize-y text-[12px]"
                              placeholder="Why this score? A number with no justification is not usable in the report."
                              value={s?.reasoning ?? ""}
                              onChange={(e) => {
                                if (!s) return;
                                onLinesChange((lines) =>
                                  lines.map((l) =>
                                    l.id === line.id
                                      ? {
                                          ...l,
                                          scores: {
                                            ...l.scores,
                                            [d.id]: { ...s, reasoning: e.target.value },
                                          },
                                        }
                                      : l
                                  )
                                );
                              }}
                              disabled={!s}
                            />
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
