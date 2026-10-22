import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url)); // server/
export const PROJECT_ROOT = path.resolve(HERE, "..");
export const NEXIS_ROOT = path.resolve(PROJECT_ROOT, "..", ".."); // projects/<name> -> repo root

export const PORT = Number(process.env.CONTENT_OS_PORT || 4600);
export const HOST = "127.0.0.1";
export const TZ = "Asia/Karachi";

// CONTENT_OS_DATA_DIR: test seam so the suite never touches the real database.
export const DATA_DIR = process.env.CONTENT_OS_DATA_DIR || path.join(PROJECT_ROOT, "data");
export const DB_FILE = path.join(DATA_DIR, "content-os.db");
export const RUNS_DIR = path.join(DATA_DIR, "runs");
export const LOGS_DIR = path.join(DATA_DIR, "logs");
export const MIGRATIONS_DIR = path.join(HERE, "db", "migrations");
export const DIST_DIR = path.join(PROJECT_ROOT, "dist");
export const GUARD_FILE = path.join(HERE, "engine", "hook-guard.mjs");
export const PROMPTS_DIR = path.join(HERE, "engine", "prompts");

export const CLAUDE_BIN = process.env.CLAUDE_BIN || "claude";
/** Test seam: JSON array of args injected before the standard ones (lets tests run `node fake-claude.mjs`). */
export const CLAUDE_BIN_ARGS: string[] = process.env.CLAUDE_BIN_ARGS ? JSON.parse(process.env.CLAUDE_BIN_ARGS) : [];
export const PYTHON_BIN = process.env.CONTENT_OS_PYTHON || "python";

/** Browser origins allowed to call state-changing routes (localhost UI + the daily brief app). */
export const ALLOWED_ORIGINS = new Set(
  [
    `http://127.0.0.1:${PORT}`,
    `http://localhost:${PORT}`,
    "http://127.0.0.1:5174",
    "http://localhost:5174",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    ...(process.env.CONTENT_OS_EXTRA_ORIGINS || "").split(",").map((s) => s.trim()),
  ].filter(Boolean),
);

/**
 * The root .env is parsed into an object and NEVER merged into process.env:
 * D:\Nexis\.env carries ANTHROPIC_API_KEY, and a spawned `claude -p` that sees it
 * bills the API instead of the subscription. Only jobs that need a key on purpose
 * (the daily brief) get specific values injected.
 */
export function rootEnv(): Record<string, string> {
  const file = process.env.CONTENT_OS_ENV_FILE || path.join(NEXIS_ROOT, ".env");
  const out: Record<string, string> = {};
  let text = "";
  try {
    text = fs.readFileSync(file, "utf8");
  } catch {
    return out;
  }
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trim();
    if (!line || line.startsWith("#")) continue;
    const eq = line.indexOf("=");
    if (eq <= 0) continue;
    const key = line.slice(0, eq).trim().replace(/^export\s+/, "");
    let val = line.slice(eq + 1).trim();
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1);
    } else {
      const hash = val.indexOf(" #");
      if (hash >= 0) val = val.slice(0, hash).trim();
    }
    out[key] = val;
  }
  return out;
}

export function ensureDirs(): void {
  for (const d of [DATA_DIR, RUNS_DIR, LOGS_DIR]) fs.mkdirSync(d, { recursive: true });
}
