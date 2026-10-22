// LinkedIn has no newsletter API, so publishing is assisted: Content OS flags the
// issue ready at its time, the reviewer pastes it (rich text copy in the UI), then
// marks it published here, which appends the edition's issue log.
import fs from "node:fs";
import path from "node:path";
import { NEXIS_ROOT } from "../config.ts";

const PERSONAL_TEMPLATE = "# Notes from the Workbench - issue log\n\n| # | Date drafted | Title | Source | Doc | Status |\n|---|---|---|---|---|---|\n";

export function appendIssueLog(input: {
  edition: string;
  issueLogRel: string;
  draftedOn: string;
  publishedOn: string;
  title: string;
  source: string;
  url: string;
}): string {
  const file = path.join(NEXIS_ROOT, input.issueLogRel);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  if (!fs.existsSync(file)) fs.writeFileSync(file, input.edition === "agency" ? "| Date drafted | Title | Source | Google Doc | Status |\n| --- | --- | --- | --- | --- |\n" : PERSONAL_TEMPLATE);
  const text = fs.readFileSync(file, "utf8");
  const cell = (s: string) => s.replace(/\|/g, "/").replace(/[\r\n]+/g, " ").trim();
  let row: string;
  if (input.edition === "agency") {
    // Agency log columns: Date drafted | Title | Source | Google Doc | Status
    row = `| ${input.draftedOn} | ${cell(input.title)} | ${cell(input.source)} | ${cell(input.url)} | published ${input.publishedOn} |`;
  } else {
    const n = (text.match(/^\|\s*\d+\s*\|/gm) || []).length + 1;
    row = `| ${n} | ${input.draftedOn} | ${cell(input.title)} | ${cell(input.source)} | ${cell(input.url)} | published ${input.publishedOn} |`;
  }
  fs.writeFileSync(file, text.replace(/\s*$/, "\n") + row + "\n");
  return file;
}
