import { NextResponse } from "next/server";
import { execFile } from "child_process";
import { promisify } from "util";

const execFileAsync = promisify(execFile);

const SPREADSHEET_ID = process.env.GOOGLE_SHEETS_SPREADSHEET_ID;
// Direct path to gws JS entry point — avoids .cmd wrapper PATH issues on Windows
const GWS_SCRIPT = "C:/Users/qubit/AppData/Roaming/npm/node_modules/@googleworkspace/cli/run.js";

interface SaveRequest {
  briefDate: string;
  title: string;
  format: string;
  timeliness: string;
  angle: string;
  hook: string;
  keyPoints: string[];
  relatedTrends: string[];
}

export async function POST(request: Request) {
  if (!SPREADSHEET_ID) {
    return NextResponse.json(
      { error: "GOOGLE_SHEETS_SPREADSHEET_ID not configured" },
      { status: 500 }
    );
  }

  try {
    const body: SaveRequest = await request.json();

    const now = new Date().toISOString().slice(0, 19).replace("T", " ");
    const keyPoints = body.keyPoints.join("\n");
    const relatedTrends = body.relatedTrends.join(", ");

    const row = [
      now,
      body.briefDate,
      body.title,
      body.format,
      body.timeliness,
      body.angle,
      body.hook,
      keyPoints,
      relatedTrends,
      "New",
    ];

    const jsonValues = JSON.stringify([row]);

    const { stdout, stderr } = await execFileAsync(
      process.execPath, // use the same Node.js binary running Next.js
      [
        GWS_SCRIPT,
        "sheets",
        "+append",
        "--spreadsheet",
        SPREADSHEET_ID,
        "--json-values",
        jsonValues,
      ],
      { timeout: 15000 }
    );

    // gws writes "Using keyring backend" to stderr — only treat as error if actual API error
    if (stderr && stderr.includes('"code"') && stderr.includes('"message"')) {
      console.error("[Sheets] gws error:", stderr);
      return NextResponse.json({ error: "Failed to save to sheet" }, { status: 500 });
    }

    return NextResponse.json({ success: true, message: "Saved to Google Sheet" });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    console.error("[Sheets] Error:", message);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
