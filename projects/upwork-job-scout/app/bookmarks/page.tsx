'use client'

import { useEffect, useState } from 'react'
import { Job } from '@/lib/scorer'
import JobCard from '@/components/JobCard'

type BookmarkedJob = Job & { score: number; bookmark_id: number; notes: string; bookmarked_at: string }

export default function BookmarksPage() {
  const [jobs, setJobs] = useState<BookmarkedJob[]>([])
  const [loading, setLoading] = useState(true)

  const load = () => {
    fetch('/api/bookmarks')
      .then(r => r.json())
      .then(data => { setJobs(data); setLoading(false) })
  }

  useEffect(() => { load() }, [])

  const handleRemove = async (jobId: string) => {
    await fetch('/api/bookmarks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ jobId }),
    })
    load()
  }

  return (
    <div className="max-w-3xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-white">
          Bookmarks
          {jobs.length > 0 && (
            <span className="ml-2 text-sm font-normal text-gray-500">{jobs.length}</span>
          )}
        </h1>
        <p className="text-sm text-gray-500 mt-1">Jobs saved for later review</p>
      </div>

      {loading ? (
        <div className="flex flex-col gap-2.5">
          {[...Array(3)].map((_, i) => <div key={i} className="h-36 rounded-lg bg-white/5 animate-pulse" />)}
        </div>
      ) : jobs.length === 0 ? (
        <div className="text-center py-24 text-gray-600">
          <div className="text-4xl mb-4 opacity-30">🔖</div>
          <p className="text-base font-medium text-gray-500 mb-1">No bookmarks yet</p>
          <p className="text-sm">Star a job from the dashboard to save it here</p>
        </div>
      ) : (
        <div className="flex flex-col gap-2.5">
          {jobs.map(job => (
            <JobCard
              key={job.id}
              job={{ ...job, bookmarked: true }}
              onBookmark={handleRemove}
            />
          ))}
        </div>
      )}
    </div>
  )
}
