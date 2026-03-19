"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

interface BriefSummary {
  date: string;
  overallSentiment: { label: string; summary: string } | null;
  topTakeaway: string | null;
  totalArticlesFetched: number | null;
  trends: {
    title: string;
    slug: string;
    momentumSignal: string;
    contentPotentialScore: number | null;
  }[];
  categories: {
    name: string;
    slug: string;
    insight: string;
    articles: { id: number }[];
  }[];
}

interface BriefDate {
  date: string;
}

const SENTIMENT_COLORS: Record<string, string> = {
  bullish: "text-emerald-400",
  cautious: "text-amber-400",
  mixed: "text-blue-400",
  bearish: "text-red-400",
};

const MOMENTUM_ICONS: Record<string, string> = {
  rising: "\u2191",
  steady: "\u2192",
  cooling: "\u2193",
};

export default function ComparePage() {
  return (
    <Suspense fallback={<div className="text-center py-12 text-muted-foreground/50">Loading...</div>}>
      <CompareContent />
    </Suspense>
  );
}

function CompareContent() {
  const searchParams = useSearchParams();
  const [dates, setDates] = useState<BriefDate[]>([]);
  const [dateA, setDateA] = useState(searchParams.get("a") || "");
  const [dateB, setDateB] = useState(searchParams.get("b") || "");
  const [briefA, setBriefA] = useState<BriefSummary | null>(null);
  const [briefB, setBriefB] = useState<BriefSummary | null>(null);

  useEffect(() => {
    fetch("/api/briefs")
      .then((r) => r.json())
      .then((d: BriefDate[]) => {
        setDates(d);
        if (!dateA && d.length >= 2) setDateA(d[1].date);
        if (!dateB && d.length >= 1) setDateB(d[0].date);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (dateA) {
      fetch(`/api/briefs/${dateA}`)
        .then((r) => (r.ok ? r.json() : null))
        .then(setBriefA)
        .catch(() => setBriefA(null));
    }
  }, [dateA]);

  useEffect(() => {
    if (dateB) {
      fetch(`/api/briefs/${dateB}`)
        .then((r) => (r.ok ? r.json() : null))
        .then(setBriefB)
        .catch(() => setBriefB(null));
    }
  }, [dateB]);

  const trendSlugsA = new Set(briefA?.trends.map((t) => t.slug) || []);
  const trendSlugsB = new Set(briefB?.trends.map((t) => t.slug) || []);
  const newTrends = briefB?.trends.filter((t) => !trendSlugsA.has(t.slug)) || [];
  const droppedTrends = briefA?.trends.filter((t) => !trendSlugsB.has(t.slug)) || [];
  const continuingTrends = briefB?.trends.filter((t) => trendSlugsA.has(t.slug)) || [];

  return (
    <div className="max-w-5xl mx-auto px-8 py-10">
      <h1 className="text-2xl font-bold mb-2">Compare Briefs</h1>
      <p className="text-[13px] text-muted-foreground mb-6">
        Side-by-side comparison of two briefs
      </p>

      {/* Date selectors */}
      <div className="flex items-center gap-4 mb-8">
        <div className="flex-1">
          <label className="text-[11px] font-semibold text-muted-foreground uppercase tracking-[0.1em] mb-1.5 block">
            Date A (older)
          </label>
          <select
            value={dateA}
            onChange={(e) => setDateA(e.target.value)}
            className="w-full rounded-lg border border-border bg-background px-3 py-2 text-[14px] text-foreground"
          >
            <option value="">Select date</option>
            {dates.map((d) => (
              <option key={d.date} value={d.date}>
                {d.date}
              </option>
            ))}
          </select>
        </div>
        <span className="text-muted-foreground/40 mt-5">vs</span>
        <div className="flex-1">
          <label className="text-[11px] font-semibold text-muted-foreground uppercase tracking-[0.1em] mb-1.5 block">
            Date B (newer)
          </label>
          <select
            value={dateB}
            onChange={(e) => setDateB(e.target.value)}
            className="w-full rounded-lg border border-border bg-background px-3 py-2 text-[14px] text-foreground"
          >
            <option value="">Select date</option>
            {dates.map((d) => (
              <option key={d.date} value={d.date}>
                {d.date}
              </option>
            ))}
          </select>
        </div>
      </div>

      {briefA && briefB && (
        <div className="space-y-8">
          {/* Sentiment comparison */}
          <div className="grid grid-cols-2 gap-4">
            {[briefA, briefB].map((brief, i) => (
              <div
                key={i}
                className="rounded-xl border border-border/60 p-5"
              >
                <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-[0.1em] mb-2">
                  {brief.date} Sentiment
                </p>
                {brief.overallSentiment ? (
                  <>
                    <p
                      className={`text-lg font-bold capitalize ${
                        SENTIMENT_COLORS[brief.overallSentiment.label] ||
                        "text-foreground"
                      }`}
                    >
                      {brief.overallSentiment.label}
                    </p>
                    <p className="text-[13px] text-muted-foreground mt-1">
                      {brief.overallSentiment.summary}
                    </p>
                  </>
                ) : (
                  <p className="text-muted-foreground/50">No sentiment data</p>
                )}
                {brief.topTakeaway && (
                  <p className="text-[13px] text-foreground/80 mt-3 italic">
                    &ldquo;{brief.topTakeaway}&rdquo;
                  </p>
                )}
              </div>
            ))}
          </div>

          {/* Trend changes */}
          <div>
            <h2 className="text-lg font-bold mb-4">Trend Changes</h2>

            {newTrends.length > 0 && (
              <div className="mb-4">
                <p className="text-[12px] font-semibold text-emerald-400 uppercase tracking-[0.1em] mb-2">
                  New in {dateB}
                </p>
                <div className="space-y-2">
                  {newTrends.map((t) => (
                    <div
                      key={t.slug}
                      className="rounded-lg border border-emerald-500/20 bg-emerald-500/[0.05] p-3 flex items-center justify-between"
                    >
                      <span className="text-[14px] font-medium">{t.title}</span>
                      <span className="text-[12px] text-emerald-400">
                        {MOMENTUM_ICONS[t.momentumSignal]} {t.momentumSignal} &middot; score {t.contentPotentialScore}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {droppedTrends.length > 0 && (
              <div className="mb-4">
                <p className="text-[12px] font-semibold text-red-400 uppercase tracking-[0.1em] mb-2">
                  Dropped from {dateA}
                </p>
                <div className="space-y-2">
                  {droppedTrends.map((t) => (
                    <div
                      key={t.slug}
                      className="rounded-lg border border-red-500/20 bg-red-500/[0.05] p-3 flex items-center justify-between"
                    >
                      <span className="text-[14px] font-medium text-muted-foreground">
                        {t.title}
                      </span>
                      <span className="text-[12px] text-red-400/60">
                        was {t.momentumSignal}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {continuingTrends.length > 0 && (
              <div>
                <p className="text-[12px] font-semibold text-muted-foreground uppercase tracking-[0.1em] mb-2">
                  Continuing
                </p>
                <div className="space-y-2">
                  {continuingTrends.map((t) => {
                    const prev = briefA.trends.find((a) => a.slug === t.slug);
                    const scoreChange =
                      (t.contentPotentialScore ?? 0) -
                      (prev?.contentPotentialScore ?? 0);
                    return (
                      <div
                        key={t.slug}
                        className="rounded-lg border border-border/40 p-3 flex items-center justify-between"
                      >
                        <span className="text-[14px] font-medium">
                          {t.title}
                        </span>
                        <div className="flex items-center gap-3 text-[12px]">
                          <span className="text-muted-foreground/60">
                            {MOMENTUM_ICONS[t.momentumSignal]} {t.momentumSignal}
                          </span>
                          {scoreChange !== 0 && (
                            <span
                              className={
                                scoreChange > 0
                                  ? "text-emerald-400"
                                  : "text-red-400"
                              }
                            >
                              {scoreChange > 0 ? "+" : ""}
                              {scoreChange} score
                            </span>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Article count comparison */}
          <div>
            <h2 className="text-lg font-bold mb-4">Coverage Comparison</h2>
            <div className="grid grid-cols-2 gap-4">
              {[briefA, briefB].map((brief, i) => (
                <div key={i} className="rounded-xl border border-border/60 p-5">
                  <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-[0.1em] mb-3">
                    {brief.date}
                  </p>
                  <div className="space-y-2">
                    {brief.categories.map((cat) => (
                      <div
                        key={cat.slug}
                        className="flex items-center justify-between text-[13px]"
                      >
                        <span className="text-muted-foreground">{cat.name}</span>
                        <span className="text-foreground font-medium">
                          {cat.articles.length} articles
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {(!briefA || !briefB) && dateA && dateB && (
        <div className="text-center py-12 text-muted-foreground/50">
          Loading comparison...
        </div>
      )}
    </div>
  );
}
