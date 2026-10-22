/**
 * Google Workspace CLI access, invoked as `node <cli>/run.js ...` directly (no
 * cmd.exe) so JSON args pass verbatim. Same approach as daily-news-brief's
 * scripts/gws.ts, plus one more search location: on this machine gws is only
 * installed inside the Codex app's virtualized AppData, and running it from
 * there still uses the shared ~/.config/gws login.
 */
import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

export function findGwsRunJs(): string | null {
  const candidates: string[] = [];
  if (process.env.GWS_RUN_JS) candidates.push(process.env.GWS_RUN_JS);
  const appdata = process.env.APPDATA || "";
  candidates.push(path.join(appdata, "npm", "node_modules", "@googleworkspace", "cli", "run.js"));
  const packages = path.join(process.env.LOCALAPPDATA || "", "Packages");
  try {
    for (const dir of fs.readdirSync(packages)) {
      if (!dir.startsWith("OpenAI.Codex_")) continue;
      candidates.push(
        path.join(packages, dir, "LocalCache", "Roaming", "npm", "node_modules", "@googleworkspace", "cli", "run.js"),
      );
    }
  } catch {
    /* no Packages dir (non-Windows or no Store apps) */
  }
  return candidates.find((p) => fs.existsSync(p)) ?? null;
}

/**
 * Python skill scripts (save_content.py, sheets.py) look for gws under %APPDATA%\npm.
 * When the only install is the Codex app's, point APPDATA at its virtualized Roaming dir
 * for that child process so those scripts find it too.
 */
export function gwsChildEnv(base: NodeJS.ProcessEnv = process.env): NodeJS.ProcessEnv {
  const runJs = findGwsRunJs();
  if (!runJs || !runJs.includes("OpenAI.Codex_")) return base;
  const roaming = runJs.slice(0, runJs.toLowerCase().indexOf(`${path.sep}npm${path.sep}`.toLowerCase()));
  return { ...base, APPDATA: roaming };
}

const TRANSIENT = [
  "request failed", "timeout", "timed out", "econnreset", "socket hang up", "etimedout",
  "enotfound", "503", "502", "500", "rate limit", "temporarily", "network", "unavailable",
];

export function runGwsOnce(args: string[], timeoutMs = 120_000): Promise<any> {
  const runJs = findGwsRunJs();
  if (!runJs) return Promise.reject(new Error("gws CLI not found. Install it with: npm i -g @googleworkspace/cli"));
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, [runJs, ...args], { windowsHide: true, timeout: timeoutMs });
    let out = "";
    let err = "";
    child.stdout.on("data", (d) => (out += d.toString("utf-8")));
    child.stderr.on("data", (d) => (err += d.toString("utf-8")));
    child.on("error", reject);
    child.on("close", (code) => {
      const s = out.trim();
      if (code === 0) {
        if (!s) return resolve({});
        try {
          const parsed = JSON.parse(s);
          if (parsed?.error) return reject(new Error(parsed.error.message || JSON.stringify(parsed.error)));
          return resolve(parsed);
        } catch {
          return resolve({ raw: s });
        }
      }
      try {
        const parsed = JSON.parse(s);
        reject(new Error(parsed.error?.message || parsed.message || err.trim() || `gws exited ${code}`));
      } catch {
        reject(new Error(err.trim() || s || `gws exited ${code}`));
      }
    });
  });
}

/** Retries transient failures. Never use for appends: a lost response can still have written. */
export async function runGws(args: string[], jsonBody?: unknown): Promise<any> {
  const full = jsonBody === undefined ? args : [...args, "--json", JSON.stringify(jsonBody)];
  let last = "gws error";
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      return await runGwsOnce(full);
    } catch (e) {
      last = (e as Error).message;
      if (attempt < 2 && TRANSIENT.some((m) => last.toLowerCase().includes(m))) {
        await new Promise((r) => setTimeout(r, 2000 * (attempt + 1)));
        continue;
      }
      break;
    }
  }
  throw new Error(last);
}

const q = (tab: string) => `'${tab.replace(/'/g, "''")}'`;

export async function readValues(sheetId: string, range: string): Promise<string[][]> {
  const data = await runGws(["sheets", "spreadsheets", "values", "get", "--params", JSON.stringify({ spreadsheetId: sheetId, range })]);
  return (data?.values as string[][]) || [];
}

export async function readTab(sheetId: string, tab: string): Promise<string[][]> {
  return readValues(sheetId, q(tab));
}

/** Cell values plus strikethrough runs (the Topics Ideas tab encodes "used" as strikethrough). */
export async function readTabGrid(sheetId: string, tab: string) {
  const data = await runGws([
    "sheets", "spreadsheets", "get", "--params",
    JSON.stringify({
      spreadsheetId: sheetId,
      ranges: [q(tab)],
      includeGridData: true,
      fields: "sheets(data(rowData(values(formattedValue,effectiveFormat(textFormat(strikethrough)),textFormatRuns(format(strikethrough))))))",
    }),
  ]);
  type Cell = { formattedValue?: string; effectiveFormat?: { textFormat?: { strikethrough?: boolean } }; textFormatRuns?: { format?: { strikethrough?: boolean } }[] };
  const rows: { values?: Cell[] }[] = data?.sheets?.[0]?.data?.[0]?.rowData || [];
  return rows.map((r) =>
    (r.values || []).map((c) => ({
      value: c.formattedValue ?? "",
      struck:
        !!c.effectiveFormat?.textFormat?.strikethrough ||
        (!!c.textFormatRuns?.length && c.textFormatRuns.every((run) => run.format?.strikethrough)),
    })),
  );
}

export async function sheetTabs(sheetId: string): Promise<{ title: string; sheetId: number }[]> {
  const meta = await runGws(["sheets", "spreadsheets", "get", "--params", JSON.stringify({ spreadsheetId: sheetId, fields: "sheets(properties(title,sheetId))" })]);
  return (meta?.sheets || []).map((s: { properties: { title: string; sheetId: number } }) => s.properties);
}

export async function ensureTab(sheetId: string, tab: string): Promise<void> {
  const tabs = await sheetTabs(sheetId);
  if (tabs.some((t) => t.title === tab)) return;
  await runGws(["sheets", "spreadsheets", "batchUpdate", "--params", JSON.stringify({ spreadsheetId: sheetId })], {
    requests: [{ addSheet: { properties: { title: tab, gridProperties: { frozenRowCount: 1 } } } }],
  });
}

/** Whole-tab replace: clear then write. No positional partial writes, ever. */
export async function replaceTab(sheetId: string, tab: string, rows: (string | number)[][]): Promise<void> {
  await ensureTab(sheetId, tab);
  await runGws(["sheets", "spreadsheets", "values", "clear", "--params", JSON.stringify({ spreadsheetId: sheetId, range: q(tab) })], {});
  if (!rows.length) return;
  await runGws(
    ["sheets", "spreadsheets", "values", "update", "--params", JSON.stringify({ spreadsheetId: sheetId, range: `${q(tab)}!A1`, valueInputOption: "USER_ENTERED" })],
    { values: rows },
  );
}

export async function gwsHealth(): Promise<{ ok: boolean; detail: string }> {
  const runJs = findGwsRunJs();
  if (!runJs) return { ok: false, detail: "gws CLI not installed (npm i -g @googleworkspace/cli)" };
  try {
    await runGwsOnce(["drive", "about", "get", "--params", JSON.stringify({ fields: "user(emailAddress)" })], 45_000);
    return { ok: true, detail: runJs.includes("OpenAI.Codex_") ? "using the Codex app's gws install" : "ok" };
  } catch (e) {
    const msg = (e as Error).message;
    return { ok: false, detail: /invalid_grant|auth|login|credential/i.test(msg) ? "gws login expired: run gws auth login" : msg.slice(0, 200) };
  }
}
