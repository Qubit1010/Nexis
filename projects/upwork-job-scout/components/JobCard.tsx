'use client'

import { Job } from '@/lib/scorer'
import ScoreBadge from './ScoreBadge'
import { useState, useEffect } from 'react'
import { Bookmark, BookmarkCheck, Plus, CheckCircle2, BadgeCheck } from 'lucide-react'

const VISITED_KEY = 'scout:visited'

function getVisited(): Set<string> {
  try {
    const raw = localStorage.getItem(VISITED_KEY)
    return new Set(raw ? JSON.parse(raw) : [])
  } catch { return new Set() }
}

function markVisited(id: string) {
  const visited = getVisited()
  visited.add(id)
  localStorage.setItem(VISITED_KEY, JSON.stringify([...visited]))
}

interface Props {
  job: Job & { score: number; bookmarked?: boolean; queued?: boolean }
  onBookmark?: (jobId: string) => void
  onQueue?: (jobId: string) => void
}

const CATEGORY_COLORS: Record<string, { bg: string; text: string; border: string; accent: string }> = {
  'web-dev':  { bg: 'bg-sky-500/10',    text: 'text-sky-400',    border: 'border-sky-500/20',   accent: 'bg-sky-500' },
  'ai-auto':  { bg: 'bg-violet-500/10', text: 'text-violet-400', border: 'border-violet-500/20', accent: 'bg-violet-500' },
  'cms':      { bg: 'bg-amber-500/10',  text: 'text-amber-400',  border: 'border-amber-500/20',  accent: 'bg-amber-500' },
  'data':     { bg: 'bg-emerald-500/10',text: 'text-emerald-400',border: 'border-emerald-500/20',accent: 'bg-emerald-500' },
}

const CATEGORY_LABELS: Record<string, string> = {
  'web-dev': 'Web Dev',
  'ai-auto': 'AI / Auto',
  'cms': 'CMS',
  'data': 'Data',
}

function timeAgo(isoString: string): string {
  const diff = Date.now() - new Date(isoString).getTime()
  const hours = Math.floor(diff / 3600000)
  if (hours < 1) return 'just now'
  if (hours < 24) return `${hours}h ago`
  return `${Math.floor(hours / 24)}d ago`
}

export default function JobCard({ job, onBookmark, onQueue }: Props) {
  const [bookmarked, setBookmarked] = useState(job.bookmarked ?? false)
  const [queued, setQueued] = useState(job.queued ?? false)
  const [visited, setVisited] = useState(false)

  useEffect(() => {
    setVisited(getVisited().has(job.id))
  }, [job.id])

  const handleOpen = () => {
    markVisited(job.id)
    setVisited(true)
  }

  const handleBookmark = () => {
    setBookmarked(!bookmarked)
    onBookmark?.(job.id)
  }

  const handleQueue = () => {
    setQueued(!queued)
    onQueue?.(job.id)
  }

  const dimmed = !job.client_verified
  const cat = CATEGORY_COLORS[job.category] ?? CATEGORY_COLORS['web-dev']
  const isNew = (Date.now() - new Date(job.posted_at).getTime()) < 6 * 3600000

  function proposalStyle(tier: string): string {
    if (!tier) return ''
    if (tier === 'Less than 5') return 'text-green-400'
    if (tier === '5 to 10') return 'text-yellow-400'
    return 'text-gray-500'
  }

  function proposalLabel(tier: string): string {
    const map: Record<string, string> = {
      'Less than 5': '< 5 bids',
      '5 to 10': '5-10 bids',
      '10 to 15': '10-15 bids',
      '15 to 20': '15-20 bids',
      '20 to 50': '20-50 bids',
      '50+': '50+ bids',
    }
    return map[tier] ?? ''
  }

  const accentStrip = dimmed
    ? 'bg-gray-600/30'
    : job.score >= 70
    ? 'bg-green-500'
    : job.score >= 40
    ? 'bg-yellow-500'
    : 'bg-red-500/60'

  return (
    <div
      className={`group relative rounded-lg border overflow-hidden transition-all duration-150 pl-1 ${
        dimmed
          ? 'border-white/5 bg-[#282828]/60 opacity-60 hover:opacity-80'
          : 'border-white/10 bg-[#2a2a2a] hover:border-white/20 hover:bg-[#2d2d2d]'
      }`}
    >
      {/* Left accent strip */}
      <div className={`absolute left-0 top-0 bottom-0 w-[3px] ${accentStrip}`} />

      <div className="flex items-start gap-4 p-4">
        {/* Main content */}
        <div className="flex-1 min-w-0">
          {/* Top meta row */}
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${cat.bg} ${cat.text} border ${cat.border}`}>
              {CATEGORY_LABELS[job.category] ?? job.category}
            </span>
            {!job.client_verified && (
              <span className="text-xs px-2 py-0.5 rounded-full bg-gray-700/50 text-gray-500 border border-gray-600/50">
                Unverified
              </span>
            )}
            {isNew && (
              <span className="text-xs px-2 py-0.5 rounded-full bg-[#208ec7]/20 text-[#208ec7] border border-[#208ec7]/30 font-medium">
                New
              </span>
            )}
            <span className="text-xs text-gray-600">{timeAgo(job.posted_at)}</span>
          </div>

          {/* Title */}
          <div className="flex items-center gap-2 mb-2">
            <a
              href={job.url || '#'}
              target="_blank"
              rel="noopener noreferrer"
              onClick={handleOpen}
              className={`font-semibold text-sm leading-snug line-clamp-1 hover:underline ${
                visited ? 'text-gray-500' : dimmed ? 'text-gray-400' : 'text-white'
              }`}
            >
              {job.title}
            </a>
            {visited && (
              <span className="shrink-0 text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-gray-600 border border-white/5 leading-none">
                seen
              </span>
            )}
          </div>

          {/* Description */}
          <p className="text-xs text-gray-500 line-clamp-2 mb-3 leading-relaxed">
            {job.description}
          </p>

          {/* Budget + client signals */}
          <div className="flex items-center gap-3 flex-wrap">
            <span className={`text-sm font-bold ${dimmed ? 'text-gray-500' : cat.text}`}>
              {job.budget_type === 'fixed'
                ? `$${job.budget.toLocaleString()}`
                : `$${job.budget}/hr`}
              <span className="text-xs font-normal text-gray-500 ml-1">
                {job.budget_type === 'fixed' ? 'fixed' : 'hourly'}
              </span>
            </span>

            {job.client_verified ? (
              <div className="flex items-center gap-2 text-xs text-gray-400">
                <span className="flex items-center gap-1 text-green-400">
                  <BadgeCheck size={12} />
                  Verified
                </span>
                {job.client_rating > 0 && (
                  <span className="text-yellow-400">{job.client_rating.toFixed(1)}★</span>
                )}
                {job.client_spent > 0 && (
                  <span>
                    ${job.client_spent >= 1000
                      ? `${(job.client_spent / 1000).toFixed(0)}k`
                      : job.client_spent} spent
                  </span>
                )}
                {job.client_hire_rate > 0 && (
                  <span>{Math.round(job.client_hire_rate * 100)}% hire</span>
                )}
              </div>
            ) : null}
            {job.proposals_tier && (
              <span className={`text-xs ${proposalStyle(job.proposals_tier)}`}>
                {proposalLabel(job.proposals_tier)}
              </span>
            )}
          </div>

          {/* Skills */}
          {job.skills.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2.5">
              {job.skills.slice(0, 5).map(skill => (
                <span
                  key={skill}
                  className="text-xs px-1.5 py-0.5 rounded bg-white/5 text-gray-500 border border-white/5"
                >
                  {skill}
                </span>
              ))}
              {job.skills.length > 5 && (
                <span className="text-xs px-1.5 py-0.5 rounded bg-white/5 text-gray-600 border border-white/5">
                  +{job.skills.length - 5}
                </span>
              )}
            </div>
          )}
        </div>

        {/* Right side: score + actions */}
        <div className="flex flex-col items-center gap-3 shrink-0">
          <ScoreBadge score={job.score} verified={job.client_verified} />

          <div className="flex gap-1">
            <button
              onClick={handleBookmark}
              title={bookmarked ? 'Remove bookmark' : 'Bookmark'}
              className={`p-1.5 rounded-md transition-all duration-150 ${
                bookmarked
                  ? 'text-[#208ec7] bg-[#208ec7]/15 hover:bg-[#208ec7]/25'
                  : 'text-gray-600 hover:text-gray-300 hover:bg-white/8'
              }`}
            >
              {bookmarked
                ? <BookmarkCheck size={15} />
                : <Bookmark size={15} />}
            </button>
            <button
              onClick={handleQueue}
              title={queued ? 'Remove from queue' : 'Add to bid queue'}
              className={`p-1.5 rounded-md transition-all duration-150 ${
                queued
                  ? 'text-green-400 bg-green-900/20 hover:bg-green-900/30'
                  : 'text-gray-600 hover:text-gray-300 hover:bg-white/8'
              }`}
            >
              {queued
                ? <CheckCircle2 size={15} />
                : <Plus size={15} />}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
