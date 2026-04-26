export type Tier = "Poor" | "Average" | "Good" | "Excellent";

export interface ShapValue {
  feature: string;
  shap_value: number;
  raw_value: number | boolean | null;
  dimension: "ux" | "content" | "technical" | "trust";
}

export interface Recommendation {
  feature: string;
  title: string;
  rationale: string;
  impact: string;
  dimension: "ux" | "content" | "technical" | "trust";
  priority: number;
}

export interface SubScores {
  ux: number;
  content: number;
  technical: number;
  trust: number;
}

export interface ScoreData {
  url: string;
  score: number;
  tier: Tier;
  sub_scores: SubScores;
  shap_values: ShapValue[];
  recommendations: Recommendation[];
  model_version: string;
  elapsed_ms: number;
}

export interface ScoreResponse {
  ok: boolean;
  data?: ScoreData;
  error?: string;
}
