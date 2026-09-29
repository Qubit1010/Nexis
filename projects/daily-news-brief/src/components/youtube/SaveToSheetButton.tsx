"use client";

import { useState } from "react";
import { Bookmark, BookmarkCheck, CircleAlert, Loader2 } from "lucide-react";

interface SaveToSheetButtonProps {
  payload: Record<string, unknown>;
  className?: string;
}

export function SaveToSheetButton({ payload, className = "" }: SaveToSheetButtonProps) {
  const [state, setState] = useState<"idle" | "saving" | "saved" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState("");

  async function handleSave(e: React.MouseEvent) {
    e.preventDefault();
    e.stopPropagation();
    if (state === "saving" || state === "saved") return;
    setState("saving");
    setErrorMessage("");
    try {
      const res = await fetch("/api/youtube-bookmark", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const result = await res.json().catch(() => null);
      if (!res.ok || !result?.success) {
        setErrorMessage(result?.error || "Could not save to Google Sheets. Try again.");
        setState("error");
        return;
      }
      setState("saved");
    } catch {
      setErrorMessage("Could not reach the dashboard server. Try again.");
      setState("error");
    }
  }

  return (
    <span className="inline-flex items-center gap-1">
      <button
        onClick={handleSave}
        disabled={state === "saving" || state === "saved"}
        aria-label={state === "error" ? `${errorMessage}. Click to retry.` : state === "saved" ? "Saved to Google Sheets" : "Save to Google Sheets"}
        className={`p-1 rounded-lg transition-colors disabled:cursor-default ${className} ${
          state === "saved"
            ? "text-green-400"
            : state === "error"
            ? "text-red-400"
            : "text-muted-foreground/30 hover:text-rose-400 hover:bg-rose-500/10"
        }`}
        title={state === "error" ? `${errorMessage} Click to retry.` : state === "saved" ? "Saved to Google Sheets" : "Save to Google Sheets"}
      >
        {state === "saving" ? (
          <Loader2 className="w-3.5 h-3.5 animate-spin" />
        ) : state === "saved" ? (
          <BookmarkCheck className="w-3.5 h-3.5" />
        ) : state === "error" ? (
          <CircleAlert className="w-3.5 h-3.5" />
        ) : (
          <Bookmark className="w-3.5 h-3.5" />
        )}
      </button>
      {state === "error" && (
        <span role="status" className="max-w-40 text-[10px] leading-tight text-red-400">
          Save failed. Hover for details.
        </span>
      )}
    </span>
  );
}
