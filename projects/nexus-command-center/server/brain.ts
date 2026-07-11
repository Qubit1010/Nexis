import { execFile } from "node:child_process";
import fs from "node:fs/promises";
import path from "node:path";
import { promisify } from "node:util";
import * as cfg from "./config.ts";

const execFileP = promisify(execFile);

export interface BrainFreshness {
  last_ingest: string | null;
  days_since: number | null;
  stale: boolean;
  new_skills: string[];
  new_decisions: number;
}

export interface BrainDrift {
  in_sync: boolean;
  nexis_only: string[];
  vault_only: string[];
  differ: { file: string; newer: string }[];
}

/**
 * Shell sync_vault.py and parse its --json output. The script exits 1 for
 * "stale"/"drift" (still printing valid JSON), and execFile throws on any
 * nonzero exit — so the payload is recovered from the error's stdout.
 */
async function syncJson<T>(args: string[]): Promise<T | null> {
  try {
    const { stdout } = await execFileP(cfg.PYTHON_BIN, [cfg.SYNC_SCRIPT, ...args, "--json"], {
      cwd: cfg.NEXIS_ROOT,
      timeout: 20000,
      windowsHide: true,
    });
    return JSON.parse(stdout.trim()) as T;
  } catch (e) {
    const out = (e as { stdout?: string }).stdout;
    if (out) {
      try {
        return JSON.parse(out.trim()) as T;
      } catch {
        /* not JSON — fall through */
      }
    }
    return null;
  }
}

async function readText(file: string): Promise<string | null> {
  try {
    return await fs.readFile(file, "utf8");
  } catch {
    return null;
  }
}

/** Last N lines of a markdown log matching a line-prefix regex, newest last. */
function tailMatching(text: string | null, re: RegExp, n: number): string[] {
  if (!text) return [];
  return text
    .split(/\r?\n/)
    .filter((l) => re.test(l))
    .slice(-n);
}

/**
 * Brain panel payload — freshness + drift from the brain-sync script (the
 * single source of truth), plus the always-loaded facts and recent activity.
 * Fetched on panel open, not polled: two python spawns per call.
 */
export async function getBrain() {
  const [freshness, drift, facts, wikiLog, decisions] = await Promise.all([
    syncJson<BrainFreshness>(["--ingest-status"]),
    syncJson<BrainDrift>(["--check"]),
    readText(path.join(cfg.VAULT, "CRITICAL_FACTS.md")),
    readText(path.join(cfg.VAULT, "wiki", "log.md")),
    readText(path.join(cfg.NEXIS_ROOT, "decisions", "log.md")),
  ]);
  return {
    freshness,
    drift,
    critical_facts: facts,
    wiki_log: tailMatching(wikiLog, /^- \[\d{4}-\d{2}-\d{2}\]/, 6),
    recent_decisions: tailMatching(decisions, /^\[\d{4}-\d{2}-\d{2}\]/, 8),
  };
}
