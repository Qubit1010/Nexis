import fs from "node:fs";
import path from "node:path";
import { Hono } from "hono";
import { streamSSE } from "hono/streaming";
import { desc, eq, inArray } from "drizzle-orm";
import { z } from "zod";
import { db, schema } from "../db/index.ts";
import { DATA_DIR, NEXIS_ROOT, TZ, rootEnv } from "../config.ts";
import { HttpError } from "../lib/http.ts";
import { ulid } from "../lib/ids.ts";
import { nowIso } from "../lib/time.ts";
import { emit, subscribe } from "../lib/events.ts";
import { run } from "../lib/proc.ts";
import { getSettings, putSettings, DEFAULT_SETTINGS, type Settings } from "../settings.ts";
import { safeParse } from "../engine/contract.ts";
import { killRun, liveRuns } from "../engine/generate.ts";
import { claudeAuthProbe, isSubscriptionAuth, lastRateLimit, resolveBin } from "../engine/claude-cli.ts";
import { enqueue, LANE_OF } from "../scheduler/queue.ts";
import { kick, laneState } from "../scheduler/tick.ts";
import { nextRunAfter, validCron } from "../scheduler/cron.ts";
import { attention } from "../items.ts";
import { listChannels } from "../publish/buffer.ts";
import { gwsHealth, findGwsRunJs } from "../integrations/gws.ts";

export const systemApi = new Hono();

// ---- Overview (home page) ----

systemApi.get("/overview", async (c) => {
  const s = await getSettings();
  const att = await attention(s.atRiskHours);
  const counts = await db.select({ status: schema.contentItems.status }).from(schema.contentItems);
  const byStatus: Record<string, number> = {};
  for (const r of counts) byStatus[r.status] = (byStatus[r.status] || 0) + 1;
  const inbox = (await db.select({ id: schema.ideas.id }).from(schema.ideas).where(eq(schema.ideas.status, "inbox"))).length;
  const activeJobs = await db.select().from(schema.jobs).where(inArray(schema.jobs.status, ["queued", "running", "needs_check"]));
  return c.json({
    attention: att.map((a) => ({ reason: a.reason, item: { ...a.item, brief: safeParse(a.item.briefJson) } })),
    byStatus,
    inbox,
    jobs: { queued: activeJobs.filter((j) => j.status === "queued").length, running: activeJobs.filter((j) => j.status === "running").length, needsCheck: activeJobs.filter((j) => j.status === "needs_check").length },
    lanes: laneState(),
    rateLimit: lastRateLimit,
    cadence: s.cadence,
    liveRuns: [...liveRuns.keys()],
  });
});

// ---- Runs ----

systemApi.get("/runs", async (c) => {
  const itemId = c.req.query("itemId");
  const rows = itemId
    ? await db.select().from(schema.runs).where(eq(schema.runs.itemId, itemId)).orderBy(desc(schema.runs.startedAt))
    : await db.select().from(schema.runs).orderBy(desc(schema.runs.startedAt)).limit(200);
  const items = await db.select({ id: schema.contentItems.id, title: schema.contentItems.title, format: schema.contentItems.format }).from(schema.contentItems);
  const byId = new Map(items.map((i) => [i.id, i]));
  return c.json(rows.map((r) => ({ ...r, item: r.itemId ? byId.get(r.itemId) ?? null : null, live: liveRuns.has(r.id) })));
});

/** A finished (or running) run's transcript, condensed from stream.jsonl into the same events the live stream sends. */
systemApi.get("/runs/:id", async (c) => {
  const r = await db.select().from(schema.runs).where(eq(schema.runs.id, c.req.param("id"))).get();
  if (!r) throw new HttpError(404, "NOT_FOUND", "run not found");
  const events: unknown[] = [];
  if (r.logPath && fs.existsSync(r.logPath)) {
    for (const line of fs.readFileSync(r.logPath, "utf8").split(/\r?\n/)) {
      if (!line.trim()) continue;
      try {
        const ev = JSON.parse(line);
        if (ev.type === "assistant") {
          for (const b of ev.message?.content || []) {
            if (b.type === "tool_use") events.push({ kind: "tool", name: b.name, detail: JSON.stringify(b.input ?? {}).slice(0, 240) });
            else if (b.type === "text" && b.text) events.push({ kind: "text", text: b.text });
          }
        } else if (ev.type === "result") events.push({ kind: "result", text: String(ev.result ?? "").slice(0, 2000), cost: ev.total_cost_usd, turns: ev.num_turns });
      } catch {
        /* skip noise */
      }
    }
  }
  return c.json({ run: r, events: events.slice(-400), live: liveRuns.has(r.id) });
});

systemApi.get("/runs/:id/stream", (c) => {
  const id = c.req.param("id");
  const live = liveRuns.get(id);
  return streamSSE(c, async (stream) => {
    if (!live) {
      await stream.writeSSE({ event: "end", data: "{}" });
      return;
    }
    for (const e of live.events) await stream.writeSSE({ data: JSON.stringify(e) });
    let open = true;
    const fn = (e: unknown) => void stream.writeSSE({ data: JSON.stringify(e) }).catch(() => (open = false));
    live.listeners.add(fn);
    stream.onAbort(() => {
      open = false;
    });
    while (open && liveRuns.has(id)) await stream.sleep(1000);
    live.listeners.delete(fn);
    await stream.writeSSE({ event: "end", data: "{}" }).catch(() => {});
  });
});

systemApi.post("/runs/:id/kill", async (c) => {
  if (!killRun(c.req.param("id"))) throw new HttpError(404, "NOT_LIVE", "run is not live");
  emit("user", "run", c.req.param("id"), "run.kill_requested");
  return c.json({ ok: true });
});

// ---- Jobs ----

systemApi.get("/jobs", async (c) => {
  const status = c.req.query("status");
  const rows = status
    ? await db.select().from(schema.jobs).where(eq(schema.jobs.status, status)).orderBy(desc(schema.jobs.updatedAt)).limit(300)
    : await db.select().from(schema.jobs).orderBy(desc(schema.jobs.updatedAt)).limit(300);
  return c.json(rows);
});

systemApi.post("/jobs/:id/retry", async (c) => {
  const j = await db.select().from(schema.jobs).where(eq(schema.jobs.id, c.req.param("id"))).get();
  if (!j) throw new HttpError(404, "NOT_FOUND", "job not found");
  if (["queued", "running"].includes(j.status)) throw new HttpError(409, "ACTIVE", "job is already active");
  await db.update(schema.jobs).set({ status: "queued", dueAt: nowIso(), attempts: 0, lastError: null, finishedAt: null, updatedAt: nowIso() }).where(eq(schema.jobs.id, j.id));
  emit("user", "job", j.id, "job.retry_requested");
  kick();
  return c.json({ ok: true });
});

systemApi.post("/jobs/:id/cancel", async (c) => {
  await db.update(schema.jobs).set({ status: "cancelled", updatedAt: nowIso(), finishedAt: nowIso() }).where(eq(schema.jobs.id, c.req.param("id")));
  return c.json({ ok: true });
});

/** needs_check resolved by a human: "done" (it happened) or "retry" (it did not). */
systemApi.post("/jobs/:id/resolve", async (c) => {
  const { outcome } = z.object({ outcome: z.enum(["done", "retry"]) }).parse(await c.req.json());
  const j = await db.select().from(schema.jobs).where(eq(schema.jobs.id, c.req.param("id"))).get();
  if (!j || j.status !== "needs_check") throw new HttpError(409, "NOT_NEEDS_CHECK", "job is not waiting on a check");
  await db
    .update(schema.jobs)
    .set(outcome === "done" ? { status: "done", finishedAt: nowIso(), updatedAt: nowIso() } : { status: "queued", dueAt: nowIso(), attempts: 0, updatedAt: nowIso() })
    .where(eq(schema.jobs.id, j.id));
  kick();
  return c.json({ ok: true });
});

// ---- Automations ----

systemApi.get("/automations", async (c) => {
  const rows = await db.select().from(schema.automations).orderBy(schema.automations.createdAt);
  const ids = rows.map((r) => r.lastJobId).filter(Boolean) as string[];
  const jobs = ids.length ? await db.select().from(schema.jobs).where(inArray(schema.jobs.id, ids)) : [];
  const byId = new Map(jobs.map((j) => [j.id, j]));
  return c.json(rows.map((a) => ({ ...a, payload: safeParse(a.payloadJson), lastJob: a.lastJobId ? byId.get(a.lastJobId) ?? null : null })));
});

const AutomationBody = z.object({
  name: z.string().min(1).max(120).optional(),
  cron: z.string().min(1).max(100).optional(),
  enabled: z.boolean().optional(),
  catchUp: z.enum(["once", "skip"]).optional(),
  maxLateMin: z.number().int().min(1).max(10080).optional(),
  jobType: z.string().optional(),
  payload: z.record(z.string(), z.unknown()).optional(),
});

systemApi.patch("/automations/:id", async (c) => {
  const id = c.req.param("id");
  const a = await db.select().from(schema.automations).where(eq(schema.automations.id, id)).get();
  if (!a) throw new HttpError(404, "NOT_FOUND", "automation not found");
  const body = AutomationBody.parse(await c.req.json());
  if (body.cron && !validCron(body.cron)) throw new HttpError(400, "BAD_CRON", "invalid cron expression");
  const cron = body.cron ?? a.cron;
  const patch: Partial<typeof a> = {
    name: body.name ?? a.name,
    cron,
    enabled: body.enabled ?? a.enabled,
    catchUp: body.catchUp ?? a.catchUp,
    maxLateMin: body.maxLateMin ?? a.maxLateMin,
    payloadJson: body.payload ? JSON.stringify(body.payload) : a.payloadJson,
  };
  // Re-anchor on enable or a schedule change, so turning something on never "catches up" a stale slot.
  if (body.cron || (body.enabled && !a.enabled)) patch.nextRunAt = nextRunAfter(cron, a.tz, new Date());
  await db.update(schema.automations).set(patch).where(eq(schema.automations.id, id));
  emit("user", "automation", id, "automation.updated", body);
  return c.json(await db.select().from(schema.automations).where(eq(schema.automations.id, id)).get());
});

systemApi.post("/automations", async (c) => {
  const body = AutomationBody.required({ name: true, cron: true, jobType: true }).parse(await c.req.json());
  if (!validCron(body.cron)) throw new HttpError(400, "BAD_CRON", "invalid cron expression");
  if (!LANE_OF[body.jobType] || ["generate", "revise", "buffer_push", "publish_git", "newsletter_ready"].includes(body.jobType)) {
    throw new HttpError(400, "BAD_JOB", "automations can run prepare_week, buffer_reconcile, sheet_mirror or shell");
  }
  const id = ulid();
  const tz = TZ;
  await db.insert(schema.automations).values({
    id,
    name: body.name,
    jobType: body.jobType,
    cron: body.cron,
    tz,
    enabled: body.enabled ?? true,
    catchUp: body.catchUp ?? "once",
    maxLateMin: body.maxLateMin ?? 720,
    payloadJson: JSON.stringify(body.payload ?? {}),
    nextRunAt: nextRunAfter(body.cron, tz, new Date()),
    createdAt: nowIso(),
  });
  return c.json(await db.select().from(schema.automations).where(eq(schema.automations.id, id)).get(), 201);
});

systemApi.delete("/automations/:id", async (c) => {
  const a = await db.select().from(schema.automations).where(eq(schema.automations.id, c.req.param("id"))).get();
  if (a?.builtin) throw new HttpError(409, "BUILTIN", "built-in automations can be disabled, not deleted");
  await db.delete(schema.automations).where(eq(schema.automations.id, c.req.param("id")));
  return c.json({ ok: true });
});

systemApi.post("/automations/:id/run-now", async (c) => {
  const a = await db.select().from(schema.automations).where(eq(schema.automations.id, c.req.param("id"))).get();
  if (!a) throw new HttpError(404, "NOT_FOUND", "automation not found");
  const job = await enqueue({ type: a.jobType, payload: safeParse(a.payloadJson), automationId: a.id, priority: 3 });
  await db.update(schema.automations).set({ lastRunAt: nowIso(), lastJobId: job.id }).where(eq(schema.automations.id, a.id));
  return c.json(job, 202);
});

// ---- Channels ----

systemApi.get("/channels", async (c) => {
  const rows = await db.select().from(schema.channels).orderBy(schema.channels.createdAt);
  return c.json(rows.map((r) => ({ ...r, config: safeParse(r.configJson) })));
});

systemApi.patch("/channels/:id", async (c) => {
  const id = c.req.param("id");
  const body = z.object({ name: z.string().max(120).optional(), enabled: z.boolean().optional(), config: z.record(z.string(), z.unknown()).optional() }).parse(await c.req.json());
  const ch = await db.select().from(schema.channels).where(eq(schema.channels.id, id)).get();
  if (!ch) throw new HttpError(404, "NOT_FOUND", "channel not found");
  await db
    .update(schema.channels)
    .set({
      name: body.name ?? ch.name,
      enabled: body.enabled ?? ch.enabled,
      configJson: body.config ? JSON.stringify({ ...safeParse(ch.configJson), ...body.config }) : ch.configJson,
    })
    .where(eq(schema.channels.id, id));
  emit("user", "channel", id, "channel.updated", body);
  const out = await db.select().from(schema.channels).where(eq(schema.channels.id, id)).get();
  return c.json({ ...out!, config: safeParse(out!.configJson) });
});

systemApi.get("/buffer/channels", async (c) => {
  try {
    return c.json(await listChannels());
  } catch (e) {
    return c.json({ error: (e as Error).message }, 502);
  }
});

// ---- Settings ----

systemApi.get("/settings", async (c) => c.json(await getSettings()));
systemApi.put("/settings", async (c) => {
  const body = (await c.req.json()) as Partial<Settings>;
  const allowed = Object.fromEntries(Object.entries(body).filter(([k]) => k in DEFAULT_SETTINGS)) as Partial<Settings>;
  const s = await putSettings(allowed);
  emit("user", "settings", null, "settings.updated", Object.keys(allowed));
  return c.json(s);
});

// ---- Activity feed ----

systemApi.get("/events", async (c) => {
  const limit = Math.min(Number(c.req.query("limit") || 100), 500);
  const rows = await db.select().from(schema.events).orderBy(desc(schema.events.id)).limit(limit);
  return c.json(rows.map((e) => ({ ...e, data: safeParse(e.dataJson) })));
});

systemApi.get("/events/stream", (c) =>
  streamSSE(c, async (stream) => {
    let open = true;
    const unsub = subscribe((e) => void stream.writeSSE({ data: JSON.stringify(e) }).catch(() => (open = false)));
    stream.onAbort(() => {
      open = false;
    });
    while (open) {
      await stream.sleep(15_000);
      await stream.writeSSE({ event: "ping", data: "{}" }).catch(() => (open = false));
    }
    unsub();
  }),
);

// ---- Files (run outputs + uploaded assets), confined to the data dir ----

systemApi.get("/files", async (c) => {
  const p = c.req.query("path") || "";
  const abs = path.resolve(p);
  const rel = path.relative(DATA_DIR, abs);
  if (!p || rel.startsWith("..") || path.isAbsolute(rel) || !fs.existsSync(abs) || !fs.statSync(abs).isFile()) {
    throw new HttpError(404, "NOT_FOUND", "file not found");
  }
  const ext = path.extname(abs).toLowerCase();
  const types: Record<string, string> = { ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".gif": "image/gif", ".svg": "image/svg+xml", ".md": "text/markdown; charset=utf-8", ".json": "application/json", ".txt": "text/plain; charset=utf-8" };
  return new Response(fs.readFileSync(abs), {
    headers: { "Content-Type": types[ext] || "application/octet-stream", "Content-Security-Policy": "default-src 'none'; img-src 'self' data:; style-src 'unsafe-inline'", "X-Content-Type-Options": "nosniff" },
  });
});

// ---- Health ----

systemApi.get("/health", async (c) => {
  const env = rootEnv();
  const s = await getSettings();
  const checks: { id: string; label: string; ok: boolean; detail: string }[] = [];
  const add = (id: string, label: string, ok: boolean, detail: string) => checks.push({ id, label, ok, detail });

  let claudeBin = "";
  try {
    claudeBin = resolveBin();
  } catch {
    /* reported below */
  }
  add("claude", "Claude CLI", !!claudeBin && (claudeBin === "claude" ? false : fs.existsSync(claudeBin)), claudeBin || "not found");
  const auth = await claudeAuthProbe(c.req.query("force") === "1");
  add("claude_login", "Claude CLI sign-in", auth.ok, auth.detail);
  const lastRun = await db.select().from(schema.runs).orderBy(desc(schema.runs.startedAt)).get();
  add("claude_auth", "Runs bill the subscription", !lastRun?.apiKeySource || isSubscriptionAuth(lastRun.apiKeySource), lastRun ? `last run apiKeySource=${lastRun.apiKeySource ?? "?"}` : "no runs yet (checked on every run)");
  add("anthropic_key_isolated", "API key kept out of runs", !process.env.ANTHROPIC_API_KEY, process.env.ANTHROPIC_API_KEY ? "ANTHROPIC_API_KEY is in this server's environment; it is stripped from runs, but check how the server was started" : "not in the server environment");

  const gws = await gwsHealth();
  add("gws", "Google Workspace CLI", gws.ok, gws.ok ? `${gws.detail} (${findGwsRunJs()})` : gws.detail);

  if (!env.BUFFER_API_KEY) add("buffer", "Buffer API", false, "BUFFER_API_KEY missing from D:/Nexis/.env");
  else {
    try {
      const { channels } = await listChannels();
      add("buffer", "Buffer API", true, `${channels.length} channels: ${channels.map((x) => `${x.service}/${x.displayName}`).join(", ")}`);
    } catch (e) {
      add("buffer", "Buffer API", false, (e as Error).message);
    }
  }
  add("supabase", "Image hosting (Supabase)", !!(env.SUPABASE_URL && env.SUPABASE_SERVICE_ROLE_KEY), env.SUPABASE_URL ? `bucket "${s.imageHost.bucket}"` : "SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY missing");

  const channels = await db.select().from(schema.channels).where(eq(schema.channels.kind, "git_astro"));
  for (const ch of channels) {
    const cfg = safeParse(ch.configJson);
    const repoOk = fs.existsSync(path.join(cfg.repo || "", ".git"));
    const email = repoOk ? (await run("git", ["config", "user.email"], { cwd: cfg.repo, timeoutMs: 10_000 })).out.trim() : "";
    const hasIdentity = !!(email || s.git.email);
    add(`repo_${ch.id}`, `${ch.name} repo`, repoOk && hasIdentity, !repoOk ? `${cfg.repo} not found` : hasIdentity ? `git identity ${email || s.git.email}` : "no git user.email in this repo: set Git in Settings");
    if (cfg.deployMode === "vercel-cli") {
      const tokenSet = !!env.VERCEL_TOKEN;
      const authFile = path.join(process.env.APPDATA || "", "com.vercel.cli", "Data", "auth.json");
      const loggedIn = tokenSet || fs.existsSync(authFile);
      add(`vercel_${ch.id}`, `${ch.name} deploy (Vercel CLI)`, loggedIn, loggedIn ? (tokenSet ? "VERCEL_TOKEN set" : "CLI logged in") : "not logged in: run `npx vercel login` or set VERCEL_TOKEN in D:/Nexis/.env");
    }
  }
  const py = await run("python", ["--version"], { timeoutMs: 10_000 });
  add("python", "Python", py.code === 0, (py.out || py.err).trim());
  add("brief", "Daily brief project", fs.existsSync(path.join(NEXIS_ROOT, "projects", "daily-news-brief", "package.json")), "projects/daily-news-brief");
  return c.json({ checks, ok: checks.every((x) => x.ok) });
});
