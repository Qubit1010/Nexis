"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { computeAudit } from "@/lib/scoring";
import { renderAuditMarkdown } from "@/lib/markdown";
import type { Audit, PriceBook, Rubric, ServiceLine, Source, Weights } from "@/lib/types";
import ExposureHeader from "./ExposureHeader";
import LinesPanel from "./LinesPanel";
import WeightsPanel from "./WeightsPanel";
import MenuPanel from "./MenuPanel";
import MethodPanel from "./MethodPanel";

type Tab = "lines" | "weights" | "menu" | "method";

const TABS: { id: Tab; label: string }[] = [
  { id: "lines", label: "Revenue lines" },
  { id: "weights", label: "Weights" },
  { id: "menu", label: "Repriced menu" },
  { id: "method", label: "Method & sources" },
];

export default function Workspace({
  initialAudit,
  rubric,
  pricebook,
  sources,
}: {
  initialAudit: Audit;
  rubric: Rubric;
  pricebook: PriceBook;
  sources: Record<string, Source>;
}) {
  const [audit, setAudit] = useState<Audit>(initialAudit);
  const [tab, setTab] = useState<Tab>("lines");
  const [saveState, setSaveState] = useState<"saved" | "saving" | "error">("saved");
  const [saveError, setSaveError] = useState<string | null>(null);
  const firstRender = useRef(true);

  const result = useMemo(() => computeAudit(audit.lines, audit.weights), [audit]);

  /* Debounced autosave. The data is local, so the round-trip is cheap and losing
     edits mid-call would be worse than an occasional redundant write. */
  useEffect(() => {
    if (firstRender.current) {
      firstRender.current = false;
      return;
    }
    setSaveState("saving");
    const t = setTimeout(async () => {
      try {
        const res = await fetch(`/api/audits/${audit.id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            business: audit.business,
            weights: audit.weights,
            rubric_version: audit.rubric_version,
            pricebook_version: audit.pricebook_version,
            lines: audit.lines,
          }),
        });
        if (!res.ok) {
          const data = await res.json().catch(() => ({}));
          throw new Error(data.error ?? `Save failed (${res.status})`);
        }
        setSaveState("saved");
        setSaveError(null);
      } catch (err) {
        setSaveState("error");
        setSaveError(err instanceof Error ? err.message : String(err));
      }
    }, 700);
    return () => clearTimeout(t);
  }, [audit]);

  /**
   * Takes an updater rather than an array so an in-flight scoring request merges into
   * whatever the lines are when it lands, instead of overwriting edits made while it ran.
   */
  const setLines = useCallback((update: (prev: ServiceLine[]) => ServiceLine[]) => {
    setAudit((a) => ({ ...a, lines: update(a.lines) }));
  }, []);

  const setWeights = useCallback((weights: Weights) => {
    setAudit((a) => ({ ...a, weights }));
  }, []);

  function exportMarkdown() {
    const md = renderAuditMarkdown(audit, rubric, pricebook, sources);
    const blob = new Blob([md], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `ai-exposure-audit-${audit.business.name
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "")}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <div className="no-print mb-8 flex items-center justify-between">
        <Link href="/" className="tabular text-[11px] uppercase tracking-[0.16em] text-bone-600 hover:text-bone-300">
          &larr; All audits
        </Link>
        <div className="flex items-center gap-4">
          <span
            className="tabular text-[10px] uppercase tracking-[0.12em]"
            style={{
              color:
                saveState === "error"
                  ? "var(--color-signal-severe)"
                  : saveState === "saving"
                    ? "var(--color-bone-600)"
                    : "var(--color-signal-low)",
            }}
            title={saveError ?? undefined}
          >
            {saveState === "saving" ? "saving" : saveState === "error" ? "save failed" : "saved"}
          </span>
          <button className="btn" onClick={() => window.print()}>
            Print
          </button>
          <button className="btn btn-primary" onClick={exportMarkdown}>
            Export markdown
          </button>
        </div>
      </div>

      {saveError && (
        <div className="no-print mb-6 rounded border border-signal-severe/40 bg-signal-severe/10 px-4 py-3">
          <p className="text-[13px] text-signal-severe">
            Changes are not being saved: {saveError}
          </p>
        </div>
      )}

      <ExposureHeader
        audit={audit}
        result={result}
        onBusinessChange={(business) => setAudit((a) => ({ ...a, business }))}
      />

      <nav className="no-print mb-8 flex gap-1 overflow-x-auto border-b border-ink-700">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className="tabular -mb-px shrink-0 whitespace-nowrap border-b-2 px-4 py-3 text-[11px] uppercase tracking-[0.12em] transition-colors"
            style={{
              borderColor: tab === t.id ? "var(--color-ember-500)" : "transparent",
              color: tab === t.id ? "var(--color-bone-100)" : "var(--color-bone-600)",
            }}
          >
            {t.label}
          </button>
        ))}
      </nav>

      {tab === "lines" && (
        <LinesPanel
          audit={audit}
          rubric={rubric}
          result={result}
          onLinesChange={setLines}
        />
      )}
      {tab === "weights" && (
        <WeightsPanel
          rubric={rubric}
          weights={audit.weights}
          sources={sources}
          onChange={setWeights}
        />
      )}
      {tab === "menu" && (
        <MenuPanel
          audit={audit}
          pricebook={pricebook}
          sources={sources}
          result={result}
          onLinesChange={setLines}
        />
      )}
      {tab === "method" && (
        <MethodPanel rubric={rubric} pricebook={pricebook} sources={sources} />
      )}
    </main>
  );
}
