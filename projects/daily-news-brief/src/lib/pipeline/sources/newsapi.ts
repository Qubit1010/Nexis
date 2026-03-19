import type { RawArticle } from "./types";
import type { Category } from "../categories";

interface NewsAPIResponse {
  status: string;
  totalResults: number;
  articles: Array<{
    title: string;
    url: string;
    source: { name: string };
    publishedAt: string;
    description: string | null;
  }>;
}

export async function fetchFromNewsAPI(
  categories: Category[]
): Promise<RawArticle[]> {
  const apiKey = process.env.NEWSAPI_KEY;
  if (!apiKey) {
    console.warn("[NewsAPI] NEWSAPI_KEY not set, skipping");
    return [];
  }

  const fromDate = new Date();
  fromDate.setDate(fromDate.getDate() - 2);
  const fromStr = fromDate.toISOString().split("T")[0];

  const results = await Promise.allSettled(
    categories.map(async (cat) => {
      const params = new URLSearchParams({
        q: cat.newsApiQuery,
        sortBy: "publishedAt",
        pageSize: "10",
        from: fromStr,
        language: "en",
        apiKey,
      });

      const response = await fetch(
        `https://newsapi.org/v2/everything?${params.toString()}`
      );

      if (!response.ok) {
        const errorBody = await response.text();
        throw new Error(
          `NewsAPI error for "${cat.name}": ${response.status} - ${errorBody}`
        );
      }

      const data: NewsAPIResponse = await response.json();

      return data.articles
        .filter((a) => a.title && a.title !== "[Removed]" && a.description)
        .map(
          (a): RawArticle => ({
            title: a.title,
            url: a.url,
            source: a.source.name,
            sourceOrigin: "newsapi",
            publishedAt: a.publishedAt,
            description: a.description || "",
          })
        );
    })
  );

  const articles: RawArticle[] = [];
  for (const result of results) {
    if (result.status === "fulfilled") {
      articles.push(...result.value);
    } else {
      console.error("[NewsAPI]", result.reason);
    }
  }

  console.log(`[NewsAPI] Fetched ${articles.length} articles`);
  return articles;
}
