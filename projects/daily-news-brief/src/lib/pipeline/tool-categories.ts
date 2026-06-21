export interface ToolCategory {
  name: string;
  slug: string;
  keywords: string[];
  description: string;
  /** How to frame this domain to an SMB audience. */
  audienceLens: string;
  /** Business-problem search phrases handed to the engine for this domain. */
  problemQueries: string[];
  sortOrder: number;
}

// Practical AI domains = the four business problems Aleem's agency helps SMBs
// solve with AI tools + workflows. Evidence (engine articles, tool updates) is
// bucketed into these domains; "keywords" drive the keyword fallback in the
// categorizer, "problemQueries" seed the per-domain engine fetch.
export const TOOL_CATEGORIES: ToolCategory[] = [
  {
    name: "Marketing",
    slug: "marketing",
    keywords: [
      "marketing", "content marketing", "seo", "ads", "advertising",
      "social media", "email marketing", "newsletter", "copywriting", "copy",
      "brand", "branding", "campaign", "blog", "carousel", "reel", "video",
      "image generation", "thumbnail", "creative", "canva", "capcut", "veo",
      "sora", "runway", "midjourney", "elevenlabs", "heygen", "opus clip",
      "hootsuite", "buffer", "jasper", "copy.ai", "writesonic", "audience",
    ],
    description:
      "AI tools and workflows for content marketing, SEO, ads, social, email, and creative production.",
    audienceLens:
      "Show SMB owners which AI tools and agent workflows let them run marketing (content, SEO, ads, email, creative) at agency quality without an agency budget.",
    problemQueries: [
      "AI tools for content marketing and SEO",
      "AI workflow to generate social media content",
      "AI for email marketing and ad copy",
    ],
    sortOrder: 0,
  },
  {
    name: "Sales",
    slug: "sales",
    keywords: [
      "sales", "outreach", "cold email", "cold outreach", "lead", "lead gen",
      "lead generation", "prospect", "prospecting", "crm", "pipeline",
      "personalization", "icebreaker", "enrichment", "email finder",
      "deliverability", "follow-up", "sequence", "outbound", "appointment",
      "booking", "closing", "deal", "instantly", "apollo", "lemlist",
      "smartlead", "clay", "hubspot", "pipedrive", "salesforce", "phantombuster",
    ],
    description:
      "AI tools and workflows for outreach, lead generation, CRM, prospecting, and closing deals.",
    audienceLens:
      "Help SMB owners book more qualified calls and close more deals: find prospects, personalize cold outreach at scale, manage pipeline, and automate follow-ups with AI.",
    problemQueries: [
      "AI cold outreach and lead generation tools",
      "AI workflow to personalize sales emails at scale",
      "AI CRM and pipeline automation for sales",
    ],
    sortOrder: 1,
  },
  {
    name: "Managing & Scaling",
    slug: "managing-scaling",
    keywords: [
      "operations", "ops", "automation", "workflow", "agent", "agentic",
      "ai agent", "mcp", "mcp server", "claude code", "codex", "cursor",
      "n8n", "make", "zapier", "langgraph", "crewai", "orchestration",
      "project management", "task", "delegation", "hiring", "onboarding",
      "internal tool", "reporting", "dashboard", "back office", "process",
      "sop", "knowledge", "notion", "linear", "airtable", "scale", "scaling",
    ],
    description:
      "AI agents and automations that run back-office operations, internal tooling, reporting, and let a small team scale.",
    audienceLens:
      "Show SMB owners how to use Claude Code, Codex, MCP servers, and automation tools to replace manual operations, build internal tools without a developer, and scale without scaling headcount.",
    problemQueries: [
      "AI agents to automate business operations",
      "Claude Code and MCP for internal business tools",
      "AI workflow automation to scale a small team",
    ],
    sortOrder: 2,
  },
  {
    name: "Online Presence",
    slug: "online-presence",
    keywords: [
      "personal brand", "personal branding", "website", "portfolio", "landing page",
      "web design", "framer", "webflow", "wordpress", "shopify", "no-code",
      "social presence", "linkedin", "x", "twitter", "instagram", "thought leadership",
      "reputation", "community", "audience building", "profile", "bio", "seo",
      "domain", "hosting", "site builder", "presence", "online presence",
    ],
    description:
      "AI tools and workflows for building a website, personal brand, social presence, and online reputation.",
    audienceLens:
      "Help SMB owners and founders build a credible online presence: ship a website, grow a personal brand, and show up consistently on social with AI doing the heavy lifting.",
    problemQueries: [
      "AI tools to build a website or landing page fast",
      "AI for personal brand and LinkedIn presence",
      "AI workflow to build online presence for founders",
    ],
    sortOrder: 3,
  },
];
