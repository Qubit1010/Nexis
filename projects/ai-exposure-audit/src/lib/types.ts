/**
 * Core types. The scoring shapes here are the product; everything else is plumbing.
 */

export type DimensionId =
  | "output_determinism"
  | "client_self_service"
  | "judgment_thinness"
  | "artifact_billing"
  | "price_anchor_erosion";

export const DIMENSION_IDS: DimensionId[] = [
  "output_determinism",
  "client_self_service",
  "judgment_thinness",
  "artifact_billing",
  "price_anchor_erosion",
];

/** 1-5. Every dimension is oriented so 5 = maximum exposure. No inverted dimensions exist. */
export type ScoreValue = 1 | 2 | 3 | 4 | 5;

export type EvidenceTier = "documented" | "practitioner" | "judgment";

/** Where a score came from. A number with no provenance is not allowed to exist. */
export type Provenance = "llm" | "llm-adjusted" | "manual";

export type PricingModel = "hourly" | "fixed" | "retainer" | "outcome";

export interface DimensionScore {
  value: ScoreValue;
  reasoning: string;
  provenance: Provenance;
}

export interface RubricDimension {
  id: DimensionId;
  name: string;
  question: string;
  high_means: string;
  evidence_tier: EvidenceTier;
  evidence_note: string;
  sources: string[];
  anchors: Record<string, string>;
}

export interface Rubric {
  version: string;
  published: string;
  title: string;
  orientation: string;
  weights_disclaimer: string;
  default_weights: Weights;
  dimensions: RubricDimension[];
}

export type Weights = Record<DimensionId, number>;

export interface Source {
  title: string;
  publisher: string;
  url: string;
  kind: string;
  caveat?: string;
}

export interface SourceRegistry {
  version: string;
  note: string;
  sources: Record<string, Source>;
}

export interface PriceAnchor {
  id: string;
  label: string;
  amount?: number;
  amount_low?: number;
  amount_high?: number;
  unit: string;
  display: string;
  evidence_tier: EvidenceTier;
  sources: string[];
  note?: string;
}

export interface Archetype {
  id: string;
  name: string;
  what_changes: string;
  attacks_dimensions: DimensionId[];
  anchor_ref: string | null;
  evidence_tier: EvidenceTier;
  evidence_note: string;
  sources: string[];
}

export interface PriceBook {
  version: string;
  published: string;
  global_caveat: string;
  anchors: PriceAnchor[];
  archetypes: Archetype[];
}

export interface ServiceLine {
  id: string;
  name: string;
  /** Percentage points of the book, 0-100. */
  revenue_share_pct: number;
  deliverable_description: string;
  pricing_model: PricingModel;
  typical_price: number | null;
  scores: Partial<Record<DimensionId, DimensionScore>>;
  replacement: {
    archetype_id: string;
    rationale: string;
  } | null;
  sort_order: number;
}

export interface Business {
  name: string;
  headcount: number | null;
  avg_project_value: number | null;
  positioning: string;
}

export interface Audit {
  id: string;
  business: Business;
  weights: Weights;
  rubric_version: string;
  pricebook_version: string;
  lines: ServiceLine[];
  created_at: string;
  updated_at: string;
}

/* ---------- computed results ---------- */

export interface LineExposure {
  line_id: string;
  /** null when any dimension is unscored. Never a partial number. */
  exposure: number | null;
  /** revenue_share_pct * exposure. null when exposure is null. */
  contribution: number | null;
  missing_dimensions: DimensionId[];
  /** Per-dimension normalized values, shown so the arithmetic is checkable by hand. */
  normalized: Partial<Record<DimensionId, number>>;
}

export interface AuditResult {
  lines: LineExposure[];
  /** Sum of contributions across fully scored lines. Null if no line is fully scored. */
  exposed_revenue_pct: number | null;
  /** Revenue share covered by fully scored lines. Tells you how much of the book the number speaks for. */
  scored_revenue_pct: number;
  /** Sum of all revenue shares entered. Flagged when it is not 100. */
  total_revenue_pct: number;
  warnings: string[];
  complete: boolean;
}
