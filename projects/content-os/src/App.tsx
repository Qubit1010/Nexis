import type { ReactNode } from "react";
import type { Overview } from "./lib/api";
import { toast, useApi, useConnected, useLiveEvents, useRoute, useToasts } from "./lib/hooks";
import { Week } from "./pages/Week";
import { Inbox } from "./pages/Inbox";
import { Ideas } from "./pages/Ideas";
import { ItemPage } from "./pages/Item";
import { Runs, RunDetail } from "./pages/Runs";
import { Automations } from "./pages/Automations";
import { Settings } from "./pages/Settings";

const NAV: { path: string; label: string; key?: keyof Pick<Overview, "inbox"> | "attention" }[] = [
  { path: "", label: "Week", key: "attention" },
  { path: "inbox", label: "Inbox", key: "inbox" },
  { path: "ideas", label: "Ideas" },
  { path: "runs", label: "Runs" },
  { path: "automations", label: "Automations" },
  { path: "settings", label: "Settings" },
];

function Shell({ children }: { children: ReactNode }) {
  const route = useRoute();
  const ov = useApi<Overview>("/overview").data;
  const connected = useConnected();
  const current = route[0] === "item" ? "" : route[0] ?? "";
  const util = ov?.rateLimit?.sevenDayUtilization;

  useLiveEvents((e) => {
    if (e.type === "generation.done") toast(e.data?.status === "blocked" ? "Draft ready (blocked by the gate, check the rescue)" : "Draft ready for review", e.data?.fails ? "err" : "ok", `#/item/${e.entityId}`);
    else if (e.type === "item.published" && e.actor !== "user") toast(`Published${e.data?.url ? `: ${e.data.url}` : ""}`, "ok", `#/item/${e.entityId}`);
    else if (e.type === "newsletter.ready") toast(`Newsletter ready to post: ${e.data?.title ?? ""}`, "info", `#/item/${e.entityId}`);
    else if (e.type === "job.failed") toast(`Job failed (${e.data?.type}): ${String(e.data?.error ?? "").slice(0, 140)}`, "err", e.data?.itemId ? `#/item/${e.data.itemId}` : undefined);
    else if (e.type === "buffer.scheduled") toast("Scheduled in Buffer", "ok", `#/item/${e.entityId}`);
    else if (e.type === "automation.caught_up") toast(`Caught up a missed run (${e.data?.lateMin} min late)`, "info");
  });

  return (
    <div className="min-h-screen md:grid md:grid-cols-[208px_1fr]">
      <aside className="border-b border-line bg-s1/60 md:sticky md:top-0 md:h-screen md:border-b-0 md:border-r">
        <div className="flex items-center gap-2.5 px-4 py-4">
          <div className="grid size-8 place-items-center rounded-lg bg-accent font-mono text-[13px] font-bold text-bg">C</div>
          <div>
            <div className="text-[14px] font-semibold leading-tight">Content OS</div>
            <div className="flex items-center gap-1.5 text-[11px] text-dim">
              <span className={`size-1.5 rounded-full ${connected ? "bg-pos" : "bg-neg"}`} />
              {connected ? "live" : "reconnecting"}
            </div>
          </div>
        </div>
        <nav className="flex gap-1 overflow-x-auto px-2 pb-2 md:block md:space-y-0.5 md:overflow-visible">
          {NAV.map((n) => {
            const count = n.key === "inbox" ? ov?.inbox : n.key === "attention" ? ov?.attention.length : undefined;
            const active = current === n.path;
            return (
              <a
                key={n.path}
                href={`#/${n.path}`}
                className={`flex shrink-0 items-center justify-between gap-3 rounded-lg px-3 py-2 text-[13px] transition-colors ${active ? "bg-s3 text-ink" : "text-muted hover:bg-s2 hover:text-ink"}`}
              >
                {n.label}
                {!!count && <span className={`rounded-full px-1.5 font-mono text-[11px] ${n.key === "attention" ? "bg-warn/15 text-warn" : "bg-accent-soft text-accent-bright"}`}>{count}</span>}
              </a>
            );
          })}
        </nav>
        <div className="hidden space-y-2 px-4 pt-4 text-[11px] text-dim md:block">
          <div className="flex justify-between">
            <span>Claude lane</span>
            <span className="font-mono text-muted">{ov ? `${ov.lanes.running.claude}/${ov.lanes.capacity.claude}` : "-"}</span>
          </div>
          <div className="flex justify-between">
            <span>Queued jobs</span>
            <span className="font-mono text-muted">{ov?.jobs.queued ?? "-"}</span>
          </div>
          {!!ov?.jobs.needsCheck && (
            <a href="#/settings" className="flex justify-between text-warn">
              <span>Needs check</span>
              <span className="font-mono">{ov.jobs.needsCheck}</span>
            </a>
          )}
          {util != null && (
            <div>
              <div className="flex justify-between">
                <span>Plan usage (7d)</span>
                <span className="font-mono text-muted">{Math.round(util * 100)}%</span>
              </div>
              <div className="mt-1 h-1 overflow-hidden rounded-full bg-s3">
                <div className={`h-full ${util > 0.85 ? "bg-neg" : util > 0.6 ? "bg-warn" : "bg-accent"}`} style={{ width: `${Math.min(100, util * 100)}%` }} />
              </div>
            </div>
          )}
        </div>
      </aside>
      <main className="min-w-0 px-4 py-5 md:px-8 md:py-7">{children}</main>
      <Toasts />
    </div>
  );
}

function Toasts() {
  const toasts = useToasts();
  return (
    <div className="pointer-events-none fixed bottom-4 right-4 z-50 flex w-[min(380px,calc(100vw-2rem))] flex-col gap-2" aria-live="polite">
      {toasts.map((t) => {
        const cls = t.kind === "err" ? "border-neg/40" : t.kind === "ok" ? "border-pos/40" : "border-line-strong";
        const body = <div className={`pointer-events-auto rounded-lg border bg-s2 px-3.5 py-2.5 text-[13px] shadow-xl ${cls}`}>{t.text}</div>;
        return t.href ? (
          <a key={t.id} href={t.href}>
            {body}
          </a>
        ) : (
          <div key={t.id}>{body}</div>
        );
      })}
    </div>
  );
}

export function App() {
  const route = useRoute();
  const [page, arg] = route;
  let content: ReactNode;
  if (page === "inbox") content = <Inbox />;
  else if (page === "ideas") content = <Ideas />;
  else if (page === "item" && arg) content = <ItemPage id={arg} />;
  else if (page === "runs" && arg) content = <RunDetail id={arg} />;
  else if (page === "runs") content = <Runs />;
  else if (page === "automations") content = <Automations />;
  else if (page === "settings") content = <Settings />;
  else content = <Week />;
  return <Shell>{content}</Shell>;
}
