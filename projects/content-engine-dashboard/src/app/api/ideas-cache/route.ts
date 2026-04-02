import { NextResponse } from "next/server";
import { cacheGet } from "@/lib/db";
import type { PullIdeasOutput } from "@/lib/types";

export const dynamic = "force-dynamic";

export async function GET() {
  const cached = cacheGet<PullIdeasOutput>("ideas");
  if (!cached) {
    return NextResponse.json({ data: null, savedAt: null });
  }
  return NextResponse.json({ data: cached.value, savedAt: cached.savedAt });
}
