import { spawn } from "child_process";
import { readFileSync, writeFileSync, mkdtempSync, rmSync } from "fs";
import { tmpdir } from "os";
import { join, resolve } from "path";
import { parse as parseDotenv } from "dotenv";
import type { RawArticle } from "./types";

export type Depth = "lean" | "full";

/** Canonical last30days source names (see lib/pipeline.py MOCK_AVAILABLE_SOURCES). */
const LEAN_SOURCES = ["reddit", "hackernews", "github", "grounding"];
const FULL_EXTRA_SOURCES = ["x", "youtube", "tiktok", "instagram", "threads", "polymarket"];

/** Keys the engine reads for its paid/optional sources + cheap rerank. */
const ENGINE_KEYS = [
  "OPENAI_API_KEY",
  "PARALLEL_API_KEY",
  "SCRAPECREATORS_API_KEY",
  "XAI_API_KEY",
  "BRAVE_API_KEY",
  "EXA_API_KEY",
  "SERPER_API_KEY",
  "OPENROUTER_API_KEY",
];

const SOURCE_LABELS: Record<string, string> = {
  reddit: "Reddit",
  hackernews: "Hacker News",
  github: "GitHub",
  grounding: "Web",
  x: "X",
  youtube: "YouTube",
  tiktok: "TikTok",
  instagram: "Instagram",
  threads: "Threads",
  polymarket: "Polymarket",
  perplexity: "Perplexity",
};

const PER_TOPIC_TIMEOUT_MS = 240_000;
const CONCURRENCY = 3;

// --- Path / env resolution (override via env, sensible defaults) ---

function projectRoot(): string {
  // cron runs with cwd = <repo>/projects/daily-news-brief; Next.js loads .env so
  // LAST30DAYS_BRIEF_ROOT/LAST30DAYS_DIR can pin absolute paths there if needed.
  return process.env.LAST30DAYS_BRIEF_ROOT || process.cwd();
}

function repoRoot(): string {
  return resolve(projectRoot(), "..", "..");
}

function engineDir(): string {
  return (
    process.env.LAST30DAYS_DIR ||
    resolve(repoRoot(), ".claude", "skills", "last30days", "scripts")
  );
}

function pythonExe(): string {
  return (
    process.env.LAST30DAYS_PYTHON ||
    "C:/Users/qubit/AppData/Local/Python/bin/python3.14.exe"
  );
}

function childEnv(): NodeJS.ProcessEnv {
  // Pull engine keys from the repo-root .env (single source of truth) and merge
  // under process.env (process.env wins for overlaps). Keeps secrets in one place.
  const repoEnvPath = process.env.LAST30DAYS_ENV || resolve(repoRoot(), ".env");
  let parsed: Record<string, string> = {};
  try {
    parsed = parseDotenv(readFileSync(repoEnvPath));
  } catch {
    /* repo .env not found — rely on process.env / OS keychain */
  }
  const merged: NodeJS.ProcessEnv = { ...parsed, ...process.env };
  merged.PYTHONIOENCODING = "utf-8";
  return merged;
}

// --- Plan + invocation ---

function buildPlan(topic: string, sources: string[]): string {
  return JSON.stringify({
    intent: "general",
    freshness_mode: "recent",
    cluster_mode: "topical",
    subqueries: [
      {
        label: "main",
        search_query: topic,
        ranking_query: `${topic} latest news updates`,
        sources,
        weight: 1.0,
      },
    ],
  });
}

interface EngineCandidate {
  title?: string;
  url?: string;
  source?: string;
  sources?: string[];
  snippet?: string;
  engagement?: number | null;
  source_items?: Array<{
    body?: string;
    published_at?: string;
    engagement?: Record<string, number>;
  }>;
}

interface EngineReport {
  ranked_candidates?: EngineCandidate[];
  errors_by_source?: Record<string, string>;
}

function runEngineForTopic(
  topic: string,
  days: number,
  sources: string[],
  env: NodeJS.ProcessEnv
): Promise<EngineReport> {
  const dir = engineDir();
  const tmp = mkdtempSync(join(tmpdir(), "l30-"));
  const planFile = join(tmp, "plan.json");
  writeFileSync(planFile, buildPlan(topic, sources), "utf-8");

  const args = [
    join(dir, "last30days.py"),
    topic,
    "--emit",
    "json",
    "--search",
    sources.join(","),
    "--days",
    String(days),
    "--plan",
    planFile,
  ];

  return new Promise((resolvePromise, reject) => {
    const child = spawn(pythonExe(), args, {
      cwd: dir,
      env,
      timeout: PER_TOPIC_TIMEOUT_MS,
      windowsHide: true,
    });

    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (d) => (stdout += d.toString("utf-8")));
    child.stderr.on("data", (d) => (stderr += d.toString("utf-8")));

    child.on("error", (err) => {
      rmSync(tmp, { recursive: true, force: true });
      reject(err);
    });

    child.on("close", (code) => {
      rmSync(tmp, { recursive: true, force: true });
      if (code !== 0) {
        const tail = stderr.trim().split("\n").slice(-3).join(" | ");
        reject(new Error(`last30days exited ${code} for "${topic}": ${tail}`));
        return;
      }
      try {
        resolvePromise(JSON.parse(stdout) as EngineReport);
      } catch {
        reject(new Error(`last30days returned non-JSON for "${topic}"`));
      }
    });
  });
}

// --- Mapping: Candidate -> RawArticle ---

function bestPublishedAt(c: EngineCandidate): string {
  const dates = (c.source_items || [])
    .map((s) => s.published_at)
    .filter((d): d is string => !!d)
    .sort();
  return dates.length ? dates[dates.length - 1] : new Date().toISOString();
}

function commentCount(c: EngineCandidate): number | undefined {
  let total = 0;
  let found = false;
  for (const s of c.source_items || []) {
    const e = s.engagement || {};
    for (const k of ["comments", "cmt", "replies", "descendants"]) {
      if (typeof e[k] === "number") {
        total += e[k];
        found = true;
      }
    }
  }
  return found ? total : undefined;
}

function mapCandidate(c: EngineCandidate, topic: string): RawArticle | null {
  const title = (c.title || "").trim();
  const url = (c.url || "").trim();
  if (!title || !url) return null;

  const origin = c.source || "web";
  const body = (c.snippet || c.source_items?.[0]?.body || "").trim();

  return {
    title,
    url,
    source: SOURCE_LABELS[origin] || origin,
    sourceOrigin: "last30days",
    publishedAt: bestPublishedAt(c),
    description: body.slice(0, 500),
    engagementScore:
      typeof c.engagement === "number" ? c.engagement : undefined,
    commentCount: commentCount(c),
    sourceCount: c.sources?.length || 1,
    topic,
  };
}

/**
 * Fetch + rank evidence for a set of topics via the last30days engine.
 * Runs topics in parallel (capped) and fails open per-topic: one failed topic
 * or source never sinks the run.
 */
export async function fetchViaLast30Days(
  topics: string[],
  days: number,
  depth: Depth,
  sourcesOverride?: string[]
): Promise<RawArticle[]> {
  const sources =
    sourcesOverride ??
    (depth === "full" ? [...LEAN_SOURCES, ...FULL_EXTRA_SOURCES] : LEAN_SOURCES);
  const env = childEnv();

  console.log(
    `[last30days] Fetching ${topics.length} topics (${depth}, days=${days}, sources=${sources.join(",")})`
  );

  const articles: RawArticle[] = [];

  for (let i = 0; i < topics.length; i += CONCURRENCY) {
    const batch = topics.slice(i, i + CONCURRENCY);
    const results = await Promise.allSettled(
      batch.map((t) => runEngineForTopic(t, days, sources, env))
    );

    results.forEach((res, idx) => {
      const topic = batch[idx];
      if (res.status === "rejected") {
        console.error(`[last30days] Topic "${topic}" failed:`, res.reason?.message || res.reason);
        return;
      }
      const report = res.value;
      const errs = report.errors_by_source || {};
      if (Object.keys(errs).length) {
        console.warn(`[last30days] "${topic}" source errors:`, errs);
      }
      let mapped = 0;
      for (const cand of report.ranked_candidates || []) {
        const ra = mapCandidate(cand, topic);
        if (ra) {
          articles.push(ra);
          mapped++;
        }
      }
      console.log(`[last30days] "${topic}" -> ${mapped} articles`);
    });
  }

  console.log(`[last30days] Total: ${articles.length} articles from ${topics.length} topics`);
  return articles;
}
