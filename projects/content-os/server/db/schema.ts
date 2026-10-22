// Portable by construction: ULID text ids, ISO-UTC text timestamps, JSON as text.
// Moving to Postgres later is a dialect port of this file, not a data redesign.
import { index, integer, real, sqliteTable, text, uniqueIndex } from "drizzle-orm/sqlite-core";

const ts = (name: string) => text(name);

export const ideas = sqliteTable(
  "ideas",
  {
    id: text("id").primaryKey(),
    workspaceId: text("workspace_id").notNull().default("default"),
    title: text("title").notNull(),
    summary: text("summary"),
    url: text("url"),
    // youtube_topic | youtube_video | youtube_idea | news_article | practical_idea | topics_sheet | manual
    source: text("source").notNull(),
    sourceRef: text("source_ref"),
    payloadJson: text("payload_json"),
    dedupeKey: text("dedupe_key").notNull(),
    status: text("status").notNull().default("inbox"), // inbox | shortlisted | used | archived
    pillar: text("pillar"),
    notes: text("notes"),
    seenCount: integer("seen_count").notNull().default(1),
    createdAt: ts("created_at").notNull(),
    updatedAt: ts("updated_at").notNull(),
  },
  (t) => [uniqueIndex("ideas_dedupe").on(t.workspaceId, t.dedupeKey), index("ideas_status").on(t.status)],
);

export const contentItems = sqliteTable(
  "content_items",
  {
    id: text("id").primaryKey(),
    workspaceId: text("workspace_id").notNull().default("default"),
    ideaId: text("idea_id"),
    // linkedin_post | personal_blog | agency_blog | li_newsletter
    format: text("format").notNull(),
    channelId: text("channel_id"),
    title: text("title").notNull(),
    briefJson: text("brief_json").notNull().default("{}"),
    scheduledFor: ts("scheduled_for"),
    // planned | generating | review | approved | scheduled | ready_to_post | publishing | published | failed | missed | skipped
    status: text("status").notNull().default("planned"),
    currentVersionId: text("current_version_id"),
    dependsOnItemId: text("depends_on_item_id"),
    approvedAt: ts("approved_at"),
    publishedAt: ts("published_at"),
    publishedUrl: text("published_url"),
    externalId: text("external_id"),
    docUrl: text("doc_url"),
    sheetRef: text("sheet_ref"),
    error: text("error"),
    createdAt: ts("created_at").notNull(),
    updatedAt: ts("updated_at").notNull(),
  },
  (t) => [
    index("items_sched").on(t.scheduledFor),
    index("items_status").on(t.status),
    uniqueIndex("items_sheet_ref").on(t.sheetRef),
  ],
);

export const versions = sqliteTable(
  "versions",
  {
    id: text("id").primaryKey(),
    itemId: text("item_id").notNull(),
    n: integer("n").notNull(),
    kind: text("kind").notNull(), // generated | revised | manual
    runId: text("run_id"),
    bodyMd: text("body_md").notNull(),
    metaJson: text("meta_json").notNull().default("{}"),
    filesJson: text("files_json").notNull().default("{}"),
    checksJson: text("checks_json").notNull().default("[]"),
    feedback: text("feedback"),
    createdAt: ts("created_at").notNull(),
  },
  (t) => [uniqueIndex("versions_item_n").on(t.itemId, t.n)],
);

export const assets = sqliteTable("assets", {
  id: text("id").primaryKey(),
  itemId: text("item_id").notNull(),
  kind: text("kind").notNull(), // image | cover
  localPath: text("local_path").notNull(),
  publicUrl: text("public_url"),
  alt: text("alt"),
  createdAt: ts("created_at").notNull(),
});

export const runs = sqliteTable(
  "runs",
  {
    id: text("id").primaryKey(),
    jobId: text("job_id"),
    itemId: text("item_id"),
    engine: text("engine").notNull().default("claude-cli"),
    sessionId: text("session_id"),
    model: text("model"),
    pid: integer("pid"),
    status: text("status").notNull(), // running | ok | blocked | error | timeout | killed | rate_limited
    startedAt: ts("started_at").notNull(),
    endedAt: ts("ended_at"),
    durationMs: integer("duration_ms"),
    numTurns: integer("num_turns"),
    // Estimate at API prices; on a subscription nothing is billed per run.
    costUsdEquiv: real("cost_usd_equiv"),
    usageJson: text("usage_json"),
    apiKeySource: text("api_key_source"),
    logPath: text("log_path"),
    error: text("error"),
  },
  (t) => [index("runs_item").on(t.itemId)],
);

export const jobs = sqliteTable(
  "jobs",
  {
    id: text("id").primaryKey(),
    // generate | revise | buffer_push | buffer_reconcile | publish_git | newsletter_ready | sheet_mirror | shell | prepare_week | at_risk_scan
    type: text("type").notNull(),
    lane: text("lane").notNull(), // claude | io
    payloadJson: text("payload_json").notNull().default("{}"),
    itemId: text("item_id"),
    automationId: text("automation_id"),
    idempotencyKey: text("idempotency_key"),
    priority: integer("priority").notNull().default(5), // lower runs first
    dueAt: ts("due_at").notNull(),
    // queued | running | done | failed | cancelled | missed | needs_check
    status: text("status").notNull().default("queued"),
    attempts: integer("attempts").notNull().default(0),
    maxAttempts: integer("max_attempts").notNull().default(3),
    lockedAt: ts("locked_at"),
    lastError: text("last_error"),
    resultJson: text("result_json"),
    createdAt: ts("created_at").notNull(),
    updatedAt: ts("updated_at").notNull(),
    finishedAt: ts("finished_at"),
  },
  (t) => [uniqueIndex("jobs_idem").on(t.idempotencyKey), index("jobs_due").on(t.status, t.dueAt)],
);

export const automations = sqliteTable("automations", {
  id: text("id").primaryKey(),
  workspaceId: text("workspace_id").notNull().default("default"),
  name: text("name").notNull(),
  jobType: text("job_type").notNull(),
  payloadJson: text("payload_json").notNull().default("{}"),
  cron: text("cron").notNull(),
  tz: text("tz").notNull().default("Asia/Karachi"),
  enabled: integer("enabled", { mode: "boolean" }).notNull().default(true),
  catchUp: text("catch_up").notNull().default("once"), // once | skip
  maxLateMin: integer("max_late_min").notNull().default(720),
  nextRunAt: ts("next_run_at"),
  lastRunAt: ts("last_run_at"),
  lastJobId: text("last_job_id"),
  builtin: integer("builtin", { mode: "boolean" }).notNull().default(false),
  createdAt: ts("created_at").notNull(),
});

export const channels = sqliteTable("channels", {
  id: text("id").primaryKey(),
  workspaceId: text("workspace_id").notNull().default("default"),
  kind: text("kind").notNull(), // buffer | git_astro | manual_newsletter
  format: text("format").notNull(), // the item format this channel publishes
  name: text("name").notNull(),
  configJson: text("config_json").notNull().default("{}"),
  enabled: integer("enabled", { mode: "boolean" }).notNull().default(true),
  createdAt: ts("created_at").notNull(),
});

export const settings = sqliteTable("settings", {
  key: text("key").primaryKey(),
  valueJson: text("value_json").notNull(),
  updatedAt: ts("updated_at").notNull(),
});

export const events = sqliteTable(
  "events",
  {
    id: integer("id").primaryKey({ autoIncrement: true }),
    ts: ts("ts").notNull(),
    actor: text("actor").notNull(), // user | scheduler | engine | publisher | ingest
    entity: text("entity").notNull(),
    entityId: text("entity_id"),
    type: text("type").notNull(),
    dataJson: text("data_json"),
  },
  (t) => [index("events_entity").on(t.entity, t.entityId)],
);
