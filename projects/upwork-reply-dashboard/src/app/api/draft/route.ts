import { NextRequest, NextResponse } from "next/server";
import Anthropic from "@anthropic-ai/sdk";
import OpenAI from "openai";
import fs from "fs";
import path from "path";
import { countExchanges, normalizeIdentity } from "@/lib/db";

// Primary model (Anthropic). OpenAI is the fallback if Anthropic errors or is unkeyed.
const ANTHROPIC_MODEL = "claude-sonnet-4-6";
const OPENAI_FALLBACK_MODEL = "gpt-5.2";

export const dynamic = "force-dynamic";

type Situation = "pre_hire" | "active" | "closeout" | "reactivation";
type JobType = "ai-services" | "marketing-automation" | "web-dev";

const PROMPTS_ROOT = path.join(process.cwd(), "prompts");

function read(skill: string, rel: string): string {
  return fs.readFileSync(path.join(PROMPTS_ROOT, skill, rel), "utf-8");
}

function section(title: string, body: string): string {
  return `---\n\n## ${title}\n\n${body}`;
}

const SITUATION_LABEL: Record<Situation, string> = {
  pre_hire: "Pre-hire Q&A + negotiation",
  active: "Active project",
  closeout: "Closeout + review ask",
  reactivation: "Reactivation",
};

const JOBTYPE_LABEL: Record<JobType, string> = {
  "ai-services": "AI Services (agentic automation — the premium wedge)",
  "marketing-automation": "Marketing Automation (workflows, CRM, lead ops)",
  "web-dev": "Web Dev (React/Next/Webflow/WordPress build)",
};

// The objection/value frameworks only earn their tokens where a client can push
// back (pre-hire negotiation, active-project scope). Closeout/reactivation skip them.
function loadsObjectionBrain(situation: Situation): boolean {
  return situation === "pre_hire" || situation === "active";
}

function buildSystemPrompt(situation: Situation): string {
  const parts: string[] = [];

  // The reply brain — always loaded.
  parts.push(read("upwork-reply-drafter", "SKILL.md"));
  parts.push(section("The Four Situations (per-situation playbook)", read("upwork-reply-drafter", "references/situations.md")));
  parts.push(section("Upwork Platform Mechanics (hard rules a reply must respect)", read("upwork-reply-drafter", "references/upwork-mechanics.md")));
  parts.push(section("Research Synthesis (the cited evidence behind every move)", read("upwork-reply-drafter", "references/research-synthesis.md")));

  // Negotiation/objection situations get the full framework brain.
  if (loadsObjectionBrain(situation)) {
    parts.push(section("Objection Psychology — DIAGNOSE the distortion FIRST", read("sales-playbook", "frameworks/objection-psychology.md")));
    parts.push(section("Objection Responses (phrase-level, tagged to the taxonomy)", read("sales-playbook", "frameworks/objection-riffs.md")));
    parts.push(section("Hormozi Value Equation (reframe cost as outcome + risk)", read("sales-playbook", "frameworks/hormozi-value-equation.md")));
  }
  parts.push(section("Voss Calibrated Questions (labeling, mirroring, how/what questions)", read("sales-playbook", "frameworks/voss-calibrated-questions.md")));

  // AI-tell / banned-phrase filter last so it's the final gate in the model's context.
  parts.push(section("Banned Phrases + AI Tells — scan EVERY reply against this before returning", read("sales-playbook", "references/what-not-to-do.md")));

  return parts.join("\n\n");
}

async function generateDraft(
  systemPrompt: string,
  userMessage: string
): Promise<{ raw: string; provider: "anthropic" | "openai" }> {
  const anthropicKey = process.env.ANTHROPIC_API_KEY;
  const openaiKey = process.env.OPENAI_API_KEY;

  if (!anthropicKey && !openaiKey) {
    throw new Error(
      "No API key set. Add ANTHROPIC_API_KEY (and optionally OPENAI_API_KEY as fallback) to .env.local (see README)."
    );
  }

  let anthropicError: unknown = null;

  if (anthropicKey) {
    try {
      const anthropic = new Anthropic({ apiKey: anthropicKey });
      const message = await anthropic.messages.create({
        model: ANTHROPIC_MODEL,
        max_tokens: 1024,
        system: systemPrompt,
        messages: [{ role: "user", content: userMessage }],
      });
      const raw = message.content[0]?.type === "text" ? message.content[0].text : "";
      if (raw.trim()) return { raw, provider: "anthropic" };
      throw new Error("Anthropic returned an empty response");
    } catch (err) {
      anthropicError = err;
    }
  }

  if (openaiKey) {
    if (anthropicError) console.warn("Anthropic failed, falling back to OpenAI:", anthropicError);
    const openai = new OpenAI({ apiKey: openaiKey });
    const completion = await openai.chat.completions.create({
      model: OPENAI_FALLBACK_MODEL,
      // gpt-5* rejects max_tokens; it wants max_completion_tokens + reasoning_effort
      max_completion_tokens: 2048,
      reasoning_effort: "low",
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userMessage },
      ],
    });
    const raw = completion.choices[0]?.message?.content ?? "";
    if (raw.trim()) return { raw, provider: "openai" };
    throw new Error("OpenAI fallback returned an empty response");
  }

  throw anthropicError instanceof Error ? anthropicError : new Error(String(anthropicError));
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const situation = body.situation as Situation;
    const jobType = (body.jobType as JobType) || "ai-services";

    if (!situation || !["pre_hire", "active", "closeout", "reactivation"].includes(situation)) {
      return NextResponse.json(
        { error: "situation must be 'pre_hire', 'active', 'closeout', or 'reactivation'" },
        { status: 400 }
      );
    }

    const {
      clientMessage,
      thread,
      profile,
      goal,
      identityRaw,
      state,
    } = body as {
      clientMessage?: string;
      thread?: string;
      profile?: string;
      goal?: string;
      identityRaw?: string;
      state?: { exchange_count?: number; stage?: string; last_contact?: string };
    };

    // Reactivation reopens a cold thread, so it needs the profile + a past outcome, not a live message.
    if (situation !== "reactivation" && !clientMessage?.trim()) {
      return NextResponse.json({ error: "clientMessage is required" }, { status: 400 });
    }
    if (!profile?.trim()) {
      return NextResponse.json({ error: "a client/job profile line is required" }, { status: 400 });
    }

    const systemPrompt = buildSystemPrompt(situation);

    const contactHint = identityRaw ? normalizeIdentity(identityRaw) : undefined;
    const combined = [thread, clientMessage].filter(Boolean).join("\n");
    const exchangeCount = Math.max(countExchanges(combined, contactHint), state?.exchange_count ?? 0);

    const userMessage = `Draft the next reply in this Upwork CLIENT conversation.

SITUATION: ${SITUATION_LABEL[situation]}
JOB TYPE: ${JOBTYPE_LABEL[jobType]}

CONVERSATION STATE (ground truth — do not re-infer):
- Client replies so far: ${exchangeCount}
- Stage: ${state?.stage || "infer from the thread"}${state?.last_contact ? `\n- Last contact: ${state.last_contact}` : ""}

CLIENT / JOB PROFILE: ${profile}${goal ? `\nMY GOAL FOR THIS REPLY: ${goal}` : ""}
${thread ? `\nFULL THREAD SO FAR:\n${thread}\n` : ""}${clientMessage ? `\nCLIENT'S LATEST MESSAGE (reply to this):\n${clientMessage}` : `\n(No live message — this is a REACTIVATION. Open a dormant client relationship with a genuine reason and one low-friction next step. Reference a specific past outcome from the profile.)`}

Follow the ${SITUATION_LABEL[situation]} playbook and the platform mechanics. Move scope, never the rate. Never advise closing the contract yourself. Match the client's length and register, open with a specific diagnosis or real detail (not a warm-up), 150-200 words max, no em-dash, no banned phrases or AI tells, and vary the shape. If proof helps, use exactly one matched result from the bank (never invent numbers).

OUTPUT FORMAT — start with the finished reply itself (no labels, no preamble, ready to paste). After the reply, a line containing only --- then:
Situation: ${SITUATION_LABEL[situation]}
Move: <the one tactic used>
Why: <one line — why this is the right next step in this thread>`;

    const { raw, provider } = await generateDraft(systemPrompt, userMessage);

    const splitParts = raw.split(/\n-{3,}\n/);
    let msg = (splitParts[0] ?? "").trim();
    const metaBlock = splitParts.slice(1).join("\n");

    // Strip a leading bracketed scaffold line if the model echoed the OUTPUT FORMAT.
    msg = msg
      .replace(/^\s*\[[^\]\n]*(ready to paste|the reply|the message)[^\]\n]*\]\s*\n+/i, "")
      .trim();

    const grab = (label: string): string => {
      const m = metaBlock.match(new RegExp(`${label}:\\s*(.+)`));
      return m?.[1]?.trim() ?? "";
    };

    const meta = {
      situation: grab("Situation") || SITUATION_LABEL[situation],
      move: grab("Move"),
      why: grab("Why"),
    };

    return NextResponse.json({ message: msg, meta, provider });
  } catch (err) {
    const m = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: m }, { status: 500 });
  }
}
