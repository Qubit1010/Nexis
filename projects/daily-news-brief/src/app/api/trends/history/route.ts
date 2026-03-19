import { db } from "@/lib/db";
import { trends, briefs } from "@/lib/db/schema";
import { eq, and, gte } from "drizzle-orm";
import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  const slugs = req.nextUrl.searchParams.get("slugs")?.split(",") || [];
  const date = req.nextUrl.searchParams.get("date") || "";

  if (slugs.length === 0 || !date) {
    return NextResponse.json({});
  }

  // Get briefs from the last 7 days
  const d = new Date(date + "T00:00:00");
  d.setDate(d.getDate() - 7);
  const weekAgo = d.toISOString().split("T")[0];

  const allTrends = db
    .select({
      slug: trends.slug,
      date: briefs.date,
      contentPotentialScore: trends.contentPotentialScore,
      momentumSignal: trends.momentumSignal,
    })
    .from(trends)
    .innerJoin(briefs, eq(trends.briefId, briefs.id))
    .where(gte(briefs.date, weekAgo))
    .all();

  // Group by slug
  const history: Record<
    string,
    { date: string; score: number; momentum: string }[]
  > = {};

  for (const slug of slugs) {
    history[slug] = allTrends
      .filter((t) => t.slug === slug)
      .map((t) => ({
        date: t.date,
        score: t.contentPotentialScore ?? 0,
        momentum: t.momentumSignal,
      }))
      .sort((a, b) => a.date.localeCompare(b.date));
  }

  return NextResponse.json(history);
}
