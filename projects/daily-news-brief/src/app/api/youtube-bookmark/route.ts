import { NextResponse } from "next/server";
import { execFile } from "child_process";
import { promisify } from "util";

const execFileAsync = promisify(execFile);
const SPREADSHEET_ID = process.env.GOOGLE_SHEETS_SPREADSHEET_ID;
const GWS_SCRIPT =
  "C:/Users/qubit/AppData/Roaming/npm/node_modules/@googleworkspace/cli/run.js";
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
  if (!SPREADSHEET_ID) {
    return NextResponse.json(
      { error: "GOOGLE_SHEETS_SPREADSHEET_ID not configured" },
      { status: 500 }
    );
  }

  try {
    const body = await request.json();
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

    const params = JSON.stringify({
      spreadsheetId: SPREADSHEET_ID,
      range: `${SHEET_TAB}!A1`,
      valueInputOption: "USER_ENTERED",
    });
    const json = JSON.stringify({ values: [row] });

    const { stderr } = await execFileAsync(
      process.execPath,
      [
        GWS_SCRIPT,
        "sheets",
        "spreadsheets",
        "values",
        "append",
        "--params",
        params,
        "--json",
        json,
      ],
      { timeout: 15000 }
    );

    if (stderr && stderr.includes('"code"') && stderr.includes('"message"')) {
      console.error("[YT Bookmark] gws error:", stderr);
      return NextResponse.json({ error: "Failed to save to sheet" }, { status: 500 });
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    console.error("[YT Bookmark] Error:", message);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
