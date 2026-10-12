import { readFileSync } from "fs";
import { resolve } from "path";
import { parse } from "dotenv";
import { NextResponse } from "next/server";
import { runGwsCommand } from "../../scripts/gws";

export function sheetsConfig(): NodeJS.ProcessEnv {
  let files: Record<string, string> = {};
  for (const path of [resolve(process.cwd(), "../..", ".env"), resolve(process.cwd(), ".env")]) {
    try {
      files = { ...files, ...parse(readFileSync(path)) };
    } catch {
      // File configuration is optional when supplied through the environment.
    }
  }
  // Re-read file settings so a corrected spreadsheet ID works without a restart.
  return { ...process.env, ...files };
}

const readyTabs = new Map<string, Promise<void>>();

async function ensureTab(spreadsheetId: string, tab: string, headers: string[]) {
  const key = `${spreadsheetId}:${tab}`;
  if (!readyTabs.has(key)) {
    const setup = (async () => {
      const metadata = await runGwsCommand([
        "sheets", "spreadsheets", "get", "--params",
        JSON.stringify({ spreadsheetId, fields: "sheets(properties(title))" }),
      ]);
      if (metadata.sheets?.some((sheet: { properties: { title: string } }) => sheet.properties.title === tab)) return;
      await runGwsCommand([
        "sheets", "spreadsheets", "batchUpdate", "--params", JSON.stringify({ spreadsheetId }),
        "--json", JSON.stringify({ requests: [{ addSheet: { properties: { title: tab, gridProperties: { frozenRowCount: 1 } } } }] }),
      ]);
      await runGwsCommand([
        "sheets", "spreadsheets", "values", "update", "--params",
        JSON.stringify({ spreadsheetId, range: `'${tab.replace(/'/g, "''")}'!A1`, valueInputOption: "RAW" }),
        "--json", JSON.stringify({ values: [headers] }),
      ]);
    })();
    readyTabs.set(key, setup);
    setup.catch(() => readyTabs.delete(key));
  }
  await readyTabs.get(key);
}

export async function appendToSheet(tab: string, headers: string[], row: (string | number)[]) {
  const spreadsheetId = sheetsConfig().GOOGLE_SHEETS_SPREADSHEET_ID?.trim();
  if (!spreadsheetId) throw new Error("Set GOOGLE_SHEETS_SPREADSHEET_ID in D:/Nexis/.env, then retry.");
  await ensureTab(spreadsheetId, tab, headers);
  const result = await runGwsCommand([
    "sheets", "spreadsheets", "values", "append", "--params",
    JSON.stringify({ spreadsheetId, range: `'${tab.replace(/'/g, "''")}'!A1`, valueInputOption: "RAW", insertDataOption: "INSERT_ROWS" }),
    "--json", JSON.stringify({ values: [row] }),
  ]);
  // Do not retry append automatically: a lost response can still have written a row.
  if (result.updates?.updatedRows !== 1) throw new Error("Google Sheets did not confirm saving the row. Check the sheet before retrying.");
  return { spreadsheetId, range: result.updates.updatedRange as string };
}

export function sheetsError(error: unknown) {
  const message = error instanceof Error ? error.message : "Google Sheets could not save this item.";
  console.error("[Sheets]", message);
  if (/invalid_grant|authentication|auth error|login|credentials/i.test(message)) {
    return NextResponse.json({ error: "Google Sheets sign-in expired. Run gws auth login on this machine, then retry." }, { status: 503 });
  }
  return NextResponse.json({ error: message }, { status: 500 });
}
