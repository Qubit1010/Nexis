import { db, schema } from "../db/index.ts";
import { nowIso } from "./time.ts";

export interface ActivityEvent {
  id?: number;
  ts: string;
  actor: string;
  entity: string;
  entityId: string | null;
  type: string;
  data?: unknown;
}

type Listener = (e: ActivityEvent) => void;
const listeners = new Set<Listener>();

export function subscribe(fn: Listener): () => void {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

/** Append to the audit feed and fan out to live UI streams. Never throws. */
export function emit(actor: string, entity: string, entityId: string | null, type: string, data?: unknown): void {
  const e: ActivityEvent = { ts: nowIso(), actor, entity, entityId, type, data };
  try {
    const row = db
      .insert(schema.events)
      .values({
        ts: e.ts,
        actor,
        entity,
        entityId,
        type,
        dataJson: data === undefined ? null : JSON.stringify(data),
      })
      .returning({ id: schema.events.id })
      .get();
    e.id = row.id;
  } catch {
    /* the audit feed must never take a request down */
  }
  for (const fn of listeners) {
    try {
      fn(e);
    } catch {
      /* a broken stream unsubscribes itself */
    }
  }
}
