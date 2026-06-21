import { TOOL_CATEGORIES } from "./tool-categories";

export interface PracticalTopic {
  /** Search phrase handed to the last30days engine. */
  topic: string;
  /** Domain slug this topic feeds, or null for cross-domain tool updates. */
  domain: string | null;
  kind: "tool-update" | "problem";
  /** For tool-update topics: the canonical tool name (for display/grouping). */
  tool?: string;
}

/**
 * Tools people actually use day-to-day. Their UPDATES are the core of Practical
 * AI ("what's new about the tools you already rely on"). Kept tight so the daily
 * run stays fast; expand on --full.
 */
export const TRACKED_TOOLS: string[] = [
  "Claude Code",
  "OpenAI Codex CLI",
  "Gemini CLI",
  "Cursor AI editor",
  "MCP servers Model Context Protocol",
];

/** Extra tracked tools pulled in only on --full / depth="full". */
export const TRACKED_TOOLS_FULL: string[] = [
  "n8n automation",
  "LangGraph agents",
  "Windsurf editor",
  "Claude agent skills",
];

/**
 * Build the practical topic set:
 * - tool-update topics from TRACKED_TOOLS (domain-agnostic; bucketed later)
 * - one business-problem query per domain (more on --full)
 */
export function resolvePracticalTopics(depth: "lean" | "full"): PracticalTopic[] {
  const topics: PracticalTopic[] = [];

  const tools =
    depth === "full" ? [...TRACKED_TOOLS, ...TRACKED_TOOLS_FULL] : TRACKED_TOOLS;
  for (const tool of tools) {
    topics.push({
      topic: `${tool} new features updates and use cases`,
      domain: null,
      kind: "tool-update",
      tool,
    });
  }

  const problemsPerDomain = depth === "full" ? 2 : 1;
  for (const cat of TOOL_CATEGORIES) {
    for (const q of cat.problemQueries.slice(0, problemsPerDomain)) {
      topics.push({ topic: q, domain: cat.slug, kind: "problem" });
    }
  }

  return topics;
}
