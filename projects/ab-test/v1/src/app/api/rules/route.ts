import { z } from 'zod';
import { fail, json, readJson, requireAdmin } from '@/lib/http';
import { saveRuleSet } from '@/lib/qualify';
import { getBands, listRules } from '@/lib/rules';
import { rulesPayloadSchema } from '@/lib/schema';
import type { RuleInput } from '@/types';

export const runtime = 'nodejs';

export async function GET(request: Request): Promise<Response> {
  const denied = await requireAdmin(request);
  if (denied) return denied;

  return json({ rules: listRules(), bands: getBands() });
}

/** Replaces the whole rule set, then rescores every lead in the same transaction. */
export async function PUT(request: Request): Promise<Response> {
  const denied = await requireAdmin(request);
  if (denied) return denied;

  const body = await readJson(request);
  if (!body.ok) return fail(400, 'bad_request', 'Body must be JSON.');

  const parsed = rulesPayloadSchema.safeParse(body.data);
  if (!parsed.success) {
    return fail(
      400,
      'validation_error',
      'Those rules are not valid.',
      z.flattenError(parsed.error).fieldErrors,
    );
  }

  const result = saveRuleSet(parsed.data.rules as RuleInput[], parsed.data.bands);
  return json(result);
}
