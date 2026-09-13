"use client";

import type { PriceBook, Rubric, Source } from "@/lib/types";

/**
 * The part that survives a sharp client. Everything the model rests on, including
 * what it does not know, stated before they ask.
 */
export default function MethodPanel({
  rubric,
  pricebook,
  sources,
}: {
  rubric: Rubric;
  pricebook: PriceBook;
  sources: Record<string, Source>;
}) {
  const used = new Set<string>();
  rubric.dimensions.forEach((d) => d.sources.forEach((s) => used.add(s)));
  pricebook.anchors.forEach((a) => a.sources.forEach((s) => used.add(s)));
  pricebook.archetypes.forEach((a) => a.sources.forEach((s) => used.add(s)));

  return (
    <section className="max-w-3xl space-y-11">
      <div>
        <h2 className="mb-3 text-lg font-semibold text-bone-100">The model</h2>
        <p className="mb-4 text-[13px] leading-relaxed text-bone-300">{rubric.orientation}</p>
        <pre className="tabular overflow-x-auto rounded border border-ink-700 bg-ink-850 px-4 py-3.5 text-[12px] leading-relaxed text-bone-300">
{`n_d       = (score_d - 1) / 4        -> [0,1]
exposure  = sum(weight_d * n_d)      -> [0,1]
exposed % = sum(revenue_share * exposure)`}
        </pre>
      </div>

      <div>
        <h2 className="mb-4 text-lg font-semibold text-bone-100">What this does not know</h2>
        <ul className="space-y-3.5">
          <Gap tier="judgment" title="No source scores a named service line.">
            Nothing in the research gives a numeric AI-substitution risk for &quot;web design&quot; or
            any other line. The scores here are structured judgment against a sourced rubric. They
            are reproducible and arguable, which is the point, but they are not measurements.
          </Gap>
          <Gap tier="judgment" title="The weights have no source.">
            No study establishes how much each dimension contributes to substitution risk. They
            default to equal and are adjustable, and the number moves when you change them.
          </Gap>
          <Gap tier="documented" title="The price book is one source.">
            {pricebook.global_caveat}
          </Gap>
          <Gap tier="practitioner" title="Artifact billing is the weakest dimension.">
            That accountable delivery is the defensible position rests on a single practitioner
            argument. It is reasoning, not measurement, and it is flagged as such wherever it is
            used.
          </Gap>
          <Gap tier="documented" title="Market figures are real; applying them here is inference.">
            Delivery compressing 3-4x, Big Six share falling from 44.6% to 29.6%, and 60% of US
            marketing leaders spending less on agencies are all documented at market level. That
            they apply to this specific business in this proportion is an inference.
          </Gap>
        </ul>
      </div>

      <div>
        <h2 className="mb-4 text-lg font-semibold text-bone-100">Dimensions</h2>
        <div className="space-y-5">
          {rubric.dimensions.map((d) => (
            <div key={d.id} className="border-t border-ink-700 pt-3.5">
              <div className="mb-1.5 flex flex-wrap items-center gap-2.5">
                <span className="text-[14px] font-medium text-bone-100">{d.name}</span>
                <span className={`tag tag-${d.evidence_tier}`}>{d.evidence_tier}</span>
              </div>
              <p className="mb-2.5 text-[12.5px] text-bone-500">{d.question}</p>
              <ol className="space-y-1">
                {Object.entries(d.anchors)
                  .sort(([a], [b]) => Number(a) - Number(b))
                  .map(([n, text]) => (
                    <li key={n} className="flex gap-3 text-[12px] leading-relaxed text-bone-500">
                      <span className="tabular shrink-0 text-bone-600">{n}</span>
                      <span>{text}</span>
                    </li>
                  ))}
              </ol>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h2 className="mb-4 text-lg font-semibold text-bone-100">Sources</h2>
        <ul className="space-y-3">
          {[...used].sort().map((id) => {
            const s = sources[id];
            if (!s) {
              return (
                <li key={id} className="text-[12.5px] text-signal-severe">
                  <code>{id}</code> does not resolve. Any claim resting on it is unsourced.
                </li>
              );
            }
            return (
              <li key={id} className="border-t border-ink-700 pt-3">
                <a
                  href={s.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[13px] text-bone-100 underline decoration-ink-500 underline-offset-2 hover:text-ember-300"
                >
                  {s.title}
                </a>
                <p className="tabular mt-1 text-[11px] text-bone-600">
                  {s.publisher} &middot; {s.kind}
                </p>
                {s.caveat && (
                  <p className="mt-1.5 text-[11.5px] leading-relaxed text-signal-moderate">
                    {s.caveat}
                  </p>
                )}
              </li>
            );
          })}
        </ul>
      </div>
    </section>
  );
}

function Gap({
  tier,
  title,
  children,
}: {
  tier: "documented" | "practitioner" | "judgment";
  title: string;
  children: React.ReactNode;
}) {
  return (
    <li className="border-t border-ink-700 pt-3.5">
      <div className="mb-1.5 flex flex-wrap items-center gap-2.5">
        <span className={`tag tag-${tier}`}>{tier}</span>
        <span className="text-[13px] font-medium text-bone-100">{title}</span>
      </div>
      <p className="text-[12.5px] leading-relaxed text-bone-500">{children}</p>
    </li>
  );
}
