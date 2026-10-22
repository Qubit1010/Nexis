// One-way mirror: Content OS -> a Google Sheet tab, so the team and a phone can see
// the schedule. Whole-tab clear + write every time (never positional partial
// writes), and nothing is ever read back. Section rows repeat per week, like the
// hand-kept SM Schedule.
import { db, schema } from "../db/index.ts";
import { fmtClock, fmtSheetDate, fmtSheetDay, pktParts } from "../lib/time.ts";
import { emit } from "../lib/events.ts";
import { getSettings, FORMAT_LABELS, type Format } from "../settings.ts";
import { safeParse } from "../engine/contract.ts";
import { replaceTab } from "./gws.ts";

const HEADER = ["Date", "Day", "Platform", "Format", "Topic / Idea", "Post Description", "Reference", "Content Mode", "Pillars", "Final Video/Post", "Publish Time", "Status", "Channel", "Content OS ID"];
const SECTION_ORDER: [Format, string][] = [
  ["personal_blog", "Blog Posts"],
  ["linkedin_post", "Posts"],
  ["agency_blog", "Agency Blog Posts"],
  ["li_newsletter", "Newsletter"],
];
const STATUS_LABEL: Record<string, string> = {
  planned: "Planned",
  generating: "Generating",
  review: "In Review",
  approved: "Approved",
  scheduled: "Scheduled",
  ready_to_post: "Ready to Post",
  publishing: "Publishing",
  published: "Published",
  failed: "Failed",
  missed: "Missed",
  skipped: "Cancelled",
};
const PLATFORM: Record<Format, string> = { linkedin_post: "LinkedIn", personal_blog: "Blog", agency_blog: "Blog", li_newsletter: "LinkedIn" };

function weekKey(iso: string): string {
  const p = pktParts(iso);
  const d = new Date(Date.UTC(p.y, p.m - 1, p.d));
  const dow = (d.getUTCDay() + 6) % 7; // Monday = 0
  d.setUTCDate(d.getUTCDate() - dow);
  return d.toISOString().slice(0, 10);
}

export async function buildMirrorRows(): Promise<string[][]> {
  const items = (await db.select().from(schema.contentItems)).filter((i) => i.scheduledFor);
  const channels = new Map((await db.select().from(schema.channels)).map((c) => [c.id, c.name]));
  const weeks = new Map<string, typeof items>();
  for (const i of items) {
    const k = weekKey(i.scheduledFor!);
    if (!weeks.has(k)) weeks.set(k, []);
    weeks.get(k)!.push(i);
  }
  const rows: string[][] = [HEADER];
  for (const week of [...weeks.keys()].sort()) {
    const inWeek = weeks.get(week)!;
    for (const [format, label] of SECTION_ORDER) {
      const group = inWeek.filter((i) => i.format === format).sort((a, b) => a.scheduledFor!.localeCompare(b.scheduledFor!));
      if (!group.length) continue;
      rows.push([label]);
      for (const i of group) {
        const b = safeParse(i.briefJson);
        rows.push([
          fmtSheetDate(i.scheduledFor!),
          fmtSheetDay(i.scheduledFor!),
          PLATFORM[i.format as Format] ?? "",
          FORMAT_LABELS[i.format as Format] ?? i.format,
          i.title,
          String(b.description ?? ""),
          String(b.reference ?? ""),
          String(b.contentMode ?? ""),
          String(b.pillar ?? ""),
          i.publishedUrl || i.docUrl || "",
          fmtClock(i.scheduledFor!),
          STATUS_LABEL[i.status] ?? i.status,
          i.channelId ? channels.get(i.channelId) ?? "" : "",
          i.id,
        ]);
      }
    }
  }
  return rows;
}

export async function mirrorSchedule(): Promise<unknown> {
  const s = await getSettings();
  if (!s.mirror.enabled) return { skipped: "mirror disabled in Settings" };
  if (s.mirror.tab.trim().toLowerCase() === "sm schedule") {
    // Guard against clobbering the hand-kept tab by accident: only an explicit cutover writes there.
    const confirmed = (s.mirror as { cutoverConfirmed?: boolean }).cutoverConfirmed;
    if (!confirmed) return { skipped: "refusing to overwrite the hand-kept SM Schedule tab without a confirmed cutover" };
  }
  const rows = await buildMirrorRows();
  await replaceTab(s.mirror.sheetId, s.mirror.tab, rows);
  emit("scheduler", "system", null, "mirror.synced", { tab: s.mirror.tab, rows: rows.length });
  return { tab: s.mirror.tab, rows: rows.length };
}
