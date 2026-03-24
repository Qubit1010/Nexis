import 'server-only'
import { XMLParser } from 'fast-xml-parser'
import { RawJob } from './db'

const parser = new XMLParser({ ignoreAttributes: false, attributeNamePrefix: '' })

const CATEGORY_MAP: Record<string, string> = {
  'Web Development': 'web-dev',
  'Web & Mobile Design': 'web-dev',
  'Ecommerce Development': 'web-dev',
  'AI Apps & Integration': 'ai-auto',
  'AI Agents': 'ai-auto',
  'Generative AI': 'ai-auto',
  'Data Science & Analytics': 'data',
  'Data Engineering': 'data',
  'WordPress': 'cms',
  'Shopify': 'cms',
  'Webflow': 'cms',
  'CMS Development': 'cms',
}

function mapCategory(raw: string): string {
  for (const [key, val] of Object.entries(CATEGORY_MAP)) {
    if (raw.toLowerCase().includes(key.toLowerCase())) return val
  }
  return 'web-dev'
}

function stripHtml(html: string): string {
  return html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim()
}

function parseBudget(description: string): { budget: number; budget_type: 'fixed' | 'hourly' } {
  // Hourly: "$10.00-$30.00"
  const hourlyMatch = description.match(/\$[\d,]+\.?\d*\s*[-–]\s*\$[\d,]+\.?\d*\s*(?:\/hr|per hour|hourly)/i)
  if (hourlyMatch) {
    const nums = hourlyMatch[0].match(/[\d,]+\.?\d*/g) ?? []
    const avg = nums.map(n => parseFloat(n.replace(/,/g, ''))).reduce((a, b) => a + b, 0) / (nums.length || 1)
    return { budget: Math.round(avg), budget_type: 'hourly' }
  }

  // Fixed: "Budget: $500" or "Fixed Price: $500"
  const fixedMatch = description.match(/(?:budget|fixed[- ]price)[:\s]+\$?([\d,]+)/i)
  if (fixedMatch) {
    return { budget: parseFloat(fixedMatch[1].replace(/,/g, '')), budget_type: 'fixed' }
  }

  // Single dollar amount fallback
  const singleMatch = description.match(/\$\s*([\d,]+)/)
  if (singleMatch) {
    return { budget: parseFloat(singleMatch[1].replace(/,/g, '')), budget_type: 'fixed' }
  }

  return { budget: 0, budget_type: 'fixed' }
}

function normalizeProposalTier(raw: string): string {
  const map: Record<string, string> = {
    'less than 5': 'Less than 5',
    '5 to 10': '5 to 10',
    '10 to 15': '10 to 15',
    '15 to 20': '15 to 20',
    '20 to 50': '20 to 50',
    '50+': '50+',
  }
  return map[raw?.toLowerCase?.().trim()] ?? raw ?? ''
}

function jobIdFromUrl(url: string): string {
  const match = url.match(/~([a-f0-9]+)/)
  return match ? match[1] : url.replace(/[^a-z0-9]/gi, '').slice(-20)
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function parseItem(item: any): RawJob | null {
  try {
    const title = stripHtml(String(item.title ?? ''))
    const link = String(item.link ?? item.guid?.['#text'] ?? item.guid ?? '')
    const description = stripHtml(String(item.description ?? ''))
    const pubDate = item.pubDate ? new Date(item.pubDate).toISOString() : new Date().toISOString()

    const { budget, budget_type } = parseBudget(description)

    const rawCategory = String(
      item['upwork:job-category-2'] ?? item['upwork:job-category'] ?? ''
    )
    const category = mapCategory(rawCategory)

    const skillsRaw = String(item['upwork:skills'] ?? '')
    const skills = skillsRaw ? skillsRaw.split(',').map(s => s.trim()).filter(Boolean) : []

    const clientFeedback = parseFloat(String(item['upwork:client-feedback'] ?? '0')) || 0
    const clientSpent = parseFloat(String(item['upwork:client-total-spent'] ?? '0')) || 0
    const clientHireRate = parseFloat(String(item['upwork:client-jobs-posted'] ?? '0')) > 0
      ? parseFloat(String(item['upwork:client-total-reviews'] ?? '0')) / parseFloat(String(item['upwork:client-jobs-posted'] ?? '1'))
      : 0
    const clientVerified = clientSpent > 0 || clientFeedback > 0

    const proposalTier = normalizeProposalTier(String(item['upwork:proposals-tier'] ?? ''))

    const id = jobIdFromUrl(link)

    return {
      id,
      title,
      description,
      budget,
      budget_type,
      category,
      skills,
      client_verified: clientVerified,
      client_spent: clientSpent,
      client_rating: clientFeedback,
      client_hire_rate: Math.min(1, clientHireRate),
      posted_at: pubDate,
      proposals_tier: proposalTier,
      url: link,
    }
  } catch {
    return null
  }
}

export async function fetchJobsForTerm(term: string): Promise<RawJob[]> {
  const url = `https://www.upwork.com/ab/feed/jobs/rss?q=${encodeURIComponent(term)}&sort=recency&paging=0%3B50`

  const res = await fetch(url, {
    headers: { 'User-Agent': 'Mozilla/5.0 (compatible; JobScout/1.0)' },
    next: { revalidate: 0 },
  })

  if (!res.ok) throw new Error(`RSS fetch failed for "${term}": ${res.status}`)

  const xml = await res.text()
  const parsed = parser.parse(xml)
  const items = parsed?.rss?.channel?.item ?? []
  const itemArr = Array.isArray(items) ? items : [items]

  return itemArr.map(parseItem).filter((j): j is RawJob => j !== null)
}
