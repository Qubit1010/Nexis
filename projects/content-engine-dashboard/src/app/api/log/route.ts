import { NextResponse } from "next/server";
import { execFile } from "child_process";
import { existsSync } from "fs";
import path from "path";

export const dynamic = "force-dynamic";

const SHEET_ID = "1TwAuLDKak3hpPWqlojpNL_OTsUyCOBaAVjRRncOpb9Q";
const LOG_TAB = "Content Log";

// Mirror the Python scripts' approach: call run-gws.js via node directly
// so JSON args are passed as-is without shell quoting issues.
function findGwsInvocation(): { exe: string; prefix: string[] } {
  const appData = process.env.APPDATA || "";
  const npmDir = path.join(appData, "npm");

  const gwsJs = path.join(
    npmDir,
    "node_modules",
    "@googleworkspace",
    "cli",
    "run.js"
  );
  if (existsSync(gwsJs)) {
    return { exe: process.execPath, prefix: [gwsJs] };
  }

  // Fall back: gws.cmd via shell (last resort, may have quoting issues)
  const gwsCmd = path.join(npmDir, "gws.cmd");
  if (existsSync(gwsCmd)) {
    return { exe: gwsCmd, prefix: [] };
  }

  return { exe: "gws", prefix: [] };
}

function runGws(args: string[]): Promise<string> {
  const { exe, prefix } = findGwsInvocation();
  // No shell when calling node directly — args are passed as-is (no quoting issues)
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
        resolve((stdout as string).trim());
      }
    );
  });
}

export async function GET() {
  try {
    const paramsJson = JSON.stringify({
      spreadsheetId: SHEET_ID,
      range: LOG_TAB,
    });

    const stdout = await runGws([
      "sheets",
      "spreadsheets",
      "values",
      "get",
      "--params",
      paramsJson,
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
    // Content Log tab hasn't been created yet — return empty gracefully
    if (
      message.includes("Unable to parse range") ||
      message.includes("Content Log")
    ) {
      return NextResponse.json({
        headers: [],
        rows: [],
        note: "Content Log tab not created yet. Log a post first.",
      });
    }
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
