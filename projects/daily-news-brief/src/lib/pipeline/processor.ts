import OpenAI from "openai";
import {
  buildPass1Prompt,
  buildSynthesisPrompt,
  type Pass1Result,
  type SynthesisResult,
} from "./prompts";
import { withRetry, extractJSON } from "./utils";
import type { RawArticle } from "./sources/types";

let client: OpenAI | null = null;

function getClient(): OpenAI {
  if (!client) {
    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) {
      throw new Error("OPENAI_API_KEY is not set in environment variables");
    }
    client = new OpenAI({ apiKey });
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
  const openai = getClient();

  const message = await withRetry(() =>
    openai.chat.completions.create({
      model: "gpt-4o-mini",
      max_tokens: 2048,
      messages: [{ role: "user", content: prompt }],
    })
  );

  const responseText = message.choices[0]?.message?.content ?? "";

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
  const openai = getClient();

  const message = await withRetry(() =>
    openai.chat.completions.create({
      model: "gpt-4o",
      max_tokens: 4096,
      messages: [{ role: "user", content: prompt }],
    })
  );

  const responseText = message.choices[0]?.message?.content ?? "";

  return parseJSON<SynthesisResult>(responseText, "synthesis");
}
