import DOMPurify from "dompurify";
import { marked } from "marked";
import { useCallback, useEffect, useState } from "react";
import { api, ApiError, type BrainStatus, type OpsData } from "../api";
import { useStore } from "../store";

marked.setOptions({ gfm: true, breaks: true, async: false });

function md(text: string): { __html: string } {
  return { __html: DOMPurify.sanitize(marked.parse(text) as string) };
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <div
      className="mb-2 text-[11px] uppercase"
      style={{ color: "var(--np-fog)", letterSpacing: "0.22em" }}
    >
      {children}
    </div>
  );
}

function basename(p: string): string {
  const parts = p.replace(/\\/g, "/").split("/");
  return parts[parts.length - 1] || p;
}

/**
 * Brain tab: the knowledge half's health (freshness/OVERDUE + drift, from the
 * brain-sync script), CRITICAL_FACTS inline, recent activity, and ops depth
 * (spend, run history, outputs). Signal + safe check only — the real ingest
 * stays Claude-driven in a session, so there is no "ingest" button here.
 */
export default function BrainPanel() {
  const deck = useStore((s) => s.deck);
  const setDeck = useStore((s) => s.setDeck);
  const loadGraph = useStore((s) => s.loadGraph);
  const loadVitals = useStore((s) => s.loadVitals);
  const [brain, setBrain] = useState<BrainStatus | null>(null);
  const [ops, setOps] = useState<OpsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);
  const [scanBusy, setScanBusy] = useState(false);
  const [scanMsg, setScanMsg] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const [b, o] = await Promise.all([api.brain(), api.ops()]);
      setBrain(b);
      setOps(o);
      setErr(null);
    } catch {
      setErr("Failed to load brain status.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const running = !!deck?.running;
  const locked = !!deck?.locked;

  const checkBrain = async () => {
    try {
      await api.run("brain-pulse"); // existing read-profile deck preset
      setDeck(await api.status());
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : "Failed to start the check.");
    }
  };

  const rescan = async () => {
    setScanBusy(true);
    setScanMsg(null);
    try {
      const r = await api.scanGraph();
      setScanMsg(`rescanned — ${r.counts.nodes ?? "?"} nodes / ${r.counts.edges ?? "?"} edges`);
      await Promise.all([loadGraph(), loadVitals()]);
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : "Scan failed.");
    } finally {
      setScanBusy(false);
    }
  };

  const f = brain?.freshness;
  const d = brain?.drift;
  const maxUsd = Math.max(0.0001, ...(ops?.spend_by_day.map((s) => s.usd) ?? []));

  return (
    <div className="flex h-full flex-col">
      {/* Status strip */}
      <div
        className="flex shrink-0 flex-wrap items-center gap-3 px-5 py-3"
        style={{ borderBottom: "1px solid var(--np-hairline)" }}
      >
        {f ? (
          <span
            className="np-chip"
            style={{
              cursor: "default",
              borderColor: f.stale ? "var(--np-warn)" : "var(--np-ok)",
              color: f.stale ? "var(--np-warn)" : "var(--np-ok)",
            }}
            title={f.stale ? `${f.new_skills.length} new skills, ${f.new_decisions} new decisions` : "wiki is current"}
          >
            {f.stale ? "INGEST OVERDUE" : "WIKI CURRENT"}
            <span style={{ color: "var(--np-fog)" }}>
              last {f.last_ingest ?? "never"} · {f.days_since ?? "—"}d ago
            </span>
          </span>
        ) : (
          <span className="np-chip" style={{ cursor: "default" }}>
            freshness unavailable
          </span>
        )}
        {d && (
          <span
            className="np-chip"
            style={{ cursor: "default", color: d.in_sync ? "var(--np-fog)" : "var(--np-warn)" }}
            title={
              d.in_sync
                ? "context/ + decisions/ match the vault"
                : [...d.differ.map((x) => x.file), ...d.nexis_only, ...d.vault_only].join(", ")
            }
          >
            mirror {d.in_sync ? "in sync" : `${d.differ.length + d.nexis_only.length + d.vault_only.length} drifted`}
          </span>
        )}
        <span className="ml-auto flex items-center gap-2">
          {scanMsg && (
            <span className="np-mono text-xs" style={{ color: "var(--np-ok)" }}>
              {scanMsg}
            </span>
          )}
          <button
            className="np-btn-ghost"
            disabled={running || locked}
            title="Run the Brain Pulse deck preset (read-only headless check)"
            onClick={() => void checkBrain()}
          >
            Check brain
          </button>
          <button
            className="np-btn-ghost"
            disabled={scanBusy}
            title="Re-run the graph scanner (local, free)"
            onClick={() => void rescan()}
          >
            {scanBusy ? "Scanning…" : "Rescan graph"}
          </button>
          <button className="np-btn-ghost" onClick={() => void refresh()}>
            Refresh
          </button>
        </span>
      </div>

      {err && (
        <p className="px-5 pt-2 text-[13px]" style={{ color: "var(--np-err)" }}>
          {err}
        </p>
      )}

      {loading && !brain ? (
        <div className="flex flex-1 items-center justify-center">
          <span className="np-mono" style={{ color: "var(--np-fog)" }}>
            reading the brain…
          </span>
        </div>
      ) : (
        <div className="grid min-h-0 flex-1 grid-cols-1 gap-4 overflow-y-auto p-5 xl:grid-cols-3">
          {/* Health + activity */}
          <div className="min-w-0 space-y-5">
            {f && f.stale && (
              <div>
                <SectionTitle>Behind since {f.last_ingest ?? "?"}</SectionTitle>
                <p className="text-sm" style={{ color: "var(--np-fog)" }}>
                  {f.new_skills.length} new skill(s), {f.new_decisions} new decision(s). Run the
                  brain-sync ingest from a session to distill them.
                </p>
                {f.new_skills.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {f.new_skills.map((s) => (
                      <span key={s} className="np-chip" style={{ cursor: "default" }}>
                        {s}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}
            <div>
              <SectionTitle>Wiki ingest log</SectionTitle>
              <div className="space-y-1.5">
                {brain?.wiki_log.length ? (
                  [...brain.wiki_log].reverse().map((l, i) => (
                    <p key={i} className="truncate text-[13px]" style={{ color: "var(--np-fog)" }} title={l}>
                      {l.replace(/^-\s*/, "")}
                    </p>
                  ))
                ) : (
                  <span className="np-mono opacity-50">no log</span>
                )}
              </div>
            </div>
            <div>
              <SectionTitle>Recent decisions</SectionTitle>
              <div className="space-y-1.5">
                {brain?.recent_decisions.length ? (
                  [...brain.recent_decisions].reverse().map((l, i) => (
                    <p key={i} className="truncate text-[13px]" style={{ color: "var(--np-fog)" }} title={l}>
                      {l.split(" | ")[0]}
                    </p>
                  ))
                ) : (
                  <span className="np-mono opacity-50">no decisions</span>
                )}
              </div>
            </div>
          </div>

          {/* Critical facts */}
          <div className="min-w-0">
            <SectionTitle>Critical facts (always loaded)</SectionTitle>
            {brain?.critical_facts ? (
              <div
                className="chat-md rounded-md p-4 text-[13px]"
                style={{ background: "rgba(11,11,11,0.5)", border: "1px solid var(--np-hairline)" }}
                dangerouslySetInnerHTML={md(brain.critical_facts)}
              />
            ) : (
              <span className="np-mono opacity-50">CRITICAL_FACTS.md not readable</span>
            )}
          </div>

          {/* Ops depth */}
          <div className="min-w-0 space-y-5">
            <div>
              <SectionTitle>Run spend · last {ops?.spend_by_day.length ?? 0} active days</SectionTitle>
              {ops?.spend_by_day.length ? (
                <div className="flex h-20 items-end gap-1" aria-label="Spend by day">
                  {ops.spend_by_day.map((s) => (
                    <div
                      key={s.day}
                      className="flex-1 rounded-t-sm"
                      style={{
                        height: `${Math.max(6, (s.usd / maxUsd) * 100)}%`,
                        background: "var(--np-grad)",
                        minWidth: 6,
                      }}
                      title={`${s.day} · $${s.usd.toFixed(3)} · ${s.runs} run(s)`}
                    />
                  ))}
                </div>
              ) : (
                <span className="np-mono opacity-50">no runs logged yet</span>
              )}
            </div>
            <div>
              <SectionTitle>Recent runs</SectionTitle>
              <div className="space-y-1">
                {ops?.recent_runs.length ? (
                  ops.recent_runs.slice(0, 10).map((r, i) => (
                    <div key={i} className="np-mono flex items-center gap-2 text-xs" title={r.ts}>
                      <span style={{ color: "var(--np-fog)" }}>{r.ts.slice(5, 16).replace("T", " ")}</span>
                      <span className="min-w-0 flex-1 truncate">{r.label}</span>
                      <span style={{ color: "var(--np-fog)" }}>{r.profile}</span>
                      <span>${r.cost_usd.toFixed(3)}</span>
                      <span
                        style={{ color: r.exit === "ok" ? "var(--np-ok)" : "var(--np-err)" }}
                      >
                        {r.exit}
                      </span>
                    </div>
                  ))
                ) : (
                  <span className="np-mono opacity-50">none yet</span>
                )}
              </div>
            </div>
            <div>
              <SectionTitle>Recent outputs → vault</SectionTitle>
              <div className="space-y-1">
                {ops?.recent_outputs.length ? (
                  ops.recent_outputs.map((o, i) => (
                    <div key={i} className="np-mono flex items-center gap-2 text-xs" title={o.file}>
                      <span className="min-w-0 flex-1 truncate">{basename(o.file)}</span>
                      <span style={{ color: "var(--np-fog)" }}>{o.label}</span>
                    </div>
                  ))
                ) : (
                  <span className="np-mono opacity-50">none yet</span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
