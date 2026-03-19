"use client";

import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { useState } from "react";

interface BriefHeaderProps {
  date: string;
  createdAt: string;
  totalArticles: number;
  totalCategories: number;
  sourcesUsed?: number | null;
  totalArticlesFetched?: number | null;
}

export function BriefHeader({
  date,
  createdAt,
  totalArticles,
  totalCategories,
  sourcesUsed,
  totalArticlesFetched,
}: BriefHeaderProps) {
  const [regenerating, setRegenerating] = useState(false);
  const router = useRouter();

  const formatted = new Date(date + "T00:00:00").toLocaleDateString("en-US", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  async function handleRegenerate() {
    setRegenerating(true);
    try {
      await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ date }),
      });
      router.refresh();
    } finally {
      setRegenerating(false);
    }
  }

  return (
    <div className="relative rounded-xl bg-gradient-to-r from-[var(--background)] to-[var(--navy-light)] border border-border/50 p-6 sm:p-8 animate-fade-in overflow-hidden">
      {/* Subtle decorative element */}
      <div className="absolute top-0 right-0 w-48 h-48 bg-primary/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/4 pointer-events-none" />

      <div className="relative flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div className="space-y-3">
          <p className="text-xs font-semibold text-primary uppercase tracking-[0.15em] animate-fade-in stagger-1">
            AI Intelligence Brief
          </p>
          <h1 className="text-2xl sm:text-4xl font-bold tracking-tight animate-fade-in stagger-2">
            {formatted}
          </h1>
          <div className="flex items-center gap-2.5 flex-wrap animate-fade-in stagger-3">
            <span className="inline-flex items-center gap-1.5 text-xs font-medium text-primary bg-primary/10 border border-primary/20 px-3 py-1.5 rounded-full">
              {totalCategories} categories
            </span>
            <span className="inline-flex items-center gap-1.5 text-xs font-medium text-secondary bg-secondary/10 border border-secondary/20 px-3 py-1.5 rounded-full">
              {totalArticles} articles
            </span>
            {sourcesUsed != null && sourcesUsed > 0 && (
              <span className="inline-flex items-center gap-1.5 text-xs font-medium text-primary bg-primary/10 border border-primary/20 px-3 py-1.5 rounded-full">
                {sourcesUsed} sources
              </span>
            )}
            {totalArticlesFetched != null && totalArticlesFetched > 0 && (
              <span className="inline-flex items-center gap-1.5 text-xs font-medium text-primary bg-primary/10 border border-primary/20 px-3 py-1.5 rounded-full">
                {totalArticlesFetched} fetched
              </span>
            )}
            <span className="text-xs text-muted-foreground/50 animate-fade-in stagger-4">
              Generated{" "}
              {new Date(createdAt).toLocaleTimeString("en-US", {
                hour: "numeric",
                minute: "2-digit",
              })}
            </span>
          </div>
        </div>

        <Button
          className="shrink-0 h-10 px-5 text-sm font-medium bg-primary/10 text-primary border border-primary/25 hover:bg-primary/20 hover:border-primary/40 transition-all duration-200 rounded-lg animate-fade-in stagger-4"
          onClick={handleRegenerate}
          disabled={regenerating}
        >
          {regenerating ? (
            <span className="flex items-center gap-2">
              <span className="w-3.5 h-3.5 border-2 border-primary/30 border-t-primary rounded-full animate-spin" />
              Regenerating...
            </span>
          ) : (
            "Regenerate"
          )}
        </Button>
      </div>
    </div>
  );
}
