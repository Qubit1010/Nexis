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
    const skillRoot = path.join(process.cwd(), "..", "..", ".claude", "skills", "instagram-dm-responder");
    const skillMd = fs.readFileSync(path.join(skillRoot, "SKILL.md"), "utf-8");
    const refFile = scenario === "A" ? "touch-sequence.md" : "conversation-playbook.md";
    const refMd = fs.readFileSync(path.join(skillRoot, "references", refFile), "utf-8");
    const systemPrompt = `${skillMd}\n\n---\n\n${refMd}`;

    // Build user message
    let userMessage: string;

    if (scenario === "A") {
      const { name, username, bio, followers, touchNumber, recentPost, previousTouch } = body as {
        name: string;
        username?: string;
        bio: string;
        followers?: string;
        touchNumber: 2 | 3 | 4;
        recentPost?: string;
        previousTouch?: string;
      };

      if (!name || !bio) {
        return NextResponse.json({ error: "name and bio are required" }, { status: 400 });
      }

      const dayMap: Record<number, string> = { 2: "3-4", 3: "8-10", 4: "15" };
      const day = dayMap[touchNumber] ?? "3-4";

      userMessage = `I need Touch ${touchNumber} for a prospect who got my opening DM and hasn't replied. Here's their info:

Name: ${name}${username ? `\nUsername: ${username}` : ""}
Bio: ${bio}${followers ? `\nFollowers: ${followers}` : ""}${recentPost ? `\nRecent post caption: ${recentPost}` : ""}
${previousTouch ? `\nPrevious touch I sent:\n"${previousTouch}"\n` : ""}
Write Touch ${touchNumber} for Day ${day}. Output only the message — no preamble, no explanation, no commentary. Just the DM, ready to paste.`;
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
[The reply message, ready to paste into Instagram]

---
Phase: [Open / Label / Deepen / Proof / Warm Ask / Call]
Tactic: [one line naming the move used]

Start with the reply message directly. Do not include any analysis, explanation, or preamble before the message.`;
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
