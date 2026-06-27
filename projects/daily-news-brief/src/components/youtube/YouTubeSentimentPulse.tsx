interface YouTubeSentiment {
  overall: string;
  confidence: number;
  reasoning: string;
  signals: Array<{ signal: string; weight: string }>;
}

interface YouTubeSentimentPulseProps {
  sentiment: YouTubeSentiment | null;
}

const SENTIMENT_CONFIG: Record<
  string,
  { icon: string; color: string; bg: string; border: string; glow: string }
> = {
  bullish: {
    icon: "▲",
    color: "text-green-400",
    bg: "from-green-500/12 to-green-600/4",
    border: "border-green-500/20",
    glow: "rgba(34,197,94,0.4)",
  },
  cautious: {
    icon: "◆",
    color: "text-amber-400",
    bg: "from-amber-500/12 to-amber-600/4",
    border: "border-amber-500/20",
    glow: "rgba(245,158,11,0.4)",
  },
  mixed: {
    icon: "●",
    color: "text-violet-400",
    bg: "from-violet-500/12 to-violet-600/4",
    border: "border-violet-500/20",
    glow: "rgba(167,139,250,0.4)",
  },
  "hype-driven": {
    icon: "⚡",
    color: "text-violet-400",
    bg: "from-violet-500/12 to-purple-600/4",
    border: "border-violet-500/20",
    glow: "rgba(167,139,250,0.4)",
  },
  bearish: {
    icon: "▼",
    color: "text-red-400",
    bg: "from-red-500/12 to-red-600/4",
    border: "border-red-500/20",
    glow: "rgba(239,68,68,0.4)",
  },
  neutral: {
    icon: "↔",
    color: "text-zinc-400",
    bg: "from-zinc-500/12 to-zinc-600/4",
    border: "border-zinc-500/20",
    glow: "rgba(161,161,170,0.4)",
  },
};

const WEIGHT_CONFIG: Record<string, string> = {
  strong: "text-rose-400 bg-rose-500/10 border-rose-500/20",
  moderate: "text-amber-400 bg-amber-500/10 border-amber-500/20",
  weak: "text-zinc-400 bg-zinc-500/10 border-zinc-500/20",
};

export function YouTubeSentimentPulse({ sentiment }: YouTubeSentimentPulseProps) {
  if (!sentiment) return null;

  const config = SENTIMENT_CONFIG[sentiment.overall] || SENTIMENT_CONFIG.mixed;
  const label = sentiment.overall.replace("-", " ");

  return (
    <div className="animate-slide-up">
      <div
        className={`rounded-xl border ${config.border} bg-gradient-to-br ${config.bg} p-6 transition-all duration-300 hover:shadow-lg`}
      >
        <div className="flex items-center gap-4 mb-4">
          <div
            className={`w-12 h-12 rounded-xl flex items-center justify-center text-2xl ${config.color}`}
            style={{
              ["--glow-color" as string]: config.glow,
              animation: "pulse-glow 2.5s ease-in-out infinite",
              background: "oklch(0.16 0.02 258)",
            }}
          >
            {config.icon}
          </div>
          <div>
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-[0.12em]">
              YouTube Space Sentiment
            </p>
            <span
              className={`inline-block mt-1 text-sm font-bold px-3 py-0.5 rounded-full ${config.color}`}
              style={{ background: "oklch(0.16 0.02 258 / 0.6)" }}
            >
              {label.charAt(0).toUpperCase() + label.slice(1)}
            </span>
            {sentiment.confidence > 0 && (
              <span className="ml-2 text-xs text-muted-foreground/50">
                {Math.round(sentiment.confidence * 100)}% confidence
              </span>
            )}
          </div>
        </div>

        <p className="text-sm text-foreground/80 leading-relaxed">{sentiment.reasoning}</p>

        {sentiment.signals && sentiment.signals.length > 0 && (
          <div className="mt-4 space-y-2">
            <p className="text-[11px] font-semibold text-muted-foreground/60 uppercase tracking-[0.12em]">
              Signals
            </p>
            <div className="flex flex-wrap gap-2">
              {sentiment.signals.map((s, i) => (
                <span
                  key={i}
                  className={`inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border ${WEIGHT_CONFIG[s.weight] || WEIGHT_CONFIG.weak}`}
                >
                  {s.signal}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
