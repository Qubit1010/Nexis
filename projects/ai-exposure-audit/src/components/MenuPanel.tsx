"use client";

import { exposureBand } from "@/lib/scoring";
import type { Audit, AuditResult, PriceBook, ServiceLine, Source } from "@/lib/types";

/**
 * The deliverable: what each exposed line moves to, and at what anchor.
 *
 * Where no price anchor exists in the research (strategy work), it says so instead of
 * producing a number. That gap is the honest output, not a bug to paper over.
 */
export default function MenuPanel({
  audit,
  pricebook,
  sources,
  result,
  onLinesChange,
}: {
  audit: Audit;
  pricebook: PriceBook;
  sources: Record<string, Source>;
  result: AuditResult;
  onLinesChange: (update: (prev: ServiceLine[]) => ServiceLine[]) => void;
}) {
  const ordered = [...audit.lines].sort((a, b) => {
    const ra = result.lines.find((r) => r.line_id === a.id)?.contribution ?? -1;
    const rb = result.lines.find((r) => r.line_id === b.id)?.contribution ?? -1;
    return rb - ra;
  });

  function setReplacement(lineId: string, archetypeId: string) {
    onLinesChange((lines) =>
      lines.map((l) =>
        l.id === lineId
          ? {
              ...l,
              replacement: archetypeId
                ? { archetype_id: archetypeId, rationale: l.replacement?.rationale ?? "" }
                : null,
            }
          : l
      )
    );
  }

  function setRationale(lineId: string, rationale: string) {
    onLinesChange((lines) =>
      lines.map((l) =>
        l.id === lineId && l.replacement ? { ...l, replacement: { ...l.replacement, rationale } } : l
      )
    );
  }

  if (audit.lines.length === 0) {
    return (
      <div className="rounded border border-dashed border-ink-600 px-6 py-14 text-center">
        <p className="text-sm text-bone-500">Add revenue lines first.</p>
      </div>
    );
  }

  return (
    <section>
      <div className="mb-7 rounded border border-ink-600 bg-ink-850 px-5 py-4">
        <div className="mb-2 flex items-center gap-2.5">
          <span className="tag tag-documented">documented</span>
          <span className="text-[13px] font-medium text-bone-100">On the price anchors</span>
        </div>
        <p className="text-[12.5px] leading-relaxed text-bone-300">{pricebook.global_caveat}</p>
      </div>

      <div className="space-y-3.5">
        {ordered.map((line) => {
          const r = result.lines.find((x) => x.line_id === line.id);
          const arch = pricebook.archetypes.find((a) => a.id === line.replacement?.archetype_id);
          const anchor = arch?.anchor_ref
            ? pricebook.anchors.find((a) => a.id === arch.anchor_ref)
            : null;
          const band = r?.exposure != null ? exposureBand(r.exposure) : null;

          return (
            <article
              key={line.id}
              className="print-block rounded border border-ink-700 bg-ink-850 px-5 py-4"
            >
              <div className="mb-3.5 flex flex-wrap items-baseline gap-x-3 gap-y-1.5">
                <h3 className="text-[15px] font-medium text-bone-100">
                  {line.name || "Unnamed line"}
                </h3>
                <span className="tabular text-[11px] text-bone-600">
                  {line.revenue_share_pct}% of book &middot; priced {line.pricing_model}
                  {line.typical_price ? ` at ~${line.typical_price}` : ""}
                </span>
                {band && (
                  <span className="tabular ml-auto text-[11px] uppercase tracking-[0.1em] text-bone-500">
                    {band} exposure
                  </span>
                )}
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="tabular mb-1.5 block text-[10px] uppercase tracking-[0.12em] text-bone-600">
                    Move to
                  </label>
                  <select
                    className="field"
                    value={line.replacement?.archetype_id ?? ""}
                    onChange={(e) => setReplacement(line.id, e.target.value)}
                  >
                    <option value="">Not mapped</option>
                    {pricebook.archetypes.map((a) => (
                      <option key={a.id} value={a.id}>
                        {a.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="tabular mb-1.5 block text-[10px] uppercase tracking-[0.12em] text-bone-600">
                    Price anchor
                  </label>
                  {!arch ? (
                    <p className="pt-2 text-[13px] text-bone-600">Pick an archetype.</p>
                  ) : anchor ? (
                    <div className="flex flex-wrap items-center gap-2 pt-1.5">
                      <span className="tabular text-[15px] font-semibold text-ember-300">
                        {anchor.display}
                      </span>
                      <span className={`tag tag-${anchor.evidence_tier}`}>
                        {anchor.evidence_tier}
                      </span>
                      {anchor.sources.map((id) => {
                        const s = sources[id];
                        return s ? (
                          <a
                            key={id}
                            href={s.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-[11px] text-bone-600 underline decoration-ink-500 underline-offset-2 hover:text-ember-300"
                          >
                            {s.publisher}
                          </a>
                        ) : null;
                      })}
                    </div>
                  ) : (
                    <div className="pt-1.5">
                      <span className="tag tag-judgment">no anchor in sources</span>
                      <p className="mt-1.5 text-[11.5px] leading-relaxed text-bone-500">
                        Nothing in the research prices this. Any number here would be invented.
                        Price it from your own book.
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {arch && (
                <>
                  <p className="mt-3.5 text-[12.5px] leading-relaxed text-bone-300">
                    {arch.what_changes}
                  </p>
                  <p className="mt-1.5 text-[11.5px] leading-relaxed text-bone-600">
                    <span className={`tag tag-${arch.evidence_tier} mr-2`}>
                      {arch.evidence_tier}
                    </span>
                    {arch.evidence_note}
                  </p>
                  <textarea
                    className="field mt-3 min-h-[54px] resize-y text-[12.5px]"
                    placeholder="Anything specific to this client about the move. Goes into the deliverable."
                    value={line.replacement?.rationale ?? ""}
                    onChange={(e) => setRationale(line.id, e.target.value)}
                  />
                </>
              )}
            </article>
          );
        })}
      </div>
    </section>
  );
}
