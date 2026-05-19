import { db } from "@/lib/db";
import {
  toolBriefs,
  toolCategories,
  tools as toolsTable,
  toolTrends,
  toolContentIdeas,
  workflowRecipes,
} from "@/lib/db/schema";
import { eq, asc } from "drizzle-orm";
import { notFound } from "next/navigation";
import { ToolsBriefHeader } from "@/components/tools-brief-header";
import { ToolsCategorySection } from "@/components/tools-category-section";
import { ToolTrends } from "@/components/tool-trends";
import { ToolContentIdeas } from "@/components/tool-content-ideas";
import { CollapsibleSection } from "@/components/collapsible-section";
import { ReadingProgress } from "@/components/reading-progress";
import { BestInDomainGrid, type DomainWinner } from "@/components/best-in-domain-grid";
import { WorkflowRecipe } from "@/components/workflow-recipe";

export const dynamic = "force-dynamic";

interface ToolsPageProps {
  params: Promise<{ date: string }>;
}

export default async function ToolsPage({ params }: ToolsPageProps) {
  const { date } = await params;

  const brief = db.select().from(toolBriefs).where(eq(toolBriefs.date, date)).get();
  if (!brief) notFound();

  const cats = db
    .select()
    .from(toolCategories)
    .where(eq(toolCategories.briefId, brief.id))
    .orderBy(asc(toolCategories.sortOrder))
    .all();

  const catsWithTools = cats.map((cat) => {
    const rows = db
      .select()
      .from(toolsTable)
      .where(eq(toolsTable.categoryId, cat.id))
      .orderBy(asc(toolsTable.sortOrder))
      .all();
    return {
      ...cat,
      tools: rows.map((r) => ({
        ...r,
        howToSteps: JSON.parse(r.howToSteps) as string[],
        tags: JSON.parse(r.tags) as string[],
      })),
    };
  });

  // Best-in-domain winners
  const winners: DomainWinner[] = [];
  for (const cat of catsWithTools) {
    const best = cat.tools.find((t) => t.isBestInDomain === 1);
    if (!best) continue;
    winners.push({
      domainName: cat.name,
      domainSlug: cat.slug,
      toolName: best.name,
      toolUrl: best.url,
      oneLiner: best.oneLiner,
      bestUseCase: best.bestUseCase,
      reason: best.bestInDomainReason || best.bestUseCase,
      pricingTier: best.pricingTier,
    });
  }

  const trends = db
    .select()
    .from(toolTrends)
    .where(eq(toolTrends.briefId, brief.id))
    .orderBy(asc(toolTrends.sortOrder))
    .all()
    .map((t) => ({ ...t, toolNames: JSON.parse(t.toolNames) as string[] }));

  const contentIdeas = db
    .select()
    .from(toolContentIdeas)
    .where(eq(toolContentIdeas.briefId, brief.id))
    .orderBy(asc(toolContentIdeas.sortOrder))
    .all()
    .map((i) => ({
      ...i,
      keyPoints: JSON.parse(i.keyPoints) as string[],
      relatedToolNames: JSON.parse(i.relatedToolNames) as string[],
    }));

  const recipeRow = db
    .select()
    .from(workflowRecipes)
    .where(eq(workflowRecipes.briefId, brief.id))
    .get();

  const recipe = recipeRow
    ? {
        ...recipeRow,
        toolsUsed: JSON.parse(recipeRow.toolsUsed) as string[],
        steps: JSON.parse(recipeRow.steps) as Array<{
          step: string;
          commandOrPrompt: string;
          expectedOutcome: string;
        }>,
      }
    : null;

  const totalTools = catsWithTools.reduce((sum, c) => sum + c.tools.length, 0);

  let topPickName: string | null = null;
  let topPickWhy: string | null = null;
  if (brief.topPickToolId) {
    const top = db
      .select()
      .from(toolsTable)
      .where(eq(toolsTable.id, brief.topPickToolId))
      .get();
    if (top) {
      topPickName = top.name;
      topPickWhy = top.bestUseCase;
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-8 py-10">
      <ReadingProgress />
      <ToolsBriefHeader
        date={brief.date}
        createdAt={brief.createdAt}
        totalTools={totalTools}
        totalCategories={catsWithTools.length}
        sourcesUsed={brief.sourcesUsed}
        topPickName={topPickName}
        topPickWhy={topPickWhy}
        crossDomainInsight={brief.crossDomainInsight}
      />

      {/* Best in domain hero grid */}
      {winners.length > 0 && (
        <div className="mt-8" id="best-in-domain">
          <p className="text-[11px] font-semibold text-muted-foreground/60 uppercase tracking-[0.15em] mb-3">
            Best Tools by Domain
          </p>
          <BestInDomainGrid winners={winners} briefDate={brief.date} />
        </div>
      )}

      {/* Workflow recipe of the day */}
      {recipe && (
        <div className="mt-8" id="workflow-recipe">
          <WorkflowRecipe recipe={recipe} briefDate={brief.date} />
        </div>
      )}

      {trends.length > 0 && (
        <div className="mt-8" id="tool-trends">
          <CollapsibleSection id="tool-trends" label="Trends Across Tools">
            <ToolTrends trends={trends} briefDate={brief.date} />
          </CollapsibleSection>
        </div>
      )}

      {contentIdeas.length > 0 && (
        <div className="mt-8" id="tool-content-ideas">
          <CollapsibleSection
            id="tool-content-ideas"
            label="Content Ideas From Today's Tools"
          >
            <ToolContentIdeas ideas={contentIdeas} briefDate={brief.date} />
          </CollapsibleSection>
        </div>
      )}

      {/* Divider */}
      <div className="relative my-10">
        <div className="h-px bg-border" />
        <span className="absolute left-1/2 -translate-x-1/2 -translate-y-1/2 bg-background px-4 text-[11px] font-semibold text-muted-foreground/50 uppercase tracking-[0.15em]">
          All Tools by Domain
        </span>
      </div>

      <div className="space-y-12">
        {catsWithTools.map((cat) => (
          <ToolsCategorySection
            key={cat.id}
            name={cat.name}
            slug={cat.slug}
            summary={cat.summary}
            tools={cat.tools}
            briefDate={brief.date}
          />
        ))}
      </div>

      <div className="mt-16 mb-8 text-center">
        <div className="h-px bg-border mb-6" />
        <p className="text-[13px] text-muted-foreground/40">
          Generated by AI Intel Brief · Tools curated for business operators
        </p>
      </div>
    </div>
  );
}
