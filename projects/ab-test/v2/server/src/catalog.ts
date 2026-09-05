/**
 * The single source of truth for the shape of a lead.
 *
 * The public form renders its selects from this, and the rules editor renders its value
 * pickers from this. That is deliberate: it makes it impossible to author a rule that
 * references a budget or timeline value the form can never actually produce.
 */

export type Option = { value: number; label: string; hint?: string };

export const BUDGET_OPTIONS: Option[] = [
  { value: 1, label: 'Under $1,000', hint: 'Exploring, or a very small piece of work' },
  { value: 2, label: '$1,000 - $5,000', hint: 'A defined single deliverable' },
  { value: 3, label: '$5,000 - $15,000', hint: 'A full project' },
  { value: 4, label: '$15,000 - $50,000', hint: 'A build plus ongoing work' },
  { value: 5, label: '$50,000+', hint: 'A programme of work' },
];

export const TIMELINE_OPTIONS: Option[] = [
  { value: 5, label: 'Immediately', hint: 'Ready to start this week' },
  { value: 4, label: 'Within a month', hint: 'Budget approved, scoping now' },
  { value: 3, label: '1 - 3 months', hint: 'Planned, not yet started' },
  { value: 2, label: '3 - 6 months', hint: 'On the roadmap' },
  { value: 1, label: 'No fixed date', hint: 'Researching options' },
];

export const NEED_OPTIONS = [
  { value: 'ai-automation', label: 'AI automation & workflows' },
  { value: 'web-app', label: 'Custom web app / SaaS' },
  { value: 'website', label: 'Website or marketing site' },
  { value: 'cms', label: 'CMS build (WordPress, Webflow, Shopify)' },
  { value: 'data', label: 'Data & analytics' },
  { value: 'integration', label: 'Systems integration' },
  { value: 'other', label: 'Something else' },
] as const;

export const NEED_VALUES = NEED_OPTIONS.map((n) => n.value) as string[];

export const STATUSES = ['new', 'contacted', 'qualified', 'dead'] as const;
export type Status = (typeof STATUSES)[number];

export const BANDS = ['hot', 'warm', 'cold'] as const;
export type Band = (typeof BANDS)[number];

export const RULE_FIELDS = ['budget', 'timeline', 'needs', 'company', 'message', 'email'] as const;
export type RuleField = (typeof RULE_FIELDS)[number];

export const RULE_OPS = ['gte', 'lte', 'eq', 'includes', 'contains', 'not_contains'] as const;
export type RuleOp = (typeof RULE_OPS)[number];

/** Which operators are legal on which field. Enforced at write time, not just in the UI. */
export const FIELD_OPS: Record<RuleField, readonly RuleOp[]> = {
  budget: ['gte', 'lte', 'eq'],
  timeline: ['gte', 'lte', 'eq'],
  needs: ['includes'],
  company: ['contains', 'not_contains'],
  message: ['contains', 'not_contains'],
  email: ['contains', 'not_contains'],
};

export const FIELD_LABELS: Record<RuleField, string> = {
  budget: 'Budget',
  timeline: 'Timeline',
  needs: 'What they need',
  company: 'Company',
  message: 'Project description',
  email: 'Email address',
};

export const OP_LABELS: Record<RuleOp, string> = {
  gte: 'is at least',
  lte: 'is at most',
  eq: 'is exactly',
  includes: 'includes',
  contains: 'contains the text',
  not_contains: 'does not contain the text',
};

export const SCORE_MIN = 0;
export const SCORE_MAX = 100;
