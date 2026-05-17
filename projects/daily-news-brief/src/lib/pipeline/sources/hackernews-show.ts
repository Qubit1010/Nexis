import type { RawTool } from "./tool-types";

const HN_API = "https://hacker-news.firebaseio.com/v0";
const BATCH_SIZE = 20;

// "Show HN" stories that are AI tool launches
const SHOWN_AI_KEYWORDS = [
  "ai", "llm", "gpt", "claude", "agent", "automation", "copilot",
  "rag", "embed", "vector", "chatbot", "assistant", "generation",
  "model", "ml", "mcp", "no-code", "workflow", "scraper",
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

function isShowHNAITool(title: string): boolean {
  const lower = title.toLowerCase();
  if (!lower.startsWith("show hn")) return false;
  return SHOWN_AI_KEYWORDS.some((kw) => lower.includes(kw));
}

function parseName(title: string): string {
  // "Show HN: ToolName – tagline" -> "ToolName"
  const stripped = title.replace(/^show hn:\s*/i, "");
  const dash = stripped.split(/\s[—–-]\s/);
  return (dash[0] || stripped).trim();
}

async function fetchInBatches(ids: number[]): Promise<PromiseSettledResult<HNItem>[]> {
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

export async function fetchFromHackerNewsShow(): Promise<RawTool[]> {
  try {
    const showRes = await fetch(`${HN_API}/showstories.json`);
    if (!showRes.ok) throw new Error(`HN show stories: ${showRes.status}`);
    const showIds: number[] = await showRes.json();

    // Top 100 Show HN stories
    const items = await fetchInBatches(showIds.slice(0, 100));

    const tools: RawTool[] = [];
    for (const result of items) {
      if (result.status !== "fulfilled") continue;
      const item = result.value;
      if (!item || !item.title || !item.url) continue;
      if (!isShowHNAITool(item.title)) continue;

      const name = parseName(item.title);
      const tagline = item.title.replace(/^show hn:\s*/i, "").trim();

      tools.push({
        name,
        tagline,
        url: item.url,
        source: "Show HN",
        sourceOrigin: "hackernews-show",
        publishedAt: item.time
          ? new Date(item.time * 1000).toISOString()
          : new Date().toISOString(),
        description: tagline,
        upvotes: item.score ?? 0,
        commentCount: item.descendants ?? 0,
      });
    }

    console.log(`[ShowHN] Fetched ${tools.length} AI tool launches`);
    return tools;
  } catch (error) {
    console.error("[ShowHN] Error:", error);
    return [];
  }
}
