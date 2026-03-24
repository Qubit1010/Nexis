import { NextRequest, NextResponse } from 'next/server'
import { getDb, getSearchTerms, setSearchTerms } from '@/lib/db'

export async function GET() {
  const db = getDb()
  const rows = db.prepare(`SELECT key, value FROM settings WHERE key LIKE 'budget_floor.%'`).all() as {
    key: string; value: string
  }[]

  const floors: Record<string, Record<string, number>> = {}
  for (const row of rows) {
    const [, , category, type] = row.key.split('.')
    if (!floors[category]) floors[category] = {}
    floors[category][type] = parseFloat(row.value)
  }

  return NextResponse.json({ floors, searchTerms: getSearchTerms() })
}

export async function PUT(req: NextRequest) {
  const body = await req.json() as {
    floors?: Record<string, { fixed: number; hourly: number }>
    searchTerms?: string[]
  }
  const db = getDb()

  if (body.floors) {
    const upsert = db.prepare(
      `INSERT INTO settings (key, value, updated_at) VALUES (?, ?, datetime('now'))
       ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at`
    )
    for (const [category, values] of Object.entries(body.floors)) {
      upsert.run(`budget_floor.${category}.fixed`, String(values.fixed))
      upsert.run(`budget_floor.${category}.hourly`, String(values.hourly))
    }
  }

  if (body.searchTerms !== undefined) {
    setSearchTerms(body.searchTerms)
  }

  return NextResponse.json({ ok: true })
}
