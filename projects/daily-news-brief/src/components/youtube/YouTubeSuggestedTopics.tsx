"use client";

import { SaveToSheetButton } from "./SaveToSheetButton";

interface SuggestedTopic {
  topic: string;
  angle: string;
  whyNow: string;
  targetFormat: string | null;
  competitionLevel: string | null;
  referenceVideos: string[];
}

interface YouTubeSuggestedTopicsProps {
  topics: SuggestedTopic[];
}

const COMPETITION_STYLES: Record<string, string> = {
  low: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
  medium: "text-amber-400 bg-amber-500/10 border-amber-500/20",
  high: "text-red-400 bg-red-500/10 border-red-500/20",
};

const FORMAT_STYLES: Record<string, string> = {
  tutorial: "text-rose-400 bg-rose-500/10 border-rose-500/20",
  opinion: "text-sky-400 bg-sky-500/10 border-sky-500/20",
  news: "text-amber-400 bg-amber-500/10 border-amber-500/20",
  demo: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
  explainer: "text-indigo-400 bg-indigo-500/10 border-indigo-500/20",
  comparison: "text-orange-400 bg-orange-500/10 border-orange-500/20",
  "deep-dive": "text-fuchsia-400 bg-fuchsia-500/10 border-fuchsia-500/20",
};

export function YouTubeSuggestedTopics({ topics }: YouTubeSuggestedTopicsProps) {
  if (!topics.length) return null;

  return (
    <div>
      <p className="text-[11px] font-semibold text-muted-foreground/60 uppercase tracking-[0.15em] mb-4">
        Suggested Topics to Create
      </p>
      <div className="space-y-4">
        {topics.map((t, i) => {
          const compStyle =
            COMPETITION_STYLES[t.competitionLevel || "medium"] || COMPETITION_STYLES.medium;
          const fmtStyle =
            FORMAT_STYLES[t.targetFormat || ""] ||
            "text-zinc-400 bg-zinc-500/10 border-zinc-500/20";

          return (
            <div
              key={i}
              className="rounded-xl border border-border/50 bg-card/30 p-4 hover:border-rose-500/20 transition-colors"
            >
              <div className="flex items-start justify-between gap-3 mb-2">
                <h3 className="text-sm font-semibold leading-snug">{t.topic}</h3>
                <div className="flex items-center gap-1.5 shrink-0">
                  <SaveToSheetButton
                    payload={{ type: "idea", title: t.topic, formatSuggestion: t.targetFormat }}
                  />
                  {t.competitionLevel && (
                    <span
                      className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${compStyle}`}
                    >
                      {t.competitionLevel} comp
                    </span>
                  )}
                  {t.targetFormat && (
                    <span
                      className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${fmtStyle}`}
                    >
                      {t.targetFormat}
                    </span>
                  )}
                </div>
              </div>

              <p className="text-xs text-muted-foreground/80 leading-relaxed mb-3">
                {t.angle}
              </p>

              <blockquote className="border-l-2 border-amber-500/40 pl-3 mb-3">
                <p className="text-[11px] text-amber-400/80 italic leading-relaxed">
                  {t.whyNow}
                </p>
              </blockquote>

              {t.referenceVideos.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {t.referenceVideos.map((ref, ri) => (
                    <span
                      key={ri}
                      className="text-[10px] text-muted-foreground/40 bg-muted/20 px-2 py-0.5 rounded-full border border-border/30 line-clamp-1 max-w-[200px]"
                    >
                      {ref}
                    </span>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
