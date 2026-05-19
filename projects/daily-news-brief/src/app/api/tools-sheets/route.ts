import { NextResponse } from "next/server";
import { execFile } from "child_process";
import { promisify } from "util";

const execFileAsync = promisify(execFile);

// Reuse the same spreadsheet, but append to a different tab
const SPREADSHEET_ID = process.env.GOOGLE_SHEETS_SPREADSHEET_ID;
const SHEET_TAB = process.env.GOOGLE_SHEETS_TOOLS_TAB || "Tool Content Drafts";
const GWS_SCRIPT = "C:/Users/qubit/AppData/Roaming/npm/node_modules/@googleworkspace/cli/run.js";

interface SaveRequest {
  briefDate: string;
  name: string;
  url: string;
  domain: string;
  domainSlug: string;
  oneLiner: string;
  bestUseCase: string;
  howToSteps: string[];
  audienceHook: string;
  pricingTier: string | null;
  tags: string[];
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
    const howTo = body.howToSteps.map((s, i) => `${i + 1}. ${s}`).join("\n");
    const tags = body.tags.join(", ");

    const row = [
      now,
      body.briefDate,
      body.name,
      body.url,
      body.domain,
      body.pricingTier ?? "unknown",
      body.oneLiner,
      body.bestUseCase,
      howTo,
      body.audienceHook,
      tags,
      "New",
    ];

    const jsonValues = JSON.stringify([row]);

    const args = [
      GWS_SCRIPT,
      "sheets",
      "+append",
      "--spreadsheet",
      SPREADSHEET_ID,
      "--json-values",
      jsonValues,
      "--range",
      `${SHEET_TAB}!A:L`,
    ];

    const { stderr } = await execFileAsync(process.execPath, args, {
      timeout: 15000,
    });

    if (stderr && stderr.includes('"code"') && stderr.includes('"message"')) {
      console.error("[ToolsSheets] gws error:", stderr);
      return NextResponse.json(
        { error: "Failed to save to sheet" },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      message: `Saved to "${SHEET_TAB}" tab`,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    console.error("[ToolsSheets] Error:", message);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
