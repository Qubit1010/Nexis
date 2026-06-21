import { generateDailyBrief, type BriefOptions } from "@/lib/pipeline/run";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  // Auth check — optional, only enforced when BRIEF_AUTH_TOKEN is set
  const expectedToken = process.env.BRIEF_AUTH_TOKEN;
  if (expectedToken) {
    const authHeader = request.headers.get("Authorization");
    if (authHeader !== `Bearer ${expectedToken}`) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }
  }

  try {
    const body = await request.json().catch(() => ({}));
    const date = body.date as string | undefined;

    // Optional on-demand topic mode: { topic, days, depth }
    const opts: BriefOptions = {};
    if (typeof body.topic === "string" && body.topic.trim()) {
      opts.mode = "topic";
      opts.topic = body.topic.trim();
    }
    if (typeof body.days === "number") opts.days = body.days;
    if (body.depth === "full" || body.depth === "lean") opts.depth = body.depth;

    const result = await generateDailyBrief(date, opts);

    return NextResponse.json(result, {
      status: result.success ? 200 : 207, // 207 = partial success
    });
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Unknown error";
    return NextResponse.json(
      { success: false, error: message },
      { status: 500 }
    );
  }
}
