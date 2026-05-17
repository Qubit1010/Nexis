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
import { TOOL_CATEGORIES } from "./tool-categories";
import { fetchAllToolSources } from "./sources/tool-index";
import { deduplicateTools } from "./tool-deduplicator";
import { categorizeTools } from "./tool-categorizer";
import {
  analyzeToolCategory,
  synthesizeToolBrief,
  type ToolCategoryPass1Output,
} from "./tool-processor";
import type { RawTool } from "./sources/tool-types";

interface ToolBriefResult {
  success: boolean;
  briefId?: number;
  date: string;
  errors: string[];
}

export async function generateToolsBrief(
  date?: string
): Promise<ToolBriefResult> {
  const targetDate = date || new Date().toISOString().split("T")[0];
  const errors: string[] = [];

  console.log(`\n========================================`);
  console.log(`  Generating TOOLS brief for ${targetDate}`);
  console.log(`========================================\n`);

  // --- Step 1: Fetch from all tool sources ---
  console.log("[Step 1/6] Fetching from all tool sources...");
  const rawTools = await fetchAllToolSources();
  if (rawTools.length === 0) {
    return {
      success: false,
      date: targetDate,
      errors: ["No tools fetched from any source"],
    };
  }

  // --- Step 2: Deduplicate ---
  console.log("\n[Step 2/6] Deduplicating tools...");
  const deduplicated = deduplicateTools(rawTools);

  // --- Step 3: Categorize ---
  console.log("\n[Step 3/6] Categorizing tools into 4 business domains...");
  const categorized = categorizeTools(deduplicated, TOOL_CATEGORIES);

  // --- Step 4: Create pending brief ---
  const pendingDate = `${targetDate}_pending`;
  const brief = db
    .insert(toolBriefs)
    .values({
      date: pendingDate,
      totalTools: rawTools.length,
      sourcesUsed: new Set(rawTools.map((t) => t.sourceOrigin)).size,
    })
    .returning()
    .get();

  // --- Step 5: Pass 1 — Per-category analysis with Haiku ---
  console.log("\n[Step 4/6] Analyzing each domain with Haiku...");
  const pass1Results: ToolCategoryPass1Output[] = [];

  const categoryResults = await Promise.allSettled(
    categorized.map(async ({ category, tools: catTools }) => {
      console.log(`  Processing: ${category.name} (${catTools.length} tools)...`);
      const analysis = await analyzeToolCategory(
        category.name,
        category.audienceLens,
        catTools
      );
      return { category, rawTools: catTools, analysis };
    })
  );

  for (const result of categoryResults) {
    if (result.status === "rejected") {
      const errorMsg =
        result.reason instanceof Error
          ? result.reason.message
          : String(result.reason);
      errors.push(errorMsg);
      console.error(`  [ERROR]`, errorMsg);
      continue;
    }

    const { category, rawTools: catRawTools, analysis } = result.value;

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

    // Sort best-in-domain tool to position 0
    const sortedTools = [...analysis.tools].sort((a, b) => {
      const aBest = analysis.bestInDomain?.name?.toLowerCase() === a.name.toLowerCase();
      const bBest = analysis.bestInDomain?.name?.toLowerCase() === b.name.toLowerCase();
      if (aBest && !bBest) return -1;
      if (bBest && !aBest) return 1;
      return b.relevanceScore - a.relevanceScore;
    });

    for (let i = 0; i < sortedTools.length; i++) {
      const t = sortedTools[i];
      const isBest =
        analysis.bestInDomain?.name?.toLowerCase() === t.name.toLowerCase();
      let raw: RawTool | undefined;
      if (
        t.originalIndex !== undefined &&
        t.originalIndex >= 0 &&
        t.originalIndex < catRawTools.length
      ) {
        raw = catRawTools[t.originalIndex];
      }
      if (!raw) {
        raw = catRawTools.find(
          (r) => r.name.toLowerCase() === t.name.toLowerCase()
        );
      }

      db.insert(toolsTable)
        .values({
          categoryId: categoryRow.id,
          name: t.name,
          url: raw?.url || "#",
          source: raw?.source || "Unknown",
          sourceOrigin: raw?.sourceOrigin || null,
          oneLiner: t.oneLiner,
          bestUseCase: t.bestUseCase,
          howToSteps: JSON.stringify(t.howToSteps),
          audienceHook: t.audienceHook,
          pricingTier: t.pricingTier,
          tags: JSON.stringify(t.tags),
          upvotes: raw?.upvotes || 0,
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
      toolCount: catRawTools.length,
      tools: analysis.tools.map((t) => {
        let raw: RawTool | undefined;
        if (
          t.originalIndex !== undefined &&
          t.originalIndex >= 0 &&
          t.originalIndex < catRawTools.length
        ) {
          raw = catRawTools[t.originalIndex];
        }
        return {
          name: t.name,
          oneLiner: t.oneLiner,
          bestUseCase: t.bestUseCase,
          audienceHook: t.audienceHook,
          relevanceScore: t.relevanceScore,
          upvotes: raw?.upvotes,
        };
      }),
    });
  }

  // --- Step 6: Synthesis with Sonnet ---
  console.log("\n[Step 5/6] Synthesizing tools brief with Sonnet...");
  if (pass1Results.length > 0) {
    try {
      const synthesis = await synthesizeToolBrief(pass1Results, targetDate);

      db.update(toolBriefs)
        .set({ crossDomainInsight: synthesis.crossDomainInsight })
        .where(eq(toolBriefs.id, brief.id))
        .run();

      console.log("\n[Step 6/6] Storing trends and content ideas...");
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

      // Workflow recipe of the day
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

      // Top pick: try to link to a real tool row by name
      const topPickRow = db
        .select()
        .from(toolsTable)
        .all()
        .find((r) => r.name.toLowerCase() === synthesis.topPick.name.toLowerCase());

      if (topPickRow) {
        db.update(toolBriefs)
          .set({ topPickToolId: topPickRow.id })
          .where(eq(toolBriefs.id, brief.id))
          .run();
      }

      console.log(`  Top pick: ${synthesis.topPick.name}`);
      console.log(`  ${synthesis.trends.length} trends stored`);
      console.log(`  ${synthesis.contentIdeas.length} content ideas stored`);
    } catch (error) {
      const msg = error instanceof Error ? error.message : String(error);
      errors.push(`Synthesis failed: ${msg}`);
      console.error(`  [ERROR] Synthesis:`, msg);
    }
  }

  // --- Finalize: swap pending with real date ---
  const existing = db
    .select()
    .from(toolBriefs)
    .where(eq(toolBriefs.date, targetDate))
    .get();
  if (existing) {
    db.delete(toolBriefs).where(eq(toolBriefs.id, existing.id)).run();
  }
  db.update(toolBriefs)
    .set({ date: targetDate })
    .where(eq(toolBriefs.id, brief.id))
    .run();

  const successCount = categoryResults.filter((r) => r.status === "fulfilled").length;
  console.log(
    `\n[Done] Tools brief generated: ${successCount}/${TOOL_CATEGORIES.length} domains, ${rawTools.length} tools fetched`
  );

  return {
    success: errors.length === 0,
    briefId: brief.id,
    date: targetDate,
    errors,
  };
}
