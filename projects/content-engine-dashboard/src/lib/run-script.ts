import { execFile } from "child_process";
import { existsSync } from "fs";
import path from "path";
import os from "os";

const REPO_ROOT = path.join(process.cwd(), "../..");
const SCRIPTS_DIR = path.join(
  REPO_ROOT,
  ".claude/skills/content-engine/scripts"
);

function resolvePythonBin(): string {
  if (process.env.PYTHON_BIN) return process.env.PYTHON_BIN;
  const home = os.homedir();
  const candidates = [
    path.join(home, "AppData/Local/Programs/Python/Python313/python.exe"),
    path.join(home, "AppData/Local/Programs/Python/Python312/python.exe"),
    path.join(home, "AppData/Local/Programs/Python/Python311/python.exe"),
  ];
  for (const c of candidates) {
    if (existsSync(c)) return c;
  }
  return process.platform === "win32" ? "py" : "python3";
}

const PYTHON_BIN = resolvePythonBin();

export function runScript(
  scriptName: string,
  args: string[] = [],
  env?: Record<string, string>,
  timeoutMs: number = 120_000
): Promise<string> {
  return new Promise((resolve, reject) => {
    const scriptPath = path.join(SCRIPTS_DIR, scriptName);

    execFile(
      PYTHON_BIN,
      [scriptPath, ...args],
      {
        cwd: REPO_ROOT,
        timeout: timeoutMs,
        maxBuffer: 10 * 1024 * 1024, // 10MB stdout buffer
        env: {
          ...process.env,
          ...env,
        },
      },
      (error, stdout, stderr) => {
        if (error) {
          reject(
            new Error(
              `Script ${scriptName} failed (exit ${error.code}): ${stderr || error.message}`
            )
          );
          return;
        }
        resolve(stdout);
      }
    );
  });
}
