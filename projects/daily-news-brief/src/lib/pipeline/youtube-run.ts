import { spawn } from "child_process";
import { readFileSync } from "fs";
import { join, resolve } from "path";
import { db } from "../db";
import {
  youtubeBriefs,
  youtubeTrendingTopics,
  youtubeTopVideos,
  youtubeChannelStats,
  youtubeContentIdeas,
  youtubeSuggestedTopics,
} from "../db/schema";
import { eq } from "drizzle-orm";

interface YoutubeBriefResult {
  success: boolean;
  briefId?: number;
  date: string;
  errors: string[];
}

function youtubeBriefDir(): string {
  if (process.env.YOUTUBE_BRIEF_DIR) return process.env.YOUTUBE_BRIEF_DIR;
  // cron + Next.js both run with cwd = <repo>/projects/daily-news-brief.
  // Resolve from cwd, NOT __dirname: under Turbopack __dirname points inside .next/,
  // so the old path resolved to a non-existent dir -> spawn ENOENT that hung 300s.
  const repoRoot = resolve(process.cwd(), "..", "..");
  return resolve(repoRoot, ".claude", "skills", "youtube-daily-brief");
}

function pythonExe(): string {
  return (
    process.env.LAST30DAYS_PYTHON ||
    "C:/Users/qubit/AppData/Local/Python/bin/python3.14.exe"
  );
}

function childEnv(): NodeJS.ProcessEnv {
  // The cron/API entrypoints load projects/daily-news-brief/.env into process.env;
  // the Python scripts read GOOGLE_API_KEY / OPENAI_API_KEY straight from there.
  return { ...process.env, PYTHONIOENCODING: "utf-8" };
}

function runPythonScript(scriptRelPath: string, dir: string): Promise<void> {
  return new Promise((resolvePromise, reject) => {
    const child = spawn(pythonExe(), [scriptRelPath], {
      cwd: dir,
      env: childEnv(),
      windowsHide: true,
    });

    const stderr: string[] = [];
    child.stderr.on("data", (d: Buffer) => {
      const line = d.toString();
      stderr.push(line);
      process.stderr.write(line);
    });
    child.stdout.on("data", (d: Buffer) => process.stdout.write(d.toString()));

    const timer = setTimeout(() => {
      child.kill();
      reject(new Error(`Script ${scriptRelPath} timed out after 300s`));
    }, 300_000);

    // Without this, a spawn failure (e.g. bad python path / cwd -> ENOENT) emits
    // 'error' not 'close', the promise never settles, and it hangs until the timeout.
    child.on("error", (err) => {
      clearTimeout(timer);
      reject(new Error(`Failed to spawn ${scriptRelPath}: ${err.message}`));
    });

    child.on("close", (code) => {
      clearTimeout(timer);
      if (code === 0) resolvePromise();
      else reject(new Error(`Script ${scriptRelPath} exited ${code}: ${stderr.join("")}`));
    });
  });
}

function readAnalysisJson(dir: string): Record<string, unknown> {
  const path = join(dir, ".tmp", "analysis.json");
  return JSON.parse(readFileSync(path, "utf-8")) as Record<string, unknown>;
}

export async function generateYoutubeBrief(date?: string): Promise<YoutubeBriefResult> {
  const targetDate = date || new Date().toISOString().split("T")[0];
  const dir = youtubeBriefDir();
  const errors: string[] = [];

  console.log(`\n========================================`);
  console.log(`  Generating YOUTUBE INTELLIGENCE brief for ${targetDate}`);
  console.log(`========================================\n`);

  // Step 1: Scrape channels
  console.log("[Step 1/4] Scraping YouTube channels...");
  try {
    await runPythonScript("scripts/scrape_channels.py", dir);
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    errors.push(`Scrape failed: ${msg}`);
    return { success: false, date: targetDate, errors };
  }

  // Step 2: Analyze with OpenAI
  console.log("\n[Step 2/4] Analyzing content with OpenAI...");
  try {
    await runPythonScript("scripts/analyze_content.py", dir);
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    errors.push(`Analysis failed: ${msg}`);
    return { success: false, date: targetDate, errors };
  }

  // Step 3: Read analysis.json
  console.log("\n[Step 3/4] Reading analysis...");
  let analysis: Record<string, unknown>;
  try {
    analysis = readAnalysisJson(dir);
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    errors.push(`Could not read analysis.json: ${msg}`);
    return { success: false, date: targetDate, errors };
  }

  // Step 4: Atomic DB write
  console.log("\n[Step 4/4] Storing to database...");

  const pendingDate = `${targetDate}_pending`;

  const trendingTopics = (analysis.trending_topics as Array<Record<string, unknown>>) || [];
  const topPerforming = (analysis.top_performing as Array<Record<string, unknown>>) || [];
  const channelBreakdown = (analysis.channel_breakdown as Array<Record<string, unknown>>) || [];
  const contentOpportunities = (analysis.content_opportunities as Array<Record<string, unknown>>) || [];
  const suggestedTopics = (analysis.suggested_topics as Array<Record<string, unknown>>) || [];
  const sentiment = (analysis.sentiment as Record<string, unknown>) || {};

  const brief = db
    .insert(youtubeBriefs)
    .values({
      date: pendingDate,
      videoCount: (analysis.video_count as number) || topPerforming.length,
      channelCount: channelBreakdown.length,
      overallSentiment: JSON.stringify(sentiment),
      formatDistribution: JSON.stringify(analysis.format_distribution || {}),
      titlePatternsJson: JSON.stringify(analysis.title_patterns || []),
      analyzedAt: (analysis.analyzed_at as string) || null,
      modelUsed: (analysis.model_used as string) || null,
    })
    .returning()
    .get();

  for (let i = 0; i < trendingTopics.length; i++) {
    const t = trendingTopics[i];
    db.insert(youtubeTrendingTopics)
      .values({
        briefId: brief.id,
        topic: (t.topic as string) || "",
        mentionCount: (t.mention_count as number) || 0,
        channels: JSON.stringify(t.channels || []),
        sentiment: (t.sentiment as string) || null,
        summary: (t.summary as string) || "",
        sortOrder: i,
      })
      .run();
  }

  for (let i = 0; i < topPerforming.length; i++) {
    const v = topPerforming[i];
    db.insert(youtubeTopVideos)
      .values({
        briefId: brief.id,
        videoId: (v.video_id as string) || "",
        title: (v.title as string) || "",
        channelName: (v.channel_name as string) || "",
        url: (v.url as string) || "",
        thumbnailUrl: (v.thumbnail_url as string) || null,
        viewCount: (v.view_count as number) || 0,
        publishedDate: (v.published_date as string) || null,
        performanceNote: (v.performance_note as string) || null,
        sortOrder: i,
      })
      .run();
  }

  for (let i = 0; i < channelBreakdown.length; i++) {
    const c = channelBreakdown[i];
    db.insert(youtubeChannelStats)
      .values({
        briefId: brief.id,
        channelName: (c.channel_name as string) || "",
        channelHandle: (c.channel_handle as string) || null,
        videosScraped: (c.videos_scraped as number) || 0,
        totalViews: (c.total_views as number) || 0,
        avgViews: (c.avg_views as number) || 0,
        mostCommonFormat: (c.most_common_format as string) || null,
        postingFrequency: (c.posting_frequency as string) || null,
        sortOrder: i,
      })
      .run();
  }

  for (let i = 0; i < contentOpportunities.length; i++) {
    const o = contentOpportunities[i];
    db.insert(youtubeContentIdeas)
      .values({
        briefId: brief.id,
        idea: (o.idea as string) || "",
        reasoning: (o.reasoning as string) || "",
        formatSuggestion: (o.format_suggestion as string) || null,
        estimatedInterest: (o.estimated_interest as string) || null,
        sortOrder: i,
      })
      .run();
  }

  for (let i = 0; i < suggestedTopics.length; i++) {
    const s = suggestedTopics[i];
    db.insert(youtubeSuggestedTopics)
      .values({
        briefId: brief.id,
        topic: (s.topic as string) || "",
        angle: (s.angle as string) || "",
        whyNow: (s.why_now as string) || "",
        targetFormat: (s.target_format as string) || null,
        competitionLevel: (s.competition_level as string) || null,
        referenceVideos: JSON.stringify(s.reference_videos || []),
        sortOrder: i,
      })
      .run();
  }

  // Swap pending → real date
  const existing = db.select().from(youtubeBriefs).where(eq(youtubeBriefs.date, targetDate)).get();
  if (existing) {
    db.delete(youtubeBriefs).where(eq(youtubeBriefs.id, existing.id)).run();
  }
  db.update(youtubeBriefs).set({ date: targetDate }).where(eq(youtubeBriefs.id, brief.id)).run();

  console.log(
    `\n[Done] YouTube brief stored: ${trendingTopics.length} topics, ${topPerforming.length} videos, ${channelBreakdown.length} channels`
  );

  return { success: errors.length === 0, briefId: brief.id, date: targetDate, errors };
}
