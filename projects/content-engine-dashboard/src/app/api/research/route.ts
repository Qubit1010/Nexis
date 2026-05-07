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

    // Research uses Claude's built-in web_search tool — no OpenAI equivalent.
    // If Anthropic is unavailable, return available:false so generation still proceeds without research.
    if (!apiKey) {
      return NextResponse.json({ available: false, error: "ANTHROPIC_API_KEY not set — research skipped" });
    }

    try {
      const stdout = await runScript(
        "research_topic.py",
        ["--topic", topic],
        { ANTHROPIC_API_KEY: apiKey }
      );
      const data: ResearchOutput = JSON.parse(stdout);
      return NextResponse.json(data);
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      // If it looks like a credit/quota failure, degrade gracefully
      const isQuotaError = /credit|quota|billing|overload|529/i.test(msg);
      if (isQuotaError) {
        console.warn("Anthropic quota hit during research — skipping research, generation will still run:", msg);
        return NextResponse.json({ available: false, error: "Anthropic API limit reached — research skipped" });
      }
      throw err;
    }
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
