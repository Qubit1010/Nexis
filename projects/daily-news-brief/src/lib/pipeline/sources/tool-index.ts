import type { RawTool } from "./tool-types";
import { fetchFromProductHunt } from "./producthunt";
import { fetchFromHackerNewsShow } from "./hackernews-show";
import { fetchFromNewsletters } from "./newsletters";
import { fetchFromGitHubTrending } from "./github-trending";
import { fetchFromHuggingFace } from "./huggingface";
import { fetchFromFirecrawlDirectories } from "./firecrawl-directories";

export type { RawTool } from "./tool-types";

export async function fetchAllToolSources(): Promise<RawTool[]> {
  console.log("[ToolSources] Fetching from all tool sources in parallel...");

  const sourceCalls = [
    { name: "ProductHunt", fn: fetchFromProductHunt },
    { name: "ShowHN", fn: fetchFromHackerNewsShow },
    { name: "Newsletters", fn: fetchFromNewsletters },
    { name: "GitHubTrending", fn: fetchFromGitHubTrending },
    { name: "HuggingFace", fn: fetchFromHuggingFace },
    { name: "Firecrawl", fn: fetchFromFirecrawlDirectories },
  ];

  const results = await Promise.allSettled(sourceCalls.map((s) => s.fn()));

  const tools: RawTool[] = [];
  const sourceCounts: Record<string, number> = {};

  results.forEach((result, i) => {
    const name = sourceCalls[i].name;
    if (result.status === "fulfilled") {
      sourceCounts[name] = result.value.length;
      tools.push(...result.value);
    } else {
      console.error(`[ToolSources] ${name} failed:`, result.reason);
      sourceCounts[name] = 0;
    }
  });

  console.log(
    `[ToolSources] Totals: ${Object.entries(sourceCounts)
      .map(([k, v]) => `${k}=${v}`)
      .join(", ")}`
  );
  console.log(`[ToolSources] Grand total: ${tools.length} tools`);
  return tools;
}
