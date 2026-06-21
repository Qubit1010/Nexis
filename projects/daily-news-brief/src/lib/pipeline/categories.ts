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
    name: "AI Business & Strategy",
    slug: "ai-business-strategy",
    keywords: [
      "funding", "acquisition", "Series A", "Series B", "Series C",
      "revenue", "IPO", "partnership", "strategy", "valuation",
      "venture capital", "investment", "startup funding", "billion",
      "OpenAI", "Anthropic", "Google AI", "Microsoft AI", "Meta AI",
      "Apple AI", "Amazon AI", "DeepMind", "compete", "market share",
      "hire", "talent", "lab", "datacenter", "chips", "Nvidia",
    ],
    newsApiQuery:
      '"AI funding" OR "AI acquisition" OR "AI investment" OR "OpenAI" OR "Anthropic" OR "Google AI" OR "Microsoft AI" OR "AI startup"',
    description:
      "Funding rounds, acquisitions, big-lab strategy, talent moves, partnerships, and market dynamics across the AI industry.",
    sortOrder: 1,
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
    sortOrder: 2,
  },
];
