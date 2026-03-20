"use client";

import { useState, useCallback } from "react";
import { useBookmarkContext } from "@/lib/hooks/bookmark-context";

export function BookmarksPanel({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const { bookmarks, toggleBookmark, clearBookmarks } = useBookmarkContext();
  const [savingId, setSavingId] = useState<number | null>(null);
  const [savedIds, setSavedIds] = useState<Set<number>>(new Set());

  const saveToSheet = useCallback(
    async (b: (typeof bookmarks)[0]) => {
      if (savedIds.has(b.id)) return;
      setSavingId(b.id);
      try {
        const res = await fetch("/api/sheets/articles", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            briefDate: b.date,
            title: b.title,
            source: b.source,
            url: b.url,
            tldr: b.tldr,
          }),
        });
        if (!res.ok) throw new Error("Failed to save");
        setSavedIds((prev) => new Set(prev).add(b.id));
      } catch (err) {
        console.error("Failed to save article to sheet:", err);
      } finally {
        setSavingId(null);
      }
    },
    [savedIds]
  );

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[10vh]">
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />
      <div className="relative w-full max-w-lg mx-4 rounded-xl border border-border bg-background shadow-2xl animate-fade-in max-h-[70vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-border">
          <div>
            <h3 className="text-[16px] font-bold">Saved Articles</h3>
            <p className="text-[12px] text-muted-foreground/60">
              {bookmarks.length} bookmark{bookmarks.length !== 1 ? "s" : ""}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {bookmarks.length > 0 && (
              <button
                onClick={clearBookmarks}
                className="text-[12px] text-red-400/70 hover:text-red-400 transition-colors"
              >
                Clear all
              </button>
            )}
            <button
              onClick={onClose}
              className="w-7 h-7 rounded-md flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-accent/60 transition-all"
            >
              &#10005;
            </button>
          </div>
        </div>

        {/* Bookmarks list */}
        <div className="flex-1 overflow-y-auto py-2">
          {bookmarks.length === 0 && (
            <div className="px-5 py-8 text-center text-[13px] text-muted-foreground/50">
              No saved articles yet. Hover over an article and click the
              bookmark icon to save it.
            </div>
          )}
          {bookmarks.map((b) => (
            <div
              key={b.id}
              className="px-5 py-3 hover:bg-accent/40 transition-colors group"
            >
              <div className="flex items-start justify-between gap-2">
                <a
                  href={b.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[14px] font-medium text-foreground hover:text-primary transition-colors line-clamp-2"
                >
                  {b.title}
                </a>
                <div className="flex items-center gap-1 shrink-0 mt-0.5">
                  <button
                    onClick={() => saveToSheet(b)}
                    disabled={savingId === b.id || savedIds.has(b.id)}
                    className={`w-6 h-6 rounded flex items-center justify-center transition-all duration-200 ${
                      savedIds.has(b.id)
                        ? "text-green-400"
                        : savingId === b.id
                          ? "text-muted-foreground/40 animate-pulse"
                          : "text-muted-foreground/40 hover:text-foreground hover:bg-accent/60"
                    }`}
                    title={savedIds.has(b.id) ? "Saved to Google Sheet" : "Save to Google Sheet"}
                  >
                    <svg
                      width="13"
                      height="13"
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
                  <button
                    onClick={() =>
                      toggleBookmark({
                        id: b.id,
                        title: b.title,
                        url: b.url,
                        source: b.source,
                        tldr: b.tldr,
                        date: b.date,
                      })
                    }
                    className="text-amber-400 hover:text-red-400 transition-colors"
                    title="Remove bookmark"
                  >
                    <svg
                      width="14"
                      height="14"
                      viewBox="0 0 24 24"
                      fill="currentColor"
                      stroke="currentColor"
                      strokeWidth="2"
                    >
                      <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
                    </svg>
                  </button>
                </div>
              </div>
              <div className="flex items-center gap-2 mt-1 text-[12px] text-muted-foreground/50">
                <span>{b.source}</span>
                <span>&middot;</span>
                <span>{b.date}</span>
              </div>
              <p className="text-[13px] text-muted-foreground/60 mt-1 line-clamp-2">
                {b.tldr}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
