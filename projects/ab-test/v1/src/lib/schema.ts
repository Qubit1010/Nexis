import { z } from 'zod';
import { LEAD_STATUSES, RULE_FIELDS, RULE_OPERATORS } from '@/types';
import { SERVICE_VALUES, TIMELINE_VALUES } from './options';

/** Public intake submission. The only untrusted input path in the product. */
export const leadSubmissionSchema = z.object({
  name: z.string().trim().min(1, 'Tell us who you are.').max(120),
  email: z.string().trim().email('Enter a valid email address.').max(200),
  company: z.string().trim().max(160).default(''),
  budget: z.coerce.number().int('Pick a budget band.').min(0).max(100_000_000),
  timeline: z.enum(TIMELINE_VALUES, { error: 'Pick a timeline.' }),
  services: z
    .array(z.enum(SERVICE_VALUES))
    .min(1, 'Pick at least one thing you need.')
    .max(SERVICE_VALUES.length),
  needs: z
    .string()
    .trim()
    .min(10, 'A sentence or two, so we know what we are looking at.')
    .max(4000),
  source: z.string().trim().max(160).default(''),
  /** Honeypot. Real people never see this field, so a value means a bot. */
  website: z.string().max(200).optional(),
});

export type LeadSubmission = z.infer<typeof leadSubmissionSchema>;

export const leadUpdateSchema = z
  .object({
    status: z.enum(LEAD_STATUSES).optional(),
    notes: z.string().max(4000).optional(),
  })
  .refine((patch) => patch.status !== undefined || patch.notes !== undefined, {
    error: 'Send a status or a note.',
  });

const ruleValueSchema = z.union([z.number(), z.string(), z.array(z.string())]);

const ruleInputSchema = z
  .object({
    label: z.string().trim().min(1, 'Every rule needs a name.').max(80),
    field: z.enum(RULE_FIELDS),
    operator: z.enum(RULE_OPERATORS),
    value: ruleValueSchema,
    points: z.number().int().min(-100).max(100),
    enabled: z.boolean(),
  })
  .superRefine((rule, ctx) => {
    if (rule.operator === 'gte' || rule.operator === 'lte') {
      const numeric = typeof rule.value === 'number' ? rule.value : Number(rule.value);
      if (Array.isArray(rule.value) || !Number.isFinite(numeric)) {
        ctx.addIssue({
          code: 'custom',
          path: ['value'],
          message: 'Greater/less than needs a number.',
        });
      }
    }
    if (rule.operator === 'in' && !Array.isArray(rule.value)) {
      ctx.addIssue({
        code: 'custom',
        path: ['value'],
        message: '"Is one of" needs a list of values.',
      });
    }
  });

export const rulesPayloadSchema = z
  .object({
    rules: z.array(ruleInputSchema).max(60, 'Sixty rules is already too many.'),
    bands: z.object({
      hot: z.number().int().min(1).max(100),
      warm: z.number().int().min(0).max(99),
    }),
  })
  .refine((payload) => payload.bands.hot > payload.bands.warm, {
    path: ['bands', 'hot'],
    error: 'The hot threshold has to sit above the warm one.',
  });

export const sessionSchema = z.object({
  password: z.string().min(1, 'Enter the password.').max(200),
});

export const leadQuerySchema = z.object({
  status: z.enum(['all', ...LEAD_STATUSES]).catch('all'),
  band: z.enum(['all', 'hot', 'warm', 'cold']).catch('all'),
  sort: z.enum(['score', 'created_at', 'name']).catch('score'),
  order: z.enum(['asc', 'desc']).catch('desc'),
  q: z.string().trim().max(120).catch(''),
});
