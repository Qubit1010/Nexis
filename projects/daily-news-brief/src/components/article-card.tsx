interface Article {
  title: string;
  url: string;
  source: string;
  publishedAt: string | null;
  tldr: string;
  sentimentTag?: string | null;
  engagementScore?: number | null;
  commentCount?: number | null;
  sourceCount?: number | null;
}

interface ArticleCardProps {
  article: Article;
  index: number;
  bookmarked?: boolean;
  onToggleBookmark?: () => void;
  onCopyTldr?: () => void;
}

const SENTIMENT_COLORS: Record<string, string> = {
  excited: "bg-emerald-400",
  neutral: "bg-zinc-400",
  concerned: "bg-amber-400",
  skeptical: "bg-red-400",
};

export function ArticleCard({
  article,
  index,
  bookmarked,
  onToggleBookmark,
  onCopyTldr,
}: ArticleCardProps) {
  const publishedDate = article.publishedAt
    ? new Date(article.publishedAt).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
      })
    : null;

  const sentimentDot = article.sentimentTag
    ? SENTIMENT_COLORS[article.sentimentTag] || "bg-zinc-400"
    : null;

  return (
    <div
      className="group rounded-xl border border-border/60 p-5 transition-all duration-300 hover:border-primary/25 hover:bg-card hover:shadow-[0_4px_24px_rgba(0,0,0,0.15)] hover:translate-y-[-1px] cursor-default"
      style={{ animationDelay: `${index * 0.03}s` }}
      data-article-card
    >
      <div className="flex items-start gap-3">
        <span className="text-[12px] font-mono text-muted-foreground/40 mt-0.5 shrink-0">
          {String(index + 1).padStart(2, "0")}
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-2">
            <a
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              className="font-semibold text-[15px] leading-snug hover:text-primary transition-colors duration-200 inline-block"
            >
              {article.title}
              <span className="inline-block ml-1.5 opacity-0 group-hover:opacity-100 transition-opacity duration-200 text-primary/60 text-xs">
                &#8599;
              </span>
            </a>
            {/* Action buttons */}
            <div className="flex items-center gap-1 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
              {onCopyTldr && (
                <button
                  onClick={onCopyTldr}
                  className="w-7 h-7 rounded-md flex items-center justify-center text-muted-foreground/50 hover:text-foreground hover:bg-accent/60 transition-all duration-200"
                  title="Copy TL;DR"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                  </svg>
                </button>
              )}
              {onToggleBookmark && (
                <button
                  onClick={onToggleBookmark}
                  className={`w-7 h-7 rounded-md flex items-center justify-center transition-all duration-200 ${
                    bookmarked
                      ? "text-amber-400 hover:text-amber-300"
                      : "text-muted-foreground/50 hover:text-foreground hover:bg-accent/60"
                  }`}
                  title={bookmarked ? "Remove bookmark" : "Bookmark"}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill={bookmarked ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
                  </svg>
                </button>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2 mt-1.5 flex-wrap">
            {sentimentDot && (
              <span
                className={`w-1.5 h-1.5 rounded-full ${sentimentDot}`}
                title={article.sentimentTag || ""}
              />
            )}
            <span className="text-[13px] font-medium text-primary/70">
              {article.source}
            </span>
            {publishedDate && (
              <>
                <span className="text-muted-foreground/30">&middot;</span>
                <span className="text-[13px] text-muted-foreground/60">
                  {publishedDate}
                </span>
              </>
            )}
            {article.engagementScore != null && article.engagementScore > 0 && (
              <>
                <span className="text-muted-foreground/30">&middot;</span>
                <span className="text-[12px] text-orange-400/70">
                  {article.engagementScore} pts
                </span>
              </>
            )}
            {article.sourceCount != null && article.sourceCount > 1 && (
              <>
                <span className="text-muted-foreground/30">&middot;</span>
                <span className="text-[12px] text-emerald-400/70">
                  {article.sourceCount} sources
                </span>
              </>
            )}
          </div>
          <p className="text-[14px] text-muted-foreground mt-2.5 leading-relaxed">
            {article.tldr}
          </p>
        </div>
      </div>
    </div>
  );
}
