/**
 * Auth for exactly one operator.
 *
 * There is no user table because there are no users, only the owner. A shared password
 * unlocks a signed, expiring cookie; the cookie is the whole session. If this ever gains a
 * second human, this file is what gets replaced, and nothing else has to change.
 *
 * Web Crypto rather than node:crypto so the same code runs unchanged in either runtime.
 */

export const SESSION_COOKIE = 'leadq_session';
const MAX_AGE_SECONDS = 60 * 60 * 24 * 7;

const DEV_SECRET = 'leadq-dev-secret-do-not-use-in-production';
const DEV_PASSWORD = 'changeme';

let warned = false;

function warnOnce(): void {
  if (warned || process.env.NODE_ENV === 'test') return;
  warned = true;
  console.warn(
    '[leadq] ADMIN_PASSWORD or SESSION_SECRET is unset. Falling back to development ' +
      'defaults. Set both in .env before exposing this to the internet.',
  );
}

function secret(): string {
  const value = process.env.SESSION_SECRET;
  if (value && value.length > 0) return value;
  warnOnce();
  return DEV_SECRET;
}

function adminPassword(): string {
  const value = process.env.ADMIN_PASSWORD;
  if (value && value.length > 0) return value;
  warnOnce();
  return DEV_PASSWORD;
}

function base64url(bytes: Uint8Array): string {
  let binary = '';
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

async function hmac(payload: string): Promise<string> {
  const key = await crypto.subtle.importKey(
    'raw',
    new TextEncoder().encode(secret()),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign'],
  );
  const signature = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(payload));
  return base64url(new Uint8Array(signature));
}

async function sha256(value: string): Promise<string> {
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(value));
  return base64url(new Uint8Array(digest));
}

/** Constant-time over equal-length inputs, which is guaranteed by hashing first. */
function equals(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i += 1) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

/**
 * Both sides are hashed before comparison so the compare is fixed-width and the loop
 * cannot leak the password's length.
 */
export async function verifyPassword(candidate: string): Promise<boolean> {
  const [given, expected] = await Promise.all([sha256(candidate), sha256(adminPassword())]);
  return equals(given, expected);
}

export async function createSessionToken(now: number = Date.now()): Promise<string> {
  const expiry = String(now + MAX_AGE_SECONDS * 1000);
  return expiry + '.' + (await hmac(expiry));
}

export async function verifySessionToken(
  token: string | null | undefined,
  now: number = Date.now(),
): Promise<boolean> {
  if (!token) return false;
  const separator = token.indexOf('.');
  if (separator < 1) return false;

  const expiry = token.slice(0, separator);
  const signature = token.slice(separator + 1);

  if (!equals(signature, await hmac(expiry))) return false;

  const expiresAt = Number(expiry);
  return Number.isFinite(expiresAt) && expiresAt > now;
}

/** Reads the session cookie off a plain Request, so handlers stay testable. */
export function readSessionCookie(request: Request): string | null {
  const header = request.headers.get('cookie');
  if (!header) return null;
  for (const part of header.split(';')) {
    const [name, ...rest] = part.trim().split('=');
    if (name === SESSION_COOKIE) return decodeURIComponent(rest.join('='));
  }
  return null;
}

export function sessionCookie(token: string | null): string {
  const secure = process.env.NODE_ENV === 'production' ? '; Secure' : '';
  if (token === null) {
    return SESSION_COOKIE + '=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0' + secure;
  }
  return (
    SESSION_COOKIE +
    '=' +
    encodeURIComponent(token) +
    '; HttpOnly; SameSite=Lax; Path=/; Max-Age=' +
    MAX_AGE_SECONDS +
    secure
  );
}

export async function isAuthenticated(request: Request): Promise<boolean> {
  return verifySessionToken(readSessionCookie(request));
}
