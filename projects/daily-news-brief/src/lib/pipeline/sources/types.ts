export interface RawArticle {
  title: string;
  url: string;
  source: string; // e.g. "TechCrunch", "Ars Technica", "Reddit", "GitHub"
  sourceOrigin: "newsapi" | "hackernews" | "rss" | "last30days";
  publishedAt: string;
  description: string;
  engagementScore?: number;
  commentCount?: number;
  sourceCount?: number;
  /** Theme/topic that surfaced this article (last30days runs). */
  topic?: string;
}
