interface YouTubeFormatDistributionProps {
  distribution: Record<string, number>;
}

const FORMAT_COLORS: Record<string, string> = {
  tutorial: "bg-rose-500",
  opinion: "bg-sky-500",
  news: "bg-amber-500",
  demo: "bg-emerald-500",
  interview: "bg-orange-500",
  explainer: "bg-indigo-500",
  comparison: "bg-teal-500",
  "deep-dive": "bg-pink-500",
};

export function YouTubeFormatDistribution({ distribution }: YouTubeFormatDistributionProps) {
  const entries = Object.entries(distribution).filter(([, v]) => v > 0);
  if (!entries.length) return null;

  const total = entries.reduce((sum, [, v]) => sum + v, 0);
  const sorted = [...entries].sort((a, b) => b[1] - a[1]);

  return (
    <div>
      <p className="text-[11px] font-semibold text-muted-foreground/60 uppercase tracking-[0.15em] mb-4">
        Format Distribution
      </p>
      <div className="rounded-xl border border-border/50 bg-card/30 p-5 space-y-3">
        {sorted.map(([format, count]) => {
          const pct = total > 0 ? Math.round((count / total) * 100) : 0;
          const barColor = FORMAT_COLORS[format] || "bg-zinc-500";

          return (
            <div key={format}>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-medium capitalize">{format}</span>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground/50">{count}</span>
                  <span className="text-xs font-semibold text-muted-foreground/70 w-8 text-right">
                    {pct}%
                  </span>
                </div>
              </div>
              <div className="h-1.5 rounded-full bg-muted/30 overflow-hidden">
                <div
                  className={`h-full w-full rounded-full ${barColor} opacity-70 origin-left`}
                  style={{
                    transform: `scaleX(${pct / 100})`,
                    transition: "transform 0.5s ease",
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
