import { DEFAULT_DAILY_TOPICS } from "./themes";
import { fetchFromHackerNews } from "./sources/hackernews";
import { fetchFromRSS } from "./sources/rss";
import { callWithFallback } from "./processor";
import { titleSimilarity, extractJSON } from "./utils";

export type BriefMode = "daily" | "topic";

export interface ResolveTopicsOptions {
  mode: BriefMode;
  /** Required when mode === "topic": the single user-named subject. */
  topic?: string;
  /** Max live-derived breaking topics added on top of the curated set. Default 2. */
  maxDerived?: number;
}

const DEFAULT_MAX_DERIVED = 2;

/** Headline auto-derive is ON by default; set DAILY_BRIEF_DERIVE_TOPICS=0 to disable. */
function deriveEnabled(): boolean {
  const v = (process.env.DAILY_BRIEF_DERIVE_TOPICS ?? "").trim().toLowerCase();
  return v !== "0" && v !== "false" && v !== "off" && v !== "no";
}

/**
 * Resolve the topic set that drives the fetch.
 *
 * - "topic" mode: returns just the user-named topic. No curated list, no
 *   headline derivation. The timeline is passed straight to the engine by the
 *   caller. This is the "specific topic + specific timeline" path.
 * - "daily" mode: always returns the full curated theme set (guarantees coverage
 *   across all 6 categories) and, by default, ADDS up to `maxDerived` live
 *   breaking topics auto-derived from today's free RSS/HN headlines (one cheap
 *   LLM call) — to catch news the fixed list misses. Disable with
 *   DAILY_BRIEF_DERIVE_TOPICS=0; tune the count with DAILY_BRIEF_MAX_DERIVED.
 */
export async function resolveTopics(
  opts: ResolveTopicsOptions
): Promise<string[]> {
  if (opts.mode === "topic") {
    const t = (opts.topic || "").trim();
    if (!t) throw new Error("topic mode requires a non-empty topic");
    return [t];
  }

  const curated = [...DEFAULT_DAILY_TOPICS];
  const maxDerived =
    opts.maxDerived ??
    parseInt(process.env.DAILY_BRIEF_MAX_DERIVED || String(DEFAULT_MAX_DERIVED), 10);

  let derived: string[] = [];
  if (deriveEnabled() && maxDerived > 0) {
    try {
      derived = await deriveTopicsFromHeadlines(maxDerived);
    } catch (err) {
      console.error("[Topics] Headline derivation failed (skipping):", err);
    }
  }

  // Keep ALL curated themes (category coverage); append deduped breaking topics.
  const merged = [...curated];
  let added = 0;
  for (const candidate of derived) {
    const c = candidate.trim();
    if (!c) continue;
    if (merged.some((m) => titleSimilarity(m, c) > 0.7)) continue;
    merged.push(c);
    if (++added >= maxDerived) break;
  }

  console.log(
    `[Topics] daily mode: ${merged.length} topics (${curated.length} curated + ${added} live-derived)`
  );
  return merged;
}

/**
 * Discovery seed only: pull today's free RSS + HN headlines and ask a cheap
 * model to extract the hottest AI topics as short search phrases. The headlines
 * are NOT used as evidence — the research engine does the real fetch per topic.
 */
async function deriveTopicsFromHeadlines(limit: number): Promise<string[]> {
  const [hn, rss] = await Promise.allSettled([
    fetchFromHackerNews(),
    fetchFromRSS(),
  ]);

  const headlines: string[] = [];
  for (const r of [hn, rss]) {
    if (r.status === "fulfilled") {
      for (const a of r.value) headlines.push(a.title);
    }
  }
  if (headlines.length === 0) return [];

  const prompt = `Below are today's AI/tech headlines. Extract the ${limit} hottest, most newsworthy AI topics as SHORT search phrases (2-5 words each, no punctuation). Return ONLY a JSON array of strings.

Headlines:
${headlines.slice(0, 80).map((h) => `- ${h}`).join("\n")}

JSON array:`;

  const raw = await callWithFallback(
    prompt,
    "topic-derivation",
    "gpt-5.4-mini",
    "claude-haiku-4-5-20251001",
    400
  );

  const json = extractJSON(raw) ?? raw;
  try {
    const parsed = JSON.parse(json);
    if (Array.isArray(parsed)) {
      return parsed.filter((x): x is string => typeof x === "string").slice(0, limit);
    }
  } catch {
    /* fail-open: no derived topics */
  }
  return [];
}
