// CLI for the one-time sheet import. Dry run by default; pass --commit to write.
//   node scripts/import-sheets.ts                 # dry run: what would be imported
//   node scripts/import-sheets.ts --commit        # import (idempotent: safe to repeat)
//   node scripts/import-sheets.ts --only schedule # one source: content_ideas | topics | schedule
import { importSheets } from "../server/integrations/sheets-import.ts";
import { seed } from "../server/db/seed.ts";

await seed(); // channels must exist before items are created, or imported items get none
const args = process.argv.slice(2);
const commit = args.includes("--commit");
const only = args.includes("--only") ? [args[args.indexOf("--only") + 1] as "content_ideas" | "topics" | "schedule"] : undefined;

const report = await importSheets({ dryRun: !commit, sources: only });
console.log(JSON.stringify(report, null, 2));
if (!commit) console.log("\nDry run only. Re-run with --commit to import.");
