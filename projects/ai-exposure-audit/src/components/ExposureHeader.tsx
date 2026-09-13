"use client";

import type { Audit, AuditResult, Business } from "@/lib/types";

/**
 * The headline. The exposure number is deliberately the largest thing on the page,
 * and it renders as "not calculable" rather than 0 when nothing is scored.
 */
export default function ExposureHeader({
  audit,
  result,
  onBusinessChange,
}: {
  audit: Audit;
  result: AuditResult;
  onBusinessChange: (b: Business) => void;
}) {
  const pct = result.exposed_revenue_pct;

  const color =
    pct === null
      ? "var(--color-bone-600)"
      : pct >= 60
        ? "var(--color-signal-severe)"
        : pct >= 40
          ? "var(--color-signal-high)"
          : pct >= 20
            ? "var(--color-signal-moderate)"
            : "var(--color-signal-low)";

  return (
    <header className="print-block mb-10">
      <input
        className="mb-1 w-full min-w-0 border-none bg-transparent p-0 text-3xl font-semibold tracking-tight text-bone-100 outline-none focus:text-ember-300"
        value={audit.business.name}
        onChange={(e) => onBusinessChange({ ...audit.business, name: e.target.value })}
        aria-label="Business name"
      />
      <input
        className="no-print mb-8 w-full min-w-0 border-none bg-transparent p-0 text-[13px] text-bone-500 outline-none placeholder:text-bone-600 focus:text-bone-300"
        value={audit.business.positioning}
        placeholder="How they position themselves today (optional, sharpens the scoring)"
        onChange={(e) => onBusinessChange({ ...audit.business, positioning: e.target.value })}
        aria-label="Positioning"
      />

      <div className="flex flex-wrap items-end gap-x-12 gap-y-6 border-y border-ink-700 py-7">
        <div>
          <p className="tabular mb-2 text-[10px] uppercase tracking-[0.18em] text-bone-600">
            Revenue exposed to AI substitution
          </p>
          {pct === null ? (
            <p className="tabular text-[42px] font-medium leading-none" style={{ color }}>
              not calculable
            </p>
          ) : (
            <p className="tabular text-[72px] font-bold leading-[0.85]" style={{ color }}>
              {pct.toFixed(1)}
              <span className="text-[32px] font-medium">%</span>
            </p>
          )}
        </div>

        <div className="flex gap-10">
          <Stat label="Lines" value={String(audit.lines.length)} />
          <Stat
            label="Book entered"
            value={`${result.total_revenue_pct.toFixed(0)}%`}
            warn={Math.abs(result.total_revenue_pct - 100) > 0.5 && audit.lines.length > 0}
          />
          <Stat
            label="Book scored"
            value={`${result.scored_revenue_pct.toFixed(0)}%`}
            warn={!result.complete && audit.lines.length > 0}
          />
        </div>
      </div>

      {pct !== null && (
        <p className="mt-4 max-w-2xl text-[13px] leading-relaxed text-bone-500">
          Each line&apos;s revenue share multiplied by its exposure score, summed. The per-line
          contributions below add up to this figure, so it can be checked by hand.
        </p>
      )}

      {result.warnings.length > 0 && (
        <ul className="mt-4 space-y-1.5">
          {result.warnings.map((w, i) => (
            <li key={i} className="flex gap-2.5 text-[12px] leading-relaxed text-signal-moderate">
              <span aria-hidden>&#9888;</span>
              <span>{w}</span>
            </li>
          ))}
        </ul>
      )}
    </header>
  );
}

function Stat({ label, value, warn }: { label: string; value: string; warn?: boolean }) {
  return (
    <div>
      <p className="tabular mb-1.5 text-[10px] uppercase tracking-[0.14em] text-bone-600">{label}</p>
      <p
        className="tabular text-2xl font-medium"
        style={{ color: warn ? "var(--color-signal-moderate)" : "var(--color-bone-300)" }}
      >
        {value}
      </p>
    </div>
  );
}
