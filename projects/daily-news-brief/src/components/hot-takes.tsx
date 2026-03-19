"use client";

interface Article {
  id: number;
  title: string;
  url: string;
  source: string;
  tldr: string;
  engagementScore: number | null;
  commentCount: number | null;
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

function formatEngagement(score: number): string {
  if (score >= 1000) return `${(score / 1000).toFixed(1)}k`;
  return String(score);
}

function buildHNSearchUrl(title: string): string {
  return `https://news.ycombinator.com/item?id=${encodeURIComponent(title)}`;
}

export function HotTakes({ articles }: HotTakesProps) {
  if (articles.length === 0) return null;

  // Already sorted by engagement from the parent, but ensure it
  const sorted = [...articles].sort(
    (a, b) => (b.engagementScore ?? 0) - (a.engagementScore ?? 0)
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
            Highest engagement from Hacker News
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {sorted.map((article, i) => {
          const sentiment = SENTIMENT_DOT[article.sentimentTag || "neutral"] || SENTIMENT_DOT.neutral;
          const engagement = article.engagementScore ?? 0;
          const comments = article.commentCount ?? 0;

          return (
            <div
              key={article.id}
              className="group rounded-xl border border-border/60 p-4 transition-all duration-300 hover:border-orange-500/25 hover:shadow-[0_0_20px_rgba(249,115,22,0.08)] animate-slide-up"
              style={{ animationDelay: `${i * 0.06}s`, animationFillMode: "both" }}
            >
              <div className="flex items-start gap-4">
                {/* Upvote count - prominent */}
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
                    {formatEngagement(engagement)}
                  </span>
                  <span className="text-[10px] text-muted-foreground/40">points</span>
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

                  {/* Meta row: source badge, comments, sentiment */}
                  <div className="flex items-center gap-3 mt-2">
                    {/* Source badge */}
                    <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full bg-orange-500/15 text-orange-400">
                      {article.source === "hackernews" ? "Hacker News" : article.source}
                    </span>

                    {/* Comment count */}
                    {comments > 0 && (
                      <span className="inline-flex items-center gap-1 text-[12px] text-muted-foreground/60">
                        <svg
                          width="12"
                          height="12"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                        </svg>
                        {comments}
                      </span>
                    )}

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

                  {/* HN discussion link */}
                  <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 mt-2.5 text-[11px] font-semibold text-orange-400/70 hover:text-orange-400 transition-colors"
                  >
                    <svg
                      width="12"
                      height="12"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                      <polyline points="15 3 21 3 21 9" />
                      <line x1="10" y1="14" x2="21" y2="3" />
                    </svg>
                    View discussion
                  </a>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
