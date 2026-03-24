import { NextResponse } from 'next/server'
import { getSearchTerms, upsertJobs } from '@/lib/db'
import { fetchJobsForTerm } from '@/lib/rss'

export async function POST() {
  const terms = getSearchTerms()
  if (terms.length === 0) return NextResponse.json({ fetched: 0, terms: [] })

  const results = await Promise.allSettled(terms.map(fetchJobsForTerm))

  let allJobs = results
    .filter((r): r is PromiseFulfilledResult<Awaited<ReturnType<typeof fetchJobsForTerm>>> => r.status === 'fulfilled')
    .flatMap(r => r.value)

  // Deduplicate by id
  const seen = new Set<string>()
  allJobs = allJobs.filter(j => {
    if (seen.has(j.id)) return false
    seen.add(j.id)
    return true
  })

  upsertJobs(allJobs)

  return NextResponse.json({ fetched: allJobs.length, terms })
}
