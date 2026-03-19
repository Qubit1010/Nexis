import Parser from "rss-parser";
import type { RawArticle } from "./types";

const parser = new Parser({
  timeout: 10000,
  headers: {
    "User-Agent": "DailyNewsBrief/1.0",
  },
});

const RSS_FEEDS = [
  {
    url: "http://arxiv.org/rss/cs.AI",
    name: "ArXiv cs.AI",
  },
  {
    url: "https://techcrunch.com/category/artificial-intelligence/feed/",
    name: "TechCrunch AI",
  },
  {
    url: "https://www.technologyreview.com/topic/artificial-intelligence/feed",
    name: "MIT Tech Review",
  },
  {
    url: "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    name: "The Verge AI",
  },
  {
    url: "https://feeds.arstechnica.com/arstechnica/technology-lab",
    name: "Ars Technica",
  },
];

export async function fetchFromRSS(): Promise<RawArticle[]> {
  const results = await Promise.allSettled(
    RSS_FEEDS.map(async (feed) => {
      const parsed = await parser.parseURL(feed.url);
      const cutoff = new Date();
      cutoff.setDate(cutoff.getDate() - 2);

      return (parsed.items || [])
        .filter((item) => {
          if (!item.title) return false;
          const pubDate = item.pubDate ? new Date(item.pubDate) : new Date();
          return pubDate >= cutoff;
        })
        .map(
          (item): RawArticle => ({
            title: item.title || "",
            url: item.link || "",
            source: feed.name,
            sourceOrigin: "rss",
            publishedAt: item.pubDate
              ? new Date(item.pubDate).toISOString()
              : new Date().toISOString(),
            description:
              item.contentSnippet?.slice(0, 500) ||
              item.content?.replace(/<[^>]*>/g, "").slice(0, 500) ||
              item.title ||
              "",
          })
        );
    })
  );

  const articles: RawArticle[] = [];
  for (const result of results) {
    if (result.status === "fulfilled") {
      articles.push(...result.value);
    } else {
      console.error("[RSS]", result.reason);
    }
  }

  console.log(`[RSS] Fetched ${articles.length} articles from ${RSS_FEEDS.length} feeds`);
  return articles;
}
