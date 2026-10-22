/**
 * Headless `claude -p` runs on the Claude subscription. Ported from
 * projects/nexus-command-center/server/spawn.ts (bin resolution, kill tree,
 * stream-json parsing), without its module-level mutex: the job queue's
 * claude lane (capacity 1) is the concurrency control here.
 */
import { execFile, execFileSync, spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { CLAUDE_BIN, CLAUDE_BIN_ARGS, GUARD_FILE, NEXIS_ROOT, rootEnv } from "../config.ts";

export interface EngineSpec {
  runId: string;
  runDir: string;
  prompt: string;
  model: string;
  maxTurns: number;
  timeoutMs: number;
  systemPromptFile?: string;
  sessionId?: string;
  resume?: string;
  extraReadDirs?: string[];
}

export interface RateLimitInfo {
  status: string;
  resetsAt: number | null;
  rateLimitType?: string;
  sevenDayUtilization?: number;
  fiveHourUtilization?: number;
}

export type EngineStatus = "ok" | "error" | "timeout" | "killed" | "rate_limited" | "auth_refused" | "auth_failed";

/** The CLI's own sign-in is gone; retrying cannot help until someone runs `claude` and /login. */
export const AUTH_FAILED_RE = /failed to authenticate|oauth session expired|not logged in|please run \/login|invalid api key|authentication_failed/i;
export const AUTH_HELP =
  "The Claude CLI is signed out for headless runs. Recommended: in a terminal run `claude setup-token`, then add CLAUDE_CODE_OAUTH_TOKEN=<the token> to D:/Nexis/.env (a long-lived subscription token made for unattended runs). Or run `claude`, type /login and sign in.";

export interface EngineResult {
  status: EngineStatus;
  sessionId: string | null;
  apiKeySource: string | null;
  costUsd: number;
  numTurns: number | null;
  usage: unknown;
  resultText: string;
  error: string | null;
  rateLimit: RateLimitInfo | null;
  durationMs: number;
}

export type EngineEvent =
  | { kind: "init"; sessionId: string; apiKeySource: string | null; model: string | null }
  | { kind: "text"; text: string }
  | { kind: "tool"; name: string; detail: string }
  | { kind: "rate_limit"; info: RateLimitInfo };

/** The last rate-limit window the CLI reported; gates new runs when the plan is nearly used up. */
export let lastRateLimit: RateLimitInfo | null = null;

export function pickRunnableBin(lines: string[]): string | null {
  const clean = lines.map((l) => l.trim()).filter(Boolean);
  return clean.find((l) => /\.(cmd|exe|bat)$/i.test(l)) ?? clean[0] ?? null;
}

let resolvedBin: string | null = null;
export function resolveBin(): string {
  if (resolvedBin) return resolvedBin;
  let bin = CLAUDE_BIN;
  if (bin === "claude" && process.platform === "win32") {
    try {
      const out = execFileSync("where.exe", ["claude"], { encoding: "utf8" });
      const picked = pickRunnableBin(out.split(/\r?\n/));
      if (picked) bin = picked;
    } catch {
      /* fall through: spawn surfaces the error */
    }
  }
  resolvedBin = bin;
  return bin;
}

export function killTree(pid: number | null | undefined): void {
  if (!pid) return;
  if (process.platform === "win32") execFile("taskkill", ["/PID", String(pid), "/T", "/F"], () => {});
  else {
    try {
      process.kill(pid, "SIGKILL");
    } catch {
      /* already gone */
    }
  }
}

export function killTreeSync(pid: number | null | undefined): void {
  if (!pid) return;
  try {
    if (process.platform === "win32") execFileSync("taskkill", ["/PID", String(pid), "/T", "/F"], { stdio: "ignore" });
    else process.kill(pid, "SIGKILL");
  } catch {
    /* already gone */
  }
}

/**
 * Child env: no ANTHROPIC_* (an API key would bill the API instead of the
 * subscription) and none of a host Claude Code session's variables (the
 * server may have been started from inside one).
 */
export function engineEnv(runDir: string): NodeJS.ProcessEnv {
  const env: NodeJS.ProcessEnv = {};
  for (const [k, v] of Object.entries(process.env)) {
    if (/^ANTHROPIC_/i.test(k)) continue;
    if (/^(CLAUDECODE|CLAUDE_CODE_.*|CLAUDE_AGENT_SDK.*|CLAUDE_PID|CLAUDE_EFFORT)$/i.test(k)) continue;
    env[k] = v;
  }
  // The supported always-on auth: a long-lived subscription token from `claude setup-token`,
  // kept in D:/Nexis/.env. It is a subscription login, not an API key.
  const token = rootEnv().CLAUDE_CODE_OAUTH_TOKEN;
  if (token) env.CLAUDE_CODE_OAUTH_TOKEN = token;
  env.CONTENT_OS_RUN_DIR = runDir;
  env.PYTHONIOENCODING = "utf-8";
  return env;
}

/** Subscription sign-ins: interactive OAuth ("none") or the setup-token OAuth token. Anything else is an API key. */
export function isSubscriptionAuth(apiKeySource: string | null): boolean {
  return apiKeySource === "none" || /oauth/i.test(apiKeySource ?? "");
}

const SENSITIVE_READS = [
  "Read(**/.env)",
  "Read(**/.env.*)",
  "Read(**/*.pem)",
  "Read(**/*.key)",
  "Read(**/id_rsa*)",
  "Read(**/.ssh/**)",
  "Read(**/credentials*)",
  "Read(**/settings.local.json)",
];

export function writeRunSettings(runDir: string, extraReadDirs: string[] = []): string {
  const file = path.join(runDir, "settings.json");
  const settings = {
    permissions: {
      // Headless runs cannot prompt: anything not listed is denied (dontAsk).
      allow: ["Read", "Glob", "Grep", "Write", "Edit", "Bash", "WebSearch", "WebFetch", "Skill", "Task", "TodoWrite"],
      deny: ["NotebookEdit", ...SENSITIVE_READS],
      additionalDirectories: [NEXIS_ROOT, runDir, ...extraReadDirs],
    },
    hooks: {
      PreToolUse: [
        {
          matcher: ".*",
          hooks: [{ type: "command", command: `node "${GUARD_FILE}" generate "${runDir}"` }],
        },
      ],
    },
  };
  fs.writeFileSync(file, JSON.stringify(settings, null, 2));
  return file;
}

let authCache: { at: number; ok: boolean; detail: string } | null = null;

/**
 * One tiny haiku call with the exact env runs get, to tell "signed in" from "signed out"
 * before a real run fails. Cached for 10 minutes; `force` re-checks.
 */
export async function claudeAuthProbe(force = false): Promise<{ ok: boolean; detail: string }> {
  if (!force && authCache && Date.now() - authCache.at < 10 * 60_000) return authCache;
  const os = await import("node:os");
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "content-os-probe-"));
  const result = await new Promise<{ ok: boolean; detail: string }>((resolve) => {
    const bin = resolveBin();
    const proc = spawn(bin, [...CLAUDE_BIN_ARGS, "-p", "--output-format", "json", "--model", "haiku", "--max-turns", "1", "--strict-mcp-config"], {
      cwd: dir,
      env: engineEnv(dir),
      shell: /\.(cmd|bat)$/i.test(bin),
      windowsHide: true,
    });
    let out = "";
    proc.stdout?.on("data", (d) => (out += d));
    proc.stdin?.on("error", () => {});
    proc.stdin?.end("Reply with the single word OK.");
    const timer = setTimeout(() => killTree(proc.pid), 90_000);
    proc.on("error", (e) => resolve({ ok: false, detail: e.message }));
    proc.on("close", () => {
      clearTimeout(timer);
      try {
        const j = JSON.parse(out.slice(out.indexOf("{")));
        if (j.is_error) resolve({ ok: false, detail: AUTH_FAILED_RE.test(String(j.result)) ? AUTH_HELP : String(j.result).slice(0, 200) });
        else resolve({ ok: true, detail: "signed in (subscription)" });
      } catch {
        resolve({ ok: false, detail: out.slice(0, 200) || "no response from claude" });
      }
    });
  });
  fs.rmSync(dir, { recursive: true, force: true });
  authCache = { at: Date.now(), ...result };
  return result;
}

export interface EngineHandle {
  pid: number | undefined;
  done: Promise<EngineResult>;
  kill: () => void;
}

export function startEngineRun(spec: EngineSpec, onEvent: (e: EngineEvent) => void = () => {}): EngineHandle {
  fs.mkdirSync(spec.runDir, { recursive: true });
  const settingsFile = writeRunSettings(spec.runDir, spec.extraReadDirs);
  const bin = resolveBin();
  const args = [
    ...CLAUDE_BIN_ARGS,
    "-p", // prompt on stdin: nothing derived from ingested content ever lands in argv
    "--output-format", "stream-json",
    "--verbose",
    "--model", spec.model,
    "--max-turns", String(spec.maxTurns),
    "--permission-mode", "dontAsk",
    "--settings", settingsFile,
    "--setting-sources", "project",
    "--strict-mcp-config",
    ...(spec.resume ? ["--resume", spec.resume] : spec.sessionId ? ["--session-id", spec.sessionId] : []),
    ...(spec.systemPromptFile ? ["--append-system-prompt-file", spec.systemPromptFile] : []),
  ];
  const startMs = Date.now();
  const useShell = /\.(cmd|bat)$/i.test(bin);
  const proc = spawn(bin, args, {
    cwd: NEXIS_ROOT, // so CLAUDE.md, .claude/skills and the skills' relative paths resolve
    env: engineEnv(spec.runDir),
    shell: useShell,
    windowsHide: true,
    stdio: ["pipe", "pipe", "pipe"],
  });
  const log = fs.createWriteStream(path.join(spec.runDir, "stream.jsonl"), { flags: "a" });

  let buf = "";
  let errOut = "";
  let timedOut = false;
  let killed = false;
  let authRefused = false;
  let sessionId: string | null = spec.resume ?? spec.sessionId ?? null;
  let apiKeySource: string | null = null;
  let resultText = "";
  let cost = 0;
  let numTurns: number | null = null;
  let usage: unknown = null;
  let resultError = false;
  let sawResult = false;
  let rateLimit: RateLimitInfo | null = null;

  const handleLine = (line: string) => {
    log.write(line + "\n");
    let ev: any;
    try {
      ev = JSON.parse(line);
    } catch {
      return; // non-JSON verbose noise
    }
    if (ev.type === "system" && ev.subtype === "init") {
      if (ev.session_id) sessionId = String(ev.session_id);
      apiKeySource = ev.apiKeySource == null ? null : String(ev.apiKeySource);
      onEvent({ kind: "init", sessionId: sessionId ?? "", apiKeySource, model: ev.model ?? null });
      // Subscription OAuth only. Anything else means a key leaked in and the run would bill the API.
      if (!isSubscriptionAuth(apiKeySource) && process.env.CONTENT_OS_ALLOW_API_KEY !== "1") {
        authRefused = true;
        killTree(proc.pid);
      }
    } else if (ev.type === "rate_limit_event" && ev.rate_limit_info) {
      const r = ev.rate_limit_info;
      rateLimit = {
        status: String(r.status ?? "unknown"),
        resetsAt: typeof r.resetsAt === "number" ? r.resetsAt : null,
        rateLimitType: r.rateLimitType,
        sevenDayUtilization: r.unifiedWindows?.seven_day?.utilization,
        fiveHourUtilization: r.unifiedWindows?.five_hour?.utilization,
      };
      lastRateLimit = rateLimit;
      onEvent({ kind: "rate_limit", info: rateLimit });
    } else if (ev.type === "assistant") {
      const blocks = ev.message?.content;
      if (Array.isArray(blocks)) {
        for (const b of blocks) {
          if (b?.type === "tool_use") {
            onEvent({ kind: "tool", name: String(b.name ?? "tool"), detail: JSON.stringify(b.input ?? {}).slice(0, 240) });
          } else if (b?.type === "text" && b.text) {
            onEvent({ kind: "text", text: String(b.text) });
          }
        }
      }
    } else if (ev.type === "result") {
      sawResult = true;
      cost = Number(ev.total_cost_usd ?? 0);
      resultText = String(ev.result ?? "");
      resultError = !!ev.is_error;
      numTurns = typeof ev.num_turns === "number" ? ev.num_turns : null;
      usage = ev.usage ?? null;
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
  proc.stdin?.on("error", () => {}); // EPIPE on a failed spawn must not crash the server
  proc.stdin?.write(spec.prompt);
  proc.stdin?.end();

  const timer = setTimeout(() => {
    timedOut = true;
    killTree(proc.pid);
  }, spec.timeoutMs);

  const done = new Promise<EngineResult>((resolve) => {
    let finished = false;
    const finish = (exitCode: number | null, spawnError?: Error) => {
      if (finished) return;
      finished = true;
      clearTimeout(timer);
      if (buf.trim()) handleLine(buf.trim());
      log.end();
      const limited = rateLimit && rateLimit.status !== "allowed" && rateLimit.status !== "allowed_warning";
      let status: EngineStatus;
      if (authRefused) status = "auth_refused";
      else if (resultError && AUTH_FAILED_RE.test(resultText)) status = "auth_failed";
      else if (killed) status = "killed";
      else if (timedOut) status = "timeout";
      else if (limited && (resultError || !sawResult)) status = "rate_limited";
      else if (spawnError || resultError || !sawResult || exitCode !== 0) status = "error";
      else status = "ok";
      const error =
        status === "ok"
          ? null
          : status === "auth_refused"
            ? `refused: claude reported apiKeySource=${apiKeySource}, which would bill the API instead of the subscription`
            : status === "auth_failed"
              ? `${AUTH_HELP} (${resultText.slice(0, 120)})`
              : spawnError?.message || (resultError ? resultText.slice(0, 500) : "") || errOut.slice(0, 500) || status;
      resolve({
        status,
        sessionId,
        apiKeySource,
        costUsd: cost,
        numTurns,
        usage,
        resultText,
        error,
        rateLimit,
        durationMs: Date.now() - startMs,
      });
    };
    proc.on("error", (e) => finish(null, e));
    proc.on("close", (code) => finish(code));
  });

  return {
    pid: proc.pid,
    done,
    kill: () => {
      killed = true;
      killTree(proc.pid);
    },
  };
}
