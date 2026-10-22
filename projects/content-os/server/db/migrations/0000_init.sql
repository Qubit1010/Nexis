CREATE TABLE `assets` (
	`id` text PRIMARY KEY NOT NULL,
	`item_id` text NOT NULL,
	`kind` text NOT NULL,
	`local_path` text NOT NULL,
	`public_url` text,
	`alt` text,
	`created_at` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `automations` (
	`id` text PRIMARY KEY NOT NULL,
	`workspace_id` text DEFAULT 'default' NOT NULL,
	`name` text NOT NULL,
	`job_type` text NOT NULL,
	`payload_json` text DEFAULT '{}' NOT NULL,
	`cron` text NOT NULL,
	`tz` text DEFAULT 'Asia/Karachi' NOT NULL,
	`enabled` integer DEFAULT true NOT NULL,
	`catch_up` text DEFAULT 'once' NOT NULL,
	`max_late_min` integer DEFAULT 720 NOT NULL,
	`next_run_at` text,
	`last_run_at` text,
	`last_job_id` text,
	`builtin` integer DEFAULT false NOT NULL,
	`created_at` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `channels` (
	`id` text PRIMARY KEY NOT NULL,
	`workspace_id` text DEFAULT 'default' NOT NULL,
	`kind` text NOT NULL,
	`format` text NOT NULL,
	`name` text NOT NULL,
	`config_json` text DEFAULT '{}' NOT NULL,
	`enabled` integer DEFAULT true NOT NULL,
	`created_at` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `content_items` (
	`id` text PRIMARY KEY NOT NULL,
	`workspace_id` text DEFAULT 'default' NOT NULL,
	`idea_id` text,
	`format` text NOT NULL,
	`channel_id` text,
	`title` text NOT NULL,
	`brief_json` text DEFAULT '{}' NOT NULL,
	`scheduled_for` text,
	`status` text DEFAULT 'planned' NOT NULL,
	`current_version_id` text,
	`depends_on_item_id` text,
	`approved_at` text,
	`published_at` text,
	`published_url` text,
	`external_id` text,
	`doc_url` text,
	`sheet_ref` text,
	`error` text,
	`created_at` text NOT NULL,
	`updated_at` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `items_sched` ON `content_items` (`scheduled_for`);--> statement-breakpoint
CREATE INDEX `items_status` ON `content_items` (`status`);--> statement-breakpoint
CREATE UNIQUE INDEX `items_sheet_ref` ON `content_items` (`sheet_ref`);--> statement-breakpoint
CREATE TABLE `events` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`ts` text NOT NULL,
	`actor` text NOT NULL,
	`entity` text NOT NULL,
	`entity_id` text,
	`type` text NOT NULL,
	`data_json` text
);
--> statement-breakpoint
CREATE INDEX `events_entity` ON `events` (`entity`,`entity_id`);--> statement-breakpoint
CREATE TABLE `ideas` (
	`id` text PRIMARY KEY NOT NULL,
	`workspace_id` text DEFAULT 'default' NOT NULL,
	`title` text NOT NULL,
	`summary` text,
	`url` text,
	`source` text NOT NULL,
	`source_ref` text,
	`payload_json` text,
	`dedupe_key` text NOT NULL,
	`status` text DEFAULT 'inbox' NOT NULL,
	`pillar` text,
	`notes` text,
	`seen_count` integer DEFAULT 1 NOT NULL,
	`created_at` text NOT NULL,
	`updated_at` text NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `ideas_dedupe` ON `ideas` (`workspace_id`,`dedupe_key`);--> statement-breakpoint
CREATE INDEX `ideas_status` ON `ideas` (`status`);--> statement-breakpoint
CREATE TABLE `jobs` (
	`id` text PRIMARY KEY NOT NULL,
	`type` text NOT NULL,
	`lane` text NOT NULL,
	`payload_json` text DEFAULT '{}' NOT NULL,
	`item_id` text,
	`automation_id` text,
	`idempotency_key` text,
	`priority` integer DEFAULT 5 NOT NULL,
	`due_at` text NOT NULL,
	`status` text DEFAULT 'queued' NOT NULL,
	`attempts` integer DEFAULT 0 NOT NULL,
	`max_attempts` integer DEFAULT 3 NOT NULL,
	`locked_at` text,
	`last_error` text,
	`result_json` text,
	`created_at` text NOT NULL,
	`updated_at` text NOT NULL,
	`finished_at` text
);
--> statement-breakpoint
CREATE UNIQUE INDEX `jobs_idem` ON `jobs` (`idempotency_key`);--> statement-breakpoint
CREATE INDEX `jobs_due` ON `jobs` (`status`,`due_at`);--> statement-breakpoint
CREATE TABLE `runs` (
	`id` text PRIMARY KEY NOT NULL,
	`job_id` text,
	`item_id` text,
	`engine` text DEFAULT 'claude-cli' NOT NULL,
	`session_id` text,
	`model` text,
	`pid` integer,
	`status` text NOT NULL,
	`started_at` text NOT NULL,
	`ended_at` text,
	`duration_ms` integer,
	`num_turns` integer,
	`cost_usd_equiv` real,
	`usage_json` text,
	`api_key_source` text,
	`log_path` text,
	`error` text
);
--> statement-breakpoint
CREATE INDEX `runs_item` ON `runs` (`item_id`);--> statement-breakpoint
CREATE TABLE `settings` (
	`key` text PRIMARY KEY NOT NULL,
	`value_json` text NOT NULL,
	`updated_at` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `versions` (
	`id` text PRIMARY KEY NOT NULL,
	`item_id` text NOT NULL,
	`n` integer NOT NULL,
	`kind` text NOT NULL,
	`run_id` text,
	`body_md` text NOT NULL,
	`meta_json` text DEFAULT '{}' NOT NULL,
	`files_json` text DEFAULT '{}' NOT NULL,
	`checks_json` text DEFAULT '[]' NOT NULL,
	`feedback` text,
	`created_at` text NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `versions_item_n` ON `versions` (`item_id`,`n`);