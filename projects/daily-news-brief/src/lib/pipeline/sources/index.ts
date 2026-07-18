import type { RawArticle } from "./types";
import { resolveTopics, type BriefMode } from "../topics";
import { fetchViaResearch, type Depth } from "./research";

export type { RawArticle } from "./types";
export type { Depth } from "./research";

export interface FetchOptions {
  mode: BriefMode;
  /** Required for mode === "topic". */
  topic?: string;
  /** Lookback window in days (freshness filter on dated results). */
  days: number;
  /** "lean" (medium research depth) or "full" (deep, adds Jina + extraction). */
  depth: Depth;
}

/**
 * Evidence fetch layer. Resolves the topic set (curated daily themes, or a single
 * user-named topic) and fetches + ranks via the research skill (Exa + Tavily +
 * Serper fused, cross-source ranked, junk-filtered).
 */
export async function fetchAllSources(opts: FetchOptions): Promise<RawArticle[]> {
  const topics = await resolveTopics({ mode: opts.mode, topic: opts.topic });
  const articles = await fetchViaResearch(topics, {
    days: opts.days,
    depth: opts.depth,
  });

  const sourceTypes = new Set(articles.map((a) => a.source));
  console.log(
    `[Sources] Total: ${articles.length} articles across ${sourceTypes.size} source types`
  );
  return articles;
}
