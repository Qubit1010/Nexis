import { NextRequest, NextResponse } from "next/server";
import Anthropic from "@anthropic-ai/sdk";
import OpenAI from "openai";
import type { ContentMode, PillarKey } from "@/lib/types";

export const dynamic = "force-dynamic";

// Spec mirrors .claude/skills/content-engine/references/platform-formats.md (2026 research
// from marketing-advisor). Keep the two in sync when either changes.
const PLATFORM_SPECS: Record<string, string> = {
  "LinkedIn Text Post": `150-300 words (a narrative post may run to ~500 only if the formatting is flawless).
Line 1 = a standalone STOP-SCROLL hook inside the first 125-150 characters (the part shown before "see more"): a bold claim, a number, or a specific moment. Never waste it on context or warm-up.
Line 2 = a short "fold break", a one-line tease that makes the reader click "see more". Most posts die at this fold, so earn the click.
Body: ONE idea per line. Single-sentence lines with a BLANK line between every line. Do NOT write 3-4 sentence paragraph blocks — dense blocks get skimmed and kill dwell time, which is the #1 ranking signal (a 61s+ read earns ~13x the engagement of a 3s skim). The white space IS the format; the post should be easy to read top to bottom.
Keep every line short, specific, and personal: real experience, real numbers, concrete detail. No filler line.
NO link in the body (an external link cuts reach 50-70%). If a link is essential, end with "link's in the comments" instead.
No headers, no emojis, no em dashes.
End with ONE specific question that invites a real reply. Do NOT add a "follow me", "repost", or "share this" line — the close must be a value-native question, a "save this", or a comment-to-DM trigger.
Hashtags: 1-2 relevant, or none (3-5 cuts reach ~29%).`,

  "LinkedIn Carousel": `LinkedIn document (PDF) carousel — the #1 organic format on LinkedIn (6.6-7% engagement rate). 6-12 slides. For EACH slide output exactly this structure (no deviations):

Slide N Visual Concept: [One sentence describing the layout/visual treatment — clean, high-contrast]
Headline Text: [Bold, punchy text, max 10 words]
Subtext: [1-2 supporting sentences]

Slide 1 (cover): a strong standalone hook that works as a thumbnail (max 8 words headline), high contrast.
Slides 2 to N-1: one insight, step, or argument per slide, consistent layout.
Last slide: a value-native CTA + handle ("Save this" or a comment-to-DM trigger — NOT a generic "follow me").

After the slides, add:
Post text: 50-150 words of context to post alongside the document. Hook first, no link in the body.`,

  "LinkedIn Article": `600-1200 words. SEO-friendly H1 (use primary_keyword if available). Open with a bold claim or a specific moment — zero throat-clearing.
Body: 2-3 H2 sections (H2 every 200-300 words), specific data from research.
Conclusion: framework/lesson + one value-native CTA (not a generic follow ask). Write at least 600 words.`,

  "LinkedIn Newsletter": `400-600 words. Conversational tone. Intro: why this matters now.
Body: 2-3 main insights with examples. End: one actionable takeaway. No "follow me" boilerplate.`,

  "Instagram Carousel": `6-8 slides. For EACH slide output exactly this structure (no deviations):

Slide N Visual Concept: [One sentence describing the background, visual element, or graphic treatment]
Headline Text: [The bold, punchy text on the slide — max 10 words]
Subtext: [1-2 supporting sentences that expand the headline]

Slide 1: STOP-SCROLL HOOK — shocking stat, bold claim, or counter-intuitive statement (max 8 words headline). The cover must stand alone as a thumbnail.
Slide 2: Set up the problem or context.
Slides 3-6: One insight, step, or argument per slide.
Last slide: value-native CTA — "Save this if you're building one" or a comment-to-DM trigger (NOT a bare "Follow for more").

After all slides, add:
Caption: 100-250 chars, hooks the scroll, ends with a question or save prompt, max 2 emojis.
Hashtags: 3-5 niche tags (use research hashtags if available — never a 30-tag wall).`,

  "Instagram Caption": `Standalone Instagram caption (no slides, no script). 125-250 words.
Structure:
- Line 1: STOP-SCROLL hook — bold claim, counter-intuitive statement, or provocative question. It must work standalone AND land inside the first ~125 characters, because the caption truncates at "... more".
- Body: ONE idea per line, short punchy single-sentence lines with a blank line between them. Each line earns the next. Use personal experience, specific numbers, or a concrete insight. No dense paragraph blocks, no fluff.
- Then zoom out: the broader principle or why this matters.
- Final line: a value-native CTA — an open question, "save this", or a comment-to-DM trigger. NOT a bare "follow me".
Optimize for saves and sends (a send is worth 3-5x a like, a save ~3x), not likes.
No emojis, no em dashes.
Hashtags (on a new line): 3-5 highly relevant niche tags only. Quality over quantity.`,

  "Instagram Reel": `Short-form video script, 15-30 seconds (completion beats length). COLD OPEN — drop straight into the climax, motion in the first frame, NO "hey guys / today I want to talk about".
Hook (0-3s): spoken AND on-screen text — win this or lose 50% of viewers.
Body (3-25s): 3-5 punchy beats, one per scene, spoken lines under 10 words. Include [B-ROLL] notes.
Close (final 2-5s): one value-native CTA (often comment-to-DM).
Note at the top that kinetic captions are mandatory (most watch on mute) and to optimize for saves + sends, not likes.`,

  "Instagram Short Video": `45-90 second video script. Cold-open hook + problem + 3 insights + value-native CTA.
Format: [SCENE] descriptions + spoken dialogue. Include [B-ROLL]. Kinetic captions mandatory.`,

  "Blog Article": `800-1500 words. SEO + AI-citable: use primary_keyword in a natural H1 (under 60 chars), put a crisp definition/summary near the top, and write self-contained factual sentences (AI engines like ChatGPT/Perplexity should be able to quote you).
Intro: hook + problem + what you'll learn (NO "In today's landscape" openings).
Body: 4-6 H2 sections (H2 every 200-350 words; that many sections is how you reach 800+ words). Embed 2 data_points from research naturally with inline citation; answer 1-2 people_also_ask questions as their own H2s.
Conclusion: zoom out to the universal pattern + one clear next step.
When the topic allows, prefer a comparison ("X vs Y") or customer-voiced angle, which convert far better.
Write the FULL 800-1500 words. Do not stop short of 800 words; if you are short, deepen an example or add a sub-section.`,

  "Blog Tutorial": `Step-by-step guide. 600-1000 words. H1: "How I [did X]" format.
Intro: why this matters + quick result. Steps: numbered, specific, with code/examples if relevant. Show one failure mode.
End: result + what to try next.`,

  "Blog Opinion": `400-700 words. Strong POV. H1: contrarian statement.
Intro: the popular belief you're challenging (use a fresh phrase each time — e.g. "what most people think", "the standard advice", "what everyone assumes", "the default take", "the accepted playbook" — never repeat the same phrase). Body: why it's wrong + your experience.
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

// Long-form formats need more output headroom so they don't truncate (1200 tokens ~= 900 words).
function getMaxTokens(platform: string, format: string): number {
  const key = `${platform} ${format}`;
  const longForm = new Set(["LinkedIn Article", "LinkedIn Newsletter", "Blog Article", "Blog Tutorial"]);
  return longForm.has(key) ? 2400 : 1400;
}

const PILLAR_DEFINITIONS: Record<PillarKey, string> = {
  lived_experience: "LIVED EXPERIENCE: Root it in real events — failed proposals, client mistakes, what actually happened. Include at least one specific anchor: project type, client type, dollar amount, time lost, or exact mistake. Vague experience is as bad as no experience.",
  strong_pov: "STRONG POV: Take a clear, defensible side. Name the popular belief you're rejecting — use a different phrase each time (e.g. 'what most people assume', 'the standard advice', 'the default take', 'the accepted playbook', 'what everyone gets wrong', 'the usual thinking'). Never write the phrase 'conventional wisdom'. The opinion must be defensible — state the condition under which you'd be wrong. Never be neutral.",
  cross_domain: "CROSS-DOMAIN SYNTHESIS: Connect AI/tech with an unexpected domain (Philosophy, compiler theory, gym discipline, history, science, systems thinking). The connection must be non-obvious. Lead with the unexpected domain first (philosophy, experience, computer science, tech-business, history, or some insight) before bridging to the business/AI point.",
  taste_judgment: "TASTE & JUDGMENT: Make a decisive call. State what you would NOT do and why. Never hedge with 'it depends' — if context matters, state the specific condition, then make the call.",
  identity_voice: "IDENTITY & VOICE: Founder in Pakistan building real AI systems. This context must appear as constraint, not credential — show how it limits or shapes decisions. If the piece could have been written by a US-based senior engineer with no resource pressure, rewrite it. Do NOT name a specific company/agency or reference school, university, classroom, lectures, or being a student.",
  practical_stakes: "PRACTICAL STAKES: Answer two questions — what breaks if you ignore this? And what does doing it right look like in production? Don't explain a concept without grounding it in a consequence. The production example must come from real work, not a hypothetical.",
  content_specific: "CONTENT SPECIFIC: Explain what the topic is, how it works, and how it applies in real business or life. Be engaging, easy to understand, and easy to follow. Ground explanations in practical use cases.",
};

const MODE_INSTRUCTIONS: Record<ContentMode, string> = {
  news: `CONTENT MODE: News / Analysis
This is data-driven content. Your primary job is to inform and analyze, not to tell a personal story.
- Lead with facts, statistics, and what actually happened.
- Personalization should be light: one brief anchor to Aleem's perspective is sufficient. Do not force lived experience if the topic does not naturally connect.
- Prioritize clarity and insight over storytelling.
- Frame the analysis through Aleem's lens as a founder building real AI systems — what does this mean for builders and founders?`,

  opinion: `CONTENT MODE: Opinion / POV
This is a position piece. Aleem must take a clear, defensible side.
- Open with the contrarian claim. Build the argument. End with the principle.
- Do not hedge. Do not present "both sides." Pick one and own it.
- Name the popular belief you're rejecting — use a different phrase each time (e.g. "what most people assume", "the standard advice", "the default take", "the accepted playbook", "what everyone gets wrong"). Never write the phrase "conventional wisdom".
- The opinion must be defensible — state the condition under which you'd be wrong.`,

  story: `CONTENT MODE: Personal Story
This is narrative-first. The insight must emerge from the story — do not front-load conclusions.
- Start in the moment, not with the lesson.
- Identity and context (Pakistan, founder, real constraints) must be felt throughout — never name a school, university, or agency.
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
  context?: string,
  contentMode?: ContentMode,
  selectedPillars?: PillarKey[]
): string {
  const spec = getFormatSpec(platform, format);

  const modeBlock = contentMode ? `\n${MODE_INSTRUCTIONS[contentMode]}\n` : "";

  const pillarsToEnforce = selectedPillars && selectedPillars.length > 0 ? selectedPillars : Object.keys(PILLAR_DEFINITIONS) as PillarKey[];
  const pillarsBlock = `ACTIVE PILLARS — enforce ALL of these in the output (others are optional):
${pillarsToEnforce.map((k) => `- ${PILLAR_DEFINITIONS[k]}`).join("\n")}`;

  return `You are writing content for Aleem Ul Hassan's personal brand.

HARD CONSTRAINT — DO NOT mention any of the following anywhere in the output:
- Aleem's agency name (NexusPoint) or any phrasing like "my agency", "at my company", "my AI agency"
- Academia: university, college, school, classroom, lectures, professor, course, degree, BSAI, "as a student", "in my studies", "in my classes"
If the topic naturally pulls toward these, reframe in personal/operational terms instead (e.g. "in my own work", "building real systems", "from what I've shipped").

${modeBlock}
THE UNSWAPPABLE FORMULA — every piece must satisfy this or it's generic:
(Personal Experience) + (Strong Opinion) + (Cross-domain Insight) + (Clear Identity)
If any element is missing, rewrite until all four are present.

${pillarsBlock}

CONTENT LADDER — aim for level 7+ only, never below 5:
FORBIDDEN: AI summaries / generic SEO filler / generic tutorials / neutral explainers (SEO done WITH a strong POV and real experience is encouraged for blogs)
REQUIRED: Case studies, essays with POV, personal frameworks, original theories, public thinking in real time

GOLDEN PATTERN (for blog long-form and LinkedIn text posts/articles ONLY, never carousels or video):
Real problem -> Naive/wrong approach -> Discovery -> Mistake made -> Insight extracted -> Extractable principle
This shapes the narrative arc ONLY. Never use the step names ("Discovery", "Mistake Made", "Insight Extracted", "The Principle") as literal headlines, slide titles, or section labels. Carousel slide headlines must be punchy content, not framework labels.

ANTI-PATTERNS — never produce any of these:
- "Here are [N] ways to..." with no personal stake
- Neutral summaries of what a tool does without Aleem's experience with it
- Any opening that explains a concept before establishing why it matters to Aleem specifically
- Generic advice that could apply to anyone — anchor to Aleem's specific context
- Filler phrases: "In today's rapidly evolving...", "It's no secret that...", "Game-changer", "Leverage"

VOICE RULES — apply without exception:
- Write as Aleem in first person: "I", "my", "I built", "I tried", "I noticed"
- PUNCTUATION: no em dashes or en dashes (use commas, periods, or short sentences). Use only straight ASCII apostrophes (') and quotes ("), never curly or smart quotes. Smart punctuation corrupts when the text is saved or pasted.
- No emojis for LinkedIn or Blog; maximum 2 emojis for Instagram
- Specific > vague: replace "many companies" with actual numbers from the research data
- Hook first, never bury the lead
- Short sentences. White space. No corporate filler.
- LENGTH DISCIPLINE: hit the target word count in the format spec. At least the minimum, never over the maximum. If you are under the minimum, add another concrete example, data point, or sub-point, never filler. Every sentence must add new information. Do not stop short of the minimum.

ALEEM'S CONTEXT (use this to inform voice — but do NOT name the agency or reference school/university/being-a-student in the output):
- 25-year-old founder building AI automation systems from Islamabad, Pakistan
- Builds real AI systems: multi-agent workflows, automation pipelines, Claude Code extensions
- Runs a real team. Deals with real client constraints.
- Interests beyond tech: Philosophy, Science, Stoicism, History, systems thinking, gym discipline
- Audience: startup founders, tech entrepreneurs, developers, AI-curious builders
- Core message: AI as a business outcome driver, not a tech toy. Chatbots are v1. Agents are v2.
${context ? `\nSOURCE MATERIAL (use facts, quotes, and specifics from this to ground the content — do not summarize it, extract what's useful and make it Aleem's own):\n${context}\n` : ""}
PLATFORM: ${platform}
FORMAT: ${format}
TOPIC: ${topic}

FORMAT SPECIFICATIONS:
${spec}

Write the complete, finished, publish-ready content that meets the minimum word count. Output ONLY the content, no intro like "Here's the post:", no commentary, no markdown wrapper around the piece. Use straight ASCII quotes and apostrophes, and no em dashes.`;
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { topic, platform, format, context, contentMode, selectedPillars } = body as {
      topic: string;
      platform: string;
      format: string;
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

    const anthropicKey = process.env.ANTHROPIC_API_KEY;
    const openaiKey = process.env.OPENAI_API_KEY;

    if (!anthropicKey && !openaiKey) {
      return NextResponse.json(
        { error: "No API keys configured. Set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env.local" },
        { status: 500 }
      );
    }

    const prompt = buildPrompt(platform, format, topic, context, contentMode, selectedPillars);
    const maxTokens = getMaxTokens(platform, format);

    let content = "";
    let usedFallback = false;

    if (anthropicKey) {
      try {
        const anthropic = new Anthropic({ apiKey: anthropicKey });
        const message = await anthropic.messages.create({
          model: "claude-sonnet-4-6",
          max_tokens: maxTokens,
          messages: [{ role: "user", content: prompt }],
        });
        content = message.content[0]?.type === "text" ? message.content[0].text : "";
      } catch (anthropicErr) {
        if (!openaiKey) throw anthropicErr;
        console.warn("Anthropic API failed, falling back to OpenAI:", anthropicErr instanceof Error ? anthropicErr.message : anthropicErr);
        usedFallback = true;
      }
    } else {
      usedFallback = true;
    }

    if (usedFallback && openaiKey) {
      const openai = new OpenAI({ apiKey: openaiKey });
      const completion = await openai.chat.completions.create({
        model: "gpt-5.2",
        max_tokens: Math.max(maxTokens, 2000),
        temperature: 0.8,
        messages: [{ role: "user", content: prompt }],
      });
      content = completion.choices[0]?.message?.content ?? "";
    }

    return NextResponse.json({ content, ...(usedFallback && { provider: "openai" }) });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
