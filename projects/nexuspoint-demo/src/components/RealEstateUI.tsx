"use client";
import { useEffect, useId, useRef, type ReactNode } from "react";

const PATHS: Record<string, ReactNode> = {
  grid: <><path d="M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z" /></>,
  pipeline: <><path d="M3 5h4v14H3zM10 5h4v9h-4zM17 5h4v5h-4z" /></>,
  home: <><path d="M3 11 12 4l9 7" /><path d="M5 10v10h14V10M10 20v-6h4v6" /></>,
  pin: <><path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0Z" /><circle cx="12" cy="10" r="2.5" /></>,
  calendar: <><path d="M4 6h16v14H4zM4 10h16M8 3v5m8-5v5" /></>,
  chat: <path d="M4 20 5 16A8 8 0 1 1 9 19Z" />,
  users: <><circle cx="9" cy="8" r="4" /><path d="M2 21v-1a7 7 0 0 1 14 0v1m2-17a4 4 0 0 1 0 8m1 3a6 6 0 0 1 3 5" /></>,
  chart: <><path d="M4 20V4M4 20h16" /><path d="M8 16v-5m4 5V8m4 8v-3" /></>,
  clock: <><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></>,
  settings: <><path d="M4 6h16M4 12h16M4 18h16" /><circle cx="9" cy="6" r="2" /><circle cx="15" cy="12" r="2" /><circle cx="8" cy="18" r="2" /></>,
  sun: <><circle cx="12" cy="12" r="4" /><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5" /></>,
  arrow: <path d="M4 12h16m-6-6 6 6-6 6" />,
  check: <path d="m5 12 4 4L19 6" />,
  plane: <path d="m3 13 7-2 4-8 2 1-2 7 6 2v2l-7-1-3 6H8l1-7-6 2Z" />,
  search: <><circle cx="10" cy="10" r="6" /><path d="m15 15 6 6" /></>,
  bolt: <path d="M13 2 4 14h7l-1 8 9-12h-7Z" />,
  tag: <><path d="M3 12V3h9l9 9-9 9Z" /><circle cx="8" cy="8" r="1.5" /></>,
  note: <><path d="M5 3h10l4 4v14H5Z" /><path d="M9 11h6M9 15h6" /></>,
  close: <path d="m6 6 12 12M18 6 6 18" />,
};
export function ReIcon({ name = "grid" }: { name?: string }) {
  return <svg className="re-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="square" strokeLinejoin="miter" aria-hidden="true">{PATHS[name] ?? PATHS.grid}</svg>;
}

/** Line illustrations for sample listings. Deliberately schematic: no photos are implied to be real. */
export function PropertyArt({ kind }: { kind: string }) {
  const stroke = { fill: "none", stroke: "currentColor", strokeWidth: 1.4 } as const;
  return <svg className={`re-art re-art-${kind}`} viewBox="0 0 320 180" aria-hidden="true">
    <defs><pattern id={`g-${kind}`} width="16" height="16" patternUnits="userSpaceOnUse"><path d="M16 0H0v16" {...stroke} strokeWidth=".5" opacity=".25" /></pattern></defs>
    <rect width="320" height="180" fill={`url(#g-${kind})`} />
    {kind === "plot" || kind === "file" ? <>
      <path d="M40 150 110 40h170l-50 110Z" {...stroke} />
      <path d="M95 64h170M70 103h178" {...stroke} strokeDasharray="4 6" opacity=".6" />
      <path d="M150 40 120 150M215 40l-35 110" {...stroke} opacity=".45" />
      <rect x="168" y="78" width="34" height="22" className="re-art-accent" />
      {kind === "file" && <><rect x="232" y="18" width="62" height="78" {...stroke} /><path d="M244 36h38M244 50h38M244 64h24" {...stroke} /></>}
    </> : kind === "apartment" ? <>
      <path d="M95 160V40h80v120M175 160V70h60v90M60 160h210" {...stroke} />
      {Array.from({ length: 12 }, (_, i) => <rect key={i} x={108 + (i % 3) * 22} y={52 + Math.floor(i / 3) * 26} width="12" height="14" {...stroke} className={i === 4 ? "re-art-accent" : undefined} />)}
      {Array.from({ length: 6 }, (_, i) => <rect key={"b" + i} x={188 + (i % 2) * 24} y={84 + Math.floor(i / 2) * 24} width="12" height="12" {...stroke} />)}
    </> : kind === "commercial" ? <>
      <path d="M60 160V70l40-20h120l40 20v90M60 160h200M60 70h200" {...stroke} />
      <rect x="80" y="100" width="70" height="60" {...stroke} /><rect x="170" y="100" width="70" height="40" className="re-art-accent" />
      <path d="M100 82h120" {...stroke} strokeDasharray="3 5" />
    </> : <>
      <path d="M70 160V88l90-52 90 52v72M50 160h220M70 88h180" {...stroke} />
      <rect x="140" y="112" width="40" height="48" className="re-art-accent" />
      <rect x="92" y="104" width="30" height="24" {...stroke} /><rect x="198" y="104" width="30" height="24" {...stroke} />
      <path d="M160 36v-14h22v26" {...stroke} />
    </>}
  </svg>;
}

export function ReModal({ title, onClose, children, wide = false }: { title: string; onClose: () => void; children: ReactNode; wide?: boolean }) {
  const ref = useRef<HTMLDivElement>(null), close = useRef(onClose), uid = useId();
  close.current = onClose;
  useEffect(() => {
    const before = document.activeElement as HTMLElement | null, overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const nodes = () => Array.from(ref.current?.querySelectorAll<HTMLElement>("button:not(:disabled),input:not(:disabled),select:not(:disabled),textarea:not(:disabled),a[href]") ?? []);
    nodes()[0]?.focus();
    const key = (e: KeyboardEvent) => {
      if (e.key === "Escape") close.current();
      if (e.key !== "Tab") return;
      const n = nodes(), first = n[0], last = n.at(-1);
      if (!n.length) { e.preventDefault(); return; }
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last?.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first?.focus(); }
    };
    document.addEventListener("keydown", key);
    return () => { document.removeEventListener("keydown", key); document.body.style.overflow = overflow; before?.focus(); };
  }, []);
  return <div className="re-overlay" onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }}>
    <div className={`re-modal${wide ? " wide" : ""}`} role="dialog" aria-modal="true" aria-labelledby={uid} ref={ref}>
      <div className="re-row"><h2 id={uid}>{title}</h2><button type="button" className="re-icon-btn" onClick={onClose} aria-label="Close / بند کریں"><ReIcon name="close" /></button></div>
      {children}
    </div>
  </div>;
}
