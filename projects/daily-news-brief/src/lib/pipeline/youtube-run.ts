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
import { parse as parseDotenv } from "dotenv";
import { pythonExecutable } from "./python";

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

function childEnv(): NodeJS.ProcessEnv {
  // Read files on each run so adding a missing key does not require a restart.
  let parsed: Record<string, string> = {};
  for (const envPath of [resolve(process.cwd(), "..", "..", ".env"), resolve(process.cwd(), ".env")]) {
    try {
      parsed = { ...parsed, ...parseDotenv(readFileSync(envPath)) };
    } catch {
      // An environment file is optional when keys are already in process.env.
    }
  }
  return { ...parsed, ...process.env, PYTHONIOENCODING: "utf-8" };
}

function runPythonScript(scriptRelPath: string, dir: string, env: NodeJS.ProcessEnv): Promise<void> {
  return new Promise((resolvePromise, reject) => {
    const python = pythonExecutable(
      process.cwd(),
      env.YOUTUBE_BRIEF_PYTHON || env.LAST30DAYS_PYTHON || env.RESEARCH_PYTHON
    );
    const child = spawn(python, [scriptRelPath], {
      cwd: dir,
      env,
      windowsHide: true,
    });

    const output: string[] = [];
    const redactKeys = (text: string) => {
      for (const key of [env.GOOGLE_API_KEY, env.OPENAI_API_KEY]) {
        if (key) text = text.split(key).join("[redacted]");
      }
      return text;
    };
    child.stderr.on("data", (d: Buffer) => {
      const line = redactKeys(d.toString());
      output.push(line);
      process.stderr.write(line);
    });
    child.stdout.on("data", (d: Buffer) => {
      const line = redactKeys(d.toString());
      output.push(line);
      process.stdout.write(line);
    });

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
      else {
        const details = output.join("").trim().split(/\r?\n/).slice(-10).join("\n");
        reject(new Error(`Script ${scriptRelPath} exited ${code}: ${details}`));
      }
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

  const env = childEnv();
  const missingKeys = ["GOOGLE_API_KEY", "OPENAI_API_KEY"].filter((key) => !env[key]?.trim());
  if (missingKeys.length > 0) {
    return {
      success: false,
      date: targetDate,
      errors: [`Missing ${missingKeys.join(" and ")}. Add the key to the repo .env or projects/daily-news-brief/.env. GOOGLE_API_KEY must support YouTube Data API v3.`],
    };
  }

  // Step 1: Scrape channels
  console.log("[Step 1/4] Scraping YouTube channels...");
  try {
    await runPythonScript("scripts/scrape_channels.py", dir, env);
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    errors.push(`Scrape failed: ${msg}`);
    return { success: false, date: targetDate, errors };
  }

  // Step 2: Analyze with OpenAI
  console.log("\n[Step 2/4] Analyzing content with OpenAI...");
  try {
    await runPythonScript("scripts/analyze_content.py", dir, env);
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
