import { useMemo, useState } from "react";
import { api, type Idea } from "../lib/api";
import { useAction, useApi } from "../lib/hooks";
import { Button, Empty, inputCls, Pill } from "../components/ui";
import { PlanDialog } from "../components/PlanDialog";
import { savedAgo, SOURCE_LABEL } from "./Inbox";

const TABS: { status: Idea["status"]; label: string; hint: string }[] = [
  { status: "shortlisted", label: "Shortlist", hint: "Your topic ideas: plan the best ones onto the calendar" },
  { status: "used", label: "Used", hint: "Already planned or written" },
  { status: "archived", label: "Archived", hint: "Passed on. Restore anything worth another look" },
  { status: "inbox", label: "Inbox", hint: "Not triaged yet" },
];

export function Ideas() {
  const [tab, setTab] = useState<Idea["status"]>("shortlisted");
  const [q, setQ] = useState("");
  const { data, reload } = useApi<Idea[]>(`/ideas?status=${tab}`);
  const [planIdea, setPlanIdea] = useState<Idea | null>(null);
  const { run } = useAction();
  const filtered = useMemo(() => {
    const s = q.toLowerCase();
    return (data ?? []).filter((i) => !s || i.title.toLowerCase().includes(s) || (i.summary || "").toLowerCase().includes(s));
  }, [data, q]);

  const set = async (i: Idea, status: Idea["status"]) => {
    await run(i.id, () => api.patch(`/ideas/${i.id}`, { status }));
    reload();
  };

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-[22px] font-semibold tracking-tight">Ideas</h1>
          <p className="text-[13px] text-dim">{TABS.find((t) => t.status === tab)?.hint}</p>
        </div>
        <input className={`${inputCls} max-w-xs`} placeholder="Search ideas" value={q} onChange={(e) => setQ(e.target.value)} />
      </header>
      <div className="flex gap-1 border-b border-line">
        {TABS.map((t) => (
          <button key={t.status} onClick={() => setTab(t.status)} className={`-mb-px border-b-2 px-3 py-2 text-[13px] ${tab === t.status ? "border-accent text-ink" : "border-transparent text-muted hover:text-ink"}`}>
            {t.label}
          </button>
        ))}
      </div>
      {data && filtered.length === 0 && <Empty>Nothing here.</Empty>}
      <div className="grid gap-2 md:grid-cols-2">
        {filtered.map((i) => {
          const payload = (() => {
            try {
              return JSON.parse(i.payloadJson || "{}");
            } catch {
              return {};
            }
          })();
          return (
            <div key={i.id} className="flex flex-col rounded-xl border border-line bg-s1 px-4 py-3">
              <div className="flex flex-wrap items-center gap-2 text-[11px] text-dim">
                <span className="rounded border border-line-strong px-1.5 py-px">{SOURCE_LABEL[i.source] ?? i.source}</span>
                {payload.category && <span>{payload.category}</span>}
                {payload.week ? <span className="font-mono">week of {payload.week}</span> : <span>{savedAgo(i)}</span>}
                <Pill status={i.status} />
              </div>
              <div className="mt-1.5 text-[14px] font-medium leading-snug">{i.title}</div>
              {i.summary && <p className="mt-1 line-clamp-3 text-[12.5px] text-muted">{i.summary}</p>}
              {i.url && (
                <a href={i.url} target="_blank" rel="noreferrer" className="mt-1 truncate text-[12px] text-accent-bright hover:underline">
                  {i.url}
                </a>
              )}
              <div className="mt-3 flex flex-wrap gap-1.5">
                {tab !== "archived" && (
                  <Button variant="quiet" onClick={() => set(i, "archived")}>
                    Archive
                  </Button>
                )}
                {tab !== "shortlisted" && <Button onClick={() => set(i, "shortlisted")}>Shortlist</Button>}
                <Button variant="primary" onClick={() => setPlanIdea(i)}>
                  Plan
                </Button>
              </div>
            </div>
          );
        })}
      </div>
      <PlanDialog open={!!planIdea} onClose={() => setPlanIdea(null)} idea={planIdea} />
    </div>
  );
}
