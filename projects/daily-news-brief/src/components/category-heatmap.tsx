interface CategoryData {
  name: string;
  slug: string;
  articleCount: number;
  avgRelevance: number;
  sentimentBreakdown: Record<string, number>;
}

interface CategoryHeatmapProps {
  categories: CategoryData[];
}

const SENTIMENT_COLORS: Record<string, { bg: string; text: string; label: string }> = {
  excited: { bg: "bg-emerald-400", text: "text-emerald-400", label: "Excited" },
  neutral: { bg: "bg-zinc-400", text: "text-zinc-400", label: "Neutral" },
  concerned: { bg: "bg-amber-400", text: "text-amber-400", label: "Concerned" },
  skeptical: { bg: "bg-red-400", text: "text-red-400", label: "Skeptical" },
};

function RelevanceBar({ value, max }: { value: number; max: number }) {
  const pct = max > 0 ? (value / max) * 100 : 0;
  const color =
    pct >= 75
      ? "bg-emerald-400"
      : pct >= 50
      ? "bg-blue-400"
      : pct >= 25
      ? "bg-amber-400"
      : "bg-zinc-400";

  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 rounded-full bg-muted/40 overflow-hidden">
        <div
          className={`h-full rounded-full ${color} transition-all duration-500`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-[12px] font-bold text-foreground/70 w-8 text-right tabular-nums">
        {value.toFixed(1)}
      </span>
    </div>
  );
}

function DominantSentiment({ breakdown }: { breakdown: Record<string, number> }) {
  const total = Object.values(breakdown).reduce((s, v) => s + v, 0);
  if (total === 0) return <span className="text-[12px] text-muted-foreground/30">—</span>;

  const sorted = Object.entries(breakdown)
    .filter(([, v]) => v > 0)
    .sort(([, a], [, b]) => b - a);

  const [topSentiment, topCount] = sorted[0];
  const topPct = Math.round((topCount / total) * 100);
  const config = SENTIMENT_COLORS[topSentiment];

  return (
    <div className="flex items-center gap-1.5">
      <span className={`w-2 h-2 rounded-full ${config?.bg || "bg-zinc-400"}`} />
      <span className={`text-[12px] font-semibold ${config?.text || "text-zinc-400"}`}>
        {config?.label || topSentiment}
      </span>
      <span className="text-[11px] text-muted-foreground/40">
        {topPct}%
      </span>
    </div>
  );
}

export function CategoryHeatmap({ categories }: CategoryHeatmapProps) {
  if (categories.length === 0) return null;

  const maxArticles = Math.max(...categories.map((c) => c.articleCount));
  const maxRelevance = Math.max(...categories.map((c) => c.avgRelevance));

  // Sort by article count descending for better readability
  const sorted = [...categories].sort((a, b) => b.articleCount - a.articleCount);

  return (
    <div className="animate-slide-up">
      <div className="flex items-center gap-3 mb-5">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/25 to-primary/10 flex items-center justify-center">
          <span className="text-primary text-lg font-bold">::</span>
        </div>
        <div>
          <h2 className="text-lg font-bold tracking-tight">Category Overview</h2>
          <p className="text-[13px] text-muted-foreground">
            Coverage volume, relevance scores, and dominant sentiment per category
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {sorted.map((cat) => {
          const totalSentiment = Object.values(cat.sentimentBreakdown).reduce(
            (s, v) => s + v,
            0
          );

          return (
            <div
              key={cat.slug}
              className="rounded-xl border border-border/60 p-4 hover:border-primary/20 transition-colors"
            >
              <div className="flex items-start justify-between gap-4 mb-3">
                <h3 className="text-[14px] font-semibold">{cat.name}</h3>
                <div className="flex items-center gap-1.5 shrink-0">
                  <span className="text-[20px] font-bold text-primary leading-none">
                    {cat.articleCount}
                  </span>
                  <span className="text-[11px] text-muted-foreground/50">
                    {cat.articleCount === 1 ? "article" : "articles"}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                {/* Relevance */}
                <div>
                  <p className="text-[10px] font-semibold text-muted-foreground/50 uppercase tracking-[0.1em] mb-1.5">
                    Avg Relevance
                  </p>
                  <RelevanceBar value={cat.avgRelevance} max={maxRelevance} />
                </div>

                {/* Sentiment */}
                <div>
                  <p className="text-[10px] font-semibold text-muted-foreground/50 uppercase tracking-[0.1em] mb-1.5">
                    Dominant Tone
                  </p>
                  <div className="flex items-center gap-3">
                    <DominantSentiment breakdown={cat.sentimentBreakdown} />
                    {/* Mini sentiment bar */}
                    {totalSentiment > 0 && (
                      <div className="flex-1 flex h-2 rounded-full overflow-hidden">
                        {Object.entries(cat.sentimentBreakdown).map(
                          ([sentiment, count]) => {
                            if (count === 0) return null;
                            const pct = (count / totalSentiment) * 100;
                            const config = SENTIMENT_COLORS[sentiment];
                            return (
                              <div
                                key={sentiment}
                                className={`${config?.bg || "bg-zinc-400"} transition-all duration-300`}
                                style={{ width: `${pct}%` }}
                                title={`${config?.label || sentiment}: ${count} (${Math.round(pct)}%)`}
                              />
                            );
                          }
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 mt-3 px-1">
        {Object.entries(SENTIMENT_COLORS).map(([key, config]) => (
          <div key={key} className="flex items-center gap-1.5 text-[11px] text-muted-foreground/60">
            <span className={`w-2 h-2 rounded-full ${config.bg}`} />
            {config.label}
          </div>
        ))}
      </div>
    </div>
  );
}
