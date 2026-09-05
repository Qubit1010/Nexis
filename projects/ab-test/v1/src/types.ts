export const LEAD_STATUSES = ['new', 'contacted', 'qualified', 'dead'] as const;
export type LeadStatus = (typeof LEAD_STATUSES)[number];

export const BANDS = ['hot', 'warm', 'cold'] as const;
export type Band = (typeof BANDS)[number];

export const RULE_FIELDS = [
  'budget',
  'timeline',
  'services',
  'needs',
  'company',
  'source',
  'email',
] as const;
export type RuleField = (typeof RULE_FIELDS)[number];

export const RULE_OPERATORS = [
  'gte',
  'lte',
  'eq',
  'neq',
  'contains',
  'in',
  'present',
  'absent',
] as const;
export type RuleOperator = (typeof RULE_OPERATORS)[number];

/** A rule operand. Numbers for budget comparisons, a string for text, a list for `in`. */
export type RuleValue = number | string | string[];

export interface Rule {
  id: string;
  label: string;
  field: RuleField;
  operator: RuleOperator;
  value: RuleValue;
  points: number;
  enabled: boolean;
  position: number;
}

/** A rule as the editor submits it: identity and order come from array position. */
export type RuleInput = Omit<Rule, 'id' | 'position'>;

export interface Bands {
  hot: number;
  warm: number;
}

/** One line of the scoring receipt: a rule that actually fired. */
export interface BreakdownEntry {
  ruleId: string;
  label: string;
  points: number;
}

/** The subset of a lead the scoring engine reads. Nothing else is scorable. */
export interface ScorableLead {
  name: string;
  email: string;
  company: string;
  budget: number;
  timeline: string;
  services: string[];
  needs: string;
  source: string;
}

export interface Lead extends ScorableLead {
  id: string;
  status: LeadStatus;
  score: number;
  band: Band;
  breakdown: BreakdownEntry[];
  notes: string;
  createdAt: string;
  updatedAt: string;
}

export interface ScoreResult {
  score: number;
  band: Band;
  breakdown: BreakdownEntry[];
}

export interface StatusCounts {
  all: number;
  new: number;
  contacted: number;
  qualified: number;
  dead: number;
}
