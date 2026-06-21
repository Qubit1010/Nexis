import type { RawArticle } from "./sources/types";

interface ArticleInput {
  title: string;
  description: string;
  source: string;
  engagementScore?: number;
  commentCount?: number;
  sourceCount?: number;
}

export interface Pass1Result {
  insight: string;
  articles: Array<{
    originalIndex: number;
    title: string;
    tldr: string;
    sentimentTag: "excited" | "neutral" | "concerned" | "skeptical";
    relevanceScore: number;
  }>;
  emergingThemes: string[];
}

export interface SynthesisResult {
  trends: Array<{
    title: string;
    slug: string;
    summary: string;
    momentumSignal: "rising" | "steady" | "cooling";
    categories: string[];
    sourceCount: number;
    contentPotentialScore: number;
  }>;
  overallSentiment: {
    label: "bullish" | "cautious" | "mixed" | "bearish";
    summary: string;
  };
  topTakeaway: string;
}

function formatArticleForPrompt(a: ArticleInput, i: number): string {
  let line = `${i + 1}. [idx:${i}] "${a.title}" (${a.source})`;
  if (a.engagementScore) line += ` [${a.engagementScore} upvotes]`;
  if (a.commentCount) line += ` [${a.commentCount} comments]`;
  if (a.sourceCount && a.sourceCount > 1)
    line += ` [covered by ${a.sourceCount} sources]`;
  line += `\n   ${a.description}`;
  return line;
}

export function buildPass1Prompt(
  categoryName: string,
  categoryDescription: string,
  articles: ArticleInput[]
): string {
  const articleList = articles
    .map((a, i) => formatArticleForPrompt(a, i))
    .join("\n\n");

  return `You are a senior AI industry analyst writing a daily intelligence brief for an operator who runs an AI automation agency and needs to stay current on where the industry is heading. Analyze the following articles for the category "${categoryName}" (${categoryDescription}).

ARTICLES:
${articleList}

INSTRUCTIONS:
1. Write a 2-3 sentence "So What?" insight identifying the overarching trend or theme. Be opinionated, forward-looking, and specific. What does this signal about where the AI industry is going?
2. For each article, provide:
   - The originalIndex (the number after [idx:] in the article listing)
   - A 1-2 sentence TL;DR capturing the key takeaway
   - A sentiment tag: "excited" (positive/optimistic), "neutral" (factual/informational), "concerned" (cautious/worried), or "skeptical" (doubtful/critical)
   - A relevance score from 1-10 (how important is this for understanding where the AI industry is heading?)
3. Identify 2-3 emerging themes or keywords you see across these articles.

${engagementContext(articles)}

Return your response as valid JSON with this exact structure:
{
  "insight": "Your 2-3 sentence trend analysis here",
  "articles": [
    { "originalIndex": 0, "title": "Exact article title from input", "tldr": "1-2 sentence summary", "sentimentTag": "excited|neutral|concerned|skeptical", "relevanceScore": 8 }
  ],
  "emergingThemes": ["theme1", "theme2", "theme3"]
}

IMPORTANT:
- Return ONLY valid JSON, no markdown code fences or extra text
- Keep article titles exactly as provided
- Include the originalIndex for each article (the idx number from the listing)
- Order articles by relevance score (highest first)
- Be specific — avoid generic statements like "AI is growing"
- Consider engagement signals (upvotes, comments) as indicators of community interest`;
}

function engagementContext(articles: ArticleInput[]): string {
  const withEngagement = articles.filter((a) => a.engagementScore);
  if (withEngagement.length === 0) return "";
  return `NOTE: Some articles include engagement metrics (upvotes, comments) from Hacker News. Higher engagement = more community interest. Factor this into your relevance scoring.`;
}

export function buildSynthesisPrompt(
  categoryResults: Array<{
    categoryName: string;
    categorySlug: string;
    insight: string;
    emergingThemes: string[];
    articleCount: number;
    topArticles: Array<{
      title: string;
      tldr: string;
      sentimentTag: string;
      relevanceScore: number;
      engagementScore?: number;
    }>;
  }>,
  date: string
): string {
  const categorySummaries = categoryResults
    .map(
      (cat) => `
### ${cat.categoryName} (${cat.articleCount} articles)
**Insight:** ${cat.insight}
**Themes:** ${cat.emergingThemes.join(", ")}
**Top stories:**
${cat.topArticles
  .slice(0, 5)
  .map(
    (a) =>
      `- "${a.title}" (${a.sentimentTag}, relevance: ${a.relevanceScore}/10${a.engagementScore ? `, ${a.engagementScore} upvotes` : ""})\n  ${a.tldr}`
  )
  .join("\n")}`
    )
    .join("\n");

  return `You are a strategic AI industry analyst. Today is ${date}. Below are analyzed summaries from ${categoryResults.length} AI/tech news categories. Your job is to synthesize this into a sharp daily intelligence read for an operator who runs an AI automation agency and needs to understand where the industry is moving — what the big labs are doing, what is being funded, and how policy/safety is shifting. This is industry awareness, NOT a content plan.

${categorySummaries}

PRODUCE THE FOLLOWING:

1. **TRENDS** (exactly 5): Cross-category industry developments you see emerging. For each:
   - Title: short, punchy name
   - Slug: kebab-case version
   - Summary: 2-3 sentences explaining the development and why it matters for the industry
   - Momentum: "rising" (accelerating), "steady" (ongoing), or "cooling" (fading)
   - Categories: which category slugs this trend spans
   - Source count: how many distinct stories feed this trend
   - Content potential score: 1-10 rating of how significant/noteworthy this development is

2. **OVERALL SENTIMENT**: What's the AI industry feeling like today?
   - Label: "bullish" (excited/optimistic), "cautious" (careful/measured), "mixed" (split opinions), or "bearish" (worried/negative)
   - Summary: 2-3 sentences capturing the mood

3. **TOP TAKEAWAY**: One sentence. If the reader sees nothing else today, what should they know about the state of the AI industry?

Return your response as valid JSON with this exact structure:
{
  "trends": [
    { "title": "...", "slug": "...", "summary": "...", "momentumSignal": "rising|steady|cooling", "categories": ["slug1", "slug2"], "sourceCount": 5, "contentPotentialScore": 8 }
  ],
  "overallSentiment": {
    "label": "bullish|cautious|mixed|bearish",
    "summary": "..."
  },
  "topTakeaway": "..."
}

IMPORTANT:
- Return ONLY valid JSON, no markdown code fences or extra text
- Be specific and opinionated — generic observations are useless
- Focus on what genuinely shifts the industry, not hype
- Weight high-engagement stories (upvotes/comments) as signals of what matters`;
}
