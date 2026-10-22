import { and, eq, lte } from "drizzle-orm";
import { db, schema } from "../db/index.ts";
import { nowIso } from "../lib/time.ts";
import { emit } from "../lib/events.ts";
import { killTreeSync } from "../engine/claude-cli.ts";
import { claimNext, completeJob, enqueue, failJob, onEnqueue, type Job, type Lane } from "./queue.ts";
import { nextRunAfter } from "./cron.ts";
import { handle } from "./handlers.ts";

const LANE_CAP: Record<Lane, number> = { claude: 1, io: 2 };
const running: Record<Lane, number> = { claude: 0, io: 0 };
const ON_TIME_MS = 2 * 60_000;
const TICK_MS = Number(process.env.CONTENT_OS_TICK_MS || 30_000);

/**
 * Due automations become jobs. However many occurrences were missed while the
 * PC was off, catch_up=once enqueues exactly one (keyed on the occurrence time,
 * so a double tick cannot duplicate it), and next_run_at always moves to the
 * next occurrence after *now*: a backlog is never replayed.
 */
export async function runAutomations(now = new Date()): Promise<number> {
  const due = await db
    .select()
    .from(schema.automations)
    .where(and(eq(schema.automations.enabled, true), lte(schema.automations.nextRunAt, now.toISOString())));
  let enqueued = 0;
  for (const a of due) {
    const late = now.getTime() - Date.parse(a.nextRunAt!);
    const next = nextRunAfter(a.cron, a.tz, now);
    if (late <= ON_TIME_MS || (a.catchUp === "once" && late <= a.maxLateMin * 60_000)) {
      const job = await enqueue({
        type: a.jobType,
        payload: JSON.parse(a.payloadJson || "{}"),
        automationId: a.id,
        idempotencyKey: `auto:${a.id}:${a.nextRunAt}`,
      });
      await db.update(schema.automations).set({ nextRunAt: next, lastRunAt: now.toISOString(), lastJobId: job.id }).where(eq(schema.automations.id, a.id));
      if (late > ON_TIME_MS) emit("scheduler", "automation", a.id, "automation.caught_up", { missedAt: a.nextRunAt, lateMin: Math.round(late / 60_000) });
      enqueued++;
    } else {
      await db.update(schema.automations).set({ nextRunAt: next }).where(eq(schema.automations.id, a.id));
      emit("scheduler", "automation", a.id, "automation.missed", { missedAt: a.nextRunAt, lateMin: Math.round(late / 60_000) });
    }
  }
  return enqueued;
}

/** Item-facing consequences of a job's final state. */
async function reflectOnItem(job: Job, state: string, error: string): Promise<void> {
  if (!job.itemId) return;
  const patch: Record<string, unknown> = { updatedAt: nowIso() };
  if (state === "failed") {
    patch.status = "failed";
    patch.error = error;
  } else if (state === "missed") {
    patch.status = "missed";
    patch.error = error;
  } else if (state === "needs_check") {
    patch.error = error;
  } else return;
  await db.update(schema.contentItems).set(patch).where(eq(schema.contentItems.id, job.itemId));
}

async function runJob(job: Job): Promise<void> {
  emit("scheduler", "job", job.id, "job.started", { type: job.type, itemId: job.itemId, attempt: job.attempts });
  try {
    const result = await handle(job);
    await completeJob(job, result);
  } catch (e) {
    const state = await failJob(job, e);
    await reflectOnItem(job, state, e instanceof Error ? e.message : String(e));
  }
}

let ticking = false;
export async function tick(): Promise<void> {
  if (ticking) return;
  ticking = true;
  try {
    await runAutomations();
    for (const lane of ["claude", "io"] as Lane[]) {
      while (running[lane] < LANE_CAP[lane]) {
        const job = claimNext(lane);
        if (!job) break;
        running[lane]++;
        void runJob(job).finally(() => {
          running[lane]--;
          kick();
        });
      }
    }
  } catch (e) {
    emit("scheduler", "system", null, "tick.error", { error: (e as Error).message });
  } finally {
    ticking = false;
  }
}

let kickTimer: NodeJS.Timeout | null = null;
/** Run a tick soon (debounced): called after enqueues and job completions. */
export function kick(): void {
  if (kickTimer) return;
  kickTimer = setTimeout(() => {
    kickTimer = null;
    void tick();
  }, 250);
}

/**
 * Boot recovery. Jobs left "running" by a crash go back to the queue (their
 * attempt still counts), except buffer pushes: whether Buffer got the post is
 * unknown, and a duplicate post is worse than a delay, so a human checks.
 * Orphaned claude processes are killed by their recorded pid.
 */
export async function recover(): Promise<{ requeued: number; needsCheck: number; orphans: number }> {
  const stuck = await db.select().from(schema.jobs).where(eq(schema.jobs.status, "running"));
  let requeued = 0;
  let needsCheck = 0;
  for (const j of stuck) {
    if (j.type === "buffer_push") {
      await db.update(schema.jobs).set({ status: "needs_check", lockedAt: null, updatedAt: nowIso(), lastError: "interrupted mid-push; check Buffer before retrying" }).where(eq(schema.jobs.id, j.id));
      needsCheck++;
    } else {
      await db.update(schema.jobs).set({ status: "queued", lockedAt: null, updatedAt: nowIso(), lastError: "interrupted by a restart" }).where(eq(schema.jobs.id, j.id));
      requeued++;
    }
  }
  const orphanRuns = await db.select().from(schema.runs).where(eq(schema.runs.status, "running"));
  for (const r of orphanRuns) {
    killTreeSync(r.pid);
    await db.update(schema.runs).set({ status: "killed", endedAt: nowIso(), error: "orphaned by a restart" }).where(eq(schema.runs.id, r.id));
  }
  // Items stranded mid-generation by the crash (their job was just requeued).
  const generating = await db.select().from(schema.contentItems).where(eq(schema.contentItems.status, "generating"));
  for (const i of generating) {
    await db.update(schema.contentItems).set({ status: i.currentVersionId ? "review" : "planned", updatedAt: nowIso() }).where(eq(schema.contentItems.id, i.id));
  }
  if (requeued || needsCheck || orphanRuns.length) emit("scheduler", "system", null, "recovery", { requeued, needsCheck, orphans: orphanRuns.length });
  return { requeued, needsCheck, orphans: orphanRuns.length };
}

let interval: NodeJS.Timeout | null = null;
export function startScheduler(): void {
  onEnqueue(kick);
  void tick();
  interval = setInterval(() => void tick(), TICK_MS);
}

export function stopScheduler(): void {
  if (interval) clearInterval(interval);
  interval = null;
}

export function laneState() {
  return { running: { ...running }, capacity: LANE_CAP };
}
