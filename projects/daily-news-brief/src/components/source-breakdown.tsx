interface SourceBreakdownProps {
  /** Article counts keyed by display source label (e.g. "Reddit", "GitHub", "Web"). */
  counts: Record<string, number>;
}

// Stable color per known source label; anything else falls back to a neutral slate.
const SOURCE_COLORS: Record<string, { color: string; textColor: string }> = {
  Reddit: { color: "bg-orange-500", textColor: "text-orange-500" },
  "Hacker News": { color: "bg-orange-400", textColor: "text-orange-400" },
  GitHub: { color: "bg-violet-400", textColor: "text-violet-400" },
  Web: { color: "bg-blue-400", textColor: "text-blue-400" },
  X: { color: "bg-sky-400", textColor: "text-sky-400" },
  YouTube: { color: "bg-red-400", textColor: "text-red-400" },
  TikTok: { color: "bg-pink-400", textColor: "text-pink-400" },
  Instagram: { color: "bg-fuchsia-400", textColor: "text-fuchsia-400" },
  Threads: { color: "bg-zinc-400", textColor: "text-zinc-400" },
  Polymarket: { color: "bg-emerald-400", textColor: "text-emerald-400" },
};

const FALLBACK = { color: "bg-slate-400", textColor: "text-slate-400" };

export function SourceBreakdown({ counts }: SourceBreakdownProps) {
  const entries = Object.entries(counts)
    .filter(([, n]) => n > 0)
    .sort((a, b) => b[1] - a[1]);
  const total = entries.reduce((sum, [, n]) => sum + n, 0);
  if (total === 0) return null;

  return (
    <div className="rounded-xl border border-border/60 p-4 animate-fade-in">
      <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-[0.1em] mb-3">
        Source Distribution
      </p>

      {/* Stacked bar */}
      <div className="flex h-3 rounded-full overflow-hidden mb-3">
        {entries.map(([label, n]) => {
          const pct = (n / total) * 100;
          const { color } = SOURCE_COLORS[label] || FALLBACK;
          return (
            <div
              key={label}
              className={`${color} transition-all duration-500`}
              style={{ width: `${pct}%` }}
            />
          );
        })}
      </div>

      {/* Labels */}
      <div className="flex flex-wrap items-center gap-4">
        {entries.map(([label, n]) => {
          const { textColor } = SOURCE_COLORS[label] || FALLBACK;
          return (
            <div key={label} className="flex items-center gap-1.5 text-[12px]">
              <span className={textColor + " font-bold"}>{n}</span>
              <span className="text-muted-foreground/60">{label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
