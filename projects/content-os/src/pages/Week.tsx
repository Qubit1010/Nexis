import { useMemo, useState } from "react";
import { api, FORMAT_LABELS, FORMATS, type Format, type ItemSummary, type Overview } from "../lib/api";
import { addDays, atPkt, dayKey, fmtDay, fmtTime, pkt, pktClock, weekStart } from "../lib/time";
import { useAction, useApi } from "../lib/hooks";
import { Button, Card, Empty, Pill, SectionTitle } from "../components/ui";
import { PlanDialog } from "../components/PlanDialog";

const REASONS: Record<string, { label: string; tone: string; hint: string }> = {
  overdue: { label: "Overdue", tone: "text-neg", hint: "The slot passed unapproved: publish now, move it, or skip it" },
  at_risk: { label: "At risk", tone: "text-neg", hint: "Slot is close and it is not approved" },
  review: { label: "Review", tone: "text-warn", hint: "Draft waiting for you" },
  ready_to_post: { label: "Ready to post", tone: "text-warn", hint: "Paste it into LinkedIn, then mark published" },
  failed: { label: "Failed", tone: "text-neg", hint: "Open to see why and retry" },
  missed: { label: "Missed", tone: "text-neg", hint: "The PC was off past the window. Publish now or move it" },
  needs_check: { label: "Needs check", tone: "text-warn", hint: "Outcome unknown: check Buffer" },
};

export function Week() {
  const [anchor, setAnchor] = useState(() => weekStart(new Date().toISOString()));
  const to = addDays(anchor, 7);
  const items = useApi<ItemSummary[]>(`/items?from=${encodeURIComponent(anchor)}&to=${encodeURIComponent(to)}`);
  const ov = useApi<Overview>("/overview").data;
  const [plan, setPlan] = useState<{ format?: Format; day?: string } | null>(null);
  const [dragId, setDragId] = useState<string | null>(null);
  const { busy, run } = useAction();

  const days = useMemo(() => Array.from({ length: 7 }, (_, i) => dayKey(addDays(anchor, i) )), [anchor]);
  const todayKey = dayKey(new Date().toISOString());
  const scheduled = (items.data ?? []).filter((i) => i.scheduledFor && i.status !== "skipped");
  const unscheduled = (items.data ?? []).filter((i) => !i.scheduledFor && !["skipped", "published"].includes(i.status));
  const cell = (format: Format, day: string) => scheduled.filter((i) => i.format === format && dayKey(i.scheduledFor!) === day).sort((a, b) => a.scheduledFor!.localeCompare(b.scheduledFor!));
  const needDrafts = scheduled.filter((i) => i.status === "planned" && !i.currentVersionId && Date.parse(i.scheduledFor!) > Date.now());

  const move = async (id: string, day: string) => {
    const item = scheduled.find((i) => i.id === id);
    if (!item) return;
    if (dayKey(item.scheduledFor!) === day) return;
    const next = atPkt(day, pktClock(item.scheduledFor!));
    await run("move", () => api.patch(`/items/${id}`, { scheduledFor: next }), ["approved", "scheduled"].includes(item.status) ? "Moved. It was approved, so approve it again for the new slot." : "Moved");
    items.reload();
  };

  const label = `${fmtDay(anchor)} to ${fmtDay(addDays(anchor, 6))}`;
  const isThisWeek = anchor === weekStart(new Date().toISOString());

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-[22px] font-semibold tracking-tight">This week{!isThisWeek && <span className="text-muted">, {label}</span>}</h1>
          <p className="text-[13px] text-dim">{isThisWeek ? label : "Drag a card to another day to move it. Times are PKT."}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="quiet" onClick={() => setAnchor(addDays(anchor, -7))} aria-label="Previous week">
            Prev
          </Button>
          {!isThisWeek && <Button onClick={() => setAnchor(weekStart(new Date().toISOString()))}>Today</Button>}
          <Button variant="quiet" onClick={() => setAnchor(addDays(anchor, 7))} aria-label="Next week">
            Next
          </Button>
          {needDrafts.length > 0 && (
            <Button busy={busy === "bulk"} onClick={() => run("bulk", () => api.post("/items/bulk/generate", { ids: needDrafts.map((i) => i.id) }), `Queued ${needDrafts.length} draft(s)`)}>
              Draft the week ({needDrafts.length})
            </Button>
          )}
          <Button variant="primary" onClick={() => setPlan({})}>
            Plan a piece
          </Button>
        </div>
      </header>

      {!!ov?.attention.length && (
        <section>
          <SectionTitle>Needs you</SectionTitle>
          <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
            {ov.attention.slice(0, 9).map(({ reason, item }) => {
              const r = REASONS[reason] ?? { label: reason, tone: "text-muted", hint: "" };
              return (
                <a key={`${reason}-${item.id}`} href={`#/item/${item.id}`} className="group rounded-xl border border-line bg-s1 px-4 py-3 transition-colors hover:border-line-strong hover:bg-s2">
                  <div className="flex items-center justify-between gap-2 text-[11px]">
                    <span className={`font-semibold uppercase tracking-wider ${r.tone}`}>{r.label}</span>
                    <span className="text-dim">
                      {FORMAT_LABELS[item.format]} · {item.scheduledFor ? `${fmtDay(item.scheduledFor)} ${fmtTime(item.scheduledFor)}` : "unscheduled"}
                    </span>
                  </div>
                  <div className="mt-1 line-clamp-2 text-[13.5px] font-medium">{item.title}</div>
                  <div className="mt-0.5 text-[12px] text-dim">{item.error && reason !== "review" ? item.error.slice(0, 110) : r.hint}</div>
                </a>
              );
            })}
          </div>
        </section>
      )}

      <section>
        <SectionTitle>Calendar</SectionTitle>
        {items.error && <p className="text-neg">{items.error}</p>}
        <div className="overflow-x-auto rounded-xl border border-line">
          <div className="grid min-w-[980px] grid-cols-[150px_repeat(7,minmax(0,1fr))]">
            <div className="border-b border-r border-line bg-s1 px-3 py-2" />
            {days.map((d) => {
              const iso = atPkt(d, "12:00");
              return (
                <div key={d} className={`border-b border-r border-line px-3 py-2 text-[12px] last:border-r-0 ${d === todayKey ? "bg-accent-soft text-ink" : "bg-s1 text-muted"}`}>
                  <span className="font-semibold">{new Intl.DateTimeFormat("en-GB", { timeZone: "Asia/Karachi", weekday: "short" }).format(new Date(iso))}</span> <span className="font-mono">{pkt(iso).getUTCDate()}</span>
                </div>
              );
            })}
            {FORMATS.map((f) => {
              const count = scheduled.filter((i) => i.format === f).length;
              const target = ov?.cadence?.[f] ?? 0;
              return (
                <Lane key={f} format={f} count={count} target={target}>
                  {days.map((d) => (
                    <div
                      key={d}
                      onDragOver={(e) => {
                        if (dragId) e.preventDefault();
                      }}
                      onDrop={(e) => {
                        e.preventDefault();
                        const id = e.dataTransfer.getData("text/plain");
                        setDragId(null);
                        if (id) void move(id, d);
                      }}
                      className={`group relative min-h-[104px] space-y-1.5 border-b border-r border-line p-1.5 last:border-r-0 ${d === todayKey ? "bg-accent-soft/40" : ""}`}
                    >
                      {cell(f, d).map((i) => (
                        <ItemCard key={i.id} item={i} onDragStart={() => setDragId(i.id)} onDragEnd={() => setDragId(null)} />
                      ))}
                      <button
                        onClick={() => setPlan({ format: f, day: d })}
                        className="absolute bottom-1 right-1 rounded-md px-1.5 text-[16px] leading-6 text-dim opacity-0 transition-opacity hover:bg-s3 hover:text-ink focus:opacity-100 group-hover:opacity-100"
                        aria-label={`Plan a ${FORMAT_LABELS[f]} on ${d}`}
                      >
                        +
                      </button>
                    </div>
                  ))}
                </Lane>
              );
            })}
          </div>
        </div>
      </section>

      {unscheduled.length > 0 && (
        <section>
          <SectionTitle>Unscheduled</SectionTitle>
          <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {unscheduled.map((i) => (
              <ItemCard key={i.id} item={i} wide />
            ))}
          </div>
        </section>
      )}

      {items.data && scheduled.length === 0 && (
        <Empty>
          Nothing planned this week. Shortlist ideas in the <a className="text-accent-bright underline" href="#/inbox">Inbox</a>, then plan them here.
        </Empty>
      )}

      <PlanDialog open={!!plan} onClose={() => setPlan(null)} initialFormat={plan?.format} initialDay={plan?.day} />
    </div>
  );
}

function Lane({ format, count, target, children }: { format: Format; count: number; target: number; children: React.ReactNode }) {
  const short = target > 0 && count < target;
  return (
    <>
      <div className="border-b border-r border-line bg-s1 px-3 py-2.5">
        <div className="text-[13px] font-medium">{FORMAT_LABELS[format]}</div>
        {target > 0 && (
          <div className={`font-mono text-[11px] ${short ? "text-warn" : "text-pos"}`}>
            {count}/{target} this week
          </div>
        )}
      </div>
      {children}
    </>
  );
}

function ItemCard({ item, wide, onDragStart, onDragEnd }: { item: ItemSummary; wide?: boolean; onDragStart?: () => void; onDragEnd?: () => void }) {
  const draggable = !!onDragStart && !["published", "publishing"].includes(item.status);
  return (
    <a
      href={`#/item/${item.id}`}
      draggable={draggable}
      onDragStart={(e) => {
        e.dataTransfer.setData("text/plain", item.id);
        e.dataTransfer.effectAllowed = "move";
        onDragStart?.();
      }}
      onDragEnd={onDragEnd}
      className={`block rounded-lg border border-line bg-s2 px-2 py-1.5 transition-colors hover:border-line-strong hover:bg-s3 ${draggable ? "cursor-grab active:cursor-grabbing" : ""}`}
      title={item.title}
    >
      <div className="flex flex-wrap items-center justify-between gap-x-1 gap-y-0.5">
        <span className="whitespace-nowrap font-mono text-[11px] text-dim">{item.scheduledFor ? fmtTime(item.scheduledFor).replace(/\s?(AM|PM)$/, (m) => m.trim().toLowerCase()) : wide ? FORMAT_LABELS[item.format] : ""}</span>
        <Pill status={item.status} />
      </div>
      <div className={`mt-0.5 text-[12.5px] font-medium leading-snug ${wide ? "line-clamp-2" : "line-clamp-3"}`}>{item.title}</div>
      {item.version && (item.version.fails > 0 || item.version.status === "blocked") && (
        <div className="mt-0.5 text-[11px] text-warn">{item.version.status === "blocked" ? "gate blocked" : `${item.version.fails} check fail${item.version.fails > 1 ? "s" : ""}`}</div>
      )}
    </a>
  );
}
