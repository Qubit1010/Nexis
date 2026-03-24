'use client'

import { useState } from 'react'
import { X, RotateCcw } from 'lucide-react'

export interface Filters {
  categories: string[]
  keywords: string[]
  minBudget: number
  budgetType: 'all' | 'fixed' | 'hourly'
  verifiedOnly: boolean
  timeWindow: 'all' | '6h' | '12h' | '24h'
}

interface Props {
  filters: Filters
  onChange: (filters: Filters) => void
  totalJobs: number
  filteredJobs: number
}

const CATEGORIES = [
  { id: 'web-dev',  label: 'Web Dev',       color: 'data-[active=true]:bg-sky-500/20 data-[active=true]:text-sky-400 data-[active=true]:border-sky-500/40' },
  { id: 'ai-auto',  label: 'AI / Auto',      color: 'data-[active=true]:bg-violet-500/20 data-[active=true]:text-violet-400 data-[active=true]:border-violet-500/40' },
  { id: 'cms',      label: 'CMS',            color: 'data-[active=true]:bg-amber-500/20 data-[active=true]:text-amber-400 data-[active=true]:border-amber-500/40' },
  { id: 'data',     label: 'Data',           color: 'data-[active=true]:bg-emerald-500/20 data-[active=true]:text-emerald-400 data-[active=true]:border-emerald-500/40' },
]

const SECTION = 'text-[10px] text-gray-500 uppercase tracking-widest mb-2 font-medium'
const DIVIDER = 'border-t border-white/5 pt-4'

export default function FilterSidebar({ filters, onChange, totalJobs, filteredJobs }: Props) {
  const [keywordInput, setKeywordInput] = useState('')

  const toggleCategory = (id: string) => {
    const next = filters.categories.includes(id)
      ? filters.categories.filter(c => c !== id)
      : [...filters.categories, id]
    onChange({ ...filters, categories: next })
  }

  const addKeyword = () => {
    const kw = keywordInput.trim()
    if (!kw || filters.keywords.includes(kw)) return
    onChange({ ...filters, keywords: [...filters.keywords, kw] })
    setKeywordInput('')
  }

  const removeKeyword = (kw: string) => {
    onChange({ ...filters, keywords: filters.keywords.filter(k => k !== kw) })
  }

  const resetFilters = () => {
    onChange({ categories: [], keywords: [], minBudget: 0, budgetType: 'all', verifiedOnly: false, timeWindow: 'all' })
  }

  const hasActiveFilters =
    filters.categories.length > 0 ||
    filters.keywords.length > 0 ||
    filters.minBudget > 0 ||
    filters.budgetType !== 'all' ||
    filters.verifiedOnly ||
    filters.timeWindow !== 'all'

  return (
    <aside className="w-52 shrink-0 flex flex-col gap-5 sticky top-[57px] self-start max-h-[calc(100vh-57px)] overflow-y-auto pb-4">
      {/* Job count */}
      <div className="flex items-baseline justify-between">
        <p className="text-white font-semibold text-sm">
          {filteredJobs}
          <span className="text-gray-500 font-normal"> jobs</span>
        </p>
        {filteredJobs !== totalJobs && (
          <span className="text-[11px] text-gray-600">of {totalJobs}</span>
        )}
      </div>

      {/* Categories */}
      <div>
        <p className={SECTION}>Category</p>
        <div className="grid grid-cols-2 gap-1.5">
          {CATEGORIES.map(cat => {
            const active = filters.categories.includes(cat.id)
            return (
              <button
                key={cat.id}
                data-active={active}
                onClick={() => toggleCategory(cat.id)}
                className={`px-2.5 py-1.5 rounded-md text-xs font-medium border transition-all duration-150 text-left
                  ${active
                    ? ''
                    : 'bg-white/5 text-gray-400 border-white/10 hover:text-gray-300 hover:border-white/20'
                  } ${cat.color}`}
              >
                {cat.label}
              </button>
            )
          })}
        </div>
      </div>

      {/* Keywords */}
      <div className={DIVIDER}>
        <p className={SECTION}>Keywords</p>
        <div className="flex gap-1 mb-2">
          <input
            value={keywordInput}
            onChange={e => setKeywordInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && addKeyword()}
            placeholder="Add keyword..."
            className="flex-1 bg-white/5 border border-white/10 rounded-md px-2.5 py-1.5 text-xs text-white placeholder-gray-600 focus:outline-none focus:border-[#208ec7]/50 focus:bg-white/8 transition-colors min-w-0"
          />
          <button
            onClick={addKeyword}
            className="px-2.5 py-1.5 rounded-md bg-[#208ec7]/15 text-[#208ec7] text-xs hover:bg-[#208ec7]/25 transition-colors border border-[#208ec7]/20 font-medium"
          >
            +
          </button>
        </div>
        {filters.keywords.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {filters.keywords.map(kw => (
              <span
                key={kw}
                className="flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-[#208ec7]/15 text-[#208ec7] border border-[#208ec7]/20"
              >
                {kw}
                <button
                  onClick={() => removeKeyword(kw)}
                  className="hover:text-white transition-colors ml-0.5"
                >
                  <X size={10} />
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Budget type */}
      <div className={DIVIDER}>
        <p className={SECTION}>Budget Type</p>
        <div className="flex gap-1">
          {(['all', 'fixed', 'hourly'] as const).map(type => (
            <button
              key={type}
              onClick={() => onChange({ ...filters, budgetType: type })}
              className={`flex-1 py-1.5 rounded-md text-xs font-medium transition-all capitalize ${
                filters.budgetType === type
                  ? 'bg-[#208ec7]/20 text-[#208ec7] border border-[#208ec7]/30'
                  : 'bg-white/5 text-gray-400 hover:text-gray-300 border border-white/10 hover:border-white/20'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* Min budget */}
      <div className={DIVIDER}>
        <p className={SECTION}>Min Budget</p>
        <div className="relative">
          <span className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-500 text-xs font-medium">$</span>
          <input
            type="number"
            min={0}
            value={filters.minBudget || ''}
            onChange={e => onChange({ ...filters, minBudget: parseFloat(e.target.value) || 0 })}
            placeholder="0"
            className="w-full bg-white/5 border border-white/10 rounded-md pl-6 pr-2 py-1.5 text-xs text-white placeholder-gray-600 focus:outline-none focus:border-[#208ec7]/50 focus:bg-white/8 transition-colors"
          />
        </div>
      </div>

      {/* Time window */}
      <div className={DIVIDER}>
        <p className={SECTION}>Posted</p>
        <div className="flex gap-1">
          {(['all', '6h', '12h', '24h'] as const).map(tw => (
            <button
              key={tw}
              onClick={() => onChange({ ...filters, timeWindow: tw })}
              className={`flex-1 py-1.5 rounded-md text-xs font-medium transition-all ${
                filters.timeWindow === tw
                  ? 'bg-[#208ec7]/20 text-[#208ec7] border border-[#208ec7]/30'
                  : 'bg-white/5 text-gray-400 hover:text-gray-300 border border-white/10 hover:border-white/20'
              }`}
            >
              {tw === 'all' ? 'All' : tw}
            </button>
          ))}
        </div>
      </div>

      {/* Verified only */}
      <div className={DIVIDER}>
        <label className="flex items-center gap-2.5 cursor-pointer group select-none">
          <div
            onClick={() => onChange({ ...filters, verifiedOnly: !filters.verifiedOnly })}
            className={`w-4 h-4 rounded border flex items-center justify-center transition-all cursor-pointer shrink-0 ${
              filters.verifiedOnly
                ? 'bg-[#208ec7] border-[#208ec7]'
                : 'border-white/20 group-hover:border-white/40'
            }`}
          >
            {filters.verifiedOnly && (
              <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                <path d="M2 5L4 7L8 3" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            )}
          </div>
          <span
            onClick={() => onChange({ ...filters, verifiedOnly: !filters.verifiedOnly })}
            className="text-sm text-gray-400 group-hover:text-gray-300 transition-colors"
          >
            Verified only
          </span>
        </label>
      </div>

      {/* Reset */}
      {hasActiveFilters && (
        <button
          onClick={resetFilters}
          className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-300 transition-colors"
        >
          <RotateCcw size={11} />
          Reset filters
        </button>
      )}
    </aside>
  )
}
