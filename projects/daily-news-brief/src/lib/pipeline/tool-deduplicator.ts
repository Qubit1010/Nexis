import type { RawTool } from "./sources/tool-types";

function normalize(s: string): string {
  return s
    .toLowerCase()
    .replace(/[^\w\s]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function namesMatch(a: string, b: string): boolean {
  const na = normalize(a);
  const nb = normalize(b);
  if (na === nb) return true;
  const shorter = na.length < nb.length ? na : nb;
  const longer = na.length < nb.length ? nb : na;
  if (shorter.length < 4) return false;
  return longer.includes(shorter);
}

// Hosts that are shared across many unrelated tools — never dedupe by URL alone for these
const GENERIC_HOSTS = new Set([
  "github.com", "gitlab.com", "bitbucket.org",
  "huggingface.co", "vercel.app", "netlify.app",
  "replit.com", "streamlit.app", "gradio.app",
  "notion.site", "notion.so", "carrd.co", "framer.website",
  "medium.com", "substack.com", "dev.to",
  "youtube.com", "youtu.be", "twitter.com", "x.com",
]);

function urlHost(u: string): string {
  try {
    return new URL(u).hostname.replace(/^www\./, "");
  } catch {
    return u;
  }
}

function isGenericHost(host: string): boolean {
  return GENERIC_HOSTS.has(host) || host.endsWith(".github.io");
}

// Tools we explicitly do NOT want surfaced. Focus is agentic coding tools
// (Claude Code, Codex, Cursor, MCP servers, autonomous agents) — not legacy
// no-code/iPaaS workflow platforms.
const BLOCKED_TOOL_PATTERNS = [
  /\bn8n\b/i,
  /\bzapier\b/i,
  /\bmake\.com\b/i,
  /\bintegromat\b/i,
  /\bpipedream\b/i,
  /\btray\.io\b/i,
  /\bworkato\b/i,
];

function isBlocked(tool: RawTool): boolean {
  const haystack = `${tool.name} ${tool.tagline || ""} ${tool.description || ""} ${tool.url}`;
  return BLOCKED_TOOL_PATTERNS.some((re) => re.test(haystack));
}

export function deduplicateTools(tools: RawTool[]): RawTool[] {
  const blockedCount = tools.filter(isBlocked).length;
  const filtered = tools.filter((t) => !isBlocked(t));
  if (blockedCount > 0) {
    console.log(`[ToolDedup] Blocked ${blockedCount} non-agentic workflow tools (n8n, Zapier, Make, etc.)`);
  }

  const groups: RawTool[][] = [];

  for (const tool of filtered) {
    let foundGroup = false;
    for (const group of groups) {
      const head = group[0];
      const sameName = namesMatch(tool.name, head.name);
      const hostA = urlHost(tool.url);
      const hostB = urlHost(head.url);
      const sameUrl =
        tool.url &&
        head.url &&
        hostA === hostB &&
        !isGenericHost(hostA);
      if (sameName || sameUrl) {
        group.push(tool);
        foundGroup = true;
        break;
      }
    }
    if (!foundGroup) groups.push([tool]);
  }

  const deduplicated: RawTool[] = groups.map((group) => {
    const best = group.reduce((a, b) =>
      (b.description?.length || 0) > (a.description?.length || 0) ? b : a
    );
    const maxUpvotes = Math.max(...group.map((t) => t.upvotes ?? 0));
    const maxComments = Math.max(...group.map((t) => t.commentCount ?? 0));
    return {
      ...best,
      upvotes: maxUpvotes || undefined,
      commentCount: maxComments || undefined,
    };
  });

  const removed = filtered.length - deduplicated.length;
  if (removed > 0) {
    console.log(`[ToolDedup] Removed ${removed} duplicates (${filtered.length} → ${deduplicated.length})`);
  }
  return deduplicated;
}
