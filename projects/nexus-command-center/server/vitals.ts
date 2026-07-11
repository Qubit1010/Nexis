import { execFile } from "node:child_process";
import fs from "node:fs/promises";
import path from "node:path";
import { promisify } from "node:util";
import * as cfg from "./config.ts";

const execFileP = promisify(execFile);

async function graphMeta(): Promise<{ counts: Record<string, number>; generated_at: string | null }> {
  try {
    const raw = await fs.readFile(cfg.DATA_FILE, "utf8");
    const meta = JSON.parse(raw).meta ?? {};
    return { counts: meta.counts ?? {}, generated_at: meta.generated_at ?? null };
  } catch {
    return { counts: {}, generated_at: null };
  }
}

async function lastSync(): Promise<{ ts: string; line: string } | null> {
  try {
    const raw = await fs.readFile(path.join(cfg.NEXIS_ROOT, "logs", "brain-sync.log"), "utf8");
    const lines = raw.trim().split(/\r?\n/);
    for (let i = lines.length - 1; i >= 0; i--) {
      const m = lines[i].match(/(\d{4}-\d{2}-\d{2}[T ][\d:.]+)/);
      if (m) return { ts: m[1].replace(" ", "T"), line: lines[i].slice(0, 160) };
    }
    return null;
  } catch {
    return null;
  }
}

async function lastVaultCommit(): Promise<{ ts: string; message: string } | null> {
  try {
    const { stdout } = await execFileP("git", ["-C", cfg.VAULT, "log", "-1", "--format=%cI|%s"], {
      timeout: 4000,
    });
    const [ts, ...rest] = stdout.trim().split("|");
    return ts ? { ts, message: rest.join("|") } : null;
  } catch {
    return null;
  }
}

async function commandSpend(): Promise<{ total_usd: number; runs: number }> {
  try {
    const raw = await fs.readFile(cfg.LOG_FILE, "utf8");
    let total = 0;
    let runs = 0;
    for (const line of raw.split(/\r?\n/)) {
      if (!line.trim()) continue;
      try {
        total += Number(JSON.parse(line).cost_usd ?? 0);
        runs++;
      } catch {
        /* skip bad line */
      }
    }
    return { total_usd: Math.round(total * 10000) / 10000, runs };
  } catch {
    return { total_usd: 0, runs: 0 };
  }
}

export async function getVitals() {
  const [meta, sync, vault, spend] = await Promise.all([
    graphMeta(),
    lastSync(),
    lastVaultCommit(),
    commandSpend(),
  ]);
  return {
    counts: meta.counts,
    last_sync: sync,
    last_vault_commit: vault,
    command_spend: spend,
    graph_generated_at: meta.generated_at,
  };
}

// ---- ops depth (Brain panel) ----

interface RunEntry {
  ts: string;
  label: string;
  profile: string;
  cost_usd: number;
  duration_ms: number;
  exit: string;
  result_file: string | null;
}

/**
 * Heavier ops payload from the audit log — spend history, recent runs, and
 * the vault files runs wrote. Separate from /api/vitals so the 15s top-bar
 * poll stays cheap.
 */
export async function getOps() {
  let entries: RunEntry[] = [];
  try {
    const raw = await fs.readFile(cfg.LOG_FILE, "utf8");
    entries = raw
      .split(/\r?\n/)
      .filter((l) => l.trim())
      .flatMap((l) => {
        try {
          const p = JSON.parse(l);
          return [
            {
              ts: String(p.ts ?? ""),
              label: String(p.label ?? ""),
              profile: String(p.profile ?? ""),
              cost_usd: Number(p.cost_usd ?? 0),
              duration_ms: Number(p.duration_ms ?? 0),
              exit: String(p.exit ?? ""),
              result_file: p.result_file ? String(p.result_file) : null,
            },
          ];
        } catch {
          return [];
        }
      });
  } catch {
    /* no log yet — empty ops */
  }

  const byDay = new Map<string, { usd: number; runs: number }>();
  for (const e of entries) {
    const day = e.ts.slice(0, 10);
    if (!day) continue;
    const b = byDay.get(day) ?? { usd: 0, runs: 0 };
    b.usd += e.cost_usd;
    b.runs++;
    byDay.set(day, b);
  }
  return {
    spend_by_day: [...byDay.entries()]
      .sort((a, b) => a[0].localeCompare(b[0]))
      .slice(-14)
      .map(([day, b]) => ({ day, usd: Math.round(b.usd * 10000) / 10000, runs: b.runs })),
    recent_runs: entries.slice(-15).reverse(),
    recent_outputs: entries
      .filter((e) => e.result_file)
      .slice(-10)
      .reverse()
      .map((e) => ({ ts: e.ts, label: e.label, file: e.result_file as string })),
  };
}
