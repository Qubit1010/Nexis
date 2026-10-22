import Database from "better-sqlite3";
import { drizzle } from "drizzle-orm/better-sqlite3";
import { migrate } from "drizzle-orm/better-sqlite3/migrator";
import { DB_FILE, MIGRATIONS_DIR, ensureDirs } from "../config.ts";
import * as schema from "./schema.ts";

ensureDirs();
export const sqlite = new Database(DB_FILE);
sqlite.pragma("journal_mode = WAL");
sqlite.pragma("busy_timeout = 5000");

export const db = drizzle(sqlite, { schema });
migrate(db, { migrationsFolder: MIGRATIONS_DIR });

export { schema };
