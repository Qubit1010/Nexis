// Work with Content OS run folders outside the scheduler.
//
//   node scripts/run-folder.ts prepare <itemId>            # writes input.json + prompt.md, prints the folder
//   node scripts/run-folder.ts adopt <itemId> <runFolder>   # validates output.json, runs the checks, stores a version
//
// "prepare" + a normal Claude session + "adopt" is how a draft written by hand (or by a
// session that is already signed in) comes into Content OS for review and scheduling.
import path from "node:path";
import { RUNS_DIR } from "../server/config.ts";
import { ulid } from "../server/lib/ids.ts";
import { adoptRunFolder, prepareRunFolder } from "../server/engine/generate.ts";

const [cmd, itemId, folder] = process.argv.slice(2);
if (cmd === "prepare" && itemId) {
  const runDir = path.join(RUNS_DIR, `manual-${ulid()}`);
  const { systemPromptFile } = await prepareRunFolder(itemId, runDir);
  console.log(JSON.stringify({ runDir, prompt: path.join(runDir, "prompt.md"), contract: systemPromptFile }, null, 2));
} else if (cmd === "adopt" && itemId && folder) {
  const { versionId, checks } = await adoptRunFolder(itemId, path.resolve(folder));
  console.log(JSON.stringify({ versionId, fails: checks.filter((c) => c.level === "fail"), warns: checks.filter((c) => c.level === "warn") }, null, 2));
} else {
  console.error("usage: run-folder.ts prepare <itemId> | adopt <itemId> <runFolder>");
  process.exit(2);
}
