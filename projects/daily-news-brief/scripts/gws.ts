/**
 * Minimal Google Workspace access for the daily digest: Sheets read/write + one
 * Gmail send. Invokes the gws CLI the same way leads-to-crm's sheets.py does —
 * `node <cli>/run.js ...` directly, NOT through cmd.exe — so JSON args pass
 * verbatim with zero Windows quoting hell. Payloads here are tiny (a couple of
 * rows, one email), so no batching machinery is needed.
 */
import { spawn } from "child_process";
import { existsSync } from "fs";
import { join } from "path";

function findGws(): { cmd: string; base: string[]; shell: boolean } {
  const npmDir = join(process.env.APPDATA || "", "npm");
  for (const js of ["run.js", "run-gws.js"]) {
    const gwsJs = join(npmDir, "node_modules", "@googleworkspace", "cli", js);
    if (existsSync(gwsJs)) {
      for (const node of [
        join(npmDir, "node.exe"),
        join(process.env.ProgramFiles || "C:\\Program Files", "nodejs", "node.exe"),
      ]) {
        if (existsSync(node)) return { cmd: node, base: [gwsJs], shell: false };
      }
      return { cmd: "node", base: [gwsJs], shell: false };
    }
  }
  const gwsCmd = join(npmDir, "gws.cmd");
  if (existsSync(gwsCmd)) return { cmd: gwsCmd, base: [], shell: true };
  return { cmd: "gws", base: [], shell: true };
}

const GWS = findGws();

const TRANSIENT = [
  "request failed", "timeout", "timed out", "econnreset", "socket hang up",
  "etimedout", "enotfound", "503", "502", "500", "rate limit", "temporarily",
  "network", "unavailable",
];

function runOnce(args: string[]): Promise<unknown> {
  return new Promise((resolvePromise, reject) => {
    const child = spawn(GWS.cmd, [...GWS.base, ...args], {
      shell: GWS.shell,
      windowsHide: true,
      timeout: 120_000,
    });
    let out = "";
    let err = "";
    child.stdout.on("data", (d) => (out += d.toString("utf-8")));
    child.stderr.on("data", (d) => (err += d.toString("utf-8")));
    child.on("error", reject);
    child.on("close", (code) => {
      if (code === 0) {
        const s = out.trim();
        if (!s) return resolvePromise({});
        try {
          resolvePromise(JSON.parse(s));
        } catch {
          resolvePromise({ raw: s });
        }
        return;
      }
      reject(new Error(err.trim() || `gws exited ${code}`));
    });
  });
}

async function runGws(args: string[], jsonBody?: unknown): Promise<any> {
  const full = jsonBody === undefined ? args : [...args, "--json", JSON.stringify(jsonBody)];
  let lastErr = "gws error";
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      return await runOnce(full);
    } catch (e) {
      lastErr = (e as Error).message;
      if (attempt < 2 && TRANSIENT.some((m) => lastErr.toLowerCase().includes(m))) {
        await new Promise((r) => setTimeout(r, 2000 * (attempt + 1)));
        continue;
      }
      break;
    }
  }
  throw new Error(lastErr);
}

// --- Sheets ---

function colLetter(idx0: number): string {
  let s = "";
  let n = idx0 + 1;
  while (n) {
    const rem = (n - 1) % 26;
    s = String.fromCharCode(65 + rem) + s;
    n = Math.floor((n - 1) / 26);
  }
  return s;
}

export async function createDigestSpreadsheet(title: string, tabs: string[]): Promise<string> {
  const res = await runGws(["sheets", "spreadsheets", "create"], {
    properties: { title },
    sheets: tabs.map((t) => ({ properties: { title: t } })),
  });
  if (!res?.spreadsheetId) throw new Error(`create spreadsheet failed: ${JSON.stringify(res)}`);
  return res.spreadsheetId as string;
}

async function readValues(sheetId: string, tab: string): Promise<string[][]> {
  const data = await runGws([
    "sheets", "spreadsheets", "values", "get",
    "--params", JSON.stringify({ spreadsheetId: sheetId, range: tab }),
  ]);
  return (data?.values as string[][]) || [];
}

async function updateRange(sheetId: string, a1: string, rows: string[][]): Promise<void> {
  await runGws(
    ["sheets", "spreadsheets", "values", "update", "--params",
      JSON.stringify({ spreadsheetId: sheetId, range: a1, valueInputOption: "RAW" })],
    { values: rows }
  );
}

async function appendRow(sheetId: string, tab: string, row: string[]): Promise<void> {
  await runGws(
    ["sheets", "spreadsheets", "values", "append", "--params",
      JSON.stringify({
        spreadsheetId: sheetId, range: `${tab}!A1`,
        valueInputOption: "RAW", insertDataOption: "INSERT_ROWS",
      })],
    { values: [row] }
  );
}

/**
 * One row per day: write the header if the tab is empty, replace the row whose
 * first cell already equals row[0] (the date), else append. Idempotent per date.
 */
export async function upsertRowByDate(
  sheetId: string,
  tab: string,
  header: string[],
  row: string[]
): Promise<"updated" | "appended"> {
  const values = await readValues(sheetId, tab);
  if (values.length === 0) {
    await updateRange(sheetId, `${tab}!A1`, [header]);
  }
  const lastCol = colLetter(row.length - 1);
  for (let i = 1; i < values.length; i++) {
    if ((values[i]?.[0] || "") === row[0]) {
      await updateRange(sheetId, `${tab}!A${i + 1}:${lastCol}${i + 1}`, [row]);
      return "updated";
    }
  }
  await appendRow(sheetId, tab, row);
  return "appended";
}

async function getTabGid(sheetId: string, title: string): Promise<number> {
  const meta = await runGws([
    "sheets", "spreadsheets", "get",
    "--params", JSON.stringify({ spreadsheetId: sheetId }),
  ]);
  for (const sh of meta?.sheets || []) {
    const p = sh.properties || {};
    if ((p.title || "").toLowerCase() === title.toLowerCase()) return p.sheetId as number;
  }
  throw new Error(`tab not found: ${title}`);
}

/**
 * Make a digest tab readable: frozen bold header, body wrapped + top/left aligned
 * (so tall multi-line rows read from the top, not floating centered), and per-column
 * widths. Idempotent — safe to re-apply every run so new rows stay formatted.
 */
export async function formatDigestTab(
  sheetId: string,
  tab: string,
  colWidths: number[]
): Promise<void> {
  const gid = await getTabGid(sheetId, tab);
  const requests: unknown[] = [
    {
      updateSheetProperties: {
        properties: { sheetId: gid, gridProperties: { frozenRowCount: 1 } },
        fields: "gridProperties.frozenRowCount",
      },
    },
    {
      repeatCell: {
        range: { sheetId: gid, startRowIndex: 0, endRowIndex: 1 },
        cell: {
          userEnteredFormat: {
            textFormat: { bold: true },
            backgroundColor: { red: 0.9, green: 0.92, blue: 0.96 },
            horizontalAlignment: "CENTER",
            verticalAlignment: "MIDDLE",
            wrapStrategy: "WRAP",
          },
        },
        fields:
          "userEnteredFormat(textFormat,backgroundColor,horizontalAlignment,verticalAlignment,wrapStrategy)",
      },
    },
    {
      repeatCell: {
        range: { sheetId: gid, startRowIndex: 1 },
        cell: {
          userEnteredFormat: {
            wrapStrategy: "WRAP",
            verticalAlignment: "TOP",
            horizontalAlignment: "LEFT",
          },
        },
        fields: "userEnteredFormat(wrapStrategy,verticalAlignment,horizontalAlignment)",
      },
    },
  ];
  colWidths.forEach((w, i) =>
    requests.push({
      updateDimensionProperties: {
        range: { sheetId: gid, dimension: "COLUMNS", startIndex: i, endIndex: i + 1 },
        properties: { pixelSize: w },
        fields: "pixelSize",
      },
    })
  );
  await runGws(
    ["sheets", "spreadsheets", "batchUpdate", "--params", JSON.stringify({ spreadsheetId: sheetId })],
    { requests }
  );
}

// --- Gmail ---

export async function sendEmail(to: string, subject: string, html: string): Promise<void> {
  const mime = [
    `To: ${to}`,
    `Subject: ${subject}`,
    "MIME-Version: 1.0",
    'Content-Type: text/html; charset="UTF-8"',
    "",
    html,
  ].join("\r\n");
  const raw = Buffer.from(mime, "utf-8").toString("base64url");
  await runGws(
    ["gmail", "users", "messages", "send", "--params", JSON.stringify({ userId: "me" })],
    { raw }
  );
}
