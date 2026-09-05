import { createHash, timingSafeEqual } from 'node:crypto';
import type { FastifyReply, FastifyRequest } from 'fastify';
import { config } from './config.ts';

export const SESSION_COOKIE = 'li_session';

/**
 * Compare via fixed-length digests so the comparison cannot leak the password's length,
 * and via timingSafeEqual so it cannot leak a prefix through timing.
 */
export function passwordMatches(candidate: string, expected: string = config.adminPassword): boolean {
  const a = createHash('sha256').update(candidate, 'utf8').digest();
  const b = createHash('sha256').update(expected, 'utf8').digest();
  return timingSafeEqual(a, b);
}

type SessionPayload = { sub: 'admin'; exp: number };

export function issueSession(reply: FastifyReply): void {
  const payload: SessionPayload = { sub: 'admin', exp: Date.now() + config.sessionTtlMs };
  // signCookie applies an HMAC keyed on SESSION_SECRET; a tampered value fails verification.
  reply.setCookie(SESSION_COOKIE, JSON.stringify(payload), {
    path: '/',
    httpOnly: true,
    sameSite: 'lax',
    secure: config.isProd,
    signed: true,
    maxAge: Math.floor(config.sessionTtlMs / 1000),
  });
}

export function clearSession(reply: FastifyReply): void {
  reply.clearCookie(SESSION_COOKIE, { path: '/' });
}

function readSession(req: FastifyRequest): SessionPayload | null {
  const raw = req.cookies[SESSION_COOKIE];
  if (!raw) return null;
  const unsigned = req.unsignCookie(raw);
  if (!unsigned.valid || unsigned.value === null) return null;
  try {
    const parsed = JSON.parse(unsigned.value) as SessionPayload;
    if (parsed.sub !== 'admin') return null;
    if (typeof parsed.exp !== 'number' || parsed.exp < Date.now()) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function isAuthed(req: FastifyRequest): boolean {
  return readSession(req) !== null;
}

/** onRequest hook for every admin route. Registered per-scope, never opt-in per-handler. */
export async function requireAuth(req: FastifyRequest, reply: FastifyReply): Promise<void> {
  if (isAuthed(req)) return;
  clearSession(reply);
  await reply.code(401).send({ error: 'Not signed in' });
}
