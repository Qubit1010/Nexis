import { existsSync, readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { MODEL_ID } from './pricing.ts';

export const PROJECT_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

/**
 * Reads THIS directory's .env and nothing else.
 *
 * Deliberately does not walk up the tree. The parent repository has its own .env with a real
 * ANTHROPIC_API_KEY in it; inheriting that would have made the "runs without a key" requirement
 * impossible to verify honestly and would have spent the user's money without them asking.
 * Real environment variables still win, so `ANTHROPIC_API_KEY=... npm start` works as expected.
 */
function readLocalEnvFile(): Record<string, string> {
  const envPath = path.join(PROJECT_ROOT, '.env');
  if (!existsSync(envPath)) return {};

  const out: Record<string, string> = {};
  for (const rawLine of readFileSync(envPath, 'utf8').split(/\r?\n/)) {
    const line = rawLine.trim();
    if (line.length === 0 || line.startsWith('#')) continue;
    const eq = line.indexOf('=');
    if (eq === -1) continue;
    const key = line.slice(0, eq).trim();
    let value = line.slice(eq + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    if (key.length > 0) out[key] = value;
  }
  return out;
}

export type Config = {
  port: number;
  dbPath: string;
  model: string;
  apiKey: string | undefined;
};

export function loadConfig(overrides: Partial<Config> = {}): Config {
  const fileEnv = readLocalEnvFile();
  const get = (key: string): string | undefined => process.env[key] ?? fileEnv[key];

  const rawKey = (get('ANTHROPIC_API_KEY') ?? '').trim();

  return {
    port: Number(get('PORT') ?? 4200),
    dbPath: path.resolve(PROJECT_ROOT, get('REPLYLAB_DB') ?? 'data/replylab.db'),
    model: get('REPLYLAB_MODEL') ?? MODEL_ID,
    apiKey: rawKey.length > 0 ? rawKey : undefined,
    ...overrides,
  };
}
