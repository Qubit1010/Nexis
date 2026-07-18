import { resolveWeek, type UpworkOutcome } from "@/lib/weeks";
import { delta, shortDate } from "@/lib/format";
import { NoData, PageShell } from "@/components/shell";
import { EmptyState, StatTile, StatusPill, Unavailable } from "@/components/ui";

export const dynamic = "force-dynamic";

const RANK: Record<UpworkOutcome, number> = { hired: 0, interview: 1, viewed: 2, sent: 3 };

export default async function UpworkDetail({ searchParams }: { searchParams: Promise<{ week?: string }> }) {
  const { week } = await searchParams;
  const r = resolveWeek(week);
  if (!r) return <NoData />;

  const { weeks, key, snap, prev } = r;
  const u = snap.upwork;
  const shell = {
    weeks,
    activeWeek: key,
    basePath: "/upwork",
    back: { href: `/?week=${key}`, label: "Overview" },
    section: { label: "Upwork" },
    ctx: { label: snap.label, start: snap.start, end: snap.end, generated_at: snap.generated_at },
  };

  if (!u.available) {
    return (
      <PageShell {...shell}>
        <Unavailable reason={u.reason} />
      </PageShell>
    );
  }

  const items = [...(u.items ?? [])].sort((a, b) => {
    const dr = RANK[a.outcome] - RANK[b.outcome];
    return dr !== 0 ? dr : (b.date ?? "").localeCompare(a.date ?? "");
  });

  return (
    <PageShell {...shell}>
      <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        <StatTile label="Proposals" value={u.proposals ?? 0} delta={delta(u.proposals, prev?.upwork?.proposals)} />
        <StatTile label="Connects" value={u.connects ?? 0} delta={delta(u.connects, prev?.upwork?.connects)} />
        <StatTile label="Spend" value={`$${(u.dollars ?? 0).toFixed(2)}`} sub="connects × $0.15" />
        <StatTile label="Viewed" value={u.viewed ?? 0} sub={`${u.view_rate ?? 0}% of sent`} />
        <StatTile label="Interviews" value={u.interviews ?? 0} sub={`${u.interview_rate ?? 0}%`} />
        <StatTile label="Hired" value={u.hired ?? 0} sub={`${u.hire_rate ?? 0}%`} accent={(u.hired ?? 0) > 0} />
      </div>

      {items.length === 0 ? (
        <EmptyState label="No proposals sent this week." />
      ) : (
        <div className="overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--surface-1)]">
          <table className="w-full text-left text-[13px]">
            <thead>
              <tr className="border-b border-[var(--border)] text-[11px] uppercase tracking-[0.1em] text-[var(--dim)]">
                <th className="px-4 py-3 font-medium">Date</th>
                <th className="px-4 py-3 font-medium">Job title</th>
                <th className="px-4 py-3 font-medium">Sender</th>
                <th className="px-4 py-3 text-right font-medium">Connects</th>
                <th className="px-4 py-3 font-medium">Outcome</th>
              </tr>
            </thead>
            <tbody>
              {items.map((it, i) => (
                <tr key={i} className="border-b border-[var(--border)] last:border-0 transition-colors hover:bg-[var(--surface-2)]">
                  <td className="whitespace-nowrap px-4 py-3 font-mono text-[12px] text-[var(--dim)]">{shortDate(it.date)}</td>
                  <td className="px-4 py-3 text-[var(--text)]">
                    <span className="flex items-center gap-2">
                      {it.title || <span className="text-[var(--dim)]">(untitled job)</span>}
                      {it.boosted && (
                        <span className="rounded bg-[var(--accent-soft)] px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wide text-[var(--accent-bright)]">
                          Boosted
                        </span>
                      )}
                    </span>
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 text-[var(--muted)]">{it.sender}</td>
                  <td className="px-4 py-3 text-right font-mono text-[var(--muted)]">{it.connects || "—"}</td>
                  <td className="px-4 py-3">
                    <StatusPill value={it.outcome} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {u.by_sender && Object.keys(u.by_sender).length > 1 && (
        <div className="mt-5 flex flex-wrap gap-x-5 gap-y-1.5 text-[12px] text-[var(--muted)]">
          {Object.entries(u.by_sender).map(([name, s]) => (
            <span key={name}>
              <span className="font-medium text-[var(--text)]">{name}</span>{" "}
              <span className="font-mono text-[var(--dim)]">{s.proposals} sent · {s.interviews} int · {s.hired} hired</span>
            </span>
          ))}
        </div>
      )}
    </PageShell>
  );
}
