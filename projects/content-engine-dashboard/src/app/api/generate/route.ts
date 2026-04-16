import { NextRequest, NextResponse } from "next/server";
import type { ResearchOutput, ContentMode, PillarKey } from "@/lib/types";

export const dynamic = "force-dynamic";

const PLATFORM_SPECS: Record<string, string> = {
  "LinkedIn Text Post": `300-800 words. Strong 3-line hook (each line is its own paragraph).
Body: 4-6 short insight paragraphs, each 1-3 sentences. Specific and personal.
End with an open question to invite discussion. No headers. Lots of white space.`,

  "LinkedIn Article": `800-1500 words. SEO-friendly H1 title (use primary_keyword if available).
Intro: hook + problem statement. Body: 3-4 sections with H2 headers. Specific data from research.
Conclusion: key takeaway + CTA.`,

  "LinkedIn Newsletter": `600-1000 words. Conversational tone. Intro: why this matters now.
Body: 3 main insights with examples. End: one actionable takeaway.`,

  "Instagram Carousel": `5-8 slides. For EACH slide output exactly this structure (no deviations):

Slide N Visual Concept: [One sentence describing the background, visual element, or graphic treatment]
Headline Text: [The bold, punchy text on the slide — max 10 words]
Subtext: [1-2 supporting sentences that expand the headline]

Slide 1: STOP-SCROLL HOOK — shocking stat, bold claim, or counter-intuitive statement (max 8 words headline).
Slide 2: Set up the problem or context.
Slides 3-5: One insight, step, or argument per slide.
Slide 6 (optional): Bonus tip or contrarian take.
Last slide: CTA — "Follow for more" or "Save this."

After all slides, add:
Caption: 100-250 chars, hooks the scroll, max 2 emojis.
Hashtags: use research hashtags if available.`,

  "Instagram Caption": `Standalone Instagram caption (no slides, no script).
Structure:
- Line 1: STOP-SCROLL hook — bold claim, counter-intuitive statement, or provocative question. This line must work standalone.
- Lines 2-6: Build the argument. Short punchy sentences. Each line earns the next. Use personal experience, specific numbers, or a concrete insight. No fluff.
- Line 7-8: Zoom out — the broader principle or why this matters.
- Final line: CTA or open question that invites a reply or save.
Length: 150-300 words (not chars). Enough depth to earn engagement, short enough to not lose them.
Line breaks: one blank line between each section for Instagram readability.
Max 2 emojis, placed where they add emphasis — not as decoration at the end.
Hashtags (on a new line after the caption): 8-15 niche-specific tags. Use research hashtags if available.`,

  "Instagram Reel": `Short-form video script. Hook (0-3s): visual + spoken hook.
Body (3-30s): 3-5 punchy points, one per scene. Outro (30-45s): CTA.
Include [B-ROLL] notes. Keep spoken lines under 10 words each.`,

  "Instagram Short Video": `45-90 second video script. Hook + problem + 3 insights + CTA.
Format: [SCENE] descriptions + spoken dialogue.`,

  "Blog Article": `800-2000 words. SEO-optimized. Use primary_keyword in H1 title.
Intro: hook + problem + what you'll learn (no "In today's landscape" openings).
Body: 3-4 H2 sections. Embed 2-3 data_points from research naturally.
Conclusion: summary + actionable next step + soft CTA.`,

  "Blog Tutorial": `Step-by-step guide. 800-1500 words. H1: "How I [did X]" format.
Intro: why this matters + quick result. Steps: numbered, specific, with code/examples if relevant.
End: result + what to try next.`,

  "Blog Opinion": `500-1000 words. Strong POV. H1: contrarian statement.
Intro: the conventional wisdom. Body: why it's wrong + your experience.
End: what you actually believe + invite disagreement.`,
};

function getFormatSpec(platform: string, format: string): string {
  const key = `${platform} ${format}`;
  return (
    PLATFORM_SPECS[key] ||
    PLATFORM_SPECS[`${platform} ${Object.keys(PLATFORM_SPECS).find((k) => k.includes(format)) || ""}`] ||
    `Write a complete ${format} for ${platform}. 300-600 words. Hook first, specific details, end with CTA.`
  );
}

const PILLAR_DEFINITIONS: Record<PillarKey, string> = {
  lived_experience: "LIVED EXPERIENCE: Root it in real events — failed proposals, client mistakes, what actually happened. Include at least one specific anchor: project type, client type, dollar amount, time lost, or exact mistake. Vague experience is as bad as no experience.",
  strong_pov: "STRONG POV: Take a clear, defensible side. Name the conventional wisdom you're rejecting before you reject it. The opinion must be defensible — state the condition under which you'd be wrong. Never be neutral.",
  cross_domain: "CROSS-DOMAIN SYNTHESIS: Connect AI/tech with an unexpected domain (Philosophy, Stoicism, compiler theory, gym discipline, history). The connection must be non-obvious. Lead with the unexpected domain before bridging to the business/AI point.",
  taste_judgment: "TASTE & JUDGMENT: Make a decisive call. State what you would NOT do and why. Never hedge with 'it depends' — if context matters, state the specific condition, then make the call.",
  identity_voice: "IDENTITY & VOICE: Student founder in Pakistan building real systems. This context must appear as constraint, not credential — show how it limits or shapes decisions. If the piece could have been written by a US-based senior engineer with no resource pressure, rewrite it.",
  practical_stakes: "PRACTICAL STAKES: Answer two questions — what breaks if you ignore this? And what does doing it right look like in production? Don't explain a concept without grounding it in a consequence. The production example must come from real work, not a hypothetical.",
  content_specific: "CONTENT SPECIFIC: Explain what the topic is, how it works, and how it applies in real business or life. Be engaging, easy to understand, and easy to follow. Ground explanations in practical use cases.",
};

const MODE_INSTRUCTIONS: Record<ContentMode, string> = {
  news: `CONTENT MODE: News / Analysis
This is data-driven content. Your primary job is to inform and analyze, not to tell a personal story.
- Lead with facts, statistics, and what actually happened.
- Personalization should be light: one brief anchor to Aleem's perspective is sufficient. Do not force lived experience if the topic does not naturally connect.
- Prioritize clarity and insight over storytelling.
- Frame the analysis through Aleem's lens as an AI agency founder — what does this mean for builders and founders?`,

  opinion: `CONTENT MODE: Opinion / POV
This is a position piece. Aleem must take a clear, defensible side.
- Open with the contrarian claim. Build the argument. End with the principle.
- Do not hedge. Do not present "both sides." Pick one and own it.
- Name the conventional wisdom you're rejecting before you reject it.
- The opinion must be defensible — state the condition under which you'd be wrong.`,

  story: `CONTENT MODE: Personal Story
This is narrative-first. The insight must emerge from the story — do not front-load conclusions.
- Start in the moment, not with the lesson.
- Identity and context (Pakistan, student founder, real constraints) must be felt throughout.
- The reader should discover the principle alongside Aleem, not be told it upfront.
- End with the extractable principle that generalizes beyond the specific case.`,

  tutorial: `CONTENT MODE: Tutorial / How-to
This is practical content. Lead with what the reader will be able to do after reading.
- Each step must be grounded in a real scenario from Aleem's work or context.
- No theoretical fluff — every point needs a real-world application or consequence.
- Show the pitfall or failure mode at least once so the reader understands what to avoid.`,
};

function buildPrompt(
  platform: string,
  format: string,
  topic: string,
  research: ResearchOutput | null,
  context?: string,
  contentMode?: ContentMode,
  selectedPillars?: PillarKey[]
): string {
  const spec = getFormatSpec(platform, format);
  const hasResearch = research?.available && research.primary_keyword;

  let researchBlock = "";
  if (hasResearch) {
    researchBlock = `
RESEARCH DATA (use this to make the content specific and credible):
- Primary keyword: ${research!.primary_keyword}
- Secondary keywords: ${research!.secondary_keywords?.join(", ") || "none"}
- Content gap (your differentiated angle): ${research!.content_gap || "none"}
${
  research!.data_points?.length
    ? `- Data points to use:\n${research!.data_points
        .slice(0, 3)
        .map((d) => `  • ${d.fact} (${d.source})`)
        .join("\n")}`
    : ""
}
${
  research!.hashtags?.length && platform === "Instagram"
    ? `- Hashtags: ${research!.hashtags.join(" ")}`
    : ""
}`;
  }

  const modeBlock = contentMode ? `\n${MODE_INSTRUCTIONS[contentMode]}\n` : "";

  const pillarsToEnforce = selectedPillars && selectedPillars.length > 0 ? selectedPillars : Object.keys(PILLAR_DEFINITIONS) as PillarKey[];
  const pillarsBlock = `ACTIVE PILLARS — enforce ALL of these in the output (others are optional):
${pillarsToEnforce.map((k) => `- ${PILLAR_DEFINITIONS[k]}`).join("\n")}`;

  return `You are writing content for Aleem Ul Hassan's personal brand (NexusPoint AI agency).
${modeBlock}
THE UNSWAPPABLE FORMULA — every piece must satisfy this or it's generic:
(Personal Experience) + (Strong Opinion) + (Cross-domain Insight) + (Clear Identity)
If any element is missing, rewrite until all four are present.

${pillarsBlock}

ALEEM'S DUAL LENS (use especially for LinkedIn):
Pair the academic frame with the operational reality:
"In [university/classroom], we [theoretical framing]. At NexusPoint, we [real-world deployment outcome]."
Example: "In my lectures, standard theory is one thing. In the trenches of running an agency, the real constraints look completely different."

CONTENT LADDER — aim for level 7+ only, never below 5:
FORBIDDEN: AI summaries / SEO blogs / generic tutorials / neutral explainers
REQUIRED: Case studies, essays with POV, personal frameworks, original theories, public thinking in real time

GOLDEN PATTERN (for long-form and LinkedIn):
Real problem -> Naive/wrong approach -> Discovery -> Mistake made -> Insight extracted -> Extractable principle
Example: Start with the problem you actually faced. Show your wrong first instinct. Reveal what you learned. End with a principle that generalises beyond your specific case.

ANTI-PATTERNS — never produce any of these:
- "Here are [N] ways to..." with no personal stake
- Neutral summaries of what a tool does without Aleem's experience with it
- Any opening that explains a concept before establishing why it matters to Aleem specifically
- Generic advice that could apply to anyone — anchor to Aleem's specific context
- Filler phrases: "In today's rapidly evolving...", "It's no secret that...", "Game-changer", "Leverage"

VOICE RULES — apply without exception:
- Write as Aleem in first person: "I", "my", "I built", "I tried", "I noticed"
- No em dashes — use commas or short sentences instead
- No emojis for LinkedIn or Blog; maximum 2 emojis for Instagram
- Specific > vague: replace "many companies" with actual numbers from the research data
- Hook first — never bury the lead
- Short sentences. White space. No corporate filler.

ALEEM'S CONTEXT:
- 25-year-old founder of NexusPoint (AI automation agency) + BSAI student in Islamabad, Pakistan
- Builds real AI systems: multi-agent workflows, automation pipelines, Claude Code extensions
- Runs a real team. Deals with real client constraints.
- Interests beyond tech: Philosophy, Science, Stoicism, History, systems thinking, gym discipline
- Audience: startup founders, tech entrepreneurs, developers, AI-curious builders
- Core message: AI as a business outcome driver, not a tech toy. Chatbots are v1. Agents are v2.
${researchBlock}
${context ? `\nSOURCE MATERIAL (use facts, quotes, and specifics from this to ground the content — do not summarize it, extract what's useful and make it Aleem's own):\n${context}\n` : ""}
PLATFORM: ${platform}
FORMAT: ${format}
TOPIC: ${topic}

FORMAT SPECIFICATIONS:
${spec}

Write the complete, finished, publish-ready content. Output ONLY the content — no intro like "Here's the post:", no commentary, no markdown headers around the piece itself. Just the content.`;
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { topic, platform, format, research, context, contentMode, selectedPillars } = body as {
      topic: string;
      platform: string;
      format: string;
      research?: ResearchOutput;
      context?: string;
      contentMode?: ContentMode;
      selectedPillars?: PillarKey[];
    };

    if (!topic || !platform || !format) {
      return NextResponse.json(
        { error: "topic, platform, and format are required" },
        { status: 400 }
      );
    }

    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) {
      return NextResponse.json(
        { error: "OPENAI_API_KEY is not set in .env.local" },
        { status: 500 }
      );
    }

    const prompt = buildPrompt(platform, format, topic, research ?? null, context, contentMode, selectedPillars);

    const response = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: "gpt-4o",
        messages: [{ role: "user", content: prompt }],
        temperature: 0.7,
        max_tokens: 2000,
      }),
    });

    if (!response.ok) {
      const err = await response.text();
      return NextResponse.json(
        { error: `OpenAI error: ${err}` },
        { status: 500 }
      );
    }

    const data = await response.json() as {
      choices: Array<{ message: { content: string } }>;
    };
    const content = data.choices[0]?.message?.content ?? "";

    return NextResponse.json({ content });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
