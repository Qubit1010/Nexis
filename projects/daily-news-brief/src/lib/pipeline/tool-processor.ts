import {
  buildToolAnalysisPrompt,
  buildToolsSynthesisPrompt,
  type ToolAnalysisResult,
  type ToolSynthesisResult,
} from "./tool-prompts";
import { callWithFallback } from "./processor";
import { extractJSON } from "./utils";
import type { RawTool } from "./sources/tool-types";

function parseJSON<T>(text: string, context: string): T {
  try {
    return JSON.parse(text);
  } catch {
    const extracted = extractJSON(text);
    if (extracted) return JSON.parse(extracted);
    throw new Error(
      `Failed to parse LLM response for "${context}": ${text.slice(0, 200)}`
    );
  }
}

export interface ToolCategoryPass1Output {
  categoryName: string;
  categorySlug: string;
  summary: string;
  bestInDomain: { name: string; reason: string } | null;
  toolCount: number;
  tools: Array<{
    name: string;
    oneLiner: string;
    bestUseCase: string;
    audienceHook: string;
    relevanceScore: number;
    upvotes?: number;
  }>;
}

export async function analyzeToolCategory(
  categoryName: string,
  audienceLens: string,
  tools: RawTool[]
): Promise<ToolAnalysisResult> {
  if (tools.length === 0) {
    return {
      summary: "No new tools found in this category today.",
      tools: [],
    };
  }

  const prompt = buildToolAnalysisPrompt(categoryName, audienceLens, tools);
  const responseText = await callWithFallback(
    prompt,
    categoryName,
    "gpt-4o-mini",
    "claude-haiku-4-5-20251001",
    4096
  );

  return parseJSON<ToolAnalysisResult>(responseText, categoryName);
}

export async function synthesizeToolBrief(
  categoryResults: ToolCategoryPass1Output[],
  date: string
): Promise<ToolSynthesisResult> {
  const prompt = buildToolsSynthesisPrompt(
    categoryResults.map((c) => ({
      categoryName: c.categoryName,
      categorySlug: c.categorySlug,
      summary: c.summary,
      bestInDomain: c.bestInDomain,
      tools: c.tools,
    })),
    date
  );

  const responseText = await callWithFallback(
    prompt,
    "tool-synthesis",
    "gpt-4o",
    "claude-sonnet-4-6",
    8192
  );

  return parseJSON<ToolSynthesisResult>(responseText, "tool-synthesis");
}
