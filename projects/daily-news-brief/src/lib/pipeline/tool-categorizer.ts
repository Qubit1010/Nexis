import type { RawTool } from "./sources/tool-types";
import type { ToolCategory } from "./tool-categories";

export interface CategorizedTools {
  category: ToolCategory;
  tools: RawTool[];
}

function scoreToolForCategory(tool: RawTool, category: ToolCategory): number {
  const text = `${tool.name} ${tool.tagline} ${tool.description}`.toLowerCase();
  let score = 0;
  for (const keyword of category.keywords) {
    if (text.includes(keyword.toLowerCase())) score++;
  }
  return score;
}

export function categorizeTools(
  tools: RawTool[],
  categories: ToolCategory[]
): CategorizedTools[] {
  const buckets = new Map<string, RawTool[]>();
  for (const cat of categories) buckets.set(cat.slug, []);

  let uncategorized = 0;
  for (const tool of tools) {
    let bestCat: ToolCategory | null = null;
    let bestScore = 0;
    for (const cat of categories) {
      const score = scoreToolForCategory(tool, cat);
      if (score > bestScore) {
        bestScore = score;
        bestCat = cat;
      }
    }
    if (bestCat && bestScore > 0) buckets.get(bestCat.slug)!.push(tool);
    else uncategorized++;
  }

  if (uncategorized > 0) {
    console.log(`[ToolCategorizer] ${uncategorized} tools uncategorized`);
  }

  const result: CategorizedTools[] = categories.map((cat) => {
    const catTools = buckets.get(cat.slug) || [];
    catTools.sort((a, b) => {
      const upDiff = (b.upvotes ?? 0) - (a.upvotes ?? 0);
      if (upDiff !== 0) return upDiff;
      return new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime();
    });
    return { category: cat, tools: catTools.slice(0, 10) };
  });

  const total = result.reduce((sum, r) => sum + r.tools.length, 0);
  console.log(`[ToolCategorizer] ${total} tools categorized across ${categories.length} domains`);
  for (const r of result) {
    console.log(`  ${r.category.name}: ${r.tools.length} tools`);
  }
  return result;
}
