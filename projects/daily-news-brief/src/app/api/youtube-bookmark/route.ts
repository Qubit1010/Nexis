import { NextResponse } from "next/server";
import { appendToSheet, sheetsError } from "@/lib/google-sheets";
import { saveEverywhere, type ContentOsIdea } from "@/lib/content-os";
const SHEET_TAB = "Youtube bookmarked";

function formatDuration(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0)
    return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  return `${m}:${String(s).padStart(2, "0")}`;
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    if (!["video", "idea", "topic"].includes(body.type) || !(body.type === "topic" ? body.topic : body.title)?.trim()) {
      return NextResponse.json({ error: "An item type and title are required." }, { status: 400 });
    }
    const dateSaved = new Date().toISOString().slice(0, 10);

    let row: (string | number)[];
    let idea: ContentOsIdea;

    if (body.type === "video") {
      // Likes are not in the stored brief data; leave Eng Rate blank rather than writing a false 0.
      const likes = typeof body.likeCount === "number" && body.likeCount > 0 ? body.likeCount : null;
      const engRate =
        likes && body.viewCount > 0
          ? Number(((likes / body.viewCount) * 100).toFixed(2))
          : "";
      row = [
        dateSaved,
        body.title,
        body.channelName,
        body.url,
        body.viewCount || "",
        likes ?? "",
        engRate,
        body.durationSeconds ? formatDuration(body.durationSeconds) : "",
        body.publishedDate ? String(body.publishedDate).slice(0, 10) : "",
        "New",
      ];
      idea = {
        title: body.title,
        url: body.url,
        summary: body.summary || null,
        source: "youtube_video",
        payload: { channel: body.channelName, views: body.viewCount ?? null, publishedDate: body.publishedDate ?? null },
      };
    } else if (body.type === "idea") {
      row = [
        dateSaved,
        body.title,
        body.formatSuggestion || "Content Idea",
        "",
        "",
        "",
        "",
        "",
        "",
        "New",
      ];
      idea = {
        title: body.title,
        summary: body.summary || null,
        source: "youtube_idea",
        payload: { format: body.formatSuggestion || null, ...(body.details || {}) },
      };
    } else {
      // topic
      const channels = Array.isArray(body.channels)
        ? body.channels.slice(0, 3).join(", ")
        : "";
      row = [dateSaved, body.topic, channels, "", "", "", "", "", "", "New"];
      idea = {
        title: body.topic,
        summary: body.summary || null,
        source: "youtube_topic",
        payload: { channels: body.channels || [], mentionCount: body.mentionCount ?? null, sentiment: body.sentiment ?? null },
      };
    }

    const result = await saveEverywhere(
      () =>
        appendToSheet(
          SHEET_TAB,
          ["Date Saved", "Title", "Channel", "URL", "Views", "Likes", "Eng Rate", "Duration", "Published Date", "Status"],
          row
        ),
      idea
    );
    if (!result.ok) return sheetsError(result.sheetError);
    return NextResponse.json({ success: true, ...(result.sheet || {}), contentOs: result.contentOs, sheetSaved: !!result.sheet });
  } catch (error) {
    return sheetsError(error);
  }
}
