import type { RawArticle } from "./types";
import { resolveTopics, type BriefMode } from "../topics";
import { fetchViaLast30Days, type Depth } from "./last30days";

export type { RawArticle } from "./types";

export interface FetchOptions {
  mode: BriefMode;
  /** Required for mode === "topic". */
  topic?: string;
  /** Lookback window in days (passed to the engine). */
  days: number;
  /** "lean" (free/cheap) or "full" (adds paid social sources). */
  depth: Depth;
}

// News brief excludes GitHub: repo commits/READMEs are tooling noise, not
// industry news. (GitHub stays on for Practical AI, where it is the signal.)
const NEWS_SOURCES = ["reddit", "hackernews", "grounding"];
const NEWS_SOURCES_FULL = [...NEWS_SOURCES, "x", "youtube", "threads"];

/**
 * Evidence fetch layer. Resolves the topic set (curated daily themes, or a single
 * user-named topic) and fetches + ranks via the last30days engine. Replaces the
 * old NewsAPI/HN/RSS sweep — the engine is far more robust (multi-source, RRF
 * fusion, cross-source corroboration, graceful per-source degradation).
 */
export async function fetchAllSources(opts: FetchOptions): Promise<RawArticle[]> {
  const topics = await resolveTopics({ mode: opts.mode, topic: opts.topic });
  const newsSources = opts.depth === "full" ? NEWS_SOURCES_FULL : NEWS_SOURCES;
  const articles = await fetchViaLast30Days(topics, opts.days, opts.depth, newsSources);

  const sourceTypes = new Set(articles.map((a) => a.source));
  console.log(
    `[Sources] Total: ${articles.length} articles across ${sourceTypes.size} source types`
  );
  return articles;
}
