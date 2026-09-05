import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { closeDb } from '@/lib/db';

let directory: string | null = null;

/**
 * Points the app at a throwaway SQLite file. `getDb()` reopens whenever LEADQ_DB_PATH
 * changes, so no module mocking is needed to isolate a suite.
 */
export function useTempDb(): void {
  closeDb();
  directory = mkdtempSync(join(tmpdir(), 'leadq-test-'));
  process.env.LEADQ_DB_PATH = join(directory, 'leads.db');
}

export function dropTempDb(): void {
  closeDb();
  if (directory) rmSync(directory, { recursive: true, force: true });
  directory = null;
  delete process.env.LEADQ_DB_PATH;
}
