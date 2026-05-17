export interface RawTool {
  name: string;
  tagline: string; // 1-line description from the source
  url: string;
  source: string; // human-readable: "Product Hunt", "BetaList", "Show HN"
  sourceOrigin: "producthunt" | "tool-rss" | "hackernews-show";
  publishedAt: string;
  description: string; // longer body if available, else falls back to tagline
  upvotes?: number;
  commentCount?: number;
}
