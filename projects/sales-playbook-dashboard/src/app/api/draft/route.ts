import { NextRequest, NextResponse } from "next/server";
import Anthropic from "@anthropic-ai/sdk";
import OpenAI from "openai";
import fs from "fs";
import path from "path";

// Primary model (Anthropic). OpenAI is the fallback if Anthropic errors or is unkeyed.
const ANTHROPIC_MODEL = "claude-sonnet-4-6";
const OPENAI_FALLBACK_MODEL = "gpt-5.2";

export const dynamic = "force-dynamic";

type Platform = "linkedin" | "instagram";
type Mode = "opener" | "followup" | "reply";

const PLAYBOOK_ROOT = path.join(process.cwd(), "prompts", "sales-playbook");

function read(rel: string): string {
  return fs.readFileSync(path.join(PLAYBOOK_ROOT, rel), "utf-8");
}

function section(title: string, body: string): string {
  return `---\n\n## ${title}\n\n${body}`;
}

// LinkedIn connection notes are hard-capped at 300 chars. Post-connection DMs and
// live replies can run longer. Instagram is mobile-first: 300 ideal, 400 hard cap.
function charGuidance(platform: Platform, mode: Mode): string {
  if (platform === "linkedin") {
    return mode === "opener"
      ? "HARD CAP: 300 characters. This is a LinkedIn connection note — LinkedIn rejects anything longer."
      : "Keep it tight. Ideal under 350 characters, never over 600.";
  }
  return "Instagram is mobile-first. 300 characters ideal, 400 hard cap.";
}

function platformName(p: Platform): string {
  return p === "linkedin" ? "LinkedIn" : "Instagram";
}

// First-touch naming differs by platform.
function firstTouchName(p: Platform): string {
  return p === "linkedin" ? "connection note (or first DM)" : "Touch 1 DM";
}

function followupDay(platform: Platform, n: number): string {
  if (platform === "linkedin") {
    return ({ 2: "4", 3: "9", 4: "16" } as Record<number, string>)[n] ?? "4";
  }
  return ({ 2: "3", 3: "5", 4: "7-14" } as Record<number, string>)[n] ?? "3";
}

function buildSystemPrompt(platform: Platform, mode: Mode): string {
  const parts: string[] = [];

  // The playbook brain — always loaded.
  parts.push(read("SKILL.md"));
  parts.push(section("Opener Archetypes (rotate — never two prospects the same one back-to-back)", read("frameworks/opener-archetypes.md")));
  parts.push(section("Offer Positioning (AI automation is the wedge — never lead with web)", read("offer/ai-automation-positioning.md")));
  parts.push(section("Proof Bank (use ONE matched peer per message; never fabricate numbers)", read("offer/proof-bank.md")));

  // The gold-standard voice exemplar for this platform — this is what makes the
  // output sound human instead of like AI cadence. Match its register, not its words.
  const workedExample = platform === "linkedin" ? "worked-example-linkedin.md" : "worked-example-instagram.md";
  parts.push(section(`Worked Example — ${platformName(platform)} (the voice to match, do NOT copy verbatim)`, read(`references/${workedExample}`)));

  // Mode-specific material.
  if (mode === "opener" || mode === "followup") {
    const seq = platform === "linkedin" ? "linkedin-cold-dm-sequence.md" : "instagram-cold-dm-sequence.md";
    parts.push(section(`${platformName(platform)} Cold DM Sequence (cadence + structure)`, read(`scripts/${seq}`)));
  } else {
    parts.push(section("Live Conversation Playbook (6 phases + objection branches)", read("scripts/live-conversation-playbook.md")));
    parts.push(section("Voss Calibrated Questions (by phase)", read("frameworks/voss-calibrated-questions.md")));
    parts.push(section("Objection Responses", read("frameworks/objection-riffs.md")));
  }

  // Banned phrases last so they're the final filter in the model's context.
  parts.push(section("Banned Phrases — scan EVERY message against this before returning", read("references/what-not-to-do.md")));

  return parts.join("\n\n");
}

// Generate the draft. Tries Anthropic first; on any error (or if no Anthropic key)
// falls back to OpenAI. Returns the raw text plus which provider produced it.
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
      // Fall through to OpenAI if we have a key; otherwise rethrow below.
    }
  }

  if (openaiKey) {
    const openai = new OpenAI({ apiKey: openaiKey });
    const completion = await openai.chat.completions.create({
      model: OPENAI_FALLBACK_MODEL,
      max_tokens: 1024,
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userMessage },
      ],
    });
    const raw = completion.choices[0]?.message?.content ?? "";
    if (raw.trim()) return { raw, provider: "openai" };
    throw new Error("OpenAI fallback returned an empty response");
  }

  // Anthropic was the only provider and it failed.
  throw anthropicError instanceof Error
    ? anthropicError
    : new Error(String(anthropicError));
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const platform = body.platform as Platform;
    const mode = body.mode as Mode;

    if (!platform || !["linkedin", "instagram"].includes(platform)) {
      return NextResponse.json({ error: "platform must be 'linkedin' or 'instagram'" }, { status: 400 });
    }
    if (!mode || !["opener", "followup", "reply"].includes(mode)) {
      return NextResponse.json({ error: "mode must be 'opener', 'followup', or 'reply'" }, { status: 400 });
    }

    const systemPrompt = buildSystemPrompt(platform, mode);
    const chars = charGuidance(platform, mode);
    const pName = platformName(platform);

    let userMessage: string;

    if (mode === "opener") {
      const { name, role, company, signal, archetype } = body as {
        name?: string;
        role?: string;
        company?: string;
        signal?: string;
        archetype?: string;
      };
      if (!name || !role) {
        return NextResponse.json({ error: "name and role/bio are required for a cold opener" }, { status: 400 });
      }

      const archetypeLine =
        archetype && archetype !== "auto"
          ? `Use this archetype: ${archetype}. Adapt it to the signal below.`
          : "Pick the single best-fitting archetype for the available signal (auto-rotate). If there's a strong trigger, favor Specific Signal + Named Peer or Observation + Confession; if signal is thin, favor Permission-Based or Anti-Pitch.";

      userMessage = `Write a cold ${pName} ${firstTouchName(platform)} for this prospect.

Name: ${name}
Role / headline / bio: ${role}${company ? `\nCompany: ${company}` : ""}${signal ? `\nRecent post / trigger signal: ${signal}` : ""}

${archetypeLine}
${chars}
Match the voice in the worked example. No pitch, no calendar link, no em-dash, no emoji, no banned phrases. If you drop proof, use exactly one matched peer from the proof bank.

OUTPUT FORMAT — start your output with the finished message itself (no labels, no brackets, no preamble). After the message, a line containing only --- then:
Archetype: <which archetype you used>
Why: <one line — why this archetype + signal fit this prospect>`;
    } else if (mode === "followup") {
      const { name, role, company, touchNumber, signal, previousMessage } = body as {
        name?: string;
        role?: string;
        company?: string;
        touchNumber?: number;
        signal?: string;
        previousMessage?: string;
      };
      if (!name || !role) {
        return NextResponse.json({ error: "name and role/bio are required for a follow-up" }, { status: 400 });
      }
      const n = touchNumber ?? 2;
      const day = followupDay(platform, n);
      const stepLabel = platform === "linkedin" ? `DM ${n}` : `Touch ${n}`;

      userMessage = `Write ${stepLabel} (Day ${day}) for a ${pName} prospect who got my first touch but hasn't replied. Move the sequence forward — do not repeat the opener's angle.

Name: ${name}
Role / headline / bio: ${role}${company ? `\nCompany: ${company}` : ""}${signal ? `\nRecent post / signal: ${signal}` : ""}
${previousMessage ? `\nPrevious message I already sent (do NOT repeat its phrasing or core observation):\n"${previousMessage}"\n` : ""}
${chars}
No "just following up" / "bumping" / "circling back". Match the worked example's voice. No em-dash, no emoji, no banned phrases. Any call ask must be anchored to the Ops Teardown deliverable, never "quick chat".

OUTPUT FORMAT — start your output with the finished message itself (no labels, no brackets, no preamble). After the message, a line containing only --- then:
Archetype: <the angle/move used for this touch>
Why: <one line — what this touch does that the previous one didn't>`;
    } else {
      const { conversation, profileLine, goal } = body as {
        conversation?: string;
        profileLine?: string;
        goal?: string;
      };
      if (!conversation || !profileLine) {
        return NextResponse.json({ error: "conversation and profile are required for a live reply" }, { status: 400 });
      }

      userMessage = `Live ${pName} conversation. Draft the next reply that moves them exactly one phase forward (never skip phases).

${conversation}

Profile: ${profileLine}${goal ? `\nMy goal: ${goal}` : ""}

Match their register and message length. Label before you pull. Don't drop proof until they've disclosed a real pain or asked what I do; when you do, use one matched peer from the proof bank. Don't ask for a call until they've shown pull — and if you do, anchor it to the Ops Teardown deliverable, never "quick chat". ${chars} No em-dash, no emoji, no banned phrases.

OUTPUT FORMAT — start your output with the finished reply itself (no labels, no brackets, no analysis before it). After the reply, a line containing only --- then:
Phase: <Qualify / Label / Deepen / Proof / Warm Ask / Call>
Tactic: <one line naming the move>
Why: <one line — why this is the right next step in the thread>`;
    }

    const { raw, provider } = await generateDraft(systemPrompt, userMessage);

    // Split the message from the meta block.
    const parts = raw.split(/\n-{3,}\n/);
    let msg = (parts[0] ?? "").trim();
    const metaBlock = parts.slice(1).join("\n");

    // Defensively strip a leading bracketed placeholder line if the model echoed
    // the OUTPUT FORMAT scaffold (e.g. "[The message, ready to paste]").
    msg = msg
      .replace(/^\s*\[[^\]\n]*(ready to paste|the message|the reply)[^\]\n]*\]\s*\n+/i, "")
      .trim();

    const grab = (label: string): string => {
      const m = metaBlock.match(new RegExp(`${label}:\\s*(.+)`));
      return m?.[1]?.trim() ?? "";
    };

    const meta = {
      archetype: grab("Archetype"),
      phase: grab("Phase"),
      tactic: grab("Tactic"),
      why: grab("Why"),
    };

    return NextResponse.json({ message: msg, meta, provider });
  } catch (err) {
    const m = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: m }, { status: 500 });
  }
}
