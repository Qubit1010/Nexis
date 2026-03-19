interface SentimentPulseProps {
  sentiment: {
    label: string;
    summary: string;
  } | null;
  topTakeaway: string | null;
}

const SENTIMENT_CONFIG: Record<
  string,
  { icon: string; color: string; bg: string; border: string; glow: string }
> = {
  bullish: {
    icon: "\u25B2",
    color: "text-green-400",
    bg: "from-green-500/12 to-green-600/4",
    border: "border-green-500/20",
    glow: "rgba(34,197,94,0.4)",
  },
  cautious: {
    icon: "\u25C6",
    color: "text-amber-400",
    bg: "from-amber-500/12 to-amber-600/4",
    border: "border-amber-500/20",
    glow: "rgba(245,158,11,0.4)",
  },
  mixed: {
    icon: "\u25CF",
    color: "text-violet-400",
    bg: "from-violet-500/12 to-violet-600/4",
    border: "border-violet-500/20",
    glow: "rgba(167,139,250,0.4)",
  },
  bearish: {
    icon: "\u25BC",
    color: "text-red-400",
    bg: "from-red-500/12 to-red-600/4",
    border: "border-red-500/20",
    glow: "rgba(239,68,68,0.4)",
  },
};

export function SentimentPulse({
  sentiment,
  topTakeaway,
}: SentimentPulseProps) {
  if (!sentiment) return null;

  const config =
    SENTIMENT_CONFIG[sentiment.label] || SENTIMENT_CONFIG.mixed;

  return (
    <div className="animate-slide-up">
      <div
        className={`rounded-xl border ${config.border} bg-gradient-to-br ${config.bg} p-6 transition-all duration-300 hover:shadow-lg`}
      >
        {/* Sentiment header */}
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
              AI Space Sentiment
            </p>
            <span
              className={`inline-block mt-1 text-sm font-bold px-3 py-0.5 rounded-full ${config.color}`}
              style={{ background: "oklch(0.16 0.02 258 / 0.6)" }}
            >
              {sentiment.label.charAt(0).toUpperCase() +
                sentiment.label.slice(1)}
            </span>
          </div>
        </div>

        {/* Summary */}
        <p className="text-sm text-foreground/80 leading-relaxed">
          {sentiment.summary}
        </p>

        {/* Top takeaway */}
        {topTakeaway && (
          <div className="mt-5 pl-4 border-l-2 border-primary/60">
            <p className="text-[11px] font-semibold text-primary uppercase tracking-[0.12em] mb-1.5">
              If you read nothing else today
            </p>
            <p className="text-base font-medium text-foreground/95 leading-relaxed">
              {topTakeaway}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
