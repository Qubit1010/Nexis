import { spawn } from "child_process";
import { readFileSync } from "fs";
import { join, resolve } from "path";
import { parse as parseDotenv } from "dotenv";
import type { RawArticle } from "./types";

export type Depth = "lean" | "full";

const PER_QUERY_TIMEOUT_MS = 120_000;
const CONCURRENCY = 3;
const RESULTS_PER_TOPIC = 10;

// --- Path / env resolution (override via env, sensible defaults) ---

function projectRoot(): string {
  return process.env.RESEARCH_BRIEF_ROOT || process.cwd();
}

function repoRoot(): string {
  return resolve(projectRoot(), "..", "..");
}

function engineDir(): string {
  return (
    process.env.RESEARCH_DIR ||
    resolve(repoRoot(), ".claude", "skills", "research", "scripts")
  );
}

function pythonExe(): string {
  // The research skill's deps (exa-py) live under Python312, not the 3.14
  // install the old last30days engine used.
  return (
    process.env.RESEARCH_PYTHON ||
    "C:/Users/qubit/AppData/Local/Programs/Python/Python312/python.exe"
  );
}

function childEnv(): NodeJS.ProcessEnv {
  // Pull API keys from the repo-root .env (single source of truth) and merge
  // under process.env (process.env wins for overlaps). research.py's own
  // _env.py also loads the repo .env; this is belt-and-braces for overrides.
  const repoEnvPath = process.env.RESEARCH_ENV || resolve(repoRoot(), ".env");
  let parsed: Record<string, string> = {};
  try {
    parsed = parseDotenv(readFileSync(repoEnvPath));
  } catch {
    /* repo .env not found — rely on process.env */
  }
  const merged: NodeJS.ProcessEnv = { ...parsed, ...process.env };
  merged.PYTHONIOENCODING = "utf-8";
  return merged;
}

// --- URL quality filter (shared by news, practical, and lookup pipelines) ---

// Repo-activity pages, single comment threads, and known junk: never evidence.
const JUNK_URL_PATTERNS: RegExp[] = [
  /github\.com\/[^/]+\/[^/]+\/(issues|pull|discussions|commit|blob|compare|releases\/tag)/i,
  /news\.ycombinator\.com\/item/i,
  /code\.claude\.com/i,
  /reddit\.com\/r\/[^/]+\/comments/i,
  /(^|\.)pinterest\./i,
];

export function isJunkUrl(url: string): boolean {
  return JUNK_URL_PATTERNS.some((re) => re.test(url));
}

// Authoritative, practically useful domains get a small rank nudge (sourced
// from the 2026 research pass — see research/2026-07-18-*.md reports).
const TRUSTED_DOMAINS = new Set([
  "anthropic.com",
  "openai.com",
  "developers.openai.com",
  "docs.github.com",
  "hubspot.com",
  "blog.hubspot.com",
  "zapier.com",
  "buffer.com",
  "hootsuite.com",
  "semrush.com",
  "sproutsocial.com",
  "salesforce.com",
  "sba.gov",
  "impactplus.com",
  "marketinginsidergroup.com",
  "mckinsey.com",
  "hbr.org",
  "forbes.com",
  "techcrunch.com",
  "theverge.com",
  "arstechnica.com",
  "technologyreview.com",
  "reuters.com",
  "bloomberg.com",
  "wsj.com",
]);

function urlHost(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return "";
  }
}

function isTrusted(url: string): boolean {
  const host = urlHost(url);
  return (
    TRUSTED_DOMAINS.has(host) ||
    [...TRUSTED_DOMAINS].some((d) => host.endsWith(`.${d}`))
  );
}

/** Human label for the source column: publisher hostname, not an engine name. */
export function hostLabel(url: string): string {
  const host = urlHost(url);
  if (!host) return "Web";
  if (host.includes("reddit.com")) return "Reddit";
  if (host.includes("youtube.com") || host.includes("youtu.be")) return "YouTube";
  if (host.includes("github.com")) return "GitHub";
  return host;
}

// --- Invocation ---

interface ResearchResult {
  title?: string;
  url?: string;
  snippet?: string;
  source?: string;
  sources?: string[];
  best_score?: number;
  published_date?: string;
}

interface ResearchPayload {
  results?: ResearchResult[];
  answer?: string | null;
}

function runResearchQuery(
  query: string,
  depth: Depth,
  env: NodeJS.ProcessEnv
): Promise<ResearchPayload> {
  const dir = engineDir();
  const args = [
    join(dir, "research.py"),
    "--query",
    query,
    "--depth",
    depth === "full" ? "deep" : "medium",
    // Pin general mode: auto-detect can flip tool/brand names into entity mode.
    "--mode",
    "general",
    "--json",
    // The pipelines run their own synthesis passes; skip research.py's.
    "--no-synth",
    "--num",
    "10",
  ];

  return new Promise((resolvePromise, reject) => {
    const child = spawn(pythonExe(), args, {
      cwd: dir, // research.py uses bare sibling imports; cwd must be its dir
      env,
      timeout: PER_QUERY_TIMEOUT_MS,
      windowsHide: true,
    });

    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (d) => (stdout += d.toString("utf-8")));
    child.stderr.on("data", (d) => (stderr += d.toString("utf-8")));

    child.on("error", reject);

    child.on("close", (code) => {
      if (code !== 0) {
        const tail = stderr.trim().split("\n").slice(-3).join(" | ");
        reject(new Error(`research.py exited ${code} for "${query}": ${tail}`));
        return;
      }
      try {
        resolvePromise(JSON.parse(stdout) as ResearchPayload);
      } catch {
        reject(new Error(`research.py returned non-JSON for "${query}"`));
      }
    });
  });
}

// --- Mapping: fused result -> RawArticle ---

function mapResult(r: ResearchResult, topic: string): RawArticle | null {
  const title = (r.title || "").trim();
  const url = (r.url || "").trim();
  if (!title || !url || isJunkUrl(url)) return null;

  return {
    title,
    url,
    source: hostLabel(url),
    sourceOrigin: "research",
    publishedAt: r.published_date || new Date().toISOString(),
    description: (r.snippet || "").slice(0, 500),
    sourceCount: r.sources?.length || 1,
    topic,
  };
}

function rankScore(r: ResearchResult): number {
  const corroboration = (r.sources?.length || 1) * 10;
  const trust = r.url && isTrusted(r.url) ? 5 : 0;
  return corroboration + trust + (r.best_score || 0);
}

/** Drop results that are DATED and stale; keep undated (engines often omit dates). */
function isFresh(r: ResearchResult, days: number): boolean {
  if (!r.published_date) return true;
  const ts = Date.parse(r.published_date);
  if (Number.isNaN(ts)) return true;
  return Date.now() - ts <= days * 86_400_000;
}

export interface ResearchFetchOptions {
  days: number;
  depth: Depth;
  /** Results kept per topic after ranking (default 10). */
  num?: number;
}

/**
 * Fetch + rank evidence for a set of queries via the research skill
 * (Exa + Tavily + Serper fused, cross-source ranked). Runs queries in
 * parallel (capped) and fails open per-query: one failed query never
 * sinks the run. NOTE: research.py exits 0 even when every engine fails,
 * so the per-topic count logs are the visibility for silent zero-runs.
 */
export async function fetchViaResearch(
  topics: string[],
  opts: ResearchFetchOptions
): Promise<RawArticle[]> {
  const env = childEnv();
  const keep = opts.num ?? RESULTS_PER_TOPIC;

  console.log(
    `[research] Fetching ${topics.length} topics (${opts.depth}, days=${opts.days})`
  );

  const articles: RawArticle[] = [];

  for (let i = 0; i < topics.length; i += CONCURRENCY) {
    const batch = topics.slice(i, i + CONCURRENCY);
    const results = await Promise.allSettled(
      batch.map((t) => runResearchQuery(t, opts.depth, env))
    );

    results.forEach((res, idx) => {
      const topic = batch[idx];
      if (res.status === "rejected") {
        console.error(`[research] Topic "${topic}" failed:`, res.reason?.message || res.reason);
        return;
      }
      const ranked = (res.value.results || [])
        .filter((r) => isFresh(r, opts.days))
        .sort((a, b) => rankScore(b) - rankScore(a))
        .slice(0, keep);

      let mapped = 0;
      for (const r of ranked) {
        const ra = mapResult(r, topic);
        if (ra) {
          articles.push(ra);
          mapped++;
        }
      }
      console.log(`[research] "${topic}" -> ${mapped} articles`);
    });
  }

  console.log(`[research] Total: ${articles.length} articles from ${topics.length} topics`);
  return articles;
}
