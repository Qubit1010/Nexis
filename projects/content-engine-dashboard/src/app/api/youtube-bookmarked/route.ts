import { NextResponse } from "next/server";
import { execFile } from "child_process";
import { existsSync } from "fs";
import path from "path";

export const dynamic = "force-dynamic";

const SHEET_ID = "1TwAuLDKak3hpPWqlojpNL_OTsUyCOBaAVjRRncOpb9Q";
const TAB = "Youtube bookmarked";

function findGwsInvocation(): { exe: string; prefix: string[] } {
  const appData = process.env.APPDATA || "";
  const npmDir = path.join(appData, "npm");
  const gwsJs = path.join(npmDir, "node_modules", "@googleworkspace", "cli", "run-gws.js");
  if (existsSync(gwsJs)) return { exe: process.execPath, prefix: [gwsJs] };
  const gwsCmd = path.join(npmDir, "gws.cmd");
  if (existsSync(gwsCmd)) return { exe: gwsCmd, prefix: [] };
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
        if (error) { reject(new Error(`gws failed: ${stderr || error.message}`)); return; }
        resolve((stdout as string).trim());
      }
    );
  });
}

export async function GET() {
  try {
    const paramsJson = JSON.stringify({ spreadsheetId: SHEET_ID, range: TAB });
    const stdout = await runGws(["sheets", "spreadsheets", "values", "get", "--params", paramsJson]);

    if (!stdout) return NextResponse.json({ videos: [], fetchedAt: new Date().toISOString() });

    const data = JSON.parse(stdout) as { values?: string[][] };
    const values = data.values ?? [];

    if (values.length < 2) return NextResponse.json({ videos: [], fetchedAt: new Date().toISOString() });

    // Columns: Date Saved, Title, Channel, URL, Views, Likes, Eng Rate, Duration, Published Date, Status
    const rows = values.slice(1);
    const videos = rows
      .filter((r) => r[1]) // must have a title
      .map((r) => ({
        dateSaved: r[0] ?? "",
        title: r[1] ?? "",
        channel: r[2] ?? "",
        url: r[3] ?? "",
        views: parseInt(r[4] ?? "0", 10) || 0,
        likes: parseInt(r[5] ?? "0", 10) || 0,
        engRate: parseFloat(r[6] ?? "0") || 0,
        duration: r[7] ?? "",
        publishedDate: r[8] ?? "",
        status: r[9] ?? "",
      }));

    return NextResponse.json({ videos, fetchedAt: new Date().toISOString() });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
