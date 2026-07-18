import type { PracticalItem, Mover } from "./sources/practical-index";

export interface ToolAnalysisResult {
  summary: string;
  bestInDomain: {
    name: string; // must match one of the tool names returned below
    reason: string; // why this beats the others
  } | null;
  tools: Array<{
    originalIndex: number;
    name: string;
    oneLiner: string;
    bestUseCase: string;
    howToSteps: string[];
    audienceHook: string;
    pricingTier: "free" | "freemium" | "paid" | "unknown";
    tags: string[];
    relevanceScore: number;
  }>;
}

export interface ToolSynthesisResult {
  topPick: {
    name: string;
    why: string;
  };
  trends: Array<{
    title: string;
    slug: string;
    summary: string;
    toolNames: string[];
    contentPotential: number;
  }>;
  contentIdeas: Array<{
    title: string;
    angle: string;
    format: "tutorial" | "carousel" | "reel" | "thread" | "blog";
    hook: string;
    keyPoints: string[];
    relatedToolNames: string[];
  }>;
  workflowRecipe: {
    title: string;
    subtitle: string;
    scenario: string;
    agent: string;
    toolsUsed: string[];
    steps: Array<{
      step: string;
      commandOrPrompt: string;
      expectedOutcome: string;
    }>;
    timeSaved: string;
    difficulty: "beginner" | "intermediate" | "advanced";
    audienceHook: string;
  };
  crossDomainInsight: string;
}

function formatEvidenceForPrompt(item: PracticalItem, i: number): string {
  let line = `${i + 1}. [idx:${i}] "${item.title}" (${item.source})`;
  if (item.sourceCount && item.sourceCount > 1)
    line += ` [corroborated by ${item.sourceCount} search engines]`;
  if (item.description) line += `\n   Detail: ${item.description.slice(0, 400)}`;
  line += `\n   URL: ${item.url}`;
  return line;
}

export function buildToolAnalysisPrompt(
  topicName: string,
  businessProblem: string,
  items: PracticalItem[]
): string {
  const evidence = items.map((t, i) => formatEvidenceForPrompt(t, i)).join("\n\n");

  return `You are a hands-on AI operator writing the "${topicName}" section of Practical AI - a daily brief that teaches small business owners how AGENTIC AI (Claude Code, Claude Cowork, Codex, and similar agents) solves real marketing problems. Your audience is SMB owners, founders, freelancers, and operators - not engineers chasing news. The mission: show AI solving basic business problems practically, so people learn to use it instead of fearing it.

THE BUSINESS PROBLEM THIS SECTION SOLVES:
${businessProblem}

EVIDENCE (guides, tutorials, case studies, discussions from the last week):
${evidence}

INSTRUCTIONS:
1. Write a 2-3 sentence "summary": restate the business problem in plain language, then what the evidence says is now possible or changing for an owner facing it.
2. Pick the SINGLE BEST solution for a business audience and put it in "bestInDomain":
   - "name" MUST match one of the solution names you return below
   - "reason" must be 1-2 sentences explaining WHY this beats the rest (specific advantage, not generic praise)
   - If there is genuinely nothing useful in this batch, set bestInDomain to null.
3. The evidence is articles/guides, NOT a product list - so EXTRACT and NAME each concrete SOLUTION: a workflow or setup an owner can run this week. For each one worth surfacing, produce:
   - originalIndex (the idx of the evidence item it came from)
   - name: the agentic solution, named by outcome (e.g. "Claude Code weekly content calendar agent", "Codex competitor-audit workflow") - every card must be powered by Claude Code, Claude Cowork, Codex, or an agentic tool named in the evidence
   - oneLiner: a crisp single sentence in plain English - what it does for the business
   - bestUseCase: 1-2 sentences naming WHO should use it and WHAT specific ${topicName.toLowerCase()} outcome they get
   - howToSteps: EXACTLY 3 short, concrete, copy-paste steps to apply it today. Wherever possible include the literal first prompt to paste into the agent, the command to run, or the URL to start from.
   - audienceHook: ONE social-ready opening line showing AI solving this problem practically (no em dashes, use plain hyphens)
   - pricingTier: "free", "freemium", "paid", or "unknown"
   - tags: 2-4 short tags
   - relevanceScore: 1-10 - how useful for a typical SMB owner solving this ${topicName.toLowerCase()} problem? Penalize hype, pure news with no actionable use, engineer-only minutiae, and anything that is just a GitHub repo or issue thread with no business application.
4. Skip items that are just news, drama, or that you cannot turn into a concrete business use. Deduplicate the same solution across multiple evidence items into one card.
5. Order by relevanceScore descending. Cap at 6 cards per topic.

Return your response as valid JSON with this exact structure:
{
  "summary": "...",
  "bestInDomain": { "name": "Exact Tool Name", "reason": "..." },
  "tools": [
    {
      "originalIndex": 0,
      "name": "Tool Name",
      "oneLiner": "...",
      "bestUseCase": "...",
      "howToSteps": ["step 1", "step 2", "step 3"],
      "audienceHook": "...",
      "pricingTier": "free|freemium|paid|unknown",
      "tags": ["tag1", "tag2"],
      "relevanceScore": 8
    }
  ]
}

IMPORTANT:
- Return ONLY valid JSON, no markdown code fences or extra text.
- howToSteps MUST be exactly 3 items.
- Never use em dashes — use plain hyphens, commas, or colons instead (this content goes into Google Sheets which corrupts em dashes).
- Be opinionated. Skip generic praise.
- "bestInDomain.name" MUST exactly match one of the tool names in your "tools" array.`;
}

export function buildToolsSynthesisPrompt(
  categoryResults: Array<{
    categoryName: string;
    categorySlug: string;
    summary: string;
    bestInDomain: { name: string; reason: string } | null;
    tools: Array<{
      name: string;
      oneLiner: string;
      bestUseCase: string;
      audienceHook: string;
      relevanceScore: number;
    }>;
  }>,
  date: string,
  movers: Mover[] = []
): string {
  const categorySummaries = categoryResults
    .map(
      (cat) => `
### ${cat.categoryName} (${cat.tools.length} tools)
**Summary:** ${cat.summary}
**Best in domain:** ${cat.bestInDomain ? `${cat.bestInDomain.name} - ${cat.bestInDomain.reason}` : "(none)"}
**Top tools:**
${cat.tools
  .slice(0, 5)
  .map(
    (t) =>
      `- "${t.name}" (relevance: ${t.relevanceScore}/10)\n  ${t.oneLiner}\n  Use case: ${t.bestUseCase}`
  )
  .join("\n")}`
    )
    .join("\n");

  const moversBlock = movers.length
    ? `\nWHAT'S SURGING RIGHT NOW (GitHub trending + new models):\n${movers
        .slice(0, 12)
        .map((m) => `- ${m.name} (${m.signal})${m.blurb ? ` - ${m.blurb}` : ""}`)
        .join("\n")}\n`
    : "";

  const topicNames = categoryResults.map((c) => c.categoryName).join(", ");

  return `You are the strategic advisor behind "Practical AI" - a daily brief that teaches small business owners how AGENTIC AI (Claude Code, Claude Cowork, Codex) solves real marketing problems. Today is ${date}. Today's brief covers these marketing topics: ${topicNames}. Each section below has agentic solutions for its business problem, with a "best in domain" pick. Your job is to synthesize a practical, builder-minded brief - what to actually use and how - and above all, content the reader (Aleem) can publish to attract SMB clients.

${categorySummaries}
${moversBlock}

PRODUCE THE FOLLOWING:

1. **TOP PICK**: The single best solution of the day across today's topics. Name + 2-3 sentences explaining why it beats the rest, who it's for, what outcome it enables. This should USUALLY be one of the "best in domain" picks but you can override if a runner-up is clearly stronger.

2. **TRENDS** (3-5): Cross-topic trends you see in today's solutions. For each:
   - title: short, punchy name
   - slug: kebab-case
   - summary: 2-3 sentences explaining the trend and its business implication
   - toolNames: which specific solution names from above support this trend
   - contentPotential: 1-10 — how good would this be as content?

3. **CONTENT IDEAS** (exactly 8) — THE FLAGSHIP DELIVERABLE: Ready-to-publish content angles Aleem posts on LinkedIn/Instagram to attract SMB clients. Every idea follows the arc: real business problem -> agentic-AI solution -> concrete result. The goal is showing AI solving problems practically so people learn to use it instead of hating it. Rules:
   - At least 2 must be "tutorial" format (step-by-step how-to using one specific solution)
   - At least 1 must be "carousel" (Instagram, 5-7 slides)
   - At least 1 must be "reel" (short-form video script)
   - Each idea must name AT LEAST one specific solution from above
   - At least half the ideas must map directly to today's topics (${topicNames})
   - Every angle must be specific and actionable. No filler.

   For each idea:
   - title, angle, format, hook, keyPoints (3-5), relatedToolNames

4. **WORKFLOW RECIPE OF THE DAY**: A practical, ready-to-execute workflow that solves ONE of today's topics (${topicNames}) end-to-end using Claude Code, Claude Cowork, Codex, Cursor, or an MCP server. This is the centrepiece. Pretend Aleem is going to record a 5-minute video walking through this tomorrow.

   - title: Punchy name (e.g. "Build a Weekly Client Report Bot with Claude Code in 20 Minutes")
   - subtitle: One-line "what you'll have at the end"
   - scenario: 2-3 sentences — what business problem this solves and who it's for (freelancers? agency owners? solopreneurs?)
   - agent: Which agent powers this — "Claude Code" / "Codex CLI" / "Cursor" / "MCP server" / "Custom agent" / etc.
   - toolsUsed: Array of tool names (mix of today's tools and standard tools like Google Sheets, Gmail, Notion)
   - steps: 4-6 step objects. Each step has:
       - step: short instruction (e.g. "Install the MCP server")
       - commandOrPrompt: the actual command, prompt, or config snippet to paste (e.g. "claude mcp add ..." or a literal Claude Code prompt the user would type)
       - expectedOutcome: 1 sentence describing what happens after this step
   - timeSaved: realistic estimate (e.g. "~2 hours/week" or "30 min per client")
   - difficulty: "beginner" / "intermediate" / "advanced"
   - audienceHook: One social-ready line Aleem could open a post or reel with

5. **CROSS DOMAIN INSIGHT**: ONE sentence. If a business owner reads only one thing from today's tools brief, what should they take away?

Return your response as valid JSON with this exact structure:
{
  "topPick": { "name": "Tool Name", "why": "..." },
  "trends": [
    { "title": "...", "slug": "...", "summary": "...", "toolNames": ["..."], "contentPotential": 8 }
  ],
  "contentIdeas": [
    { "title": "...", "angle": "...", "format": "tutorial|carousel|reel|thread|blog", "hook": "...", "keyPoints": ["..."], "relatedToolNames": ["..."] }
  ],
  "workflowRecipe": {
    "title": "...",
    "subtitle": "...",
    "scenario": "...",
    "agent": "Claude Code",
    "toolsUsed": ["..."],
    "steps": [
      { "step": "...", "commandOrPrompt": "...", "expectedOutcome": "..." }
    ],
    "timeSaved": "...",
    "difficulty": "beginner|intermediate|advanced",
    "audienceHook": "..."
  },
  "crossDomainInsight": "..."
}

IMPORTANT:
- Return ONLY valid JSON, no markdown code fences or extra text.
- Never use em dashes — use plain hyphens, commas, or colons instead.
- The workflowRecipe.steps[].commandOrPrompt MUST be literal text the user can copy and paste — actual prompts, actual CLI commands, actual config snippets. Not abstract descriptions.
- If today's tools don't directly fit a Claude Code workflow, build the recipe around Claude Code + a standard tool (Google Sheets, Gmail, Notion, Linear) and reference today's tools where they help.
- Every content idea and the workflow recipe must be something Aleem can actually post or build in the next 24 hours.`;
}
