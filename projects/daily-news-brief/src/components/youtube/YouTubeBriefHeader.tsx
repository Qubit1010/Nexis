"use client";

import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Youtube } from "lucide-react";

interface YouTubeBriefHeaderProps {
  date: string;
  createdAt: string;
  videoCount: number;
  channelCount: number;
  analyzedAt?: string | null;
  modelUsed?: string | null;
}

export function YouTubeBriefHeader({
  date,
  createdAt,
  videoCount,
  channelCount,
  analyzedAt,
  modelUsed,
}: YouTubeBriefHeaderProps) {
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
      await fetch("/api/generate-youtube", {
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
    <div className="space-y-4">
      <div className="relative rounded-xl bg-gradient-to-r from-[var(--background)] to-[var(--navy-light)] border border-border/50 p-6 sm:p-8 animate-fade-in overflow-hidden">
        <div className="absolute top-0 right-0 w-48 h-48 bg-rose-500/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/4 pointer-events-none" />

        <div className="relative flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div className="space-y-3">
            <p className="text-xs font-semibold text-rose-500 uppercase tracking-[0.15em] inline-flex items-center gap-2">
              <Youtube className="w-3.5 h-3.5" />
              YouTube Intelligence
            </p>
            <h1 className="text-2xl sm:text-4xl font-bold tracking-tight">
              {formatted}
            </h1>
            <div className="flex items-center gap-2.5 flex-wrap">
              <span className="inline-flex items-center gap-1.5 text-xs font-medium text-rose-500 bg-rose-500/10 border border-rose-500/20 px-3 py-1.5 rounded-full">
                {channelCount} channels
              </span>
              <span className="inline-flex items-center gap-1.5 text-xs font-medium text-secondary bg-secondary/10 border border-secondary/20 px-3 py-1.5 rounded-full">
                {videoCount} videos
              </span>
              {modelUsed && (
                <span className="inline-flex items-center gap-1.5 text-xs font-medium text-rose-500/70 bg-rose-500/5 border border-rose-500/15 px-3 py-1.5 rounded-full">
                  {modelUsed}
                </span>
              )}
              <span className="text-xs text-muted-foreground/50">
                {analyzedAt
                  ? `Analyzed ${new Date(analyzedAt).toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" })}`
                  : `Generated ${new Date(createdAt).toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" })}`}
              </span>
            </div>
          </div>

          <Button
            className="shrink-0 h-10 px-5 text-sm font-medium bg-rose-500/10 text-rose-500 border border-rose-500/25 hover:bg-rose-500/20 hover:border-rose-500/40 transition-all duration-200 rounded-lg"
            onClick={handleRegenerate}
            disabled={regenerating}
          >
            {regenerating ? (
              <span className="flex items-center gap-2">
                <span className="w-3.5 h-3.5 border-2 border-rose-500/30 border-t-rose-500 rounded-full animate-spin" />
                Regenerating...
              </span>
            ) : (
              "Regenerate"
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
