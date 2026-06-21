import { fetchViaLast30Days, type Depth } from "./last30days";
import { fetchFromGitHubTrending } from "./github-trending";
import { fetchOpenRouterNewModels } from "./openrouter";
import { resolvePracticalTopics } from "../practical-topics";

/** A single piece of engine evidence, tagged with the domain/kind that fetched it. */
export interface PracticalItem {
  title: string;
  url: string;
  source: string;
  description: string;
  publishedAt: string;
  engagementScore?: number;
  commentCount?: number;
  sourceCount?: number;
  /** Domain slug this item feeds, or null for cross-domain tool updates. */
  domain: string | null;
  kind: "tool-update" | "problem";
  tool?: string;
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
}

const PRACTICAL_DAYS = 7;
const MAX_GITHUB_MOVERS = 8;

/**
 * Practical AI data layer. Fetches:
 *  - engine evidence for tracked-tool updates + per-domain business problems
 *    (via the shared last30days wrapper, fail-open per topic)
 *  - a movers leaderboard from GitHub Trending + OpenRouter (best-effort)
 */
export async function fetchPracticalEvidence(depth: Depth): Promise<PracticalEvidence> {
  const topics = resolvePracticalTopics(depth);
  const topicMeta = new Map(topics.map((t) => [t.topic, t]));

  console.log(`[Practical] Fetching evidence for ${topics.length} topics (${depth})...`);

  const [articles, github, orModels] = await Promise.all([
    fetchViaLast30Days(topics.map((t) => t.topic), PRACTICAL_DAYS, depth),
    fetchFromGitHubTrending().catch(() => []),
    fetchOpenRouterNewModels().catch(() => []),
  ]);

  const items: PracticalItem[] = articles.map((a) => {
    const meta = a.topic ? topicMeta.get(a.topic) : undefined;
    return {
      title: a.title,
      url: a.url,
      source: a.source,
      description: a.description,
      publishedAt: a.publishedAt,
      engagementScore: a.engagementScore,
      commentCount: a.commentCount,
      sourceCount: a.sourceCount,
      domain: meta?.domain ?? null,
      kind: meta?.kind ?? "tool-update",
      tool: meta?.tool,
    };
  });

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
  return { items, movers };
}
