import { NextResponse } from "next/server";
import { runScript } from "@/lib/run-script";
import { cacheSet } from "@/lib/db";
import type { PullIdeasOutput } from "@/lib/types";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const stdout = await runScript("pull_ideas.py");
    const data: PullIdeasOutput = JSON.parse(stdout);

    // Persist to SQLite so the ideate page can restore without re-running the script
    cacheSet("ideas", data);

    return NextResponse.json(data);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
