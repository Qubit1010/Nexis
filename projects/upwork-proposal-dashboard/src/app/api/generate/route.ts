import { NextRequest, NextResponse } from "next/server";
import Anthropic from "@anthropic-ai/sdk";
import OpenAI from "openai";
import fs from "fs";
import path from "path";

export const dynamic = "force-dynamic";

function loadSkill(): string {
  const skillPath = path.join(process.cwd(), "src", "skill.md");
  return fs.readFileSync(skillPath, "utf-8");
}

function parseResponse(raw: string): { proposal: string; jobType: string } {
  const jobTypeMatch = raw.match(/Job type detected:\s*(.+)/i);
  const jobType = jobTypeMatch ? jobTypeMatch[1].trim() : "AI Services";
  const proposal = raw
    .split(/Job type detected:/i)[0]
    .replace(/—/g, "-")
    .replace(/[-]{3,}\s*$/gm, "")
    .trim();
  return { proposal, jobType };
}

async function generateWithAnthropic(systemPrompt: string, jobPost: string): Promise<string> {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) throw new Error("ANTHROPIC_API_KEY is not set");

  const anthropic = new Anthropic({ apiKey });
  const message = await anthropic.messages.create({
    model: "claude-sonnet-4-6",
    max_tokens: 1024,
    system: systemPrompt,
    messages: [{ role: "user", content: jobPost }],
  });

  return message.content[0]?.type === "text" ? message.content[0].text : "";
}

async function generateWithOpenAI(systemPrompt: string, jobPost: string): Promise<string> {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) throw new Error("OPENAI_API_KEY is not set");

  const openai = new OpenAI({ apiKey });
  const completion = await openai.chat.completions.create({
    model: "gpt-4o",
    max_tokens: 1024,
    messages: [
      { role: "system", content: systemPrompt },
      { role: "user", content: jobPost },
    ],
  });

  return completion.choices[0]?.message?.content ?? "";
}

export async function POST(req: NextRequest) {
  try {
    const { jobPost } = await req.json() as { jobPost: string };

    if (!jobPost?.trim()) {
      return NextResponse.json({ error: "jobPost is required" }, { status: 400 });
    }

    const systemPrompt = loadSkill();
    let raw = "";
    let provider = "anthropic";

    try {
      raw = await generateWithAnthropic(systemPrompt, jobPost);
    } catch (anthropicErr) {
      console.warn("Anthropic API failed, falling back to OpenAI:", anthropicErr instanceof Error ? anthropicErr.message : anthropicErr);
      provider = "openai";
      raw = await generateWithOpenAI(systemPrompt, jobPost);
    }

    const { proposal, jobType } = parseResponse(raw);
    return NextResponse.json({ proposal, jobType, provider });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
