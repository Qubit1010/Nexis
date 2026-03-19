import type { RawArticle } from "./types";

const HN_API = "https://hacker-news.firebaseio.com/v0";
const BATCH_SIZE = 20;

const AI_KEYWORDS = [
  "ai", "artificial intelligence", "machine learning", "llm", "gpt",
  "claude", "gemini", "llama", "openai", "anthropic", "chatgpt",
  "deep learning", "neural", "transformer", "diffusion", "agent",
  "automation", "copilot", "model", "ml", "nlp", "computer vision",
  "fine-tun", "training", "benchmark", "alignment", "safety",
  "midjourney", "stable diffusion", "deepseek", "mistral", "groq",
  "hugging face", "langchain", "vector", "embedding", "rag",
  "agentic", "mcp", "cursor", "windsurf", "devin",
];

interface HNItem {
  id: number;
  title?: string;
  url?: string;
  score?: number;
  descendants?: number;
  time?: number;
  type?: string;
}

function isAIRelated(title: string): boolean {
  const lower = title.toLowerCase();
  return AI_KEYWORDS.some((kw) => lower.includes(kw));
}

async function fetchInBatches(
  ids: number[]
): Promise<PromiseSettledResult<HNItem>[]> {
  const results: PromiseSettledResult<HNItem>[] = [];

  for (let i = 0; i < ids.length; i += BATCH_SIZE) {
    const batch = ids.slice(i, i + BATCH_SIZE);
    const batchResults = await Promise.allSettled(
      batch.map(async (id): Promise<HNItem> => {
        const res = await fetch(`${HN_API}/item/${id}.json`);
        if (!res.ok) throw new Error(`HN item ${id}: ${res.status}`);
        return res.json();
      })
    );
    results.push(...batchResults);
  }

  return results;
}

export async function fetchFromHackerNews(): Promise<RawArticle[]> {
  try {
    const topRes = await fetch(`${HN_API}/topstories.json`);
    if (!topRes.ok) throw new Error(`HN top stories: ${topRes.status}`);
    const topIds: number[] = await topRes.json();

    // Fetch top 150 items in batches of 20
    const itemIds = topIds.slice(0, 150);
    const items = await fetchInBatches(itemIds);

    const articles: RawArticle[] = [];
    for (const result of items) {
      if (result.status !== "fulfilled") continue;
      const item = result.value;
      if (!item || !item.title || !item.url) continue;
      if (!isAIRelated(item.title)) continue;

      articles.push({
        title: item.title,
        url: item.url,
        source: "Hacker News",
        sourceOrigin: "hackernews",
        publishedAt: item.time
          ? new Date(item.time * 1000).toISOString()
          : new Date().toISOString(),
        description: `${item.title} (${item.score ?? 0} points, ${item.descendants ?? 0} comments on HN)`,
        engagementScore: item.score ?? 0,
        commentCount: item.descendants ?? 0,
      });
    }

    console.log(
      `[HackerNews] Fetched ${articles.length} AI-related articles from top 150`
    );
    return articles;
  } catch (error) {
    console.error("[HackerNews] Error:", error);
    return [];
  }
}
