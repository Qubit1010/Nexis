import { and, eq, sql } from "drizzle-orm";
import { z } from "zod";
import { db, schema } from "./db/index.ts";
import { ulid } from "./lib/ids.ts";
import { nowIso } from "./lib/time.ts";
import { dedupeKey } from "./lib/dedupe.ts";
import { emit } from "./lib/events.ts";

export const IDEA_SOURCES = ["youtube_topic", "youtube_video", "youtube_idea", "news_article", "practical_idea", "topics_sheet", "manual"] as const;

export const IdeaInput = z.object({
  title: z.string().trim().min(1).max(500),
  url: z.string().trim().max(2000).nullish(),
  summary: z.string().max(8000).nullish(),
  source: z.enum(IDEA_SOURCES),
  sourceRef: z.string().max(500).nullish(),
  payload: z.record(z.string(), z.unknown()).nullish(),
  pillar: z.string().max(100).nullish(),
  status: z.enum(["inbox", "shortlisted", "used", "archived"]).optional(),
});
export type IdeaInputT = z.infer<typeof IdeaInput>;

const STATUS_RANK: Record<string, number> = { inbox: 0, archived: 1, shortlisted: 2, used: 3 };

export interface IngestResult {
  id: string;
  duplicate: boolean;
  seenCount: number;
}

/** Insert or bump. A re-bookmark of the same URL (or same title when there is no URL) never duplicates. */
export async function ingestIdea(input: IdeaInputT, actor = "ingest"): Promise<IngestResult> {
  const key = dedupeKey({ url: input.url, title: input.title });
  const now = nowIso();
  const existing = await db.select().from(schema.ideas).where(and(eq(schema.ideas.workspaceId, "default"), eq(schema.ideas.dedupeKey, key))).get();
  if (existing) {
    // A stronger signal wins: a bookmark later copied into Topics Ideas becomes shortlisted, a struck one used.
    const promote = input.status && STATUS_RANK[input.status] > STATUS_RANK[existing.status] ? input.status : existing.status;
    await db
      .update(schema.ideas)
      .set({
        // Re-running the sheet import is not a fresh bookmark.
        seenCount: actor === "import" ? existing.seenCount : sql`${schema.ideas.seenCount} + 1`,
        updatedAt: now,
        status: promote,
        // Fill gaps the first save left, never overwrite what is there.
        summary: existing.summary || input.summary || null,
        url: existing.url || input.url || null,
      })
      .where(eq(schema.ideas.id, existing.id));
    emit(actor, "idea", existing.id, "idea.seen_again", { title: existing.title, source: input.source });
    return { id: existing.id, duplicate: true, seenCount: existing.seenCount + 1 };
  }
  const id = ulid();
  await db.insert(schema.ideas).values({
    id,
    title: input.title,
    summary: input.summary ?? null,
    url: input.url ?? null,
    source: input.source,
    sourceRef: input.sourceRef ?? null,
    payloadJson: input.payload ? JSON.stringify(input.payload) : null,
    dedupeKey: key,
    status: input.status ?? "inbox",
    pillar: input.pillar ?? null,
    createdAt: now,
    updatedAt: now,
  });
  emit(actor, "idea", id, "idea.added", { title: input.title, source: input.source });
  return { id, duplicate: false, seenCount: 1 };
}
