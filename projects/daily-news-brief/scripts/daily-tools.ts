import { config } from "dotenv";
import { resolve } from "path";

config({ path: resolve(__dirname, "..", ".env") });

import { generateToolsBrief } from "../src/lib/pipeline/tool-run";

async function main() {
  const date = process.argv[2];
  console.log(
    `[${new Date().toISOString()}] Starting tools brief generation${date ? ` for ${date}` : ""}...`
  );

  const result = await generateToolsBrief(date);

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
