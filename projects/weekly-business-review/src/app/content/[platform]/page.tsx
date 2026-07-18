import { notFound } from "next/navigation";
import { resolveWeek } from "@/lib/weeks";
import { num, PLATFORM_LABEL, shortDate } from "@/lib/format";
import { NoData, PageShell } from "@/components/shell";
import { EmptyState, Icon, StatTile, Unavailable } from "@/components/ui";

export const dynamic = "force-dynamic";

const PLATFORMS = ["instagram", "facebook", "linkedin"] as const;
type Platform = (typeof PLATFORMS)[number];

export default async function ContentDetail({
  params,
  searchParams,
}: {
  params: Promise<{ platform: string }>;
  searchParams: Promise<{ week?: string }>;
}) {
  const { platform } = await params;
  if (!PLATFORMS.includes(platform as Platform)) notFound();
  const { week } = await searchParams;
  const r = resolveWeek(week);
  if (!r) return <NoData />;

  const { weeks, key, snap } = r;
  const c = snap.content;
  const pv = c.platforms?.[platform];
  const shell = {
    weeks,
    activeWeek: key,
    basePath: `/content/${platform}`,
    back: { href: `/?week=${key}`, label: "Overview" },
    section: { label: PLATFORM_LABEL[platform] ?? platform, platform },
    ctx: { label: snap.label, start: snap.start, end: snap.end, generated_at: snap.generated_at },
  };

  if (!c.available || !pv) {
    return (
      <PageShell {...shell}>
        <Unavailable reason={c.reason ?? "No content for this platform this week"} />
      </PageShell>
    );
  }

  const posts = (c.posts ?? []).filter((p) => p.platform === platform);
  const metricEntries = Object.entries(pv.metrics).filter(([k]) => k !== "Eng. Rate");

  return (
    <PageShell {...shell}>
      {/* Platform totals */}
      <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
        <StatTile label="Posts" value={pv.posts} />
        <StatTile label="Eng. rate" value={`${pv.metrics["Eng. Rate"] ?? 0}%`} accent />
        {metricEntries.slice(0, 6).map(([k, val]) => (
          <StatTile key={k} label={k} value={num(val)} />
        ))}
      </div>

      {posts.length === 0 ? (
        <EmptyState label="No posts published to this platform this week." />
      ) : (
        <ul className="flex flex-col gap-3">
          {posts.map((post, i) => (
            <li key={i} className="rounded-2xl border border-[var(--border)] bg-[var(--surface-1)] p-4 sm:p-5">
              <div className="mb-3 flex items-center justify-between gap-3">
                <span className="font-mono text-[12px] text-[var(--dim)]">{shortDate(post.sentAt)}</span>
                {post.link && (
                  <a
                    href={post.link}
                    target="_blank"
                    rel="noreferrer"
                    className="group inline-flex items-center gap-1.5 text-[12px] font-medium text-[var(--muted)] hover:text-[var(--accent-bright)]"
                  >
                    View post
                    <Icon name="external" className="h-3.5 w-3.5" />
                  </a>
                )}
              </div>
              <p className="text-[13px] leading-relaxed text-[var(--text)]" style={{ textWrap: "pretty" }}>
                {post.text?.trim() || "(no caption)"}
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                {Object.entries(post.metrics)
                  .filter(([k]) => k !== "Eng. Rate")
                  .map(([k, val]) => (
                    <span
                      key={k}
                      className="inline-flex items-baseline gap-1.5 rounded-lg border border-[var(--border)] bg-[var(--surface-2)] px-2.5 py-1 text-[12px]"
                    >
                      <span className="text-[var(--dim)]">{k}</span>
                      <span className="font-mono font-semibold text-[var(--text)]">{num(val)}</span>
                    </span>
                  ))}
                <span className="inline-flex items-baseline gap-1.5 rounded-lg border border-[rgba(32,142,199,0.28)] bg-[var(--accent-soft)] px-2.5 py-1 text-[12px]">
                  <span className="text-[var(--accent)]">Eng.</span>
                  <span className="font-mono font-semibold text-[var(--accent-bright)]">{num(post.metrics["Eng. Rate"] ?? 0)}%</span>
                </span>
              </div>
            </li>
          ))}
        </ul>
      )}

      <p className="mt-4 text-[12px] text-[var(--dim)]">
        Metrics are Buffer&apos;s at snapshot time. Engagement keeps accruing after posting — re-run{" "}
        <code className="font-mono text-[var(--muted)]">wbr.py --week {key}</code> to refresh.
      </p>
    </PageShell>
  );
}
