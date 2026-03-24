import { NextRequest, NextResponse } from 'next/server'
import { getDb, getBudgetFloors } from '@/lib/db'
import { DUMMY_JOBS } from '@/data/dummy-jobs'
import { scoreJob } from '@/lib/scorer'

export async function GET() {
  const db = getDb()
  const bookmarks = db.prepare(`SELECT * FROM bookmarks ORDER BY created_at DESC`).all() as {
    id: number; job_id: string; notes: string; created_at: string
  }[]

  const floors = getBudgetFloors()
  const result = bookmarks.map(b => {
    const job = DUMMY_JOBS.find(j => j.id === b.job_id)
    if (!job) return null
    return { ...job, score: scoreJob(job, floors), bookmark_id: b.id, notes: b.notes, bookmarked_at: b.created_at }
  }).filter(Boolean)

  return NextResponse.json(result)
}

export async function POST(req: NextRequest) {
  const { jobId, notes = '' } = await req.json()
  const db = getDb()

  const existing = db.prepare(`SELECT id FROM bookmarks WHERE job_id = ?`).get(jobId)
  if (existing) {
    db.prepare(`DELETE FROM bookmarks WHERE job_id = ?`).run(jobId)
    return NextResponse.json({ removed: true })
  }

  db.prepare(`INSERT INTO bookmarks (job_id, notes) VALUES (?, ?)`).run(jobId, notes)
  return NextResponse.json({ added: true })
}

export async function DELETE(req: NextRequest) {
  const { jobId } = await req.json()
  const db = getDb()
  db.prepare(`DELETE FROM bookmarks WHERE job_id = ?`).run(jobId)
  return NextResponse.json({ ok: true })
}
