import { db } from "@/lib/db";
import {
  briefs,
  categories,
  articles,
  trends,
  contentIdeas,
} from "@/lib/db/schema";
import { eq, asc } from "drizzle-orm";
import { NextResponse } from "next/server";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ date: string }> }
) {
  const { date } = await params;

  const brief = db
    .select()
    .from(briefs)
    .where(eq(briefs.date, date))
    .get();

  if (!brief) {
    return NextResponse.json(
      { error: "No brief found for this date" },
      { status: 404 }
    );
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
      categorySlugs: JSON.parse(t.categorySlugs),
    }));

  const briefContentIdeas = db
    .select()
    .from(contentIdeas)
    .where(eq(contentIdeas.briefId, brief.id))
    .orderBy(asc(contentIdeas.sortOrder))
    .all()
    .map((idea) => ({
      ...idea,
      keyPoints: JSON.parse(idea.keyPoints),
      relatedTrendSlugs: JSON.parse(idea.relatedTrendSlugs),
    }));

  return NextResponse.json({
    date: brief.date,
    createdAt: brief.createdAt,
    overallSentiment: brief.overallSentiment
      ? JSON.parse(brief.overallSentiment)
      : null,
    topTakeaway: brief.topTakeaway,
    sourcesUsed: brief.sourcesUsed,
    totalArticlesFetched: brief.totalArticlesFetched,
    categories: catsWithArticles,
    trends: briefTrends,
    contentIdeas: briefContentIdeas,
  });
}
