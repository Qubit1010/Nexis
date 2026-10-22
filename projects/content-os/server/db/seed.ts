// First-boot defaults. Idempotent: rows are keyed by fixed ids and only
// inserted when missing, so a user's edits are never overwritten on restart.
import { and, eq, isNull } from "drizzle-orm";
import { db, schema } from "./index.ts";
import { nextRunAfter } from "../scheduler/cron.ts";
import { nowIso } from "../lib/time.ts";
import { TZ } from "../config.ts";

const CHANNELS = [
  {
    id: "li-personal",
    kind: "buffer",
    format: "linkedin_post",
    name: "LinkedIn (Aleem)",
    config: { bufferChannelId: null, bufferService: "linkedin" },
  },
  {
    id: "blog-personal",
    kind: "git_astro",
    format: "personal_blog",
    name: "aleemuh.com blog",
    config: {
      repo: "D:/aleem-portfolio",
      branch: "master",
      contentDir: "src/content/blog",
      assetsDir: "src/assets/blog",
      siteUrl: "https://aleemuh.com",
      blogPath: "/blog/",
      // "git" relies on the Vercel Git integration; "vercel-cli" deploys explicitly.
      deployMode: "git",
      categories: ["ai-automation", "claude-code", "marketing-systems", "gpt-codex", "ai-news"],
      coverFit: false,
      voice: "personal",
    },
  },
  {
    id: "blog-agency",
    kind: "git_astro",
    format: "agency_blog",
    name: "nexus-point.co blog",
    config: {
      repo: "D:/nexuspoint-site",
      branch: "master",
      contentDir: "src/content/blog",
      assetsDir: "src/assets/blog",
      siteUrl: "https://nexus-point.co",
      blogPath: "/blog/",
      // The site's Vercel Git integration still points at an old repo, so a push does not deploy.
      deployMode: "vercel-cli",
      vercelScope: "qubit1010s-projects",
      categories: ["automation", "websites", "systems", "build-notes"],
      coverFit: true,
      voice: "agency",
    },
  },
  {
    id: "nl-personal",
    kind: "manual_newsletter",
    format: "li_newsletter",
    name: "Notes from the Workbench",
    config: { edition: "personal", linkedinUrl: "https://www.linkedin.com/", issueLog: "content/linkedin-newsletter/issue-log.md" },
  },
  {
    id: "nl-agency",
    kind: "manual_newsletter",
    format: "li_newsletter",
    name: "NexusPoint newsletter",
    config: { edition: "agency", linkedinUrl: "https://www.linkedin.com/", issueLog: "content/linkedin-newsletter/nexuspoint/issue-log.md" },
  },
];

const AUTOMATIONS = [
  {
    id: "prepare-week",
    name: "Prepare the week (generate planned drafts)",
    jobType: "prepare_week",
    cron: "0 7 * * *",
    enabled: true,
    catchUp: "once",
    maxLateMin: 720,
    payload: {},
  },
  {
    id: "buffer-reconcile",
    name: "Check Buffer for sent posts",
    jobType: "buffer_reconcile",
    cron: "*/30 * * * *",
    enabled: true,
    catchUp: "once",
    maxLateMin: 1440,
    payload: {},
  },
  {
    id: "news-brief",
    name: "Daily brief: News + Practical AI",
    jobType: "shell",
    cron: "0 8 * * 0",
    // Off by default: brief generation spends OpenAI/Anthropic API credit.
    enabled: false,
    catchUp: "once",
    maxLateMin: 720,
    payload: { task: "daily_brief" },
  },
  {
    id: "youtube-brief",
    name: "YouTube brief",
    jobType: "shell",
    cron: "30 8 * * 0",
    enabled: false,
    catchUp: "once",
    maxLateMin: 720,
    payload: { task: "youtube_brief" },
  },
  {
    id: "sheet-mirror",
    name: "Mirror schedule to Google Sheet",
    jobType: "sheet_mirror",
    cron: "30 2 * * *",
    enabled: false,
    catchUp: "once",
    maxLateMin: 1440,
    payload: {},
  },
];

export async function seed(): Promise<void> {
  const now = nowIso();
  for (const c of CHANNELS) {
    await db
      .insert(schema.channels)
      .values({ id: c.id, kind: c.kind, format: c.format, name: c.name, configJson: JSON.stringify(c.config), createdAt: now })
      .onConflictDoNothing();
  }
  // Items created before their channel existed (e.g. an import run before the first boot)
  // get their format's first channel. Self-healing on every boot.
  for (const c of CHANNELS) {
    if (CHANNELS.find((x) => x.format === c.format) !== c) continue;
    await db.update(schema.contentItems).set({ channelId: c.id }).where(and(eq(schema.contentItems.format, c.format), isNull(schema.contentItems.channelId)));
  }
  for (const a of AUTOMATIONS) {
    await db
      .insert(schema.automations)
      .values({
        id: a.id,
        name: a.name,
        jobType: a.jobType,
        cron: a.cron,
        tz: TZ,
        enabled: a.enabled,
        catchUp: a.catchUp,
        maxLateMin: a.maxLateMin,
        payloadJson: JSON.stringify(a.payload),
        nextRunAt: nextRunAfter(a.cron, TZ, new Date()),
        builtin: true,
        createdAt: now,
      })
      .onConflictDoNothing();
  }
}
