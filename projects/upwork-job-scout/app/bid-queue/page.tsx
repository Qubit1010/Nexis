'use client'

import { useEffect, useState } from 'react'
import { Job } from '@/lib/scorer'
import ScoreBadge from '@/components/ScoreBadge'
import { BadgeCheck, Trash2 } from 'lucide-react'

type QueuedJob = Job & {
  score: number
  queue_id: number
  status: 'pending' | 'sent' | 'won' | 'lost'
  notes: string
  queued_at: string
}

const STATUSES = [
  { value: 'pending', label: 'Pending', style: 'data-[active=true]:bg-yellow-900/40 data-[active=true]:text-yellow-300 data-[active=true]:border-yellow-700/60' },
  { value: 'sent',    label: 'Sent',    style: 'data-[active=true]:bg-blue-900/40 data-[active=true]:text-blue-300 data-[active=true]:border-blue-700/60' },
  { value: 'won',     label: 'Won',     style: 'data-[active=true]:bg-green-900/40 data-[active=true]:text-green-300 data-[active=true]:border-green-700/60' },
  { value: 'lost',    label: 'Lost',    style: 'data-[active=true]:bg-red-900/40 data-[active=true]:text-red-300 data-[active=true]:border-red-700/60' },
]

const STAT_STYLES: Record<string, { bg: string; text: string; border: string }> = {
  pending: { bg: 'bg-yellow-900/20', text: 'text-yellow-400', border: 'border-yellow-800/40' },
  sent:    { bg: 'bg-blue-900/20',   text: 'text-blue-400',   border: 'border-blue-800/40' },
  won:     { bg: 'bg-green-900/20',  text: 'text-green-400',  border: 'border-green-800/40' },
  lost:    { bg: 'bg-red-900/20',    text: 'text-red-400',    border: 'border-red-800/40' },
}

export default function BidQueuePage() {
  const [jobs, setJobs] = useState<QueuedJob[]>([])
  const [loading, setLoading] = useState(true)

  const load = () => {
    fetch('/api/bid-queue')
      .then(r => r.json())
      .then(data => { setJobs(data); setLoading(false) })
  }

  useEffect(() => { load() }, [])

  const updateStatus = async (queueId: number, status: string, notes: string) => {
    await fetch('/api/bid-queue', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ queueId, status, notes }),
    })
    load()
  }

  const removeFromQueue = async (queueId: number) => {
    await fetch('/api/bid-queue', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ queueId }),
    })
    load()
  }

  const counts = {
    pending: jobs.filter(j => j.status === 'pending').length,
    sent:    jobs.filter(j => j.status === 'sent').length,
    won:     jobs.filter(j => j.status === 'won').length,
    lost:    jobs.filter(j => j.status === 'lost').length,
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-white">Bid Queue</h1>
        <p className="text-sm text-gray-500 mt-1">Track your bids from queue to close</p>
      </div>

      {/* Stats */}
      {jobs.length > 0 && (
        <div className="grid grid-cols-4 gap-3 mb-6">
          {Object.entries(counts).map(([status, count]) => {
            const s = STAT_STYLES[status]
            return (
              <div key={status} className={`rounded-xl border p-4 text-center ${s.bg} ${s.border}`}>
                <p className={`text-3xl font-bold leading-none mb-1 ${s.text}`}>{count}</p>
                <p className="text-xs text-gray-500 capitalize">{status}</p>
              </div>
            )
          })}
        </div>
      )}

      {loading ? (
        <div className="flex flex-col gap-2.5">
          {[...Array(3)].map((_, i) => <div key={i} className="h-24 rounded-lg bg-white/5 animate-pulse" />)}
        </div>
      ) : jobs.length === 0 ? (
        <div className="text-center py-24 text-gray-600">
          <div className="text-4xl mb-4 opacity-30">📋</div>
          <p className="text-base font-medium text-gray-500 mb-1">Bid queue is empty</p>
          <p className="text-sm">Add jobs from the dashboard using the + button</p>
        </div>
      ) : (
        <div className="flex flex-col gap-2.5">
          {jobs.map(job => (
            <div key={job.queue_id} className="rounded-lg border border-white/10 bg-[#2a2a2a] hover:border-white/20 transition-colors p-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-sm text-white leading-snug mb-2 line-clamp-1">{job.title}</h3>

                  <div className="flex items-center gap-2 text-xs text-gray-500 mb-3">
                    {job.client_verified
                      ? <span className="flex items-center gap-1 text-green-400"><BadgeCheck size={12} /> Verified</span>
                      : <span className="text-gray-600">Unverified</span>}
                    {job.client_rating > 0 && <span className="text-yellow-400">{job.client_rating.toFixed(1)}★</span>}
                    <span>{job.budget_type === 'fixed' ? `$${job.budget.toLocaleString()} fixed` : `$${job.budget}/hr`}</span>
                  </div>

                  {/* Inline status pills */}
                  <div className="flex gap-1.5 flex-wrap">
                    {STATUSES.map(s => (
                      <button
                        key={s.value}
                        data-active={job.status === s.value}
                        onClick={() => updateStatus(job.queue_id, s.value, job.notes)}
                        className={`px-2.5 py-1 rounded-full text-xs font-medium border transition-all
                          bg-white/5 text-gray-500 border-white/10 hover:text-gray-300 hover:border-white/20
                          ${s.style}`}
                      >
                        {s.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="flex flex-col items-center gap-3 shrink-0">
                  <ScoreBadge score={job.score} verified={job.client_verified} />
                  <button
                    onClick={() => removeFromQueue(job.queue_id)}
                    className="p-1.5 rounded-md text-gray-600 hover:text-red-400 hover:bg-red-900/10 transition-all"
                    title="Remove from queue"
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
