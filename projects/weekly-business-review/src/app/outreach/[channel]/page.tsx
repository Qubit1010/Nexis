import { notFound } from "next/navigation";
import { resolveWeek } from "@/lib/weeks";
import { delta, PLATFORM_LABEL, shortDate } from "@/lib/format";
import { NoData, PageShell } from "@/components/shell";
import { EmptyState, Icon, StatTile, StatusPill, TypeBadge, Unavailable } from "@/components/ui";

export const dynamic = "force-dynamic";

const CHANNELS = ["linkedin", "instagram", "facebook"] as const;
type Channel = (typeof CHANNELS)[number];

export default async function OutreachDetail({
  params,
  searchParams,
}: {
  params: Promise<{ channel: string }>;
  searchParams: Promise<{ week?: string }>;
}) {
  const { channel } = await params;
  if (!CHANNELS.includes(channel as Channel)) notFound();
  const { week } = await searchParams;
  const r = resolveWeek(week);
  if (!r) return <NoData />;

  const { weeks, key, snap, prev } = r;
  const v = snap.outreach.channels?.[channel];
  const pv = prev?.outreach?.channels?.[channel];
  const shell = {
    weeks,
    activeWeek: key,
    basePath: `/outreach/${channel}`,
    back: { href: `/?week=${key}`, label: "Overview" },
    section: { label: PLATFORM_LABEL[channel] ?? channel, platform: channel },
    ctx: { label: snap.label, start: snap.start, end: snap.end, generated_at: snap.generated_at },
  };

  if (!v?.available) {
    return (
      <PageShell {...shell}>
        <Unavailable reason={v?.reason ?? "Channel unavailable"} />
      </PageShell>
    );
  }

  const leads = v.leads ?? [];
  const showType = channel !== "linkedin"; // LinkedIn CRM has no Contact Type column
  const showHandle = channel === "instagram";

  return (
    <PageShell {...shell}>
      <div className="mb-6 grid grid-cols-2 gap-3 sm:max-w-[520px] sm:grid-cols-3">
        <StatTile label="Leads added" value={v.added ?? 0} delta={delta(v.added, pv?.added)} />
        <StatTile label="Outreach sent" value={v.sent ?? 0} delta={delta(v.sent, pv?.sent)} />
        {v.by_type ? (
          <StatTile label="Founder / Company" value={`${v.by_type.Founder} / ${v.by_type.Company}`} />
        ) : (
          <StatTile label="Contact type" value="—" sub="not tracked here" />
        )}
      </div>

      {leads.length === 0 ? (
        <EmptyState label="No leads added to this channel during the week." />
      ) : (
        <div className="overflow-x-auto rounded-2xl border border-[var(--border)] bg-[var(--surface-1)]">
          <table className="w-full min-w-[640px] text-left text-[13px]">
            <thead>
              <tr className="border-b border-[var(--border)] text-[11px] uppercase tracking-[0.1em] text-[var(--dim)]">
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Company</th>
                <th className="px-4 py-3 font-medium">Role</th>
                {showType && <th className="px-4 py-3 font-medium">Type</th>}
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 text-right font-medium">Added</th>
              </tr>
            </thead>
            <tbody>
              {leads.map((ld, i) => (
                <tr key={i} className="border-b border-[var(--border)] last:border-0 transition-colors hover:bg-[var(--surface-2)]">
                  <td className="px-4 py-3">
                    {ld.url ? (
                      <a
                        href={ld.url}
                        target="_blank"
                        rel="noreferrer"
                        className="group inline-flex items-center gap-1.5 font-medium text-[var(--text)] hover:text-[var(--accent-bright)]"
                      >
                        {ld.name || (showHandle && ld.handle) || "(no name)"}
                        <Icon name="external" className="h-3.5 w-3.5 text-[var(--dim)] group-hover:text-[var(--accent-bright)]" />
                      </a>
                    ) : (
                      <span className="text-[var(--muted)]">{ld.name || "(no name)"}</span>
                    )}
                    {showHandle && ld.handle && <div className="font-mono text-[11px] text-[var(--dim)]">{ld.handle}</div>}
                  </td>
                  <td className="px-4 py-3 text-[var(--muted)]">{ld.company || "—"}</td>
                  <td className="px-4 py-3 text-[var(--muted)]">{ld.role || "—"}</td>
                  {showType && (
                    <td className="px-4 py-3">
                      <TypeBadge type={ld.type} />
                    </td>
                  )}
                  <td className="px-4 py-3">
                    <StatusPill value={ld.status || "New"} />
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 text-right font-mono text-[12px] text-[var(--dim)]">{shortDate(ld.date)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <p className="mt-4 text-[12px] text-[var(--dim)]">
        Showing all {leads.length} leads added this week. Status reflects the CRM (New → Sent); replies and closes
        aren&apos;t tracked in the sheet.
      </p>
    </PageShell>
  );
}
