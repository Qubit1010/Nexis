import Parser from "rss-parser";
import type { RawTool } from "./tool-types";

const parser = new Parser({
  timeout: 10000,
  headers: { "User-Agent": "DailyNewsBrief/1.0" },
});

// Product Hunt's AI category RSS — newest launches, includes title, description, link, pubDate
const PH_FEEDS = [
  {
    url: "https://www.producthunt.com/feed?category=artificial-intelligence",
    name: "Product Hunt",
  },
];

function parseNameAndTagline(title: string, contentSnippet?: string): { name: string; tagline: string } {
  // PH titles look like: "Tool Name — One-line tagline"
  const dash = title.split(/\s[—–-]\s/);
  if (dash.length >= 2) {
    return { name: dash[0].trim(), tagline: dash.slice(1).join(" - ").trim() };
  }
  return { name: title.trim(), tagline: (contentSnippet || "").slice(0, 200) };
}

export async function fetchFromProductHunt(): Promise<RawTool[]> {
  const results = await Promise.allSettled(
    PH_FEEDS.map(async (feed) => {
      const parsed = await parser.parseURL(feed.url);
      const cutoff = new Date();
      cutoff.setDate(cutoff.getDate() - 2);

      return (parsed.items || [])
        .filter((item) => {
          if (!item.title) return false;
          const pubDate = item.pubDate ? new Date(item.pubDate) : new Date();
          return pubDate >= cutoff;
        })
        .map((item): RawTool => {
          const { name, tagline } = parseNameAndTagline(
            item.title || "",
            item.contentSnippet
          );
          const body =
            item.contentSnippet?.slice(0, 600) ||
            item.content?.replace(/<[^>]*>/g, "").slice(0, 600) ||
            tagline;

          return {
            name,
            tagline,
            url: item.link || "",
            source: feed.name,
            sourceOrigin: "producthunt",
            publishedAt: item.pubDate
              ? new Date(item.pubDate).toISOString()
              : new Date().toISOString(),
            description: body,
          };
        });
    })
  );

  const tools: RawTool[] = [];
  for (const result of results) {
    if (result.status === "fulfilled") tools.push(...result.value);
    else console.error("[ProductHunt]", result.reason);
  }
  console.log(`[ProductHunt] Fetched ${tools.length} tools`);
  return tools;
}
