import { NextResponse } from "next/server";
import { appendToSheet, sheetsError } from "@/lib/google-sheets";
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

    if (body.type === "video") {
      const engRate =
        body.viewCount > 0
          ? Number(((body.likeCount / body.viewCount) * 100).toFixed(2))
          : "";
      row = [
        dateSaved,
        body.title,
        body.channelName,
        body.url,
        body.viewCount || "",
        body.likeCount || "",
        engRate,
        body.durationSeconds ? formatDuration(body.durationSeconds) : "",
        body.publishedDate ? String(body.publishedDate).slice(0, 10) : "",
        "New",
      ];
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
    } else {
      // topic
      const channels = Array.isArray(body.channels)
        ? body.channels.slice(0, 3).join(", ")
        : "";
      row = [dateSaved, body.topic, channels, "", "", "", "", "", "", "New"];
    }

    const saved = await appendToSheet(
      SHEET_TAB,
      ["Date Saved", "Title", "Channel", "URL", "Views", "Likes", "Eng Rate", "Duration", "Published Date", "Status"],
      row
    );
    return NextResponse.json({ success: true, ...saved });
  } catch (error) {
    return sheetsError(error);
  }
}
