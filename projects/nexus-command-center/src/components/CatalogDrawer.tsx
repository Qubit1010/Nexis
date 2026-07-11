import { useMemo, useState } from "react";
import { useStore } from "../store";
import { colorFor, TYPE_LABEL } from "../palette";

/** Left slide-in: searchable catalog — the keyboard path to every node. */
export default function CatalogDrawer() {
  const graph = useStore((s) => s.graph);
  const open = useStore((s) => s.catalogOpen);
  const setCatalog = useStore((s) => s.setCatalog);
  const select = useStore((s) => s.select);
  const setFocus = useStore((s) => s.setFocus);
  const [q, setQ] = useState("");

  const results = useMemo(() => {
    if (!graph) return [];
    const needle = q.trim().toLowerCase();
    const hits = needle
      ? graph.nodes.filter(
          (n) => n.label.toLowerCase().includes(needle) || n.id.toLowerCase().includes(needle),
        )
      : graph.nodes;
    return hits.slice(0, 60);
  }, [graph, q]);

  return (
    <aside
      className="absolute inset-y-0 left-0 z-30 flex w-[380px] flex-col overflow-hidden"
      style={{
        background: "var(--np-panel-grad)",
        borderRight: "1px solid var(--np-hairline)",
        transform: open ? "translateX(0)" : "translateX(-100%)",
        transition: "transform 240ms var(--np-ease)",
      }}
      aria-hidden={!open}
    >
      <div className="flex items-center justify-between p-6 pb-4">
        <h2 className="np-display text-xl">Catalog</h2>
        <button className="np-btn-ghost" style={{ padding: "4px 12px" }} onClick={() => setCatalog(false)}>
          esc
        </button>
      </div>
      <div className="px-6 pb-3">
        <input
          className="np-input"
          placeholder="Search skills, projects, wiki…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          autoFocus={open}
        />
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto px-3 pb-4">
        {results.length === 0 ? (
          <p className="px-3 py-6 text-sm" style={{ color: "var(--np-fog)" }}>
            Nothing matches — the system doesn't do that yet.
          </p>
        ) : (
          results.map((n) => (
            <button
              key={n.id}
              className="np-t flex w-full items-center gap-2 rounded-md px-3 py-2 text-left text-sm hover:bg-white/5"
              onClick={() => {
                select(n.id);
                setFocus(n.id);
              }}
            >
              <span
                className="inline-block h-2 w-2 shrink-0 rounded-full"
                style={{ background: colorFor(n.colorIndex) }}
              />
              <span className="truncate">{n.label}</span>
              <span className="np-mono ml-auto shrink-0 opacity-50">
                {TYPE_LABEL[n.type] ?? n.type}
              </span>
            </button>
          ))
        )}
        {graph && results.length === 60 && (
          <p className="np-mono px-3 py-2 opacity-50">showing first 60 — refine the search</p>
        )}
      </div>
    </aside>
  );
}
