import { eq } from "drizzle-orm";
import { db, schema } from "./db/index.ts";
import { nowIso } from "./lib/time.ts";

export type Format = "linkedin_post" | "personal_blog" | "agency_blog" | "li_newsletter";
export const FORMATS: Format[] = ["linkedin_post", "personal_blog", "agency_blog", "li_newsletter"];
export const FORMAT_LABELS: Record<Format, string> = {
  linkedin_post: "LinkedIn post",
  personal_blog: "Personal blog",
  agency_blog: "Agency blog",
  li_newsletter: "LinkedIn newsletter",
};

export interface FormatEngine {
  model: string;
  maxTurns: number;
  timeoutMin: number;
}

export interface Settings {
  formats: Record<Format, FormatEngine>;
  /** Generate drafts this far ahead of the slot. */
  leadTimeHours: number;
  /** Not approved this close to the slot -> "at risk" in the attention rail. */
  atRiskHours: number;
  /** A blog publish this late is held as missed instead of auto-publishing. */
  blogMaxLateMin: number;
  /** Default publish time (PKT) when an item is planned onto a day without a time. */
  defaultPublishTime: string;
  pauseGeneration: boolean;
  /** No new claude runs start inside this PKT window (keeps interactive usage free). */
  quietHours: { start: string; end: string } | null;
  /** Skip starting a run when the 7-day plan window is this utilized. */
  maxWeeklyUtilization: number;
  /** Weekly cadence targets shown on the calendar. */
  cadence: Record<Format, number>;
  mirror: { enabled: boolean; sheetId: string; tab: string };
  sources: { contentIdeasSheetId: string; scheduleSheetId: string };
  git: { name: string; email: string };
  imageHost: { kind: "supabase"; bucket: string };
}

export const DEFAULT_SETTINGS: Settings = {
  formats: {
    linkedin_post: { model: "sonnet", maxTurns: 60, timeoutMin: 25 },
    personal_blog: { model: "opus", maxTurns: 120, timeoutMin: 60 },
    agency_blog: { model: "opus", maxTurns: 120, timeoutMin: 60 },
    li_newsletter: { model: "sonnet", maxTurns: 40, timeoutMin: 20 },
  },
  leadTimeHours: 48,
  atRiskHours: 12,
  blogMaxLateMin: 720,
  defaultPublishTime: "9:00 am",
  pauseGeneration: false,
  quietHours: null,
  maxWeeklyUtilization: 0.9,
  cadence: { linkedin_post: 2, personal_blog: 3, agency_blog: 3, li_newsletter: 1 },
  mirror: {
    enabled: false,
    sheetId: "13RiOJpxWly5BztZdpLhGK5kT_Unna8Lnc-8GboApJ74",
    // A new tab by default: the existing "SM Schedule" is only taken over at an explicit cutover.
    tab: "SM Schedule (Content OS)",
  },
  sources: {
    contentIdeasSheetId: "",
    scheduleSheetId: "13RiOJpxWly5BztZdpLhGK5kT_Unna8Lnc-8GboApJ74",
  },
  git: { name: "Qubit1010", email: "" },
  imageHost: { kind: "supabase", bucket: "content-os" },
};

export async function getSettings(): Promise<Settings> {
  const rows = await db.select().from(schema.settings);
  const merged: Record<string, unknown> = structuredClone(DEFAULT_SETTINGS) as unknown as Record<string, unknown>;
  for (const r of rows) {
    try {
      const v = JSON.parse(r.valueJson);
      const base = merged[r.key];
      merged[r.key] =
        base && typeof base === "object" && !Array.isArray(base) && v && typeof v === "object" ? deepMerge(base, v) : v;
    } catch {
      /* ignore a corrupt row, defaults stand */
    }
  }
  return merged as unknown as Settings;
}

function deepMerge(a: any, b: any): any {
  const out = { ...a };
  for (const [k, v] of Object.entries(b)) {
    out[k] = v && typeof v === "object" && !Array.isArray(v) && a[k] && typeof a[k] === "object" ? deepMerge(a[k], v) : v;
  }
  return out;
}

export async function putSettings(patch: Partial<Settings>): Promise<Settings> {
  const now = nowIso();
  for (const [key, value] of Object.entries(patch)) {
    if (!(key in DEFAULT_SETTINGS)) continue;
    await db
      .insert(schema.settings)
      .values({ key, valueJson: JSON.stringify(value), updatedAt: now })
      .onConflictDoUpdate({ target: schema.settings.key, set: { valueJson: JSON.stringify(value), updatedAt: now } });
  }
  return getSettings();
}

export async function deleteSetting(key: string): Promise<void> {
  await db.delete(schema.settings).where(eq(schema.settings.key, key));
}
