import type { RawTool } from "./sources/tool-types";

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

function formatToolForPrompt(t: RawTool, i: number): string {
  let line = `${i + 1}. [idx:${i}] "${t.name}" (${t.source})`;
  if (t.upvotes) line += ` [${t.upvotes} upvotes/likes]`;
  line += `\n   Tagline: ${t.tagline || "(none)"}`;
  if (t.description && t.description !== t.tagline) {
    line += `\n   Description: ${t.description.slice(0, 400)}`;
  }
  line += `\n   URL: ${t.url}`;
  return line;
}

export function buildToolAnalysisPrompt(
  categoryName: string,
  audienceLens: string,
  tools: RawTool[]
): string {
  const toolList = tools.map((t, i) => formatToolForPrompt(t, i)).join("\n\n");

  return `You are a hands-on AI operator who teaches business owners how to actually use new AI tools. You write for a content creator whose audience is small business owners, founders, freelancers, and operators who want to use AI to grow their business.

You are reviewing today's new AI tools in the "${categoryName}" category.

AUDIENCE LENS: ${audienceLens}

TOOLS TO REVIEW:
${toolList}

INSTRUCTIONS:
1. Write a 2-3 sentence "summary" of what's new in this domain today and why a business owner should care.
2. Pick the SINGLE BEST tool in this domain for a business audience and put it in "bestInDomain":
   - "name" MUST match one of the tool names you return below
   - "reason" must be 1-2 sentences explaining WHY this beats the rest (specific advantage, not generic praise)
   - If there is genuinely nothing useful in this batch, set bestInDomain to null.
3. For each tool you keep, produce:
   - originalIndex (the idx number from the listing)
   - name (clean tool name)
   - oneLiner: a crisp single sentence in plain English (no marketing fluff)
   - bestUseCase: 1-2 sentences naming WHO should use it and for WHAT specific business outcome
   - howToSteps: EXACTLY 3 short, concrete steps to start using it today. Include URLs, signup actions, first-prompt examples where possible.
   - audienceHook: ONE social-ready opening line (no em dashes, use plain hyphens)
   - pricingTier: "free", "freemium", "paid", or "unknown"
   - tags: 2-4 short tags
   - relevanceScore: 1-10 — how useful for a typical business owner? Penalize toys, duplicates of well-known tools, and overly technical-only releases.
4. Skip tools that are toys, vapourware, or that you cannot describe usefully. Return only the tools worth surfacing.
5. Order tools by relevanceScore descending. Cap at 6 tools per category.

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
      upvotes?: number;
    }>;
  }>,
  date: string
): string {
  const categorySummaries = categoryResults
    .map(
      (cat) => `
### ${cat.categoryName} (${cat.tools.length} tools)
**Summary:** ${cat.summary}
**Best in domain:** ${cat.bestInDomain ? `${cat.bestInDomain.name} — ${cat.bestInDomain.reason}` : "(none)"}
**Top tools:**
${cat.tools
  .slice(0, 5)
  .map(
    (t) =>
      `- "${t.name}" (relevance: ${t.relevanceScore}/10${t.upvotes ? `, ${t.upvotes} upvotes` : ""})\n  ${t.oneLiner}\n  Use case: ${t.bestUseCase}`
  )
  .join("\n")}`
    )
    .join("\n");

  return `You are a strategic content advisor for a business-facing AI content creator named Aleem. Today is ${date}. Below are new AI tools categorized across 4 business operations domains. Each domain has a chosen "best in domain" tool. Your job is to synthesize this into a daily "AI tools for business" brief that helps Aleem teach his audience.

${categorySummaries}

PRODUCE THE FOLLOWING:

1. **TOP PICK**: The single best tool of the day across ALL 4 domains. Name + 2-3 sentences explaining why it beats every other tool today, who it's for, what outcome it enables. This should USUALLY be one of the "best in domain" picks but you can override if a runner-up is clearly stronger.

2. **TRENDS** (3-5): Cross-domain trends you see in today's tools. For each:
   - title: short, punchy name
   - slug: kebab-case
   - summary: 2-3 sentences explaining the trend and its business implication
   - toolNames: which specific tool names from above support this trend
   - contentPotential: 1-10 — how good would this be as content?

3. **CONTENT IDEAS** (exactly 8): Ready-to-publish content angles for Aleem's audience. Rules:
   - At least 2 must be "tutorial" format (step-by-step how-to using one specific tool)
   - At least 1 must be "carousel" (Instagram, 5-7 slides)
   - At least 1 must be "reel" (short-form video script)
   - Each idea must name AT LEAST one specific tool from above
   - Cover at least 3 of the 4 domains across the 8 ideas
   - Every angle must be specific and actionable. No filler.

   For each idea:
   - title, angle, format, hook, keyPoints (3-5), relatedToolNames

4. **WORKFLOW RECIPE OF THE DAY**: A practical, ready-to-execute workflow that uses Claude Code, Codex, Cursor, an MCP server, or an agentic coding agent — combined with 1-2 of today's tools when possible — to automate a real business task. This is the centrepiece. Pretend Aleem is going to record a 5-minute video walking through this tomorrow.

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
