import { beforeAll, describe, expect, it } from 'vitest';
import {
  SESSION_COOKIE,
  createSessionToken,
  readSessionCookie,
  sessionCookie,
  verifyPassword,
  verifySessionToken,
} from '@/lib/auth';

beforeAll(() => {
  process.env.ADMIN_PASSWORD = 'correct-horse-battery';
  process.env.SESSION_SECRET = 'test-secret-value';
});

describe('verifyPassword', () => {
  it('accepts the configured password', async () => {
    await expect(verifyPassword('correct-horse-battery')).resolves.toBe(true);
  });

  it('rejects a wrong password, including a prefix of the right one', async () => {
    await expect(verifyPassword('wrong')).resolves.toBe(false);
    await expect(verifyPassword('correct-horse')).resolves.toBe(false);
    await expect(verifyPassword('')).resolves.toBe(false);
  });
});

describe('session tokens', () => {
  it('signs a token that verifies', async () => {
    const token = await createSessionToken();
    await expect(verifySessionToken(token)).resolves.toBe(true);
  });

  it('rejects a tampered signature', async () => {
    const token = await createSessionToken();
    const [expiry, signature] = token.split('.');
    const flipped = (signature ?? '').slice(0, -1) + 'X';
    await expect(verifySessionToken(expiry + '.' + flipped)).resolves.toBe(false);
  });

  it('rejects an extended expiry that was not re-signed', async () => {
    const token = await createSessionToken();
    const signature = token.split('.')[1] ?? '';
    const forged = String(Date.now() + 90 * 24 * 3600 * 1000) + '.' + signature;
    await expect(verifySessionToken(forged)).resolves.toBe(false);
  });

  it('rejects a correctly signed but expired token', async () => {
    const longAgo = Date.now() - 30 * 24 * 3600 * 1000;
    const token = await createSessionToken(longAgo);
    await expect(verifySessionToken(token)).resolves.toBe(false);
  });

  it('rejects junk, empty and missing tokens', async () => {
    await expect(verifySessionToken('')).resolves.toBe(false);
    await expect(verifySessionToken(null)).resolves.toBe(false);
    await expect(verifySessionToken(undefined)).resolves.toBe(false);
    await expect(verifySessionToken('nodot')).resolves.toBe(false);
    await expect(verifySessionToken('.onlysig')).resolves.toBe(false);
  });

  it('rejects a token signed with a different secret', async () => {
    const token = await createSessionToken();
    process.env.SESSION_SECRET = 'a-completely-different-secret';
    await expect(verifySessionToken(token)).resolves.toBe(false);
    process.env.SESSION_SECRET = 'test-secret-value';
  });
});

describe('cookie plumbing', () => {
  it('builds an httpOnly, lax, path-scoped cookie', () => {
    const header = sessionCookie('abc.def');
    expect(header).toContain(SESSION_COOKIE + '=abc.def');
    expect(header).toContain('HttpOnly');
    expect(header).toContain('SameSite=Lax');
    expect(header).toContain('Path=/');
    expect(header).toContain('Max-Age=604800');
  });

  it('expires the cookie when signing out', () => {
    expect(sessionCookie(null)).toContain('Max-Age=0');
  });

  it('reads its own cookie back off a request, ignoring neighbours', () => {
    const request = new Request('http://localhost:3000/', {
      headers: { cookie: 'other=1; ' + SESSION_COOKIE + '=token-value; another=2' },
    });
    expect(readSessionCookie(request)).toBe('token-value');
  });

  it('returns null when no cookie header is present', () => {
    expect(readSessionCookie(new Request('http://localhost:3000/'))).toBeNull();
  });
});
