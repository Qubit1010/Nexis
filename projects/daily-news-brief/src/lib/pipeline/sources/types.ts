export interface RawArticle {
  title: string;
  url: string;
  source: string; // e.g. "TechCrunch", "Ars Technica"
  sourceOrigin: "newsapi" | "hackernews" | "rss";
  publishedAt: string;
  description: string;
  engagementScore?: number;
  commentCount?: number;
  sourceCount?: number;
}
