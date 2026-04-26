import { NextResponse } from "next/server";
import { execFile } from "child_process";
import { existsSync } from "fs";
import path from "path";
import { SCHEDULE_COLUMNS } from "@/lib/types";

export const dynamic = "force-dynamic";

const SHEET_ID = "13RiOJpxWly5BztZdpLhGK5kT_Unna8Lnc-8GboApJ74";
const SCHEDULE_TAB = "SM Schedule";

export { SCHEDULE_COLUMNS };

function findGwsInvocation(): { exe: string; prefix: string[] } {
  const appData = process.env.APPDATA || "";
  const npmDir = path.join(appData, "npm");

  const gwsJs = path.join(npmDir, "node_modules", "@googleworkspace", "cli", "run.js");
  if (existsSync(gwsJs)) {
    return { exe: process.execPath, prefix: [gwsJs] };
  }

  const gwsCmd = path.join(npmDir, "gws.cmd");
  if (existsSync(gwsCmd)) {
    return { exe: gwsCmd, prefix: [] };
  }

  return { exe: "gws", prefix: [] };
}

function runGws(args: string[]): Promise<string> {
  const { exe, prefix } = findGwsInvocation();
  const useShell = prefix.length === 0;

  return new Promise((resolve, reject) => {
    execFile(
      exe,
      [...prefix, ...args],
      { shell: useShell, timeout: 60_000, encoding: "utf8" },
      (error, stdout, stderr) => {
        if (error) {
          reject(new Error(`gws failed: ${stderr || error.message}`));
          return;
        }
        // Strip "Using keyring backend" lines before parsing
        const clean = (stdout as string)
          .split("\n")
          .filter((l) => !l.startsWith("Using keyring"))
          .join("\n")
          .trim();
        resolve(clean);
      }
    );
  });
}

export async function GET() {
  try {
    const paramsJson = JSON.stringify({
      spreadsheetId: SHEET_ID,
      range: SCHEDULE_TAB,
    });

    const stdout = await runGws([
      "sheets", "spreadsheets", "values", "get", "--params", paramsJson,
    ]);

    if (!stdout) {
      return NextResponse.json({ headers: [], rows: [] });
    }

    const data = JSON.parse(stdout) as { values?: string[][] };
    const values = data.values ?? [];

    if (values.length === 0) {
      return NextResponse.json({ headers: [], rows: [] });
    }

    const headers = values[0];
    const rows = values.slice(1);

    return NextResponse.json({ headers, rows });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}

export async function PUT(req: Request) {
  try {
    const body = await req.json() as { rowNumber: number; row: string[] };
    const { rowNumber, row } = body;

    if (!Array.isArray(row) || typeof rowNumber !== "number") {
      return NextResponse.json({ error: "invalid body" }, { status: 400 });
    }

    // SCHEDULE_COLUMNS has 21 cols (A–U)
    const lastCol = String.fromCharCode(64 + SCHEDULE_COLUMNS.length);
    const range = `${SCHEDULE_TAB}!A${rowNumber}:${lastCol}${rowNumber}`;

    const paramsJson = JSON.stringify({
      spreadsheetId: SHEET_ID,
      range,
      valueInputOption: "RAW",
    });
    const bodyJson = JSON.stringify({ values: [row] });

    await runGws([
      "sheets", "spreadsheets", "values", "update",
      "--params", paramsJson,
      "--json", bodyJson,
    ]);

    return NextResponse.json({ ok: true });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}

export async function POST(req: Request) {
  try {
    const body = await req.json() as { row: string[] };
    const { row } = body;

    if (!Array.isArray(row)) {
      return NextResponse.json({ error: "row must be an array" }, { status: 400 });
    }

    const paramsJson = JSON.stringify({
      spreadsheetId: SHEET_ID,
      range: `${SCHEDULE_TAB}!A1`,
      valueInputOption: "RAW",
      insertDataOption: "INSERT_ROWS",
    });

    const bodyJson = JSON.stringify({ values: [row] });

    await runGws([
      "sheets", "spreadsheets", "values", "append",
      "--params", paramsJson,
      "--json", bodyJson,
    ]);

    return NextResponse.json({ ok: true });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
