import { db } from "@/lib/db";
import { articles, categories, briefs } from "@/lib/db/schema";
import { eq, or, like, desc } from "drizzle-orm";
import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  const q = req.nextUrl.searchParams.get("q")?.trim();
  if (!q || q.length < 2) {
    return NextResponse.json([]);
  }

  const pattern = `%${q}%`;

  const results = db
    .select({
      id: articles.id,
      title: articles.title,
      source: articles.source,
      tldr: articles.tldr,
      sentimentTag: articles.sentimentTag,
      date: briefs.date,
      categoryName: categories.name,
      categorySlug: categories.slug,
    })
    .from(articles)
    .innerJoin(categories, eq(articles.categoryId, categories.id))
    .innerJoin(briefs, eq(categories.briefId, briefs.id))
    .where(or(like(articles.title, pattern), like(articles.tldr, pattern)))
    .orderBy(desc(briefs.date))
    .limit(20)
    .all();

  return NextResponse.json(results);
}
