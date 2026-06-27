"use client";

import { SaveToSheetButton } from "./SaveToSheetButton";

interface TrendingTopic {
  topic: string;
  mentionCount: number;
  channels: string[];
  sentiment: string | null;
  summary: string;
}

interface YouTubeTrendingTopicsProps {
  topics: TrendingTopic[];
}

const SENTIMENT_COLORS: Record<string, string> = {
  bullish: "text-green-400 bg-green-500/10 border-green-500/20",
  cautious: "text-amber-400 bg-amber-500/10 border-amber-500/20",
  neutral: "text-zinc-400 bg-zinc-500/10 border-zinc-500/20",
  "hype-driven": "text-violet-400 bg-violet-500/10 border-violet-500/20",
  mixed: "text-violet-400 bg-violet-500/10 border-violet-500/20",
};

export function YouTubeTrendingTopics({ topics }: YouTubeTrendingTopicsProps) {
  if (!topics.length) return null;

  return (
    <div>
      <p className="text-[11px] font-semibold text-muted-foreground/60 uppercase tracking-[0.15em] mb-4">
        Trending Topics
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {topics.map((t, i) => {
          const sentimentColor =
            SENTIMENT_COLORS[t.sentiment || "neutral"] || SENTIMENT_COLORS.neutral;
          return (
            <div
              key={i}
              className="rounded-xl border border-border/50 bg-card/30 p-4 hover:border-rose-500/20 hover:bg-rose-500/[0.02] transition-all duration-200"
            >
              <div className="flex items-start justify-between gap-3 mb-2">
                <h3 className="font-semibold text-sm leading-snug">{t.topic}</h3>
                <div className="flex items-center gap-1.5 shrink-0">
                  <SaveToSheetButton
                    payload={{ type: "topic", topic: t.topic, mentionCount: t.mentionCount, channels: t.channels }}
                  />
                  <span className="text-xs font-bold text-rose-400">
                    {t.mentionCount}x
                  </span>
                </div>
              </div>

              <p className="text-xs text-muted-foreground/70 leading-relaxed mb-3">
                {t.summary}
              </p>

              <div className="flex items-center gap-2 flex-wrap">
                {t.sentiment && (
                  <span
                    className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${sentimentColor}`}
                  >
                    {t.sentiment}
                  </span>
                )}
                {t.channels.slice(0, 3).map((ch, ci) => (
                  <span
                    key={ci}
                    className="text-[10px] text-muted-foreground/50 bg-muted/20 px-2 py-0.5 rounded-full border border-border/30"
                  >
                    {ch}
                  </span>
                ))}
                {t.channels.length > 3 && (
                  <span className="text-[10px] text-muted-foreground/40">
                    +{t.channels.length - 3}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
