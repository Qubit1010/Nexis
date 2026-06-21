import { db } from "../db";
import { practicalLookups } from "../db/schema";
import { fetchViaLast30Days } from "./sources/last30days";
import { callWithFallback } from "./processor";
import { extractJSON } from "./utils";
import type { RawArticle } from "./sources/types";

export interface LookupResult {
  summary: string;
  whatsNew: Array<{ title: string; detail: string; url: string }>;
  howPeopleSolve: Array<{
    problem: string;
    approach: string;
    tools: string[];
    steps: string[];
  }>;
}

function buildLookupPrompt(tool: string, days: number, articles: RawArticle[]): string {
  const evidence = articles
    .slice(0, 30)
    .map((a, i) => {
      const sig: string[] = [];
      if (a.engagementScore) sig.push(`${a.engagementScore} upvotes`);
      if (a.commentCount) sig.push(`${a.commentCount} comments`);
      if (a.sourceCount && a.sourceCount > 1) sig.push(`${a.sourceCount} sources`);
      return `${i + 1}. "${a.title}" (${a.source}${sig.length ? `, ${sig.join(", ")}` : ""})\n   ${a.description.slice(0, 300)}\n   ${a.url}`;
    })
    .join("\n\n");

  return `You are a hands-on AI operator advising small business owners. Below is everything from the last ${days} days about "${tool}" - updates, releases, and how people are actually using it. Turn it into a practical lookup.

EVIDENCE:
${evidence}

PRODUCE valid JSON with this exact structure:
{
  "summary": "2-3 sentences: what ${tool} is right now and what's notable in this window",
  "whatsNew": [
    { "title": "short update headline", "detail": "1-2 sentences on what changed and why it matters", "url": "source url from the evidence" }
  ],
  "howPeopleSolve": [
    { "problem": "a concrete business problem (marketing, sales, operations, or online presence)", "approach": "how people use ${tool} to solve it", "tools": ["${tool}", "other tools combined"], "steps": ["3-5 concrete copy-pasteable steps, commands, or prompts"] }
  ]
}

RULES:
- whatsNew: 3-6 items, newest/most important first, each with a real URL from the evidence.
- howPeopleSolve: 3-5 items, each tied to a real SMB business outcome with concrete, copy-pasteable steps.
- Be specific and practical - no hype, no generic advice. If the evidence is thin, say so honestly in the summary.
- Never use em dashes; use plain hyphens.
- Return ONLY valid JSON, no markdown fences.`;
}

/**
 * Live tool lookup: fetch fresh evidence for one tool over a window, analyze
 * "what's new + how people solve business problems with it", and persist it.
 * Returns the new row id.
 */
export async function runToolLookup(tool: string, days: number): Promise<number> {
  const cleanTool = tool.trim();
  if (!cleanTool) throw new Error("tool is required");
  const window = Number.isFinite(days) && days > 0 ? Math.min(days, 90) : 7;

  const articles = await fetchViaLast30Days([cleanTool], window, "lean");
  if (articles.length === 0) {
    throw new Error(`No evidence found for "${cleanTool}" in the last ${window} days`);
  }

  const raw = await callWithFallback(
    buildLookupPrompt(cleanTool, window, articles),
    `lookup:${cleanTool}`,
    "gpt-5.2",
    "claude-sonnet-4-6",
    6000
  );
  const parsed = JSON.parse(extractJSON(raw) ?? raw) as LookupResult;

  const sources = articles.slice(0, 20).map((a) => ({
    title: a.title,
    url: a.url,
    source: a.source,
  }));

  const row = db
    .insert(practicalLookups)
    .values({
      tool: cleanTool,
      days: window,
      summary: parsed.summary,
      whatsNew: JSON.stringify(parsed.whatsNew || []),
      howPeopleSolve: JSON.stringify(parsed.howPeopleSolve || []),
      sources: JSON.stringify(sources),
    })
    .returning()
    .get();

  return row.id;
}
