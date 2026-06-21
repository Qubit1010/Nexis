/**
 * Curated daily theme list for the "AI industry intel" news sweep.
 *
 * Scope is deliberately INDUSTRY news — frontier models, research breakthroughs,
 * big-lab moves, funding/M&A, regulation, and safety/ethics. Practical tooling
 * ("how to use Claude Code / agents for business") lives in the separate
 * Practical AI vertical, not here. Each theme is a search phrase handed to the
 * last30days engine; the keyword categorizer (see `categories.ts`) then buckets
 * results into the display categories. Themes drive WHAT is fetched; categories
 * drive HOW it is displayed.
 *
 * `coversCategories` is documentation only (which category slugs each theme is
 * expected to feed) — it is not used for routing.
 */
export interface DailyTheme {
  topic: string;
  coversCategories: string[];
}

export const DAILY_THEMES: DailyTheme[] = [
  {
    topic: "frontier AI model releases and benchmark results",
    coversCategories: ["ai-models-breakthroughs"],
  },
  {
    topic: "AI research breakthroughs and new papers",
    coversCategories: ["ai-models-breakthroughs"],
  },
  {
    topic: "OpenAI Anthropic Google DeepMind Meta AI strategy and moves",
    coversCategories: ["ai-business-strategy", "ai-models-breakthroughs"],
  },
  {
    topic: "AI funding rounds, acquisitions and valuations",
    coversCategories: ["ai-business-strategy"],
  },
  {
    topic: "AI regulation, policy and government action",
    coversCategories: ["ai-ethics-safety"],
  },
  {
    topic: "AI safety, alignment and ethics debates",
    coversCategories: ["ai-ethics-safety"],
  },
];

export const DEFAULT_DAILY_TOPICS: string[] = DAILY_THEMES.map((t) => t.topic);
