import { db } from "@/lib/db";
import { toolBriefs } from "@/lib/db/schema";
import { desc } from "drizzle-orm";
import { NextResponse } from "next/server";

export async function GET() {
  const all = db
    .select({ date: toolBriefs.date, createdAt: toolBriefs.createdAt })
    .from(toolBriefs)
    .orderBy(desc(toolBriefs.date))
    .all();

  return NextResponse.json(all);
}
