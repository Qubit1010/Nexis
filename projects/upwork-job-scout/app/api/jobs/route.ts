import { NextResponse } from 'next/server'
import { getDb, getBudgetFloors } from '@/lib/db'
import { scoreJob, Job } from '@/lib/scorer'

// Dummy data — used when DB has no jobs (real Upwork API coming soon)
const DUMMY_JOBS: Job[] = [
  {
    id: 'dummy-1',
    title: 'Build a Framer website for SaaS startup',
    description: 'We need a beautiful marketing site built in Framer. Must be responsive and match our Figma designs. We have a tight timeline of 2 weeks.',
    budget: 1200,
    budget_type: 'fixed',
    category: 'web-dev',
    skills: ['Framer', 'UI Design', 'Responsive Design', 'Figma'],
    client_verified: true,
    client_spent: 8500,
    client_rating: 4.9,
    client_hire_rate: 0.72,
    posted_at: new Date(Date.now() - 2 * 3600000).toISOString(),
    proposals_tier: 'Less than 5',
    url: '#',
  },
  {
    id: 'dummy-2',
    title: 'Next.js developer for fintech dashboard',
    description: 'Looking for an experienced Next.js developer to build a real-time financial dashboard. Must have experience with server components, Tailwind, and REST APIs.',
    budget: 45,
    budget_type: 'hourly',
    category: 'web-dev',
    skills: ['Next.js', 'TypeScript', 'Tailwind CSS', 'REST APIs'],
    client_verified: true,
    client_spent: 32000,
    client_rating: 4.7,
    client_hire_rate: 0.65,
    posted_at: new Date(Date.now() - 4 * 3600000).toISOString(),
    proposals_tier: '5 to 10',
    url: '#',
  },
  {
    id: 'dummy-3',
    title: 'AI automation for lead generation pipeline',
    description: 'We want to automate our entire lead gen process using AI. Need someone to build an n8n/Python workflow that scrapes leads, enriches them, and sends personalized cold emails.',
    budget: 2500,
    budget_type: 'fixed',
    category: 'ai-auto',
    skills: ['n8n', 'Python', 'OpenAI API', 'Automation', 'LangChain'],
    client_verified: true,
    client_spent: 15000,
    client_rating: 5.0,
    client_hire_rate: 0.80,
    posted_at: new Date(Date.now() - 1 * 3600000).toISOString(),
    proposals_tier: 'Less than 5',
    url: '#',
  },
  {
    id: 'dummy-4',
    title: 'Webflow redesign for e-commerce brand',
    description: 'Our current Webflow site looks dated. We need a full redesign that improves conversions. You will work from existing brand guidelines and our Figma prototype.',
    budget: 800,
    budget_type: 'fixed',
    category: 'cms',
    skills: ['Webflow', 'UI Design', 'CMS', 'E-commerce'],
    client_verified: true,
    client_spent: 4200,
    client_rating: 4.6,
    client_hire_rate: 0.55,
    posted_at: new Date(Date.now() - 8 * 3600000).toISOString(),
    proposals_tier: '10 to 15',
    url: '#',
  },
  {
    id: 'dummy-5',
    title: 'WordPress custom plugin development',
    description: 'Need a custom WooCommerce plugin that integrates with our warehouse management system via API. Must handle inventory sync and order routing.',
    budget: 600,
    budget_type: 'fixed',
    category: 'cms',
    skills: ['WordPress', 'PHP', 'WooCommerce', 'API Integration'],
    client_verified: false,
    client_spent: 0,
    client_rating: 0,
    client_hire_rate: 0,
    posted_at: new Date(Date.now() - 12 * 3600000).toISOString(),
    proposals_tier: '20 to 50',
    url: '#',
  },
  {
    id: 'dummy-6',
    title: 'Build AI chatbot for customer support',
    description: 'Looking for someone to build a RAG-based chatbot trained on our documentation. Should integrate with our existing Intercom setup and handle 80% of tier-1 support queries.',
    budget: 3500,
    budget_type: 'fixed',
    category: 'ai-auto',
    skills: ['LangChain', 'RAG', 'OpenAI', 'Python', 'Chatbot'],
    client_verified: true,
    client_spent: 22000,
    client_rating: 4.8,
    client_hire_rate: 0.70,
    posted_at: new Date(Date.now() - 3 * 3600000).toISOString(),
    proposals_tier: '5 to 10',
    url: '#',
  },
  {
    id: 'dummy-7',
    title: 'Data analysis and visualization — sales data',
    description: 'We have 2 years of sales data in CSV files. Need someone to clean, analyze, and build an interactive dashboard (Plotly or similar) showing key business metrics.',
    budget: 25,
    budget_type: 'hourly',
    category: 'data',
    skills: ['Python', 'Pandas', 'Plotly', 'Data Analysis', 'Excel'],
    client_verified: true,
    client_spent: 3000,
    client_rating: 4.5,
    client_hire_rate: 0.45,
    posted_at: new Date(Date.now() - 6 * 3600000).toISOString(),
    proposals_tier: '15 to 20',
    url: '#',
  },
  {
    id: 'dummy-8',
    title: 'Framer expert for product landing page',
    description: 'Quick project — need a high-converting product landing page in Framer. We have the copy and brand assets ready. Just need execution.',
    budget: 400,
    budget_type: 'fixed',
    category: 'web-dev',
    skills: ['Framer', 'Landing Page', 'UI Design'],
    client_verified: true,
    client_spent: 1200,
    client_rating: 4.3,
    client_hire_rate: 0.60,
    posted_at: new Date(Date.now() - 30 * 60000).toISOString(),
    proposals_tier: 'Less than 5',
    url: '#',
  },
]

export async function GET() {
  const db = getDb()
  const floors = getBudgetFloors()

  const rows = db.prepare(`SELECT * FROM jobs ORDER BY posted_at DESC`).all() as {
    id: string; title: string; description: string; budget: number; budget_type: string;
    category: string; skills: string; client_verified: number; client_spent: number;
    client_rating: number; client_hire_rate: number; posted_at: string;
    proposals_tier: string; url: string;
  }[]

  // Fall back to dummy data if DB is empty (until Upwork API is connected)
  if (rows.length === 0) {
    return NextResponse.json(
      DUMMY_JOBS.map(job => ({ ...job, score: scoreJob(job, floors) }))
    )
  }

  const jobs = rows.map(row => {
    const job = {
      ...row,
      skills: (() => { try { return JSON.parse(row.skills ?? '[]') } catch { return [] } })(),
      client_verified: Boolean(row.client_verified),
      budget_type: row.budget_type as 'fixed' | 'hourly',
      proposals_tier: row.proposals_tier ?? '',
      url: row.url ?? '',
    }
    return { ...job, score: scoreJob(job, floors) }
  })

  return NextResponse.json(jobs)
}
