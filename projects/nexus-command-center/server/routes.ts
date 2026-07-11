import fs from "node:fs";
import { Hono } from "hono";
import { buildActionRun, loadActions } from "./actions.ts";
import { getBrain } from "./brain.ts";
import {
  createThread,
  deleteThread,
  getThread,
  listThreads,
  startChatTurn,
  stopChatTurn,
  type ChatWireEvent,
} from "./chat.ts";
import * as cfg from "./config.ts";
import { openInEditor, projectLogs, projectsState, startProject, stopProject } from "./projects.ts";
import { runScan } from "./scan.ts";
import { ack, deckState, HttpError, loadPresets, startRun } from "./spawn.ts";
import { getOps, getVitals } from "./vitals.ts";

type Status = 400 | 404 | 409 | 423 | 500;

/** The /api sub-app (architecture.md §6). Exported separately for tests. */
export function apiRoutes(): Hono {
  const api = new Hono();

  api.onError((err, c) => {
    if (err instanceof HttpError) {
      return c.json({ error: err.message, code: err.code }, err.status as Status);
    }
    console.error(err);
    return c.json({ error: "internal error", code: "INTERNAL" }, 500);
  });

  api.get("/graph", (c) => {
    if (!fs.existsSync(cfg.DATA_FILE)) {
      return c.json(
        { error: "system graph not built yet — run: npm run scan", code: "GRAPH_MISSING" },
        404,
      );
    }
    const raw = fs.readFileSync(cfg.DATA_FILE, "utf8");
    return c.body(raw, 200, { "Content-Type": "application/json" });
  });

  api.get("/vitals", async (c) => c.json(await getVitals()));

  // — Brain panel: freshness/drift via the brain-sync script + ops depth —

  api.get("/brain", async (c) => c.json(await getBrain()));

  api.get("/ops", async (c) => c.json(await getOps()));

  api.post("/graph/scan", async (c) => c.json(await runScan())); // throws 409/500

  api.get("/commands", (c) => {
    // Prompts stay server-side — the UI only ever sees id/label/description
    // (preset-only guardrail, decisions.md).
    const commands = loadPresets().map(({ id, label, description }) => ({ id, label, description }));
    return c.json({ commands });
  });

  api.post("/command", async (c) => {
    const body = await c.req.json().catch(() => ({}) as { id?: string; confirm?: boolean });
    if (body.confirm !== true) {
      return c.json({ error: "confirm: true required", code: "UNCONFIRMED" }, 400);
    }
    const preset = loadPresets().find((p) => p.id === body.id);
    if (!preset) {
      return c.json({ error: `unknown command: ${body.id}`, code: "UNKNOWN_COMMAND" }, 400);
    }
    // Deck presets always run the read profile. Throws HttpError 409/423.
    const startedRun = startRun({ id: preset.id, label: preset.label, prompt: preset.prompt, profile: "read" });
    return c.json(startedRun, 202);
  });

  api.get("/command/status", (c) => c.json(deckState()));

  api.post("/command/ack", (c) => {
    ack();
    return c.json({ locked: false });
  });

  // — Skill quick-actions (curated templates, act profile) —

  api.get("/skill-actions", (c) => {
    // Templates stay server-side; the UI gets id/label/description/inputs
    // (+ the skill folder name, so graph skill-nodes can map to an action).
    const actions = loadActions().map(({ id, label, description, inputs, skill }) => ({
      id,
      label,
      description,
      inputs,
      skill,
    }));
    return c.json({ actions });
  });

  api.post("/skill-action", async (c) => {
    const body = await c.req
      .json()
      .catch(() => ({}) as { id?: string; inputs?: Record<string, unknown>; confirm?: boolean });
    if (body.confirm !== true) {
      return c.json({ error: "confirm: true required", code: "UNCONFIRMED" }, 400);
    }
    const spec = buildActionRun(body.id, body.inputs ?? {}); // throws 400s
    return c.json(startRun(spec), 202); // throws 409/423 — same mutex/ceiling as the deck
  });

  // — Chat with Nexis (the one freeform surface; tightest profile, streamed NDJSON) —

  api.get("/chat/threads", (c) => c.json({ threads: listThreads() }));

  api.post("/chat/threads", (c) => c.json(createThread(), 201));

  api.get("/chat/threads/:id", (c) => c.json(getThread(c.req.param("id"))));

  api.delete("/chat/threads/:id", (c) => {
    deleteThread(c.req.param("id"));
    return c.json({ ok: true });
  });

  api.post("/chat/threads/:id/message", async (c) => {
    const body = await c.req.json().catch(() => ({}) as { text?: string });
    // Start the turn BEFORE opening the stream so validation/mutex/lock
    // failures return normal JSON statuses (400/404/409/423), then bridge
    // events into the NDJSON response. Anything emitted in between is buffered.
    const buf: ChatWireEvent[] = [];
    let sink: ((e: ChatWireEvent) => void) | null = null;
    const emit = (e: ChatWireEvent) => (sink ? sink(e) : buf.push(e));
    startChatTurn(c.req.param("id"), body.text ?? "", emit); // throws HttpError

    const enc = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        let closed = false;
        sink = (e) => {
          if (closed) return;
          try {
            controller.enqueue(enc.encode(JSON.stringify(e) + "\n"));
          } catch {
            closed = true; // client went away — the run still finishes and persists
            return;
          }
          if (e.type === "done") {
            closed = true;
            try {
              controller.close();
            } catch {
              /* already closed */
            }
          }
        };
        for (const e of buf) sink(e);
        buf.length = 0;
      },
      cancel() {
        sink = () => {}; // swallow the rest; chat.ts persists on final regardless
      },
    });
    return c.body(stream, 200, { "Content-Type": "application/x-ndjson" });
  });

  api.post("/chat/threads/:id/stop", (c) => c.json(stopChatTurn(c.req.param("id"))));

  // — Projects launcher (curated registry, server-supervised dev servers) —

  api.get("/projects", (c) => c.json({ projects: projectsState() }));

  api.post("/projects/:id/start", (c) => c.json(startProject(c.req.param("id")), 202));

  api.post("/projects/:id/stop", (c) => c.json(stopProject(c.req.param("id"))));

  api.get("/projects/:id/logs", (c) => c.json({ logs: projectLogs(c.req.param("id")) }));

  api.post("/projects/:id/open-editor", (c) => {
    openInEditor(c.req.param("id"));
    return c.json({ ok: true });
  });

  return api;
}
