import { NextRequest, NextResponse } from 'next/server'
import { getDb, getBudgetFloors } from '@/lib/db'
import { DUMMY_JOBS } from '@/data/dummy-jobs'
import { scoreJob } from '@/lib/scorer'

export async function GET() {
  const db = getDb()
  const queue = db.prepare(`SELECT * FROM bid_queue ORDER BY created_at DESC`).all() as {
    id: number; job_id: string; status: string; notes: string; created_at: string
  }[]

  const floors = getBudgetFloors()
  const result = queue.map(q => {
    const job = DUMMY_JOBS.find(j => j.id === q.job_id)
    if (!job) return null
    return { ...job, score: scoreJob(job, floors), queue_id: q.id, status: q.status, notes: q.notes, queued_at: q.created_at }
  }).filter(Boolean)

  return NextResponse.json(result)
}

export async function POST(req: NextRequest) {
  const { jobId, notes = '' } = await req.json()
  const db = getDb()

  const existing = db.prepare(`SELECT id FROM bid_queue WHERE job_id = ?`).get(jobId)
  if (existing) {
    db.prepare(`DELETE FROM bid_queue WHERE job_id = ?`).run(jobId)
    return NextResponse.json({ removed: true })
  }

  db.prepare(`INSERT INTO bid_queue (job_id, notes) VALUES (?, ?)`).run(jobId, notes)
  return NextResponse.json({ added: true })
}

export async function PATCH(req: NextRequest) {
  const { queueId, status, notes } = await req.json()
  const db = getDb()
  db.prepare(`UPDATE bid_queue SET status = ?, notes = ? WHERE id = ?`).run(status, notes ?? '', queueId)
  return NextResponse.json({ ok: true })
}

export async function DELETE(req: NextRequest) {
  const { queueId } = await req.json()
  const db = getDb()
  db.prepare(`DELETE FROM bid_queue WHERE id = ?`).run(queueId)
  return NextResponse.json({ ok: true })
}
