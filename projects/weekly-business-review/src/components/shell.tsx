import type { ReactNode } from "react";
import Link from "next/link";
import { shortDate } from "@/lib/format";
import { Icon, PlatformDot } from "@/components/ui";

/* Shared frame: brand header, week switcher (stays on the current route), and an optional
   back link + section breadcrumb for the drill-down pages. */

export function PageShell({
  weeks,
  activeWeek,
  basePath,
  ctx,
  back,
  section,
  children,
}: {
  weeks: string[];
  activeWeek: string;
  basePath: string;
  ctx: { label: string; start: string; end: string; generated_at: string };
  back?: { href: string; label: string };
  section?: { label: string; platform?: string };
  children: ReactNode;
}) {
  return (
    <div className="mx-auto max-w-5xl px-5 py-8 sm:px-8 sm:py-10">
      <header className="mb-8">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            {back && (
              <Link
                href={back.href}
                className="mb-3 inline-flex items-center gap-1.5 text-[12px] font-medium text-[var(--dim)] transition-colors hover:text-[var(--accent-bright)]"
              >
                <Icon name="arrow-left" className="h-3.5 w-3.5" />
                {back.label}
              </Link>
            )}
            <div className="flex items-center gap-3">
              <div className="brandmark flex h-9 w-9 shrink-0 items-center justify-center rounded-xl">
                <span className="text-[15px] font-bold tracking-tight text-white">N</span>
              </div>
              <div>
                <h1 className="flex items-center gap-2 text-[19px] font-semibold leading-tight tracking-tight text-[var(--text)]">
                  {section ? (
                    <>
                      <span className="text-[var(--muted)]">Weekly Review</span>
                      <span className="text-[var(--dim)]">/</span>
                      <span className="inline-flex items-center gap-1.5">
                        {section.platform && <PlatformDot platform={section.platform} />}
                        {section.label}
                      </span>
                    </>
                  ) : (
                    "Weekly Business Review"
                  )}
                </h1>
                <p className="mt-0.5 text-[12px] font-medium text-[var(--accent)]">NexusPoint</p>
              </div>
            </div>
          </div>

          <WeekSwitch weeks={weeks} activeWeek={activeWeek} basePath={basePath} />
        </div>

        <p className="mt-4 flex flex-wrap items-center gap-x-2.5 gap-y-1 text-[12px] text-[var(--muted)]">
          <Icon name="calendar" className="h-3.5 w-3.5 text-[var(--dim)]" />
          <span className="font-mono font-medium text-[var(--text)]">{ctx.label}</span>
          <span className="text-[var(--dim)]">
            {shortDate(ctx.start)} → {shortDate(ctx.end)}
          </span>
          <span className="text-[var(--border-strong)]">·</span>
          <span className="text-[var(--dim)]">generated {ctx.generated_at.replace("T", " ")}</span>
        </p>
      </header>

      {children}
    </div>
  );
}

/** Shown when a detail page can't resolve a snapshot for the requested week. */
export function NoData() {
  return (
    <div className="mx-auto max-w-4xl px-8 py-16">
      <h1 className="text-[20px] font-semibold text-[var(--text)]">No snapshot for this week</h1>
      <p className="mt-3 text-[var(--muted)]">
        Generate one with the weekly-business-review skill, then reload.{" "}
        <Link href="/" className="text-[var(--accent-bright)] hover:underline">
          Back to overview
        </Link>
      </p>
    </div>
  );
}

function WeekSwitch({ weeks, activeWeek, basePath }: { weeks: string[]; activeWeek: string; basePath: string }) {
  return (
    <nav aria-label="Select week" className="flex flex-wrap gap-1.5">
      {weeks.map((wk) => {
        const active = wk === activeWeek;
        return (
          <Link
            key={wk}
            href={`${basePath}?week=${wk}`}
            aria-current={active ? "page" : undefined}
            className={`rounded-lg border px-2.5 py-1.5 font-mono text-[12px] font-medium transition-colors ${
              active
                ? "border-[rgba(32,142,199,0.32)] bg-[var(--accent-soft)] text-[var(--accent-bright)]"
                : "border-[var(--border)] text-[var(--dim)] hover:border-[var(--border-strong)] hover:text-[var(--muted)]"
            }`}
          >
            {wk}
          </Link>
        );
      })}
    </nav>
  );
}
