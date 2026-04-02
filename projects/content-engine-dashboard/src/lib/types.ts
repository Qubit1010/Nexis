// ---- pull_ideas.py output types ----

export interface PlatformAffinity {
  platforms: string[];
}

export interface NewsIdea {
  source: "news-brief";
  title: string;
  angle: string;
  format: string;
  hook: string;
  key_points: string[];
  timeliness: string; // "breaking" | "trending" | "evergreen"
  related_trends: string[];
  platform_affinity: string[];
}

export interface YouTubeOpportunity {
  source: "youtube-brief";
  idea: string;
  reasoning: string;
  format_suggestion: string;
  estimated_interest: string; // "high" | "medium" | "low"
  platform_affinity: string[];
}

export interface YouTubeTopic {
  source: "youtube-brief";
  topic: string;
  angle: string;
  why_now: string;
  target_format: string;
  competition_level: string; // "low" | "medium" | "high"
  reference_videos: string[];
  platform_affinity: string[];
}

export interface TrendingTopic {
  topic: string;
  mention_count: number;
  sentiment: string;
  summary: string;
}

export interface SavedIdea {
  source: "saved-topics";
  title: string;
  format: string;
  timeliness: string;
  angle: string;
  hook: string;
  key_points: string[];
  related_trends: string[];
  date_saved: string;
  brief_date: string;
  platform_affinity: string[];
  saved_bonus: true;
}

export interface NewsBrief {
  available: boolean;
  date: string | null;
  ideas: NewsIdea[];
  trends: TrendingTopic[];
  error: string | null;
}

export interface YouTubeBrief {
  available: boolean;
  analyzed_at: string | null;
  content_opportunities: YouTubeOpportunity[];
  suggested_topics: YouTubeTopic[];
  trending_topics: TrendingTopic[];
  error: string | null;
}

export interface SavedTopics {
  available: boolean;
  ideas: SavedIdea[];
  error: string | null;
}

export interface PullIdeasOutput {
  generated_at: string;
  news_brief: NewsBrief;
  youtube_brief: YouTubeBrief;
  saved_topics: SavedTopics;
  errors: string[];
}

// ---- Scored idea (computed client-side) ----

export type IdeaSource = "news-brief" | "youtube-brief" | "saved-topics";
export type Platform = "LinkedIn" | "Instagram" | "Blog";
export type Format =
  | "Text Post"
  | "Carousel"
  | "Reel"
  | "Article"
  | "Tutorial"
  | "Thread"
  | "Newsletter"
  | "Short Video";

export interface ScoredIdea {
  id: string;
  score: number; // 0-10
  topic: string;
  platform: Platform;
  format: Format | string;
  hook: string;
  angle: string;
  whyNow?: string;
  pillar: string;
  source: IdeaSource;
  timeliness?: string;
  competition?: string;
  momentum?: string;
  isCooling?: boolean;
}

// ---- research_topic.py output types ----

export interface DataPoint {
  fact: string;
  source: string;
}

export interface ResearchOutput {
  topic: string;
  available: boolean;
  error?: string;
  primary_keyword?: string;
  secondary_keywords?: string[];
  data_points?: DataPoint[];
  competing_angles?: string[];
  content_gap?: string;
  people_also_ask?: string[];
  hashtags?: string[];
  searched_at?: string;
}

// ---- Content Log row ----

export interface LogRow {
  date: string;
  platform: string;
  format: string;
  title: string;
  goal: string;
  hook: string;
  docUrl: string;
  status: string;
}
