import { randomBytes } from 'node:crypto';

const env = process.env;
export const IS_PROD = env.NODE_ENV === 'production';
export const IS_TEST = env.NODE_ENV === 'test' || env.VITEST === 'true';

function sessionSecret(): string {
  const fromEnv = env.SESSION_SECRET?.trim();
  if (fromEnv && fromEnv.length >= 16 && fromEnv !== 'generate-with-openssl-rand-hex-32') {
    return fromEnv;
  }
  if (IS_PROD) {
    throw new Error(
      'SESSION_SECRET must be set to a random value of at least 16 characters in production. ' +
        'Generate one with: node -e "console.log(require(\'crypto\').randomBytes(32).toString(\'hex\'))"',
    );
  }
  // Dev and test only: ephemeral, so restarting invalidates old sessions. Never a fixed default.
  return randomBytes(32).toString('hex');
}

export const config = {
  port: Number(env.PORT ?? 4100),
  host: env.HOST ?? '127.0.0.1',
  dbPath: env.DB_PATH ?? './data/leads.db',
  adminPassword: env.ADMIN_PASSWORD?.trim() || 'change-me',
  sessionSecret: sessionSecret(),
  sessionTtlMs: 1000 * 60 * 60 * 12,
  // Only enable behind a reverse proxy you control. The rate limiter keys on the client IP,
  // and trusting X-Forwarded-For with nothing in front lets a caller forge it and bypass
  // every limit.
  trustProxy: env.TRUST_PROXY === 'true',
  isProd: IS_PROD,
  isTest: IS_TEST,
} as const;

export const usingDefaultPassword = config.adminPassword === 'change-me';
