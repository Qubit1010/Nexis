import { NextRequest, NextResponse } from "next/server";
import type { ResearchOutput } from "@/lib/types";

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

  "Instagram Carousel": `5-8 slides. Return as:
Slide 1: [STOP-SCROLL HOOK — max 8 words, bold statement or shocking stat]
Slide 2: [Setup the problem or context]
Slide 3: [First insight or step]
Slide 4: [Second insight or step]
Slide 5: [Third insight or step]
Slide 6 (if applicable): [Bonus tip or contrarian take]
Slide 7/8: [CTA slide — "Follow for more" or "Save this for later"]
Caption: 100-250 chars, hooks the scroll, max 2 emojis.
Hashtags: use research hashtags if available.`,

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

function buildPrompt(
  platform: string,
  format: string,
  topic: string,
  research: ResearchOutput | null
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

  return `You are writing content for Aleem Ul Hassan's personal brand (NexusPoint AI agency).

VOICE RULES — these define Aleem's brand, apply without exception:
- Write as Aleem in first person: "I", "my", "I built", "I tried", "I noticed"
- "How I" not "How to" — personal experience over generic advice
- No em dashes — use commas or short sentences instead
- No emojis for LinkedIn or Blog; maximum 2 emojis for Instagram
- Specific > vague: replace "many companies" with actual numbers from data
- Hook first — never bury the lead
- Never start with "In today's rapidly evolving AI landscape..." or any variant
- Short sentences. White space. No corporate filler.

ALEEM'S CONTEXT:
- 21-year-old founder of NexusPoint (AI automation agency) + BSAI student in Islamabad
- Builds real AI systems: multi-agent workflows, automation pipelines, Claude Code extensions
- Audience: startup founders, tech entrepreneurs, developers, AI-curious builders
- Core message: AI as a business outcome driver, not a tech toy
${researchBlock}

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
    const { topic, platform, format, research } = body as {
      topic: string;
      platform: string;
      format: string;
      research?: ResearchOutput;
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

    const prompt = buildPrompt(platform, format, topic, research ?? null);

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
