/**
 * Opportunity scoring algorithm — mirrors SKILL.md scoring table.
 *
 * Max 10 points:
 *   Timeliness: breaking=3, trending=2, evergreen=1
 *   Competition: low=3, medium=2, high=1, unknown=2
 *   Momentum: rising=2, steady=1, cooling=0
 *   Pillar fit: strong=2, moderate=1, none=0
 *   Saved bonus: +1
 */

import type {
  NewsIdea,
  YouTubeOpportunity,
  YouTubeTopic,
  SavedIdea,
  ScoredIdea,
  Platform,
} from "./types";

let _idCounter = 0;
function uid() {
  return String(++_idCounter);
}

function timelinessPts(t: string): number {
  if (t === "breaking") return 3;
  if (t === "trending") return 2;
  return 1; // evergreen / unknown
}

function competitionPts(c: string): number {
  if (c === "low") return 3;
  if (c === "high") return 1;
  return 2; // medium / unknown
}

function momentumPts(m: string): number {
  if (m === "rising") return 2;
  if (m === "cooling") return 0;
  return 1; // steady / unknown
}

function pillarPts(topic: string): number {
  const t = topic.toLowerCase();
  // AI / automation = Pillar 1 (strong fit)
  if (
    t.includes("ai") ||
    t.includes("automation") ||
    t.includes("agent") ||
    t.includes("claude") ||
    t.includes("llm") ||
    t.includes("gpt") ||
    t.includes("workflow")
  )
    return 2;
  // Tech / business = Pillar 2-3 (moderate)
  if (
    t.includes("tech") ||
    t.includes("startup") ||
    t.includes("business") ||
    t.includes("founder") ||
    t.includes("agency")
  )
    return 1;
  return 1; // default moderate
}

function inferPlatform(affinity: string[]): Platform {
  const first = (affinity[0] || "linkedin").toLowerCase();
  if (first === "instagram") return "Instagram";
  if (first === "blog") return "Blog";
  return "LinkedIn";
}

function formatLabel(raw: string): string {
  const map: Record<string, string> = {
    thread: "Thread",
    blog: "Article",
    newsletter: "Newsletter",
    tutorial: "Tutorial",
    explainer: "Text Post",
    opinion: "Text Post",
    comparison: "Text Post",
    news: "Text Post",
    demo: "Reel",
    interview: "Article",
    carousel: "Carousel",
    "text post": "Text Post",
    article: "Article",
    reel: "Reel",
    "short video": "Short Video",
  };
  return map[raw.toLowerCase()] ?? raw;
}

export function scoreNewsIdea(idea: NewsIdea): ScoredIdea {
  const score = Math.min(
    10,
    timelinessPts(idea.timeliness) +
      competitionPts("medium") +
      momentumPts(idea.timeliness === "breaking" ? "rising" : "steady") +
      pillarPts(idea.title)
  );

  return {
    id: uid(),
    score,
    topic: idea.title,
    platform: inferPlatform(idea.platform_affinity),
    format: formatLabel(idea.format),
    hook: idea.hook,
    angle: idea.angle,
    pillar: "AI & Automation",
    source: "news-brief",
    timeliness: idea.timeliness,
    isCooling: false,
  };
}

export function scoreYouTubeOpportunity(opp: YouTubeOpportunity): ScoredIdea {
  const interestMomentum =
    opp.estimated_interest === "high" ? "rising" : "steady";
  const score = Math.min(
    10,
    timelinessPts("trending") +
      competitionPts("medium") +
      momentumPts(interestMomentum) +
      pillarPts(opp.idea)
  );

  return {
    id: uid(),
    score,
    topic: opp.idea,
    platform: inferPlatform(opp.platform_affinity),
    format: formatLabel(opp.format_suggestion),
    hook: "",
    angle: opp.reasoning,
    whyNow: opp.reasoning,
    pillar: "AI & Automation",
    source: "youtube-brief",
    timeliness: "trending",
  };
}

export function scoreYouTubeTopic(topic: YouTubeTopic): ScoredIdea {
  const isCooling = topic.competition_level === "high";
  const score = Math.min(
    10,
    timelinessPts("trending") +
      competitionPts(topic.competition_level) +
      momentumPts(isCooling ? "cooling" : "rising") +
      pillarPts(topic.topic)
  );

  return {
    id: uid(),
    score,
    topic: topic.topic,
    platform: inferPlatform(topic.platform_affinity),
    format: formatLabel(topic.target_format),
    hook: "",
    angle: topic.angle,
    whyNow: topic.why_now,
    pillar: "AI & Automation",
    source: "youtube-brief",
    competition: topic.competition_level,
    isCooling,
  };
}

export function scoreSavedIdea(idea: SavedIdea): ScoredIdea {
  const score = Math.min(
    10,
    timelinessPts(idea.timeliness || "evergreen") +
      competitionPts("medium") +
      momentumPts("steady") +
      pillarPts(idea.title) +
      1 // saved bonus
  );

  return {
    id: uid(),
    score,
    topic: idea.title,
    platform: inferPlatform(idea.platform_affinity),
    format: formatLabel(idea.format),
    hook: idea.hook,
    angle: idea.angle,
    pillar: "AI & Automation",
    source: "saved-topics",
    timeliness: idea.timeliness,
  };
}
