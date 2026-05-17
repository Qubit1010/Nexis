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
