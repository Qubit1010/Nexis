import { db } from "../db";
import {
  toolBriefs,
  toolCategories,
  tools as toolsTable,
  toolTrends,
  toolContentIdeas,
  workflowRecipes,
} from "../db/schema";
import { eq } from "drizzle-orm";
import { fetchPracticalEvidence, type PracticalItem } from "./sources/practical-index";
import { categorizePractical } from "./practical-categorizer";
import {
  analyzeToolCategory,
  synthesizeToolBrief,
  type ToolCategoryPass1Output,
} from "./tool-processor";
import { titleSimilarity } from "./utils";
import type { Depth } from "./sources/last30days";

/** Normalize for tool-name matching: lowercase, unify dashes/arrows, collapse ws. */
function normName(s: string): string {
  return s
    .toLowerCase()
    .replace(/[→–—>]/g, "-") // arrows/en/em-dash/gt -> hyphen
    .replace(/\s+/g, " ")
    .trim();
}

interface ToolBriefResult {
  success: boolean;
  briefId?: number;
  date: string;
  errors: string[];
}

/**
 * Generate the "Practical AI" brief: what's new about the tools SMBs use + how to
 * solve Marketing / Sales / Managing & Scaling / Online Presence problems with
 * them. Evidence comes from the last30days engine + a GitHub/OpenRouter movers
 * signal; analysis is Haiku per domain + Sonnet synthesis.
 */
export async function generateToolsBrief(
  date?: string,
  depth: Depth = "lean"
): Promise<ToolBriefResult> {
  const targetDate = date || new Date().toISOString().split("T")[0];
  const errors: string[] = [];

  console.log(`\n========================================`);
  console.log(`  Generating PRACTICAL AI brief for ${targetDate} (${depth})`);
  console.log(`========================================\n`);

  // --- Step 1: Fetch evidence (engine) + movers (GitHub/OpenRouter) ---
  console.log("[Step 1/6] Fetching practical evidence...");
  const { items, movers } = await fetchPracticalEvidence(depth);
  if (items.length === 0) {
    return {
      success: false,
      date: targetDate,
      errors: ["No practical evidence fetched from any source"],
    };
  }

  // --- Step 2: Categorize into the 4 business domains ---
  console.log("\n[Step 2/6] Categorizing into business domains...");
  const categorized = categorizePractical(items);

  // --- Step 3: Create pending brief ---
  const pendingDate = `${targetDate}_pending`;
  const brief = db
    .insert(toolBriefs)
    .values({
      date: pendingDate,
      totalTools: items.length,
      sourcesUsed: new Set(items.map((t) => t.source)).size,
      moversJson: JSON.stringify(movers),
    })
    .returning()
    .get();

  // --- Step 4: Pass 1 — Per-domain analysis with Haiku ---
  console.log("\n[Step 3/6] Analyzing each domain with Haiku...");
  const pass1Results: ToolCategoryPass1Output[] = [];

  const categoryResults = await Promise.allSettled(
    categorized.map(async ({ category, items: catItems }) => {
      console.log(`  Processing: ${category.name} (${catItems.length} items)...`);
      const analysis = await analyzeToolCategory(
        category.name,
        category.audienceLens,
        catItems
      );
      return { category, items: catItems, analysis };
    })
  );

  for (const result of categoryResults) {
    if (result.status === "rejected") {
      const errorMsg =
        result.reason instanceof Error ? result.reason.message : String(result.reason);
      errors.push(errorMsg);
      console.error(`  [ERROR]`, errorMsg);
      continue;
    }

    const { category, items: catItems, analysis } = result.value;

    const categoryRow = db
      .insert(toolCategories)
      .values({
        briefId: brief.id,
        name: category.name,
        slug: category.slug,
        summary: analysis.summary,
        sortOrder: category.sortOrder,
      })
      .returning()
      .get();

    // Best-in-domain to position 0, then by relevance
    const sortedTools = [...analysis.tools].sort((a, b) => {
      const aBest = analysis.bestInDomain?.name?.toLowerCase() === a.name.toLowerCase();
      const bBest = analysis.bestInDomain?.name?.toLowerCase() === b.name.toLowerCase();
      if (aBest && !bBest) return -1;
      if (bBest && !aBest) return 1;
      return b.relevanceScore - a.relevanceScore;
    });

    for (let i = 0; i < sortedTools.length; i++) {
      const t = sortedTools[i];
      const isBest = analysis.bestInDomain?.name?.toLowerCase() === t.name.toLowerCase();
      let raw: PracticalItem | undefined;
      if (t.originalIndex >= 0 && t.originalIndex < catItems.length) {
        raw = catItems[t.originalIndex];
      }

      db.insert(toolsTable)
        .values({
          categoryId: categoryRow.id,
          name: t.name,
          url: raw?.url || "#",
          source: raw?.source || "Unknown",
          sourceOrigin: "last30days",
          oneLiner: t.oneLiner,
          bestUseCase: t.bestUseCase,
          howToSteps: JSON.stringify(t.howToSteps),
          audienceHook: t.audienceHook,
          pricingTier: t.pricingTier,
          tags: JSON.stringify(t.tags),
          upvotes: raw?.engagementScore || 0,
          relevanceScore: t.relevanceScore,
          isBestInDomain: isBest ? 1 : 0,
          bestInDomainReason: isBest ? analysis.bestInDomain?.reason || null : null,
          sortOrder: i,
        })
        .run();
    }

    pass1Results.push({
      categoryName: category.name,
      categorySlug: category.slug,
      summary: analysis.summary,
      bestInDomain: analysis.bestInDomain,
      toolCount: catItems.length,
      tools: analysis.tools.map((t) => {
        const raw =
          t.originalIndex >= 0 && t.originalIndex < catItems.length
            ? catItems[t.originalIndex]
            : undefined;
        return {
          name: t.name,
          oneLiner: t.oneLiner,
          bestUseCase: t.bestUseCase,
          audienceHook: t.audienceHook,
          relevanceScore: t.relevanceScore,
          upvotes: raw?.engagementScore,
        };
      }),
    });
  }

  // --- Step 5: Synthesis with Sonnet (movers woven in) ---
  console.log("\n[Step 4/6] Synthesizing Practical AI brief with Sonnet...");
  if (pass1Results.length > 0) {
    try {
      const synthesis = await synthesizeToolBrief(pass1Results, targetDate, movers);

      db.update(toolBriefs)
        .set({ crossDomainInsight: synthesis.crossDomainInsight })
        .where(eq(toolBriefs.id, brief.id))
        .run();

      console.log("\n[Step 5/6] Storing trends, content ideas, recipe...");
      for (let i = 0; i < synthesis.trends.length; i++) {
        const trend = synthesis.trends[i];
        db.insert(toolTrends)
          .values({
            briefId: brief.id,
            title: trend.title,
            slug: trend.slug,
            summary: trend.summary,
            toolNames: JSON.stringify(trend.toolNames),
            contentPotential: trend.contentPotential,
            sortOrder: i,
          })
          .run();
      }

      for (let i = 0; i < synthesis.contentIdeas.length; i++) {
        const idea = synthesis.contentIdeas[i];
        db.insert(toolContentIdeas)
          .values({
            briefId: brief.id,
            title: idea.title,
            angle: idea.angle,
            format: idea.format,
            hook: idea.hook,
            keyPoints: JSON.stringify(idea.keyPoints),
            relatedToolNames: JSON.stringify(idea.relatedToolNames),
            sortOrder: i,
          })
          .run();
      }

      if (synthesis.workflowRecipe) {
        const r = synthesis.workflowRecipe;
        db.insert(workflowRecipes)
          .values({
            briefId: brief.id,
            title: r.title,
            subtitle: r.subtitle,
            scenario: r.scenario,
            agent: r.agent,
            toolsUsed: JSON.stringify(r.toolsUsed),
            steps: JSON.stringify(r.steps),
            timeSaved: r.timeSaved || null,
            difficulty: r.difficulty || null,
            audienceHook: r.audienceHook,
          })
          .run();
      }

      const allToolRows = db.select().from(toolsTable).all();
      const pickName = normName(synthesis.topPick.name);
      const topPickRow =
        allToolRows.find((r) => normName(r.name) === pickName) ||
        allToolRows.find((r) => titleSimilarity(normName(r.name), pickName) > 0.6);
      if (topPickRow) {
        db.update(toolBriefs)
          .set({ topPickToolId: topPickRow.id })
          .where(eq(toolBriefs.id, brief.id))
          .run();
      }

      console.log(`  Top pick: ${synthesis.topPick.name}`);
      console.log(`  ${synthesis.trends.length} trends, ${synthesis.contentIdeas.length} ideas, ${movers.length} movers`);
    } catch (error) {
      const msg = error instanceof Error ? error.message : String(error);
      errors.push(`Synthesis failed: ${msg}`);
      console.error(`  [ERROR] Synthesis:`, msg);
    }
  }

  // --- Step 6: Finalize — swap pending with real date ---
  const existing = db.select().from(toolBriefs).where(eq(toolBriefs.date, targetDate)).get();
  if (existing) {
    db.delete(toolBriefs).where(eq(toolBriefs.id, existing.id)).run();
  }
  db.update(toolBriefs).set({ date: targetDate }).where(eq(toolBriefs.id, brief.id)).run();

  const successCount = categoryResults.filter((r) => r.status === "fulfilled").length;
  console.log(
    `\n[Done] Practical AI brief generated: ${successCount}/${categorized.length} domains, ${items.length} items`
  );

  return { success: errors.length === 0, briefId: brief.id, date: targetDate, errors };
}
