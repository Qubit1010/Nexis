"use client";

import { useEffect, useState } from "react";

interface Trend {
  id: number;
  title: string;
  slug: string;
  summary: string;
  momentumSignal: string;
  contentPotentialScore: number | null;
  sourceCount: number | null;
  categorySlugs: string[];
  firstSeenDate: string;
  lastSeenDate: string;
}

interface TrendingNowProps {
  trends: Trend[];
  date: string;
}

interface HistoryPoint {
  date: string;
  score: number;
  momentum: string;
}

const MOMENTUM_CONFIG: Record<
  string,
  { label: string; icon: string; color: string; bg: string; arrow: string }
> = {
  rising: {
    label: "Rising",
    icon: "\u2191",
    color: "text-emerald-400",
    bg: "bg-emerald-500/15",
    arrow: "#34d399",
  },
  steady: {
    label: "Steady",
    icon: "\u2192",
    color: "text-amber-400",
    bg: "bg-amber-500/15",
    arrow: "#f59e0b",
  },
  cooling: {
    label: "Cooling",
    icon: "\u2193",
    color: "text-red-400",
    bg: "bg-red-500/15",
    arrow: "#f87171",
  },
};

const CATEGORY_LABELS: Record<string, { label: string; color: string }> = {
  "ai-models-breakthroughs": { label: "Models", color: "bg-blue-500/15 text-blue-400" },
  "ai-tools-products": { label: "Tools", color: "bg-cyan-500/15 text-cyan-400" },
  "ai-business-strategy": { label: "Business", color: "bg-violet-500/15 text-violet-400" },
  "ai-automation-workflows": { label: "Automation", color: "bg-amber-500/15 text-amber-400" },
  "ai-content-creators": { label: "Content", color: "bg-emerald-500/15 text-emerald-400" },
  "ai-ethics-safety": { label: "Ethics", color: "bg-rose-500/15 text-rose-400" },
};

function MomentumArrow({ signal }: { signal: string }) {
  const config = MOMENTUM_CONFIG[signal] || MOMENTUM_CONFIG.steady;
  const paths: Record<string, string> = {
    rising: "M12 19V5m0 0l-7 7m7-7l7 7",
    steady: "M5 12h14m0 0l-7-7m7 7l-7 7",
    cooling: "M12 5v14m0 0l7-7m-7 7l-7-7",
  };

  return (
    <div className={`flex items-center gap-1.5 ${config.bg} rounded-lg px-2.5 py-1.5`}>
      <svg
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke={config.arrow}
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d={paths[signal] || paths.steady} />
      </svg>
      <span className={`text-[11px] font-bold ${config.color}`}>{config.label}</span>
    </div>
  );
}

function Sparkline({ points }: { points: HistoryPoint[] }) {
  if (points.length < 2) return null;

  const w = 120;
  const h = 36;
  const padding = 4;
  const scores = points.map((p) => p.score);
  const min = Math.min(...scores);
  const max = Math.max(...scores);
  const range = max - min || 1;

  const coords = points.map((p, i) => ({
    x: padding + (i / (points.length - 1)) * (w - padding * 2),
    y: padding + (1 - (p.score - min) / range) * (h - padding * 2),
  }));

  const d = coords.map((c, i) => `${i === 0 ? "M" : "L"} ${c.x} ${c.y}`).join(" ");

  // Area fill path
  const areaD = `${d} L ${coords[coords.length - 1].x} ${h} L ${coords[0].x} ${h} Z`;

  const lastMomentum = points[points.length - 1].momentum;
  const color =
    lastMomentum === "rising"
      ? "#34d399"
      : lastMomentum === "cooling"
        ? "#f87171"
        : "#f59e0b";

  return (
    <div className="mt-3">
      <p className="text-[10px] text-muted-foreground/50 mb-1">7-day trend</p>
      <svg width={w} height={h} className="w-full">
        <defs>
          <linearGradient id={`spark-fill-${lastMomentum}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.2" />
            <stop offset="100%" stopColor={color} stopOpacity="0" />
          </linearGradient>
        </defs>
        <path d={areaD} fill={`url(#spark-fill-${lastMomentum})`} />
        <path
          d={d}
          fill="none"
          stroke={color}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <circle
          cx={coords[coords.length - 1].x}
          cy={coords[coords.length - 1].y}
          r="3"
          fill={color}
        />
      </svg>
    </div>
  );
}

function ContentPotentialBar({ score }: { score: number }) {
  const maxScore = 10;
  const pct = Math.min((score / maxScore) * 100, 100);
  const barColor =
    pct >= 70 ? "bg-emerald-400" : pct >= 40 ? "bg-amber-400" : "bg-zinc-500";

  return (
    <div className="flex items-center gap-2 mt-2">
      <span className="text-[10px] text-muted-foreground/50 shrink-0 w-16">Potential</span>
      <div className="flex-1 h-1.5 rounded-full bg-muted/30 overflow-hidden">
        <div
          className={`h-full rounded-full ${barColor} transition-all duration-700`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-[11px] font-bold text-foreground/70 tabular-nums w-5 text-right">
        {score}
      </span>
    </div>
  );
}

export function TrendingNow({ trends, date }: TrendingNowProps) {
  const [history, setHistory] = useState<Record<string, HistoryPoint[]>>({});

  useEffect(() => {
    if (trends.length === 0) return;
    const slugs = trends.map((t) => t.slug).join(",");
    fetch(`/api/trends/history?slugs=${encodeURIComponent(slugs)}&date=${date}`)
      .then((r) => r.json())
      .then(setHistory)
      .catch(() => {});
  }, [trends, date]);

  if (trends.length === 0) return null;

  return (
    <div className="animate-slide-up">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500/25 to-emerald-600/10 flex items-center justify-center">
          <span className="text-emerald-400 text-lg font-bold">#</span>
        </div>
        <div>
          <h2 className="text-lg font-bold tracking-tight">Trending Now</h2>
          <p className="text-[13px] text-muted-foreground">
            Cross-source trends across today&apos;s coverage
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {trends.map((trend, i) => {
          const potentialScore = trend.contentPotentialScore ?? 0;
          const sparklineData = history[trend.slug] || [];

          return (
            <div
              key={trend.id}
              className="group relative rounded-xl border border-border/60 p-5 transition-all duration-300 hover:border-amber-500/30 hover:shadow-[0_0_24px_rgba(245,158,11,0.08)] animate-slide-up"
              style={{
                animationDelay: `${i * 0.07}s`,
                animationFillMode: "both",
              }}
            >
              {/* Gradient glow border on hover */}
              <div className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none bg-gradient-to-br from-amber-500/5 via-transparent to-teal-500/5" />

              <div className="relative">
                {/* Header: momentum + categories */}
                <div className="flex items-center justify-between mb-3">
                  <MomentumArrow signal={trend.momentumSignal} />
                  {trend.sourceCount && trend.sourceCount > 1 && (
                    <span className="text-[11px] text-muted-foreground/50">
                      {trend.sourceCount} sources
                    </span>
                  )}
                </div>

                {/* Title */}
                <h3 className="font-semibold text-[15px] leading-snug mb-2">
                  {trend.title}
                </h3>

                {/* Summary */}
                <p className="text-[13px] text-muted-foreground leading-relaxed line-clamp-3">
                  {trend.summary}
                </p>

                {/* Content potential bar */}
                <ContentPotentialBar score={potentialScore} />

                {/* Category pills */}
                <div className="flex flex-wrap gap-1.5 mt-3">
                  {trend.categorySlugs.map((slug) => {
                    const cat = CATEGORY_LABELS[slug];
                    return (
                      <span
                        key={slug}
                        className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${cat?.color || "bg-zinc-500/15 text-zinc-400"}`}
                      >
                        {cat?.label || slug}
                      </span>
                    );
                  })}
                </div>

                {/* Sparkline */}
                {sparklineData.length >= 2 && <Sparkline points={sparklineData} />}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
