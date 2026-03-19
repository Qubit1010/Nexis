import { config } from "dotenv";
import { resolve } from "path";

// Load .env from project root
config({ path: resolve(__dirname, "..", ".env") });

import { generateDailyBrief } from "../src/lib/pipeline/run";

async function main() {
  const date = process.argv[2]; // Optional: pass a specific date
  console.log(
    `[${new Date().toISOString()}] Starting daily brief generation${date ? ` for ${date}` : ""}...`
  );

  const result = await generateDailyBrief(date);

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
