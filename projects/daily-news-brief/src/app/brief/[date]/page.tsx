import { db } from "@/lib/db";
import {
  briefs,
  categories,
  articles,
  trends,
  contentIdeas,
} from "@/lib/db/schema";
import { eq, asc, desc } from "drizzle-orm";
import { notFound } from "next/navigation";
import { BriefHeader } from "@/components/brief-header";
import { SentimentPulse } from "@/components/sentiment-pulse";
import { TrendingNow } from "@/components/trending-now";
import { ContentOpportunities } from "@/components/content-opportunities";
import { HotTakes } from "@/components/hot-takes";
import { Keynotes } from "@/components/keynotes";
import { FilterableCoverage } from "@/components/filterable-coverage";
import { CategoryHeatmap } from "@/components/category-heatmap";
import { SourceBreakdown } from "@/components/source-breakdown";
import { SentimentTimeline } from "@/components/sentiment-timeline";
import { KeyboardNav } from "@/components/keyboard-nav";
import { ReadingProgress } from "@/components/reading-progress";
import { CollapsibleSection } from "@/components/collapsible-section";

export const dynamic = "force-dynamic";

interface BriefPageProps {
  params: Promise<{ date: string }>;
}

export default async function BriefPage({ params }: BriefPageProps) {
  const { date } = await params;

  const brief = db
    .select()
    .from(briefs)
    .where(eq(briefs.date, date))
    .get();

  if (!brief) {
    notFound();
  }

  const cats = db
    .select()
    .from(categories)
    .where(eq(categories.briefId, brief.id))
    .orderBy(asc(categories.sortOrder))
    .all();

  const catsWithArticles = cats.map((cat) => {
    const arts = db
      .select()
      .from(articles)
      .where(eq(articles.categoryId, cat.id))
      .orderBy(asc(articles.sortOrder))
      .all();
    return { ...cat, articles: arts };
  });

  const briefTrends = db
    .select()
    .from(trends)
    .where(eq(trends.briefId, brief.id))
    .orderBy(asc(trends.sortOrder))
    .all()
    .map((t) => ({
      ...t,
      categorySlugs: JSON.parse(t.categorySlugs) as string[],
    }));

  const briefContentIdeas = db
    .select()
    .from(contentIdeas)
    .where(eq(contentIdeas.briefId, brief.id))
    .orderBy(asc(contentIdeas.sortOrder))
    .all()
    .map((idea) => ({
      ...idea,
      keyPoints: JSON.parse(idea.keyPoints) as string[],
      relatedTrendSlugs: JSON.parse(idea.relatedTrendSlugs) as string[],
    }));

  // Get top HN articles by engagement
  const allArticles = catsWithArticles.flatMap((c) => c.articles);
  const hotArticles = allArticles
    .filter((a) => a.engagementScore != null && a.engagementScore > 0)
    .sort((a, b) => (b.engagementScore ?? 0) - (a.engagementScore ?? 0))
    .slice(0, 5);

  const totalArticles = catsWithArticles.reduce(
    (sum, c) => sum + c.articles.length,
    0
  );

  const overallSentiment = brief.overallSentiment
    ? (JSON.parse(brief.overallSentiment) as { label: string; summary: string })
    : null;

  const keynotesData = catsWithArticles.map((cat) => ({
    name: cat.name,
    slug: cat.slug,
    insight: cat.insight,
    articleCount: cat.articles.length,
  }));

  // Heatmap data
  const heatmapData = catsWithArticles.map((cat) => {
    const relevanceScores = cat.articles
      .map((a) => a.relevanceScore)
      .filter((s): s is number => s != null);
    const avgRelevance =
      relevanceScores.length > 0
        ? relevanceScores.reduce((s, v) => s + v, 0) / relevanceScores.length
        : 0;
    const sentimentBreakdown: Record<string, number> = {};
    for (const a of cat.articles) {
      const tag = a.sentimentTag || "neutral";
      sentimentBreakdown[tag] = (sentimentBreakdown[tag] || 0) + 1;
    }
    return {
      name: cat.name,
      slug: cat.slug,
      articleCount: cat.articles.length,
      avgRelevance,
      sentimentBreakdown,
    };
  });

  // Source breakdown counts
  const sourceCounts = { newsapi: 0, hackernews: 0, rss: 0 };
  for (const a of allArticles) {
    const origin = a.sourceOrigin as keyof typeof sourceCounts;
    if (origin in sourceCounts) sourceCounts[origin]++;
  }

  return (
    <div className="max-w-4xl mx-auto px-8 py-10">
      <ReadingProgress />
      <BriefHeader
        date={brief.date}
        createdAt={brief.createdAt}
        totalArticles={totalArticles}
        totalCategories={catsWithArticles.length}
        sourcesUsed={brief.sourcesUsed}
        totalArticlesFetched={brief.totalArticlesFetched}
      />

      {/* Sentiment Pulse */}
      <div className="mt-8" id="sentiment">
        <SentimentPulse
          sentiment={overallSentiment}
          topTakeaway={brief.topTakeaway}
        />
      </div>

      {/* Sentiment Timeline */}
      <div className="mt-4">
        <SentimentTimeline date={date} />
      </div>

      {/* Trending Now */}
      <div className="mt-8" id="trending">
        <CollapsibleSection id="trending" label="Trending Now">
          <TrendingNow trends={briefTrends} date={date} />
        </CollapsibleSection>
      </div>

      {/* Content Opportunities */}
      <div className="mt-8" id="content-ideas">
        <CollapsibleSection id="content-ideas" label="Content Opportunities">
          <ContentOpportunities ideas={briefContentIdeas} />
        </CollapsibleSection>
      </div>

      {/* Most Discussed */}
      {hotArticles.length > 0 && (
        <div className="mt-8" id="most-discussed">
          <CollapsibleSection id="most-discussed" label="Most Discussed">
            <HotTakes articles={hotArticles} />
          </CollapsibleSection>
        </div>
      )}

      {/* Category Heatmap */}
      <div className="mt-8">
        <CollapsibleSection id="category-heatmap" label="Category Heatmap">
          <CategoryHeatmap categories={heatmapData} />
        </CollapsibleSection>
      </div>

      {/* Source Breakdown */}
      <div className="mt-8">
        <SourceBreakdown {...sourceCounts} />
      </div>

      {/* Divider */}
      <div className="relative my-10">
        <div className="h-px bg-border" />
        <span className="absolute left-1/2 -translate-x-1/2 -translate-y-1/2 bg-background px-4 text-[11px] font-semibold text-muted-foreground/50 uppercase tracking-[0.15em]">
          Category Keynotes
        </span>
      </div>

      {/* Keynotes section */}
      <CollapsibleSection id="keynotes" label="Category Keynotes">
        <Keynotes categories={keynotesData} date={brief.date} />
      </CollapsibleSection>

      {/* Divider */}
      <div className="relative my-10">
        <div className="h-px bg-border" />
        <span className="absolute left-1/2 -translate-x-1/2 -translate-y-1/2 bg-background px-4 text-[11px] font-semibold text-muted-foreground/50 uppercase tracking-[0.15em]">
          Full Coverage
        </span>
      </div>

      {/* Category sections with filters */}
      <CollapsibleSection id="full-coverage" label="Full Coverage">
        <FilterableCoverage categories={catsWithArticles} date={date} />
      </CollapsibleSection>

      <KeyboardNav />

      {/* Footer */}
      <div className="mt-16 mb-8 text-center">
        <div className="h-px bg-border mb-6" />
        <p className="text-[13px] text-muted-foreground/40">
          Generated by AI Intel Brief &middot; Multi-source AI-powered
          intelligence
        </p>
      </div>
    </div>
  );
}
