import { db } from "../db";
import { practicalLookups } from "../db/schema";
import { fetchViaResearch } from "./sources/research";
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

// ---------------------------------------------------------------------------
// Prompt
// ---------------------------------------------------------------------------

function evidenceBlock(articles: RawArticle[]): string {
  return articles
    .slice(0, 40)
    .map((a, i) => {
      const sig =
        a.sourceCount && a.sourceCount > 1
          ? ` (corroborated by ${a.sourceCount} search engines)`
          : "";
      const desc = a.description ? `\n   ${a.description.slice(0, 350)}` : "";
      return `${i + 1}. [${a.source}] "${a.title}"${sig}${desc}\n   ${a.url}`;
    })
    .join("\n\n");
}

const JSON_SHAPE = `{
  "summary": "2-3 sentences: what TOOL is right now and what's notable in this window",
  "whatsNew": [
    { "title": "short update headline", "detail": "1-2 sentences on what changed and why it matters", "url": "source url from the evidence" }
  ],
  "howPeopleSolve": [
    { "problem": "a concrete business problem (marketing, sales, operations, or online presence)", "approach": "how people use TOOL to solve it", "tools": ["TOOL", "other tools combined"], "steps": ["3-5 concrete copy-pasteable steps, commands, or prompts"] }
  ]
}`;

const RULES = `RULES:
- whatsNew: 3-6 items, newest/most important first, each with a real URL from the evidence/sources.
- howPeopleSolve: 3-5 items, each tied to a real SMB business outcome with concrete, copy-pasteable steps.
- Be specific and practical - no hype, no generic advice. If the evidence is thin, say so honestly in the summary.
- Never use em dashes; use plain hyphens.
- Return ONLY valid JSON, no markdown fences.`;

function buildLookupPrompt(tool: string, days: number, articles: RawArticle[]): string {
  return `You are a hands-on AI operator advising small business owners. Below is everything from the last ${days} days about "${tool}" across official docs, blog posts, tutorials, and community discussion. Turn it into a practical lookup.

EVIDENCE:
${evidenceBlock(articles)}

PRODUCE valid JSON with this exact structure (replace TOOL with "${tool}"):
${JSON_SHAPE}

Prioritize official docs and hands-on tutorials; items corroborated by multiple search engines are stronger signals.
${RULES}`;
}

// ---------------------------------------------------------------------------
// Main export
// ---------------------------------------------------------------------------

export async function runToolLookup(tool: string, days: number): Promise<number> {
  const cleanTool = tool.trim();
  if (!cleanTool) throw new Error("tool is required");
  const window = Number.isFinite(days) && days > 0 ? Math.min(days, 90) : 7;

  const queries = [
    `${cleanTool} new features updates changelog`,
    `${cleanTool} how to use for business tutorial guide`,
  ];
  const fetched = await fetchViaResearch(queries, { days: window, depth: "lean" });

  // Dedupe across the two queries by URL.
  const seen = new Set<string>();
  const articles: RawArticle[] = [];
  for (const a of fetched) {
    if (seen.has(a.url)) continue;
    seen.add(a.url);
    articles.push(a);
  }

  if (articles.length === 0) {
    throw new Error(`No evidence found for "${cleanTool}" in the last ${window} days`);
  }
  console.log(`[Lookup] "${cleanTool}" -> ${articles.length} evidence items`);

  const prompt = buildLookupPrompt(cleanTool, window, articles);
  const raw = await callWithFallback(
    prompt,
    `lookup:${cleanTool}`,
    "gpt-5.2",
    "claude-sonnet-4-6",
    6000
  );
  const parsed = JSON.parse(extractJSON(raw) ?? raw) as LookupResult;

  const sourceList = articles.slice(0, 20).map((a) => ({
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
      sources: JSON.stringify(sourceList),
      notebookUrl: null,
    })
    .returning()
    .get();

  return row.id;
}
