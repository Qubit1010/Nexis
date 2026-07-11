import { before, test } from "node:test";
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import type { Hono } from "hono";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const GUARD = path.join(HERE, "hook-guard.mjs");
const FAKE = path.join(HERE, "fake-claude.mjs");

function runGuard(payload: unknown, profile?: string): Promise<number> {
  return new Promise((resolve) => {
    const args = profile ? [GUARD, profile] : [GUARD];
    const p = spawn(process.execPath, args, { stdio: ["pipe", "ignore", "ignore"] });
    p.stdin.write(JSON.stringify(payload));
    p.stdin.end();
    p.on("close", (code) => resolve(code ?? -1));
  });
}

let app: Hono;
let runsDir: string;

before(async () => {
  // Isolate side effects BEFORE the config module loads: temp vault, fake bin,
  // temp runs dir, and fixture registries for projects + skill actions.
  process.env.OBSIDIAN_VAULT_PATH = fs.mkdtempSync(path.join(os.tmpdir(), "ncc-vault-"));
  runsDir = fs.mkdtempSync(path.join(os.tmpdir(), "ncc-runs-"));
  process.env.NCC_RUNS_DIR = runsDir;
  process.env.CLAUDE_BIN = process.execPath;
  process.env.CLAUDE_BIN_ARGS = JSON.stringify([FAKE]);

  const fixtures = fs.mkdtempSync(path.join(os.tmpdir(), "ncc-fixtures-"));
  fs.writeFileSync(
    path.join(fixtures, "fake-server.mjs"),
    `console.log("FAKE SERVER READY");\nsetInterval(() => {}, 1000);\n`,
  );
  fs.writeFileSync(
    path.join(fixtures, "projects.json"),
    JSON.stringify([
      {
        id: "fake-app",
        label: "Fake App",
        description: "long-running test double",
        dir: fixtures,
        command: `"${process.execPath}" fake-server.mjs`,
        url: "http://localhost:9999",
        port: 9999,
        ready_regex: "READY",
      },
    ]),
  );
  process.env.NCC_PROJECTS_FILE = path.join(fixtures, "projects.json");

  fs.writeFileSync(
    path.join(fixtures, "skill-actions.json"),
    JSON.stringify([
      {
        id: "test-action",
        label: "Test Action",
        description: "fixture action",
        skill: "test",
        inputs: [{ name: "text", label: "Text", multiline: true }],
        prompt_template: "Do the thing with: {text}",
        profile: "act",
      },
    ]),
  );
  process.env.NCC_SKILL_ACTIONS_FILE = path.join(fixtures, "skill-actions.json");
  process.env.NCC_CHAT_FILE = path.join(fixtures, "chat-threads.json");

  // Brain panel fixtures: seed the temp vault so the node-native reads are
  // deterministic (the sync-script halves degrade to null without python).
  const vault = process.env.OBSIDIAN_VAULT_PATH;
  fs.mkdirSync(path.join(vault, "wiki"), { recursive: true });
  fs.writeFileSync(path.join(vault, "CRITICAL_FACTS.md"), "# Critical Facts\n\n- fixture fact\n");
  fs.writeFileSync(
    path.join(vault, "wiki", "log.md"),
    "# Wiki Operation Log\n\n- [2026-07-11] fixture ingest entry\n",
  );

  // Scan seam: a stub scanner with an env-controlled sleep (for the 409 test).
  fs.writeFileSync(
    path.join(fixtures, "fake-scan.mjs"),
    `await new Promise((r) => setTimeout(r, Number(process.env.FAKE_SCAN_MS || 0)));\n`,
  );
  process.env.NCC_SCAN_CMD = JSON.stringify([process.execPath, path.join(fixtures, "fake-scan.mjs")]);

  const { apiRoutes } = await import("./routes.ts");
  app = apiRoutes();
});

function post(body: unknown): Promise<Response> {
  return Promise.resolve(
    app.request("/command", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  );
}

async function waitIdle(timeoutMs = 8000): Promise<any> {
  const t0 = Date.now();
  while (Date.now() - t0 < timeoutMs) {
    const s = await (await app.request("/command/status")).json();
    if (!s.running) return s;
    await new Promise((r) => setTimeout(r, 100));
  }
  throw new Error("run never finished");
}

// ---- guardrail layer 2: the PreToolUse hook ----

test("hook-guard blocks sensitive reads, Bash, destructive patterns", async () => {
  assert.equal(await runGuard({ tool_name: "Read", tool_input: { file_path: "C:/x/.env" } }), 2);
  assert.equal(await runGuard({ tool_name: "Read", tool_input: { file_path: "C:/r/client-projects/a/plan.md" } }), 2);
  assert.equal(await runGuard({ tool_name: "Read", tool_input: { file_path: "C:/u/.ssh/id_rsa" } }), 2);
  assert.equal(await runGuard({ tool_name: "Bash", tool_input: { command: "echo hi" } }), 2);
  assert.equal(await runGuard({ tool_name: "Grep", tool_input: { pattern: "rm -rf /" } }), 2);
  assert.equal(await runGuard({ tool_name: "Read", tool_input: { file_path: "C:/r/context/me.md" } }), 0);
  assert.equal(await runGuard({ tool_name: "Glob", tool_input: { pattern: "**/*.md" } }), 0);
});

test("hook-guard act profile: Bash allowed, sensitive + destructive still blocked", async () => {
  assert.equal(await runGuard({ tool_name: "Bash", tool_input: { command: "python scripts/run.py" } }, "act"), 0);
  assert.equal(await runGuard({ tool_name: "Bash", tool_input: { command: "rm -rf C:/x" } }, "act"), 2);
  assert.equal(await runGuard({ tool_name: "Bash", tool_input: { command: "git push --force" } }, "act"), 2);
  assert.equal(await runGuard({ tool_name: "Read", tool_input: { file_path: "C:/x/.env" } }, "act"), 2);
  assert.equal(await runGuard({ tool_name: "Read", tool_input: { file_path: "C:/r/client-projects/a/x.md" } }, "act"), 2);
  // read profile stays the default when the arg is missing or unknown
  assert.equal(await runGuard({ tool_name: "Bash", tool_input: { command: "echo hi" } }, "bogus"), 2);
});

// ---- bin resolution (the ENOENT fix) ----

test("pickRunnableBin prefers .cmd/.exe over the extensionless npm shim", async () => {
  const { pickRunnableBin } = await import("./spawn.ts");
  const whereOut = [
    "C:\\Users\\qubit\\AppData\\Roaming\\npm\\claude",
    "C:\\Users\\qubit\\AppData\\Roaming\\npm\\claude.cmd",
    "",
  ];
  assert.equal(pickRunnableBin(whereOut), "C:\\Users\\qubit\\AppData\\Roaming\\npm\\claude.cmd");
  assert.equal(pickRunnableBin(["C:\\bin\\claude.exe"]), "C:\\bin\\claude.exe");
  // no executable extension anywhere -> first non-empty line (POSIX-style)
  assert.equal(pickRunnableBin(["/usr/local/bin/claude", ""]), "/usr/local/bin/claude");
  assert.equal(pickRunnableBin(["", "  "]), null);
});

// ---- API contract ----

test("GET /commands lists presets without prompts", async () => {
  const r = await app.request("/commands");
  assert.equal(r.status, 200);
  const b = await r.json();
  assert.ok(Array.isArray(b.commands) && b.commands.length >= 3);
  for (const c of b.commands) {
    assert.ok(c.id && c.label && c.description);
    assert.equal(c.prompt, undefined, "prompts must never reach the client");
  }
});

test("POST /command validates confirm and id", async () => {
  let r = await post({ id: "decision-digest" });
  assert.equal(r.status, 400);
  assert.equal((await r.json()).code, "UNCONFIRMED");

  r = await post({ id: "not-a-preset", confirm: true });
  assert.equal(r.status, 400);
  assert.equal((await r.json()).code, "UNKNOWN_COMMAND");
});

test("run lifecycle: 202, mutex 409, ok result saved to vault", async () => {
  const r1 = await post({ id: "decision-digest", confirm: true });
  assert.equal(r1.status, 202);
  const started = await r1.json();
  assert.ok(started.run_id && started.started);

  const r2 = await post({ id: "decision-digest", confirm: true });
  assert.equal(r2.status, 409);
  assert.equal((await r2.json()).code, "RUN_IN_PROGRESS");

  const s = await waitIdle();
  assert.equal(s.last.exit, "ok");
  assert.equal(s.locked, false);
  assert.ok(s.last.result_file, "result file path recorded");
  assert.ok(fs.existsSync(s.last.result_file), "result written into the vault");
  assert.match(fs.readFileSync(s.last.result_file, "utf8"), /Fake report/);
});

test("ceiling: over-cost run locks the deck until /ack", async () => {
  process.env.FAKE_COST = "0.90";
  try {
    const r1 = await post({ id: "brain-pulse", confirm: true });
    assert.equal(r1.status, 202);
    const s = await waitIdle();
    assert.equal(s.locked, true);
    assert.equal(s.last.over_ceiling, true);

    const r2 = await post({ id: "brain-pulse", confirm: true });
    assert.equal(r2.status, 423);
    assert.equal((await r2.json()).code, "CEILING_LOCKED");

    const r3 = await app.request("/command/ack", { method: "POST" });
    assert.equal((await r3.json()).locked, false);
    const s2 = await (await app.request("/command/status")).json();
    assert.equal(s2.locked, false);
  } finally {
    delete process.env.FAKE_COST;
  }
});

// ---- skill quick-actions (act profile) ----

function postAction(body: unknown): Promise<Response> {
  return Promise.resolve(
    app.request("/skill-action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  );
}

test("GET /skill-actions lists actions without prompt templates", async () => {
  const r = await app.request("/skill-actions");
  assert.equal(r.status, 200);
  const b = await r.json();
  assert.equal(b.actions.length, 1);
  assert.equal(b.actions[0].id, "test-action");
  assert.ok(Array.isArray(b.actions[0].inputs));
  assert.equal(b.actions[0].skill, "test", "skill folder exposed for graph mapping");
  assert.equal(b.actions[0].prompt_template, undefined, "templates must never reach the client");
});

test("POST /skill-action validates confirm, id, and inputs", async () => {
  let r = await postAction({ id: "test-action", inputs: { text: "x" } });
  assert.equal((await r.json()).code, "UNCONFIRMED");

  r = await postAction({ id: "nope", inputs: { text: "x" }, confirm: true });
  assert.equal((await r.json()).code, "UNKNOWN_ACTION");

  r = await postAction({ id: "test-action", inputs: {}, confirm: true });
  assert.equal((await r.json()).code, "MISSING_INPUT");

  r = await postAction({ id: "test-action", inputs: { text: "x".repeat(6001) }, confirm: true });
  assert.equal((await r.json()).code, "INPUT_TOO_LONG");
});

test("skill action runs on the act profile and shares the deck engine", async () => {
  const r = await postAction({ id: "test-action", inputs: { text: "hello" }, confirm: true });
  assert.equal(r.status, 202);
  const s = await waitIdle();
  assert.equal(s.last.exit, "ok");
  assert.ok(s.last.run_id.endsWith("test-action"));

  // audit log records the profile
  const log = fs.readFileSync(path.join(runsDir, "log.jsonl"), "utf8").trim().split(/\r?\n/);
  const lastEntry = JSON.parse(log[log.length - 1]);
  assert.equal(lastEntry.profile, "act");

  // the act settings file exists and actually allows Bash (read one denies it)
  const act = JSON.parse(fs.readFileSync(path.join(runsDir, "claude-settings-act.json"), "utf8"));
  assert.ok(act.permissions.allow.includes("Bash"));
  const read = JSON.parse(fs.readFileSync(path.join(runsDir, "claude-settings-read.json"), "utf8"));
  assert.ok(read.permissions.deny.includes("Bash"));
  assert.match(act.hooks.PreToolUse[0].hooks[0].command, /hook-guard\.mjs" act$/);
});

// ---- projects launcher ----

async function waitProject(id: string, want: string, timeoutMs = 8000): Promise<any> {
  const t0 = Date.now();
  while (Date.now() - t0 < timeoutMs) {
    const b = await (await app.request("/projects")).json();
    const p = b.projects.find((x: { id: string }) => x.id === id);
    if (p?.status === want) return p;
    await new Promise((r) => setTimeout(r, 100));
  }
  throw new Error(`project ${id} never reached ${want}`);
}

test("projects: registry served, start -> running, double-start 409, stop", async () => {
  const list = await (await app.request("/projects")).json();
  assert.equal(list.projects.length, 1);
  assert.equal(list.projects[0].status, "stopped");

  const r1 = await app.request("/projects/fake-app/start", { method: "POST" });
  assert.equal(r1.status, 202);
  const running = await waitProject("fake-app", "running");
  assert.ok(running.pid, "supervisor recorded a pid");
  assert.ok(running.logs.some((l: string) => l.includes("FAKE SERVER READY")));

  const r2 = await app.request("/projects/fake-app/start", { method: "POST" });
  assert.equal(r2.status, 409);
  assert.equal((await r2.json()).code, "ALREADY_RUNNING");

  const r3 = await app.request("/projects/fake-app/stop", { method: "POST" });
  assert.equal((await r3.json()).status, "stopped");
  await waitProject("fake-app", "stopped");

  const r4 = await app.request("/projects/nope/start", { method: "POST" });
  assert.equal(r4.status, 400);
  assert.equal((await r4.json()).code, "UNKNOWN_PROJECT");
});

// ---- chat with Nexis (streamed NDJSON, chat profile) ----

function chatMsg(id: string, text: string): Promise<Response> {
  return Promise.resolve(
    app.request(`/chat/threads/${id}/message`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    }),
  );
}

function parseNdjson(txt: string): any[] {
  return txt
    .trim()
    .split(/\r?\n/)
    .filter(Boolean)
    .map((l) => JSON.parse(l));
}

test("chat settings: tightest profile (no Write), hook runs with chat arg", async () => {
  const { ensureRunFiles } = await import("./config.ts");
  ensureRunFiles();
  const chat = JSON.parse(fs.readFileSync(path.join(runsDir, "claude-settings-chat.json"), "utf8"));
  assert.deepEqual(chat.permissions.allow, ["Read", "Glob", "Grep"]);
  assert.ok(chat.permissions.deny.includes("Write"));
  assert.ok(chat.permissions.deny.includes("Bash"));
  assert.match(chat.hooks.PreToolUse[0].hooks[0].command, /hook-guard\.mjs" chat$/);
});

test("chat: create/list/get/delete threads", async () => {
  const r1 = await app.request("/chat/threads", { method: "POST" });
  assert.equal(r1.status, 201);
  const t = await r1.json();
  assert.ok(t.id);
  const list = await (await app.request("/chat/threads")).json();
  assert.ok(list.threads.some((x: { id: string }) => x.id === t.id));
  assert.equal((await app.request("/chat/threads/nope")).status, 404);
  assert.equal((await app.request(`/chat/threads/${t.id}`, { method: "DELETE" })).status, 200);
  assert.equal((await app.request(`/chat/threads/${t.id}`)).status, 404);
});

test("chat turn: streams deltas + tool + done, persists messages + session", async () => {
  const t = await (await app.request("/chat/threads", { method: "POST" })).json();
  const r = await chatMsg(t.id, "What is the top priority?");
  assert.equal(r.status, 200);
  const events = parseNdjson(await r.text()); // resolves when the stream closes
  assert.ok(events.filter((e) => e.type === "delta").length >= 2);
  assert.ok(events.some((e) => e.type === "tool" && e.name === "Read"));
  const done = events[events.length - 1];
  assert.equal(done.type, "done");
  assert.equal(done.exit, "ok");
  assert.equal(done.text, "Hello from fake.");
  assert.ok(done.cost_usd > 0);

  const thread = await (await app.request(`/chat/threads/${t.id}`)).json();
  assert.equal(thread.messages.length, 2);
  assert.equal(thread.messages[0].role, "user");
  assert.equal(thread.messages[1].role, "assistant");
  assert.equal(thread.messages[1].text, "Hello from fake.");
  assert.match(thread.session_id, /^sess-/);
  assert.equal(thread.title, "What is the top priority?");
});

test("chat resume: second turn keeps the session id (--resume passed through)", async () => {
  const t = await (await app.request("/chat/threads", { method: "POST" })).json();
  await (await chatMsg(t.id, "first")).text();
  const s1 = (await (await app.request(`/chat/threads/${t.id}`)).json()).session_id;
  assert.ok(s1);
  await (await chatMsg(t.id, "second")).text();
  const after = await (await app.request(`/chat/threads/${t.id}`)).json();
  // the fake mints a fresh id unless --resume passes the old one back in
  assert.equal(after.session_id, s1, "resume must keep the session id");
  assert.equal(after.messages.length, 4);
});

test("chat validation: empty, too long, unknown thread", async () => {
  const t = await (await app.request("/chat/threads", { method: "POST" })).json();
  let r = await chatMsg(t.id, "   ");
  assert.equal(r.status, 400);
  assert.equal((await r.json()).code, "EMPTY_MESSAGE");
  r = await chatMsg(t.id, "x".repeat(8001));
  assert.equal(r.status, 400);
  assert.equal((await r.json()).code, "MESSAGE_TOO_LONG");
  r = await chatMsg("nope", "hi");
  assert.equal(r.status, 404);
  assert.equal((await r.json()).code, "UNKNOWN_THREAD");
});

test("chat shares the global mutex with the deck", async () => {
  const t = await (await app.request("/chat/threads", { method: "POST" })).json();
  assert.equal((await post({ id: "decision-digest", confirm: true })).status, 202);
  const r = await chatMsg(t.id, "hi while busy");
  assert.equal(r.status, 409);
  assert.equal((await r.json()).code, "RUN_IN_PROGRESS");
  await waitIdle();
  // rejected turn must not have persisted a dangling user message
  const thread = await (await app.request(`/chat/threads/${t.id}`)).json();
  assert.equal(thread.messages.length, 0);
});

test("chat stop: kill mid-turn -> done exit killed", async () => {
  process.env.FAKE_STREAM_HANG = "4000";
  try {
    const t = await (await app.request("/chat/threads", { method: "POST" })).json();
    const pending = chatMsg(t.id, "long one");
    const t0 = Date.now();
    while (Date.now() - t0 < 5000) {
      const s = await (await app.request("/command/status")).json();
      if (s.running) break;
      await new Promise((r) => setTimeout(r, 50));
    }
    await new Promise((r) => setTimeout(r, 300)); // let the deltas land first
    const stop = await app.request(`/chat/threads/${t.id}/stop`, { method: "POST" });
    assert.equal((await stop.json()).stopped, true);
    const events = parseNdjson(await (await pending).text());
    const done = events[events.length - 1];
    assert.equal(done.type, "done");
    assert.equal(done.exit, "killed");
    await waitIdle();
  } finally {
    delete process.env.FAKE_STREAM_HANG;
  }
});

test("chat ceiling: over-cost turn locks the console until /ack", async () => {
  process.env.FAKE_COST = "0.90";
  try {
    const t = await (await app.request("/chat/threads", { method: "POST" })).json();
    const events = parseNdjson(await (await chatMsg(t.id, "expensive question")).text());
    assert.equal(events[events.length - 1].exit, "ok");
    const s = await (await app.request("/command/status")).json();
    assert.equal(s.locked, true);
    const r = await chatMsg(t.id, "another");
    assert.equal(r.status, 423);
    assert.equal((await r.json()).code, "CEILING_LOCKED");
  } finally {
    delete process.env.FAKE_COST;
    await app.request("/command/ack", { method: "POST" });
  }
});

// ---- brain panel: freshness/drift/facts + ops depth + graph rescan ----

test("GET /brain: full shape; node-native reads deterministic, script halves typed", async () => {
  const r = await app.request("/brain");
  assert.equal(r.status, 200);
  const b = await r.json();
  for (const key of ["freshness", "drift", "critical_facts", "wiki_log", "recent_decisions"]) {
    assert.ok(key in b, `payload has ${key}`);
  }
  // Node-native reads hit the seeded temp vault + the real decisions log.
  assert.match(b.critical_facts, /fixture fact/);
  assert.equal(b.wiki_log.length, 1);
  assert.match(b.wiki_log[0], /fixture ingest entry/);
  assert.ok(Array.isArray(b.recent_decisions) && b.recent_decisions.length > 0);
  assert.match(b.recent_decisions[0], /^\[\d{4}-\d{2}-\d{2}\]/);
  // Script halves: parsed JSON when python is available, null otherwise —
  // never a crash, never a non-object.
  if (b.freshness !== null) assert.equal(typeof b.freshness.stale, "boolean");
  if (b.drift !== null) assert.equal(typeof b.drift.in_sync, "boolean");
});

test("GET /ops: spend buckets, recent runs, outputs from the audit log", async () => {
  // Seed two deterministic entries (plus whatever earlier tests logged).
  const logFile = path.join(runsDir, "log.jsonl");
  fs.appendFileSync(
    logFile,
    JSON.stringify({ ts: "2026-07-09T10:00:00Z", label: "Seeded A", profile: "read", cost_usd: 0.1, duration_ms: 1000, exit: "ok", result_file: "C:/tmp/seeded-a.md" }) + "\n" +
    JSON.stringify({ ts: "2026-07-09T11:00:00Z", label: "Seeded B", profile: "act", cost_usd: 0.2, duration_ms: 2000, exit: "ok", result_file: null }) + "\n",
  );
  const r = await app.request("/ops");
  assert.equal(r.status, 200);
  const b = await r.json();
  const day = b.spend_by_day.find((d: { day: string }) => d.day === "2026-07-09");
  assert.ok(day, "seeded day bucketed");
  assert.equal(day.runs, 2);
  assert.ok(Math.abs(day.usd - 0.3) < 1e-9);
  assert.ok(b.recent_runs.some((x: { label: string }) => x.label === "Seeded B"));
  assert.ok(b.recent_outputs.some((o: { file: string }) => o.file === "C:/tmp/seeded-a.md"));
});

test("POST /graph/scan: runs the scanner, returns counts; concurrent scan 409s", async () => {
  const r = await app.request("/graph/scan", { method: "POST" });
  assert.equal(r.status, 200);
  const b = await r.json();
  assert.equal(typeof b.counts, "object");

  process.env.FAKE_SCAN_MS = "800";
  try {
    const [a, c] = await Promise.all([
      app.request("/graph/scan", { method: "POST" }),
      (async () => {
        await new Promise((res) => setTimeout(res, 150)); // let the first grab the flag
        return app.request("/graph/scan", { method: "POST" });
      })(),
    ]);
    assert.equal(a.status, 200);
    assert.equal(c.status, 409);
    assert.equal((await c.json()).code, "SCAN_IN_PROGRESS");
  } finally {
    delete process.env.FAKE_SCAN_MS;
  }
});
