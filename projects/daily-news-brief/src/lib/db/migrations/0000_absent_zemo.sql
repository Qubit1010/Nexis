CREATE TABLE `articles` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`category_id` integer NOT NULL,
	`title` text NOT NULL,
	`url` text NOT NULL,
	`source` text NOT NULL,
	`source_origin` text,
	`published_at` text,
	`tldr` text NOT NULL,
	`sentiment_tag` text,
	`relevance_score` integer,
	`engagement_score` integer,
	`comment_count` integer,
	`source_count` integer DEFAULT 1,
	`sort_order` integer DEFAULT 0 NOT NULL,
	FOREIGN KEY (`category_id`) REFERENCES `categories`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE TABLE `briefs` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`date` text NOT NULL,
	`overall_sentiment` text,
	`top_takeaway` text,
	`sources_used` integer DEFAULT 0,
	`total_articles_fetched` integer DEFAULT 0,
	`created_at` text DEFAULT (datetime('now')) NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `briefs_date_unique` ON `briefs` (`date`);--> statement-breakpoint
CREATE TABLE `categories` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`brief_id` integer NOT NULL,
	`name` text NOT NULL,
	`slug` text NOT NULL,
	`insight` text NOT NULL,
	`sort_order` integer DEFAULT 0 NOT NULL,
	FOREIGN KEY (`brief_id`) REFERENCES `briefs`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE TABLE `content_ideas` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`brief_id` integer NOT NULL,
	`title` text NOT NULL,
	`angle` text NOT NULL,
	`format` text NOT NULL,
	`hook` text NOT NULL,
	`key_points` text NOT NULL,
	`timeliness` text NOT NULL,
	`related_trend_slugs` text NOT NULL,
	`sort_order` integer DEFAULT 0 NOT NULL,
	FOREIGN KEY (`brief_id`) REFERENCES `briefs`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE TABLE `trends` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`brief_id` integer NOT NULL,
	`title` text NOT NULL,
	`slug` text NOT NULL,
	`summary` text NOT NULL,
	`momentum_signal` text NOT NULL,
	`content_potential_score` integer,
	`source_count` integer DEFAULT 1,
	`category_slugs` text NOT NULL,
	`first_seen_date` text NOT NULL,
	`last_seen_date` text NOT NULL,
	`sort_order` integer DEFAULT 0 NOT NULL,
	FOREIGN KEY (`brief_id`) REFERENCES `briefs`(`id`) ON UPDATE no action ON DELETE cascade
);
