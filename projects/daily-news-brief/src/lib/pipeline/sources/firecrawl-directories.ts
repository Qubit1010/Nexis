import type { RawTool } from "./tool-types";

// Firecrawl-scraped directories. Each entry hits a "latest" or "new" page,
// returns markdown, and we LLM-extract tool entries from it. To keep credits
// low we only scrape one page per source per run.

const FIRECRAWL_API = "https://api.firecrawl.dev/v1/scrape";

const DIRECTORIES = [
  {
    name: "There's An AI For That",
    sourceOrigin: "tool-rss" as const,
    url: "https://theresanaiforthat.com/new/",
    selector: "main",
  },
  {
    name: "AI Agents Directory",
    sourceOrigin: "tool-rss" as const,
    url: "https://aiagentslist.com/",
    selector: "main",
  },
  {
    name: "AppSumo",
    sourceOrigin: "tool-rss" as const,
    url: "https://appsumo.com/browse/?ordering=-publish_date",
    selector: "main",
  },
  {
    name: "FutureTools",
    sourceOrigin: "tool-rss" as const,
    url: "https://futuretools.io/",
    selector: "main",
  },
];

interface FirecrawlResponse {
  success: boolean;
  data?: {
    markdown?: string;
    metadata?: { title?: string };
  };
  error?: string;
}

async function scrapePage(url: string): Promise<string | null> {
  const apiKey = process.env.FIRECRAWL_API_KEY;
  if (!apiKey) return null;

  const res = await fetch(FIRECRAWL_API, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      url,
      formats: ["markdown"],
      onlyMainContent: true,
      // Keep timeout snug — these are big pages
      timeout: 25000,
    }),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`Firecrawl ${res.status} for ${url}: ${text.slice(0, 200)}`);
  }

  const json = (await res.json()) as FirecrawlResponse;
  if (!json.success || !json.data?.markdown) {
    throw new Error(`Firecrawl unsuccessful for ${url}: ${json.error || "no markdown"}`);
  }
  return json.data.markdown;
}

// Pull markdown-link-shaped tool entries: "[Name](url) - description"
function extractToolsFromMarkdown(
  md: string,
  source: string,
  sourceOrigin: "tool-rss"
): RawTool[] {
  const tools: RawTool[] = [];
  const seen = new Set<string>();

  // Pattern A: markdown headings followed by a paragraph
  const headingRe = /^#{2,4}\s+\[?([A-Z][A-Za-z0-9 .'&_-]{2,60})\]?(?:\(([^)]+)\))?\s*\n+([^\n#]{30,400})/gm;
  let m: RegExpExecArray | null;
  while ((m = headingRe.exec(md)) !== null) {
    const name = m[1].trim();
    const url = (m[2] || "").trim();
    const desc = m[3].trim();
    const key = name.toLowerCase();
    if (seen.has(key) || name.length < 3 || name.length > 60) continue;
    seen.add(key);
    tools.push({
      name,
      tagline: desc.slice(0, 200),
      url,
      source,
      sourceOrigin,
      publishedAt: new Date().toISOString(),
      description: desc,
    });
  }

  // Pattern B: "[Name](url) - tagline" inline list items
  const inlineRe = /[-*]\s+\[([A-Z][^\]]{2,60})\]\(([^)]+)\)\s*[-—:]\s*([^\n]{20,300})/g;
  while ((m = inlineRe.exec(md)) !== null) {
    const name = m[1].trim();
    const url = m[2].trim();
    const desc = m[3].trim();
    const key = name.toLowerCase();
    if (seen.has(key) || name.length < 3 || name.length > 60) continue;
    seen.add(key);
    tools.push({
      name,
      tagline: desc.slice(0, 200),
      url,
      source,
      sourceOrigin,
      publishedAt: new Date().toISOString(),
      description: desc,
    });
  }

  // Pattern C: bare anchors with following descriptive sentence (AppSumo style)
  const anchorRe = /\[([A-Z][A-Za-z0-9 .'&_-]{3,50})\]\((https?:\/\/[^\s)]+)\)\s*\n+([A-Z][^\n]{20,250})/g;
  while ((m = anchorRe.exec(md)) !== null) {
    const name = m[1].trim();
    const url = m[2].trim();
    const desc = m[3].trim();
    const key = name.toLowerCase();
    if (seen.has(key) || name.length < 3) continue;
    seen.add(key);
    tools.push({
      name,
      tagline: desc.slice(0, 200),
      url,
      source,
      sourceOrigin,
      publishedAt: new Date().toISOString(),
      description: desc,
    });
  }

  return tools;
}

export async function fetchFromFirecrawlDirectories(): Promise<RawTool[]> {
  if (!process.env.FIRECRAWL_API_KEY) {
    console.log(
      "[Firecrawl] Skipped (FIRECRAWL_API_KEY not set — add it to .env to enable TAAFT, AI Agents Directory, AppSumo)"
    );
    return [];
  }

  const results = await Promise.allSettled(
    DIRECTORIES.map(async (dir) => {
      const md = await scrapePage(dir.url);
      if (!md) return [];
      const extracted = extractToolsFromMarkdown(md, dir.name, dir.sourceOrigin);
      console.log(`[Firecrawl] ${dir.name}: extracted ${extracted.length} tools`);
      return extracted;
    })
  );

  const tools: RawTool[] = [];
  for (const result of results) {
    if (result.status === "fulfilled") tools.push(...result.value);
    else console.error("[Firecrawl]", result.reason);
  }
  console.log(`[Firecrawl] Total: ${tools.length} tools from ${DIRECTORIES.length} directories`);
  return tools;
}
