export interface RawArticle {
  title: string;
  url: string;
  source: string; // publisher hostname label, e.g. "techcrunch.com", "Reddit"
  sourceOrigin: "hackernews" | "rss" | "research";
  publishedAt: string;
  description: string;
  engagementScore?: number;
  commentCount?: number;
  sourceCount?: number;
  /** Theme/topic query that surfaced this article (research runs). */
  topic?: string;
}
