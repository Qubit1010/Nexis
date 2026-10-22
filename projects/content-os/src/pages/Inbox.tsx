import { useEffect, useMemo, useState } from "react";
import { api, type Idea } from "../lib/api";
import { ago } from "../lib/time";
import { useAction, useApi } from "../lib/hooks";
import { Button, Empty, Kbd, SectionTitle } from "../components/ui";
import { PlanDialog } from "../components/PlanDialog";

/** When it was actually saved: imported ideas carry the sheet's date, not the import time. */
export function savedAgo(i: Idea): string {
  try {
    const p = JSON.parse(i.payloadJson || "{}");
    const d = p.dateSaved || p.briefDate;
    if (typeof d === "string" && /^\d{4}-\d{2}-\d{2}/.test(d)) return `saved ${d.slice(0, 10)}`;
  } catch {
    /* fall through */
  }
  return ago(i.createdAt);
}

export const SOURCE_LABEL: Record<string, string> = {
  youtube_topic: "YouTube topic",
  youtube_video: "YouTube video",
  youtube_idea: "YouTube idea",
  news_article: "News",
  practical_idea: "Practical AI",
  topics_sheet: "Topics sheet",
  manual: "Manual",
};

/**
 * Triage: everything bookmarked in the brief lands here. Shortlist the ones worth
 * writing (they become the "topic ideas"), archive the rest, or plan one straight
 * onto the calendar. Keyboard: j/k move, s shortlist, a archive, p plan.
 */
export function Inbox() {
  const { data, reload } = useApi<Idea[]>("/ideas?status=inbox");
  const [source, setSource] = useState<string>("all");
  const [cursor, setCursor] = useState(0);
  const [planIdea, setPlanIdea] = useState<Idea | null>(null);
  const [adding, setAdding] = useState("");
  const { busy, run } = useAction();

  const ideas = useMemo(() => (data ?? []).filter((i) => source === "all" || i.source === source), [data, source]);
  const sources = useMemo(() => [...new Set((data ?? []).map((i) => i.source))], [data]);
  const current = ideas[Math.min(cursor, ideas.length - 1)];

  const setStatus = async (idea: Idea, status: Idea["status"]) => {
    await run(`s-${idea.id}`, () => api.patch(`/ideas/${idea.id}`, { status }));
    reload();
  };

  useEffect(() => {
    const on = (e: KeyboardEvent) => {
      if (planIdea || (e.target as HTMLElement)?.closest("input,textarea,select")) return;
      if (e.key === "j") setCursor((c) => Math.min(c + 1, ideas.length - 1));
      else if (e.key === "k") setCursor((c) => Math.max(c - 1, 0));
      else if (current && e.key === "s") void setStatus(current, "shortlisted");
      else if (current && e.key === "a") void setStatus(current, "archived");
      else if (current && e.key === "p") setPlanIdea(current);
      else return;
      e.preventDefault();
    };
    addEventListener("keydown", on);
    return () => removeEventListener("keydown", on);
  });

  const addManual = async () => {
    if (!adding.trim()) return;
    await run("add", () => api.post("/ideas", { title: adding.trim(), source: "manual" }), "Added to the inbox");
    setAdding("");
    reload();
  };

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-[22px] font-semibold tracking-tight">Inbox</h1>
          <p className="text-[13px] text-dim">
            Bookmarks from the daily brief land here. <Kbd>j</Kbd> <Kbd>k</Kbd> move, <Kbd>s</Kbd> shortlist, <Kbd>a</Kbd> archive, <Kbd>p</Kbd> plan.
          </p>
        </div>
        <form
          className="flex gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            void addManual();
          }}
        >
          <input value={adding} onChange={(e) => setAdding(e.target.value)} placeholder="Add an idea by hand" className="w-64 rounded-lg border border-line-strong bg-s2 px-3 py-1.5 text-[13px] placeholder:text-dim focus:border-accent focus:outline-none" />
          <Button busy={busy === "add"} type="submit">
            Add
          </Button>
        </form>
      </header>

      <div className="flex flex-wrap gap-1.5">
        {["all", ...sources].map((s) => (
          <button
            key={s}
            onClick={() => {
              setSource(s);
              setCursor(0);
            }}
            className={`rounded-full border px-3 py-1 text-[12px] ${source === s ? "border-accent bg-accent-soft text-accent-bright" : "border-line-strong text-muted hover:text-ink"}`}
          >
            {s === "all" ? `All (${data?.length ?? 0})` : `${SOURCE_LABEL[s] ?? s} (${(data ?? []).filter((i) => i.source === s).length})`}
          </button>
        ))}
      </div>

      {data && ideas.length === 0 && <Empty>Inbox zero. New bookmarks from the brief show up here live.</Empty>}

      {!data && <p className="text-[13px] text-dim">Loading...</p>}
      {data && ideas.length > 0 && <SectionTitle>{ideas.length} to triage</SectionTitle>}
      <ul className="space-y-1.5">
        {ideas.map((i, idx) => (
          <li
            key={i.id}
            onClick={() => setCursor(idx)}
            className={`rounded-xl border px-4 py-3 transition-colors ${idx === cursor ? "border-accent/50 bg-s2" : "border-line bg-s1 hover:border-line-strong"}`}
          >
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2 text-[11px] text-dim">
                  <span className="rounded border border-line-strong px-1.5 py-px">{SOURCE_LABEL[i.source] ?? i.source}</span>
                  <span>{savedAgo(i)}</span>
                  {i.seenCount > 1 && <span className="text-warn">saved {i.seenCount}x</span>}
                </div>
                <div className="mt-1 text-[14px] font-medium leading-snug">{i.title}</div>
                {i.summary && <p className="mt-1 line-clamp-2 text-[12.5px] text-muted">{i.summary}</p>}
                {i.url && (
                  <a href={i.url} target="_blank" rel="noreferrer" className="mt-1 inline-block max-w-full truncate text-[12px] text-accent-bright hover:underline" onClick={(e) => e.stopPropagation()}>
                    {i.url}
                  </a>
                )}
              </div>
              <div className="flex shrink-0 gap-1.5">
                <Button variant="quiet" busy={busy === `s-${i.id}`} onClick={() => setStatus(i, "archived")}>
                  Archive
                </Button>
                <Button onClick={() => setStatus(i, "shortlisted")}>Shortlist</Button>
                <Button variant="primary" onClick={() => setPlanIdea(i)}>
                  Plan
                </Button>
              </div>
            </div>
          </li>
        ))}
      </ul>
      <PlanDialog open={!!planIdea} onClose={() => setPlanIdea(null)} idea={planIdea} />
    </div>
  );
}
