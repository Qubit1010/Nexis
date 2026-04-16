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
  contentIdeas: Array<{
    title: string;
    angle: string;
    format: "thread" | "blog" | "newsletter";
    hook: string;
    keyPoints: string[];
    timeliness: "breaking" | "trending" | "evergreen";
    relatedTrends: string[];
  }>;
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

  return `You are a senior AI/tech analyst writing a daily intelligence brief for a content creator. Analyze the following articles for the category "${categoryName}" (${categoryDescription}).

ARTICLES:
${articleList}

INSTRUCTIONS:
1. Write a 2-3 sentence "So What?" insight identifying the overarching trend or theme. Be opinionated, forward-looking, and specific. What does this mean for someone creating AI/tech content?
2. For each article, provide:
   - The originalIndex (the number after [idx:] in the article listing)
   - A 1-2 sentence TL;DR capturing the key takeaway
   - A sentiment tag: "excited" (positive/optimistic), "neutral" (factual/informational), "concerned" (cautious/worried), or "skeptical" (doubtful/critical)
   - A relevance score from 1-10 (how relevant is this for an AI/tech content creator?)
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

  return `You are a strategic AI/tech content advisor. Today is ${date}. Below are analyzed summaries from ${categoryResults.length} AI/tech news categories. Your job is to synthesize this into actionable intelligence for a content creator who makes social threads and blog/newsletter content about AI and AI automation.

${categorySummaries}

PRODUCE THE FOLLOWING:

1. **TRENDS** (exactly 5): Cross-category trends you see emerging. For each:
   - Title: short, punchy name
   - Slug: kebab-case version
   - Summary: 2-3 sentences explaining the trend and why it matters
   - Momentum: "rising" (accelerating), "steady" (ongoing), or "cooling" (fading)
   - Categories: which category slugs this trend spans
   - Source count: how many distinct stories feed this trend
   - Content potential score: 1-10 rating of how good this would be for content (consider audience interest, freshness, depth of angle available)

2. **OVERALL SENTIMENT**: What's the AI space feeling like today?
   - Label: "bullish" (excited/optimistic), "cautious" (careful/measured), "mixed" (split opinions), or "bearish" (worried/negative)
   - Summary: 2-3 sentences capturing the mood

3. **CONTENT IDEAS** (exactly 10): Actionable content suggestions. Selection rules — follow these strictly:
   - Include ALL stories where the underlying articles have 200+ upvotes or 50+ comments (high community signal)
   - Include at least 2 "breaking" timeliness ideas — these are the freshest angles from today's news
   - Include at least 1 idea connecting to the highest content_potential_score trend
   - Cover at least 3 different category slugs across the 10 ideas — no single category dominates
   - Prefer ideas with a UNIQUE angle that hasn't been covered to death — skip generic "AI is growing" takes
   - If two ideas are on the same topic, keep only the one with the stronger hook and more specific angle
   - Fill remaining slots with the highest-potential ideas ranked by: engagement signal > timeliness > uniqueness of angle

   For each idea:
   - Title: compelling content title
   - Angle: the specific perspective or argument (1-2 sentences)
   - Format: "thread" (social media thread), "blog" (blog post or article), or "newsletter" (newsletter edition)
   - Hook: the opening line that grabs attention
   - Key points: 3-5 bullet points to cover
   - Timeliness: "breaking" (must publish today), "trending" (this week), or "evergreen" (anytime)
   - Related trends: which trend slugs this idea connects to

4. **TOP TAKEAWAY**: One sentence. If the reader sees nothing else today, what should they know?

Return your response as valid JSON with this exact structure:
{
  "trends": [
    { "title": "...", "slug": "...", "summary": "...", "momentumSignal": "rising|steady|cooling", "categories": ["slug1", "slug2"], "sourceCount": 5, "contentPotentialScore": 8 }
  ],
  "overallSentiment": {
    "label": "bullish|cautious|mixed|bearish",
    "summary": "..."
  },
  "contentIdeas": [
    { "title": "...", "angle": "...", "format": "thread|blog|newsletter", "hook": "...", "keyPoints": ["...", "..."], "timeliness": "breaking|trending|evergreen", "relatedTrends": ["trend-slug"] }
  ],
  "topTakeaway": "..."
}

IMPORTANT:
- Return ONLY valid JSON, no markdown code fences or extra text
- Be specific and opinionated — generic advice is useless
- Content ideas should be things the creator can actually make TODAY
- Follow the selection rules for content ideas exactly — do not ignore high-engagement stories
- Think like a content strategist: what would get clicks, shares, and discussion?
- No filler ideas — every one of the 10 must have a clear, differentiated angle`;
}
