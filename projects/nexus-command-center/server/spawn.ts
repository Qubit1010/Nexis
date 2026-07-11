import { execFile, execFileSync, spawn, type ChildProcess } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import * as cfg from "./config.ts";

export interface Preset {
  id: string;
  label: string;
  description: string;
  prompt: string;
  output: string;
}

/** One guarded headless run. Deck presets run "read"; skill actions run "act"; chat turns run "chat". */
export type RunProfile = "read" | "act" | "chat";

export interface RunSpec {
  id: string;
  label: string;
  prompt: string;
  profile: RunProfile;
}

export interface LastRun {
  run_id: string;
  label: string;
  cost_usd: number;
  duration_ms: number;
  exit: "ok" | "timeout" | "error" | "killed";
  result_file: string | null;
  over_ceiling: boolean;
}

export class HttpError extends Error {
  status: number;
  code: string;
  // Node strip-only TS: no parameter properties — assign explicitly.
  constructor(status: number, code: string, message?: string) {
    super(message ?? code);
    this.status = status;
    this.code = code;
  }
}

export function loadPresets(): Preset[] {
  return JSON.parse(fs.readFileSync(cfg.COMMANDS_FILE, "utf8")) as Preset[];
}

// The only stateful module: module-level mutex + deck state (architecture.md §8).
let current: { run_id: string; label: string; started: string; proc: ChildProcess } | null = null;
let last: LastRun | null = null;
let locked = false;

export function deckState() {
  return {
    running: !!current,
    current: current
      ? { run_id: current.run_id, label: current.label, started: current.started }
      : null,
    last,
    locked,
    ceilings: cfg.CEILING_USD,
  };
}

export function ack(): void {
  locked = false;
}

/**
 * Pick the Windows-runnable line from `where.exe` output. npm puts the
 * extensionless sh shim first, which spawn() can't execute (ENOENT) — prefer
 * .cmd/.exe/.bat, fall back to the first non-empty line.
 */
export function pickRunnableBin(lines: string[]): string | null {
  const clean = lines.map((l) => l.trim()).filter(Boolean);
  return clean.find((l) => /\.(cmd|exe|bat)$/i.test(l)) ?? clean[0] ?? null;
}

let resolvedBin: string | null = null;
function resolveBin(): string {
  if (resolvedBin) return resolvedBin;
  let bin = cfg.CLAUDE_BIN;
  if (bin === "claude" && process.platform === "win32") {
    try {
      const out = execFileSync("where.exe", ["claude"], { encoding: "utf8" });
      const picked = pickRunnableBin(out.split(/\r?\n/));
      if (picked) bin = picked;
    } catch {
      /* fall through — spawn will surface the error */
    }
  }
  resolvedBin = bin;
  return bin;
}

export function killTree(pid: number | undefined): void {
  if (!pid) return;
  if (process.platform === "win32") {
    execFile("taskkill", ["/PID", String(pid), "/T", "/F"], () => {});
  } else {
    try {
      process.kill(pid, "SIGKILL");
    } catch {
      /* already gone */
    }
  }
}

/** Synchronous variant for shutdown paths, where async kills would be dropped. */
export function killTreeSync(pid: number | undefined): void {
  if (!pid) return;
  try {
    if (process.platform === "win32") {
      execFileSync("taskkill", ["/PID", String(pid), "/T", "/F"], { stdio: "ignore" });
    } else {
      process.kill(pid, "SIGKILL");
    }
  } catch {
    /* already gone */
  }
}

/** Best-effort kill of the in-flight deck run (server shutdown cleanup). */
export function killCurrentRun(): void {
  if (current?.proc.pid) killTreeSync(current.proc.pid);
}

function saveResult(spec: RunSpec, resultText: string, run_id: string, cost: number): string | null {
  try {
    const dir = path.join(cfg.VAULT, "raw", "command-center");
    fs.mkdirSync(dir, { recursive: true });
    const ts = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
    const file = path.join(dir, `${ts}-${spec.id}.md`);
    const fm = `---\nsource: nexus-command-center deck\npreset: ${spec.id}\nprofile: ${spec.profile}\nrun_id: ${run_id}\ncost_usd: ${cost}\ndate: ${new Date().toISOString()}\n---\n\n`;
    fs.writeFileSync(file, fm + resultText, "utf8");
    return file;
  } catch {
    return null;
  }
}

function appendLog(entry: Record<string, unknown>): void {
  try {
    fs.appendFileSync(cfg.LOG_FILE, JSON.stringify(entry) + "\n", "utf8");
  } catch {
    /* audit log must never crash the server */
  }
}

/** Fire one guarded headless run. Throws HttpError on mutex/lock violations. */
export function startRun(spec: RunSpec): { run_id: string; label: string; started: string } {
  if (current) throw new HttpError(409, "RUN_IN_PROGRESS", "A run is already in progress");
  if (locked) throw new HttpError(423, "CEILING_LOCKED", "Acknowledge the over-ceiling run first");

  cfg.ensureRunFiles();
  const run_id = `${Date.now().toString(36)}-${spec.id}`;
  const started = new Date().toISOString();
  const startMs = Date.now();

  const bin = resolveBin();
  const args = [
    ...cfg.CLAUDE_BIN_ARGS,
    "-p", // prompt arrives on stdin — nothing user-controlled in argv
    "--output-format",
    "json",
    "--model",
    cfg.RUN_MODEL,
    "--max-turns",
    // act runs orchestrate a whole skill (research + scripts); give them headroom
    spec.profile === "act" ? "25" : "15",
    "--settings",
    cfg.SETTINGS_FILES[spec.profile],
  ];
  // Windows npm shims are .cmd — those need a shell. Args are static tokens
  // (paths without spaces verified at ensureRunFiles), prompt goes via stdin.
  const useShell = /\.(cmd|bat)$/i.test(bin);
  const proc = spawn(bin, args, {
    cwd: cfg.WORKSPACE,
    shell: useShell,
    windowsHide: true,
    stdio: ["pipe", "pipe", "pipe"],
  });

  let out = "";
  let errOut = "";
  let timedOut = false;
  proc.stdout?.on("data", (d) => (out += d));
  proc.stderr?.on("data", (d) => (errOut += d));
  proc.stdin?.on("error", () => {}); // EPIPE on failed spawn must not crash the server
  proc.stdin?.write(spec.prompt);
  proc.stdin?.end();

  const timer = setTimeout(() => {
    timedOut = true;
    killTree(proc.pid);
  }, cfg.TIMEOUT_MS[spec.profile]);

  let finished = false;
  const finish = (exitCode: number | null, spawnError?: Error) => {
    if (finished) return; // 'error' + 'close' can both fire on a failed spawn
    finished = true;
    clearTimeout(timer);
    let cost = 0;
    let resultText = "";
    let isError = !!spawnError;
    try {
      const jsonStart = out.indexOf("{");
      if (jsonStart >= 0) {
        const parsed = JSON.parse(out.slice(jsonStart));
        cost = Number(parsed.total_cost_usd ?? 0);
        resultText = String(parsed.result ?? "");
        isError = isError || !!parsed.is_error;
      } else if (!timedOut) {
        isError = true;
      }
    } catch {
      if (!timedOut) isError = true;
    }

    const exit: LastRun["exit"] = timedOut
      ? "timeout"
      : isError || exitCode !== 0
        ? "error"
        : "ok";
    const over = cost > cfg.CEILING_USD[spec.profile];
    if (over) locked = true;

    const result_file =
      exit === "ok" && resultText ? saveResult(spec, resultText, run_id, cost) : null;
    const duration_ms = Date.now() - startMs;

    last = { run_id, label: spec.label, cost_usd: cost, duration_ms, exit, result_file, over_ceiling: over };
    appendLog({
      ts: new Date().toISOString(),
      run_id,
      label: spec.label,
      profile: spec.profile,
      cost_usd: cost,
      duration_ms,
      result_file,
      exit,
      ...(spawnError ? { error: spawnError.message } : {}),
      ...(exit === "error" && errOut ? { stderr: errOut.slice(0, 500) } : {}),
    });
    current = null;
  };

  proc.on("error", (e) => finish(null, e));
  proc.on("close", (code) => finish(code));

  current = { run_id, label: spec.label, started, proc };
  return { run_id, label: spec.label, started };
}

// ---- streaming runs (chat) ----

/** Events surfaced from a stream-json run, in arrival order. */
export type StreamRunEvent =
  | { kind: "init"; session_id: string }
  | { kind: "delta"; text: string }
  | { kind: "turn_text"; text: string }
  | { kind: "tool"; name: string; detail: string }
  | {
      kind: "final";
      run_id: string;
      exit: LastRun["exit"];
      cost_usd: number;
      duration_ms: number;
      session_id: string | null;
      result_text: string;
      error: string | null;
    };

export interface StreamRunHandle {
  run_id: string;
  started: string;
  stop: () => void;
}

/**
 * Streaming variant of startRun for chat turns: same module mutex, ceiling
 * lock, timeout and audit log, but `--output-format stream-json` parsed
 * line-by-line and surfaced as events. `resume` continues a prior CLI session
 * (per-thread conversation continuity).
 */
export function startStreamRun(
  spec: RunSpec,
  opts: { resume?: string | null; onEvent: (e: StreamRunEvent) => void },
): StreamRunHandle {
  if (current) throw new HttpError(409, "RUN_IN_PROGRESS", "A run is already in progress");
  if (locked) throw new HttpError(423, "CEILING_LOCKED", "Acknowledge the over-ceiling run first");

  cfg.ensureRunFiles();
  const run_id = `${Date.now().toString(36)}-${spec.id}`;
  const started = new Date().toISOString();
  const startMs = Date.now();

  const bin = resolveBin();
  const args = [
    ...cfg.CLAUDE_BIN_ARGS,
    "-p", // prompt on stdin, as in startRun
    "--output-format",
    "stream-json",
    "--verbose", // print-mode stream-json requires it
    "--include-partial-messages",
    "--model",
    cfg.RUN_MODEL,
    "--max-turns",
    "15",
    "--settings",
    cfg.SETTINGS_FILES[spec.profile],
    ...(opts.resume ? ["--resume", opts.resume] : []),
  ];
  const useShell = /\.(cmd|bat)$/i.test(bin);
  const proc = spawn(bin, args, {
    // Chat runs from the Nexis root so the spawned claude loads CLAUDE.md and
    // answers as Nexis (deck/skill runs use the scratch workspace instead).
    cwd: cfg.NEXIS_ROOT,
    shell: useShell,
    windowsHide: true,
    stdio: ["pipe", "pipe", "pipe"],
  });

  let buf = "";
  let errOut = "";
  let timedOut = false;
  let stopRequested = false;
  let sessionId: string | null = opts.resume ?? null;
  let resultText = "";
  let cost = 0;
  let resultError = false;
  let sawResult = false;

  const handleLine = (line: string) => {
    let ev: {
      type?: string;
      subtype?: string;
      session_id?: unknown;
      event?: { type?: string; delta?: { type?: string; text?: unknown } };
      message?: { content?: unknown };
      total_cost_usd?: unknown;
      result?: unknown;
      is_error?: unknown;
    };
    try {
      ev = JSON.parse(line);
    } catch {
      return; // non-JSON verbose noise — ignore
    }
    if (ev.type === "system" && ev.subtype === "init" && ev.session_id) {
      sessionId = String(ev.session_id);
      opts.onEvent({ kind: "init", session_id: sessionId });
    } else if (ev.type === "stream_event") {
      const se = ev.event;
      if (se?.type === "content_block_delta" && se.delta?.type === "text_delta" && se.delta.text) {
        opts.onEvent({ kind: "delta", text: String(se.delta.text) });
      }
    } else if (ev.type === "assistant") {
      const blocks = ev.message?.content;
      if (Array.isArray(blocks)) {
        for (const b of blocks) {
          if (b?.type === "tool_use") {
            opts.onEvent({
              kind: "tool",
              name: String(b.name ?? "tool"),
              detail: JSON.stringify(b.input ?? {}).slice(0, 160),
            });
          } else if (b?.type === "text" && b.text) {
            // Fallback text channel for when partial deltas aren't available.
            opts.onEvent({ kind: "turn_text", text: String(b.text) });
          }
        }
      }
    } else if (ev.type === "result") {
      sawResult = true;
      cost = Number(ev.total_cost_usd ?? 0);
      resultText = String(ev.result ?? "");
      resultError = !!ev.is_error;
      if (ev.session_id) sessionId = String(ev.session_id);
    }
  };

  proc.stdout?.on("data", (d) => {
    buf += d;
    let i: number;
    while ((i = buf.indexOf("\n")) >= 0) {
      const line = buf.slice(0, i).trim();
      buf = buf.slice(i + 1);
      if (line) handleLine(line);
    }
  });
  proc.stderr?.on("data", (d) => (errOut += d));
  proc.stdin?.on("error", () => {}); // EPIPE on failed spawn must not crash the server
  proc.stdin?.write(spec.prompt);
  proc.stdin?.end();

  const timer = setTimeout(() => {
    timedOut = true;
    killTree(proc.pid);
  }, cfg.TIMEOUT_MS[spec.profile]);

  let finished = false;
  const finish = (exitCode: number | null, spawnError?: Error) => {
    if (finished) return;
    finished = true;
    clearTimeout(timer);
    if (buf.trim()) handleLine(buf.trim()); // flush a final unterminated line

    const isError = !!spawnError || resultError || (!sawResult && !timedOut && !stopRequested);
    const exit: LastRun["exit"] = stopRequested
      ? "killed"
      : timedOut
        ? "timeout"
        : isError || exitCode !== 0
          ? "error"
          : "ok";
    const over = cost > cfg.CEILING_USD[spec.profile];
    if (over) locked = true;
    const duration_ms = Date.now() - startMs;

    last = {
      run_id,
      label: spec.label,
      cost_usd: cost,
      duration_ms,
      exit,
      result_file: null, // the chat thread itself is the record
      over_ceiling: over,
    };
    appendLog({
      ts: new Date().toISOString(),
      run_id,
      label: spec.label,
      profile: spec.profile,
      cost_usd: cost,
      duration_ms,
      result_file: null,
      exit,
      ...(spawnError ? { error: spawnError.message } : {}),
      ...(exit === "error" && errOut ? { stderr: errOut.slice(0, 500) } : {}),
    });
    current = null;
    opts.onEvent({
      kind: "final",
      run_id,
      exit,
      cost_usd: cost,
      duration_ms,
      session_id: sessionId,
      result_text: resultText,
      error: spawnError
        ? spawnError.message
        : exit === "error"
          ? errOut.slice(0, 300) || "run failed"
          : null,
    });
  };

  proc.on("error", (e) => finish(null, e));
  proc.on("close", (code) => finish(code));

  current = { run_id, label: spec.label, started, proc };
  return {
    run_id,
    started,
    stop: () => {
      stopRequested = true;
      killTree(proc.pid);
    },
  };
}
