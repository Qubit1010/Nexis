"use client";

import { useEffect, useState, useCallback } from "react";

export function KeyboardNav() {
  const [activeIndex, setActiveIndex] = useState(-1);
  const [showHelp, setShowHelp] = useState(false);

  const getCards = useCallback(() => {
    return Array.from(document.querySelectorAll("[data-article-card]"));
  }, []);

  const scrollToCard = useCallback((el: Element) => {
    el.scrollIntoView({ behavior: "smooth", block: "center" });
    // Add visual focus
    document.querySelectorAll("[data-article-card]").forEach((c) =>
      c.classList.remove("ring-2", "ring-primary/50")
    );
    el.classList.add("ring-2", "ring-primary/50");
  }, []);

  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      // Don't intercept when typing in inputs
      const tag = (e.target as HTMLElement).tagName;
      if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;

      const cards = getCards();
      if (cards.length === 0) return;

      switch (e.key) {
        case "j": {
          e.preventDefault();
          const next = Math.min(activeIndex + 1, cards.length - 1);
          setActiveIndex(next);
          scrollToCard(cards[next]);
          break;
        }
        case "k": {
          e.preventDefault();
          const prev = Math.max(activeIndex - 1, 0);
          setActiveIndex(prev);
          scrollToCard(cards[prev]);
          break;
        }
        case "?": {
          e.preventDefault();
          setShowHelp((p) => !p);
          break;
        }
        case "Escape": {
          setShowHelp(false);
          document.querySelectorAll("[data-article-card]").forEach((c) =>
            c.classList.remove("ring-2", "ring-primary/50")
          );
          setActiveIndex(-1);
          break;
        }
      }
    }

    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [activeIndex, getCards, scrollToCard]);

  return (
    <>
      {/* Help tooltip */}
      <button
        onClick={() => setShowHelp((p) => !p)}
        className="fixed bottom-4 right-4 z-50 w-8 h-8 rounded-full bg-muted/80 backdrop-blur text-muted-foreground/60 hover:text-foreground text-[13px] font-bold transition-colors"
        title="Keyboard shortcuts (?)"
      >
        ?
      </button>

      {showHelp && (
        <div className="fixed bottom-14 right-4 z-50 rounded-xl border border-border bg-card/95 backdrop-blur shadow-lg p-4 w-56 animate-fade-in">
          <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-[0.1em] mb-3">
            Keyboard Shortcuts
          </p>
          <div className="space-y-2 text-[13px]">
            {[
              { key: "j", desc: "Next article" },
              { key: "k", desc: "Previous article" },
              { key: "Esc", desc: "Clear focus" },
              { key: "Ctrl+K", desc: "Search" },
              { key: "?", desc: "Toggle help" },
            ].map(({ key, desc }) => (
              <div key={key} className="flex items-center justify-between">
                <span className="text-muted-foreground">{desc}</span>
                <kbd className="text-[10px] px-1.5 py-0.5 rounded bg-muted text-muted-foreground/70">
                  {key}
                </kbd>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
}
