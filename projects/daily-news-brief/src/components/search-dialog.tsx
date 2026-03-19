"use client";

import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { useRouter } from "next/navigation";

interface SearchResult {
  id: number;
  title: string;
  source: string;
  tldr: string;
  sentimentTag: string | null;
  date: string;
  categoryName: string;
  categorySlug: string;
}

const SENTIMENT_COLORS: Record<string, string> = {
  excited: "bg-emerald-400",
  neutral: "bg-zinc-400",
  concerned: "bg-amber-400",
  skeptical: "bg-red-400",
};

export function SearchDialog({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 50);
    } else {
      setQuery("");
      setResults([]);
    }
  }, [open]);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (query.length < 2) {
      setResults([]);
      return;
    }
    setLoading(true);
    debounceRef.current = setTimeout(() => {
      fetch(`/api/search?q=${encodeURIComponent(query)}`)
        .then((r) => r.json())
        .then((data) => {
          setResults(data);
          setLoading(false);
        })
        .catch(() => setLoading(false));
    }, 300);
  }, [query]);

  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === "Escape" && open) {
        onClose();
      }
    }
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [open, onClose]);

  if (!open) return null;

  function goToResult(result: SearchResult) {
    const url = `/brief/${result.date}#${result.categorySlug}`;
    router.push(url);
    // Close after a short delay so the navigation isn't interrupted
    setTimeout(() => onClose(), 100);
  }

  return createPortal(
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center"
      style={{ position: "fixed", top: 0, left: 0, right: 0, bottom: 0 }}
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0 }}
        onClick={onClose}
      />

      {/* Dialog */}
      <div className="relative w-[35%] min-w-[320px] rounded-xl border border-border bg-background shadow-2xl animate-fade-in">
        {/* Search input */}
        <div className="flex items-center gap-3 px-4 border-b border-border">
          <span className="text-muted-foreground/50 text-sm shrink-0">/</span>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search articles across all briefs..."
            className="w-full py-3.5 bg-transparent text-[15px] text-foreground placeholder:text-muted-foreground/40 outline-none"
          />
          {loading && (
            <span className="w-4 h-4 border-2 border-primary/30 border-t-primary rounded-full animate-spin shrink-0" />
          )}
        </div>

        {/* Results */}
        {results.length > 0 && (
          <div className="max-h-[50vh] overflow-y-auto py-2">
            {results.map((r) => (
              <button
                key={`${r.date}-${r.id}`}
                onClick={() => goToResult(r)}
                className="w-full text-left px-4 py-3 hover:bg-accent/60 transition-colors duration-150"
              >
                <div className="flex items-center gap-2 mb-1">
                  {r.sentimentTag && (
                    <span
                      className={`w-1.5 h-1.5 rounded-full ${
                        SENTIMENT_COLORS[r.sentimentTag] || "bg-zinc-400"
                      }`}
                    />
                  )}
                  <span className="text-[14px] font-medium text-foreground line-clamp-1">
                    {r.title}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-[12px] text-muted-foreground/60">
                  <span>{r.source}</span>
                  <span>&middot;</span>
                  <span>{r.categoryName}</span>
                  <span>&middot;</span>
                  <span>{r.date}</span>
                </div>
              </button>
            ))}
          </div>
        )}

        {query.length >= 2 && !loading && results.length === 0 && (
          <div className="px-4 py-8 text-center text-[13px] text-muted-foreground/50">
            No articles found for "{query}"
          </div>
        )}

        {/* Footer hint */}
        <div className="px-4 py-2 border-t border-border/50 flex items-center gap-4 text-[11px] text-muted-foreground/40">
          <span>
            <kbd className="px-1 py-0.5 rounded bg-muted text-muted-foreground/60">
              Esc
            </kbd>{" "}
            to close
          </span>
          <span>
            <kbd className="px-1 py-0.5 rounded bg-muted text-muted-foreground/60">
              Ctrl+K
            </kbd>{" "}
            to toggle
          </span>
        </div>
      </div>
    </div>,
    document.body
  );
}
