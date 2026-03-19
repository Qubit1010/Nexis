import { db } from "@/lib/db";
import { briefs } from "@/lib/db/schema";
import { desc } from "drizzle-orm";
import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const SENTIMENT_SCORE: Record<string, number> = {
  bullish: 4,
  cautious: 3,
  mixed: 2,
  bearish: 1,
};

export function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const date = searchParams.get("date");

  const allBriefs = db
    .select({
      date: briefs.date,
      overallSentiment: briefs.overallSentiment,
    })
    .from(briefs)
    .orderBy(desc(briefs.date))
    .limit(14)
    .all();

  // Filter to briefs up to and including the given date, take last 7
  const filtered = date
    ? allBriefs.filter((b) => b.date <= date).slice(0, 7)
    : allBriefs.slice(0, 7);

  const points = filtered
    .reverse()
    .map((b) => {
      const sentiment = b.overallSentiment
        ? (JSON.parse(b.overallSentiment) as { label: string; summary: string })
        : null;
      return {
        date: b.date,
        label: sentiment?.label || "unknown",
        score: SENTIMENT_SCORE[sentiment?.label || ""] || 2,
        summary: sentiment?.summary || "",
      };
    });

  return NextResponse.json(points);
}
