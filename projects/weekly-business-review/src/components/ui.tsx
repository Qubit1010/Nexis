import type { ReactNode } from "react";
import Link from "next/link";
import { num } from "@/lib/format";

/* One presentational kit for the whole app. Custom inline icons (single 1.75 stroke),
   cool-slate surfaces, one blue accent. All numbers render in the mono/tabular face. */

/* ----------------------------- icons ----------------------------- */

type IconName = "arrow-right" | "arrow-left" | "up" | "down" | "external" | "calendar";

export function Icon({ name, className = "h-4 w-4" }: { name: IconName; className?: string }) {
  const p: Record<IconName, ReactNode> = {
    "arrow-right": <path d="M5 12h14M13 6l6 6-6 6" />,
    "arrow-left": <path d="M19 12H5M11 18l-6-6 6-6" />,
    up: <path d="M6 15l6-6 6 6" />,
    down: <path d="M6 9l6 6 6-6" />,
    external: <path d="M14 5h5v5M19 5l-8 8M11 5H7a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-4" />,
    calendar: <path d="M7 3v3M17 3v3M4 8h16M5 5h14a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1Z" />,
  };
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden
    >
      {p[name]}
    </svg>
  );
}

/* ----------------------------- cards ----------------------------- */

export function SectionCard({
  title,
  subtitle,
  action,
  children,
}: {
  title: string;
  subtitle?: string;
  action?: { href: string; label: string };
  children: ReactNode;
}) {
  return (
    <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface-1)] p-5 sm:p-6 shadow-[0_1px_2px_rgba(0,0,0,0.4)]">
      <header className="mb-5 flex items-center justify-between gap-3">
        <div className="flex items-baseline gap-3">
          <h2 className="text-[15px] font-semibold tracking-tight text-[var(--text)]">{title}</h2>
          {subtitle && <p className="hidden text-[12px] text-[var(--dim)] sm:block">{subtitle}</p>}
        </div>
        {action && (
          <Link
            href={action.href}
            className="group inline-flex items-center gap-1.5 rounded-lg border border-[var(--border)] px-2.5 py-1 text-[12px] font-medium text-[var(--muted)] transition-colors hover:border-[var(--border-strong)] hover:bg-[var(--accent-soft)] hover:text-[var(--accent-bright)]"
          >
            {action.label}
            <Icon name="arrow-right" className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
          </Link>
        )}
      </header>
      {children}
    </section>
  );
}

/** A whole-card clickable tile with tactile hover/press. Used for the drill-in rows/tiles. */
export function LinkTile({ href, children }: { href: string; children: ReactNode }) {
  return (
    <Link
      href={href}
      className="group block rounded-xl border border-[var(--border)] bg-[var(--surface-2)] p-4 transition-all duration-200 hover:-translate-y-0.5 hover:border-[var(--border-strong)] hover:bg-[var(--surface-3)] hover:shadow-[0_10px_30px_-12px_rgba(32,142,199,0.35)] active:translate-y-0"
    >
      {children}
    </Link>
  );
}

/* ----------------------------- stats ----------------------------- */

export function Delta({ value, suffix = "" }: { value: number | null; suffix?: string }) {
  if (value === null || value === 0) return null;
  const up = value > 0;
  return (
    <span
      className={`inline-flex items-center gap-0.5 font-mono text-[12px] font-medium ${up ? "text-[var(--pos)]" : "text-[var(--neg)]"}`}
    >
      <Icon name={up ? "up" : "down"} className="h-3 w-3" />
      {up ? "+" : ""}
      {value}
      {suffix}
    </span>
  );
}

export function StatTile({
  label,
  value,
  sub,
  delta = null,
  accent = false,
}: {
  label: string;
  value: string | number;
  sub?: string;
  delta?: number | null;
  accent?: boolean;
}) {
  return (
    <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-2)] px-4 py-3">
      <p className="text-[11px] font-medium uppercase tracking-[0.1em] text-[var(--dim)]">{label}</p>
      <div className="mt-1.5 flex items-baseline gap-2">
        <p
          className={`font-mono text-[26px] font-semibold leading-none ${accent ? "text-[var(--accent-bright)]" : "text-[var(--text)]"}`}
        >
          {typeof value === "number" ? num(value) : value}
        </p>
        <Delta value={delta} />
      </div>
      {sub && <p className="mt-1.5 text-[12px] text-[var(--muted)]">{sub}</p>}
    </div>
  );
}

/* ----------------------------- pills ----------------------------- */

const OUTCOME_STYLE: Record<string, string> = {
  hired: "text-[#7ee2ab] bg-[rgba(69,192,127,0.14)] border-[rgba(69,192,127,0.3)]",
  interview: "text-[var(--accent-bright)] bg-[var(--accent-soft)] border-[rgba(32,142,199,0.32)]",
  viewed: "text-[#c9b878] bg-[rgba(201,184,120,0.12)] border-[rgba(201,184,120,0.26)]",
  sent: "text-[var(--dim)] bg-[var(--surface-3)] border-[var(--border)]",
  new: "text-[var(--dim)] bg-[var(--surface-3)] border-[var(--border)]",
};

const OUTCOME_LABEL: Record<string, string> = {
  hired: "Hired",
  interview: "Interview",
  viewed: "Viewed",
  sent: "No response",
  new: "New",
};

/** Status/outcome pill for Upwork outcomes (hired/interview/viewed/sent) and CRM status (New/Sent). */
export function StatusPill({ value }: { value: string }) {
  const key = value.toLowerCase();
  const style = OUTCOME_STYLE[key] ?? "text-[var(--muted)] bg-[var(--surface-3)] border-[var(--border)]";
  const label = OUTCOME_LABEL[key] ?? value;
  return (
    <span className={`inline-flex items-center rounded-md border px-2 py-0.5 text-[11px] font-medium ${style}`}>
      {label}
    </span>
  );
}

export function TypeBadge({ type }: { type: string }) {
  if (!type) return <span className="text-[12px] text-[var(--dim)]">—</span>;
  const founder = type.toLowerCase() === "founder";
  return (
    <span
      className={`inline-flex items-center rounded-md px-2 py-0.5 text-[11px] font-medium ${
        founder ? "text-[#b9a6e6] bg-[rgba(139,109,214,0.14)]" : "text-[#8fb3d6] bg-[rgba(96,144,212,0.14)]"
      }`}
    >
      {type}
    </span>
  );
}

const PLATFORM_COLOR: Record<string, string> = {
  linkedin: "#55a9e0",
  instagram: "#d183c0",
  facebook: "#7f97dc",
};

export function PlatformBadge({ platform }: { platform: string }) {
  const color = PLATFORM_COLOR[platform] ?? "#98a2b3";
  return (
    <span
      className="inline-flex items-center rounded-md px-2 py-0.5 text-[11px] font-semibold capitalize"
      style={{ color, backgroundColor: `${color}1f` }}
    >
      {platform}
    </span>
  );
}

/* Small dot used before a platform name in headers. */
export function PlatformDot({ platform }: { platform: string }) {
  const color = PLATFORM_COLOR[platform] ?? "#98a2b3";
  return <span className="inline-block h-2 w-2 rounded-full" style={{ backgroundColor: color }} aria-hidden />;
}

/* ----------------------------- states ----------------------------- */

export function Unavailable({ reason, hint }: { reason?: string; hint?: string }) {
  return (
    <div className="rounded-xl border border-dashed border-[var(--border-strong)] bg-[var(--surface-2)] px-4 py-6 text-center">
      <p className="text-[13px] text-[var(--muted)]">{reason ?? "Not available"}</p>
      {hint && <p className="mt-1 text-[12px] text-[var(--dim)]">{hint}</p>}
    </div>
  );
}

export function EmptyState({ label }: { label: string }) {
  return (
    <div className="rounded-xl border border-dashed border-[var(--border)] bg-[var(--surface-2)] px-4 py-10 text-center">
      <p className="text-[13px] text-[var(--dim)]">{label}</p>
    </div>
  );
}
