import { NextResponse } from "next/server";
import { getRubricBundle } from "@/lib/rubric";

export const dynamic = "force-dynamic";

/** The rubric, price book and full source registry, so the UI can cite every number. */
export async function GET() {
  try {
    return NextResponse.json(getRubricBundle());
  } catch (err) {
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed to load rubric" },
      { status: 500 }
    );
  }
}
