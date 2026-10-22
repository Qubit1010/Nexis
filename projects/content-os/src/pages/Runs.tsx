import { useEffect, useRef, useState } from "react";
import { api, FORMAT_LABELS, type Format, type Run } from "../lib/api";
import { fmtDateTime } from "../lib/time";
import { useAction, useApi } from "../lib/hooks";
import { Button, Card, Empty, Pill, SectionTitle } from "../components/ui";

export function Runs() {
  const { data } = useApi<Run[]>("/runs");
  return (
    <div className="space-y-5">
      <header>
        <h1 className="text-[22px] font-semibold tracking-tight">Runs</h1>
        <p className="text-[13px] text-dim">Every headless Claude run. Cost is an estimate at API prices; on the subscription nothing is billed per run.</p>
      </header>
      {data && data.length === 0 && <Empty>No runs yet. Generate a draft from an item.</Empty>}
      <div className="overflow-x-auto rounded-xl border border-line">
        <table className="w-full min-w-[760px] text-[13px]">
          <thead className="bg-s1 text-left text-[11px] uppercase tracking-wider text-dim">
            <tr>
              <th className="px-3 py-2 font-medium">Started</th>
              <th className="px-3 py-2 font-medium">Item</th>
              <th className="px-3 py-2 font-medium">Model</th>
              <th className="px-3 py-2 font-medium">Turns</th>
              <th className="px-3 py-2 font-medium">Time</th>
              <th className="px-3 py-2 font-medium">Est. cost</th>
              <th className="px-3 py-2 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {(data ?? []).map((r) => (
              <tr key={r.id} className="border-t border-line hover:bg-s1">
                <td className="px-3 py-2 font-mono text-[12px] text-dim">
                  <a href={`#/runs/${r.id}`} className="hover:text-ink">
                    {fmtDateTime(r.startedAt)}
                  </a>
                </td>
                <td className="max-w-[320px] truncate px-3 py-2">
                  {r.item ? (
                    <a href={`#/item/${r.item.id}`} className="hover:text-accent-bright">
                      <span className="text-dim">{FORMAT_LABELS[r.item.format as Format] ?? r.item.format}: </span>
                      {r.item.title}
                    </a>
                  ) : (
                    "-"
                  )}
                </td>
                <td className="px-3 py-2 text-muted">{r.model}</td>
                <td className="px-3 py-2 font-mono">{r.numTurns ?? "-"}</td>
                <td className="px-3 py-2 font-mono">{r.durationMs ? `${Math.round(r.durationMs / 1000 / 60)}m ${Math.round((r.durationMs / 1000) % 60)}s` : r.live ? "live" : "-"}</td>
                <td className="px-3 py-2 font-mono text-muted">{r.costUsdEquiv != null ? `$${r.costUsdEquiv.toFixed(2)}` : "-"}</td>
                <td className="px-3 py-2">
                  <a href={`#/runs/${r.id}`}>
                    <Pill status={r.status} />
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

interface RunEvent {
  kind: "init" | "text" | "tool" | "rate_limit" | "result";
  text?: string;
  name?: string;
  detail?: string;
  apiKeySource?: string;
  cost?: number;
  turns?: number;
  ts?: string;
}

export function RunDetail({ id }: { id: string }) {
  const { data, reload } = useApi<{ run: Run; events: RunEvent[]; live: boolean }>(`/runs/${id}`, { live: false });
  const [liveEvents, setLiveEvents] = useState<RunEvent[]>([]);
  const bottom = useRef<HTMLDivElement>(null);
  const { busy, run } = useAction();
  const live = data?.live;

  useEffect(() => {
    if (!live) return;
    setLiveEvents([]);
    const es = new EventSource(`/api/runs/${id}/stream`);
    es.onmessage = (m) => setLiveEvents((prev) => [...prev, JSON.parse(m.data)]);
    es.addEventListener("end", () => {
      es.close();
      setTimeout(reload, 800);
    });
    return () => es.close();
  }, [id, live, reload]);

  useEffect(() => bottom.current?.scrollIntoView({ block: "end" }), [liveEvents.length]);

  if (!data) return <div className="text-dim">Loading...</div>;
  const events = live ? liveEvents : data.events;
  const r = data.run;
  return (
    <div className="space-y-5">
      <a href="#/runs" className="text-[12px] text-dim hover:text-ink">
        All runs
      </a>
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-[20px] font-semibold tracking-tight">Run {r.id.slice(-8)}</h1>
          <p className="text-[13px] text-dim">
            {fmtDateTime(r.startedAt)} · {r.model} · {r.numTurns ?? "?"} turns · auth {r.apiKeySource ?? "?"}
            {r.itemId && (
              <>
                {" "}
                ·{" "}
                <a href={`#/item/${r.itemId}`} className="text-accent-bright hover:underline">
                  open item
                </a>
              </>
            )}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Pill status={live ? "running" : r.status} />
          {live && (
            <Button variant="danger" busy={busy === "kill"} onClick={() => run("kill", () => api.post(`/runs/${id}/kill`, {}), "Stopping the run")}>
              Stop
            </Button>
          )}
        </div>
      </header>
      {r.error && <div className="rounded-xl border border-neg/40 bg-neg/5 px-4 py-3 text-[13px] text-neg">{r.error}</div>}
      <Card className="px-4 py-3">
        <SectionTitle>{live ? "Live" : "Transcript"}</SectionTitle>
        {events.length === 0 && <p className="text-[13px] text-dim">{live ? "Waiting for the first event..." : "No transcript recorded."}</p>}
        <ol className="space-y-2">
          {events.map((e, i) => (
            <li key={i} className="text-[13px]">
              {e.kind === "tool" && (
                <div className="font-mono text-[12px]">
                  <span className="text-accent-bright">{e.name}</span> <span className="break-all text-dim">{e.detail}</span>
                </div>
              )}
              {e.kind === "text" && <p className="whitespace-pre-wrap text-ink">{e.text}</p>}
              {e.kind === "init" && <p className="font-mono text-[12px] text-dim">session started (auth: {e.apiKeySource})</p>}
              {e.kind === "result" && (
                <p className="font-mono text-[12px] text-pos">
                  finished: {e.turns} turns{e.cost != null ? `, ~$${Number(e.cost).toFixed(2)} at API prices` : ""}
                </p>
              )}
            </li>
          ))}
        </ol>
        <div ref={bottom} />
      </Card>
    </div>
  );
}
