interface SourceBreakdownProps {
  newsapi: number;
  hackernews: number;
  rss: number;
}

const SOURCE_CONFIG = [
  { key: "newsapi", label: "NewsAPI", color: "bg-blue-400", textColor: "text-blue-400" },
  { key: "hackernews", label: "Hacker News", color: "bg-orange-400", textColor: "text-orange-400" },
  { key: "rss", label: "RSS", color: "bg-emerald-400", textColor: "text-emerald-400" },
] as const;

export function SourceBreakdown({ newsapi, hackernews, rss }: SourceBreakdownProps) {
  const total = newsapi + hackernews + rss;
  if (total === 0) return null;

  const counts: Record<string, number> = { newsapi, hackernews, rss };

  return (
    <div className="rounded-xl border border-border/60 p-4 animate-fade-in">
      <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-[0.1em] mb-3">
        Source Distribution
      </p>

      {/* Stacked bar */}
      <div className="flex h-3 rounded-full overflow-hidden mb-3">
        {SOURCE_CONFIG.map(({ key, color }) => {
          const pct = (counts[key] / total) * 100;
          if (pct === 0) return null;
          return (
            <div
              key={key}
              className={`${color} transition-all duration-500`}
              style={{ width: `${pct}%` }}
            />
          );
        })}
      </div>

      {/* Labels */}
      <div className="flex items-center gap-4">
        {SOURCE_CONFIG.map(({ key, label, textColor }) => (
          <div key={key} className="flex items-center gap-1.5 text-[12px]">
            <span className={textColor + " font-bold"}>{counts[key]}</span>
            <span className="text-muted-foreground/60">{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
