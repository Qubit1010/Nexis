import 'server-only'
import Database from 'better-sqlite3'
import path from 'path'
import fs from 'fs'

const DB_PATH = path.join(process.cwd(), 'data', 'scout.db')

// Ensure data directory exists
const dataDir = path.join(process.cwd(), 'data')
if (!fs.existsSync(dataDir)) fs.mkdirSync(dataDir, { recursive: true })

let _db: Database.Database | null = null

export function getDb(): Database.Database {
  if (_db) return _db
  _db = new Database(DB_PATH)
  _db.pragma('journal_mode = WAL')
  migrate(_db)
  return _db
}

function migrate(db: Database.Database) {
  db.exec(`
    CREATE TABLE IF NOT EXISTS jobs (
      id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      description TEXT,
      budget REAL,
      budget_type TEXT,
      category TEXT,
      skills TEXT,
      client_verified INTEGER DEFAULT 0,
      client_spent REAL DEFAULT 0,
      client_rating REAL DEFAULT 0,
      client_hire_rate REAL DEFAULT 0,
      posted_at TEXT,
      score INTEGER DEFAULT 0,
      proposals_tier TEXT DEFAULT '',
      url TEXT DEFAULT '',
      raw_json TEXT,
      fetched_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS saved_filters (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      category TEXT,
      keywords TEXT DEFAULT '[]',
      min_budget REAL DEFAULT 0,
      client_verified_only INTEGER DEFAULT 0,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS bookmarks (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      job_id TEXT NOT NULL,
      notes TEXT DEFAULT '',
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS bid_queue (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      job_id TEXT NOT NULL,
      status TEXT DEFAULT 'pending',
      notes TEXT DEFAULT '',
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS settings (
      key TEXT PRIMARY KEY,
      value TEXT NOT NULL,
      updated_at TEXT DEFAULT (datetime('now'))
    );
  `)

  // Seed default budget floors if not set
  const defaults: Record<string, string> = {
    'budget_floor.web-dev.fixed': '100',
    'budget_floor.web-dev.hourly': '15',
    'budget_floor.ai-auto.fixed': '100',
    'budget_floor.ai-auto.hourly': '10',
    'budget_floor.cms.fixed': '50',
    'budget_floor.cms.hourly': '10',
    'budget_floor.data.fixed': '50',
    'budget_floor.data.hourly': '10',
    'search_terms': JSON.stringify(['framer', 'next.js', 'webflow', 'ai automation']),
  }

  const insert = db.prepare(
    `INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)`
  )
  for (const [key, value] of Object.entries(defaults)) {
    insert.run(key, value)
  }

  // Add new columns to existing jobs table if they don't exist
  try { db.exec(`ALTER TABLE jobs ADD COLUMN proposals_tier TEXT DEFAULT ''`) } catch {}
  try { db.exec(`ALTER TABLE jobs ADD COLUMN url TEXT DEFAULT ''`) } catch {}
}

export function getSearchTerms(): string[] {
  const db = getDb()
  const row = db.prepare(`SELECT value FROM settings WHERE key = 'search_terms'`).get() as { value: string } | undefined
  try { return row ? JSON.parse(row.value) : [] } catch { return [] }
}

export function setSearchTerms(terms: string[]) {
  const db = getDb()
  db.prepare(`INSERT INTO settings (key, value, updated_at) VALUES ('search_terms', ?, datetime('now'))
    ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at`
  ).run(JSON.stringify(terms))
}

export interface RawJob {
  id: string
  title: string
  description: string
  budget: number
  budget_type: 'fixed' | 'hourly'
  category: string
  skills: string[]
  client_verified: boolean
  client_spent: number
  client_rating: number
  client_hire_rate: number
  posted_at: string
  proposals_tier: string
  url: string
}

export function upsertJobs(jobs: RawJob[]) {
  const db = getDb()
  const stmt = db.prepare(`
    INSERT OR IGNORE INTO jobs
      (id, title, description, budget, budget_type, category, skills,
       client_verified, client_spent, client_rating, client_hire_rate,
       posted_at, proposals_tier, url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `)
  const insertMany = db.transaction((rows: RawJob[]) => {
    for (const j of rows) {
      stmt.run(
        j.id, j.title, j.description, j.budget, j.budget_type, j.category,
        JSON.stringify(j.skills), j.client_verified ? 1 : 0, j.client_spent,
        j.client_rating, j.client_hire_rate, j.posted_at, j.proposals_tier, j.url
      )
    }
  })
  insertMany(jobs)
}

export function getBudgetFloors(): Record<string, { fixed: number; hourly: number }> {
  const db = getDb()
  const rows = db.prepare(`SELECT key, value FROM settings WHERE key LIKE 'budget_floor.%'`).all() as { key: string; value: string }[]

  const floors: Record<string, { fixed: number; hourly: number }> = {
    'web-dev': { fixed: 100, hourly: 15 },
    'ai-auto': { fixed: 100, hourly: 10 },
    'cms': { fixed: 50, hourly: 10 },
    'data': { fixed: 50, hourly: 10 },
  }

  for (const row of rows) {
    const parts = row.key.split('.')
    const category = parts[2]
    const type = parts[3] as 'fixed' | 'hourly'
    if (!floors[category]) floors[category] = { fixed: 0, hourly: 0 }
    floors[category][type] = parseFloat(row.value)
  }

  return floors
}
