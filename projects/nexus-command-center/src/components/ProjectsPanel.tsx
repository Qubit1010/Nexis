import { useEffect, useState } from "react";
import { api, ApiError, type ProjectView } from "../api";
import { useStore } from "../store";

const STATUS_COLOR: Record<string, string> = {
  stopped: "var(--np-fog)",
  starting: "var(--np-warn)",
  running: "var(--np-ok)",
  exited: "var(--np-err)",
};

function uptime(started: string | null, now: number): string {
  if (!started) return "";
  const s = Math.max(0, Math.floor((now - Date.parse(started)) / 1000));
  if (s < 60) return `${s}s`;
  const m = Math.floor(s / 60);
  return m < 60 ? `${m}m` : `${Math.floor(m / 60)}h ${m % 60}m`;
}

/** Projects tab: curated launchables from projects.json, server-supervised. */
export default function ProjectsPanel() {
  const projects = useStore((s) => s.projects);
  const loadProjects = useStore((s) => s.loadProjects);
  const [busy, setBusy] = useState<string | null>(null);
  const [logsFor, setLogsFor] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [now, setNow] = useState(Date.now());

  // Poll while the tab is open; supervisor state is cheap to read.
  useEffect(() => {
    loadProjects();
    const iv = setInterval(() => {
      loadProjects();
      setNow(Date.now());
    }, 3000);
    return () => clearInterval(iv);
  }, [loadProjects]);

  // Graph -> cockpit: SidePanel's "Open in Projects" highlights the card.
  const focusProjectId = useStore((s) => s.focusProjectId);
  const setFocusProject = useStore((s) => s.setFocusProject);
  useEffect(() => {
    if (!focusProjectId) return;
    const t = setTimeout(() => setFocusProject(null), 5000);
    return () => clearTimeout(t);
  }, [focusProjectId, setFocusProject]);

  const act = async (p: ProjectView, fn: (id: string) => Promise<unknown>) => {
    setBusy(p.id);
    setErr(null);
    try {
      await fn(p.id);
      await loadProjects();
    } catch (e) {
      setErr(e instanceof ApiError ? `${p.label}: ${e.message}` : `${p.label}: request failed`);
    } finally {
      setBusy(null);
    }
  };

  return (
    <div className="p-5">
      <div className="mb-4 flex items-center gap-4">
        <span
          className="text-[11px] uppercase"
          style={{ color: "var(--np-fog)", letterSpacing: "0.22em" }}
        >
          Projects
        </span>
        <span className="np-mono text-xs" style={{ color: "var(--np-fog)" }}>
          {projects.filter((p) => p.status === "running").length} running
        </span>
        {err && (
          <span className="text-[13px]" style={{ color: "var(--np-err)" }}>
            {err}
          </span>
        )}
      </div>

      {projects.length === 0 && (
        <span className="np-mono opacity-50">no projects registered — check projects.json</span>
      )}

      <div className="grid grid-cols-1 gap-3 lg:grid-cols-2 2xl:grid-cols-3">
        {projects.map((p) => {
          const stoppable = p.status === "running" || p.status === "starting";
          return (
            <div
              key={p.id}
              className="np-panel np-t p-4"
              style={focusProjectId === p.id ? { borderColor: "var(--np-blue)" } : undefined}
            >
              <div className="flex items-center gap-2">
                <span
                  className={`inline-block h-2.5 w-2.5 rounded-full ${p.status === "starting" ? "np-pulse" : ""}`}
                  style={{ background: STATUS_COLOR[p.status] }}
                />
                <span className="text-[15px]">{p.label}</span>
                <span className="np-mono text-xs" style={{ color: "var(--np-fog)" }}>
                  :{p.port}
                </span>
                <span className="np-mono ml-auto text-xs" style={{ color: "var(--np-fog)" }}>
                  {p.status === "running" && uptime(p.started, now)}
                  {p.status === "exited" && `exit ${p.exit_code ?? "?"}`}
                  {p.status === "starting" && "starting…"}
                </span>
              </div>
              <p className="mt-1 mb-3 text-sm" style={{ color: "var(--np-fog)" }}>
                {p.description}
              </p>
              <div className="flex items-center gap-2">
                {stoppable ? (
                  <button
                    className="np-btn-ghost"
                    disabled={busy === p.id}
                    onClick={() => act(p, api.projectStop)}
                  >
                    Stop
                  </button>
                ) : (
                  <button
                    className="np-btn-primary"
                    disabled={busy === p.id}
                    onClick={() => act(p, api.projectStart)}
                  >
                    Start
                  </button>
                )}
                <button
                  className="np-btn-ghost"
                  disabled={p.status !== "running"}
                  onClick={() => window.open(p.url, "_blank")}
                >
                  Open
                </button>
                <button className="np-btn-ghost" onClick={() => act(p, api.openEditor)}>
                  Editor
                </button>
                <button
                  className="np-btn-ghost ml-auto"
                  onClick={() => setLogsFor(logsFor === p.id ? null : p.id)}
                >
                  Logs
                </button>
              </div>
              {logsFor === p.id && (
                <pre
                  className="np-mono mt-3 max-h-40 overflow-y-auto rounded-md p-3 text-xs whitespace-pre-wrap"
                  style={{ background: "rgba(11,11,11,0.7)", border: "1px solid var(--np-hairline)" }}
                >
                  {p.logs.length ? p.logs.join("\n") : "no output yet"}
                </pre>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
