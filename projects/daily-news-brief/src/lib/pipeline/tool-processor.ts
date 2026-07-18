import {
  buildToolAnalysisPrompt,
  buildToolsSynthesisPrompt,
  type ToolAnalysisResult,
  type ToolSynthesisResult,
} from "./tool-prompts";
import { callWithFallback } from "./processor";
import { extractJSON } from "./utils";
import type { PracticalItem, Mover } from "./sources/practical-index";

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
  }>;
}

export async function analyzeToolCategory(
  topicName: string,
  businessProblem: string,
  items: PracticalItem[]
): Promise<ToolAnalysisResult> {
  if (items.length === 0) {
    return {
      summary: "No notable updates for this topic today.",
      bestInDomain: null,
      tools: [],
    };
  }

  const prompt = buildToolAnalysisPrompt(topicName, businessProblem, items);
  const responseText = await callWithFallback(
    prompt,
    topicName,
    "gpt-5.4-mini",
    "claude-haiku-4-5-20251001",
    4096
  );

  return parseJSON<ToolAnalysisResult>(responseText, topicName);
}

export async function synthesizeToolBrief(
  categoryResults: ToolCategoryPass1Output[],
  date: string,
  movers: Mover[] = []
): Promise<ToolSynthesisResult> {
  const prompt = buildToolsSynthesisPrompt(
    categoryResults.map((c) => ({
      categoryName: c.categoryName,
      categorySlug: c.categorySlug,
      summary: c.summary,
      bestInDomain: c.bestInDomain,
      tools: c.tools,
    })),
    date,
    movers
  );

  const responseText = await callWithFallback(
    prompt,
    "tool-synthesis",
    "gpt-5.2",
    "claude-sonnet-4-6",
    8192
  );

  return parseJSON<ToolSynthesisResult>(responseText, "tool-synthesis");
}
