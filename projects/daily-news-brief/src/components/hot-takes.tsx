"use client";

interface Article {
  id: number;
  title: string;
  url: string;
  source: string;
  tldr: string;
  sourceCount: number | null;
  sentimentTag?: string | null;
}

interface HotTakesProps {
  articles: Article[];
}

const SENTIMENT_DOT: Record<string, { color: string; label: string }> = {
  excited: { color: "bg-emerald-400", label: "Excited" },
  neutral: { color: "bg-zinc-400", label: "Neutral" },
  concerned: { color: "bg-amber-400", label: "Concerned" },
  skeptical: { color: "bg-red-400", label: "Skeptical" },
};

export function HotTakes({ articles }: HotTakesProps) {
  if (articles.length === 0) return null;

  // Already sorted by corroboration from the parent, but ensure it
  const sorted = [...articles].sort(
    (a, b) => (b.sourceCount ?? 1) - (a.sourceCount ?? 1)
  );

  return (
    <div className="animate-slide-up">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-500/25 to-orange-600/10 flex items-center justify-center">
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#fb923c"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M12 2L2 7l10 5 10-5-10-5z" />
            <path d="M2 17l10 5 10-5" />
            <path d="M2 12l10 5 10-5" />
          </svg>
        </div>
        <div>
          <h2 className="text-lg font-bold tracking-tight">Most Discussed</h2>
          <p className="text-[13px] text-muted-foreground">
            Corroborated across the most sources
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {sorted.map((article, i) => {
          const sentiment = SENTIMENT_DOT[article.sentimentTag || "neutral"] || SENTIMENT_DOT.neutral;
          const sources = article.sourceCount ?? 1;

          return (
            <div
              key={article.id}
              className="group rounded-xl border border-border/60 p-4 transition-all duration-300 hover:border-orange-500/25 hover:shadow-[0_0_20px_rgba(249,115,22,0.08)] animate-slide-up"
              style={{ animationDelay: `${i * 0.06}s`, animationFillMode: "both" }}
            >
              <div className="flex items-start gap-4">
                {/* Corroboration count - prominent */}
                <div className="shrink-0 flex flex-col items-center gap-0.5 min-w-[52px]">
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="#f97316"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M12 19V5m0 0l-7 7m7-7l7 7" />
                  </svg>
                  <span className="text-[22px] font-bold text-orange-400 leading-none tabular-nums">
                    {sources}
                  </span>
                  <span className="text-[10px] text-muted-foreground/40">sources</span>
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  {/* Title */}
                  <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-semibold text-[14px] leading-snug hover:text-amber-400 transition-colors duration-200 inline-block"
                  >
                    {article.title}
                    <span className="inline-block ml-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200 text-amber-400/60 text-xs">
                      &#8599;
                    </span>
                  </a>

                  {/* Meta row: source badge, sentiment */}
                  <div className="flex items-center gap-3 mt-2">
                    {/* Source badge */}
                    <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full bg-orange-500/15 text-orange-400">
                      {article.source === "hackernews" ? "Hacker News" : article.source}
                    </span>

                    {/* Sentiment dot */}
                    <span className="flex items-center gap-1 text-[11px] text-muted-foreground/50">
                      <span
                        className={`w-2 h-2 rounded-full ${sentiment.color}`}
                        title={sentiment.label}
                      />
                      {sentiment.label}
                    </span>
                  </div>

                  {/* TL;DR */}
                  <p className="text-[13px] text-muted-foreground mt-2.5 leading-relaxed">
                    {article.tldr}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
