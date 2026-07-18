import Link from "next/link";
import { Icon } from "@/components/ui";

export default function NotFound() {
  return (
    <div className="mx-auto flex min-h-[70vh] max-w-lg flex-col items-center justify-center px-8 text-center">
      <div className="brandmark mb-6 flex h-12 w-12 items-center justify-center rounded-2xl">
        <span className="text-[20px] font-bold tracking-tight text-white">N</span>
      </div>
      <p className="font-mono text-[13px] font-medium uppercase tracking-[0.2em] text-[var(--dim)]">404</p>
      <h1 className="mt-2 text-[22px] font-semibold tracking-tight text-[var(--text)]">That page isn&apos;t part of the review</h1>
      <p className="mt-3 text-[14px] text-[var(--muted)]">
        You&apos;ve wandered off the weekly report. The sections are Upwork, outreach, content, and productivity.
      </p>
      <Link
        href="/"
        className="mt-6 inline-flex items-center gap-1.5 rounded-lg border border-[var(--border-strong)] bg-[var(--accent-soft)] px-3.5 py-2 text-[13px] font-medium text-[var(--accent-bright)] transition-colors hover:bg-[rgba(32,142,199,0.2)]"
      >
        <Icon name="arrow-left" className="h-4 w-4" />
        Back to overview
      </Link>
    </div>
  );
}
