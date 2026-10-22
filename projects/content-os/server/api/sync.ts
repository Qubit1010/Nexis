import { Hono } from "hono";
import { z } from "zod";
import { importSheets } from "../integrations/sheets-import.ts";
import { enqueue } from "../scheduler/queue.ts";

export const syncApi = new Hono();

syncApi.post("/import/sheets", async (c) => {
  const body = z
    .object({ dryRun: z.boolean().default(true), sources: z.array(z.enum(["content_ideas", "topics", "schedule"])).optional() })
    .parse(await c.req.json().catch(() => ({})));
  return c.json(await importSheets(body));
});

syncApi.post("/mirror/sync", async (c) => c.json(await enqueue({ type: "sheet_mirror", priority: 4 }), 202));
