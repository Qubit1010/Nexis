import { and, desc, eq, inArray } from "drizzle-orm";
import { db, schema } from "./db/index.ts";
import { ulid } from "./lib/ids.ts";
import { nowIso, pktParts } from "./lib/time.ts";
import { emit } from "./lib/events.ts";
import { HttpError } from "./lib/http.ts";
import { FORMATS, type Format } from "./settings.ts";
import { activeJobFor, cancelJobsForItem, enqueue } from "./scheduler/queue.ts";
import { runChecks, type Check } from "./engine/checks.ts";
import { safeParse } from "./engine/contract.ts";
import { deletePost } from "./publish/buffer.ts";
import { appendIssueLog } from "./publish/newsletter.ts";

export type Item = typeof schema.contentItems.$inferSelect;
export type Version = typeof schema.versions.$inferSelect;

const PUBLISH_JOBS = ["buffer_push", "publish_git", "newsletter_ready"];

export async function getItem(id: string): Promise<Item> {
  const item = await db.select().from(schema.contentItems).where(eq(schema.contentItems.id, id)).get();
  if (!item) throw new HttpError(404, "NOT_FOUND", "item not found");
  return item;
}

async function setItem(id: string, patch: Partial<Item>): Promise<Item> {
  await db.update(schema.contentItems).set({ ...patch, updatedAt: nowIso() }).where(eq(schema.contentItems.id, id));
  const item = await getItem(id);
  emit("user", "item", id, "item.updated", { status: item.status });
  return item;
}

export async function getChannel(id: string | null) {
  if (!id) return undefined;
  return db.select().from(schema.channels).where(eq(schema.channels.id, id)).get();
}

export async function defaultChannelFor(format: Format) {
  return db
    .select()
    .from(schema.channels)
    .where(and(eq(schema.channels.format, format), eq(schema.channels.enabled, true)))
    .orderBy(schema.channels.createdAt)
    .get();
}

export interface PlanInput {
  ideaId?: string | null;
  format: Format;
  channelId?: string | null;
  scheduledFor?: string | null;
  title?: string;
  brief?: Record<string, unknown>;
  dependsOnItemId?: string | null;
  sheetRef?: string | null;
  status?: string;
  docUrl?: string | null;
}

export async function planItem(input: PlanInput): Promise<Item> {
  if (!FORMATS.includes(input.format)) throw new HttpError(400, "BAD_FORMAT", `format must be one of ${FORMATS.join(", ")}`);
  const idea = input.ideaId ? await db.select().from(schema.ideas).where(eq(schema.ideas.id, input.ideaId)).get() : undefined;
  if (input.ideaId && !idea) throw new HttpError(404, "NOT_FOUND", "idea not found");
  const channel = input.channelId ? await getChannel(input.channelId) : await defaultChannelFor(input.format);
  if (channel && channel.format !== input.format) throw new HttpError(400, "CHANNEL_MISMATCH", `${channel.name} publishes ${channel.format}, not ${input.format}`);
  const title = (input.title || idea?.title || "").trim();
  if (!title) throw new HttpError(400, "TITLE_REQUIRED", "a title or an idea is required");
  const brief = { topic: title, description: idea?.summary ?? "", reference: idea?.url ?? "", ...(input.brief ?? {}) };
  const now = nowIso();
  const id = ulid();
  await db.insert(schema.contentItems).values({
    id,
    ideaId: idea?.id ?? null,
    format: input.format,
    channelId: channel?.id ?? null,
    title,
    briefJson: JSON.stringify(brief),
    scheduledFor: input.scheduledFor ?? null,
    status: input.status ?? "planned",
    dependsOnItemId: input.dependsOnItemId ?? null,
    sheetRef: input.sheetRef ?? null,
    docUrl: input.docUrl ?? null,
    createdAt: now,
    updatedAt: now,
  });
  if (idea && idea.status !== "used") {
    await db.update(schema.ideas).set({ status: "used", updatedAt: now }).where(eq(schema.ideas.id, idea.id));
  }
  emit("user", "item", id, "item.planned", { format: input.format, scheduledFor: input.scheduledFor, ideaId: idea?.id });
  return getItem(id);
}

export async function updateItem(id: string, patch: { title?: string; scheduledFor?: string | null; channelId?: string | null; brief?: Record<string, unknown>; dependsOnItemId?: string | null }): Promise<Item> {
  const item = await getItem(id);
  const next: Partial<Item> = {};
  if (patch.title !== undefined) next.title = patch.title.trim() || item.title;
  if (patch.brief !== undefined) next.briefJson = JSON.stringify({ ...safeParse(item.briefJson), ...patch.brief });
  if (patch.dependsOnItemId !== undefined) next.dependsOnItemId = patch.dependsOnItemId;
  if (patch.channelId !== undefined) {
    const ch = await getChannel(patch.channelId);
    if (patch.channelId && (!ch || ch.format !== item.format)) throw new HttpError(400, "CHANNEL_MISMATCH", "that channel does not publish this format");
    next.channelId = patch.channelId;
  }
  if (patch.scheduledFor !== undefined) {
    next.scheduledFor = patch.scheduledFor;
    // Moving an approved item un-approves it: the publish job was scheduled for the old slot.
    if (["approved", "scheduled"].includes(item.status)) {
      await unapproveItem(id, "rescheduled");
      next.status = "review";
    }
  }
  return setItem(id, next);
}

export async function currentVersion(item: Item): Promise<Version | undefined> {
  if (!item.currentVersionId) return undefined;
  return db.select().from(schema.versions).where(eq(schema.versions.id, item.currentVersionId)).get();
}

export async function listVersions(itemId: string): Promise<Version[]> {
  return db.select().from(schema.versions).where(eq(schema.versions.itemId, itemId)).orderBy(desc(schema.versions.n));
}

export async function requestGeneration(id: string, opts: { feedback?: string; mode?: "fresh" | "resume" } = {}): Promise<unknown> {
  const item = await getItem(id);
  if (["published", "publishing"].includes(item.status)) throw new HttpError(409, "PUBLISHED", "already published");
  const type = opts.feedback ? "revise" : "generate";
  if (type === "revise" && !item.currentVersionId) throw new HttpError(409, "NO_VERSION", "generate a first draft before revising");
  // A plain generate already waiting (e.g. queued by "prepare the week") covers this request.
  const pending = await activeJobFor(id, ["generate"]);
  if (type === "generate" && pending?.status === "queued") return pending;
  if (["approved", "scheduled", "ready_to_post"].includes(item.status)) await unapproveItem(id, "regenerating");
  return enqueue({ type, itemId: id, payload: { feedback: opts.feedback, mode: opts.mode ?? "fresh" }, priority: 3 });
}

export async function saveManualVersion(id: string, bodyMd: string): Promise<Version> {
  const item = await getItem(id);
  const prev = await currentVersion(item);
  const channel = await getChannel(item.channelId);
  const cfg = safeParse(channel?.configJson);
  const checks: Check[] = runChecks(item.format, bodyMd, { edition: cfg.edition, categories: cfg.categories });
  const last = await db.select({ n: schema.versions.n }).from(schema.versions).where(eq(schema.versions.itemId, id)).orderBy(desc(schema.versions.n)).get();
  const versionId = ulid();
  await db.insert(schema.versions).values({
    id: versionId,
    itemId: id,
    n: (last?.n ?? 0) + 1,
    kind: "manual",
    runId: prev?.runId ?? null,
    bodyMd,
    metaJson: prev?.metaJson ?? "{}",
    filesJson: prev?.filesJson ?? "{}",
    checksJson: JSON.stringify(checks),
    createdAt: nowIso(),
  });
  if (["approved", "scheduled"].includes(item.status)) await unapproveItem(id, "edited");
  await setItem(id, { currentVersionId: versionId, status: "review", error: null });
  return (await db.select().from(schema.versions).where(eq(schema.versions.id, versionId)).get())!;
}

export async function approveItem(id: string, opts: { force?: boolean; publishNow?: boolean } = {}): Promise<Item> {
  const item = await getItem(id);
  const version = await currentVersion(item);
  if (!version) throw new HttpError(409, "NO_VERSION", "nothing to approve yet");
  if (!["review", "failed", "missed", "planned"].includes(item.status)) throw new HttpError(409, "BAD_STATE", `cannot approve an item that is ${item.status}`);
  const meta = safeParse(version.metaJson);
  const checks = safeParse(`{"c":${version.checksJson}}`).c as Check[] | undefined;
  const fails = (checks || []).filter((c) => c.level === "fail");
  if (!opts.force && (meta.status === "blocked" || fails.length)) {
    throw new HttpError(409, "NEEDS_FORCE", meta.status === "blocked" ? "the draft is blocked by the gate; approve anyway to override" : `${fails.length} check(s) failed; approve anyway to override`);
  }
  const channel = await getChannel(item.channelId);
  if (!channel) throw new HttpError(409, "NO_CHANNEL", "pick a channel before approving");
  const now = nowIso();
  if (!opts.publishNow && !item.scheduledFor) throw new HttpError(409, "NO_SLOT", "schedule a date and time, or use Publish now");
  const due = opts.publishNow ? now : item.scheduledFor!;

  if (channel.kind === "buffer") {
    if (!opts.publishNow && Date.parse(due) < Date.now() + 2 * 60_000) {
      throw new HttpError(409, "SLOT_PASSED", "this slot has already passed; move it or use Publish now");
    }
    await enqueue({ type: "buffer_push", itemId: id, payload: { versionId: version.id, publishNow: !!opts.publishNow }, idempotencyKey: `buffer_push:${id}:${version.id}:${opts.publishNow ? "now" : due}`, priority: 2 });
  } else if (channel.kind === "git_astro") {
    await enqueue({ type: "publish_git", itemId: id, dueAt: due, payload: { versionId: version.id, force: !!opts.publishNow }, idempotencyKey: `publish_git:${id}:${version.id}:${due}`, priority: 2 });
  } else if (channel.kind === "manual_newsletter") {
    await enqueue({ type: "newsletter_ready", itemId: id, dueAt: due, payload: { versionId: version.id }, idempotencyKey: `newsletter_ready:${id}:${version.id}:${due}`, priority: 2 });
  } else throw new HttpError(400, "BAD_CHANNEL", `unknown channel kind ${channel.kind}`);

  emit("user", "item", id, "item.approved", { versionId: version.id, due, channel: channel.kind });
  return setItem(id, { status: "approved", approvedAt: now, error: null });
}

export async function unapproveItem(id: string, reason = "unapproved"): Promise<Item> {
  const item = await getItem(id);
  if (item.status === "published") throw new HttpError(409, "PUBLISHED", "already published");
  await cancelJobsForItem(id, PUBLISH_JOBS);
  const channel = await getChannel(item.channelId);
  if (channel?.kind === "buffer" && item.externalId) {
    try {
      await deletePost(item.externalId);
      emit("publisher", "item", id, "buffer.deleted", { postId: item.externalId });
    } catch (e) {
      throw new HttpError(502, "BUFFER_DELETE_FAILED", `could not pull the post back from Buffer: ${(e as Error).message}. Delete it in Buffer, then retry.`);
    }
  }
  emit("user", "item", id, "item.unapproved", { reason });
  return setItem(id, { status: item.currentVersionId ? "review" : "planned", approvedAt: null, externalId: channel?.kind === "buffer" ? null : item.externalId });
}

export async function markPublished(id: string, url: string | null): Promise<Item> {
  const item = await getItem(id);
  const channel = await getChannel(item.channelId);
  const now = nowIso();
  if (channel?.kind === "manual_newsletter") {
    const cfg = safeParse(channel.configJson);
    const version = await currentVersion(item);
    const dep = item.dependsOnItemId ? await db.select().from(schema.contentItems).where(eq(schema.contentItems.id, item.dependsOnItemId)).get() : undefined;
    const d = (iso: string) => {
      const p = pktParts(iso);
      return `${p.y}-${String(p.m).padStart(2, "0")}-${String(p.d).padStart(2, "0")}`;
    };
    appendIssueLog({
      edition: cfg.edition || "personal",
      issueLogRel: cfg.issueLog || "content/linkedin-newsletter/issue-log.md",
      draftedOn: d(version?.createdAt ?? now),
      publishedOn: d(now),
      title: String(safeParse(version?.metaJson).meta?.issue_title || item.title),
      source: dep?.publishedUrl || "topic",
      url: url || "",
    });
  }
  await cancelJobsForItem(id, PUBLISH_JOBS);
  const out = await setItem(id, { status: "published", publishedAt: now, publishedUrl: url || item.publishedUrl, error: null });
  emit("user", "item", id, "item.published", { url });
  await releaseDependents(id);
  return out;
}

/** A newsletter waiting on this blog can stop waiting. */
export async function releaseDependents(itemId: string): Promise<void> {
  const deps = await db.select().from(schema.contentItems).where(eq(schema.contentItems.dependsOnItemId, itemId));
  for (const d of deps) {
    await db
      .update(schema.jobs)
      .set({ dueAt: nowIso(), updatedAt: nowIso() })
      .where(and(eq(schema.jobs.itemId, d.id), eq(schema.jobs.type, "newsletter_ready"), eq(schema.jobs.status, "queued")));
  }
}

export async function skipItem(id: string): Promise<Item> {
  await cancelJobsForItem(id, [...PUBLISH_JOBS, "generate", "revise"]);
  const item = await getItem(id);
  if (item.externalId && item.status !== "published") {
    const ch = await getChannel(item.channelId);
    if (ch?.kind === "buffer") await deletePost(item.externalId).catch(() => {});
  }
  return setItem(id, { status: "skipped" });
}

export async function deleteItem(id: string): Promise<void> {
  const item = await getItem(id);
  if (["approved", "scheduled", "publishing", "published"].includes(item.status)) {
    throw new HttpError(409, "BAD_STATE", "unapprove or skip it first; published items are kept as history");
  }
  await cancelJobsForItem(id, [...PUBLISH_JOBS, "generate", "revise"]);
  await db.delete(schema.versions).where(eq(schema.versions.itemId, id));
  await db.delete(schema.contentItems).where(eq(schema.contentItems.id, id));
  emit("user", "item", id, "item.deleted");
}

export async function itemsBetween(fromIso: string, toIso: string): Promise<Item[]> {
  const all = await db.select().from(schema.contentItems);
  return all.filter((i) => !i.scheduledFor || (i.scheduledFor >= fromIso && i.scheduledFor < toIso));
}

/** Items that need a human: drives the attention rail. */
export async function attention(atRiskHours: number) {
  const items = await db
    .select()
    .from(schema.contentItems)
    .where(inArray(schema.contentItems.status, ["planned", "review", "failed", "missed", "ready_to_post", "approved", "scheduled", "publishing", "generating"]));
  const now = Date.now();
  const needsCheck = await db.select().from(schema.jobs).where(eq(schema.jobs.status, "needs_check"));
  const out: { item: Item; reason: string }[] = [];
  for (const i of items) {
    const due = i.scheduledFor ? Date.parse(i.scheduledFor) : null;
    // Not yet approved and the slot is close (at risk) or already gone (overdue).
    const timing = due && ["planned", "review"].includes(i.status) ? (due < now ? "overdue" : due - now < atRiskHours * 3600_000 ? "at_risk" : null) : null;
    if (timing) out.push({ item: i, reason: timing });
    else if (i.status === "review") out.push({ item: i, reason: "review" });
    else if (i.status === "failed") out.push({ item: i, reason: "failed" });
    else if (i.status === "missed") out.push({ item: i, reason: "missed" });
    else if (i.status === "ready_to_post") out.push({ item: i, reason: "ready_to_post" });
  }
  const order = ["overdue", "missed", "failed", "at_risk", "ready_to_post", "needs_check", "review"];
  out.sort((a, b) => order.indexOf(a.reason) - order.indexOf(b.reason));
  for (const j of needsCheck) {
    const i = items.find((x) => x.id === j.itemId);
    if (i) out.unshift({ item: i, reason: "needs_check" });
  }
  return out;
}
