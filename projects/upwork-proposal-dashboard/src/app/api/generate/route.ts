import { NextRequest, NextResponse } from "next/server";
import Anthropic from "@anthropic-ai/sdk";
import fs from "fs";
import path from "path";

export const dynamic = "force-dynamic";

function loadSkill(): string {
  const skillPath = path.join(process.cwd(), "src", "skill.md");
  return fs.readFileSync(skillPath, "utf-8");
}

export async function POST(req: NextRequest) {
  try {
    const { jobPost } = await req.json() as { jobPost: string };

    if (!jobPost?.trim()) {
      return NextResponse.json({ error: "jobPost is required" }, { status: 400 });
    }

    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) {
      return NextResponse.json({ error: "ANTHROPIC_API_KEY is not set" }, { status: 500 });
    }

    const systemPrompt = loadSkill();
    const anthropic = new Anthropic({ apiKey });

    const message = await anthropic.messages.create({
      model: "claude-sonnet-4-6",
      max_tokens: 1024,
      system: systemPrompt,
      messages: [{ role: "user", content: jobPost }],
    });

    const raw = message.content[0]?.type === "text" ? message.content[0].text : "";

    const jobTypeMatch = raw.match(/Job type detected:\s*(.+)/i);
    const jobType = jobTypeMatch ? jobTypeMatch[1].trim() : "AI Services";
    const proposal = raw
      .split(/Job type detected:/i)[0]
      .replace(/—/g, "-")
      .replace(/[-]{3,}\s*$/gm, "")  // strip trailing --- separators
      .trim();

    return NextResponse.json({ proposal, jobType });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
