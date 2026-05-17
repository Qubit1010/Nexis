"use client";

import { useCallback, useEffect, useState } from "react";

export interface SheetPayload {
  briefDate: string;
  title: string;
  format: string;
  timeliness: string;
  angle: string;
  hook: string;
  keyPoints: string[];
  relatedTrends: string[];
}

interface CardActionsProps {
  id: string | number;
  storageKey: string;
  buildMarkdown: () => string;
  markdownFilename: string;
  buildSheetPayload: () => SheetPayload;
  className?: string;
}

const usedCache = new Map<string, Set<string>>();

function loadUsed(storageKey: string): Set<string> {
  if (typeof window === "undefined") return new Set();
  const cached = usedCache.get(storageKey);
  if (cached) return cached;
  try {
    const raw = localStorage.getItem(storageKey);
    const set = raw ? new Set<string>(JSON.parse(raw)) : new Set<string>();
    usedCache.set(storageKey, set);
    return set;
  } catch {
    return new Set();
  }
}

function persistUsed(storageKey: string, ids: Set<string>) {
  usedCache.set(storageKey, ids);
  localStorage.setItem(storageKey, JSON.stringify([...ids]));
  window.dispatchEvent(new CustomEvent(`used-changed:${storageKey}`));
}

export function CardActions({
  id,
  storageKey,
  buildMarkdown,
  markdownFilename,
  buildSheetPayload,
  className,
}: CardActionsProps) {
  const sid = String(id);
  const [isUsed, setIsUsed] = useState(false);
  const [saveState, setSaveState] = useState<"idle" | "saving" | "saved" | "error">("idle");

  useEffect(() => {
    setIsUsed(loadUsed(storageKey).has(sid));
    const handler = () => setIsUsed(loadUsed(storageKey).has(sid));
    window.addEventListener(`used-changed:${storageKey}`, handler);
    return () => window.removeEventListener(`used-changed:${storageKey}`, handler);
  }, [storageKey, sid]);

  const toggleUsed = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      const current = new Set(loadUsed(storageKey));
      if (current.has(sid)) current.delete(sid);
      else current.add(sid);
      persistUsed(storageKey, current);
      setIsUsed(current.has(sid));
    },
    [storageKey, sid]
  );

  const exportMarkdown = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      const md = buildMarkdown();
      const blob = new Blob([md], { type: "text/markdown" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = markdownFilename;
      a.click();
      URL.revokeObjectURL(url);
    },
    [buildMarkdown, markdownFilename]
  );

  const saveToSheet = useCallback(
    async (e: React.MouseEvent) => {
      e.stopPropagation();
      if (saveState === "saved" || saveState === "saving") return;
      setSaveState("saving");
      try {
        const res = await fetch("/api/sheets", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(buildSheetPayload()),
        });
        if (!res.ok) throw new Error("Failed to save");
        setSaveState("saved");
      } catch (err) {
        console.error("Failed to save to sheet:", err);
        setSaveState("error");
        setTimeout(() => setSaveState("idle"), 2500);
      }
    },
    [buildSheetPayload, saveState]
  );

  return (
    <div className={`flex items-center gap-1 shrink-0 ${className || ""}`}>
      <button
        onClick={toggleUsed}
        className={`w-7 h-7 rounded-md flex items-center justify-center transition-all duration-200 ${
          isUsed
            ? "text-emerald-400 hover:text-emerald-300"
            : "text-muted-foreground/40 hover:text-foreground hover:bg-accent/60"
        }`}
        title={isUsed ? "Mark as unused" : "Mark as used"}
      >
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <polyline points="20 6 9 17 4 12" />
        </svg>
      </button>
      <button
        onClick={exportMarkdown}
        className="w-7 h-7 rounded-md flex items-center justify-center text-muted-foreground/40 hover:text-foreground hover:bg-accent/60 transition-all duration-200"
        title="Export as Markdown"
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
        >
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="7 10 12 15 17 10" />
          <line x1="12" y1="15" x2="12" y2="3" />
        </svg>
      </button>
      <button
        onClick={saveToSheet}
        disabled={saveState === "saving" || saveState === "saved"}
        className={`w-7 h-7 rounded-md flex items-center justify-center transition-all duration-200 ${
          saveState === "saved"
            ? "text-green-400"
            : saveState === "error"
              ? "text-red-400"
              : saveState === "saving"
                ? "text-muted-foreground/40 animate-pulse"
                : "text-muted-foreground/40 hover:text-foreground hover:bg-accent/60"
        }`}
        title={
          saveState === "saved"
            ? "Saved to Google Sheet"
            : saveState === "error"
              ? "Save failed - click to retry"
              : "Save to Google Sheet"
        }
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
        >
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
          <rect x="7" y="7" width="4" height="4" />
          <line x1="15" y1="7" x2="19" y2="7" />
          <line x1="15" y1="11" x2="19" y2="11" />
          <line x1="7" y1="15" x2="19" y2="15" />
          <line x1="7" y1="19" x2="19" y2="19" />
        </svg>
      </button>
    </div>
  );
}

function slugify(s: string): string {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 50);
}

export function mdFilename(title: string, suffix?: string): string {
  const base = slugify(title) || "export";
  return suffix ? `${base}-${suffix}.md` : `${base}.md`;
}
