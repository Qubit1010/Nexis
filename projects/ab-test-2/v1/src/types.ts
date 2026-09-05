/** Mirrors the API contract in .builder/architecture.md section 6. */

export type Health = {
  ok: true;
  provider: 'anthropic' | 'stub';
  model: string;
  hasApiKey: boolean;
  pricing: { inputPerMTok: number; outputPerMTok: number; source: string };
};

export type Rating = 'good' | 'bad' | null;

export type EnquirySummary = {
  id: number;
  subject: string;
  bodyPreview: string;
  createdAt: string;
  draftCount: number;
  latestRating: Rating;
};

export type Enquiry = {
  id: number;
  subject: string;
  body: string;
  createdAt: string;
};

export type Draft = {
  id: number;
  enquiryId: number;
  promptVersionId: number;
  promptVersion: number;
  provider: string;
  model: string;
  generatedText: string;
  editedText: string | null;
  rating: Rating;
  editDistance: number | null;
  editBaseWords: number | null;
  keepRatio: number | null;
  inputTokens: number | null;
  outputTokens: number | null;
  latencyMs: number | null;
  costUsd: number | null;
  createdAt: string;
  ratedAt: string | null;
};

export type PromptVersion = {
  id: number;
  version: number;
  label: string;
  systemPrompt: string;
  createdAt: string;
  isActive: boolean;
};

export type VersionStat = {
  promptVersionId: number;
  version: number;
  label: string;
  createdAt: string;
  isActive: boolean;
  drafts: number;
  rated: number;
  good: number;
  bad: number;
  goodRate: number | null;
  wilsonLow: number | null;
  wilsonHigh: number | null;
  enoughData: boolean;
  editedCount: number;
  medianKeepRatio: number | null;
  avgLatencyMs: number | null;
  totalCostUsd: number | null;
};

export type Totals = {
  enquiries: number;
  drafts: number;
  rated: number;
  versions: number;
  minSample: number;
};

export type Scoreboard = { versions: VersionStat[]; totals: Totals };
