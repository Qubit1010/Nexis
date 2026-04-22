import { NextRequest, NextResponse } from "next/server";
import { runScript } from "@/lib/run-script";
import type { ResearchOutput } from "@/lib/types";

export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const topic: string = body.topic;

    if (!topic || typeof topic !== "string") {
      return NextResponse.json({ error: "topic is required" }, { status: 400 });
    }

    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) {
      return NextResponse.json(
        { error: "ANTHROPIC_API_KEY is not set in .env.local" },
        { status: 500 }
      );
    }

    const stdout = await runScript(
      "research_topic.py",
      ["--topic", topic],
      { ANTHROPIC_API_KEY: apiKey }
    );

    const data: ResearchOutput = JSON.parse(stdout);
    return NextResponse.json(data);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
