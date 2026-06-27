import { sqliteTable, text, integer } from "drizzle-orm/sqlite-core";
import { sql } from "drizzle-orm";

export const briefs = sqliteTable("briefs", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  date: text("date").notNull().unique(),
  overallSentiment: text("overall_sentiment"), // JSON: {label, summary}
  topTakeaway: text("top_takeaway"),
  sourcesUsed: integer("sources_used").default(0),
  totalArticlesFetched: integer("total_articles_fetched").default(0),
  createdAt: text("created_at")
    .notNull()
    .default(sql`(datetime('now'))`),
});

export const categories = sqliteTable("categories", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  briefId: integer("brief_id")
    .notNull()
    .references(() => briefs.id, { onDelete: "cascade" }),
  name: text("name").notNull(),
  slug: text("slug").notNull(),
  insight: text("insight").notNull(),
  sortOrder: integer("sort_order").notNull().default(0),
});

export const articles = sqliteTable("articles", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  categoryId: integer("category_id")
    .notNull()
    .references(() => categories.id, { onDelete: "cascade" }),
  title: text("title").notNull(),
  url: text("url").notNull(),
  source: text("source").notNull(),
  sourceOrigin: text("source_origin"), // "newsapi" | "hackernews" | "rss"
  publishedAt: text("published_at"),
  tldr: text("tldr").notNull(),
  sentimentTag: text("sentiment_tag"), // "excited" | "neutral" | "concerned" | "skeptical"
  relevanceScore: integer("relevance_score"),
  engagementScore: integer("engagement_score"),
  commentCount: integer("comment_count"),
  sourceCount: integer("source_count").default(1),
  sortOrder: integer("sort_order").notNull().default(0),
});

export const trends = sqliteTable("trends", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  briefId: integer("brief_id")
    .notNull()
    .references(() => briefs.id, { onDelete: "cascade" }),
  title: text("title").notNull(),
  slug: text("slug").notNull(),
  summary: text("summary").notNull(),
  momentumSignal: text("momentum_signal").notNull(), // "rising" | "steady" | "cooling"
  contentPotentialScore: integer("content_potential_score"),
  sourceCount: integer("source_count").default(1),
  categorySlugs: text("category_slugs").notNull(), // JSON array
  firstSeenDate: text("first_seen_date").notNull(),
  lastSeenDate: text("last_seen_date").notNull(),
  sortOrder: integer("sort_order").notNull().default(0),
});

export const contentIdeas = sqliteTable("content_ideas", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  briefId: integer("brief_id")
    .notNull()
    .references(() => briefs.id, { onDelete: "cascade" }),
  title: text("title").notNull(),
  angle: text("angle").notNull(),
  format: text("format").notNull(), // "thread" | "blog" | "newsletter"
  hook: text("hook").notNull(),
  keyPoints: text("key_points").notNull(), // JSON array
  timeliness: text("timeliness").notNull(), // "breaking" | "trending" | "evergreen"
  relatedTrendSlugs: text("related_trend_slugs").notNull(), // JSON array
  sortOrder: integer("sort_order").notNull().default(0),
});

// ============================================================
// Tool Briefs — "AI Tools for Business" educational section
// ============================================================

export const toolBriefs = sqliteTable("tool_briefs", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  date: text("date").notNull().unique(),
  totalTools: integer("total_tools").default(0),
  sourcesUsed: integer("sources_used").default(0),
  topPickToolId: integer("top_pick_tool_id"),
  crossDomainInsight: text("cross_domain_insight"),
  moversJson: text("movers_json"), // JSON: Mover[] (GitHub trending + OpenRouter)
  createdAt: text("created_at")
    .notNull()
    .default(sql`(datetime('now'))`),
});

export const toolCategories = sqliteTable("tool_categories", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  briefId: integer("brief_id")
    .notNull()
    .references(() => toolBriefs.id, { onDelete: "cascade" }),
  name: text("name").notNull(),
  slug: text("slug").notNull(),
  summary: text("summary").notNull(),
  sortOrder: integer("sort_order").notNull().default(0),
});

export const tools = sqliteTable("tools", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  categoryId: integer("category_id")
    .notNull()
    .references(() => toolCategories.id, { onDelete: "cascade" }),
  name: text("name").notNull(),
  url: text("url").notNull(),
  source: text("source").notNull(),
  sourceOrigin: text("source_origin"),
  oneLiner: text("one_liner").notNull(),
  bestUseCase: text("best_use_case").notNull(),
  howToSteps: text("how_to_steps").notNull(), // JSON array of 3 strings
  audienceHook: text("audience_hook").notNull(),
  pricingTier: text("pricing_tier"),
  tags: text("tags").notNull(), // JSON array
  upvotes: integer("upvotes").default(0),
  relevanceScore: integer("relevance_score"),
  isBestInDomain: integer("is_best_in_domain").notNull().default(0),
  bestInDomainReason: text("best_in_domain_reason"),
  sortOrder: integer("sort_order").notNull().default(0),
});

export const workflowRecipes = sqliteTable("workflow_recipes", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  briefId: integer("brief_id")
    .notNull()
    .references(() => toolBriefs.id, { onDelete: "cascade" }),
  title: text("title").notNull(),
  subtitle: text("subtitle").notNull(),
  scenario: text("scenario").notNull(), // 2-3 sentence business scenario
  agent: text("agent").notNull(), // "Claude Code" | "Codex" | "Cursor" | "MCP server" | etc.
  toolsUsed: text("tools_used").notNull(), // JSON array of strings
  steps: text("steps").notNull(), // JSON array of {step, command/prompt, expectedOutcome}
  timeSaved: text("time_saved"), // e.g. "~3 hours/week"
  difficulty: text("difficulty"), // "beginner" | "intermediate" | "advanced"
  audienceHook: text("audience_hook").notNull(),
});

export const toolTrends = sqliteTable("tool_trends", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  briefId: integer("brief_id")
    .notNull()
    .references(() => toolBriefs.id, { onDelete: "cascade" }),
  title: text("title").notNull(),
  slug: text("slug").notNull(),
  summary: text("summary").notNull(),
  toolNames: text("tool_names").notNull(), // JSON array of tool names
  contentPotential: integer("content_potential"),
  sortOrder: integer("sort_order").notNull().default(0),
});

export const toolContentIdeas = sqliteTable("tool_content_ideas", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  briefId: integer("brief_id")
    .notNull()
    .references(() => toolBriefs.id, { onDelete: "cascade" }),
  title: text("title").notNull(),
  angle: text("angle").notNull(),
  format: text("format").notNull(), // "tutorial" | "carousel" | "reel" | "thread" | "blog"
  hook: text("hook").notNull(),
  keyPoints: text("key_points").notNull(), // JSON array
  relatedToolNames: text("related_tool_names").notNull(), // JSON array
  sortOrder: integer("sort_order").notNull().default(0),
});

// Practical AI live search: a saved per-tool lookup (tool + timeline -> what's new
// + how people solve business problems with it).
export const practicalLookups = sqliteTable("practical_lookups", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  tool: text("tool").notNull(),
  days: integer("days").notNull().default(7),
  summary: text("summary").notNull(),
  whatsNew: text("whats_new").notNull(), // JSON: [{title, detail, url}]
  howPeopleSolve: text("how_people_solve").notNull(), // JSON: [{problem, approach, tools[], steps[]}]
  sources: text("sources").notNull(), // JSON: [{title, url, source}]
  notebookUrl: text("notebook_url"), // NotebookLM notebook link (grounded path only)
  createdAt: text("created_at")
    .notNull()
    .default(sql`(datetime('now'))`),
});

// ============================================================
// YouTube Intelligence — daily YouTube channel analysis
// ============================================================

export const youtubeBriefs = sqliteTable("youtube_briefs", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  date: text("date").notNull().unique(),
  videoCount: integer("video_count").default(0),
  channelCount: integer("channel_count").default(0),
  overallSentiment: text("overall_sentiment"), // JSON: {overall,confidence,reasoning,signals[]}
  formatDistribution: text("format_distribution"), // JSON: {tutorial:N,...}
  titlePatternsJson: text("title_patterns_json"), // JSON: [{pattern,count,examples[]}]
  analyzedAt: text("analyzed_at"),
  modelUsed: text("model_used"),
  createdAt: text("created_at")
    .notNull()
    .default(sql`(datetime('now'))`),
});

export const youtubeTrendingTopics = sqliteTable("youtube_trending_topics", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  briefId: integer("brief_id")
    .notNull()
    .references(() => youtubeBriefs.id, { onDelete: "cascade" }),
  topic: text("topic").notNull(),
  mentionCount: integer("mention_count").default(0),
  channels: text("channels").notNull(), // JSON: string[]
  sentiment: text("sentiment"), // "bullish"|"cautious"|"neutral"|"hype-driven"
  summary: text("summary").notNull(),
  sortOrder: integer("sort_order").notNull().default(0),
});

export const youtubeTopVideos = sqliteTable("youtube_top_videos", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  briefId: integer("brief_id")
    .notNull()
    .references(() => youtubeBriefs.id, { onDelete: "cascade" }),
  videoId: text("video_id").notNull(),
  title: text("title").notNull(),
  channelName: text("channel_name").notNull(),
  url: text("url").notNull(),
  thumbnailUrl: text("thumbnail_url"),
  viewCount: integer("view_count").default(0),
  publishedDate: text("published_date"),
  performanceNote: text("performance_note"),
  sortOrder: integer("sort_order").notNull().default(0),
});

export const youtubeChannelStats = sqliteTable("youtube_channel_stats", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  briefId: integer("brief_id")
    .notNull()
    .references(() => youtubeBriefs.id, { onDelete: "cascade" }),
  channelName: text("channel_name").notNull(),
  channelHandle: text("channel_handle"),
  videosScraped: integer("videos_scraped").default(0),
  totalViews: integer("total_views").default(0),
  avgViews: integer("avg_views").default(0),
  mostCommonFormat: text("most_common_format"),
  postingFrequency: text("posting_frequency"),
  sortOrder: integer("sort_order").notNull().default(0),
});

export const youtubeContentIdeas = sqliteTable("youtube_content_ideas", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  briefId: integer("brief_id")
    .notNull()
    .references(() => youtubeBriefs.id, { onDelete: "cascade" }),
  idea: text("idea").notNull(),
  reasoning: text("reasoning").notNull(),
  formatSuggestion: text("format_suggestion"),
  estimatedInterest: text("estimated_interest"), // "high"|"medium"|"low"
  sortOrder: integer("sort_order").notNull().default(0),
});

export const youtubeSuggestedTopics = sqliteTable("youtube_suggested_topics", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  briefId: integer("brief_id")
    .notNull()
    .references(() => youtubeBriefs.id, { onDelete: "cascade" }),
  topic: text("topic").notNull(),
  angle: text("angle").notNull(),
  whyNow: text("why_now").notNull(),
  targetFormat: text("target_format"),
  competitionLevel: text("competition_level"), // "low"|"medium"|"high"
  referenceVideos: text("reference_videos").notNull(), // JSON: string[]
  sortOrder: integer("sort_order").notNull().default(0),
});
