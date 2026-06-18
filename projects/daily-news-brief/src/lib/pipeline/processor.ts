import OpenAI from "openai";
import Anthropic from "@anthropic-ai/sdk";
import {
  buildPass1Prompt,
  buildSynthesisPrompt,
  type Pass1Result,
  type SynthesisResult,
} from "./prompts";
import { withRetry, extractJSON } from "./utils";
import type { RawArticle } from "./sources/types";

let openaiClient: OpenAI | null = null;
let anthropicClient: Anthropic | null = null;

function getOpenAIClient(): OpenAI {
  if (!openaiClient) {
    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) throw new Error("OPENAI_API_KEY is not set");
    openaiClient = new OpenAI({ apiKey });
  }
  return openaiClient;
}

function getAnthropicClient(): Anthropic {
  if (!anthropicClient) {
    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) throw new Error("ANTHROPIC_API_KEY is not set");
    anthropicClient = new Anthropic({ apiKey });
  }
  return anthropicClient;
}

function isQuotaError(err: unknown): boolean {
  if (err instanceof Error) {
    return (
      err.message.includes("429") ||
      err.message.includes("quota") ||
      err.message.includes("exceeded")
    );
  }
  return false;
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

export async function callWithFallback(
  prompt: string,
  context: string,
  openaiModel: string,
  claudeModel: string,
  maxTokens: number
): Promise<string> {
  // Try OpenAI first if key is available
  if (process.env.OPENAI_API_KEY) {
    try {
      const openai = getOpenAIClient();
      const params: OpenAI.Chat.Completions.ChatCompletionCreateParamsNonStreaming = {
        model: openaiModel,
        messages: [{ role: "user", content: prompt }],
      };
      // The gpt-5 family uses max_completion_tokens + reasoning_effort and rejects
      // the old max_tokens param (400 error), so branch on it.
      if (openaiModel.startsWith("gpt-5")) {
        params.max_completion_tokens = maxTokens;
        params.reasoning_effort = "low";
      } else {
        params.max_tokens = maxTokens;
      }
      const message = await withRetry(() =>
        openai.chat.completions.create(params)
      );
      return message.choices[0]?.message?.content ?? "";
    } catch (err) {
      if (isQuotaError(err)) {
        console.log(`  [Fallback] OpenAI quota exceeded for "${context}", switching to Claude...`);
      } else {
        throw err;
      }
    }
  } else {
    console.log(`  [Fallback] No OPENAI_API_KEY, using Claude for "${context}"...`);
  }

  // Fall back to Claude
  const anthropic = getAnthropicClient();
  const message = await withRetry(() =>
    anthropic.messages.create({
      model: claudeModel,
      max_tokens: maxTokens,
      messages: [{ role: "user", content: prompt }],
    })
  );
  const block = message.content[0];
  return block.type === "text" ? block.text : "";
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
  const responseText = await callWithFallback(
    prompt,
    categoryName,
    "gpt-5.4-mini",
    "claude-haiku-4-5-20251001",
    2048
  );

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
  const responseText = await callWithFallback(
    prompt,
    "synthesis",
    "gpt-5.2",
    "claude-sonnet-4-6",
    8192
  );

  return parseJSON<SynthesisResult>(responseText, "synthesis");
}
