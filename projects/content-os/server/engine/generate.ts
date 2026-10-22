import fs from "node:fs";
import path from "node:path";
import { desc, eq } from "drizzle-orm";
import { db, schema } from "../db/index.ts";
import { PROMPTS_DIR, RUNS_DIR } from "../config.ts";
import { ulid } from "../lib/ids.ts";
import { addMinutes, nowIso, pktParts } from "../lib/time.ts";
import { emit } from "../lib/events.ts";
import { getSettings, type Format } from "../settings.ts";
import { FatalError, RequeueError, type Job } from "../scheduler/queue.ts";
import { lastRateLimit, startEngineRun, type EngineEvent, type EngineHandle, type EngineResult } from "./claude-cli.ts";
import { buildInput, buildPrompt, readOutput, resolveInside, safeParse, type ItemContext } from "./contract.ts";
import { hasFails, runChecks, type Check } from "./checks.ts";

type Item = typeof schema.contentItems.$inferSelect;

// Live runs: the kill button and the Runs stream look them up here.
interface LiveRun {
  handle: EngineHandle;
  itemId: string;
  events: (EngineEvent & { ts: string })[];
  listeners: Set<(e: EngineEvent & { ts: string }) => void>;
}
export const liveRuns = new Map<string, LiveRun>();

export function killRun(runId: string): boolean {
  const live = liveRuns.get(runId);
  if (!live) return false;
  live.handle.kill();
  return true;
}

/** Throws RequeueError when a new claude run should not start yet. */
export async function assertGenerationAllowed(): Promise<void> {
  const s = await getSettings();
  const now = new Date();
  if (s.pauseGeneration) throw new RequeueError(addMinutes(now.toISOString(), 30), "generation is paused in Settings");
  if (s.quietHours) {
    const p = pktParts(now.toISOString());
    const cur = p.h * 60 + p.min;
    const [sh, sm] = s.quietHours.start.split(":").map(Number);
    const [eh, em] = s.quietHours.end.split(":").map(Number);
    const start = sh * 60 + (sm || 0);
    const end = eh * 60 + (em || 0);
    const inside = start <= end ? cur >= start && cur < end : cur >= start || cur < end;
    if (inside) {
      const wait = (end - cur + 1440) % 1440 || 1;
      throw new RequeueError(addMinutes(now.toISOString(), wait), "inside quiet hours");
    }
  }
  const rl = lastRateLimit;
  if (rl && rl.status !== "allowed" && rl.status !== "allowed_warning" && rl.resetsAt && rl.resetsAt * 1000 > Date.now()) {
    throw new RequeueError(new Date(rl.resetsAt * 1000 + 60_000).toISOString(), `usage limit (${rl.rateLimitType ?? "plan"}) until reset`);
  }
  if (rl?.sevenDayUtilization != null && rl.sevenDayUtilization >= s.maxWeeklyUtilization) {
    throw new RequeueError(addMinutes(now.toISOString(), 180), `weekly plan usage at ${Math.round(rl.sevenDayUtilization * 100)}%, above the ${Math.round(s.maxWeeklyUtilization * 100)}% guard`);
  }
}

async function loadContext(item: Item): Promise<Omit<ItemContext, "revision">> {
  const idea = item.ideaId ? await db.select().from(schema.ideas).where(eq(schema.ideas.id, item.ideaId)).get() : null;
  const channel = item.channelId ? await db.select().from(schema.channels).where(eq(schema.channels.id, item.channelId)).get() : null;
  let dependsOn: ItemContext["dependsOn"] = null;
  if (item.dependsOnItemId) {
    const dep = await db.select().from(schema.contentItems).where(eq(schema.contentItems.id, item.dependsOnItemId)).get();
    if (dep) {
      const depChannel = dep.channelId ? await db.select().from(schema.channels).where(eq(schema.channels.id, dep.channelId)).get() : null;
      const cfg = safeParse(depChannel?.configJson);
      const slug = safeParse((await currentVersion(dep))?.metaJson).meta?.slug as string | undefined;
      const localFile = cfg.repo && slug ? path.join(cfg.repo, cfg.contentDir || "src/content/blog", `${slug}.md`) : null;
      dependsOn = { title: dep.title, publishedUrl: dep.publishedUrl, localFile: localFile && fs.existsSync(localFile) ? localFile : null };
    }
  }
  return { item, idea: idea ?? null, channel: channel ?? null, dependsOn };
}

export async function currentVersion(item: Item) {
  if (!item.currentVersionId) return undefined;
  return db.select().from(schema.versions).where(eq(schema.versions.id, item.currentVersionId)).get();
}

async function setItem(id: string, patch: Partial<Item>): Promise<void> {
  await db.update(schema.contentItems).set({ ...patch, updatedAt: nowIso() }).where(eq(schema.contentItems.id, id));
}

function runEngine(runId: string, itemId: string, spec: Parameters<typeof startEngineRun>[0]): Promise<EngineResult> {
  const live: LiveRun = { handle: null as unknown as EngineHandle, itemId, events: [], listeners: new Set() };
  const handle = startEngineRun(spec, (e) => {
    const ev = { ...e, ts: nowIso() };
    live.events.push(ev);
    if (live.events.length > 500) live.events.shift();
    for (const fn of live.listeners) fn(ev);
    if (e.kind === "init") emit("engine", "run", runId, "run.init", { apiKeySource: e.apiKeySource, model: e.model });
  });
  live.handle = handle;
  liveRuns.set(runId, live);
  void db.update(schema.runs).set({ pid: handle.pid ?? null }).where(eq(schema.runs.id, runId)).run();
  return handle.done.finally(() => setTimeout(() => liveRuns.delete(runId), 60_000));
}

/** generate and revise jobs. Payload: { feedback?: string, mode?: "fresh" | "resume" }. */
export async function runGeneration(job: Job): Promise<unknown> {
  if (!job.itemId) throw new FatalError("generation job without an item");
  const item = await db.select().from(schema.contentItems).where(eq(schema.contentItems.id, job.itemId)).get();
  if (!item) throw new FatalError("item no longer exists");
  // A draft that lands after approval would silently replace the approved version. Requests
  // from the UI un-approve first (requestGeneration), so only stale jobs ever hit this.
  if (["approved", "scheduled", "ready_to_post", "published", "publishing", "skipped"].includes(item.status)) {
    throw new FatalError(`item is ${item.status}; not generating over it`);
  }
  await assertGenerationAllowed();

  const payload = safeParse(job.payloadJson);
  const s = await getSettings();
  const fmt = s.formats[item.format as Format];
  if (!fmt) throw new FatalError(`no engine settings for format ${item.format}`);

  const runId = ulid();
  const runDir = path.join(RUNS_DIR, runId);
  fs.mkdirSync(runDir, { recursive: true });
  const base = await loadContext(item);

  let revision: ItemContext["revision"] = null;
  let resumeSession: string | undefined;
  const prev = await currentVersion(item);
  if (job.type === "revise") {
    if (!prev) throw new FatalError("nothing to revise yet: generate first");
    const previousFile = path.join(runDir, "previous.md");
    fs.writeFileSync(previousFile, prev.bodyMd);
    revision = { previousFile, feedback: String(payload.feedback || "Tighten it.") };
    if (payload.mode === "resume" && prev.runId) {
      const prevRun = await db.select().from(schema.runs).where(eq(schema.runs.id, prev.runId)).get();
      resumeSession = prevRun?.sessionId ?? undefined;
    }
  }
  const ctx: ItemContext = { ...base, revision };
  const input = buildInput(ctx, runDir);
  fs.writeFileSync(path.join(runDir, "input.json"), JSON.stringify(input, null, 2));
  const prompt = buildPrompt(ctx, runDir, input);
  fs.writeFileSync(path.join(runDir, "prompt.md"), prompt);

  const priorStatus = item.status;
  await db.insert(schema.runs).values({
    id: runId,
    jobId: job.id,
    itemId: item.id,
    engine: "claude-cli",
    model: fmt.model,
    status: "running",
    startedAt: nowIso(),
    logPath: path.join(runDir, "stream.jsonl"),
  });
  await setItem(item.id, { status: "generating", error: null });
  emit("engine", "item", item.id, "generation.started", { runId, type: job.type });

  const spec = {
    runId,
    runDir,
    prompt,
    model: fmt.model,
    maxTurns: fmt.maxTurns,
    timeoutMs: fmt.timeoutMin * 60_000,
    systemPromptFile: path.join(PROMPTS_DIR, "_contract.md"),
    resume: resumeSession,
    extraReadDirs: [
      ...channelReadDirs(base.channel?.configJson),
      ...(base.dependsOn?.localFile ? [path.dirname(base.dependsOn.localFile)] : []),
    ],
  };
  let res = await runEngine(runId, item.id, spec);
  let totalCost = res.costUsd;
  let turns = res.numTurns ?? 0;

  const finishRun = async (status: string, error: string | null) => {
    await db
      .update(schema.runs)
      .set({
        status,
        endedAt: nowIso(),
        durationMs: res.durationMs,
        numTurns: turns,
        costUsdEquiv: totalCost,
        usageJson: JSON.stringify({ usage: res.usage, rateLimit: res.rateLimit }),
        apiKeySource: res.apiKeySource,
        sessionId: res.sessionId,
        error,
      })
      .where(eq(schema.runs.id, runId));
  };
  const restore = () => setItem(item.id, { status: priorStatus === "generating" ? (prev ? "review" : "planned") : priorStatus });

  if (res.status === "rate_limited") {
    await finishRun("rate_limited", res.error);
    await restore();
    const resetMs = res.rateLimit?.resetsAt ? res.rateLimit.resetsAt * 1000 + 60_000 : Date.now() + 60 * 60_000;
    throw new RequeueError(new Date(resetMs).toISOString(), "plan usage limit reached; requeued for the reset");
  }
  if (res.status === "auth_refused" || res.status === "killed" || res.status === "auth_failed") {
    await finishRun(res.status, res.error);
    await restore();
    throw new FatalError(res.status === "killed" ? "run stopped by user" : res.error || "auth refused");
  }

  let parsed: ReturnType<typeof readOutput> | null = null;
  let readErr: string | null = null;
  try {
    parsed = readOutput(runDir);
  } catch (e) {
    readErr = (e as Error).message;
  }
  if (!parsed) {
    await finishRun(res.status === "ok" ? "error" : res.status, readErr || res.error);
    await setItem(item.id, { status: job.attempts >= job.maxAttempts ? "failed" : priorStatus === "generating" ? "planned" : priorStatus, error: readErr || res.error });
    throw new Error(readErr || res.error || "generation failed");
  }

  const channelCfg = safeParse(base.channel?.configJson);
  const check = (main: string) =>
    runChecks(item.format, main, {
      edition: channelCfg.edition,
      categories: channelCfg.categories,
      mainFile: resolveInside(runDir, parsed!.output.files.main),
      sourceUrl: base.dependsOn?.publishedUrl ?? null,
    });
  let checks: Check[] = check(parsed.main);

  // One automatic fix-up turn on the same session, then the reviewer sees whatever remains.
  if (hasFails(checks) && parsed.output.status === "ok" && res.sessionId) {
    const fails = checks.filter((c) => c.level === "fail").map((c) => `- ${c.message}`).join("\n");
    emit("engine", "item", item.id, "generation.fixup", { runId, fails: checks.filter((c) => c.level === "fail").length });
    res = await runEngine(runId, item.id, {
      ...spec,
      prompt: `Content OS re-ran the hard checks on your files and these failed:\n\n${fails}\n\nFix them in place (same files in ${runDir.replace(/\\/g, "/")}), keep everything else, and rewrite output.json.`,
      resume: res.sessionId,
      maxTurns: 15,
      timeoutMs: 10 * 60_000,
    });
    totalCost += res.costUsd;
    turns += res.numTurns ?? 0;
    try {
      parsed = readOutput(runDir);
      checks = check(parsed.main);
    } catch {
      /* keep the first parse and its checks */
    }
  }

  const out = parsed.output;
  const versionId = await storeVersion(item, runDir, runId, parsed, checks, job.type === "revise" ? "revised" : "generated", revision?.feedback ?? null);
  await finishRun(out.status === "blocked" ? "blocked" : "ok", null);
  emit("engine", "item", item.id, "generation.done", { runId, versionId, status: out.status, fails: checks.filter((c) => c.level === "fail").length });
  return { runId, versionId, status: out.status, costUsdEquiv: totalCost };
}

/** Save a validated run folder as the item's new current version and put the item in review. */
export async function storeVersion(
  item: Item,
  runDir: string,
  runId: string | null,
  parsed: ReturnType<typeof readOutput>,
  checks: Check[],
  kind: "generated" | "revised" | "adopted",
  feedback: string | null,
): Promise<string> {
  const out = parsed.output;
  const extra = out.files.extra
    .map((rel) => {
      try {
        const abs = resolveInside(runDir, rel);
        return fs.existsSync(abs) ? { name: rel, path: abs } : null;
      } catch {
        return null;
      }
    })
    .filter(Boolean);
  const imagesDir = path.join(runDir, "images");
  const images = fs.existsSync(imagesDir) ? fs.readdirSync(imagesDir).filter((f) => /\.(png|jpe?g|webp|svg)$/i.test(f)).map((f) => path.join(imagesDir, f)) : [];

  const last = await db.select({ n: schema.versions.n }).from(schema.versions).where(eq(schema.versions.itemId, item.id)).orderBy(desc(schema.versions.n)).get();
  const versionId = ulid();
  await db.insert(schema.versions).values({
    id: versionId,
    itemId: item.id,
    n: (last?.n ?? 0) + 1,
    kind,
    runId,
    bodyMd: parsed.main,
    metaJson: JSON.stringify({
      title: out.title,
      status: out.status,
      blocked_reason: out.blocked_reason ?? null,
      rescue: out.rescue ?? null,
      gate: out.gate ?? null,
      meta: out.meta,
      sources: out.sources,
      notes: out.notes_for_reviewer ?? null,
    }),
    filesJson: JSON.stringify({ runDir, main: resolveInside(runDir, out.files.main), extra, images }),
    checksJson: JSON.stringify(checks),
    feedback,
    createdAt: nowIso(),
  });
  await setItem(item.id, {
    currentVersionId: versionId,
    status: "review",
    approvedAt: null,
    error: out.status === "blocked" ? `Blocked by the gate: ${out.blocked_reason ?? "see notes"}` : null,
  });
  return versionId;
}

/** Build the run folder (input.json + prompt.md) exactly as a generation run would, without running it. */
export async function prepareRunFolder(itemId: string, runDir: string): Promise<{ prompt: string; systemPromptFile: string }> {
  const item = await db.select().from(schema.contentItems).where(eq(schema.contentItems.id, itemId)).get();
  if (!item) throw new Error("item not found");
  fs.mkdirSync(runDir, { recursive: true });
  const ctx: ItemContext = { ...(await loadContext(item)), revision: null };
  const input = buildInput(ctx, runDir);
  fs.writeFileSync(path.join(runDir, "input.json"), JSON.stringify(input, null, 2));
  const prompt = buildPrompt(ctx, runDir, input);
  fs.writeFileSync(path.join(runDir, "prompt.md"), prompt);
  return { prompt, systemPromptFile: path.join(PROMPTS_DIR, "_contract.md") };
}

/**
 * Adopt a run folder produced outside the scheduler (a draft written in a normal Claude
 * session against the same contract): validate output.json, run the same checks, store it.
 */
export async function adoptRunFolder(itemId: string, runDir: string): Promise<{ versionId: string; checks: Check[] }> {
  const item = await db.select().from(schema.contentItems).where(eq(schema.contentItems.id, itemId)).get();
  if (!item) throw new Error("item not found");
  const parsed = readOutput(runDir);
  const ctx = await loadContext(item);
  const cfg = safeParse(ctx.channel?.configJson);
  const checks = runChecks(item.format, parsed.main, {
    edition: cfg.edition,
    categories: cfg.categories,
    mainFile: resolveInside(runDir, parsed.output.files.main),
    sourceUrl: ctx.dependsOn?.publishedUrl ?? null,
  });
  const versionId = await storeVersion(item, runDir, null, parsed, checks, "adopted", null);
  emit("user", "item", item.id, "generation.done", { versionId, status: parsed.output.status, fails: checks.filter((c) => c.level === "fail").length, adopted: true });
  return { versionId, checks };
}

function channelReadDirs(configJson: string | null | undefined): string[] {
  const cfg = safeParse(configJson);
  return cfg.repo && fs.existsSync(cfg.repo) ? [cfg.repo] : [];
}
