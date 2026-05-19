export interface ToolCategory {
  name: string;
  slug: string;
  keywords: string[];
  description: string;
  audienceLens: string; // How to frame this category to a business audience
  sortOrder: number;
}

export const TOOL_CATEGORIES: ToolCategory[] = [
  {
    name: "Content Creation",
    slug: "content-creation",
    keywords: [
      "video", "audio", "voice", "script", "copy", "image", "design",
      "thumbnail", "podcast", "music", "song", "music generation",
      "voiceover", "tts", "text-to-speech", "speech", "transcription",
      "subtitle", "caption", "veo", "sora", "runway", "pika", "luma",
      "elevenlabs", "suno", "udio", "midjourney", "dall-e", "stable diffusion",
      "flux", "ideogram", "canva", "capcut", "descript", "opus clip",
      "heygen", "synthesia", "writing", "blog", "article", "newsletter",
      "tweet", "thread", "instagram", "reel", "carousel", "post",
      "creator", "content creator", "youtube", "tiktok",
    ],
    description:
      "AI tools for creating video, audio, scripts, copy, images, and social content. The creator stack.",
    audienceLens:
      "Show business owners and solo operators how they can produce pro-grade content (videos, reels, voiceovers, carousels, blog posts) without hiring a full creative team.",
    sortOrder: 0,
  },
  {
    name: "Outreach & Sales",
    slug: "outreach-sales",
    keywords: [
      "outreach", "cold email", "sales", "crm", "lead", "lead gen",
      "lead generation", "prospect", "prospecting", "personalization",
      "personalized", "icebreaker", "enrichment", "email finder",
      "verify", "linkedin", "sales automation", "outbound", "appointment",
      "calendar", "booking", "scheduling", "warm-up", "deliverability",
      "follow-up", "sequence", "drip", "instantly", "apollo", "lemlist",
      "smartlead", "outreach.io", "hubspot", "pipedrive", "salesforce",
      "clay", "lusha", "zoominfo", "hunter", "snov", "phantombuster",
    ],
    description:
      "Cold email, LinkedIn outreach, CRM, lead enrichment, sales automation, and prospecting tools.",
    audienceLens:
      "Help business owners book more sales calls and qualified leads without burning out — find prospects, write personalized cold emails, manage pipelines, automate follow-ups.",
    sortOrder: 1,
  },
  {
    name: "Agents & Automation",
    slug: "automation-workflows",
    keywords: [
      "agent", "agentic", "ai agent", "autonomous agent", "agent framework",
      "mcp", "mcp server", "model context protocol", "claude code", "codex",
      "codex cli", "cursor", "windsurf", "v0", "bolt.new", "lovable",
      "replit agent", "devin", "smol", "aider", "continue.dev",
      "langchain", "langgraph", "crewai", "autogen", "openai swarm",
      "automation", "workflow", "orchestration", "tool use", "function calling",
      "browser automation", "computer use", "scrape", "scraping",
      "firecrawl", "apify", "browserbase", "stagehand", "playwright",
      "developer tool", "ide", "code assistant", "coding agent",
    ],
    description:
      "Agentic coding tools, MCP servers, autonomous agents, browser automation, and the agent stack.",
    audienceLens:
      "Show business owners how to use agentic tools like Claude Code, Codex, Cursor, and MCP servers to build their own automations, replace manual workflows, and ship internal tools without a developer.",
    sortOrder: 2,
  },
  {
    name: "Productivity & Ops",
    slug: "productivity-ops",
    keywords: [
      "meeting", "transcription", "transcribe", "note", "notetaker",
      "note-taking", "summary", "summarize", "summarizer", "minutes",
      "fathom", "fireflies", "otter", "grain", "tldv", "krisp",
      "project management", "task", "tasks", "kanban", "to-do", "todo",
      "asana", "notion", "linear", "monday", "clickup", "trello",
      "knowledge", "wiki", "second brain", "obsidian", "mem", "reflect",
      "research", "search", "perplexity", "you.com", "consensus",
      "elicit", "scite", "document", "pdf", "spreadsheet", "excel",
      "slides", "presentation", "calendar", "scheduling", "reclaim",
      "motion", "akiflow", "superhuman", "shortwave", "gmail",
    ],
    description:
      "Meeting tools, notetakers, project management, knowledge management, research, and team productivity.",
    audienceLens:
      "Help business owners reclaim hours each week — automate meeting notes, organize knowledge, plan projects, run faster research, and keep their team aligned without endless syncs.",
    sortOrder: 3,
  },
];
