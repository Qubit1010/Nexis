import { Hono } from "hono";
import { desc, eq } from "drizzle-orm";
import { z } from "zod";
import { db, schema } from "../db/index.ts";
import { HttpError } from "../lib/http.ts";
import { nowIso } from "../lib/time.ts";
import { emit } from "../lib/events.ts";
import { IdeaInput, ingestIdea } from "../ideas.ts";
import { planItem } from "../items.ts";
import { FORMATS } from "../settings.ts";

export const ideasApi = new Hono();

ideasApi.get("/", async (c) => {
  const status = c.req.query("status");
  const rows = await db.select().from(schema.ideas).orderBy(desc(schema.ideas.updatedAt)).limit(1000);
  const q = (c.req.query("q") || "").toLowerCase();
  return c.json(
    rows.filter((r) => (!status || r.status === status) && (!q || r.title.toLowerCase().includes(q) || (r.summary || "").toLowerCase().includes(q))),
  );
});

// Single idea or a batch: the daily brief posts one; the importer posts many.
ideasApi.post("/", async (c) => {
  const body = await c.req.json();
  if (Array.isArray(body)) {
    const items = z.array(IdeaInput).max(500).parse(body);
    const results = [];
    for (const i of items) results.push(await ingestIdea(i));
    return c.json({ results, added: results.filter((r) => !r.duplicate).length });
  }
  return c.json(await ingestIdea(IdeaInput.parse(body)));
});

const IdeaPatch = z.object({
  title: z.string().trim().min(1).max(500).optional(),
  summary: z.string().max(8000).nullish(),
  status: z.enum(["inbox", "shortlisted", "used", "archived"]).optional(),
  pillar: z.string().max(100).nullish(),
  notes: z.string().max(4000).nullish(),
});

ideasApi.patch("/:id", async (c) => {
  const id = c.req.param("id");
  const patch = IdeaPatch.parse(await c.req.json());
  const row = await db.select().from(schema.ideas).where(eq(schema.ideas.id, id)).get();
  if (!row) throw new HttpError(404, "NOT_FOUND", "idea not found");
  await db.update(schema.ideas).set({ ...patch, updatedAt: nowIso() }).where(eq(schema.ideas.id, id));
  emit("user", "idea", id, "idea.updated", patch);
  return c.json(await db.select().from(schema.ideas).where(eq(schema.ideas.id, id)).get());
});

ideasApi.delete("/:id", async (c) => {
  await db.delete(schema.ideas).where(eq(schema.ideas.id, c.req.param("id")));
  emit("user", "idea", c.req.param("id"), "idea.deleted");
  return c.json({ ok: true });
});

const PlanBody = z.object({
  format: z.enum(FORMATS as [string, ...string[]]),
  channelId: z.string().nullish(),
  scheduledFor: z.string().datetime().nullish(),
  title: z.string().max(500).optional(),
  brief: z.record(z.string(), z.unknown()).optional(),
  dependsOnItemId: z.string().nullish(),
});

ideasApi.post("/:id/plan", async (c) => {
  const body = PlanBody.parse(await c.req.json());
  const item = await planItem({ ...body, format: body.format as (typeof FORMATS)[number], ideaId: c.req.param("id") });
  return c.json(item, 201);
});
