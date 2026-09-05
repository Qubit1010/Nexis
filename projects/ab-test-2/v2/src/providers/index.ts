import { mockProvider } from './mock.ts';
import { anthropicProvider } from './anthropic.ts';
import type { Provider } from './types.ts';

/** Avoids depending on @types/node just to name the environment. */
type Env = Record<string, string | undefined>;

export type { Provider, DraftRequest, DraftResult } from './types.ts';
export { MODEL, PRICING, costUsd } from './anthropic.ts';
export { mockProvider } from './mock.ts';

/**
 * Live Claude when a key is present, the deterministic offline drafter when it is not.
 *
 * The key is read from the environment only. It is never written to the database, never
 * logged, and never returned by any endpoint.
 *
 * Set REPLY_DRAFTER_FORCE_MOCK=1 to stay offline even with a key exported, which is what
 * the test suite does so a developer's real key can never cause a test run to bill.
 */
export function selectProvider(env: Env = process.env): Provider {
  const key = env.ANTHROPIC_API_KEY?.trim();
  if (env.REPLY_DRAFTER_FORCE_MOCK === '1' || !key) return mockProvider();
  return anthropicProvider(key);
}

export function hasApiKey(env: Env = process.env): boolean {
  return Boolean(env.ANTHROPIC_API_KEY?.trim()) && env.REPLY_DRAFTER_FORCE_MOCK !== '1';
}
