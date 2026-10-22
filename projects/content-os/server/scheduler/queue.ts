import { and, eq, inArray } from "drizzle-orm";
import { db, schema, sqlite } from "../db/index.ts";
import { ulid } from "../lib/ids.ts";
import { addMinutes, nowIso } from "../lib/time.ts";
import { emit } from "../lib/events.ts";

export type Job = typeof schema.jobs.$inferSelect;
export type Lane = "claude" | "io";

export const LANE_OF: Record<string, Lane> = {
  generate: "claude",
  revise: "claude",
  buffer_push: "io",
  buffer_reconcile: "io",
  publish_git: "io",
  newsletter_ready: "io",
  sheet_mirror: "io",
  shell: "io",
  prepare_week: "io",
};

/** Thrown by a handler: put the job back for later without spending an attempt (usage limit, waiting on a dependency). */
export class RequeueError extends Error {
  dueAt: string;
  constructor(dueAt: string, message: string) {
    super(message);
    this.dueAt = dueAt;
  }
}
/** Thrown by a handler: the outcome is unknown and retrying could duplicate a side effect. A human checks. */
export class NeedsCheckError extends Error {}
/** Thrown by a handler: retrying will not help (bad config, validation failure). */
export class FatalError extends Error {}
/** Thrown by a handler: too late to act; hold for a manual decision. */
export class MissedError extends Error {}

export interface EnqueueInput {
  type: string;
  payload?: unknown;
  itemId?: string | null;
  automationId?: string | null;
  idempotencyKey?: string | null;
  dueAt?: string;
  priority?: number;
  maxAttempts?: number;
}

let kickHook: (() => void) | null = null;
export function onEnqueue(fn: () => void): void {
  kickHook = fn;
}

/** Insert a job. With an idempotency key, a second enqueue returns the existing job instead. */
export async function enqueue(input: EnqueueInput): Promise<Job> {
  const now = nowIso();
  if (input.idempotencyKey) {
    const existing = await db.select().from(schema.jobs).where(eq(schema.jobs.idempotencyKey, input.idempotencyKey)).get();
    if (existing) return existing;
  }
  const lane = LANE_OF[input.type];
  if (!lane) throw new Error(`unknown job type ${input.type}`);
  const job = await db
    .insert(schema.jobs)
    .values({
      id: ulid(),
      type: input.type,
      lane,
      payloadJson: JSON.stringify(input.payload ?? {}),
      itemId: input.itemId ?? null,
      automationId: input.automationId ?? null,
      idempotencyKey: input.idempotencyKey ?? null,
      priority: input.priority ?? 5,
      dueAt: input.dueAt ?? now,
      maxAttempts: input.maxAttempts ?? (lane === "claude" ? 2 : 3),
      createdAt: now,
      updatedAt: now,
    })
    .onConflictDoNothing()
    .returning()
    .get();
  const out = job ?? (await db.select().from(schema.jobs).where(eq(schema.jobs.idempotencyKey, input.idempotencyKey!)).get())!;
  emit("scheduler", "job", out.id, "job.queued", { type: out.type, dueAt: out.dueAt, itemId: out.itemId });
  kickHook?.();
  return out;
}

// One statement = atomic in SQLite: no two ticks can claim the same job.
const claimStmt = sqlite.prepare(`
  UPDATE jobs SET status = 'running', locked_at = @now, updated_at = @now, attempts = attempts + 1
  WHERE id = (
    SELECT id FROM jobs WHERE status = 'queued' AND lane = @lane AND due_at <= @now
    ORDER BY priority ASC, due_at ASC LIMIT 1
  ) AND status = 'queued'
  RETURNING *`);

export function claimNext(lane: Lane): Job | null {
  const row = claimStmt.get({ lane, now: nowIso() }) as Record<string, unknown> | undefined;
  if (!row) return null;
  return {
    id: row.id as string,
    type: row.type as string,
    lane: row.lane as string,
    payloadJson: row.payload_json as string,
    itemId: (row.item_id as string) ?? null,
    automationId: (row.automation_id as string) ?? null,
    idempotencyKey: (row.idempotency_key as string) ?? null,
    priority: row.priority as number,
    dueAt: row.due_at as string,
    status: row.status as string,
    attempts: row.attempts as number,
    maxAttempts: row.max_attempts as number,
    lockedAt: (row.locked_at as string) ?? null,
    lastError: (row.last_error as string) ?? null,
    resultJson: (row.result_json as string) ?? null,
    createdAt: row.created_at as string,
    updatedAt: row.updated_at as string,
    finishedAt: (row.finished_at as string) ?? null,
  };
}

async function setJob(id: string, patch: Partial<Job>): Promise<void> {
  await db.update(schema.jobs).set({ ...patch, updatedAt: nowIso() }).where(eq(schema.jobs.id, id));
}

export async function completeJob(job: Job, result: unknown): Promise<void> {
  const now = nowIso();
  await setJob(job.id, { status: "done", finishedAt: now, lockedAt: null, resultJson: JSON.stringify(result ?? null), lastError: null });
  emit("scheduler", "job", job.id, "job.done", { type: job.type, itemId: job.itemId });
}

/** Classify a handler failure into the job's next state. Returns that state. */
export async function failJob(job: Job, err: unknown): Promise<string> {
  const msg = err instanceof Error ? err.message : String(err);
  if (err instanceof RequeueError) {
    // Not the job's fault: give the attempt back.
    await setJob(job.id, { status: "queued", dueAt: err.dueAt, lockedAt: null, lastError: msg, attempts: Math.max(0, job.attempts - 1) });
    emit("scheduler", "job", job.id, "job.requeued", { type: job.type, dueAt: err.dueAt, reason: msg });
    return "queued";
  }
  if (err instanceof NeedsCheckError) {
    await setJob(job.id, { status: "needs_check", lockedAt: null, lastError: msg, finishedAt: nowIso() });
    emit("scheduler", "job", job.id, "job.needs_check", { type: job.type, itemId: job.itemId, error: msg });
    return "needs_check";
  }
  if (err instanceof MissedError) {
    await setJob(job.id, { status: "missed", lockedAt: null, lastError: msg, finishedAt: nowIso() });
    emit("scheduler", "job", job.id, "job.missed", { type: job.type, itemId: job.itemId, error: msg });
    return "missed";
  }
  if (!(err instanceof FatalError) && job.attempts < job.maxAttempts) {
    const backoffMin = 2 ** job.attempts * 2; // 4, 8, 16 ...
    const dueAt = addMinutes(nowIso(), backoffMin);
    await setJob(job.id, { status: "queued", dueAt, lockedAt: null, lastError: msg });
    emit("scheduler", "job", job.id, "job.retry", { type: job.type, dueAt, error: msg });
    return "queued";
  }
  await setJob(job.id, { status: "failed", lockedAt: null, lastError: msg, finishedAt: nowIso() });
  emit("scheduler", "job", job.id, "job.failed", { type: job.type, itemId: job.itemId, error: msg });
  return "failed";
}

export async function cancelJobsForItem(itemId: string, types: string[]): Promise<number> {
  const res = await db
    .update(schema.jobs)
    .set({ status: "cancelled", updatedAt: nowIso(), finishedAt: nowIso() })
    .where(and(eq(schema.jobs.itemId, itemId), inArray(schema.jobs.type, types), eq(schema.jobs.status, "queued")))
    .returning({ id: schema.jobs.id });
  return res.length;
}

export async function activeJobFor(itemId: string, types: string[]): Promise<Job | undefined> {
  return db
    .select()
    .from(schema.jobs)
    .where(and(eq(schema.jobs.itemId, itemId), inArray(schema.jobs.type, types), inArray(schema.jobs.status, ["queued", "running"])))
    .get();
}
