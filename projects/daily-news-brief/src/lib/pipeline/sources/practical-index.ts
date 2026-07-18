import { fetchViaResearch, type Depth } from "./research";
import { fetchFromGitHubTrending } from "./github-trending";
import { fetchOpenRouterNewModels } from "./openrouter";
import {
  resolveMarketingTopics,
  type MarketingTopic,
} from "../practical-topics";

/** A single piece of research evidence, tagged with the topic that fetched it. */
export interface PracticalItem {
  title: string;
  url: string;
  source: string;
  description: string;
  publishedAt: string;
  sourceCount?: number;
  /** Slug of the marketing topic this item feeds. */
  domain: string;
}

/** A "what's surging / what's new" leaderboard entry. */
export interface Mover {
  name: string;
  url: string;
  signal: string;
  source: "github" | "openrouter";
  blurb?: string;
}

export interface PracticalEvidence {
  items: PracticalItem[];
  movers: Mover[];
  topics: MarketingTopic[];
}

const PRACTICAL_DAYS = 7;
const MAX_GITHUB_MOVERS = 8;

/**
 * Practical AI data layer. Fetches:
 *  - research evidence for the day's rotating marketing topics (2 lean / 3 full,
 *    via the shared research wrapper, fail-open per query)
 *  - a movers leaderboard from GitHub Trending + OpenRouter (best-effort)
 */
export async function fetchPracticalEvidence(
  date: string,
  depth: Depth
): Promise<PracticalEvidence> {
  const topics = resolveMarketingTopics(date, depth);
  const queryToSlug = new Map<string, string>();
  for (const t of topics) {
    for (const q of t.queries) queryToSlug.set(q, t.slug);
  }
  const queries = [...queryToSlug.keys()];

  console.log(
    `[Practical] Topics for ${date}: ${topics.map((t) => t.name).join(", ")} (${queries.length} queries, ${depth})`
  );

  const [articles, github, orModels] = await Promise.all([
    fetchViaResearch(queries, { days: PRACTICAL_DAYS, depth }),
    fetchFromGitHubTrending().catch(() => []),
    fetchOpenRouterNewModels().catch(() => []),
  ]);

  const items: PracticalItem[] = [];
  for (const a of articles) {
    const slug = a.topic ? queryToSlug.get(a.topic) : undefined;
    if (!slug) continue;
    items.push({
      title: a.title,
      url: a.url,
      source: a.source,
      description: a.description,
      publishedAt: a.publishedAt,
      sourceCount: a.sourceCount,
      domain: slug,
    });
  }

  const movers: Mover[] = [];
  for (const repo of github
    .slice()
    .sort((a, b) => (b.upvotes || 0) - (a.upvotes || 0))
    .slice(0, MAX_GITHUB_MOVERS)) {
    movers.push({
      name: repo.name,
      url: repo.url,
      signal: `+${repo.upvotes ?? 0} stars today`,
      source: "github",
      blurb: repo.tagline,
    });
  }
  for (const m of orModels) {
    movers.push({
      name: m.name,
      url: `https://openrouter.ai/${m.id}`,
      signal: "new on OpenRouter",
      source: "openrouter",
      blurb: m.description?.slice(0, 140),
    });
  }

  console.log(`[Practical] ${items.length} evidence items, ${movers.length} movers`);
  return { items, movers, topics };
}
