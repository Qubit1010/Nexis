import { z } from 'zod';
import { fail, json, readJson, requireAdmin } from '@/lib/http';
import { deleteLead, updateLead } from '@/lib/leads';
import { leadUpdateSchema } from '@/lib/schema';

export const runtime = 'nodejs';

interface Context {
  params: Promise<{ id: string }>;
}

export async function PATCH(request: Request, context: Context): Promise<Response> {
  const denied = await requireAdmin(request);
  if (denied) return denied;

  const body = await readJson(request);
  if (!body.ok) return fail(400, 'bad_request', 'Body must be JSON.');

  const parsed = leadUpdateSchema.safeParse(body.data);
  if (!parsed.success) {
    return fail(
      400,
      'validation_error',
      'That update is not valid.',
      z.flattenError(parsed.error).fieldErrors,
    );
  }

  const { id } = await context.params;
  const lead = updateLead(id, parsed.data);
  if (!lead) return fail(404, 'not_found', 'No lead with that id.');

  return json({ lead });
}

export async function DELETE(request: Request, context: Context): Promise<Response> {
  const denied = await requireAdmin(request);
  if (denied) return denied;

  const { id } = await context.params;
  if (!deleteLead(id)) return fail(404, 'not_found', 'No lead with that id.');

  return json({ ok: true });
}
