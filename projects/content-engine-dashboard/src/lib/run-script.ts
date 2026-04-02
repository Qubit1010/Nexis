import { execFile } from "child_process";
import path from "path";

// CWD for all Python scripts is the Nexis repo root
// This file lives at: projects/content-engine-dashboard/src/lib/run-script.ts
// process.cwd() = projects/content-engine-dashboard/  (where npm run dev is called)
// Repo root = ../../ relative to CWD
const REPO_ROOT = path.join(process.cwd(), "../..");
const SCRIPTS_DIR = path.join(
  REPO_ROOT,
  ".claude/skills/content-engine/scripts"
);

export function runScript(
  scriptName: string,
  args: string[] = [],
  env?: Record<string, string>
): Promise<string> {
  return new Promise((resolve, reject) => {
    const scriptPath = path.join(SCRIPTS_DIR, scriptName);

    execFile(
      "python",
      [scriptPath, ...args],
      {
        cwd: REPO_ROOT,
        timeout: 120_000, // 2 minutes max
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
