import { NextResponse } from "next/server";
import { execFile } from "child_process";
import { promisify } from "util";

const execFileAsync = promisify(execFile);

const SPREADSHEET_ID = process.env.GOOGLE_SHEETS_SPREADSHEET_ID;
const GWS_SCRIPT = "C:/Users/qubit/AppData/Roaming/npm/node_modules/@googleworkspace/cli/run.js";

interface SaveArticleRequest {
  briefDate: string;
  title: string;
  source: string;
  url: string;
  tldr: string;
}

export async function POST(request: Request) {
  if (!SPREADSHEET_ID) {
    return NextResponse.json(
      { error: "GOOGLE_SHEETS_SPREADSHEET_ID not configured" },
      { status: 500 }
    );
  }

  try {
    const body: SaveArticleRequest = await request.json();

    const now = new Date().toISOString().slice(0, 19).replace("T", " ");

    const row = [
      now,
      body.briefDate,
      body.title,
      body.source,
      body.url,
      body.tldr,
      "New",
    ];

    // Use raw values.append API to target "Saved Articles" sheet tab
    const params = JSON.stringify({
      spreadsheetId: SPREADSHEET_ID,
      range: "Saved Articles!A1",
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
      console.error("[Sheets/Articles] gws error:", stderr);
      return NextResponse.json({ error: "Failed to save to sheet" }, { status: 500 });
    }

    return NextResponse.json({ success: true, message: "Article saved to Google Sheet" });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    console.error("[Sheets/Articles] Error:", message);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
