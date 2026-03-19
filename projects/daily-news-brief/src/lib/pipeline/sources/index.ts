import type { RawArticle } from "./types";
import type { Category } from "../categories";
import { fetchFromNewsAPI } from "./newsapi";
import { fetchFromHackerNews } from "./hackernews";
import { fetchFromRSS } from "./rss";

export type { RawArticle } from "./types";

export async function fetchAllSources(
  categories: Category[]
): Promise<RawArticle[]> {
  console.log("[Sources] Fetching from all sources in parallel...");

  const [newsapi, hackernews, rss] = await Promise.allSettled([
    fetchFromNewsAPI(categories),
    fetchFromHackerNews(),
    fetchFromRSS(),
  ]);

  const articles: RawArticle[] = [];
  const sourceNames = new Set<string>();

  for (const result of [newsapi, hackernews, rss]) {
    if (result.status === "fulfilled") {
      for (const article of result.value) {
        articles.push(article);
        sourceNames.add(article.sourceOrigin);
      }
    } else {
      console.error("[Sources] Source failed:", result.reason);
    }
  }

  console.log(
    `[Sources] Total: ${articles.length} articles from ${sourceNames.size} source types`
  );
  return articles;
}
