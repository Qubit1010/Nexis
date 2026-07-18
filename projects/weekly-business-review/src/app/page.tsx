import Link from "next/link";
import { resolveWeek } from "@/lib/weeks";
import { delta, num } from "@/lib/format";
import { PageShell } from "@/components/shell";
import { Icon, LinkTile, PlatformBadge, SectionCard, StatTile, Unavailable } from "@/components/ui";

export const dynamic = "force-dynamic";

/* Metrics to surface on each content platform tile (in priority order). */
const CONTENT_HEADLINE: Record<string, string[]> = {
  instagram: ["Views", "Reach", "Reactions"],
  facebook: ["Impressions", "Reactions", "Shares"],
  linkedin: ["Impressions", "Reach", "Reactions"],
};

export default async function Page({ searchParams }: { searchParams: Promise<{ week?: string }> }) {
  const { week } = await searchParams;
  const r = resolveWeek(week);

  if (!r) {
    return (
      <div className="mx-auto max-w-4xl px-8 py-16">
        <h1 className="text-[22px] font-semibold text-[var(--text)]">Weekly Business Review</h1>
        <p className="mt-4 text-[var(--muted)]">
          No snapshots yet. Run{" "}
          <code className="rounded bg-[var(--surface-2)] px-1.5 py-0.5 font-mono text-[12px] text-[var(--accent-bright)]">
            python .claude/skills/weekly-business-review/scripts/wbr.py
          </code>{" "}
          to generate the current week.
        </p>
      </div>
    );
  }

  const { weeks, key, snap, prev } = r;
  const wk = `?week=${key}`;
  const u = snap.upwork;
  const o = snap.outreach;
  const c = snap.content;
  const p = snap.productivity;
  const w = snap.website;

  return (
    <PageShell
      weeks={weeks}
      activeWeek={key}
      basePath="/"
      ctx={{ label: snap.label, start: snap.start, end: snap.end, generated_at: snap.generated_at }}
    >
      <div className="flex flex-col gap-5">
        {/* ---- Upwork ---- */}
        <SectionCard
          title="Upwork"
          subtitle="Proposals Timeline"
          action={u.available ? { href: `/upwork${wk}`, label: `${u.proposals ?? 0} proposals` } : undefined}
        >
          {u.available ? (
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
              <StatTile label="Proposals" value={u.proposals ?? 0} delta={delta(u.proposals, prev?.upwork?.proposals)} />
              <StatTile label="Connects" value={u.connects ?? 0} delta={delta(u.connects, prev?.upwork?.connects)} />
              <StatTile label="Spend" value={`$${(u.dollars ?? 0).toFixed(2)}`} sub="connects × $0.15" />
              <StatTile label="Viewed" value={u.viewed ?? 0} sub={`${u.view_rate ?? 0}% of sent`} />
              <StatTile label="Interviews" value={u.interviews ?? 0} sub={`${u.interview_rate ?? 0}%`} delta={delta(u.interviews, prev?.upwork?.interviews)} />
              <StatTile label="Hired" value={u.hired ?? 0} sub={`${u.hire_rate ?? 0}%`} accent={(u.hired ?? 0) > 0} delta={delta(u.hired, prev?.upwork?.hired)} />
            </div>
          ) : (
            <Unavailable reason={u.reason} />
          )}
        </SectionCard>

        {/* ---- Outreach ---- */}
        <SectionCard title="Outreach" subtitle="LinkedIn · Instagram · Facebook CRMs">
          {o.available && o.channels ? (
            <>
              <div className="mb-4 grid grid-cols-2 gap-3 sm:max-w-[340px]">
                <StatTile label="Leads added" value={o.totals?.added ?? 0} delta={delta(o.totals?.added, prev?.outreach?.totals?.added)} />
                <StatTile label="Outreach sent" value={o.totals?.sent ?? 0} delta={delta(o.totals?.sent, prev?.outreach?.totals?.sent)} />
              </div>
              <div className="grid gap-3 sm:grid-cols-3">
                {(["linkedin", "instagram", "facebook"] as const).map((ch) => {
                  const v = o.channels?.[ch];
                  if (!v?.available) return null;
                  return (
                    <LinkTile key={ch} href={`/outreach/${ch}${wk}`}>
                      <div className="mb-3 flex items-center justify-between">
                        <PlatformBadge platform={ch} />
                        <Icon name="arrow-right" className="h-4 w-4 text-[var(--dim)] transition-transform group-hover:translate-x-0.5 group-hover:text-[var(--accent-bright)]" />
                      </div>
                      <div className="flex items-baseline gap-2">
                        <span className="font-mono text-[24px] font-semibold text-[var(--text)]">{num(v.added ?? 0)}</span>
                        <span className="text-[12px] text-[var(--dim)]">added</span>
                      </div>
                      <div className="mt-1.5 flex items-center gap-2 text-[12px] text-[var(--muted)]">
                        <span className="font-mono">{v.sent ?? 0} sent</span>
                        {v.by_type && (
                          <>
                            <span className="text-[var(--border-strong)]">·</span>
                            <span className="font-mono">{v.by_type.Founder}F / {v.by_type.Company}C</span>
                          </>
                        )}
                      </div>
                    </LinkTile>
                  );
                })}
              </div>
              <p className="mt-4 text-[12px] text-[var(--dim)]">
                CRMs track New → Sent only; replies and closes aren&apos;t recorded in the sheets yet.
              </p>
            </>
          ) : (
            <Unavailable reason={o.reason} />
          )}
        </SectionCard>

        {/* ---- Content ---- */}
        <SectionCard
          title="Content"
          subtitle={`${c.totals?.posts ?? 0} posts via Buffer`}
        >
          {c.available && c.platforms ? (
            <div className="grid gap-3 sm:grid-cols-3">
              {(["instagram", "facebook", "linkedin"] as const).map((plat) => {
                const pv = c.platforms?.[plat];
                if (!pv) return null;
                const keys = CONTENT_HEADLINE[plat] ?? Object.keys(pv.metrics).slice(0, 3);
                return (
                  <LinkTile key={plat} href={`/content/${plat}${wk}`}>
                    <div className="mb-3 flex items-center justify-between">
                      <PlatformBadge platform={plat} />
                      <span className="flex items-center gap-2 text-[12px] text-[var(--dim)]">
                        {pv.posts} post{pv.posts === 1 ? "" : "s"}
                        <Icon name="arrow-right" className="h-4 w-4 transition-transform group-hover:translate-x-0.5 group-hover:text-[var(--accent-bright)]" />
                      </span>
                    </div>
                    <dl className="flex flex-col gap-1.5">
                      {keys.map((k) => (
                        <div key={k} className="flex items-baseline justify-between gap-2">
                          <dt className="text-[12px] text-[var(--muted)]">{k}</dt>
                          <dd className="font-mono text-[15px] font-semibold text-[var(--text)]">{num(pv.metrics[k] ?? 0)}</dd>
                        </div>
                      ))}
                      <div className="mt-1 flex items-baseline justify-between gap-2 border-t border-[var(--border)] pt-1.5">
                        <dt className="text-[12px] text-[var(--dim)]">Eng. rate</dt>
                        <dd className="font-mono text-[13px] font-medium text-[var(--accent-bright)]">{pv.metrics["Eng. Rate"] ?? 0}%</dd>
                      </div>
                    </dl>
                  </LinkTile>
                );
              })}
            </div>
          ) : (
            <Unavailable reason={c.reason} />
          )}
        </SectionCard>

        {/* ---- Productivity ---- */}
        <SectionCard
          title="Productivity"
          subtitle="ProductivityHub"
          action={p.available ? { href: `/productivity${wk}`, label: `${p.completed ?? 0} tasks` } : undefined}
        >
          {p.available ? (
            <>
              <div className="grid grid-cols-2 gap-3 sm:max-w-[340px]">
                <StatTile label="Tasks done" value={p.completed ?? 0} delta={delta(p.completed, prev?.productivity?.completed)} />
                <StatTile label="Focused" value={`${p.hours ?? 0}h`} delta={delta(p.hours, prev?.productivity?.hours)} />
              </div>
              {p.by_category && Object.keys(p.by_category).length > 0 && (
                <div className="mt-4 flex flex-wrap gap-x-4 gap-y-1.5 text-[12px]">
                  {Object.entries(p.by_category).map(([cat, n]) => (
                    <span key={cat} className="text-[var(--muted)]">
                      <span className="font-medium text-[var(--text)]">{cat}</span>{" "}
                      <span className="font-mono text-[var(--dim)]">{n}</span>
                    </span>
                  ))}
                </div>
              )}
            </>
          ) : (
            <Unavailable reason={p.reason} hint={p.setup} />
          )}
        </SectionCard>

        {/* ---- Website ---- */}
        <SectionCard title="Website" subtitle="nexus-point.co + personal site">
          <Unavailable reason={w.reason} hint="Phase 2" />
          {w.planned && (
            <ul className="mt-3 grid gap-1.5 text-[12px] text-[var(--dim)] sm:grid-cols-3">
              {w.planned.map((line) => (
                <li key={line} className="flex items-start gap-2">
                  <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-[var(--border-strong)]" />
                  {line}
                </li>
              ))}
            </ul>
          )}
        </SectionCard>
      </div>

      <footer className="mt-8 flex items-center justify-between border-t border-[var(--border)] pt-5 text-[12px] text-[var(--dim)]">
        <span>NexusPoint · Weekly Business Review</span>
        <Link href="/" className="hover:text-[var(--muted)]">
          Refresh with <code className="font-mono text-[var(--muted)]">wbr.py</code>
        </Link>
      </footer>
    </PageShell>
  );
}
