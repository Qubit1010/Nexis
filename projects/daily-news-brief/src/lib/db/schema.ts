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
