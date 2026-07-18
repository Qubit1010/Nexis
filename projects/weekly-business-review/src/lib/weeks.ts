import fs from "fs";
import path from "path";

const WEEKS_DIR = path.join(process.cwd(), "data", "weeks");

export type UpworkOutcome = "hired" | "interview" | "viewed" | "sent";

export type UpworkProposal = {
  date: string | null;
  title: string;
  connects: number;
  boosted: boolean;
  sender: string;
  outcome: UpworkOutcome;
};

export type OutreachLead = {
  name: string;
  company: string;
  role: string;
  url: string;
  handle: string;
  type: string;
  status: string;
  date: string | null;
};

export type OutreachChannel = {
  available: boolean;
  reason?: string;
  added?: number;
  sent?: number;
  by_type?: { Founder: number; Company: number };
  leads?: OutreachLead[];
};

export type ContentPost = {
  platform: string;
  sentAt: string | null;
  text: string;
  link: string | null;
  metrics: Record<string, number>;
};

export type ProductivityTask = {
  title: string;
  category: string;
  completed_at: string | null;
  minutes: number | null;
  stars: number | null;
};

/* Shape written by .claude/skills/weekly-business-review/scripts/wbr.py */
export type Snapshot = {
  week_key: string;
  label: string;
  start: string;
  end: string;
  generated_at: string;
  upwork: {
    available: boolean;
    reason?: string;
    proposals?: number;
    connects?: number;
    dollars?: number;
    boosted?: number;
    viewed?: number;
    view_rate?: number;
    interviews?: number;
    interview_rate?: number;
    hired?: number;
    hire_rate?: number;
    by_sender?: Record<string, { proposals: number; viewed: number; interviews: number; hired: number }>;
    items?: UpworkProposal[];
  };
  outreach: {
    available: boolean;
    reason?: string;
    totals?: { added: number; sent: number };
    channels?: Record<string, OutreachChannel>;
  };
  content: {
    available: boolean;
    reason?: string;
    totals?: { posts: number };
    platforms?: Record<string, { posts: number; metrics: Record<string, number> }>;
    posts?: ContentPost[];
  };
  productivity: {
    available: boolean;
    reason?: string;
    setup?: string;
    completed?: number;
    hours?: number;
    by_category?: Record<string, number>;
    tasks?: ProductivityTask[];
  };
  website: {
    available: boolean;
    reason?: string;
    planned?: string[];
    sites?: Record<string, string>;
  };
};

export function listWeeks(): string[] {
  if (!fs.existsSync(WEEKS_DIR)) return [];
  return fs
    .readdirSync(WEEKS_DIR)
    .filter((f) => f.endsWith(".json"))
    .map((f) => f.replace(/\.json$/, ""))
    .sort()
    .reverse();
}

export function readWeek(key: string): Snapshot | null {
  // key is a YYYY-MM-DD Monday; guard against path tricks
  if (!/^\d{4}-\d{2}-\d{2}$/.test(key)) return null;
  const file = path.join(WEEKS_DIR, `${key}.json`);
  if (!fs.existsSync(file)) return null;
  return JSON.parse(fs.readFileSync(file, "utf-8")) as Snapshot;
}

export function prevWeekKey(key: string): string {
  const d = new Date(`${key}T00:00:00Z`);
  d.setUTCDate(d.getUTCDate() - 7);
  return d.toISOString().slice(0, 10);
}

/** Resolve the ?week= param to a real snapshot (falling back to the latest week). */
export function resolveWeek(week?: string): { weeks: string[]; key: string; snap: Snapshot; prev: Snapshot | null } | null {
  const weeks = listWeeks();
  const key = week && weeks.includes(week) ? week : weeks[0];
  if (!key) return null;
  const snap = readWeek(key);
  if (!snap) return null;
  return { weeks, key, snap, prev: readWeek(prevWeekKey(key)) };
}
