"use client";

import { useState } from "react";
import { CategorySection } from "@/components/category-section";

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
  sortOrder: number;
}

interface CategoryWithArticles {
  id: number;
  name: string;
  slug: string;
  insight: string;
  articles: Article[];
}

interface FilterableCoverageProps {
  categories: CategoryWithArticles[];
  date: string;
}

const SENTIMENT_OPTIONS = [
  { value: "excited", label: "Excited", color: "bg-emerald-400", activeColor: "bg-emerald-400/20 text-emerald-400 border-emerald-400/40" },
  { value: "neutral", label: "Neutral", color: "bg-zinc-400", activeColor: "bg-zinc-400/20 text-zinc-400 border-zinc-400/40" },
  { value: "concerned", label: "Concerned", color: "bg-amber-400", activeColor: "bg-amber-400/20 text-amber-400 border-amber-400/40" },
  { value: "skeptical", label: "Skeptical", color: "bg-red-400", activeColor: "bg-red-400/20 text-red-400 border-red-400/40" },
] as const;

export function FilterableCoverage({ categories, date }: FilterableCoverageProps) {
  const [activeCategories, setActiveCategories] = useState<Set<string>>(
    new Set(categories.map((c) => c.slug))
  );
  const [activeSentiments, setActiveSentiments] = useState<Set<string>>(
    new Set(SENTIMENT_OPTIONS.map((s) => s.value))
  );

  function toggleCategory(slug: string) {
    setActiveCategories((prev) => {
      const next = new Set(prev);
      if (next.has(slug)) {
        if (next.size > 1) next.delete(slug);
      } else {
        next.add(slug);
      }
      return next;
    });
  }

  function toggleSentiment(value: string) {
    setActiveSentiments((prev) => {
      const next = new Set(prev);
      if (next.has(value)) {
        if (next.size > 1) next.delete(value);
      } else {
        next.add(value);
      }
      return next;
    });
  }

  function resetFilters() {
    setActiveCategories(new Set(categories.map((c) => c.slug)));
    setActiveSentiments(new Set(SENTIMENT_OPTIONS.map((s) => s.value)));
  }

  const allCategoriesActive = activeCategories.size === categories.length;
  const allSentimentsActive = activeSentiments.size === SENTIMENT_OPTIONS.length;
  const hasActiveFilters = !allCategoriesActive || !allSentimentsActive;

  const filtered = categories
    .filter((cat) => activeCategories.has(cat.slug))
    .map((cat) => ({
      ...cat,
      articles: cat.articles.filter(
        (a) => !a.sentimentTag || activeSentiments.has(a.sentimentTag)
      ),
    }))
    .filter((cat) => cat.articles.length > 0);

  const totalShowing = filtered.reduce((s, c) => s + c.articles.length, 0);
  const totalAll = categories.reduce((s, c) => s + c.articles.length, 0);

  return (
    <div>
      {/* Filter bar */}
      <div className="mb-8 rounded-xl border border-border/60 bg-card/50 p-4">
        <div className="flex items-center justify-between mb-3">
          <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-[0.1em]">
            Filters
          </p>
          <div className="flex items-center gap-3">
            {hasActiveFilters && (
              <button
                onClick={resetFilters}
                className="text-[12px] text-primary hover:text-primary/80 transition-colors"
              >
                Reset
              </button>
            )}
            <span className="text-[12px] text-muted-foreground/60">
              {totalShowing}/{totalAll} articles
            </span>
          </div>
        </div>

        {/* Category toggles */}
        <div className="flex flex-wrap gap-1.5 mb-3">
          {categories.map((cat) => {
            const isActive = activeCategories.has(cat.slug);
            return (
              <button
                key={cat.slug}
                onClick={() => toggleCategory(cat.slug)}
                className={`text-[12px] px-2.5 py-1 rounded-md border transition-all duration-200 ${
                  isActive
                    ? "bg-primary/15 text-primary border-primary/30"
                    : "bg-transparent text-muted-foreground/50 border-border/40 hover:border-border"
                }`}
              >
                {cat.name}
                <span className="ml-1 text-[11px] opacity-60">
                  {cat.articles.length}
                </span>
              </button>
            );
          })}
        </div>

        {/* Sentiment toggles */}
        <div className="flex flex-wrap gap-1.5">
          {SENTIMENT_OPTIONS.map((s) => {
            const isActive = activeSentiments.has(s.value);
            return (
              <button
                key={s.value}
                onClick={() => toggleSentiment(s.value)}
                className={`flex items-center gap-1.5 text-[12px] px-2.5 py-1 rounded-md border transition-all duration-200 ${
                  isActive
                    ? s.activeColor
                    : "bg-transparent text-muted-foreground/50 border-border/40 hover:border-border"
                }`}
              >
                <span
                  className={`w-1.5 h-1.5 rounded-full ${
                    isActive ? s.color : "bg-muted-foreground/30"
                  }`}
                />
                {s.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Filtered category sections */}
      <div className="space-y-12">
        {filtered.map((cat, i) => (
          <CategorySection
            key={cat.id}
            name={cat.name}
            slug={cat.slug}
            insight={cat.insight}
            articles={cat.articles}
            index={i}
            date={date}
          />
        ))}
        {filtered.length === 0 && (
          <div className="text-center py-12">
            <p className="text-muted-foreground/60 text-[14px]">
              No articles match the current filters
            </p>
            <button
              onClick={resetFilters}
              className="mt-2 text-[13px] text-primary hover:text-primary/80 transition-colors"
            >
              Reset filters
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
