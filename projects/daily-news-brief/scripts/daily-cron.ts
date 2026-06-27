import { config } from "dotenv";
import { resolve } from "path";

// Load .env from project root
config({ path: resolve(__dirname, "..", ".env") });

import { generateDailyBrief, type BriefOptions } from "../src/lib/pipeline/run";
import { generateYoutubeBrief } from "../src/lib/pipeline/youtube-run";

function parseArgs(argv: string[]): { date?: string; opts: BriefOptions; runYoutube: boolean } {
  const opts: BriefOptions = {};
  let date: string | undefined;
  let runYoutube = false;

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === "--topic") {
      opts.mode = "topic";
      opts.topic = argv[++i];
    } else if (arg === "--days") {
      opts.days = parseInt(argv[++i], 10);
    } else if (arg === "--full" || arg === "--deep") {
      opts.depth = "full";
    } else if (arg === "--youtube") {
      runYoutube = true;
    } else if (!arg.startsWith("--") && !date) {
      date = arg; // optional positional YYYY-MM-DD
    }
  }
  return { date, opts, runYoutube };
}

async function main() {
  const { date, opts, runYoutube } = parseArgs(process.argv.slice(2));

  if (runYoutube) {
    console.log(
      `[${new Date().toISOString()}] Starting YouTube brief generation${date ? ` for ${date}` : ""}...`
    );
    const result = await generateYoutubeBrief(date);
    if (result.success) {
      console.log(`[${new Date().toISOString()}] YouTube brief generated successfully for ${result.date}`);
    } else {
      console.log(`[${new Date().toISOString()}] YouTube brief generated with errors for ${result.date}:`);
      result.errors.forEach((e) => console.error(`  - ${e}`));
    }
    process.exit(result.success ? 0 : 1);
    return;
  }

  console.log(
    `[${new Date().toISOString()}] Starting brief generation${date ? ` for ${date}` : ""}` +
      `${opts.mode === "topic" ? ` (topic: "${opts.topic}")` : ""}...`
  );

  const result = await generateDailyBrief(date, opts);

  if (result.success) {
    console.log(
      `[${new Date().toISOString()}] Brief generated successfully for ${result.date}`
    );
  } else {
    console.log(
      `[${new Date().toISOString()}] Brief generated with errors for ${result.date}:`
    );
    result.errors.forEach((e) => console.error(`  - ${e}`));
  }

  process.exit(result.success ? 0 : 1);
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
