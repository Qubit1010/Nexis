"use client";

import { useState } from "react";
import { ArticleCard } from "@/components/article-card";
import { useBookmarkContext } from "@/lib/hooks/bookmark-context";

interface Article {
  id: number;
  title: string;
  url: string;
  source: string;
  sourceOrigin: string | null;
  publishedAt: string | null;
  tldr: string;
  sentimentTag: string | null;
  relevanceScore: number | null;
  engagementScore: number | null;
  commentCount: number | null;
  sourceCount: number | null;
}

interface CategorySectionProps {
  name: string;
  slug: string;
  insight: string;
  articles: Article[];
  index: number;
  date?: string;
}

type SortKey = "default" | "relevance" | "engagement" | "recency" | "sources";

const SORT_OPTIONS: { value: SortKey; label: string }[] = [
  { value: "default", label: "Default" },
  { value: "relevance", label: "Relevance" },
  { value: "engagement", label: "Engagement" },
  { value: "recency", label: "Newest" },
  { value: "sources", label: "Sources" },
];

function sortArticles(articles: Article[], key: SortKey): Article[] {
  if (key === "default") return articles;
  const sorted = [...articles];
  switch (key) {
    case "relevance":
      return sorted.sort(
        (a, b) => (b.relevanceScore ?? 0) - (a.relevanceScore ?? 0)
      );
    case "engagement":
      return sorted.sort(
        (a, b) => (b.engagementScore ?? 0) - (a.engagementScore ?? 0)
      );
    case "recency":
      return sorted.sort((a, b) => {
        const da = a.publishedAt ? new Date(a.publishedAt).getTime() : 0;
        const db = b.publishedAt ? new Date(b.publishedAt).getTime() : 0;
        return db - da;
      });
    case "sources":
      return sorted.sort(
        (a, b) => (b.sourceCount ?? 1) - (a.sourceCount ?? 1)
      );
  }
}

export function CategorySection({
  name,
  slug,
  insight,
  articles,
  index,
  date = "",
}: CategorySectionProps) {
  const [sortKey, setSortKey] = useState<SortKey>("default");
  const { isBookmarked, toggleBookmark } = useBookmarkContext();
  const sorted = sortArticles(articles, sortKey);

  return (
    <section
      id={slug}
      className="scroll-mt-8 animate-slide-up"
      style={{ opacity: 0, animationDelay: `${index * 0.08}s` }}
    >
      {/* Category header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-primary/15 flex items-center justify-center shrink-0">
            <span className="text-[11px] font-bold text-primary">
              {String(index + 1).padStart(2, "0")}
            </span>
          </div>
          <div>
            <h2 className="text-[22px] font-bold tracking-tight leading-tight">
              {name}
            </h2>
            <p className="text-[13px] text-muted-foreground">
              {articles.length} article{articles.length !== 1 ? "s" : ""}
            </p>
          </div>
        </div>

        {/* Sort controls */}
        <div className="flex items-center gap-1">
          {SORT_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => setSortKey(opt.value)}
              className={`text-[11px] px-2 py-1 rounded-md transition-all duration-200 ${
                sortKey === opt.value
                  ? "bg-primary/15 text-primary"
                  : "text-muted-foreground/50 hover:text-muted-foreground hover:bg-accent/40"
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Insight card */}
      <div className="mb-5 relative rounded-xl border border-primary/20 bg-gradient-to-br from-primary/[0.08] to-primary/[0.03] p-5 transition-all duration-300 hover:border-primary/30 hover:shadow-[0_0_30px_rgba(59,130,246,0.06)]">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-5 h-5 rounded-full bg-primary/20 flex items-center justify-center">
            <span className="text-primary text-[10px]">*</span>
          </div>
          <p className="text-[12px] font-semibold text-primary uppercase tracking-[0.1em]">
            Key Insight
          </p>
        </div>
        <p className="text-[15px] leading-relaxed text-foreground/90">
          {insight}
        </p>
      </div>

      {/* Articles */}
      <div className="space-y-3 ml-1">
        {sorted.map((article, i) => (
          <ArticleCard
            key={article.id}
            article={article}
            index={i}
            bookmarked={isBookmarked(article.id)}
            onToggleBookmark={() =>
              toggleBookmark({
                id: article.id,
                title: article.title,
                url: article.url,
                source: article.source,
                tldr: article.tldr,
                date,
              })
            }
            onCopyTldr={() => navigator.clipboard.writeText(article.tldr)}
          />
        ))}
      </div>
    </section>
  );
}
