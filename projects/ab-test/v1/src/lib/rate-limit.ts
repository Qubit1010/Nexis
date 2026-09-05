/**
 * Fixed-window limiter for the one public endpoint.
 *
 * Deliberately in-process: a single-process app does not need Redis, and a real deployment
 * should put a proper limit at the proxy anyway. This exists so an unattended public form
 * cannot be hammered into a full disk in an afternoon.
 */

interface Window {
  count: number;
  resetAt: number;
}

const windows = new Map<string, Window>();
const MAX_TRACKED_KEYS = 5000;

function prune(now: number): void {
  for (const [key, window] of windows) {
    if (now >= window.resetAt) windows.delete(key);
  }
}

/** Returns true when the request is allowed, false when the caller is over the limit. */
export function hit(key: string, limit: number, windowMs: number): boolean {
  const now = Date.now();
  if (windows.size > MAX_TRACKED_KEYS) prune(now);

  const existing = windows.get(key);
  if (!existing || now >= existing.resetAt) {
    windows.set(key, { count: 1, resetAt: now + windowMs });
    return true;
  }
  if (existing.count >= limit) return false;

  existing.count += 1;
  return true;
}

export function resetRateLimits(): void {
  windows.clear();
}

/** Best effort. Behind a proxy this is only as trustworthy as the proxy's headers. */
export function clientKey(request: Request): string {
  const forwarded = request.headers.get('x-forwarded-for');
  if (forwarded) return forwarded.split(',')[0]?.trim() || 'unknown';
  return request.headers.get('x-real-ip') ?? 'unknown';
}
