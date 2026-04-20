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
  source: "content-opportunities";
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

export interface SavedArticle {
  source: "saved-articles";
  title: string;
  publication: string;
  url: string;
  tldr: string;
  date_saved: string;
  brief_date: string;
  platform_affinity: string[];
  saved_bonus: true;
}

export interface SavedArticlesSource {
  available: boolean;
  articles: SavedArticle[];
  error: string | null;
}

export interface PullIdeasOutput {
  generated_at: string;
  news_brief: NewsBrief;
  youtube_brief: YouTubeBrief;
  saved_topics: SavedTopics;
  saved_articles: SavedArticlesSource;
  errors: string[];
}

// ---- Scored idea (computed client-side) ----

export type IdeaSource = "news-brief" | "youtube-brief" | "content-opportunities" | "saved-articles" | "youtube-bookmarked";

export interface YouTubeBookmarkedVideo {
  dateSaved: string;
  title: string;
  channel: string;
  url: string;
  views: number;
  likes: number;
  engRate: number;
  duration: string;
  publishedDate: string;
  status: string;
}
export type Platform = "LinkedIn" | "Instagram" | "Blog";

export type ContentMode = "news" | "opinion" | "story" | "tutorial";

export type PillarKey =
  | "lived_experience"
  | "strong_pov"
  | "cross_domain"
  | "taste_judgment"
  | "identity_voice"
  | "practical_stakes"
  | "content_specific";

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
  url?: string;
  date?: string;
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

// ---- Weekly Schedule columns (shared between API route and modal) ----

export const SCHEDULE_COLUMNS = [
  "Date", "Day", "Platform", "Post Type", "Media Type", "Content Theme",
  "Topic / Idea", "Post Description", "Video/Post Script", "Video Prompt",
  "Image Prompt", "Reference Images", "Thumbnail", "Audio", "Draft",
  "Final Video/Post", "Reference", "Hashtags", "Publish Time", "Status", "Editor",
] as const;

// ---- Weekly Schedule row ----

export interface ScheduleRow {
  date: string;
  day: string;
  platform: string;
  postType: string;
  mediaType: string;
  contentTheme: string;
  topic: string;
  description: string;
  videoScript: string;
  videoPrompt: string;
  imagePrompt: string;
  referenceImages: string;
  thumbnail: string;
  audio: string;
  draft: string;
  finalPost: string;
  reference: string;
  hashtags: string;
  publishTime: string;
  status: string;
  editor: string;
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
