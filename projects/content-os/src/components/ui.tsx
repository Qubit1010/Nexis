import { useEffect, type ButtonHTMLAttributes, type ReactNode } from "react";

type Variant = "primary" | "ghost" | "danger" | "quiet";

export function Button({ variant = "ghost", busy, className = "", children, ...rest }: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant; busy?: boolean }) {
  const styles: Record<Variant, string> = {
    primary: "bg-accent text-white hover:bg-accent-bright border-transparent",
    ghost: "bg-s2 text-ink hover:bg-s3 border-line-strong",
    danger: "bg-transparent text-neg hover:bg-neg/10 border-neg/30",
    quiet: "bg-transparent text-muted hover:text-ink hover:bg-s3 border-transparent",
  };
  return (
    <button
      {...rest}
      disabled={rest.disabled || busy}
      className={`inline-flex items-center justify-center gap-1.5 rounded-lg border px-3 py-1.5 text-[13px] font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent ${styles[variant]} ${className}`}
    >
      {busy && <span className="size-3 animate-spin rounded-full border-2 border-current border-t-transparent" aria-hidden />}
      {children}
    </button>
  );
}

export const STATUS_STYLE: Record<string, string> = {
  planned: "text-muted border-line-strong",
  generating: "text-accent-bright border-accent/40 bg-accent-soft",
  review: "text-warn border-warn/40 bg-warn/10",
  approved: "text-accent-bright border-accent/40",
  scheduled: "text-accent-bright border-accent/40 bg-accent-soft",
  ready_to_post: "text-warn border-warn/40 bg-warn/10",
  publishing: "text-accent-bright border-accent/40",
  published: "text-pos border-pos/40 bg-pos/10",
  failed: "text-neg border-neg/40 bg-neg/10",
  missed: "text-neg border-neg/40",
  skipped: "text-dim border-line",
  inbox: "text-accent-bright border-accent/40",
  shortlisted: "text-warn border-warn/40",
  used: "text-pos border-pos/40",
  archived: "text-dim border-line",
  queued: "text-muted border-line-strong",
  running: "text-accent-bright border-accent/40 bg-accent-soft",
  done: "text-pos border-pos/40",
  needs_check: "text-warn border-warn/40 bg-warn/10",
  cancelled: "text-dim border-line",
  ok: "text-pos border-pos/40",
  blocked: "text-warn border-warn/40",
  error: "text-neg border-neg/40",
  timeout: "text-neg border-neg/40",
  killed: "text-dim border-line",
  rate_limited: "text-warn border-warn/40",
  auth_refused: "text-neg border-neg/40",
};

export const STATUS_LABEL: Record<string, string> = {
  ready_to_post: "ready to post",
  needs_check: "needs check",
  rate_limited: "usage limit",
  auth_refused: "auth refused",
};

export function Pill({ status, children }: { status: string; children?: ReactNode }) {
  return (
    <span className={`inline-flex items-center whitespace-nowrap rounded-full border px-2 py-0.5 text-[11px] font-medium leading-4 ${STATUS_STYLE[status] ?? "text-muted border-line-strong"}`}>
      {children ?? STATUS_LABEL[status] ?? status.replace(/_/g, " ")}
    </span>
  );
}

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={`rounded-xl border border-line bg-s1 ${className}`}>{children}</div>;
}

export function SectionTitle({ children, right }: { children: ReactNode; right?: ReactNode }) {
  return (
    <div className="mb-3 flex items-center justify-between gap-3">
      <h2 className="text-[11px] font-semibold uppercase tracking-[0.14em] text-dim">{children}</h2>
      {right}
    </div>
  );
}

export function Empty({ children }: { children: ReactNode }) {
  return <div className="rounded-xl border border-dashed border-line-strong px-4 py-10 text-center text-[13px] text-dim">{children}</div>;
}

export function Modal({ open, onClose, title, children, wide }: { open: boolean; onClose: () => void; title: string; children: ReactNode; wide?: boolean }) {
  useEffect(() => {
    if (!open) return;
    const on = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    addEventListener("keydown", on);
    return () => removeEventListener("keydown", on);
  }, [open, onClose]);
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/60 px-4 py-[8vh] backdrop-blur-sm" onMouseDown={onClose} role="dialog" aria-modal aria-label={title}>
      <div className={`w-full ${wide ? "max-w-3xl" : "max-w-lg"} rounded-xl border border-line-strong bg-s1 shadow-2xl`} onMouseDown={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between border-b border-line px-5 py-3.5">
          <h3 className="text-[15px] font-semibold">{title}</h3>
          <button onClick={onClose} className="rounded-md px-2 py-1 text-muted hover:bg-s3 hover:text-ink" aria-label="Close">
            Esc
          </button>
        </div>
        <div className="px-5 py-4">{children}</div>
      </div>
    </div>
  );
}

export function Field({ label, hint, children }: { label: string; hint?: string; children: ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1 block text-[12px] font-medium text-muted">{label}</span>
      {children}
      {hint && <span className="mt-1 block text-[11px] text-dim">{hint}</span>}
    </label>
  );
}

export const inputCls =
  "w-full rounded-lg border border-line-strong bg-s2 px-3 py-2 text-[13px] text-ink placeholder:text-dim focus:border-accent focus:outline-none";

export function Kbd({ children }: { children: ReactNode }) {
  return <kbd className="rounded border border-line-strong bg-s2 px-1.5 py-px font-mono text-[11px] text-muted">{children}</kbd>;
}

export function Stat({ label, value, tone }: { label: string; value: ReactNode; tone?: "warn" | "neg" | "pos" }) {
  const color = tone === "warn" ? "text-warn" : tone === "neg" ? "text-neg" : tone === "pos" ? "text-pos" : "text-ink";
  return (
    <div className="rounded-lg border border-line bg-s2 px-3 py-2">
      <div className="text-[11px] text-dim">{label}</div>
      <div className={`font-mono text-[18px] font-semibold ${color}`}>{value}</div>
    </div>
  );
}
