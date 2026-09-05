import { z } from 'zod';
import { createSessionToken, sessionCookie, verifyPassword } from '@/lib/auth';
import { fail, json, readJson } from '@/lib/http';
import { hit, clientKey } from '@/lib/rate-limit';
import { sessionSchema } from '@/lib/schema';

export const runtime = 'nodejs';

export async function POST(request: Request): Promise<Response> {
  if (!hit('login:' + clientKey(request), 10, 60_000)) {
    return fail(429, 'rate_limited', 'Too many attempts. Wait a minute.');
  }

  const body = await readJson(request);
  if (!body.ok) return fail(400, 'bad_request', 'Body must be JSON.');

  const parsed = sessionSchema.safeParse(body.data);
  if (!parsed.success) {
    return fail(400, 'validation_error', 'Enter the password.', z.flattenError(parsed.error).fieldErrors);
  }

  if (!(await verifyPassword(parsed.data.password))) {
    return fail(401, 'unauthorized', 'That password is not right.');
  }

  return json({ ok: true }, { headers: { 'set-cookie': sessionCookie(await createSessionToken()) } });
}

export async function DELETE(): Promise<Response> {
  return json({ ok: true }, { headers: { 'set-cookie': sessionCookie(null) } });
}
