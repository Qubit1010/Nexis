'use client'

import { useEffect, useState } from 'react'
import { X, RefreshCw } from 'lucide-react'

type Floors = Record<string, { fixed: number; hourly: number }>

const CATEGORIES = [
  { id: 'web-dev', label: 'Web Dev' },
  { id: 'ai-auto', label: 'AI / Automation' },
  { id: 'cms', label: 'CMS' },
  { id: 'data', label: 'Data Analysis' },
]

export default function SettingsPage() {
  const [floors, setFloors] = useState<Floors>({})
  const [searchTerms, setSearchTerms] = useState<string[]>([])
  const [termInput, setTermInput] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [fetching, setFetching] = useState(false)
  const [fetchResult, setFetchResult] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/settings')
      .then(r => r.json())
      .then(data => {
        setFloors(data.floors ?? {})
        setSearchTerms(data.searchTerms ?? [])
        setLoading(false)
      })
  }, [])

  const updateFloor = (category: string, type: 'fixed' | 'hourly', value: string) => {
    setFloors(prev => ({
      ...prev,
      [category]: { ...prev[category], [type]: parseFloat(value) || 0 },
    }))
    setSaved(false)
  }

  const addTerm = () => {
    const t = termInput.trim().toLowerCase()
    if (!t || searchTerms.includes(t)) return
    setSearchTerms(prev => [...prev, t])
    setTermInput('')
    setSaved(false)
  }

  const removeTerm = (t: string) => {
    setSearchTerms(prev => prev.filter(s => s !== t))
    setSaved(false)
  }

  const save = async () => {
    setSaving(true)
    await fetch('/api/settings', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ floors, searchTerms }),
    })
    setSaving(false)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const fetchNow = async () => {
    setFetching(true)
    setFetchResult(null)
    try {
      // Save terms first so fetcher uses latest
      await fetch('/api/settings', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ searchTerms }),
      })
      const res = await fetch('/api/fetch-jobs', { method: 'POST' })
      const data = await res.json()
      setFetchResult(`Fetched ${data.fetched} jobs across ${data.terms.length} search terms`)
    } catch {
      setFetchResult('Fetch failed — check console')
    }
    setFetching(false)
  }

  return (
    <div className="max-w-lg mx-auto p-6 space-y-8">
      <div>
        <h1 className="text-xl font-semibold text-white">Settings</h1>
        <p className="text-sm text-gray-500 mt-1">Configure job fetching and scoring thresholds</p>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => <div key={i} className="h-16 rounded-lg bg-white/5 animate-pulse" />)}
        </div>
      ) : (
        <>
          {/* Search Terms */}
          <div>
            <p className="text-[10px] text-gray-500 uppercase tracking-widest mb-3 font-medium">Search Terms</p>
            <div className="flex gap-1 mb-3">
              <input
                value={termInput}
                onChange={e => setTermInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && addTerm()}
                placeholder="e.g. framer, webflow, next.js..."
                className="flex-1 bg-white/5 border border-white/10 rounded-md px-3 py-1.5 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-[#208ec7]/50 transition-colors"
              />
              <button
                onClick={addTerm}
                className="px-3 py-1.5 rounded-md bg-[#208ec7]/15 text-[#208ec7] text-sm hover:bg-[#208ec7]/25 transition-colors border border-[#208ec7]/20 font-medium"
              >
                Add
              </button>
            </div>

            {searchTerms.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mb-3">
                {searchTerms.map(t => (
                  <span
                    key={t}
                    className="flex items-center gap-1 text-xs px-2.5 py-1 rounded-full bg-[#208ec7]/15 text-[#208ec7] border border-[#208ec7]/20"
                  >
                    {t}
                    <button onClick={() => removeTerm(t)} className="hover:text-white transition-colors ml-0.5">
                      <X size={10} />
                    </button>
                  </span>
                ))}
              </div>
            )}

            <button
              onClick={fetchNow}
              disabled={fetching || searchTerms.length === 0}
              className="flex items-center gap-2 px-4 py-2 rounded-md bg-white/5 border border-white/10 text-sm text-gray-300 hover:bg-white/8 hover:border-white/20 transition-all disabled:opacity-40"
            >
              <RefreshCw size={13} className={fetching ? 'animate-spin' : ''} />
              {fetching ? 'Fetching...' : 'Fetch Now'}
            </button>

            {fetchResult && (
              <p className="text-xs text-gray-400 mt-2">{fetchResult}</p>
            )}
          </div>

          {/* Budget Floors */}
          <div>
            <p className="text-[10px] text-gray-500 uppercase tracking-widest mb-3 font-medium">Budget Floors</p>
            <div className="rounded-xl border border-white/10 bg-[#252525] overflow-hidden">
              <div className="grid grid-cols-3 gap-0 px-5 py-3 border-b border-white/8 bg-white/2 text-[10px] text-gray-500 uppercase tracking-widest font-medium">
                <span>Category</span>
                <span>Fixed Min ($)</span>
                <span>Hourly Min ($/hr)</span>
              </div>

              {CATEGORIES.map((cat, i) => (
                <div
                  key={cat.id}
                  className={`grid grid-cols-3 gap-4 items-center px-5 py-3.5 hover:bg-white/2 transition-colors ${i < CATEGORIES.length - 1 ? 'border-b border-white/5' : ''}`}
                >
                  <span className="text-sm text-gray-300 font-medium">{cat.label}</span>
                  <div className="relative">
                    <span className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-500 text-xs">$</span>
                    <input
                      type="number"
                      min={0}
                      value={floors[cat.id]?.fixed ?? ''}
                      onChange={e => updateFloor(cat.id, 'fixed', e.target.value)}
                      className="bg-white/5 border border-white/10 rounded-md pl-6 pr-2 py-1.5 text-sm text-white focus:outline-none focus:border-[#208ec7]/50 focus:bg-white/8 transition-colors w-full"
                    />
                  </div>
                  <div className="relative">
                    <span className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-500 text-xs">$</span>
                    <input
                      type="number"
                      min={0}
                      value={floors[cat.id]?.hourly ?? ''}
                      onChange={e => updateFloor(cat.id, 'hourly', e.target.value)}
                      className="bg-white/5 border border-white/10 rounded-md pl-6 pr-2 py-1.5 text-sm text-white focus:outline-none focus:border-[#208ec7]/50 focus:bg-white/8 transition-colors w-full"
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      <div className="flex items-center gap-3">
        <button
          onClick={save}
          disabled={saving || loading}
          className="px-4 py-2 rounded bg-gradient-to-r from-[#208ec7] to-[#1f5b99] text-white text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
        >
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
        {saved && <span className="text-xs text-green-400">Saved</span>}
      </div>

      <div className="rounded-xl border border-white/5 bg-white/2 p-4">
        <p className="text-xs text-gray-500 font-medium mb-2 uppercase tracking-wider">How scoring works</p>
        <p className="text-xs text-gray-500 leading-relaxed">
          Score is 0-100: budget vs floor = 60%, client quality = 40%. Unverified clients capped at 50. Proposal count applies a penalty: 20-50 bids = -25, 50+ bids = -40.
        </p>
      </div>
    </div>
  )
}
