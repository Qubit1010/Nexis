import { z } from 'zod';
import {
  BUDGET_OPTIONS, FIELD_OPS, NEED_VALUES, RULE_FIELDS, RULE_OPS, STATUSES, TIMELINE_OPTIONS,
} from './catalog.ts';

const budgetValues = BUDGET_OPTIONS.map((o) => o.value);
const timelineValues = TIMELINE_OPTIONS.map((o) => o.value);

const trimmed = (max: number) => z.string().trim().max(max);

export const leadSubmission = z.object({
  name: trimmed(120).min(2, 'Please enter your name'),
  email: trimmed(200).email('That does not look like an email address').toLowerCase(),
  company: trimmed(160).default(''),
  budget: z.number().int().refine((v) => budgetValues.includes(v), 'Pick a budget range'),
  timeline: z.number().int().refine((v) => timelineValues.includes(v), 'Pick a timeline'),
  needs: z.array(z.string().refine((v) => NEED_VALUES.includes(v), 'Unknown option'))
    .min(1, 'Pick at least one')
    .max(NEED_VALUES.length),
  message: trimmed(4000).default(''),
  // Honeypot. Real people never fill this in; it is hidden from view and from screen readers.
  // Deliberately permissive: rejecting it here would 400 and tell the bot which field caught
  // it. The route accepts the submission and drops it instead.
  website: z.string().max(200).optional(),
});

const ruleShape = {
  label: trimmed(120).min(2),
  field: z.enum(RULE_FIELDS),
  op: z.enum(RULE_OPS),
  value: trimmed(200).min(1),
  points: z.number().int().min(-100).max(100),
  enabled: z.boolean().default(true),
  sort: z.number().int().min(0).max(100000).default(0),
};

/** Rejects legal-looking-but-impossible rules, e.g. `budget contains "x"`. */
const opFitsField = <T extends { field: keyof typeof FIELD_OPS; op: string }>(r: T, ctx: z.RefinementCtx) => {
  const allowed = FIELD_OPS[r.field];
  if (!allowed.includes(r.op as never)) {
    ctx.addIssue({ code: 'custom', path: ['op'], message: `"${r.op}" cannot be used on ${r.field}` });
  }
};

export const ruleCreate = z.object(ruleShape).superRefine(opFitsField);
export const ruleUpdate = z.object(ruleShape).partial().refine(
  (v) => Object.keys(v).length > 0,
  'Nothing to update',
);

export const leadUpdate = z.object({
  status: z.enum(STATUSES).optional(),
  notes: trimmed(4000).optional(),
}).refine((v) => v.status !== undefined || v.notes !== undefined, 'Nothing to update');

export const settingsUpdate = z.object({
  hot_min: z.number().int().min(0).max(100).optional(),
  warm_min: z.number().int().min(0).max(100).optional(),
}).refine(
  (v) => v.hot_min === undefined || v.warm_min === undefined || v.hot_min > v.warm_min,
  { message: 'The hot threshold must be above the warm threshold', path: ['hot_min'] },
);

export const login = z.object({ password: z.string().min(1).max(300) });

/** Allowlist, not interpolation. `sort` reaches an ORDER BY clause. */
export const SORTABLE = ['score', 'created_at', 'name', 'company', 'status'] as const;

export const leadQuery = z.object({
  status: z.enum(STATUSES).optional(),
  band: z.enum(['hot', 'warm', 'cold']).optional(),
  q: trimmed(120).optional(),
  sort: z.enum(SORTABLE).default('score'),
  dir: z.enum(['asc', 'desc']).default('desc'),
  limit: z.coerce.number().int().min(1).max(500).default(200),
});

export type LeadSubmission = z.infer<typeof leadSubmission>;

/** Flattens a ZodError into `{ field: message }`, which is what the form actually renders. */
export function fieldErrors(err: z.ZodError): Record<string, string> {
  const out: Record<string, string> = {};
  for (const issue of err.issues) {
    const key = issue.path.length ? issue.path.join('.') : '_';
    if (!(key in out)) out[key] = issue.message;
  }
  return out;
}
