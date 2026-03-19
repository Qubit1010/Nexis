import Anthropic from "@anthropic-ai/sdk";
import {
  buildPass1Prompt,
  buildSynthesisPrompt,
  type Pass1Result,
  type SynthesisResult,
} from "./prompts";
import { withRetry, extractJSON } from "./utils";
import type { RawArticle } from "./sources/types";

let client: Anthropic | null = null;

function getClient(): Anthropic {
  if (!client) {
    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) {
      throw new Error("ANTHROPIC_API_KEY is not set in environment variables");
    }
    client = new Anthropic({ apiKey });
  }
  return client;
}

function parseJSON<T>(text: string, context: string): T {
  try {
    return JSON.parse(text);
  } catch {
    const extracted = extractJSON(text);
    if (extracted) {
      return JSON.parse(extracted);
    }
    throw new Error(
      `Failed to parse LLM response for "${context}": ${text.slice(0, 200)}`
    );
  }
}

export async function processCategoryPass1(
  categoryName: string,
  categoryDescription: string,
  articles: RawArticle[]
): Promise<Pass1Result> {
  if (articles.length === 0) {
    return {
      insight: "No articles found for this category today.",
      articles: [],
      emergingThemes: [],
    };
  }

  const prompt = buildPass1Prompt(categoryName, categoryDescription, articles);
  const anthropic = getClient();

  const message = await withRetry(() =>
    anthropic.messages.create({
      model: "claude-haiku-4-5-20251001",
      max_tokens: 2048,
      messages: [{ role: "user", content: prompt }],
    })
  );

  const responseText =
    message.content[0].type === "text" ? message.content[0].text : "";

  return parseJSON<Pass1Result>(responseText, categoryName);
}

export interface CategoryPass1Output {
  categoryName: string;
  categorySlug: string;
  insight: string;
  emergingThemes: string[];
  articleCount: number;
  topArticles: Array<{
    title: string;
    tldr: string;
    sentimentTag: string;
    relevanceScore: number;
    engagementScore?: number;
  }>;
}

export async function synthesizeBrief(
  categoryResults: CategoryPass1Output[],
  date: string
): Promise<SynthesisResult> {
  const prompt = buildSynthesisPrompt(categoryResults, date);
  const anthropic = getClient();

  const message = await withRetry(() =>
    anthropic.messages.create({
      model: "claude-sonnet-4-20250514",
      max_tokens: 4096,
      messages: [{ role: "user", content: prompt }],
    })
  );

  const responseText =
    message.content[0].type === "text" ? message.content[0].text : "";

  return parseJSON<SynthesisResult>(responseText, "synthesis");
}
