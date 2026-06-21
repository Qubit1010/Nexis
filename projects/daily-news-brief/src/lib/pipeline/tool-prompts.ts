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
  const sig: string[] = [];
  if (item.engagementScore) sig.push(`${item.engagementScore} upvotes/likes`);
  if (item.commentCount) sig.push(`${item.commentCount} comments`);
  if (item.sourceCount && item.sourceCount > 1) sig.push(`${item.sourceCount} sources`);
  if (sig.length) line += ` [${sig.join(", ")}]`;
  if (item.tool) line += `\n   About tool: ${item.tool}`;
  if (item.description) line += `\n   Detail: ${item.description.slice(0, 400)}`;
  line += `\n   URL: ${item.url}`;
  return line;
}

export function buildToolAnalysisPrompt(
  categoryName: string,
  audienceLens: string,
  items: PracticalItem[]
): string {
  const evidence = items.map((t, i) => formatEvidenceForPrompt(t, i)).join("\n\n");

  return `You are a hands-on AI operator who teaches small business owners how to actually USE AI tools to solve real business problems. Your audience is SMB owners, founders, freelancers, and operators - not engineers chasing news.

You are looking at recent updates, releases, and community discussions in the "${categoryName}" domain. Your job is to extract the TOOLS and WORKFLOWS worth using, and exactly how to apply them.

AUDIENCE LENS: ${audienceLens}

EVIDENCE (updates + discussions):
${evidence}

INSTRUCTIONS:
1. Write a 2-3 sentence "summary" of what's genuinely new or useful in this domain right now and why an SMB owner should care.
2. Pick the SINGLE BEST tool/workflow in this domain for a business audience and put it in "bestInDomain":
   - "name" MUST match one of the tool names you return below
   - "reason" must be 1-2 sentences explaining WHY this beats the rest (specific advantage, not generic praise)
   - If there is genuinely nothing useful in this batch, set bestInDomain to null.
3. The evidence is discussions/updates, NOT a product list - so EXTRACT and NAME the actual tool or workflow being discussed. For each one worth surfacing, produce:
   - originalIndex (the idx of the evidence item it came from)
   - name (clean tool or workflow name, e.g. "Claude Code", "n8n + Apollo workflow")
   - oneLiner: a crisp single sentence in plain English - what it is / what's new
   - bestUseCase: 1-2 sentences naming WHO should use it and for WHAT specific business outcome in this domain
   - howToSteps: EXACTLY 3 short, concrete steps to apply it to a business problem today. Include URLs, commands, or first-prompt examples where possible.
   - audienceHook: ONE social-ready opening line (no em dashes, use plain hyphens)
   - pricingTier: "free", "freemium", "paid", or "unknown"
   - tags: 2-4 short tags
   - relevanceScore: 1-10 - how useful for a typical SMB owner solving a ${categoryName.toLowerCase()} problem? Penalize hype, pure news with no actionable use, and engineer-only minutiae.
4. Skip items that are just news, drama, or that you cannot turn into a concrete business use. Deduplicate tools mentioned across multiple evidence items into one card.
5. Order by relevanceScore descending. Cap at 6 cards per domain.

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
      `- "${t.name}" (relevance: ${t.relevanceScore}/10${t.upvotes ? `, ${t.upvotes} upvotes` : ""})\n  ${t.oneLiner}\n  Use case: ${t.bestUseCase}`
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

  return `You are the strategic advisor behind "Practical AI" - a daily brief that teaches small business owners how to use AI tools and workflows to solve real business problems. Today is ${date}. Below are tools and workflows surfaced across 4 business-problem domains (Marketing, Sales, Managing & Scaling, Online Presence), each with a "best in domain" pick. Your job is to synthesize a practical, builder-minded brief - what to actually use and how.

${categorySummaries}
${moversBlock}

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
