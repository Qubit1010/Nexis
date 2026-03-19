"use client";

import { Button } from "@/components/ui/button";
import { useState } from "react";

export function EmptyState() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleGenerate() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/generate", { method: "POST" });
      const data = await res.json();
      if (data.success || data.briefId) {
        window.location.href = `/brief/${data.date}`;
      } else {
        setError(data.error || "Failed to generate brief");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Network error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col items-center justify-center h-full gap-8 p-8 animate-fade-in">
      <div className="text-center space-y-4">
        <div className="w-16 h-16 rounded-2xl bg-primary/15 flex items-center justify-center mx-auto mb-6">
          <span className="text-primary text-2xl font-bold">NB</span>
        </div>
        <h1 className="text-4xl font-bold tracking-tight">
          Daily News Brief
        </h1>
        <p className="text-lg text-muted-foreground max-w-md leading-relaxed">
          Generate your first AI-powered news digest. We'll pull the latest
          tech news and summarize it for you.
        </p>
      </div>
      <Button
        size="lg"
        className="h-12 px-8 text-[16px] font-medium bg-primary hover:bg-primary/90 transition-all duration-200 hover:shadow-[0_0_30px_rgba(59,130,246,0.3)]"
        onClick={handleGenerate}
        disabled={loading}
      >
        {loading ? (
          <span className="flex items-center gap-2.5">
            <span className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
            Generating your brief...
          </span>
        ) : (
          "Generate Today's Brief"
        )}
      </Button>
      {error && (
        <div className="text-[14px] text-destructive max-w-md text-center bg-destructive/10 px-4 py-3 rounded-lg border border-destructive/20">
          {error}
        </div>
      )}
    </div>
  );
}
