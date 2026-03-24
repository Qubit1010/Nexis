export interface Job {
  id: string
  title: string
  description: string
  budget: number
  budget_type: 'fixed' | 'hourly'
  category: string
  skills: string[]
  client_verified: boolean
  client_spent: number
  client_rating: number
  client_hire_rate: number
  posted_at: string
  proposals_tier: string
  url: string
  score?: number
}

export type BudgetFloors = Record<string, { fixed: number; hourly: number }>

export function scoreJob(job: Job, floors: BudgetFloors): number {
  const floor = floors[job.category] ?? { fixed: 50, hourly: 10 }

  // Unverified clients: cap total score at 50
  const maxScore = job.client_verified ? 100 : 50

  // Budget score (60 pts max)
  const budgetMin = job.budget_type === 'fixed' ? floor.fixed : floor.hourly
  let budgetScore = 0
  if (job.budget > 0 && budgetMin > 0) {
    const ratio = job.budget / budgetMin
    budgetScore = Math.min(60, Math.round(ratio * 30))
  }

  // Client quality score (40 pts max)
  let clientScore = 0
  if (job.client_verified) {
    clientScore += Math.round((job.client_rating / 5) * 20)
    if (job.client_spent > 0) {
      clientScore += Math.min(20, Math.round(Math.log10(job.client_spent / 100 + 1) * 10))
    }
  }

  // Proposal penalty — fewer bids = better opportunity
  const PROPOSAL_PENALTIES: Record<string, number> = {
    'Less than 5': 0,
    '5 to 10': -5,
    '10 to 15': -10,
    '15 to 20': -15,
    '20 to 50': -25,
    '50+': -40,
  }
  const penalty = PROPOSAL_PENALTIES[job.proposals_tier] ?? 0

  return Math.max(0, Math.min(maxScore, budgetScore + clientScore + penalty))
}

export function getScoreColor(score: number, verified: boolean): string {
  if (!verified) return 'text-gray-400'
  if (score >= 70) return 'text-green-400'
  if (score >= 40) return 'text-yellow-400'
  return 'text-red-400'
}

export function getScoreBg(score: number, verified: boolean): string {
  if (!verified) return 'bg-gray-700 text-gray-400 border-gray-600'
  if (score >= 70) return 'bg-green-900/40 text-green-400 border-green-800'
  if (score >= 40) return 'bg-yellow-900/40 text-yellow-400 border-yellow-800'
  return 'bg-red-900/40 text-red-400 border-red-800'
}
