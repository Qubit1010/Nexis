"use client";

import { useState } from "react";
import { Bookmark, BookmarkCheck, Loader2 } from "lucide-react";

interface SaveToSheetButtonProps {
  payload: Record<string, unknown>;
  className?: string;
}

export function SaveToSheetButton({ payload, className = "" }: SaveToSheetButtonProps) {
  const [state, setState] = useState<"idle" | "saving" | "saved" | "error">("idle");

  async function handleSave(e: React.MouseEvent) {
    e.preventDefault();
    e.stopPropagation();
    if (state === "saving" || state === "saved") return;
    setState("saving");
    try {
      const res = await fetch("/api/youtube-bookmark", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      setState(res.ok ? "saved" : "error");
      if (!res.ok) setTimeout(() => setState("idle"), 2000);
    } catch {
      setState("error");
      setTimeout(() => setState("idle"), 2000);
    }
  }

  return (
    <button
      onClick={handleSave}
      disabled={state === "saving" || state === "saved"}
      className={`p-1 rounded-lg transition-colors disabled:cursor-default ${className} ${
        state === "saved"
          ? "text-green-400"
          : state === "error"
          ? "text-red-400"
          : "text-muted-foreground/30 hover:text-rose-400 hover:bg-rose-500/10"
      }`}
      title={state === "saved" ? "Saved to sheet" : "Save to Content Ideas sheet"}
    >
      {state === "saving" ? (
        <Loader2 className="w-3.5 h-3.5 animate-spin" />
      ) : state === "saved" ? (
        <BookmarkCheck className="w-3.5 h-3.5" />
      ) : (
        <Bookmark className="w-3.5 h-3.5" />
      )}
    </button>
  );
}
