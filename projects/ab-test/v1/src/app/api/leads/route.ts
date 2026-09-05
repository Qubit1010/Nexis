import { randomUUID } from 'node:crypto';
import { z } from 'zod';
import { fail, json, readJson, requireAdmin } from '@/lib/http';
import { countsByStatus, createLead, listLeads } from '@/lib/leads';
import { clientKey, hit } from '@/lib/rate-limit';
import { leadQuerySchema, leadSubmissionSchema } from '@/lib/schema';

export const runtime = 'nodejs';

/** PUBLIC. The only untrusted entry point in the product. */
export async function POST(request: Request): Promise<Response> {
  if (!hit('leads:' + clientKey(request), 5, 60_000)) {
    return fail(429, 'rate_limited', 'Too many submissions. Try again in a minute.');
  }

  const body = await readJson(request);
  if (!body.ok) return fail(400, 'bad_request', 'Body must be JSON.');

  const parsed = leadSubmissionSchema.safeParse(body.data);
  if (!parsed.success) {
    return fail(
      400,
      'validation_error',
      'A few answers need fixing.',
      z.flattenError(parsed.error).fieldErrors,
    );
  }

  const { website, ...submission } = parsed.data;

  // Honeypot. A bot filled a field no human can see, so answer as if it worked and drop it.
  if (website !== undefined && website.trim() !== '') {
    return json({ ok: true, id: randomUUID() }, { status: 201 });
  }

  const lead = createLead(submission);

  // The score is internal. Returning it would leak the rule set to anyone probing the form.
  return json({ ok: true, id: lead.id }, { status: 201 });
}

/** ADMIN. */
export async function GET(request: Request): Promise<Response> {
  const denied = await requireAdmin(request);
  if (denied) return denied;

  const params = new URL(request.url).searchParams;
  const filter = leadQuerySchema.parse({
    status: params.get('status') ?? undefined,
    band: params.get('band') ?? undefined,
    sort: params.get('sort') ?? undefined,
    order: params.get('order') ?? undefined,
    q: params.get('q') ?? undefined,
  });

  return json({ leads: listLeads(filter), counts: countsByStatus() });
}
