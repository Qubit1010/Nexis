import { db } from "@/lib/db";
import { briefs } from "@/lib/db/schema";
import { desc } from "drizzle-orm";
import { NextResponse } from "next/server";

export async function GET() {
  const allBriefs = db
    .select({ date: briefs.date, createdAt: briefs.createdAt })
    .from(briefs)
    .orderBy(desc(briefs.date))
    .all();

  return NextResponse.json(allBriefs);
}
