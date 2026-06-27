"use client";

import { SaveToSheetButton } from "./SaveToSheetButton";

interface ContentIdea {
  idea: string;
  reasoning: string;
  formatSuggestion: string | null;
  estimatedInterest: string | null;
}

interface YouTubeContentIdeasProps {
  ideas: ContentIdea[];
}

const INTEREST_STYLES: Record<string, string> = {
  high: "text-green-400 bg-green-500/10 border-green-500/20",
  medium: "text-amber-400 bg-amber-500/10 border-amber-500/20",
  low: "text-zinc-400 bg-zinc-500/10 border-zinc-500/20",
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

export function YouTubeContentIdeas({ ideas }: YouTubeContentIdeasProps) {
  if (!ideas.length) return null;

  return (
    <div>
      <p className="text-[11px] font-semibold text-muted-foreground/60 uppercase tracking-[0.15em] mb-4">
        Content Opportunities
      </p>
      <div className="space-y-3">
        {ideas.map((idea, i) => {
          const interestStyle =
            INTEREST_STYLES[idea.estimatedInterest || "low"] || INTEREST_STYLES.low;
          const formatStyle =
            FORMAT_STYLES[idea.formatSuggestion || ""] ||
            "text-zinc-400 bg-zinc-500/10 border-zinc-500/20";

          return (
            <div
              key={i}
              className="rounded-xl border border-border/50 bg-card/30 p-4 hover:border-rose-500/20 transition-colors"
            >
              <div className="flex items-start justify-between gap-3 mb-2">
                <h3 className="text-sm font-semibold leading-snug">{idea.idea}</h3>
                <div className="flex items-center gap-1.5 shrink-0">
                  <SaveToSheetButton
                    payload={{ type: "idea", title: idea.idea, formatSuggestion: idea.formatSuggestion }}
                  />
                  {idea.estimatedInterest && (
                    <span
                      className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${interestStyle}`}
                    >
                      {idea.estimatedInterest}
                    </span>
                  )}
                  {idea.formatSuggestion && (
                    <span
                      className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${formatStyle}`}
                    >
                      {idea.formatSuggestion}
                    </span>
                  )}
                </div>
              </div>
              <p className="text-xs text-muted-foreground/70 leading-relaxed">
                {idea.reasoning}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
