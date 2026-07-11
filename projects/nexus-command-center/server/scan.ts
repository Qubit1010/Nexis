import { execFile } from "node:child_process";
import fs from "node:fs/promises";
import { promisify } from "node:util";
import * as cfg from "./config.ts";
import { HttpError } from "./spawn.ts";

const execFileP = promisify(execFile);

// ponytail: module-level bool, not a queue — the scan takes ~1s and the UI
// disables the button while one is in flight.
let scanning = false;

/**
 * Re-run the graph scanner (POST /api/graph/scan). Independent of the claude
 * run mutex: it's a local stdlib script, not a paid headless run.
 */
export async function runScan(): Promise<{ generated_at: string | null; counts: Record<string, number> }> {
  if (scanning) throw new HttpError(409, "SCAN_IN_PROGRESS", "A scan is already running");
  scanning = true;
  try {
    const [bin, ...args] = cfg.SCAN_CMD;
    await execFileP(bin, args, { cwd: cfg.PROJECT_ROOT, timeout: 60000, windowsHide: true });
    const meta = JSON.parse(await fs.readFile(cfg.DATA_FILE, "utf8")).meta ?? {};
    return { generated_at: meta.generated_at ?? null, counts: meta.counts ?? {} };
  } catch (e) {
    if (e instanceof HttpError) throw e;
    throw new HttpError(500, "SCAN_FAILED", (e as Error).message?.slice(0, 300) || "scan failed");
  } finally {
    scanning = false;
  }
}
