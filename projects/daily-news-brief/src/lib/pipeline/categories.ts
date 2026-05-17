export interface Category {
  name: string;
  slug: string;
  keywords: string[];
  newsApiQuery: string;
  description: string;
  sortOrder: number;
}

export const CATEGORIES: Category[] = [
  {
    name: "AI Models & Breakthroughs",
    slug: "ai-models-breakthroughs",
    keywords: [
      "model release", "benchmark", "paper", "GPT", "Claude", "Gemini",
      "Llama", "open-source model", "fine-tuning", "training", "LLM",
      "large language model", "neural network", "transformer", "diffusion",
      "multimodal", "reasoning", "context window", "tokens", "weights",
      "SOTA", "state of the art", "foundation model", "Mistral", "Grok",
      "DeepSeek", "Qwen",
    ],
    newsApiQuery:
      '"AI model" OR "large language model" OR "GPT" OR "Claude" OR "Gemini" OR "Llama" OR "machine learning research" OR "foundation model"',
    description:
      "New model releases, benchmark results, research papers, architecture breakthroughs, and capability advances.",
    sortOrder: 0,
  },
  {
    name: "AI Tools & Products",
    slug: "ai-tools-products",
    keywords: [
      "AI tool", "product launch", "API", "developer tool", "IDE",
      "copilot", "assistant", "app", "plugin", "extension", "chatbot",
      "AI feature", "integration", "SDK", "platform", "SaaS", "AI-powered",
      "cursor", "windsurf", "v0", "bolt", "replit",
    ],
    newsApiQuery:
      '"AI tool" OR "AI product" OR "AI launch" OR "AI assistant" OR "AI app" OR "developer tool" OR "AI API"',
    description:
      "New AI tools, product launches, feature releases, and developer platforms people can actually use.",
    sortOrder: 1,
  },
  {
    name: "AI Business & Strategy",
    slug: "ai-business-strategy",
    keywords: [
      "funding", "acquisition", "Series A", "Series B", "Series C",
      "revenue", "IPO", "partnership", "strategy", "valuation",
      "venture capital", "investment", "startup funding", "billion",
      "OpenAI", "Anthropic", "Google AI", "Microsoft AI", "Meta AI",
      "Apple AI", "Amazon AI", "compete", "market share",
    ],
    newsApiQuery:
      '"AI funding" OR "AI acquisition" OR "AI investment" OR "OpenAI" OR "Anthropic" OR "Google AI" OR "Microsoft AI" OR "AI startup"',
    description:
      "Funding rounds, acquisitions, big tech AI strategy, partnerships, and market dynamics.",
    sortOrder: 2,
  },
  {
    name: "AI Automation & Workflows",
    slug: "ai-automation-workflows",
    keywords: [
      "agent", "MCP", "Claude Code", "Codex", "Cursor", "workflow", "automation",
      "orchestration", "agentic", "tool use", "function calling",
      "AI agent", "autonomous", "multi-agent", "crew", "langchain",
      "langgraph", "autogen", "coding agent", "browser agent", "computer use",
    ],
    newsApiQuery:
      '"AI agent" OR "AI automation" OR "agentic AI" OR "workflow automation" OR "AI workflow" OR "MCP" OR "function calling"',
    description:
      "AI agents, automation frameworks, workflow tools, MCP, and the agentic AI ecosystem.",
    sortOrder: 3,
  },
  {
    name: "AI Content & Creator Economy",
    slug: "ai-content-creators",
    keywords: [
      "creator", "content", "YouTube", "tutorial", "course", "community",
      "build", "maker", "indie", "newsletter", "blog", "social media",
      "influencer", "AI-generated", "video", "image generation", "voice",
      "music", "creative AI", "writing", "copywriting", "Midjourney",
      "DALL-E", "Sora", "Runway", "ElevenLabs",
    ],
    newsApiQuery:
      '"AI content" OR "AI creator" OR "AI video" OR "AI image" OR "generative AI" OR "creative AI" OR "AI writing"',
    description:
      "What creators and builders are doing with AI, content generation tools, and the creator economy.",
    sortOrder: 4,
  },
  {
    name: "AI Ethics, Safety & Regulation",
    slug: "ai-ethics-safety",
    keywords: [
      "safety", "alignment", "regulation", "policy", "governance", "bias",
      "risk", "EU AI Act", "executive order", "copyright", "deepfake",
      "responsible AI", "transparency", "audit", "compliance", "lawsuit",
      "ban", "restriction", "privacy", "surveillance", "misinformation",
    ],
    newsApiQuery:
      '"AI regulation" OR "AI safety" OR "AI policy" OR "AI ethics" OR "AI governance" OR "EU AI Act" OR "AI bias"',
    description:
      "AI safety research, regulation, policy moves, ethics debates, and governance frameworks.",
    sortOrder: 5,
  },
];
