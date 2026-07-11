import { useMemo } from "react";
import { endpointId, type GraphNode } from "../api";
import { useStore } from "../store";
import { colorFor, TYPE_LABEL } from "../palette";

function prettyPath(p: string): string {
  const parts = p.replace(/\\/g, "/").split("/").filter(Boolean);
  return parts.length > 3 ? "…/" + parts.slice(-3).join("/") : parts.join("/");
}

/** Right slide-in: selected node detail + neighbors (architecture.md §7). */
export default function SidePanel() {
  const graph = useStore((s) => s.graph);
  const selectedId = useStore((s) => s.selectedId);
  const select = useStore((s) => s.select);
  const setFocus = useStore((s) => s.setFocus);
  const projects = useStore((s) => s.projects);
  const skillActions = useStore((s) => s.skillActions);
  const setConsoleTab = useStore((s) => s.setConsoleTab);
  const setFocusProject = useStore((s) => s.setFocusProject);
  const setFocusAction = useStore((s) => s.setFocusAction);

  const node = useMemo(
    () => graph?.nodes.find((n) => n.id === selectedId) ?? null,
    [graph, selectedId],
  );

  // Graph -> cockpit: a node that maps to a registry entry gets a launcher.
  const launchProject = useMemo(() => {
    if (node?.type !== "project") return null;
    const dir = node.id.split("/").pop();
    return projects.find((p) => p.id === dir) ?? null;
  }, [node, projects]);
  const launchAction = useMemo(() => {
    if (node?.type !== "skill") return null;
    const folder = node.id.split("/").pop();
    return skillActions.find((a) => a.skill === folder) ?? null;
  }, [node, skillActions]);

  const neighbors = useMemo(() => {
    if (!graph || !selectedId) return [];
    const out: { node: GraphNode; relation: string }[] = [];
    const seen = new Set<string>();
    for (const l of graph.links) {
      const s = endpointId(l.source);
      const t = endpointId(l.target);
      const otherId = s === selectedId ? t : t === selectedId ? s : null;
      if (!otherId || seen.has(otherId)) continue;
      const other = graph.nodes.find((n) => n.id === otherId);
      if (other) {
        seen.add(otherId);
        out.push({ node: other, relation: l.relation });
      }
    }
    return out;
  }, [graph, selectedId]);

  const open = !!node;
  const isAbs = node ? /^[A-Za-z]:[\\/]/.test(node.source_file) : false;
  const vscodeHref = node && isAbs ? `vscode://file/${node.source_file.replace(/\\/g, "/")}` : null;

  return (
    <aside
      className="absolute inset-y-0 right-0 z-30 flex w-[360px] flex-col overflow-hidden"
      style={{
        background: "var(--np-panel-grad)",
        borderLeft: "1px solid var(--np-hairline)",
        boxShadow: open ? "0 0 32px rgba(32,142,199,0.12)" : "none",
        transform: open ? "translateX(0)" : "translateX(100%)",
        transition: "transform 240ms var(--np-ease)",
      }}
      aria-hidden={!open}
    >
      {node && (
        <div className="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto p-6">
          <div className="flex items-center justify-between">
            <span className="np-chip" style={{ cursor: "default" }}>
              <span
                className="inline-block h-2 w-2 rounded-full"
                style={{ background: colorFor(node.colorIndex) }}
              />
              {TYPE_LABEL[node.type] ?? node.type}
            </span>
            <button className="np-btn-ghost" style={{ padding: "4px 12px" }} onClick={() => select(null)}>
              esc
            </button>
          </div>

          <div>
            <h2 className="np-display text-xl leading-snug">{node.label}</h2>
            <div className="np-mono mt-1" style={{ color: "var(--np-fog)" }}>
              {node.id} · group {String(node.group)}
            </div>
          </div>

          {node.summary && (
            <p className="text-sm" style={{ color: "var(--np-fog)" }}>
              {node.summary}
            </p>
          )}

          {node.source_file && (
            <div
              className="rounded-md p-3"
              style={{ background: "rgba(11,11,11,0.6)", border: "1px solid var(--np-hairline)" }}
            >
              <div className="np-mono mb-2 break-all" title={node.source_file}>
                {prettyPath(node.source_file)}
              </div>
              <div className="flex flex-wrap gap-2">
                {vscodeHref && (
                  <a className="np-btn-ghost inline-block no-underline" href={vscodeHref}>
                    Open in VS Code
                  </a>
                )}
                {launchProject && (
                  <button
                    className="np-btn-primary"
                    onClick={() => {
                      setFocusProject(launchProject.id);
                      setConsoleTab("projects");
                    }}
                  >
                    Open in Projects
                  </button>
                )}
                {launchAction && (
                  <button
                    className="np-btn-primary"
                    onClick={() => {
                      setFocusAction(launchAction.id);
                      setConsoleTab("skills");
                    }}
                  >
                    Run this skill
                  </button>
                )}
              </div>
            </div>
          )}

          {neighbors.length > 0 && (
            <div>
              <div
                className="mb-2 text-[11px] uppercase"
                style={{ color: "var(--np-fog)", letterSpacing: "0.18em" }}
              >
                Connected · {neighbors.length}
              </div>
              <div className="flex flex-col gap-1">
                {neighbors.slice(0, 14).map(({ node: nb, relation }) => (
                  <button
                    key={nb.id}
                    className="np-t flex items-center gap-2 rounded-md px-2 py-1.5 text-left text-sm hover:bg-white/5"
                    onClick={() => {
                      select(nb.id);
                      setFocus(nb.id);
                    }}
                  >
                    <span
                      className="inline-block h-2 w-2 shrink-0 rounded-full"
                      style={{ background: colorFor(nb.colorIndex) }}
                    />
                    <span className="truncate">{nb.label}</span>
                    <span className="np-mono ml-auto shrink-0 opacity-50">{relation}</span>
                  </button>
                ))}
                {neighbors.length > 14 && (
                  <span className="np-mono px-2 opacity-50">+{neighbors.length - 14} more</span>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </aside>
  );
}
