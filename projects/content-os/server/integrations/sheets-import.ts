// One-time (and safely repeatable) import of the existing Google Sheets:
//   Daily Brief - Content Ideas  -> ideas  (Youtube bookmarked, Saved Articles, Content Opportunities)
//   Weekly Posting Schedule / Topics Ideas -> ideas (paired category/reference columns; strikethrough = used)
//   Weekly Posting Schedule / SM Schedule  -> content items (section rows set the format)
// Idempotent: ideas dedupe on URL/title, items are keyed on their sheet row.
import { eq } from "drizzle-orm";
import { db, schema } from "../db/index.ts";
import { rootEnv } from "../config.ts";
import { parseClock, parseMonthDay, pktParts, pktToIso } from "../lib/time.ts";
import { emit } from "../lib/events.ts";
import { getSettings, type Format } from "../settings.ts";
import { ingestIdea, type IdeaInputT } from "../ideas.ts";
import { planItem } from "../items.ts";
import { readTab, readTabGrid, sheetTabs } from "./gws.ts";

const IDEA_STATUS: Record<string, IdeaInputT["status"]> = { new: "inbox", "": "inbox", old: "archived", posted: "used", used: "used" };
const FORMAT_WORDS = new Set(["comparison", "tutorial", "explainer", "news", "demo", "deep-dive", "content idea", "case study", "opinion"]);

function headerIndex(header: string[], ...names: string[]): number {
  const lower = header.map((h) => (h || "").trim().toLowerCase());
  for (const n of names) {
    const i = lower.indexOf(n.toLowerCase());
    if (i >= 0) return i;
  }
  return -1;
}

export interface ImportReport {
  dryRun: boolean;
  ideas: { tab: string; rows: number; added: number; duplicates: number }[];
  items: { rows: number; created: number; existing: number; skipped: number; byFormat: Record<string, number>; byStatus: Record<string, number> };
  warnings: string[];
}

// ---- Content Ideas spreadsheet ----

function contentIdeaRows(tab: string, values: string[][]): IdeaInputT[] {
  const [header = [], ...rows] = values;
  const col = (...n: string[]) => headerIndex(header, ...n);
  const iTitle = col("Title");
  const iUrl = col("URL");
  const iStatus = col("Status");
  const out: IdeaInputT[] = [];
  rows.forEach((r, idx) => {
    const title = (r[iTitle] || "").trim();
    if (!title) return;
    const url = iUrl >= 0 ? (r[iUrl] || "").trim() || null : null;
    const status = IDEA_STATUS[(r[iStatus] || "").trim().toLowerCase()] ?? "inbox";
    const sourceRef = `sheet:${tab}!${idx + 2}`;
    if (tab === "Youtube bookmarked") {
      const channel = (r[col("Channel")] || "").trim();
      const source = url ? "youtube_video" : FORMAT_WORDS.has(channel.toLowerCase()) ? "youtube_idea" : "youtube_topic";
      out.push({
        title,
        url,
        source,
        sourceRef,
        status,
        summary: null,
        payload: { channel, views: r[col("Views")] || null, publishedDate: r[col("Published Date")] || null, dateSaved: r[col("Date Saved")] || null },
      });
    } else if (tab === "Saved Articles") {
      out.push({ title, url, source: "news_article", sourceRef, status, summary: (r[col("TLDR")] || "").trim() || null, payload: { publisher: r[col("Source")] || null, briefDate: r[col("Brief Date")] || null } });
    } else {
      out.push({
        title,
        url,
        source: "practical_idea",
        sourceRef,
        status,
        summary: [r[col("Angle")], r[col("Hook")]].filter(Boolean).join("\n\n") || null,
        payload: { format: r[col("Format")] || null, keyPoints: r[col("Key Points")] || null, relatedTrends: r[col("Related Trends")] || null },
      });
    }
  });
  return out;
}

// ---- Topics Ideas tab ----

function topicsIdeaRows(grid: { value: string; struck: boolean }[][]): IdeaInputT[] {
  const header = (grid[0] || []).map((c) => c.value.trim());
  // Category columns are the ones whose right-hand neighbour is a "Reference/Description" column.
  const cats: { col: number; name: string }[] = [];
  header.forEach((h, i) => {
    if (h && !/^reference/i.test(h) && /^reference/i.test(header[i + 1] || "")) cats.push({ col: i, name: h });
  });
  const out: IdeaInputT[] = [];
  for (const cat of cats) {
    let week: string | null = null;
    for (let r = 1; r < grid.length; r++) {
      const cell = grid[r]?.[cat.col];
      const raw = (cell?.value || "").trim();
      if (!raw) continue;
      if (/^\d{4}-\d{2}-\d{2}$/.test(raw)) {
        week = raw;
        continue;
      }
      const ref = (grid[r]?.[cat.col + 1]?.value || "").trim();
      const extraUrl = (grid[r]?.[cat.col + 2]?.value || "").trim();
      const extraSummary = (grid[r]?.[cat.col + 3]?.value || "").trim();
      const title = raw.replace(/^-\s*/, "").replace(/\s+/g, " ").slice(0, 480);
      const url = [ref, extraUrl].find((s) => /^https?:\/\//.test(s)) || null;
      out.push({
        title,
        url,
        summary: (extraSummary || (url === ref ? "" : ref)).slice(0, 4000) || null,
        source: "topics_sheet",
        sourceRef: `sheet:Topics Ideas!${String.fromCharCode(65 + cat.col)}${r + 1}`,
        status: cell?.struck ? "used" : "shortlisted",
        payload: { category: cat.name, reference: ref || null, week },
      });
    }
  }
  return out;
}

// ---- SM Schedule tab ----

const SECTIONS: Record<string, Format> = {
  "blog posts": "personal_blog",
  posts: "linkedin_post",
  "agency blog posts": "agency_blog",
  newsletter: "li_newsletter",
};
const ITEM_STATUS: Record<string, string> = { published: "published", cancelled: "skipped", canceled: "skipped", planned: "planned", draft: "planned", scheduled: "planned" };

interface ScheduleRow {
  row: number;
  format: Format;
  scheduledFor: string;
  status: string;
  title: string;
  brief: Record<string, unknown>;
  docUrl: string | null;
  publishedUrl: string | null;
}

export function parseSchedule(values: string[][], today = new Date(), defaultTime = "9:00 am"): { rows: ScheduleRow[]; skipped: number; warnings: string[] } {
  const [header = [], ...body] = values;
  const col = (...n: string[]) => headerIndex(header, ...n);
  const c = {
    date: col("Date"),
    platform: col("Platform", "Media Platform"),
    postType: col("Post Type"),
    topic: col("Topic / Idea", "Topic/Idea", "Topic"),
    description: col("Post Description", "Description"),
    reference: col("Reference"),
    format: col("Format"),
    contentMode: col("Content Mode"),
    pillars: col("Pillars"),
    designTemplate: col("Design Template"),
    final: col("Final Video/Post", "Final Post", "Final Video / Post"),
    publishTime: col("Publish Time"),
    status: col("Status"),
    notes: col("Notes"),
  };
  const warnings: string[] = [];
  if (c.date < 0 || c.topic < 0) return { rows: [], skipped: body.length, warnings: ["SM Schedule has no Date or Topic / Idea header"] };

  // Pass 1: sections + month/day, keeping sheet order.
  type Raw = { row: number; md: { m: number; d: number; y?: number }; section: Format | null; r: string[] };
  const raws: Raw[] = [];
  let section: Format | null = null;
  let skipped = 0;
  body.forEach((r, i) => {
    const first = (r[c.date] || "").trim();
    const sec = SECTIONS[first.toLowerCase()];
    if (sec) {
      section = sec;
      return;
    }
    const topic = (r[c.topic] || "").trim();
    const md = parseMonthDay(first);
    if (!topic || !md) {
      if (topic || first) skipped++;
      return;
    }
    raws.push({ row: i + 2, md, section, r });
  });

  // Pass 2: years. Dates carry no year; walk backward from the last row, anchoring it to the
  // year that puts it closest to today. The sheet is chronological, so reading upward the
  // month normally falls; it only jumps up across a year boundary (Dec sitting above Jan),
  // which is the one place to step back a year.
  const t = pktParts(today.toISOString());
  let year = t.y;
  if (raws.length) {
    const last = raws[raws.length - 1].md;
    const cand = [t.y - 1, t.y, t.y + 1].map((y) => ({ y, dist: Math.abs(Date.UTC(y, last.m - 1, last.d) - Date.UTC(t.y, t.m - 1, t.d)) }));
    year = cand.sort((a, b) => a.dist - b.dist)[0].y;
  }
  const years: number[] = new Array(raws.length);
  for (let i = raws.length - 1; i >= 0; i--) {
    const md = raws[i].md;
    if (md.y) year = md.y;
    else if (i < raws.length - 1) {
      const next = raws[i + 1].md;
      if (md.m - next.m > 6) year--;
    }
    years[i] = md.y ?? year;
  }

  const rows: ScheduleRow[] = [];
  raws.forEach((raw, i) => {
    const r = raw.r;
    const postType = (r[c.postType] || "").toLowerCase();
    const platform = (r[c.platform] || "").toLowerCase();
    const fmtCell = (r[c.format] || "").toLowerCase();
    let format: Format | null = raw.section;
    if (!format) {
      if (postType.includes("reel")) {
        skipped++;
        return; // reels belong to reel-creator, not Content OS phase 1
      }
      format = fmtCell.includes("newsletter") ? "li_newsletter" : platform === "blog" || fmtCell.includes("blog") ? "personal_blog" : "linkedin_post";
    }
    const clock = parseClock(r[c.publishTime]) ?? parseClock(defaultTime) ?? { h: 9, min: 0 };
    const scheduledFor = pktToIso(years[i], raw.md.m, raw.md.d, clock.h, clock.min);
    const rawStatus = (r[c.status] || "").trim().toLowerCase();
    let status = ITEM_STATUS[rawStatus] ?? "planned";
    if (status === "planned" && Date.parse(scheduledFor) < today.getTime() - 2 * 86_400_000) status = "skipped"; // never happened
    const final = (r[c.final] || "").trim();
    const isUrl = /^https?:\/\//.test(final);
    const isDoc = /docs\.google\.com/.test(final);
    rows.push({
      row: raw.row,
      format,
      scheduledFor,
      status,
      title: (r[c.topic] || "").trim().replace(/^[“"]|[”"]$/g, ""),
      brief: {
        topic: (r[c.topic] || "").trim(),
        description: (r[c.description] || "").trim(),
        reference: (r[c.reference] || "").trim(),
        contentMode: (r[c.contentMode] || "").trim(),
        pillar: (r[c.pillars] || "").trim(),
        designTemplate: (r[c.designTemplate] || "").trim(),
        notes: [(r[c.notes] || "").trim(), rawStatus && !ITEM_STATUS[rawStatus] ? `sheet status: ${rawStatus}` : ""].filter(Boolean).join(" | "),
        importedFrom: `SM Schedule row ${raw.row}`,
      },
      docUrl: isDoc ? final : null,
      publishedUrl: isUrl && !isDoc && status === "published" ? final : null,
    });
  });
  return { rows, skipped, warnings };
}

// ---- Orchestration ----

export async function importSheets(opts: { dryRun: boolean; sources?: ("content_ideas" | "topics" | "schedule")[] }): Promise<ImportReport> {
  const s = await getSettings();
  const sources = opts.sources ?? ["content_ideas", "topics", "schedule"];
  const report: ImportReport = { dryRun: opts.dryRun, ideas: [], items: { rows: 0, created: 0, existing: 0, skipped: 0, byFormat: {}, byStatus: {} }, warnings: [] };
  const ingest = async (tab: string, rows: IdeaInputT[]) => {
    const entry = { tab, rows: rows.length, added: 0, duplicates: 0 };
    if (!opts.dryRun) {
      for (const r of rows) {
        const res = await ingestIdea(r, "import");
        if (res.duplicate) entry.duplicates++;
        else entry.added++;
      }
    }
    report.ideas.push(entry);
  };

  if (sources.includes("content_ideas")) {
    const sheetId = s.sources.contentIdeasSheetId || rootEnv().GOOGLE_SHEETS_SPREADSHEET_ID;
    if (!sheetId) report.warnings.push("no Content Ideas sheet id (GOOGLE_SHEETS_SPREADSHEET_ID)");
    else {
      const tabs = (await sheetTabs(sheetId)).map((t) => t.title);
      for (const tab of ["Youtube bookmarked", "Saved Articles", "Content Opportunities"]) {
        if (!tabs.includes(tab)) continue;
        await ingest(tab, contentIdeaRows(tab, await readTab(sheetId, tab)));
      }
    }
  }
  if (sources.includes("topics")) {
    const grid = await readTabGrid(s.sources.scheduleSheetId, "Topics Ideas");
    await ingest("Topics Ideas", topicsIdeaRows(grid));
  }
  if (sources.includes("schedule")) {
    const values = await readTab(s.sources.scheduleSheetId, "SM Schedule");
    const parsed = parseSchedule(values, new Date(), s.defaultPublishTime);
    report.warnings.push(...parsed.warnings);
    report.items.rows = parsed.rows.length;
    report.items.skipped = parsed.skipped;
    for (const row of parsed.rows) {
      report.items.byFormat[row.format] = (report.items.byFormat[row.format] || 0) + 1;
      report.items.byStatus[row.status] = (report.items.byStatus[row.status] || 0) + 1;
      const sheetRef = `sm:${row.row}`;
      const exists = await db.select({ id: schema.contentItems.id }).from(schema.contentItems).where(eq(schema.contentItems.sheetRef, sheetRef)).get();
      if (exists) {
        report.items.existing++;
        continue;
      }
      if (opts.dryRun) continue;
      const item = await planItem({ format: row.format, title: row.title, scheduledFor: row.scheduledFor, brief: row.brief, sheetRef, status: row.status, docUrl: row.docUrl });
      if (row.publishedUrl || row.status === "published") {
        await db.update(schema.contentItems).set({ publishedUrl: row.publishedUrl, publishedAt: row.status === "published" ? row.scheduledFor : null }).where(eq(schema.contentItems.id, item.id));
      }
      report.items.created++;
    }
  }
  if (!opts.dryRun) emit("user", "system", null, "sheets.imported", report);
  return report;
}

export { contentIdeaRows, topicsIdeaRows };
