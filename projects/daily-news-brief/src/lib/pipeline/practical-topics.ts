import type { Depth } from "./sources/research";

/**
 * The 9 SMB marketing topics Practical AI rotates through. Each daily brief
 * deep-dives 2 topics (3 on --full): the business problem in plain language,
 * the agentic-AI solution (Claude Code / Claude Cowork / Codex), copy-paste
 * how-to steps, and ready-to-post social content ideas.
 *
 * Topic definitions + queries grounded in the 2026 research pass:
 * research/2026-07-18-how-small-businesses-use-ai-agents-like-claude-code-and-code.md
 * research/2026-07-18-best-practical-ai-marketing-guidance-sources-for-smb-owners.md
 * (Key finding: the strongest sources frame agents around a concrete business
 * outcome, not a tool name — queries below lead with the outcome.)
 */
export interface MarketingTopic {
  name: string;
  slug: string;
  /** Plain-language SMB problem framing, fed straight into the Pass 1 prompt. */
  businessProblem: string;
  /** 1-2 research queries that surface practical, guide-shaped evidence. */
  queries: string[];
  sortOrder: number;
}

export const MARKETING_TOPICS: MarketingTopic[] = [
  {
    name: "Business Overview",
    slug: "business-overview",
    businessProblem:
      "Most small business owners can't articulate their positioning, offer, audience, and numbers in one clear picture, so every marketing decision is built on guesswork.",
    queries: [
      "using AI agents like Claude Code to audit and analyze a small business 2026",
      "AI business plan and positioning analysis workflow for small business",
    ],
    sortOrder: 0,
  },
  {
    name: "Content Automation",
    slug: "content-automation",
    businessProblem:
      "Consistent content across blog and social takes hours per week that owners don't have, so publishing is sporadic and compounding never starts.",
    queries: [
      "how small businesses automate content creation with AI agents Claude Code 2026",
      "AI content automation workflow blog social media small business guide",
    ],
    sortOrder: 1,
  },
  {
    name: "Target Audience",
    slug: "target-audience",
    businessProblem:
      "Most SMBs guess at their ideal customer instead of defining and validating one, so messaging speaks to everyone and lands with no one.",
    queries: [
      "using AI to identify and research target audience ICP small business 2026",
      "AI customer persona research workflow small business how to",
    ],
    sortOrder: 2,
  },
  {
    name: "Market Analysis",
    slug: "market-analysis",
    businessProblem:
      "Competitor and market research is slow manual work, so most small businesses skip it and price, position, and plan blind.",
    queries: [
      "AI agents for competitor analysis and market research small business 2026",
      "automate market research with Claude Code or Codex workflow guide",
    ],
    sortOrder: 3,
  },
  {
    name: "Marketing Goals",
    slug: "marketing-goals",
    businessProblem:
      "Without measurable marketing goals, SMBs mistake activity for progress: posting, boosting, and emailing with no way to know what's working.",
    queries: [
      "setting measurable marketing goals with AI small business framework 2026",
      "AI marketing planning and goal tracking workflow for small business",
    ],
    sortOrder: 4,
  },
  {
    name: "Marketing Strategy",
    slug: "marketing-strategy",
    businessProblem:
      "Most small businesses run tactics without a strategy, spreading a thin budget across channels that never compound into predictable growth.",
    queries: [
      "how small businesses use AI agents to build a marketing strategy 2026",
      "AI generated marketing strategy plan small business step by step",
    ],
    sortOrder: 5,
  },
  {
    name: "Social Media Strategy",
    slug: "social-media-strategy",
    businessProblem:
      "Inconsistent posting with no channel plan means SMB social accounts stall, while owners burn hours making one-off posts that don't convert.",
    queries: [
      "AI social media strategy and content calendar automation small business 2026",
      "automate social media posting and planning with AI agents guide",
    ],
    sortOrder: 6,
  },
  {
    name: "Sales Funnel",
    slug: "sales-funnel",
    businessProblem:
      "Leads leak between first touch and sale because follow-ups depend on the owner remembering; a funnel that runs itself is the fix most SMBs never build.",
    queries: [
      "AI agents automate sales funnel and lead follow up small business 2026",
      "build an automated sales funnel with AI workflow small business",
    ],
    sortOrder: 7,
  },
  {
    name: "KPIs & Reporting",
    slug: "kpis",
    businessProblem:
      "Most SMBs have no dashboard and no tracking, so decisions are made on gut feel; a simple automated KPI report changes every conversation about marketing spend.",
    queries: [
      "track marketing KPIs with AI automated reporting small business 2026",
      "AI marketing analytics dashboard automation for small business guide",
    ],
    sortOrder: 8,
  },
];

/**
 * Deterministic date-keyed rotation: regenerating a past date reproduces its
 * topics. k=2 (lean) steps through all 9 in 5 consecutive days; k=3 (full) in 3.
 */
export function resolveMarketingTopics(date: string, depth: Depth): MarketingTopic[] {
  const k = depth === "full" ? 3 : 2;
  const epochDay = Math.floor(Date.parse(`${date}T00:00:00Z`) / 86_400_000);
  const start = ((epochDay * k) % MARKETING_TOPICS.length + MARKETING_TOPICS.length) % MARKETING_TOPICS.length;
  return Array.from(
    { length: k },
    (_, i) => MARKETING_TOPICS[(start + i) % MARKETING_TOPICS.length]
  );
}
