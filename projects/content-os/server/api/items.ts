import fs from "node:fs";
import path from "node:path";
import { Hono } from "hono";
import { desc, eq, inArray } from "drizzle-orm";
import { z } from "zod";
import { db, schema } from "../db/index.ts";
import { DATA_DIR, NEXIS_ROOT, PYTHON_BIN } from "../config.ts";
import { HttpError } from "../lib/http.ts";
import { ulid } from "../lib/ids.ts";
import { nowIso } from "../lib/time.ts";
import { emit } from "../lib/events.ts";
import { run, tail } from "../lib/proc.ts";
import { FORMATS, type Format } from "../settings.ts";
import { safeParse } from "../engine/contract.ts";
import { gwsChildEnv } from "../integrations/gws.ts";
import { enqueue, cancelJobsForItem } from "../scheduler/queue.ts";
import {
  approveItem,
  currentVersion,
  deleteItem,
  getItem,
  listVersions,
  markPublished,
  planItem,
  requestGeneration,
  saveManualVersion,
  skipItem,
  unapproveItem,
  updateItem,
} from "../items.ts";

export const itemsApi = new Hono();

function summarize(item: typeof schema.contentItems.$inferSelect, v?: typeof schema.versions.$inferSelect) {
  const meta = safeParse(v?.metaJson);
  const checks = (v ? (JSON.parse(v.checksJson || "[]") as { level: string }[]) : []) || [];
  return {
    ...item,
    brief: safeParse(item.briefJson),
    version: v
      ? {
          id: v.id,
          n: v.n,
          kind: v.kind,
          title: meta.title ?? null,
          status: meta.status ?? null,
          fails: checks.filter((c) => c.level === "fail").length,
          warns: checks.filter((c) => c.level === "warn").length,
          createdAt: v.createdAt,
        }
      : null,
  };
}

itemsApi.get("/", async (c) => {
  const from = c.req.query("from");
  const to = c.req.query("to");
  let rows = await db.select().from(schema.contentItems).orderBy(desc(schema.contentItems.updatedAt));
  if (from && to) rows = rows.filter((i) => !i.scheduledFor || (i.scheduledFor >= from && i.scheduledFor < to));
  const vIds = rows.map((r) => r.currentVersionId).filter(Boolean) as string[];
  const versions = vIds.length ? await db.select().from(schema.versions).where(inArray(schema.versions.id, vIds)) : [];
  const byId = new Map(versions.map((v) => [v.id, v]));
  return c.json(rows.map((i) => summarize(i, i.currentVersionId ? byId.get(i.currentVersionId) : undefined)));
});

itemsApi.get("/:id", async (c) => {
  const item = await getItem(c.req.param("id"));
  const [versions, runs, jobs, assets, channel, idea, dependsOn, dependents] = await Promise.all([
    listVersions(item.id),
    db.select().from(schema.runs).where(eq(schema.runs.itemId, item.id)).orderBy(desc(schema.runs.startedAt)),
    db.select().from(schema.jobs).where(eq(schema.jobs.itemId, item.id)).orderBy(desc(schema.jobs.createdAt)),
    db.select().from(schema.assets).where(eq(schema.assets.itemId, item.id)),
    item.channelId ? db.select().from(schema.channels).where(eq(schema.channels.id, item.channelId)).get() : undefined,
    item.ideaId ? db.select().from(schema.ideas).where(eq(schema.ideas.id, item.ideaId)).get() : undefined,
    item.dependsOnItemId ? db.select().from(schema.contentItems).where(eq(schema.contentItems.id, item.dependsOnItemId)).get() : undefined,
    db.select().from(schema.contentItems).where(eq(schema.contentItems.dependsOnItemId, item.id)),
  ]);
  const events = await db.select().from(schema.events).where(eq(schema.events.entityId, item.id)).orderBy(desc(schema.events.id)).limit(100);
  return c.json({
    item: { ...item, brief: safeParse(item.briefJson) },
    versions: versions.map((v) => ({
      ...v,
      meta: safeParse(v.metaJson),
      files: safeParse(v.filesJson),
      checks: JSON.parse(v.checksJson || "[]"),
      extraFiles: readExtras(safeParse(v.filesJson)),
    })),
    runs,
    jobs,
    assets,
    channel: channel ? { ...channel, config: safeParse(channel.configJson) } : null,
    idea: idea ? { ...idea, payload: safeParse(idea.payloadJson) } : null,
    dependsOn: dependsOn ?? null,
    dependents,
    events: events.map((e) => ({ ...e, data: safeParse(e.dataJson) })),
  });
});

/** Extra files (infographic prompt, sources, SEO metadata) read inline so the review screen can show them. */
function readExtras(files: Record<string, any>): { name: string; content: string }[] {
  const out: { name: string; content: string }[] = [];
  for (const f of Array.isArray(files.extra) ? files.extra : []) {
    try {
      if (f?.path && fs.existsSync(f.path) && fs.statSync(f.path).size < 400_000) out.push({ name: f.name, content: fs.readFileSync(f.path, "utf8") });
    } catch {
      /* unreadable extra: skip */
    }
  }
  return out;
}

const CreateBody = z.object({
  format: z.enum(FORMATS as [string, ...string[]]),
  title: z.string().trim().min(1).max(500),
  channelId: z.string().nullish(),
  scheduledFor: z.string().datetime().nullish(),
  brief: z.record(z.string(), z.unknown()).optional(),
  dependsOnItemId: z.string().nullish(),
  ideaId: z.string().nullish(),
});

itemsApi.post("/", async (c) => {
  const body = CreateBody.parse(await c.req.json());
  return c.json(await planItem({ ...body, format: body.format as Format }), 201);
});

const PatchBody = z.object({
  title: z.string().max(500).optional(),
  scheduledFor: z.string().datetime().nullable().optional(),
  channelId: z.string().nullable().optional(),
  brief: z.record(z.string(), z.unknown()).optional(),
  dependsOnItemId: z.string().nullable().optional(),
});

itemsApi.patch("/:id", async (c) => c.json(await updateItem(c.req.param("id"), PatchBody.parse(await c.req.json()))));
itemsApi.delete("/:id", async (c) => {
  await deleteItem(c.req.param("id"));
  return c.json({ ok: true });
});

itemsApi.post("/:id/generate", async (c) => {
  const body = z.object({ feedback: z.string().max(6000).optional(), mode: z.enum(["fresh", "resume"]).optional() }).parse(await c.req.json().catch(() => ({})));
  return c.json(await requestGeneration(c.req.param("id"), body), 202);
});

itemsApi.put("/:id/version", async (c) => {
  const { bodyMd } = z.object({ bodyMd: z.string().min(1).max(400_000) }).parse(await c.req.json());
  return c.json(await saveManualVersion(c.req.param("id"), bodyMd));
});

itemsApi.post("/:id/approve", async (c) => {
  const body = z.object({ force: z.boolean().optional() }).parse(await c.req.json().catch(() => ({})));
  return c.json(await approveItem(c.req.param("id"), { force: body.force }));
});

itemsApi.post("/:id/publish-now", async (c) => {
  const body = z.object({ force: z.boolean().optional() }).parse(await c.req.json().catch(() => ({})));
  const id = c.req.param("id");
  const item = await getItem(id);
  if (["approved", "scheduled"].includes(item.status)) await unapproveItem(id, "publish now");
  if (item.status === "missed") await db.update(schema.contentItems).set({ status: "review", updatedAt: nowIso() }).where(eq(schema.contentItems.id, id));
  return c.json(await approveItem(id, { force: body.force, publishNow: true }));
});

itemsApi.post("/:id/unapprove", async (c) => c.json(await unapproveItem(c.req.param("id"))));
itemsApi.post("/:id/skip", async (c) => c.json(await skipItem(c.req.param("id"))));
itemsApi.post("/:id/mark-published", async (c) => {
  const { url } = z.object({ url: z.string().url().nullish() }).parse(await c.req.json().catch(() => ({})));
  return c.json(await markPublished(c.req.param("id"), url ?? null));
});

itemsApi.post("/:id/retry", async (c) => {
  const id = c.req.param("id");
  const item = await getItem(id);
  if (!item.currentVersionId) return c.json(await requestGeneration(id), 202);
  await cancelJobsForItem(id, ["buffer_push", "publish_git", "newsletter_ready"]);
  await db.update(schema.contentItems).set({ status: "review", error: null, updatedAt: nowIso() }).where(eq(schema.contentItems.id, id));
  return c.json(await approveItem(id, { force: true }));
});

// ---- Assets (images for Buffer posts, blog covers) ----

const ASSET_DIR = path.join(DATA_DIR, "assets");

itemsApi.post("/:id/assets", async (c) => {
  const item = await getItem(c.req.param("id"));
  const form = await c.req.parseBody();
  const file = form.file;
  if (!(file instanceof File)) throw new HttpError(400, "FILE_REQUIRED", "upload a file field named file");
  if (!/^image\/(png|jpe?g|webp|gif)$/.test(file.type)) throw new HttpError(415, "IMAGE_ONLY", "images only (png, jpg, webp, gif)");
  if (file.size > 15 * 1024 * 1024) throw new HttpError(413, "TOO_BIG", "15 MB max");
  const dir = path.join(ASSET_DIR, item.id);
  fs.mkdirSync(dir, { recursive: true });
  const kind = String(form.kind || "image") === "cover" ? "cover" : "image";
  const ext = path.extname(file.name).toLowerCase().replace(/[^.a-z]/g, "") || ".png";
  const name = kind === "cover" ? `cover${ext}` : `${Date.now().toString(36)}${ext}`;
  const localPath = path.join(dir, name);
  fs.writeFileSync(localPath, Buffer.from(await file.arrayBuffer()));
  const id = ulid();
  await db.insert(schema.assets).values({ id, itemId: item.id, kind, localPath, alt: String(form.alt || "") || null, createdAt: nowIso() });
  emit("user", "item", item.id, "asset.added", { kind, name });
  return c.json(await db.select().from(schema.assets).where(eq(schema.assets.id, id)).get(), 201);
});

itemsApi.delete("/:id/assets/:assetId", async (c) => {
  const a = await db.select().from(schema.assets).where(eq(schema.assets.id, c.req.param("assetId"))).get();
  if (a) {
    fs.rmSync(a.localPath, { force: true });
    await db.delete(schema.assets).where(eq(schema.assets.id, a.id));
  }
  return c.json({ ok: true });
});

// ---- Export the current version to a Google Doc (optional, on request) ----

itemsApi.post("/:id/export-doc", async (c) => {
  const item = await getItem(c.req.param("id"));
  const v = await currentVersion(item);
  if (!v) throw new HttpError(409, "NO_VERSION", "nothing to export");
  const sections = v.bodyMd
    .replace(/^---[\s\S]*?\n---\n/, "")
    .split(/\n(?=##\s)/)
    .map((chunk) => {
      const m = chunk.match(/^##\s+(.*)\n?([\s\S]*)$/);
      return m ? { heading: m[1].trim(), level: 2, body: m[2].trim() } : { body: chunk.trim() };
    })
    .filter((s) => s.body || ("heading" in s && s.heading));
  const payload = JSON.stringify({ title: `${item.title.replace(/&/g, "and")} - v${v.n}`, sections });
  const r = await run(PYTHON_BIN, [path.join(NEXIS_ROOT, "tools", "gdocs", "save_content.py")], {
    cwd: NEXIS_ROOT,
    input: payload,
    timeoutMs: 180_000,
    env: gwsChildEnv({ ...process.env, PYTHONIOENCODING: "utf-8" }),
  });
  let out: any = null;
  try {
    out = JSON.parse(r.out.trim().split(/\r?\n/).pop() || "");
  } catch {
    /* fall through */
  }
  if (!out?.doc_url) throw new HttpError(502, "DOC_EXPORT_FAILED", `Doc export failed: ${tail(r.err || r.out, 400)}`);
  await db.update(schema.contentItems).set({ docUrl: out.doc_url, updatedAt: nowIso() }).where(eq(schema.contentItems.id, item.id));
  emit("user", "item", item.id, "doc.exported", { url: out.doc_url });
  return c.json({ docUrl: out.doc_url });
});

/** Enqueue a manual generate for many items at once (calendar "generate the week"). */
itemsApi.post("/bulk/generate", async (c) => {
  const { ids } = z.object({ ids: z.array(z.string()).max(50) }).parse(await c.req.json());
  const out = [];
  for (const id of ids) out.push(await enqueue({ type: "generate", itemId: id, priority: 4 }));
  return c.json({ queued: out.length }, 202);
});
