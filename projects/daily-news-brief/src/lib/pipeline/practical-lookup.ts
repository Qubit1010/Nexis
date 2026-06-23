import { db } from "../db";
import { practicalLookups } from "../db/schema";
import { fetchViaLast30Days } from "./sources/last30days";
import { notebookLmLookup, isIgnoredUrl } from "./sources/notebooklm";
import { callWithFallback } from "./processor";
import { extractJSON } from "./utils";
import type { RawArticle } from "./sources/types";

export interface LookupResult {
  summary: string;
  whatsNew: Array<{ title: string; detail: string; url: string }>;
  howPeopleSolve: Array<{
    problem: string;
    approach: string;
    tools: string[];
    steps: string[];
  }>;
}

// ---------------------------------------------------------------------------
// Fallback Source 1: GitHub repo search (keyless 60/hr; auth = 5000/hr)
// Sorted by STARS so we surface real, popular projects (not random forks).
// ---------------------------------------------------------------------------

interface GitHubRepo {
  full_name: string;
  html_url: string;
  description: string | null;
  stargazers_count: number;
  updated_at: string;
  topics: string[];
  homepage: string | null;
}

async function fetchGitHubRepos(tool: string): Promise<RawArticle[]> {
  const token = process.env.GITHUB_TOKEN;
  const headers: Record<string, string> = {
    Accept: "application/vnd.github.v3+json",
    "User-Agent": "DailyBriefLookup/1.0",
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  // Sort by stars; require a floor of stars so junk repos don't surface.
  const q = encodeURIComponent(`${tool} in:name,description,topic stars:>50`);
  const url = `https://api.github.com/search/repositories?q=${q}&sort=stars&order=desc&per_page=8`;

  try {
    const res = await fetch(url, { headers });
    if (!res.ok) {
      console.warn(`[GitHubSearch] ${res.status} for "${tool}"`);
      return [];
    }
    const data = (await res.json()) as { items?: GitHubRepo[] };
    const items = (data.items || []).slice(0, 8);
    console.log(`[GitHubSearch] "${tool}" -> ${items.length} repos`);

    return items.map((repo) => {
      const topicStr = repo.topics.length ? `Topics: ${repo.topics.join(", ")}` : "";
      return {
        title: `[GitHub] ${repo.full_name}`,
        url: repo.homepage || repo.html_url,
        source: "GitHub",
        sourceOrigin: "github-search" as const,
        publishedAt: repo.updated_at,
        description: `${repo.description || ""} [${repo.stargazers_count.toLocaleString()} stars] ${topicStr}`.trim(),
        engagementScore: Math.min(repo.stargazers_count, 9999),
        topic: tool,
      };
    });
  } catch (err) {
    console.warn("[GitHubSearch] Error:", err);
    return [];
  }
}

// ---------------------------------------------------------------------------
// Fallback Source 2: Firecrawl web search (blogs, tutorials, docs)
// ---------------------------------------------------------------------------

interface FirecrawlSearchItem {
  url: string;
  title?: string;
  description?: string;
  markdown?: string;
}

async function fetchFirecrawlSearch(tool: string): Promise<RawArticle[]> {
  const apiKey = process.env.FIRECRAWL_API_KEY;
  if (!apiKey) {
    console.log("[FirecrawlSearch] Skipped (no FIRECRAWL_API_KEY)");
    return [];
  }

  const queries = [
    `${tool} tutorial guide how to use 2025 2026`,
    `${tool} plugin extension marketplace review`,
  ];

  const articles: RawArticle[] = [];
  const seen = new Set<string>();

  await Promise.allSettled(
    queries.map(async (query) => {
      try {
        const res = await fetch("https://api.firecrawl.dev/v1/search", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${apiKey}`,
          },
          body: JSON.stringify({
            query,
            limit: 5,
            scrapeOptions: { formats: ["markdown"], onlyMainContent: true },
          }),
        });
        if (!res.ok) {
          console.warn(`[FirecrawlSearch] ${res.status} for "${query}"`);
          return;
        }
        const data = (await res.json()) as {
          success: boolean;
          data?: FirecrawlSearchItem[];
        };
        if (!data.success || !data.data) return;
        for (const item of data.data) {
          if (!item.url || !item.title || seen.has(item.url)) continue;
          if (/reddit\.com|news\.ycombinator\.com/.test(item.url)) continue;
          seen.add(item.url);
          articles.push({
            title: item.title,
            url: item.url,
            source: "Web",
            sourceOrigin: "web-search" as const,
            publishedAt: new Date().toISOString(),
            description: (item.description || item.markdown || "").slice(0, 500),
            topic: tool,
          });
        }
      } catch (err) {
        console.warn(`[FirecrawlSearch] Error for "${query}":`, err);
      }
    })
  );

  return articles;
}

// ---------------------------------------------------------------------------
// Prompts
// ---------------------------------------------------------------------------

function evidenceBlock(articles: RawArticle[]): string {
  return articles
    .slice(0, 40)
    .map((a, i) => {
      const sig: string[] = [];
      if (a.engagementScore) sig.push(`${a.engagementScore} stars/upvotes`);
      if (a.commentCount) sig.push(`${a.commentCount} comments`);
      const sigStr = sig.length ? `, ${sig.join(", ")}` : "";
      const desc = a.description ? `\n   ${a.description.slice(0, 350)}` : "";
      return `${i + 1}. [${a.source}] "${a.title}"${sigStr ? ` (${sigStr})` : ""}${desc}\n   ${a.url}`;
    })
    .join("\n\n");
}

const JSON_SHAPE = `{
  "summary": "2-3 sentences: what TOOL is right now and what's notable in this window",
  "whatsNew": [
    { "title": "short update headline", "detail": "1-2 sentences on what changed and why it matters", "url": "source url from the evidence" }
  ],
  "howPeopleSolve": [
    { "problem": "a concrete business problem (marketing, sales, operations, or online presence)", "approach": "how people use TOOL to solve it", "tools": ["TOOL", "other tools combined"], "steps": ["3-5 concrete copy-pasteable steps, commands, or prompts"] }
  ]
}`;

const RULES = `RULES:
- whatsNew: 3-6 items, newest/most important first, each with a real URL from the evidence/sources.
- howPeopleSolve: 3-5 items, each tied to a real SMB business outcome with concrete, copy-pasteable steps.
- Be specific and practical - no hype, no generic advice. If the evidence is thin, say so honestly in the summary.
- Never use em dashes; use plain hyphens.
- Return ONLY valid JSON, no markdown fences.`;

/** Primary path: format NotebookLM's grounded synthesis + real sources into JSON. */
function buildGroundedPrompt(
  tool: string,
  days: number,
  synthesis: string,
  sources: RawArticle[]
): string {
  return `You are a hands-on AI operator advising small business owners. Below is a grounded, cited research synthesis about "${tool}" produced from official docs, blog tutorials, videos, and community sources over roughly the last ${days} days, followed by the source list. Reformat it into a practical lookup. Do not invent anything not supported by the synthesis or sources.

GROUNDED SYNTHESIS (inline [n] markers refer to the sources):
${synthesis}

SOURCES (use these real URLs):
${evidenceBlock(sources)}

PRODUCE valid JSON with this exact structure (replace TOOL with "${tool}"):
${JSON_SHAPE}

${RULES}`;
}

/** Fallback path: synthesize from raw fetched articles. */
function buildFallbackPrompt(tool: string, days: number, articles: RawArticle[]): string {
  return `You are a hands-on AI operator advising small business owners. Below is everything from the last ${days} days about "${tool}" across GitHub repos, blog posts, tutorials, and community discussion. Turn it into a practical lookup.

EVIDENCE:
${evidenceBlock(articles)}

PRODUCE valid JSON with this exact structure (replace TOOL with "${tool}"):
${JSON_SHAPE}

Prioritize official docs, popular GitHub repos, and blog tutorials over forum posts.
${RULES}`;
}

// ---------------------------------------------------------------------------
// Main export
// ---------------------------------------------------------------------------

export async function runToolLookup(tool: string, days: number): Promise<number> {
  const cleanTool = tool.trim();
  if (!cleanTool) throw new Error("tool is required");
  const window = Number.isFinite(days) && days > 0 ? Math.min(days, 90) : 7;

  let prompt: string;
  let sources: RawArticle[];
  let notebookUrl: string | null = null;

  // --- Primary: NotebookLM grounded lookup ---
  const grounded = await notebookLmLookup(cleanTool, window).catch((err) => {
    console.warn("[Lookup] NotebookLM failed:", err?.message);
    return null;
  });

  if (grounded && grounded.sources.length > 0) {
    console.log(`[Lookup] "${cleanTool}" via NotebookLM (${grounded.sources.length} sources)`);
    prompt = buildGroundedPrompt(cleanTool, window, grounded.synthesis, grounded.sources);
    sources = grounded.sources;
    notebookUrl = grounded.notebookUrl;
  } else {
    // --- Fallback: deterministic GitHub + web + community sources ---
    console.log(`[Lookup] "${cleanTool}" via fallback sources`);
    const [community, repos, webContent] = await Promise.all([
      fetchViaLast30Days([cleanTool], window, "lean").catch((err) => {
        console.warn("[Lookup] last30days failed:", err?.message);
        return [] as RawArticle[];
      }),
      fetchGitHubRepos(cleanTool),
      fetchFirecrawlSearch(cleanTool),
    ]);

    const articles: RawArticle[] = [...repos, ...webContent, ...community].filter(
      (a) => !isIgnoredUrl(a.url)
    );
    if (articles.length === 0) {
      throw new Error(`No evidence found for "${cleanTool}" in the last ${window} days`);
    }
    console.log(
      `[Lookup] "${cleanTool}" fallback - ${repos.length} repos, ${webContent.length} web, ${community.length} community`
    );
    prompt = buildFallbackPrompt(cleanTool, window, articles);
    sources = articles;
  }

  const raw = await callWithFallback(
    prompt,
    `lookup:${cleanTool}`,
    "gpt-5.2",
    "claude-sonnet-4-6",
    6000
  );
  const parsed = JSON.parse(extractJSON(raw) ?? raw) as LookupResult;

  const sourceList = sources.slice(0, 20).map((a) => ({
    title: a.title,
    url: a.url,
    source: a.source,
  }));

  const row = db
    .insert(practicalLookups)
    .values({
      tool: cleanTool,
      days: window,
      summary: parsed.summary,
      whatsNew: JSON.stringify(parsed.whatsNew || []),
      howPeopleSolve: JSON.stringify(parsed.howPeopleSolve || []),
      sources: JSON.stringify(sourceList),
      notebookUrl,
    })
    .returning()
    .get();

  return row.id;
}
