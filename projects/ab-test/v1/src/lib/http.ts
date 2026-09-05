import { isAuthenticated } from './auth';

export function json(data: unknown, init: ResponseInit = {}): Response {
  return new Response(JSON.stringify(data), {
    ...init,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'cache-control': 'no-store',
      ...(init.headers ?? {}),
    },
  });
}

/** One error shape for the whole API, so the client only ever parses one thing. */
export function fail(
  status: number,
  code: string,
  error: string,
  details?: unknown,
): Response {
  return json(details === undefined ? { error, code } : { error, code, details }, { status });
}

/**
 * Returns a 401 response when the caller is not the operator, or null when they are.
 * Called at the top of every admin handler. The dashboard layout gates the pages, but a
 * page gate protects pages, not the API, so each handler re-checks for itself.
 */
export async function requireAdmin(request: Request): Promise<Response | null> {
  if (await isAuthenticated(request)) return null;
  return fail(401, 'unauthorized', 'Sign in first.');
}

export async function readJson(
  request: Request,
): Promise<{ ok: true; data: unknown } | { ok: false }> {
  try {
    return { ok: true, data: await request.json() };
  } catch {
    return { ok: false };
  }
}
