import { useEffect } from "react";
import { useStore } from "../store";
import GraphCanvas from "./GraphCanvas.tsx";
import LegendFilters from "./LegendFilters.tsx";
import SidePanel from "./SidePanel.tsx";
import CatalogDrawer from "./CatalogDrawer.tsx";
import VitalsBar from "./VitalsBar.tsx";
import Console from "./Console.tsx";

export default function HudShell() {
  const graph = useStore((s) => s.graph);
  const graphError = useStore((s) => s.graphError);
  const catalogOpen = useStore((s) => s.catalogOpen);
  const setCatalog = useStore((s) => s.setCatalog);
  const select = useStore((s) => s.select);
  const loadGraph = useStore((s) => s.loadGraph);

  // Keyboard: Esc closes catalog / deselects; Ctrl+K or "/" opens the catalog
  // (the catalog is the accessible path to every node — design-system.md §8).
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const inField = (e.target as HTMLElement)?.tagName === "INPUT";
      if (e.key === "Escape") {
        if (useStore.getState().catalogOpen) setCatalog(false);
        else select(null);
      } else if ((e.key === "k" && (e.ctrlKey || e.metaKey)) || (e.key === "/" && !inField)) {
        e.preventDefault();
        setCatalog(true);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [setCatalog, select]);

  return (
    <div className="relative z-10 flex h-screen w-screen flex-col overflow-hidden">
      {/* Top bar */}
      <header
        className="flex h-14 shrink-0 items-center gap-4 px-5"
        style={{ borderBottom: "1px solid var(--np-hairline)", background: "rgba(11,11,11,0.55)", backdropFilter: "blur(8px)" }}
      >
        <div className="flex items-center gap-3">
          <img src="/logo-symbol-white.png" alt="NexusPoint" className="h-7 w-7 object-contain" />
          <span className="np-display text-[16px] tracking-wide" style={{ color: "var(--np-white)" }}>
            NEXUSPOINT
          </span>
          <span className="h-4 w-px" style={{ background: "var(--np-hairline)" }} />
          <span className="text-[11px] uppercase" style={{ color: "var(--np-fog)", letterSpacing: "0.22em" }}>
            Command Center
          </span>
        </div>
        <div className="ml-auto flex items-center gap-4">
          <VitalsBar />
          <button className="np-btn-ghost" onClick={() => setCatalog(!catalogOpen)}>
            Catalog <span className="np-mono ml-1 opacity-60">ctrl K</span>
          </button>
        </div>
      </header>

      {/* Graph stage */}
      <main className="relative min-h-0 flex-1">
        {graph ? (
          <GraphCanvas />
        ) : graphError === "missing" ? (
          <div className="flex h-full items-center justify-center">
            <div className="np-panel w-[520px] p-6">
              <div className="np-display text-xl mb-2">No system graph yet</div>
              <p className="mb-4 text-sm" style={{ color: "var(--np-fog)" }}>
                The scanner has not produced <span className="np-mono">data/system-graph.json</span>.
                Build it, then reload:
              </p>
              <pre
                className="np-mono rounded-md p-3"
                style={{ background: "rgba(11,11,11,0.7)", border: "1px solid var(--np-hairline)" }}
              >
                npm run scan
              </pre>
            </div>
          </div>
        ) : graphError ? (
          <div className="flex h-full items-center justify-center">
            <div className="np-panel w-[440px] p-6">
              <div className="np-display text-xl mb-2" style={{ color: "var(--np-err)" }}>
                Graph failed to load
              </div>
              <p className="np-mono mb-4" style={{ color: "var(--np-fog)" }}>
                {graphError}
              </p>
              <button className="np-btn-primary" onClick={() => loadGraph()}>
                Retry
              </button>
            </div>
          </div>
        ) : (
          <div className="flex h-full items-center justify-center">
            <span className="np-mono" style={{ color: "var(--np-fog)" }}>
              initializing…
            </span>
          </div>
        )}
        <LegendFilters />
        <SidePanel />
        <CatalogDrawer />
      </main>

      {/* Console dock: deck / projects / skills */}
      <Console />
    </div>
  );
}
