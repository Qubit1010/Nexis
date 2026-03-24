'use client'

import { useState, useEffect, useMemo } from 'react'
import FilterSidebar, { Filters } from '@/components/FilterSidebar'
import JobCard from '@/components/JobCard'
import { Job } from '@/lib/scorer'
import { RefreshCw } from 'lucide-react'

type SortOption = 'score' | 'newest' | 'budget'

const SORT_OPTIONS: { value: SortOption; label: string }[] = [
  { value: 'score',   label: 'Best Match' },
  { value: 'newest',  label: 'Newest' },
  { value: 'budget',  label: 'Budget' },
]

export default function Home() {
  const [jobs, setJobs] = useState<(Job & { score: number })[]>([])
  const [loading, setLoading] = useState(true)
  const [sort, setSort] = useState<SortOption>('score')
  const [filters, setFilters] = useState<Filters>({
    categories: [],
    keywords: [],
    minBudget: 0,
    budgetType: 'all',
    verifiedOnly: false,
    timeWindow: 'all',
  })

  const load = () => {
    setLoading(true)
    fetch('/api/jobs')
      .then(r => r.json())
      .then(data => { setJobs(data); setLoading(false) })
  }

  useEffect(() => { load() }, [])

  const handleBookmark = async (jobId: string) => {
    await fetch('/api/bookmarks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ jobId }),
    })
  }

  const handleQueue = async (jobId: string) => {
    await fetch('/api/bid-queue', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ jobId }),
    })
  }

  const filtered = useMemo(() => {
    let result = [...jobs]

    if (filters.categories.length > 0) {
      result = result.filter(j => filters.categories.includes(j.category))
    }
    if (filters.keywords.length > 0) {
      result = result.filter(j =>
        filters.keywords.some(kw =>
          j.title.toLowerCase().includes(kw.toLowerCase()) ||
          j.description.toLowerCase().includes(kw.toLowerCase()) ||
          j.skills.some(s => s.toLowerCase().includes(kw.toLowerCase()))
        )
      )
    }
    if (filters.minBudget > 0) {
      result = result.filter(j => j.budget >= filters.minBudget)
    }
    if (filters.budgetType !== 'all') {
      result = result.filter(j => j.budget_type === filters.budgetType)
    }
    if (filters.verifiedOnly) {
      result = result.filter(j => j.client_verified)
    }
    if (filters.timeWindow !== 'all') {
      const hours = filters.timeWindow === '6h' ? 6 : filters.timeWindow === '12h' ? 12 : 24
      const cutoff = Date.now() - hours * 3600000
      result = result.filter(j => new Date(j.posted_at).getTime() >= cutoff)
    }

    if (sort === 'score')   result.sort((a, b) => b.score - a.score)
    else if (sort === 'budget')  result.sort((a, b) => b.budget - a.budget)
    else result.sort((a, b) => new Date(b.posted_at).getTime() - new Date(a.posted_at).getTime())

    return result
  }, [jobs, filters, sort])

  return (
    <div className="flex gap-8 p-6 max-w-6xl mx-auto">
      <FilterSidebar
        filters={filters}
        onChange={setFilters}
        totalJobs={jobs.length}
        filteredJobs={filtered.length}
      />

      <div className="flex-1 min-w-0">
        {/* Toolbar */}
        <div className="flex items-center justify-between mb-4">
          {/* Sort pills */}
          <div className="flex items-center gap-1">
            {SORT_OPTIONS.map(opt => (
              <button
                key={opt.value}
                onClick={() => setSort(opt.value)}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  sort === opt.value
                    ? 'bg-[#208ec7]/20 text-[#208ec7] border border-[#208ec7]/30'
                    : 'text-gray-500 hover:text-gray-300 border border-transparent hover:border-white/10 hover:bg-white/5'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>

          {/* Refresh */}
          <button
            onClick={load}
            disabled={loading}
            title="Refresh jobs"
            className="p-1.5 rounded-md text-gray-500 hover:text-gray-300 hover:bg-white/5 transition-colors disabled:opacity-40"
          >
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>

        {/* Job list */}
        {loading ? (
          <div className="flex flex-col gap-2.5">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-36 rounded-lg bg-white/4 animate-pulse" />
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-24 text-gray-600">
            <div className="text-4xl mb-4 opacity-30">🔍</div>
            <p className="text-base font-medium text-gray-500 mb-1">No jobs match your filters</p>
            <p className="text-sm">Try adjusting your keywords or category filters</p>
          </div>
        ) : (
          <div className="flex flex-col gap-2.5">
            {filtered.map(job => (
              <JobCard
                key={job.id}
                job={job}
                onBookmark={handleBookmark}
                onQueue={handleQueue}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
