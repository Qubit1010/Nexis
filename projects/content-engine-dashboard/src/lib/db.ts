import Database from "better-sqlite3";
import path from "path";
import { existsSync, mkdirSync } from "fs";

const DATA_DIR = path.join(process.cwd(), "data");
const DB_PATH = path.join(DATA_DIR, "content-engine.db");

let _db: Database.Database | null = null;

function getDb(): Database.Database {
  if (_db) return _db;

  if (!existsSync(DATA_DIR)) {
    mkdirSync(DATA_DIR, { recursive: true });
  }

  _db = new Database(DB_PATH);

  // Key/value cache table — stores JSON blobs by key
  _db.exec(`
    CREATE TABLE IF NOT EXISTS cache (
      key   TEXT PRIMARY KEY,
      value TEXT NOT NULL,
      saved_at INTEGER NOT NULL
    )
  `);

  return _db;
}

export function cacheSet(key: string, value: unknown): void {
  const db = getDb();
  db.prepare(
    "INSERT INTO cache (key, value, saved_at) VALUES (?, ?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value, saved_at = excluded.saved_at"
  ).run(key, JSON.stringify(value), Date.now());
}

export function cacheGet<T>(key: string): { value: T; savedAt: number } | null {
  const db = getDb();
  const row = db
    .prepare("SELECT value, saved_at FROM cache WHERE key = ?")
    .get(key) as { value: string; saved_at: number } | undefined;

  if (!row) return null;
  return { value: JSON.parse(row.value) as T, savedAt: row.saved_at };
}
