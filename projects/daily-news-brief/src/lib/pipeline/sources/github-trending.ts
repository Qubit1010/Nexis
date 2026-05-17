import type { RawTool } from "./tool-types";

// GitHub Trending HTML scrape. They don't expose an API, but the page is simple enough.
const TRENDING_URL = "https://github.com/trending?since=daily";
// Topic-scoped pages — surface tools that are most likely to be agent/AI/automation tooling
const TOPIC_URLS = [
  "https://github.com/trending/python?since=daily",
  "https://github.com/trending/typescript?since=daily",
];

const AI_FILTERS = [
  "ai", "llm", "agent", "agentic", "gpt", "claude", "anthropic",
  "openai", "mcp", "model context protocol", "automation", "rag",
  "embedding", "vector", "chat", "voice", "video", "image", "audio",
  "scrape", "browser", "workflow", "no-code", "low-code", "copilot",
  "ide", "code assistant", "codex", "claude code", "cursor",
  "langchain", "langgraph", "crew", "autogen",
];

interface ParsedRepo {
  owner: string;
  name: string;
  url: string;
  description: string;
  stars: number;
  starsToday: number;
  language: string;
}

function decodeHtml(s: string): string {
  return s
    .replace(/&amp;/g, "&")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&nbsp;/g, " ")
    .trim();
}

function parseTrendingHtml(html: string): ParsedRepo[] {
  const repos: ParsedRepo[] = [];

  // Each repo block starts with <article class="Box-row">
  const blocks = html.split(/<article[^>]*class="Box-row"[^>]*>/);
  for (const block of blocks.slice(1)) {
    const end = block.indexOf("</article>");
    const body = end >= 0 ? block.slice(0, end) : block;

    // Owner/repo from <a href="/owner/name">
    const linkMatch = body.match(/<a[^>]*href="\/([^"\/]+)\/([^"\/]+)"[^>]*class="Link"[^>]*>/);
    if (!linkMatch) continue;
    const owner = linkMatch[1];
    const name = linkMatch[2];

    // Description: <p class="col-9 color-fg-muted my-1 pr-4">...</p>
    const descMatch = body.match(/<p[^>]*class="col-9 color-fg-muted[^"]*"[^>]*>([\s\S]*?)<\/p>/);
    const description = descMatch ? decodeHtml(descMatch[1].replace(/<[^>]*>/g, "").trim()) : "";

    // Language: <span itemprop="programmingLanguage">Python</span>
    const langMatch = body.match(/<span\s+itemprop="programmingLanguage">([^<]+)<\/span>/);
    const language = langMatch ? decodeHtml(langMatch[1]) : "";

    // Stars total: <a class="Link Link--muted ... " ... href="/owner/name/stargazers">12,345</a>
    const starsMatch = body.match(/href="\/[^"]+\/stargazers"[^>]*>([\s\S]*?)<\/a>/);
    const stars = starsMatch
      ? parseInt(starsMatch[1].replace(/[<>\/a-zA-Z\s]/g, "").replace(/,/g, ""), 10) || 0
      : 0;

    // Stars today: <span class="d-inline-block float-sm-right">123 stars today</span>
    const todayMatch = body.match(/(\d[\d,]*)\s+stars?\s+today/i);
    const starsToday = todayMatch ? parseInt(todayMatch[1].replace(/,/g, ""), 10) : 0;

    repos.push({
      owner,
      name,
      url: `https://github.com/${owner}/${name}`,
      description,
      stars,
      starsToday,
      language,
    });
  }

  return repos;
}

function isAIRelated(repo: ParsedRepo): boolean {
  const text = `${repo.name} ${repo.description}`.toLowerCase();
  return AI_FILTERS.some((kw) => text.includes(kw));
}

async function fetchTrendingPage(url: string): Promise<ParsedRepo[]> {
  const res = await fetch(url, {
    headers: { "User-Agent": "DailyNewsBrief/1.0" },
  });
  if (!res.ok) throw new Error(`GitHub Trending ${url}: ${res.status}`);
  const html = await res.text();
  return parseTrendingHtml(html);
}

export async function fetchFromGitHubTrending(): Promise<RawTool[]> {
  try {
    const allUrls = [TRENDING_URL, ...TOPIC_URLS];
    const results = await Promise.allSettled(allUrls.map(fetchTrendingPage));

    const seen = new Set<string>();
    const tools: RawTool[] = [];

    for (const result of results) {
      if (result.status !== "fulfilled") {
        console.error("[GitHubTrending]", result.reason);
        continue;
      }
      for (const repo of result.value) {
        if (!isAIRelated(repo)) continue;
        const key = `${repo.owner}/${repo.name}`;
        if (seen.has(key)) continue;
        seen.add(key);

        tools.push({
          name: repo.name,
          tagline: repo.description || `${repo.language} project by ${repo.owner}`,
          url: repo.url,
          source: "GitHub Trending",
          sourceOrigin: "tool-rss",
          publishedAt: new Date().toISOString(),
          description: `${repo.description}${repo.language ? ` [${repo.language}]` : ""} (${repo.stars.toLocaleString()} stars total, +${repo.starsToday} today)`,
          upvotes: repo.starsToday || Math.min(repo.stars, 9999),
        });
      }
    }

    console.log(`[GitHubTrending] Fetched ${tools.length} AI-related trending repos`);
    return tools;
  } catch (error) {
    console.error("[GitHubTrending] Error:", error);
    return [];
  }
}
