import { db } from "../db";
import { briefs, categories, articles, trends, contentIdeas } from "../db/schema";
import { eq, and, gte } from "drizzle-orm";
import { CATEGORIES } from "./categories";
import { fetchAllSources } from "./sources";
import { deduplicateArticles } from "./deduplicator";
import { categorizeArticles } from "./categorizer";
import {
  processCategoryPass1,
  synthesizeBrief,
  type CategoryPass1Output,
} from "./processor";
import { titleSimilarity } from "./utils";
import type { RawArticle } from "./sources/types";

interface BriefResult {
  success: boolean;
  briefId?: number;
  date: string;
  errors: string[];
}

export async function generateDailyBrief(
  date?: string
): Promise<BriefResult> {
  const targetDate = date || new Date().toISOString().split("T")[0];
  const errors: string[] = [];

  console.log(`\n========================================`);
  console.log(`  Generating brief for ${targetDate}`);
  console.log(`========================================\n`);

  // --- Step 1: Fetch from all sources ---
  console.log("[Step 1/6] Fetching from all sources...");
  const rawArticles = await fetchAllSources(CATEGORIES);

  if (rawArticles.length === 0) {
    return {
      success: false,
      date: targetDate,
      errors: ["No articles fetched from any source"],
    };
  }

  // --- Step 2: Deduplicate ---
  console.log("\n[Step 2/6] Deduplicating articles...");
  const deduplicated = deduplicateArticles(rawArticles);

  // --- Step 3: Categorize ---
  console.log("\n[Step 3/6] Categorizing articles...");
  const categorized = categorizeArticles(deduplicated, CATEGORIES);

  // --- Step 4: Create new brief (keep old one until we're done) ---
  const pendingDate = `${targetDate}_pending`;
  const brief = db
    .insert(briefs)
    .values({
      date: pendingDate,
      totalArticlesFetched: rawArticles.length,
      sourcesUsed: new Set(rawArticles.map((a) => a.sourceOrigin)).size,
    })
    .returning()
    .get();

  // --- Step 5: Pass 1 — Per-category analysis with Haiku ---
  console.log("\n[Step 4/6] Analyzing each category with Haiku...");
  const pass1Results: CategoryPass1Output[] = [];

  const categoryResults = await Promise.allSettled(
    categorized.map(async ({ category, articles: catArticles }) => {
      console.log(`  Processing: ${category.name} (${catArticles.length} articles)...`);
      const processed = await processCategoryPass1(
        category.name,
        category.description,
        catArticles
      );
      return { category, rawArticles: catArticles, processed };
    })
  );

  // Store Pass 1 results
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

    const { category, rawArticles: catRawArticles, processed } = result.value;

    // Insert category
    const categoryRow = db
      .insert(categories)
      .values({
        briefId: brief.id,
        name: category.name,
        slug: category.slug,
        insight: processed.insight,
        sortOrder: category.sortOrder,
      })
      .returning()
      .get();

    // Insert articles — match by originalIndex first, then fuzzy title fallback
    for (let i = 0; i < processed.articles.length; i++) {
      const processedArticle = processed.articles[i];

      // Primary: match by originalIndex from prompt
      let rawMatch: RawArticle | undefined;
      if (
        processedArticle.originalIndex !== undefined &&
        processedArticle.originalIndex >= 0 &&
        processedArticle.originalIndex < catRawArticles.length
      ) {
        rawMatch = catRawArticles[processedArticle.originalIndex];
      }

      // Fallback: fuzzy title matching
      if (!rawMatch) {
        rawMatch = catRawArticles.find(
          (r) => titleSimilarity(r.title, processedArticle.title) > 0.7
        );
      }

      db.insert(articles)
        .values({
          categoryId: categoryRow.id,
          title: processedArticle.title,
          url: rawMatch?.url || "#",
          source: rawMatch?.source || "Unknown",
          sourceOrigin: rawMatch?.sourceOrigin || null,
          publishedAt: rawMatch?.publishedAt || null,
          tldr: processedArticle.tldr,
          sentimentTag: processedArticle.sentimentTag,
          relevanceScore: processedArticle.relevanceScore,
          engagementScore: rawMatch?.engagementScore || null,
          commentCount: rawMatch?.commentCount || null,
          sourceCount: rawMatch?.sourceCount || 1,
          sortOrder: i,
        })
        .run();
    }

    // Build Pass 1 output for synthesis
    pass1Results.push({
      categoryName: category.name,
      categorySlug: category.slug,
      insight: processed.insight,
      emergingThemes: processed.emergingThemes,
      articleCount: catRawArticles.length,
      topArticles: processed.articles.map((a) => {
        let raw: RawArticle | undefined;
        if (
          a.originalIndex !== undefined &&
          a.originalIndex >= 0 &&
          a.originalIndex < catRawArticles.length
        ) {
          raw = catRawArticles[a.originalIndex];
        }
        if (!raw) {
          raw = catRawArticles.find(
            (r) => titleSimilarity(r.title, a.title) > 0.7
          );
        }
        return {
          title: a.title,
          tldr: a.tldr,
          sentimentTag: a.sentimentTag,
          relevanceScore: a.relevanceScore,
          engagementScore: raw?.engagementScore,
        };
      }),
    });
  }

  // --- Step 6: Pass 2 — Cross-category synthesis with Sonnet ---
  console.log("\n[Step 5/6] Synthesizing with Sonnet...");

  if (pass1Results.length > 0) {
    try {
      const synthesis = await synthesizeBrief(pass1Results, targetDate);

      // Update brief with synthesis data
      db.update(briefs)
        .set({
          overallSentiment: JSON.stringify(synthesis.overallSentiment),
          topTakeaway: synthesis.topTakeaway,
        })
        .where(eq(briefs.id, brief.id))
        .run();

      // Store trends with multi-day tracking
      console.log("\n[Step 6/6] Storing trends and content ideas...");
      for (let i = 0; i < synthesis.trends.length; i++) {
        const trend = synthesis.trends[i];

        // Check for existing trend within 7-day window
        const sevenDaysAgo = new Date();
        sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
        const sevenDaysAgoStr = sevenDaysAgo.toISOString().split("T")[0];

        const existingTrend = db
          .select()
          .from(trends)
          .where(
            and(
              eq(trends.slug, trend.slug),
              gte(trends.lastSeenDate, sevenDaysAgoStr)
            )
          )
          .get();

        db.insert(trends)
          .values({
            briefId: brief.id,
            title: trend.title,
            slug: trend.slug,
            summary: trend.summary,
            momentumSignal: trend.momentumSignal,
            contentPotentialScore: trend.contentPotentialScore,
            sourceCount: trend.sourceCount,
            categorySlugs: JSON.stringify(trend.categories),
            firstSeenDate: existingTrend?.firstSeenDate || targetDate,
            lastSeenDate: targetDate,
            sortOrder: i,
          })
          .run();
      }

      // Store content ideas
      for (let i = 0; i < synthesis.contentIdeas.length; i++) {
        const idea = synthesis.contentIdeas[i];
        db.insert(contentIdeas)
          .values({
            briefId: brief.id,
            title: idea.title,
            angle: idea.angle,
            format: idea.format,
            hook: idea.hook,
            keyPoints: JSON.stringify(idea.keyPoints),
            timeliness: idea.timeliness,
            relatedTrendSlugs: JSON.stringify(idea.relatedTrends),
            sortOrder: i,
          })
          .run();
      }

      console.log(`  ${synthesis.trends.length} trends stored`);
      console.log(`  ${synthesis.contentIdeas.length} content ideas stored`);
      console.log(`  Sentiment: ${synthesis.overallSentiment.label}`);
    } catch (error) {
      const msg =
        error instanceof Error ? error.message : String(error);
      errors.push(`Synthesis failed: ${msg}`);
      console.error(`  [ERROR] Synthesis:`, msg);
    }
  }

  // --- Finalize: Atomically swap old brief with new one ---
  const existing = db
    .select()
    .from(briefs)
    .where(eq(briefs.date, targetDate))
    .get();

  if (existing) {
    db.delete(briefs).where(eq(briefs.id, existing.id)).run();
  }

  db.update(briefs)
    .set({ date: targetDate })
    .where(eq(briefs.id, brief.id))
    .run();

  const successCount = categoryResults.filter(
    (r) => r.status === "fulfilled"
  ).length;
  console.log(
    `\n[Done] Brief generated: ${successCount}/${CATEGORIES.length} categories, ${rawArticles.length} articles fetched`
  );

  return {
    success: errors.length === 0,
    briefId: brief.id,
    date: targetDate,
    errors,
  };
}
