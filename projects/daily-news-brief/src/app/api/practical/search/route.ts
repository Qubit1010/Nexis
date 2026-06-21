import { runToolLookup } from "@/lib/pipeline/practical-lookup";
import { NextResponse } from "next/server";

// Long-running: the engine fetch + analysis can take ~1-2 minutes.
export const maxDuration = 300;

export async function POST(request: Request) {
  const expectedToken = process.env.BRIEF_AUTH_TOKEN;
  if (expectedToken) {
    const authHeader = request.headers.get("Authorization");
    if (authHeader !== `Bearer ${expectedToken}`) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }
  }

  try {
    const body = await request.json().catch(() => ({}));
    const tool = typeof body.tool === "string" ? body.tool.trim() : "";
    const days = typeof body.days === "number" ? body.days : 7;
    if (!tool) {
      return NextResponse.json({ error: "tool is required" }, { status: 400 });
    }

    const id = await runToolLookup(tool, days);
    return NextResponse.json({ id });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    return NextResponse.json({ success: false, error: message }, { status: 500 });
  }
}
