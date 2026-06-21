import { config } from "dotenv";
import { resolve } from "path";

config({ path: resolve(__dirname, "..", ".env") });

import { generateToolsBrief } from "../src/lib/pipeline/tool-run";

async function main() {
  const args = process.argv.slice(2);
  const depth = args.includes("--full") || args.includes("--deep") ? "full" : "lean";
  const date = args.find((a) => !a.startsWith("--"));
  console.log(
    `[${new Date().toISOString()}] Starting Practical AI brief generation${date ? ` for ${date}` : ""} (${depth})...`
  );

  const result = await generateToolsBrief(date, depth);

  if (result.success) {
    console.log(
      `[${new Date().toISOString()}] Tools brief generated successfully for ${result.date}`
    );
  } else {
    console.log(
      `[${new Date().toISOString()}] Tools brief generated with errors for ${result.date}:`
    );
    result.errors.forEach((e) => console.error(`  - ${e}`));
  }

  process.exit(result.success ? 0 : 1);
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
