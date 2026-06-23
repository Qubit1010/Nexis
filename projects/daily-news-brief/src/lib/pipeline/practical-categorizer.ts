import { TOOL_CATEGORIES, type ToolCategory } from "./tool-categories";
import type { PracticalItem } from "./sources/practical-index";

export interface CategorizedPractical {
  category: ToolCategory;
  items: PracticalItem[];
}

// Tracked-tool updates (Claude Code, Codex, MCP...) with no explicit domain
// default here — they are primarily ops/scaling tooling.
const DEFAULT_DOMAIN = "managing-scaling";
const MAX_ITEMS_PER_DOMAIN = 12;

function keywordScore(item: PracticalItem, cat: ToolCategory): number {
  const text = `${item.title} ${item.description} ${item.tool ?? ""}`.toLowerCase();
  let score = 0;
  for (const kw of cat.keywords) {
    if (text.includes(kw)) score++;
  }
  return score;
}

function bestDomain(item: PracticalItem): string {
  let best = DEFAULT_DOMAIN;
  let bestScore = 0;
  for (const cat of TOOL_CATEGORIES) {
    const s = keywordScore(item, cat);
    if (s > bestScore) {
      bestScore = s;
      best = cat.slug;
    }
  }
  return best;
}

/**
 * Bucket evidence into the 4 business domains. Problem items keep the domain
 * that fetched them; tool-update items are keyword-routed. Each domain is capped
 * and ordered by corroboration + engagement so Haiku sees the strongest signal.
 */
export function categorizePractical(items: PracticalItem[]): CategorizedPractical[] {
  const bySlug = new Map<string, PracticalItem[]>();
  for (const cat of TOOL_CATEGORIES) bySlug.set(cat.slug, []);

  for (const item of items) {
    const slug = item.domain ?? bestDomain(item);
    (bySlug.get(slug) ?? bySlug.get(DEFAULT_DOMAIN)!).push(item);
  }

  const rank = (i: PracticalItem) =>
    (i.sourceCount ?? 1) * 100 + (i.engagementScore ?? 0);

  const result: CategorizedPractical[] = [];
  for (const cat of TOOL_CATEGORIES) {
    const items = (bySlug.get(cat.slug) ?? [])
      .slice()
      .sort((a, b) => rank(b) - rank(a))
      .slice(0, MAX_ITEMS_PER_DOMAIN);
    result.push({ category: cat, items });
    console.log(`[PracticalCategorizer] ${cat.name}: ${items.length} items`);
  }
  return result;
}
