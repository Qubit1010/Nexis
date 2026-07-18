/**
 * Daily digest: read today's News Brief + Practical AI from the SQLite DB, log a
 * one-row-per-day summary into a Google Sheet, and email it. Read + notify only —
 * generation happens first, in the existing crons (see run-digest.cmd, the
 * scheduled-task target that runs daily-cron -> daily-tools -> this).
 *
 *   npx tsx scripts/daily-digest.ts                 # digest today, log + email
 *   npx tsx scripts/daily-digest.ts 2026-07-18      # a specific date
 *   npx tsx scripts/daily-digest.ts --no-email      # log to the sheet only
 *   npx tsx scripts/daily-digest.ts --schedule      # register the noon task
 *   npx tsx scripts/daily-digest.ts --unschedule    # remove it
 */
import { config } from "dotenv";
import { resolve, join } from "path";
import { existsSync, readFileSync, writeFileSync } from "fs";
import { spawnSync } from "child_process";
import Database from "better-sqlite3";

config({ path: resolve(__dirname, "..", ".env") });

import { createDigestSpreadsheet, upsertRowByDate, sendEmail, formatDigestTab } from "./gws";

const PROJECT = resolve(__dirname, "..");
const DB_PATH = join(PROJECT, "data", "news.db");
const SHEET_STATE = join(PROJECT, "data", "digest-sheet.json");
const TASK_NAME = "NexisDailyBrief";
const NEWS_TAB = "News Brief";
const PRACTICAL_TAB = "Practical AI";
const DIGEST_EMAIL = process.env.DIGEST_EMAIL || "hassanaleem86@gmail.com";
const DASHBOARD_URL = process.env.DIGEST_DASHBOARD_URL || "http://localhost:3000";

const NEWS_HEADER = ["Date", "Sentiment", "Top Takeaway", "Trends", "Top Stories", "Generated"];
const PRACTICAL_HEADER = ["Date", "Topics", "Top Pick", "Workflow Recipe", "Content Ideas", "Generated"];
const NEWS_WIDTHS = [90, 85, 260, 250, 380, 110];
const PRACTICAL_WIDTHS = [90, 130, 250, 250, 380, 110];

function jparse<T>(s: string | null | undefined, fallback: T): T {
  if (!s) return fallback;
  try {
    return JSON.parse(s) as T;
  } catch {
    return fallback;
  }
}

// --- Read today's briefs from SQLite (read-only; the app owns writes) ---

interface NewsDigest {
  sentimentLabel: string;
  sentimentSummary: string;
  takeaway: string;
  trends: Array<{ title: string; momentum: string; summary: string }>;
  stories: Array<{ title: string; source: string; url: string; sources: number }>;
}

interface PracticalDigest {
  topics: string[];
  topPick: { name: string; oneLiner: string } | null;
  recipe: { title: string; subtitle: string; agent: string; timeSaved: string | null } | null;
  insight: string;
  ideas: Array<{ title: string; format: string; hook: string }>;
}

function readNews(db: Database.Database, date: string): NewsDigest | null {
  const brief = db
    .prepare("SELECT id, overall_sentiment, top_takeaway FROM briefs WHERE date = ?")
    .get(date) as { id: number; overall_sentiment: string; top_takeaway: string } | undefined;
  if (!brief) return null;
  const sentiment = jparse<{ label?: string; summary?: string }>(brief.overall_sentiment, {});
  const trends = db
    .prepare("SELECT title, momentum_signal, summary FROM trends WHERE brief_id = ? ORDER BY sort_order")
    .all(brief.id) as Array<{ title: string; momentum_signal: string; summary: string }>;
  const stories = db
    .prepare(
      `SELECT a.title, a.source, a.url, a.source_count FROM articles a
       JOIN categories c ON a.category_id = c.id
       WHERE c.brief_id = ?
       ORDER BY a.source_count DESC, a.relevance_score DESC LIMIT 6`
    )
    .all(brief.id) as Array<{ title: string; source: string; url: string; source_count: number }>;
  return {
    sentimentLabel: sentiment.label || "n/a",
    sentimentSummary: sentiment.summary || "",
    takeaway: brief.top_takeaway || "",
    trends: trends.map((t) => ({ title: t.title, momentum: t.momentum_signal, summary: t.summary })),
    stories: stories.map((s) => ({ title: s.title, source: s.source, url: s.url, sources: s.source_count })),
  };
}

function readPractical(db: Database.Database, date: string): PracticalDigest | null {
  const tb = db
    .prepare("SELECT id, top_pick_tool_id, cross_domain_insight FROM tool_briefs WHERE date = ?")
    .get(date) as { id: number; top_pick_tool_id: number | null; cross_domain_insight: string } | undefined;
  if (!tb) return null;
  const topics = (
    db.prepare("SELECT name FROM tool_categories WHERE brief_id = ? ORDER BY sort_order").all(tb.id) as Array<{
      name: string;
    }>
  ).map((r) => r.name);
  // Prefer the stored top pick; fall back to a best-in-domain card (tool-run only
  // stores top_pick_tool_id when the synthesis name exactly matches a card, which
  // often misses) so the digest reliably shows a pick.
  const topPick =
    (tb.top_pick_tool_id
      ? (db.prepare("SELECT name, one_liner FROM tools WHERE id = ?").get(tb.top_pick_tool_id) as
          | { name: string; one_liner: string }
          | undefined)
      : undefined) ||
    (db
      .prepare(
        `SELECT t.name, t.one_liner FROM tools t
         JOIN tool_categories c ON t.category_id = c.id
         WHERE c.brief_id = ?
         ORDER BY t.is_best_in_domain DESC, t.relevance_score DESC LIMIT 1`
      )
      .get(tb.id) as { name: string; one_liner: string } | undefined);
  const recipe = db
    .prepare("SELECT title, subtitle, agent, time_saved FROM workflow_recipes WHERE brief_id = ?")
    .get(tb.id) as { title: string; subtitle: string; agent: string; time_saved: string | null } | undefined;
  const ideas = db
    .prepare("SELECT title, format, hook FROM tool_content_ideas WHERE brief_id = ? ORDER BY sort_order")
    .all(tb.id) as Array<{ title: string; format: string; hook: string }>;
  return {
    topics,
    topPick: topPick ? { name: topPick.name, oneLiner: topPick.one_liner } : null,
    recipe: recipe
      ? { title: recipe.title, subtitle: recipe.subtitle, agent: recipe.agent, timeSaved: recipe.time_saved }
      : null,
    insight: tb.cross_domain_insight || "",
    ideas,
  };
}

// --- Sheet rows ---

function newsRow(date: string, n: NewsDigest, now: string): string[] {
  const trends = n.trends.map((t) => `- ${t.title} (${t.momentum})`).join("\n\n");
  const stories = n.stories.map((s) => `- ${s.title} [${s.source}]\n${s.url}`).join("\n\n");
  return [date, n.sentimentLabel, n.takeaway, trends, stories, now];
}

function practicalRow(date: string, p: PracticalDigest, now: string): string[] {
  const topPick = p.topPick ? `${p.topPick.name} - ${p.topPick.oneLiner}` : "(none)";
  const recipe = p.recipe
    ? `${p.recipe.title} (${p.recipe.agent}${p.recipe.timeSaved ? `, ${p.recipe.timeSaved}` : ""})`
    : "(none)";
  const ideas = p.ideas.map((i) => `- [${i.format}] ${i.title}`).join("\n\n");
  return [date, p.topics.join(", "), topPick, recipe, ideas, now];
}

// --- Email ---

function esc(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function buildEmail(date: string, n: NewsDigest | null, p: PracticalDigest | null): string {
  const parts: string[] = [
    `<div style="font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;max-width:680px;margin:0 auto;color:#1a1a1a;line-height:1.5">`,
    `<h1 style="font-size:20px;margin:0 0 4px">Daily Brief - ${date}</h1>`,
    `<p style="color:#666;font-size:13px;margin:0 0 20px">NexusPoint intelligence digest</p>`,
  ];

  if (n) {
    parts.push(`<h2 style="font-size:16px;border-bottom:2px solid #eee;padding-bottom:6px">News Brief</h2>`);
    parts.push(
      `<p><strong>Sentiment:</strong> ${esc(n.sentimentLabel)}${n.sentimentSummary ? ` - ${esc(n.sentimentSummary)}` : ""}</p>`
    );
    if (n.takeaway) parts.push(`<p><strong>Takeaway:</strong> ${esc(n.takeaway)}</p>`);
    if (n.trends.length) {
      parts.push(`<p style="margin-bottom:4px"><strong>Trends</strong></p><ul style="margin-top:0">`);
      for (const t of n.trends)
        parts.push(`<li><strong>${esc(t.title)}</strong> <span style="color:#888">(${esc(t.momentum)})</span> - ${esc(t.summary)}</li>`);
      parts.push(`</ul>`);
    }
    if (n.stories.length) {
      parts.push(`<p style="margin-bottom:4px"><strong>Most corroborated stories</strong></p><ul style="margin-top:0">`);
      for (const s of n.stories)
        parts.push(`<li><a href="${esc(s.url)}">${esc(s.title)}</a> <span style="color:#888">[${esc(s.source)}, ${s.sources} sources]</span></li>`);
      parts.push(`</ul>`);
    }
    parts.push(`<p><a href="${DASHBOARD_URL}/brief/${date}">Open full News Brief -&gt;</a></p>`);
  } else {
    parts.push(`<p style="color:#b00">News Brief unavailable for ${date}.</p>`);
  }

  if (p) {
    parts.push(`<h2 style="font-size:16px;border-bottom:2px solid #eee;padding-bottom:6px;margin-top:28px">Practical AI</h2>`);
    parts.push(`<p><strong>Today's topics:</strong> ${esc(p.topics.join(", ")) || "(none)"}</p>`);
    if (p.insight) parts.push(`<p><strong>Insight:</strong> ${esc(p.insight)}</p>`);
    if (p.topPick) parts.push(`<p><strong>Top pick:</strong> ${esc(p.topPick.name)} - ${esc(p.topPick.oneLiner)}</p>`);
    if (p.recipe)
      parts.push(
        `<p><strong>Workflow recipe:</strong> ${esc(p.recipe.title)} <span style="color:#888">(${esc(p.recipe.agent)}${p.recipe.timeSaved ? `, ${esc(p.recipe.timeSaved)}` : ""})</span><br><span style="color:#555">${esc(p.recipe.subtitle)}</span></p>`
      );
    if (p.ideas.length) {
      parts.push(`<p style="margin-bottom:4px"><strong>Content ideas to post</strong></p><ul style="margin-top:0">`);
      for (const i of p.ideas)
        parts.push(`<li><span style="color:#888">[${esc(i.format)}]</span> <strong>${esc(i.title)}</strong> - ${esc(i.hook)}</li>`);
      parts.push(`</ul>`);
    }
    parts.push(`<p><a href="${DASHBOARD_URL}/tools/${date}">Open full Practical AI -&gt;</a></p>`);
  } else {
    parts.push(`<p style="color:#b00">Practical AI unavailable for ${date}.</p>`);
  }

  parts.push(`</div>`);
  return parts.join("\n");
}

// --- Sheet identity (self-bootstrapping) ---

async function resolveSheetId(): Promise<string> {
  if (process.env.DIGEST_SHEET_ID) return process.env.DIGEST_SHEET_ID;
  if (existsSync(SHEET_STATE)) {
    const id = jparse<{ spreadsheetId?: string }>(readFileSync(SHEET_STATE, "utf-8"), {}).spreadsheetId;
    if (id) return id;
  }
  console.log("[digest] No digest sheet yet - creating one...");
  const id = await createDigestSpreadsheet("NexusPoint Daily Brief", [NEWS_TAB, PRACTICAL_TAB]);
  writeFileSync(SHEET_STATE, JSON.stringify({ spreadsheetId: id }, null, 2));
  console.log(`[digest] Created: https://docs.google.com/spreadsheets/d/${id}`);
  return id;
}

// --- Scheduling (schtasks, mirrors brain-sync) ---

function schedule(): void {
  const target = `"${join(__dirname, "run-digest.cmd")}"`;
  const r = spawnSync(
    "schtasks",
    ["/Create", "/SC", "DAILY", "/ST", "12:00", "/TN", TASK_NAME, "/TR", target, "/F"],
    { encoding: "utf-8" }
  );
  if (r.status === 0) {
    console.log(`Scheduled task '${TASK_NAME}' daily at 12:00 (local time).`);
    console.log(`Target: ${target}`);
    console.log("Note: the machine must be on and signed in at noon for it to fire.");
  } else {
    console.error(`Failed to schedule: ${r.stderr || r.stdout}`);
    process.exit(1);
  }
}

function unschedule(): void {
  const r = spawnSync("schtasks", ["/Delete", "/TN", TASK_NAME, "/F"], { encoding: "utf-8" });
  console.log(r.status === 0 ? `Removed task '${TASK_NAME}'.` : `Not found or error: ${r.stderr || r.stdout}`);
}

// --- Main ---

async function main() {
  const argv = process.argv.slice(2);
  if (argv.includes("--schedule")) return schedule();
  if (argv.includes("--unschedule")) return unschedule();
  const noEmail = argv.includes("--no-email");
  const date = argv.find((a) => /^\d{4}-\d{2}-\d{2}$/.test(a)) || new Date().toISOString().split("T")[0];

  if (!existsSync(DB_PATH)) {
    console.error(`[digest] DB not found at ${DB_PATH} - run the briefs first.`);
    process.exit(1);
  }
  const db = new Database(DB_PATH, { readonly: true });
  const news = readNews(db, date);
  const practical = readPractical(db, date);
  db.close();

  if (!news && !practical) {
    console.error(`[digest] No briefs found for ${date}. Nothing to send.`);
    process.exit(1);
  }
  console.log(`[digest] ${date}: news=${news ? "ok" : "MISSING"}, practical=${practical ? "ok" : "MISSING"}`);

  const now = new Date().toISOString().replace("T", " ").slice(0, 16);
  const sheetId = await resolveSheetId();
  if (news) {
    const r = await upsertRowByDate(sheetId, NEWS_TAB, NEWS_HEADER, newsRow(date, news, now));
    console.log(`[digest] News Brief row ${r}.`);
  }
  if (practical) {
    const r = await upsertRowByDate(sheetId, PRACTICAL_TAB, PRACTICAL_HEADER, practicalRow(date, practical, now));
    console.log(`[digest] Practical AI row ${r}.`);
  }

  // Cosmetic — never let a formatting hiccup fail the digest.
  try {
    await formatDigestTab(sheetId, NEWS_TAB, NEWS_WIDTHS);
    await formatDigestTab(sheetId, PRACTICAL_TAB, PRACTICAL_WIDTHS);
  } catch (e) {
    console.warn(`[digest] Formatting skipped: ${(e as Error).message}`);
  }
  console.log(`[digest] Sheet: https://docs.google.com/spreadsheets/d/${sheetId}`);

  if (noEmail) {
    console.log("[digest] --no-email set; skipped send.");
    return;
  }
  await sendEmail(DIGEST_EMAIL, `Daily Brief - ${date}`, buildEmail(date, news, practical));
  console.log(`[digest] Emailed ${DIGEST_EMAIL}.`);
}

main().catch((err) => {
  console.error("[digest] Fatal:", err);
  process.exit(1);
});
