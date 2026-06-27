import { db } from "@/lib/db";
import { youtubeBriefs } from "@/lib/db/schema";
import { desc } from "drizzle-orm";
import { NextResponse } from "next/server";

export async function GET() {
  const all = db
    .select({ date: youtubeBriefs.date, createdAt: youtubeBriefs.createdAt })
    .from(youtubeBriefs)
    .orderBy(desc(youtubeBriefs.date))
    .all();

  return NextResponse.json(all);
}
