import { serve } from "@hono/node-server";
import { serveStatic } from "@hono/node-server/serve-static";
import { Hono } from "hono";
import { ensureRunFiles, PORT } from "./config.ts";
import { stopAllProjects } from "./projects.ts";
import { apiRoutes } from "./routes.ts";
import { killCurrentRun } from "./spawn.ts";

ensureRunFiles();

// This process supervises children (deck runs, project dev servers) — take
// them down on shutdown instead of orphaning them. Note: dev deliberately
// runs WITHOUT --watch; an auto-restarting supervisor orphans its children
// and loses run state (mtime churn in this OneDrive tree triggered exactly
// that). Restart manually after server changes.
let cleaned = false;
function cleanup(): void {
  if (cleaned) return;
  cleaned = true;
  killCurrentRun();
  stopAllProjects();
}
process.on("exit", cleanup);
for (const sig of ["SIGINT", "SIGTERM"] as const) {
  process.on(sig, () => {
    cleanup();
    process.exit(0);
  });
}

const app = new Hono();
app.route("/api", apiRoutes());
// Built SPA (run `npm run build` first; dev uses the Vite proxy instead).
app.use("/*", serveStatic({ root: "./dist" }));
app.get("*", serveStatic({ path: "./dist/index.html" }));

serve({ fetch: app.fetch, port: PORT, hostname: "127.0.0.1" }, (info) => {
  console.log(`Nexus Command Center -> http://127.0.0.1:${info.port}`);
});
