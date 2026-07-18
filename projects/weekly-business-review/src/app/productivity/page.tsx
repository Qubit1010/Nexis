import { resolveWeek } from "@/lib/weeks";
import { delta, hoursMins, shortDate, weekday } from "@/lib/format";
import { NoData, PageShell } from "@/components/shell";
import { EmptyState, StatTile, Unavailable } from "@/components/ui";

export const dynamic = "force-dynamic";

export default async function ProductivityDetail({ searchParams }: { searchParams: Promise<{ week?: string }> }) {
  const { week } = await searchParams;
  const r = resolveWeek(week);
  if (!r) return <NoData />;

  const { weeks, key, snap, prev } = r;
  const p = snap.productivity;
  const shell = {
    weeks,
    activeWeek: key,
    basePath: "/productivity",
    back: { href: `/?week=${key}`, label: "Overview" },
    section: { label: "Productivity" },
    ctx: { label: snap.label, start: snap.start, end: snap.end, generated_at: snap.generated_at },
  };

  if (!p.available) {
    return (
      <PageShell {...shell}>
        <Unavailable reason={p.reason} hint={p.setup} />
      </PageShell>
    );
  }

  const cats = Object.entries(p.by_category ?? {});
  const maxCat = Math.max(1, ...cats.map(([, n]) => n));
  const tasks = p.tasks ?? [];

  return (
    <PageShell {...shell}>
      <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
        {/* Left: totals + category breakdown */}
        <div className="flex flex-col gap-6">
          <div className="grid grid-cols-2 gap-3">
            <StatTile label="Tasks done" value={p.completed ?? 0} delta={delta(p.completed, prev?.productivity?.completed)} />
            <StatTile label="Focused" value={`${p.hours ?? 0}h`} delta={delta(p.hours, prev?.productivity?.hours)} />
          </div>

          {cats.length > 0 && (
            <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface-1)] p-5">
              <h3 className="mb-4 text-[11px] font-medium uppercase tracking-[0.1em] text-[var(--dim)]">By category</h3>
              <ul className="flex flex-col gap-2.5">
                {cats.map(([cat, n]) => (
                  <li key={cat} className="grid grid-cols-[1fr_auto] items-center gap-3">
                    <div>
                      <div className="mb-1 flex items-baseline justify-between">
                        <span className="text-[13px] text-[var(--text)]">{cat}</span>
                        <span className="font-mono text-[12px] text-[var(--dim)]">{n}</span>
                      </div>
                      <div className="h-1.5 overflow-hidden rounded-full bg-[var(--surface-3)]">
                        <div
                          className="h-full rounded-full bg-[var(--accent)]"
                          style={{ width: `${Math.round((n / maxCat) * 1000) / 10}%` }}
                        />
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Right: full task log, grouped by day */}
        <div>
          {tasks.length === 0 ? (
            <EmptyState label="No tasks completed this week." />
          ) : (
            <div className="overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--surface-1)]">
              <table className="w-full text-left text-[13px]">
                <thead>
                  <tr className="border-b border-[var(--border)] text-[11px] uppercase tracking-[0.1em] text-[var(--dim)]">
                    <th className="px-4 py-3 font-medium">Day</th>
                    <th className="px-4 py-3 font-medium">Task</th>
                    <th className="px-4 py-3 font-medium">Category</th>
                    <th className="px-4 py-3 text-right font-medium">Time</th>
                  </tr>
                </thead>
                <tbody>
                  {tasks.map((t, i) => (
                    <tr key={i} className="border-b border-[var(--border)] last:border-0 transition-colors hover:bg-[var(--surface-2)]">
                      <td className="whitespace-nowrap px-4 py-2.5">
                        <span className="font-mono text-[12px] text-[var(--muted)]">{weekday(t.completed_at)}</span>{" "}
                        <span className="font-mono text-[11px] text-[var(--dim)]">{shortDate(t.completed_at)}</span>
                      </td>
                      <td className="px-4 py-2.5 text-[var(--text)]">{t.title || "(untitled)"}</td>
                      <td className="whitespace-nowrap px-4 py-2.5 text-[12px] text-[var(--muted)]">{t.category}</td>
                      <td className="whitespace-nowrap px-4 py-2.5 text-right font-mono text-[12px] text-[var(--dim)]">
                        {hoursMins(t.minutes)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </PageShell>
  );
}
