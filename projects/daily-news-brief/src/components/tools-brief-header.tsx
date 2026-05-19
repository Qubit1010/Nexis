"use client";

import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Wrench, Sparkles } from "lucide-react";

interface ToolsBriefHeaderProps {
  date: string;
  createdAt: string;
  totalTools: number;
  totalCategories: number;
  sourcesUsed?: number | null;
  topPickName?: string | null;
  topPickWhy?: string | null;
  crossDomainInsight?: string | null;
}

export function ToolsBriefHeader({
  date,
  createdAt,
  totalTools,
  totalCategories,
  sourcesUsed,
  topPickName,
  topPickWhy,
  crossDomainInsight,
}: ToolsBriefHeaderProps) {
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
      await fetch("/api/generate-tools", {
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
    <div className="space-y-5">
      <div className="relative rounded-xl bg-gradient-to-r from-[var(--background)] to-[var(--navy-light)] border border-border/50 p-6 sm:p-8 animate-fade-in overflow-hidden">
        <div className="absolute top-0 right-0 w-48 h-48 bg-teal-500/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/4 pointer-events-none" />

        <div className="relative flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div className="space-y-3">
            <p className="text-xs font-semibold text-teal-500 uppercase tracking-[0.15em] inline-flex items-center gap-2">
              <Wrench className="w-3.5 h-3.5" />
              AI Tools for Business
            </p>
            <h1 className="text-2xl sm:text-4xl font-bold tracking-tight">
              {formatted}
            </h1>
            <div className="flex items-center gap-2.5 flex-wrap">
              <span className="inline-flex items-center gap-1.5 text-xs font-medium text-teal-500 bg-teal-500/10 border border-teal-500/20 px-3 py-1.5 rounded-full">
                {totalCategories} domains
              </span>
              <span className="inline-flex items-center gap-1.5 text-xs font-medium text-secondary bg-secondary/10 border border-secondary/20 px-3 py-1.5 rounded-full">
                {totalTools} tools
              </span>
              {sourcesUsed != null && sourcesUsed > 0 && (
                <span className="inline-flex items-center gap-1.5 text-xs font-medium text-teal-500 bg-teal-500/10 border border-teal-500/20 px-3 py-1.5 rounded-full">
                  {sourcesUsed} sources
                </span>
              )}
              <span className="text-xs text-muted-foreground/50">
                Generated{" "}
                {new Date(createdAt).toLocaleTimeString("en-US", {
                  hour: "numeric",
                  minute: "2-digit",
                })}
              </span>
            </div>
          </div>

          <Button
            className="shrink-0 h-10 px-5 text-sm font-medium bg-teal-500/10 text-teal-500 border border-teal-500/25 hover:bg-teal-500/20 hover:border-teal-500/40 transition-all duration-200 rounded-lg"
            onClick={handleRegenerate}
            disabled={regenerating}
          >
            {regenerating ? (
              <span className="flex items-center gap-2">
                <span className="w-3.5 h-3.5 border-2 border-teal-500/30 border-t-teal-500 rounded-full animate-spin" />
                Regenerating...
              </span>
            ) : (
              "Regenerate"
            )}
          </Button>
        </div>
      </div>

      {topPickName && (
        <div className="rounded-xl border border-amber-500/25 bg-amber-500/[0.04] p-5 sm:p-6 animate-fade-in">
          <div className="flex items-start gap-3">
            <div className="w-9 h-9 rounded-lg bg-amber-500/15 flex items-center justify-center shrink-0">
              <Sparkles className="w-4 h-4 text-amber-500" />
            </div>
            <div className="space-y-1.5 min-w-0">
              <p className="text-[11px] font-semibold text-amber-500/80 uppercase tracking-[0.15em]">
                Top Pick Today
              </p>
              <h2 className="text-lg sm:text-xl font-bold tracking-tight">
                {topPickName}
              </h2>
              {topPickWhy && (
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {topPickWhy}
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {crossDomainInsight && (
        <div className="rounded-xl border border-border/50 bg-card/30 p-5">
          <p className="text-[11px] font-semibold text-muted-foreground/60 uppercase tracking-[0.15em] mb-2">
            Today's Takeaway
          </p>
          <p className="text-base font-medium leading-relaxed">
            {crossDomainInsight}
          </p>
        </div>
      )}
    </div>
  );
}
