"use client";

import { DIMENSION_IDS, type Rubric, type Source, type Weights } from "@/lib/types";

/**
 * The weights are the least defensible part of the model, so they are the most
 * visible. Nothing here is hidden behind a "recommended" default the client cannot see.
 */
export default function WeightsPanel({
  rubric,
  weights,
  sources,
  onChange,
}: {
  rubric: Rubric;
  weights: Weights;
  sources: Record<string, Source>;
  onChange: (w: Weights) => void;
}) {
  const total = DIMENSION_IDS.reduce((s, d) => s + (weights[d] ?? 0), 0);

  return (
    <section className="max-w-3xl">
      <div className="mb-8 rounded border border-signal-moderate/30 bg-signal-moderate/5 px-5 py-4">
        <div className="mb-2 flex items-center gap-2.5">
          <span className="tag tag-judgment">judgment</span>
          <span className="text-[13px] font-medium text-bone-100">
            These weights are not a measured finding.
          </span>
        </div>
        <p className="text-[12.5px] leading-relaxed text-bone-300">{rubric.weights_disclaimer}</p>
      </div>

      <div className="space-y-7">
        {rubric.dimensions.map((d) => {
          const raw = weights[d.id] ?? 0;
          const share = total > 0 ? (raw / total) * 100 : 0;
          return (
            <div key={d.id}>
              <div className="mb-2 flex flex-wrap items-baseline gap-2.5">
                <span className="text-[14px] font-medium text-bone-100">{d.name}</span>
                <span className={`tag tag-${d.evidence_tier}`}>{d.evidence_tier}</span>
                <span className="tabular ml-auto text-lg font-semibold text-ember-300">
                  {share.toFixed(0)}%
                </span>
              </div>
              <input
                type="range"
                min={0}
                max={1}
                step={0.01}
                value={raw}
                onChange={(e) => onChange({ ...weights, [d.id]: Number(e.target.value) })}
                className="mb-2.5 w-full"
                aria-label={`${d.name} weight`}
              />
              <p className="mb-1.5 text-[12px] leading-relaxed text-bone-500">
                <span className="text-bone-300">A 5 means:</span> {d.high_means}
              </p>
              <p className="text-[11.5px] leading-relaxed text-bone-600">{d.evidence_note}</p>
              <p className="mt-1.5 flex flex-wrap gap-x-3 gap-y-1">
                {d.sources.map((id) => {
                  const s = sources[id];
                  if (!s) {
                    return (
                      <span key={id} className="text-[11px] text-signal-severe">
                        unresolved source ({id})
                      </span>
                    );
                  }
                  return (
                    <a
                      key={id}
                      href={s.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[11px] text-bone-600 underline decoration-ink-500 underline-offset-2 hover:text-ember-300"
                      title={s.caveat ?? s.title}
                    >
                      {s.publisher}
                    </a>
                  );
                })}
              </p>
            </div>
          );
        })}
      </div>

      <div className="mt-9 flex items-center gap-3 border-t border-ink-700 pt-5">
        <button
          className="btn"
          onClick={() => onChange({ ...rubric.default_weights })}
        >
          Reset to equal
        </button>
        <p className="text-[11.5px] text-bone-600">
          Weights are normalised before use, so only their ratio matters.
        </p>
      </div>
    </section>
  );
}
