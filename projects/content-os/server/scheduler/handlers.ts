import fs from "node:fs";
import path from "node:path";
import { and, eq, inArray, isNotNull } from "drizzle-orm";
import { db, schema } from "../db/index.ts";
import { NEXIS_ROOT, rootEnv } from "../config.ts";
import { addMinutes, nowIso, pktParts } from "../lib/time.ts";
import { emit } from "../lib/events.ts";
import { run, tail } from "../lib/proc.ts";
import { getSettings } from "../settings.ts";
import { safeParse } from "../engine/contract.ts";
import { fmValue, splitFrontmatter } from "../engine/checks.ts";
import { runGeneration } from "../engine/generate.ts";
import { activeJobFor, enqueue, FatalError, MissedError, NeedsCheckError, RequeueError, type Job } from "./queue.ts";
import { BufferError, createScheduledPost, getPost, listChannels, postsInWindow } from "../publish/buffer.ts";
import { uploadPublicImage } from "../publish/images.ts";
import { PublishError, publishToAstro, slugFromVersion, type SiteConfig } from "../publish/git-astro.ts";
import { releaseDependents } from "../items.ts";

type Item = typeof schema.contentItems.$inferSelect;

async function setItem(id: string, patch: Partial<Item>): Promise<void> {
  await db.update(schema.contentItems).set({ ...patch, updatedAt: nowIso() }).where(eq(schema.contentItems.id, id));
  emit("publisher", "item", id, "item.updated", patch);
}

async function loadForPublish(job: Job) {
  if (!job.itemId) throw new FatalError("publish job without an item");
  const item = await db.select().from(schema.contentItems).where(eq(schema.contentItems.id, job.itemId)).get();
  if (!item) throw new FatalError("item no longer exists");
  const payload = safeParse(job.payloadJson);
  if (payload.versionId && payload.versionId !== item.currentVersionId) throw new FatalError("superseded: a newer version exists; approve it to publish");
  const version = item.currentVersionId ? await db.select().from(schema.versions).where(eq(schema.versions.id, item.currentVersionId)).get() : undefined;
  if (!version) throw new FatalError("no version to publish");
  const channel = item.channelId ? await db.select().from(schema.channels).where(eq(schema.channels.id, item.channelId)).get() : undefined;
  if (!channel) throw new FatalError("item has no channel");
  return { item, version, channel, payload, cfg: safeParse(channel.configJson) };
}

// ---- Buffer ----

async function resolveBufferChannel(channel: typeof schema.channels.$inferSelect, cfg: Record<string, any>): Promise<string> {
  if (cfg.bufferChannelId) return cfg.bufferChannelId;
  const { channels } = await listChannels();
  const matches = channels.filter((c) => c.service === (cfg.bufferService || "linkedin") && !c.isDisconnected);
  if (matches.length !== 1) {
    throw new FatalError(`pick the Buffer channel for ${channel.name} in Settings (found ${matches.length} ${cfg.bufferService || "linkedin"} channels)`);
  }
  await db.update(schema.channels).set({ configJson: JSON.stringify({ ...cfg, bufferChannelId: matches[0].id }) }).where(eq(schema.channels.id, channel.id));
  return matches[0].id;
}

export async function bufferPush(job: Job): Promise<unknown> {
  const { item, version, channel, payload, cfg } = await loadForPublish(job);
  if (item.externalId) throw new FatalError(`already in Buffer as ${item.externalId}`);
  const dueAt = payload.publishNow ? addMinutes(nowIso(), 3) : item.scheduledFor;
  if (!dueAt) throw new FatalError("no publish time");
  if (Date.parse(dueAt) < Date.now() + 60_000) throw new MissedError("the slot passed before the post reached Buffer; move it or use Publish now");
  let channelId: string;
  try {
    channelId = await resolveBufferChannel(channel, cfg);
  } catch (e) {
    if (e instanceof BufferError) throw new FatalError(e.message);
    throw e;
  }

  const s = await getSettings();
  const assets = await db.select().from(schema.assets).where(eq(schema.assets.itemId, item.id));
  const imageUrls: string[] = [];
  for (const a of assets) {
    let url = a.publicUrl;
    if (!url) {
      url = await uploadPublicImage(a.localPath, s.imageHost.bucket, `${item.id}/${path.basename(a.localPath)}`);
      await db.update(schema.assets).set({ publicUrl: url }).where(eq(schema.assets.id, a.id));
    }
    imageUrls.push(url);
  }

  await setItem(item.id, { status: "publishing" });
  try {
    const post = await createScheduledPost({ channelId, text: version.bodyMd.trim(), dueAt, imageUrls });
    await setItem(item.id, { status: "scheduled", externalId: post.id, error: null });
    emit("publisher", "item", item.id, "buffer.scheduled", { postId: post.id, dueAt: post.dueAt });
    return { postId: post.id, dueAt: post.dueAt };
  } catch (e) {
    const msg = (e as Error).message;
    if (e instanceof BufferError && e.ambiguous) {
      await setItem(item.id, { error: `Buffer may have received this post. Check Buffer for a post at ${dueAt}. ${msg}` });
      throw new NeedsCheckError(msg);
    }
    await setItem(item.id, { status: "approved", error: msg });
    throw new FatalError(msg);
  }
}

export async function bufferReconcile(): Promise<unknown> {
  const bufferChannels = await db.select().from(schema.channels).where(eq(schema.channels.kind, "buffer"));
  const ids = bufferChannels.map((c) => c.id);
  if (!ids.length) return { checked: 0 };
  const pending = await db
    .select()
    .from(schema.contentItems)
    .where(and(inArray(schema.contentItems.channelId, ids), inArray(schema.contentItems.status, ["scheduled", "publishing"]), isNotNull(schema.contentItems.externalId)));
  const unsure = await db.select().from(schema.jobs).where(and(eq(schema.jobs.type, "buffer_push"), eq(schema.jobs.status, "needs_check")));
  if (!pending.length && !unsure.length) return { checked: 0 };
  if (!rootEnv().BUFFER_API_KEY) throw new FatalError("BUFFER_API_KEY missing");

  let published = 0;
  for (const item of pending) {
    const post = await getPost(item.externalId!);
    if (!post) {
      await setItem(item.id, { status: "failed", error: "the post no longer exists in Buffer (deleted there?)" });
      continue;
    }
    if (post.status === "sent") {
      await setItem(item.id, { status: "published", publishedAt: post.sentAt ?? nowIso(), publishedUrl: post.externalLink, error: null });
      emit("publisher", "item", item.id, "item.published", { url: post.externalLink });
      await releaseDependents(item.id);
      published++;
    } else if (post.status === "error") {
      await setItem(item.id, { status: "failed", error: `Buffer could not publish: ${post.error?.message ?? "unknown error"}` });
    }
  }

  // Settle ambiguous pushes: if Buffer has a post at that slot with the same opening, adopt it.
  let settled = 0;
  if (unsure.length) {
    const { orgId } = await listChannels();
    for (const j of unsure) {
      const item = j.itemId ? await db.select().from(schema.contentItems).where(eq(schema.contentItems.id, j.itemId)).get() : undefined;
      const ch = bufferChannels.find((c) => c.id === item?.channelId);
      const cfg = safeParse(ch?.configJson);
      const version = item?.currentVersionId ? await db.select().from(schema.versions).where(eq(schema.versions.id, item.currentVersionId)).get() : undefined;
      if (!item?.scheduledFor || !cfg.bufferChannelId || !version) continue;
      const posts = await postsInWindow(orgId, cfg.bufferChannelId, addMinutes(item.scheduledFor, -5), addMinutes(item.scheduledFor, 5));
      const head = version.bodyMd.trim().slice(0, 60);
      const match = posts.find((p) => p.text.trim().startsWith(head));
      if (match) {
        await setItem(item.id, { status: "scheduled", externalId: match.id, error: null });
        await db.update(schema.jobs).set({ status: "done", updatedAt: nowIso(), lastError: "settled by reconcile: Buffer had the post" }).where(eq(schema.jobs.id, j.id));
        settled++;
      }
    }
  }
  return { checked: pending.length, published, settled };
}

// ---- Astro blogs ----

export async function publishGit(job: Job): Promise<unknown> {
  const { item, version, channel, payload, cfg } = await loadForPublish(job);
  const s = await getSettings();
  const due = Date.parse(item.scheduledFor ?? job.dueAt);
  if (!payload.force && Date.now() - due > s.blogMaxLateMin * 60_000) {
    await setItem(item.id, { status: "missed", error: `publish time passed ${Math.round((Date.now() - due) / 3600_000)}h ago while the PC was off. Use Publish now to send it.` });
    throw new MissedError("too late to auto-publish");
  }
  const meta = safeParse(version.metaJson);
  const files = safeParse(version.filesJson);
  const slug = slugFromVersion(version.bodyMd, meta.meta?.slug, files.main || `${item.title}.md`);
  const site: SiteConfig = {
    repo: cfg.repo,
    branch: cfg.branch || "master",
    contentDir: cfg.contentDir || "src/content/blog",
    assetsDir: cfg.assetsDir || "src/assets/blog",
    siteUrl: cfg.siteUrl,
    blogPath: cfg.blogPath || "/blog/",
    deployMode: cfg.deployMode === "vercel-cli" ? "vercel-cli" : "git",
    vercelScope: cfg.vercelScope,
    categories: cfg.categories,
  };
  const uploaded = (await db.select().from(schema.assets).where(eq(schema.assets.itemId, item.id))).map((a) => a.localPath);
  const images = [...(Array.isArray(files.images) ? files.images : []), ...uploaded].filter((p: string) => fs.existsSync(p));

  await setItem(item.id, { status: "publishing", error: null });
  try {
    // The page renders the frontmatter title, so that is what live verification looks for.
    const fmTitle = fmValue(splitFrontmatter(version.bodyMd).fm ?? "", "title");
    const res = await publishToAstro({
      site,
      slug,
      title: String(fmTitle || meta.title || item.title),
      markdown: version.bodyMd,
      images,
      previousSha: item.externalId,
      gitIdentity: s.git,
      onCommitted: async (sha) => setItem(item.id, { externalId: sha }),
      log: (m) => emit("publisher", "item", item.id, "publish.log", { message: m }),
    });
    await setItem(item.id, { status: "published", publishedAt: nowIso(), publishedUrl: res.url, externalId: res.sha, error: null });
    emit("publisher", "item", item.id, "item.published", { url: res.url, sha: res.sha, channel: channel.name });
    await releaseDependents(item.id);
    return res;
  } catch (e) {
    const msg = (e as Error).message;
    await setItem(item.id, { error: msg });
    if (e instanceof PublishError && !e.retryable) throw new FatalError(msg);
    throw e;
  }
}

// ---- Newsletter ----

export async function newsletterReady(job: Job): Promise<unknown> {
  const { item } = await loadForPublish(job);
  if (item.dependsOnItemId) {
    const dep = await db.select().from(schema.contentItems).where(eq(schema.contentItems.id, item.dependsOnItemId)).get();
    if (dep && dep.status !== "published") {
      if (Date.now() - Date.parse(job.dueAt) > 7 * 86_400_000) throw new FatalError(`"${dep.title}" never went live; the newsletter cannot link to it`);
      throw new RequeueError(addMinutes(nowIso(), 30), `waiting for "${dep.title}" to go live`);
    }
  }
  await setItem(item.id, { status: "ready_to_post", error: null });
  emit("publisher", "item", item.id, "newsletter.ready", { title: item.title });
  return { ready: true };
}

// ---- Prepare the week ----

export async function prepareWeek(): Promise<unknown> {
  const now = nowIso();
  const horizon = addMinutes(now, 7 * 24 * 60);
  const items = await db.select().from(schema.contentItems).where(eq(schema.contentItems.status, "planned"));
  const p = pktParts(now);
  const day = `${p.y}-${p.m}-${p.d}`;
  let queued = 0;
  for (const i of items) {
    if (!i.scheduledFor || i.scheduledFor < now || i.scheduledFor > horizon || i.currentVersionId) continue;
    if (await activeJobFor(i.id, ["generate", "revise"])) continue;
    await enqueue({ type: "generate", itemId: i.id, idempotencyKey: `generate:${i.id}:auto:${day}`, priority: 6 });
    queued++;
  }
  return { queued };
}

// ---- Shell tasks (daily brief) ----

const BRIEF_DIR = path.join(NEXIS_ROOT, "projects", "daily-news-brief");
const SHELL_TASKS: Record<string, string[][]> = {
  daily_brief: [["tsx", "scripts/daily-cron.ts"], ["tsx", "scripts/daily-tools.ts"]],
  youtube_brief: [["tsx", "scripts/youtube-cron.ts"]],
};

export async function shellTask(job: Job): Promise<unknown> {
  const payload = safeParse(job.payloadJson);
  const steps = SHELL_TASKS[payload.task];
  if (!steps) throw new FatalError(`unknown shell task ${payload.task}`);
  // The brief uses the API on purpose, so this child (unlike claude runs) gets the root .env keys.
  const env = { ...process.env, ...rootEnv() };
  const results: string[] = [];
  for (const step of steps) {
    const r = await run("npx", ["--yes", ...step], { cwd: BRIEF_DIR, env, shell: true, timeoutMs: 40 * 60_000 });
    results.push(`${step.join(" ")} -> exit ${r.code}`);
    if (r.code !== 0) throw new Error(`${step.join(" ")} failed (exit ${r.code}${r.timedOut ? ", timed out" : ""}): ${tail(r.err || r.out, 800)}`);
  }
  emit("scheduler", "automation", job.automationId, "brief.generated", { task: payload.task });
  return { steps: results };
}

// ---- Dispatch ----

export async function handle(job: Job): Promise<unknown> {
  switch (job.type) {
    case "generate":
    case "revise":
      return runGeneration(job);
    case "buffer_push":
      return bufferPush(job);
    case "buffer_reconcile":
      return bufferReconcile();
    case "publish_git":
      return publishGit(job);
    case "newsletter_ready":
      return newsletterReady(job);
    case "prepare_week":
      return prepareWeek();
    case "shell":
      return shellTask(job);
    case "sheet_mirror": {
      const { mirrorSchedule } = await import("../integrations/sheets-mirror.ts");
      return mirrorSchedule();
    }
    default:
      throw new FatalError(`no handler for ${job.type}`);
  }
}
