import { spawn } from "node:child_process";

export interface ProcResult {
  code: number | null;
  out: string;
  err: string;
  timedOut: boolean;
}

/**
 * Run a command and capture output. `shell` is required for npm/npx (.cmd shims
 * on Windows); callers pass only static, trusted tokens in that case.
 */
export function run(
  cmd: string,
  args: string[],
  opts: { cwd?: string; timeoutMs?: number; env?: NodeJS.ProcessEnv; shell?: boolean; input?: string } = {},
): Promise<ProcResult> {
  return new Promise((resolve) => {
    // With a shell, pass one pre-joined command line (what Node would do anyway, minus its deprecation warning).
    const quote = (a: string) => (/[\s"&|<>^]/.test(a) ? `"${a.replace(/"/g, '\\"')}"` : a);
    const child = opts.shell
      ? spawn([cmd, ...args].map(quote).join(" "), { cwd: opts.cwd, env: opts.env ?? process.env, shell: true, windowsHide: true })
      : spawn(cmd, args, { cwd: opts.cwd, env: opts.env ?? process.env, windowsHide: true });
    let out = "";
    let err = "";
    let timedOut = false;
    const cap = (s: string) => (s.length > 200_000 ? s.slice(-200_000) : s);
    child.stdout?.on("data", (d) => (out = cap(out + d)));
    child.stderr?.on("data", (d) => (err = cap(err + d)));
    if (opts.input !== undefined) {
      child.stdin?.on("error", () => {});
      child.stdin?.end(opts.input);
    }
    const timer = opts.timeoutMs
      ? setTimeout(() => {
          timedOut = true;
          if (process.platform === "win32" && child.pid) spawn("taskkill", ["/PID", String(child.pid), "/T", "/F"], { windowsHide: true });
          else child.kill("SIGKILL");
        }, opts.timeoutMs)
      : null;
    child.on("error", (e) => {
      if (timer) clearTimeout(timer);
      resolve({ code: -1, out, err: err + e.message, timedOut });
    });
    child.on("close", (code) => {
      if (timer) clearTimeout(timer);
      resolve({ code, out, err, timedOut });
    });
  });
}

export const tail = (s: string, n = 1200) => (s.length > n ? `...${s.slice(-n)}` : s);
