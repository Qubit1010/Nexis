import { spawn, type ChildProcess } from "node:child_process";
import fs from "node:fs";
import * as cfg from "./config.ts";
import { HttpError, killTree, killTreeSync } from "./spawn.ts";

/**
 * Process supervisor for the Projects launcher. Separate concern from the
 * claude guardrails: this runs known local dev servers from the curated
 * projects.json registry — the browser only ever sends an id.
 */

export interface ProjectEntry {
  id: string;
  label: string;
  description: string;
  dir: string;
  command: string;
  url: string;
  port: number;
  ready_regex: string;
}

export type ProjectStatus = "stopped" | "starting" | "running" | "exited";

interface ProcState {
  status: ProjectStatus;
  proc: ChildProcess | null;
  pid: number | null;
  started: string | null;
  exit_code: number | null;
  logs: string[];
}

const MAX_LOG_LINES = 200;
const states = new Map<string, ProcState>();

export function loadProjects(): ProjectEntry[] {
  return JSON.parse(fs.readFileSync(cfg.PROJECTS_FILE, "utf8")) as ProjectEntry[];
}

function findEntry(id: string): ProjectEntry {
  const entry = loadProjects().find((p) => p.id === id);
  if (!entry) throw new HttpError(400, "UNKNOWN_PROJECT", `unknown project: ${id}`);
  return entry;
}

function getState(id: string): ProcState {
  let s = states.get(id);
  if (!s) {
    s = { status: "stopped", proc: null, pid: null, started: null, exit_code: null, logs: [] };
    states.set(id, s);
  }
  return s;
}

function pushLogs(s: ProcState, chunk: string, ready: RegExp): void {
  for (const line of chunk.split(/\r?\n/)) {
    if (!line.trim()) continue;
    s.logs.push(line.slice(0, 400));
    if (s.logs.length > MAX_LOG_LINES) s.logs.splice(0, s.logs.length - MAX_LOG_LINES);
    if (s.status === "starting" && ready.test(line)) s.status = "running";
  }
}

function view(entry: ProjectEntry, s: ProcState, logLines = 40) {
  return {
    id: entry.id,
    label: entry.label,
    description: entry.description,
    url: entry.url,
    port: entry.port,
    status: s.status,
    pid: s.pid,
    started: s.started,
    exit_code: s.exit_code,
    logs: s.logs.slice(-logLines),
  };
}

export type ProjectView = ReturnType<typeof view>;

export function projectsState(): ProjectView[] {
  return loadProjects().map((e) => view(e, getState(e.id)));
}

export function projectLogs(id: string): string[] {
  findEntry(id);
  return getState(id).logs.slice();
}

export function startProject(id: string): ProjectView {
  const entry = findEntry(id);
  const s = getState(id);
  if (s.status === "starting" || s.status === "running") {
    throw new HttpError(409, "ALREADY_RUNNING", `${entry.label} is already running`);
  }
  if (!fs.existsSync(entry.dir)) {
    throw new HttpError(500, "DIR_MISSING", `project dir missing: ${entry.dir}`);
  }

  // Trusted static command string from the registry; shell resolves npm/npx.
  const proc = spawn(entry.command, { cwd: entry.dir, shell: true, windowsHide: true });
  const ready = new RegExp(entry.ready_regex, "i");
  s.status = "starting";
  s.proc = proc;
  s.pid = proc.pid ?? null;
  s.started = new Date().toISOString();
  s.exit_code = null;
  s.logs = [];

  proc.stdout?.on("data", (d) => pushLogs(s, String(d), ready));
  proc.stderr?.on("data", (d) => pushLogs(s, String(d), ready));
  proc.on("error", (e) => {
    s.logs.push(`[supervisor] spawn error: ${e.message}`);
    s.status = "exited";
    s.proc = null;
  });
  proc.on("close", (code) => {
    if (s.status !== "stopped") s.status = "exited"; // died on its own
    s.exit_code = code;
    s.proc = null;
  });

  return view(entry, s);
}

export function stopProject(id: string): ProjectView {
  const entry = findEntry(id);
  const s = getState(id);
  s.status = "stopped"; // set first so 'close' doesn't flip it to "exited"
  if (s.pid) killTree(s.pid); // taskkill /T /F takes the shell + npm + dev-server tree
  s.proc = null;
  s.pid = null;
  return view(entry, s);
}

/** Best-effort shutdown of every supervised project (server exit cleanup). */
export function stopAllProjects(): void {
  for (const s of states.values()) {
    s.status = "stopped";
    if (s.pid) killTreeSync(s.pid);
    s.proc = null;
    s.pid = null;
  }
}

export function openInEditor(id: string): void {
  const entry = findEntry(id);
  // Fire-and-forget: `code <dir>` (VS Code's launcher is a .cmd, needs shell).
  spawn("code", [entry.dir], { shell: true, windowsHide: true, detached: true, stdio: "ignore" }).unref();
}
