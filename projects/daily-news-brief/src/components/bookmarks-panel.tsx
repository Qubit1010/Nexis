"use client";

import { useBookmarkContext } from "@/lib/hooks/bookmark-context";

export function BookmarksPanel({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const { bookmarks, toggleBookmark, clearBookmarks } = useBookmarkContext();

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
                  className="text-amber-400 hover:text-red-400 transition-colors shrink-0 mt-0.5"
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
