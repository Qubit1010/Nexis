import { NextRequest, NextResponse } from "next/server";
import Anthropic from "@anthropic-ai/sdk";
import fs from "fs";
import path from "path";

export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { scenario } = body as { scenario: "A" | "B" };

    if (!scenario || !["A", "B"].includes(scenario)) {
      return NextResponse.json({ error: "scenario must be A or B" }, { status: 400 });
    }

    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) {
      return NextResponse.json({ error: "ANTHROPIC_API_KEY is not set in .env.local" }, { status: 500 });
    }

    // Load skill files as system prompt
    const skillRoot = path.join(process.cwd(), "..", "..", ".claude", "skills", "linkedin-dm-responder");
    const skillMd = fs.readFileSync(path.join(skillRoot, "SKILL.md"), "utf-8");
    const refFile = scenario === "A" ? "dm-sequence-structure.md" : "voss-framework.md";
    const refMd = fs.readFileSync(path.join(skillRoot, "references", refFile), "utf-8");
    const systemPrompt = `${skillMd}\n\n---\n\n${refMd}`;

    // Build user message
    let userMessage: string;

    if (scenario === "A") {
      const { name, role, company, companySize, dmNumber, recentPost, previousDm } = body as {
        name: string;
        role: string;
        company: string;
        companySize?: string;
        dmNumber: 2 | 3 | 4;
        recentPost?: string;
        previousDm?: string;
      };

      if (!name || !role || !company) {
        return NextResponse.json({ error: "name, role, and company are required" }, { status: 400 });
      }

      const dayMap: Record<number, number> = { 2: 4, 3: 9, 4: 16 };
      const day = dayMap[dmNumber] ?? 4;

      userMessage = `I need DM ${dmNumber} for a LinkedIn prospect who accepted my connection ${day} days ago but hasn't replied. Profile:

Name: ${name}
Role: ${role}
Company: ${company}${companySize ? `\nCompany size: ${companySize}` : ""}${recentPost ? `\nRecent post/bio: ${recentPost}` : ""}
${previousDm ? `\nPrevious DM I sent:\n"${previousDm}"\n` : ""}
Write DM ${dmNumber} for Day ${day}. Output only the message — no preamble, no explanation, no commentary. Just the DM, ready to paste.`;
    } else {
      const { conversation, profileLine, goal } = body as {
        conversation: string;
        profileLine: string;
        goal?: string;
      };

      if (!conversation || !profileLine) {
        return NextResponse.json({ error: "conversation and profileLine are required" }, { status: 400 });
      }

      userMessage = `${conversation}\n\nProfile: ${profileLine}${goal ? `\nMy goal: ${goal}` : ""}

What should I send back?

OUTPUT FORMAT (follow exactly — no preamble, no analysis before the message):
[The reply message, ready to paste into LinkedIn]

---
Phase: [Qualify / Label / Proof / Pull / Call]
Tactic: [one line naming the Voss move]

Start with the reply message directly. Do not include any analysis, explanation, or "Reading the thread:" section before the message.`;
    }

    const anthropic = new Anthropic({ apiKey });
    const message = await anthropic.messages.create({
      model: "claude-sonnet-4-6",
      max_tokens: 1024,
      system: systemPrompt,
      messages: [{ role: "user", content: userMessage }],
    });

    const raw = message.content[0]?.type === "text" ? message.content[0].text : "";

    if (scenario === "B") {
      // Split on --- divider to separate the DM from Phase/Tactic metadata
      const parts = raw.split(/\n---\n/);
      const dm = parts[0].trim();
      let phase = "";
      let tactic = "";

      if (parts[1]) {
        const phaseMatch = parts[1].match(/Phase:\s*(.+)/);
        const tacticMatch = parts[1].match(/Tactic:\s*([\s\S]+)/);
        phase = phaseMatch?.[1]?.trim() ?? "";
        tactic = tacticMatch?.[1]?.trim() ?? "";
      }

      return NextResponse.json({ dm, phase, tactic });
    }

    return NextResponse.json({ dm: raw.trim() });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
