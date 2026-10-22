import fs from "node:fs";
import net from "node:net";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { serve } from "@hono/node-server";
import { serveStatic } from "@hono/node-server/serve-static";
import { Hono } from "hono";
import { ZodError } from "zod";
import { DIST_DIR, HOST, PORT } from "./config.ts";
import { guardMutations, HttpError } from "./lib/http.ts";
import { seed } from "./db/seed.ts";
import { ideasApi } from "./api/ideas.ts";
import { itemsApi } from "./api/items.ts";
import { systemApi } from "./api/system.ts";
import { syncApi } from "./api/sync.ts";
import { recover, startScheduler, stopScheduler } from "./scheduler/tick.ts";
import { liveRuns } from "./engine/generate.ts";
import { killTreeSync } from "./engine/claude-cli.ts";

/** A second instance (autostart + a manual start) must exit, not fight over the queue. */
function portInUse(port: number): Promise<boolean> {
  return new Promise((resolve) => {
    const s = net.createServer();
    s.once("error", () => resolve(true));
    s.once("listening", () => s.close(() => resolve(false)));
    s.listen(port, HOST);
  });
}

export function buildApp(): Hono {
  const app = new Hono();
  app.onError((err, c) => {
    if (err instanceof HttpError) return c.json({ error: err.message, code: err.code }, err.status as 400);
    if (err instanceof ZodError) return c.json({ error: err.issues.map((i) => `${i.path.join(".") || "body"}: ${i.message}`).join("; "), code: "INVALID" }, 400);
    if (err instanceof SyntaxError) return c.json({ error: "malformed JSON", code: "INVALID" }, 400);
    console.error(err);
    return c.json({ error: err.message || "internal error", code: "INTERNAL" }, 500);
  });
  app.use("/api/*", guardMutations);
  app.route("/api/ideas", ideasApi);
  app.route("/api/items", itemsApi);
  app.route("/api", syncApi);
  app.route("/api", systemApi);
  app.notFound((c) => (c.req.path.startsWith("/api/") ? c.json({ error: "not found", code: "NOT_FOUND" }, 404) : c.text("not found", 404)));
  if (fs.existsSync(DIST_DIR)) {
    app.use("/*", serveStatic({ root: DIST_DIR.replace(/\\/g, "/") }));
    app.get("*", serveStatic({ path: `${DIST_DIR.replace(/\\/g, "/")}/index.html` }));
  }
  return app;
}

async function main() {
  if (await portInUse(PORT)) {
    console.log(`Content OS is already running on ${HOST}:${PORT}; exiting.`);
    process.exit(0);
  }
  await seed();
  const rec = await recover();
  if (rec.requeued || rec.needsCheck || rec.orphans) console.log("recovered after restart:", rec);
  const app = buildApp();
  serve({ fetch: app.fetch, port: PORT, hostname: HOST }, (info) => {
    console.log(`Content OS -> http://${HOST}:${info.port}`);
    startScheduler();
  });

  let cleaned = false;
  const cleanup = () => {
    if (cleaned) return;
    cleaned = true;
    stopScheduler();
    for (const r of liveRuns.values()) killTreeSync(r.handle.pid);
  };
  process.on("exit", cleanup);
  for (const sig of ["SIGINT", "SIGTERM"] as const) {
    process.on(sig, () => {
      cleanup();
      process.exit(0);
    });
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) void main();
