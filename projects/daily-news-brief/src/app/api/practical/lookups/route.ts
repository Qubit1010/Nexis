import { db } from "@/lib/db";
import { practicalLookups } from "@/lib/db/schema";
import { desc } from "drizzle-orm";
import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET() {
  const rows = db
    .select({
      id: practicalLookups.id,
      tool: practicalLookups.tool,
      days: practicalLookups.days,
      createdAt: practicalLookups.createdAt,
    })
    .from(practicalLookups)
    .orderBy(desc(practicalLookups.id))
    .limit(20)
    .all();

  return NextResponse.json(rows);
}
