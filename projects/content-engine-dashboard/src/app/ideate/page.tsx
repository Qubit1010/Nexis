"use client";

import { useState, useCallback, useEffect, useMemo } from "react";
import { RefreshCw, Loader2 } from "lucide-react";
import { IdeaCard } from "@/components/idea-card";
import { SourceStatus } from "@/components/source-status";
import type { PullIdeasOutput, ScoredIdea, IdeaSource } from "@/lib/types";
import {
  scoreNewsIdea,
  scoreYouTubeOpportunity,
  scoreYouTubeTopic,
  scoreSavedIdea,
  scoreSavedArticle,
} from "@/lib/scoring";

function buildScoredIdeas(data: PullIdeasOutput): ScoredIdea[] {
  const ideas: ScoredIdea[] = [];
  for (const idea of data.news_brief.ideas ?? []) ideas.push(scoreNewsIdea(idea));
  for (const opp of data.youtube_brief.content_opportunities ?? []) ideas.push(scoreYouTubeOpportunity(opp));
  for (const topic of data.youtube_brief.suggested_topics ?? []) ideas.push(scoreYouTubeTopic(topic));
  for (const idea of data.saved_topics.ideas ?? []) ideas.push(scoreSavedIdea(idea));
  for (const article of data.saved_articles?.articles ?? []) ideas.push(scoreSavedArticle(article));

  return ideas.sort((a, b) => {
    if (a.isCooling && !b.isCooling) return 1;
    if (!a.isCooling && b.isCooling) return -1;
    return b.score - a.score;
  });
}

function formatAge(savedAt: number): string {
  const ms = Date.now() - savedAt;
  const mins = Math.floor(ms / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

type FilterSource = "all" | IdeaSource;
type SortBy = "score" | "date";

const SOURCE_LABELS: Record<FilterSource, string> = {
  all: "All",
  "news-brief": "News",
  "youtube-brief": "YouTube",
  "content-opportunities": "Content Opportunities",
  "saved-articles": "Saved Articles",
};

export default function IdeatePage() {
  const [loading, setLoading] = useState(false);
  const [initializing, setInitializing] = useState(true);
  const [data, setData] = useState<PullIdeasOutput | null>(null);
  const [ideas, setIdeas] = useState<ScoredIdea[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [savedAt, setSavedAt] = useState<number | null>(null);
  const [sourceFilter, setSourceFilter] = useState<FilterSource>("all");
  const [sortBy, setSortBy] = useState<SortBy>("score");

  const filteredIdeas = useMemo(() => {
    let result = sourceFilter === "all" ? ideas : ideas.filter((i) => i.source === sourceFilter);

    if (sortBy === "date") {
      result = [...result].sort((a, b) => {
        const da = a.date ? new Date(a.date).getTime() : 0;
        const db = b.date ? new Date(b.date).getTime() : 0;
        return db - da;
      });
    }

    return result;
  }, [ideas, sourceFilter, sortBy]);

  // Count per source for filter badges
  const counts = useMemo(() => {
    const map: Partial<Record<FilterSource, number>> = { all: ideas.length };
    for (const idea of ideas) {
      map[idea.source] = (map[idea.source] ?? 0) + 1;
    }
    return map;
  }, [ideas]);

  useEffect(() => {
    fetch("/api/ideas-cache")
      .then((r) => r.json())
      .then(({ data: cached, savedAt: ts }: { data: PullIdeasOutput | null; savedAt: number | null }) => {
        if (cached) {
          setData(cached);
          setIdeas(buildScoredIdeas(cached));
          setSavedAt(ts);
        }
      })
      .catch(() => {})
      .finally(() => setInitializing(false));
  }, []);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/pull-ideas");
      if (!res.ok) throw new Error(`Request failed: ${res.status}`);
      const json: PullIdeasOutput = await res.json();
      setData(json);
      setIdeas(buildScoredIdeas(json));
      setSavedAt(Date.now());
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }, []);

  const filterSources: FilterSource[] = ["all", "news-brief", "youtube-brief", "content-opportunities", "saved-articles"];

  return (
    <div className="max-w-4xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <h1 className="text-[26px] font-bold text-white leading-tight">Content Ideas</h1>
          <p className="text-[13px] text-[#666] mt-1">
            Scored from news briefs, YouTube trends, and saved topics. Persisted to SQLite.
          </p>
        </div>
        <button
          onClick={refresh}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl gradient-blue text-white text-[13px] font-semibold hover:opacity-90 disabled:opacity-50 transition-all duration-150 shrink-0 shadow-[0_0_20px_rgba(32,142,199,0.2)]"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
          {loading ? "Pulling ideas..." : "Refresh Ideas"}
        </button>
      </div>

      {/* Source status */}
      {data && (
        <div className="mb-5 space-y-1.5">
          <SourceStatus data={data} />
          {savedAt && (
            <p className="text-[11px] text-[#444]">
              Last pulled {formatAge(savedAt)} · saved to DB
            </p>
          )}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="rounded-xl border border-[rgba(255,100,100,0.2)] bg-[rgba(255,100,100,0.05)] p-4 mb-5">
          <p className="text-[13px] text-[#e05c5c]">Failed to pull ideas: {error}</p>
        </div>
      )}

      {/* Source warnings */}
      {data?.errors && data.errors.length > 0 && (
        <div className="rounded-xl border border-[rgba(255,165,0,0.2)] bg-[rgba(255,165,0,0.04)] p-4 mb-5">
          <p className="text-[11px] font-semibold text-[#f5a623] uppercase tracking-wide mb-1">Source Warnings</p>
          {data.errors.map((e, i) => (
            <p key={i} className="text-[12px] text-[#f5a623] opacity-70">{e}</p>
          ))}
        </div>
      )}

      {/* Loading/init skeleton */}
      {(loading || initializing) && (
        <div className="space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-36 rounded-xl bg-[#111111] border border-[rgba(255,255,255,0.04)] animate-pulse" />
          ))}
        </div>
      )}

      {/* Empty state */}
      {!loading && !initializing && ideas.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="w-14 h-14 rounded-2xl gradient-blue flex items-center justify-center mb-4 opacity-40">
            <RefreshCw className="w-6 h-6 text-white" />
          </div>
          <p className="text-[15px] font-medium text-[#555]">No ideas yet</p>
          <p className="text-[13px] text-[#444] mt-1">Hit &quot;Refresh Ideas&quot; to pull from all sources.</p>
        </div>
      )}

      {/* Filter + Sort bar */}
      {!loading && !initializing && ideas.length > 0 && (
        <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
          {/* Source filter pills */}
          <div className="flex flex-wrap gap-1.5">
            {filterSources.map((src) => {
              const count = counts[src] ?? 0;
              if (src !== "all" && count === 0) return null;
              const active = sourceFilter === src;
              return (
                <button
                  key={src}
                  onClick={() => setSourceFilter(src)}
                  className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-[12px] font-medium border transition-all duration-150 ${
                    active
                      ? "bg-[rgba(32,142,199,0.15)] border-[rgba(32,142,199,0.35)] text-[#6ab4d8]"
                      : "bg-[rgba(255,255,255,0.03)] border-[rgba(255,255,255,0.07)] text-[#555] hover:text-[#888] hover:border-[rgba(255,255,255,0.12)]"
                  }`}
                >
                  {SOURCE_LABELS[src]}
                  <span className={`text-[11px] ${active ? "opacity-70" : "opacity-40"}`}>{count}</span>
                </button>
              );
            })}
          </div>

          {/* Sort toggle */}
          <div className="flex items-center gap-1 bg-[rgba(255,255,255,0.03)] border border-[rgba(255,255,255,0.07)] rounded-lg p-0.5">
            {(["score", "date"] as SortBy[]).map((s) => (
              <button
                key={s}
                onClick={() => setSortBy(s)}
                className={`px-3 py-1 rounded-md text-[12px] font-medium transition-all duration-150 ${
                  sortBy === s
                    ? "bg-[rgba(32,142,199,0.15)] text-[#6ab4d8]"
                    : "text-[#555] hover:text-[#888]"
                }`}
              >
                {s === "score" ? "By Score" : "By Date"}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Ideas list */}
      {!loading && !initializing && ideas.length > 0 && (
        <div className="space-y-3">
          <p className="text-[11px] text-[#444] uppercase tracking-wide font-semibold mb-3">
            {filteredIdeas.length} ideas{sourceFilter !== "all" ? ` · ${SOURCE_LABELS[sourceFilter]}` : ""} · sorted by {sortBy}
          </p>
          {filteredIdeas.length === 0 ? (
            <p className="text-[13px] text-[#444] py-8 text-center">No ideas for this source.</p>
          ) : (
            filteredIdeas.map((idea, i) => (
              <IdeaCard key={idea.id} idea={idea} rank={i + 1} />
            ))
          )}
        </div>
      )}
    </div>
  );
}
