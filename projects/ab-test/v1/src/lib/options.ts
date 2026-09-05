/**
 * Form vocabularies. Kept free of zod so client components can import the labels
 * without pulling the validator into the browser bundle.
 */

export const TIMELINES = [
  { value: 'asap', label: 'As soon as possible' },
  { value: '1_month', label: 'Within a month' },
  { value: '1_3_months', label: 'One to three months' },
  { value: '3_plus_months', label: 'More than three months out' },
  { value: 'exploring', label: 'Just exploring for now' },
] as const;

export const TIMELINE_VALUES = TIMELINES.map((option) => option.value) as unknown as [
  string,
  ...string[],
];

export const SERVICES = [
  { value: 'ai-automation', label: 'AI automation and workflows' },
  { value: 'web-app', label: 'Custom web app or SaaS' },
  { value: 'website', label: 'Website or marketing site' },
  { value: 'cms', label: 'CMS build (WordPress, Webflow, Shopify)' },
  { value: 'data', label: 'Data and analytics' },
  { value: 'other', label: 'Something else' },
] as const;

export const SERVICE_VALUES = SERVICES.map((option) => option.value) as unknown as [
  string,
  ...string[],
];

/** Stored as the lower bound of the chosen band, so numeric rules can compare it. */
export const BUDGETS = [
  { value: 0, label: 'Under $1,000' },
  { value: 1000, label: '$1,000 to $5,000' },
  { value: 5000, label: '$5,000 to $10,000' },
  { value: 10000, label: '$10,000 to $25,000' },
  { value: 25000, label: '$25,000 or more' },
] as const;

export function labelFor(
  options: readonly { value: string | number; label: string }[],
  value: string | number,
): string {
  return options.find((option) => option.value === value)?.label ?? String(value);
}
