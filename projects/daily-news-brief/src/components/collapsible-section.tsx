"use client";

import { useState, useEffect, ReactNode } from "react";

interface CollapsibleSectionProps {
  id: string;
  children: ReactNode;
  defaultOpen?: boolean;
  /** Label shown when collapsed */
  label: string;
}

const STORAGE_KEY = "intel-brief-collapsed";

function getCollapsedState(): Record<string, boolean> {
  if (typeof window === "undefined") return {};
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
  } catch {
    return {};
  }
}

export function CollapsibleSection({
  id,
  children,
  defaultOpen = true,
  label,
}: CollapsibleSectionProps) {
  const [open, setOpen] = useState(defaultOpen);

  useEffect(() => {
    const state = getCollapsedState();
    if (id in state) {
      setOpen(!state[id]);
    }
  }, [id]);

  function toggle() {
    const next = !open;
    setOpen(next);
    const state = getCollapsedState();
    state[id] = !next;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }

  if (!open) {
    return (
      <button
        onClick={toggle}
        className="w-full flex items-center gap-2 py-3 px-4 rounded-xl border border-border/40 text-muted-foreground/50 hover:text-muted-foreground hover:border-border/60 transition-all cursor-pointer group"
      >
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="shrink-0"
        >
          <polyline points="9 18 15 12 9 6" />
        </svg>
        <span className="text-[13px] font-medium">{label}</span>
        <span className="text-[11px] text-muted-foreground/30 ml-auto">click to expand</span>
      </button>
    );
  }

  return (
    <div className="relative group/collapse">
      <button
        onClick={toggle}
        className="absolute -left-6 top-2 opacity-0 group-hover/collapse:opacity-100 transition-opacity text-muted-foreground/30 hover:text-muted-foreground"
        title="Collapse section"
      >
        <svg
          width="12"
          height="12"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>
      {children}
    </div>
  );
}
