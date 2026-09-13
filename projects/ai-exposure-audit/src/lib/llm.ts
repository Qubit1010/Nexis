import Anthropic from "@anthropic-ai/sdk";
import OpenAI from "openai";

/**
 * Three-leg fallback. The repo's direct Anthropic and OpenAI keys are both known to
 * run dry, so OpenRouter sits behind them.
 *
 * Model ids verified live against each provider's own /models endpoint on 2026-09-05:
 *   - claude-sonnet-5            (api.anthropic.com/v1/models)
 *   - gpt-5.2                    (api.openai.com/v1/models)
 *   - anthropic/claude-sonnet-5  (openrouter.ai/api/v1/models)
 *
 * Sonnet tier, not Opus: scoring a handful of service lines against a fixed rubric is
 * not a frontier reasoning task.
 *
 * The contract that matters: if every leg fails, this throws. It never returns a
 * degraded, partial or placeholder result. A diagnostic sold at $5,000 must fail
 * visibly rather than quietly emit a plausible number.
 */

const ANTHROPIC_MODEL = "claude-sonnet-5";
const OPENAI_MODEL = "gpt-5.2";
const OPENROUTER_MODEL = "anthropic/claude-sonnet-5";
const MAX_TOKENS = 4096;

export type LlmProvider = "anthropic" | "openai" | "openrouter";

export interface LlmResult {
  text: string;
  provider: LlmProvider;
  model: string;
}

export class AllProvidersFailedError extends Error {
  readonly attempts: { provider: string; error: string }[];
  constructor(attempts: { provider: string; error: string }[]) {
    const detail = attempts.map((a) => `${a.provider}: ${a.error}`).join(" | ");
    super(
      `Every LLM provider failed, so no scores were produced. Nothing was guessed or defaulted. Details: ${
        detail || "no provider was configured"
      }`
    );
    this.name = "AllProvidersFailedError";
    this.attempts = attempts;
  }
}

function errText(err: unknown): string {
  if (err instanceof Error) return err.message;
  return String(err);
}

async function tryAnthropic(system: string, user: string): Promise<LlmResult> {
  const key = process.env.ANTHROPIC_API_KEY;
  if (!key) throw new Error("ANTHROPIC_API_KEY is not set");
  const client = new Anthropic({ apiKey: key });
  const msg = await client.messages.create({
    model: ANTHROPIC_MODEL,
    max_tokens: MAX_TOKENS,
    system,
    messages: [{ role: "user", content: user }],
  });
  const text = msg.content
    .filter((b): b is Anthropic.TextBlock => b.type === "text")
    .map((b) => b.text)
    .join("");
  if (!text.trim()) throw new Error("returned an empty response");
  return { text, provider: "anthropic", model: ANTHROPIC_MODEL };
}

async function tryOpenAI(system: string, user: string): Promise<LlmResult> {
  const key = process.env.OPENAI_API_KEY;
  if (!key) throw new Error("OPENAI_API_KEY is not set");
  const client = new OpenAI({ apiKey: key });
  const res = await client.chat.completions.create({
    model: OPENAI_MODEL,
    // gpt-5* rejects max_tokens. It wants max_completion_tokens plus reasoning_effort.
    max_completion_tokens: MAX_TOKENS,
    reasoning_effort: "low",
    messages: [
      { role: "system", content: system },
      { role: "user", content: user },
    ],
  });
  const text = res.choices[0]?.message?.content ?? "";
  if (!text.trim()) throw new Error("returned an empty response");
  return { text, provider: "openai", model: OPENAI_MODEL };
}

async function tryOpenRouter(system: string, user: string): Promise<LlmResult> {
  const key = process.env.OPENROUTER_API_KEY;
  if (!key) throw new Error("OPENROUTER_API_KEY is not set");
  const client = new OpenAI({
    apiKey: key,
    baseURL: "https://openrouter.ai/api/v1",
  });
  const res = await client.chat.completions.create({
    model: OPENROUTER_MODEL,
    max_tokens: MAX_TOKENS,
    messages: [
      { role: "system", content: system },
      { role: "user", content: user },
    ],
  });
  const text = res.choices[0]?.message?.content ?? "";
  if (!text.trim()) throw new Error("returned an empty response");
  return { text, provider: "openrouter", model: OPENROUTER_MODEL };
}

export async function complete(system: string, user: string): Promise<LlmResult> {
  const legs: [string, () => Promise<LlmResult>][] = [
    ["anthropic/claude-sonnet-5", () => tryAnthropic(system, user)],
    ["openai/gpt-5.2", () => tryOpenAI(system, user)],
    ["openrouter/anthropic-claude-sonnet-5", () => tryOpenRouter(system, user)],
  ];

  const attempts: { provider: string; error: string }[] = [];
  for (const [label, run] of legs) {
    try {
      return await run();
    } catch (err) {
      attempts.push({ provider: label, error: errText(err) });
      console.warn(`[llm] ${label} failed: ${errText(err)}`);
    }
  }
  throw new AllProvidersFailedError(attempts);
}

/**
 * Models wrap JSON in prose and fences regardless of instruction. Pull the first
 * balanced JSON object out. A parse failure throws; it is never coerced into a default.
 */
export function extractJson<T>(text: string): T {
  const fenced = text.match(/```(?:json)?\s*([\s\S]*?)```/);
  const candidate = fenced ? fenced[1] : text;

  const start = candidate.indexOf("{");
  if (start === -1) {
    throw new Error(`No JSON object found in the model response. Raw start: ${text.slice(0, 300)}`);
  }

  let depth = 0;
  let inString = false;
  let escaped = false;
  for (let i = start; i < candidate.length; i++) {
    const ch = candidate[i];
    if (escaped) {
      escaped = false;
      continue;
    }
    if (ch === "\\") {
      escaped = true;
      continue;
    }
    if (ch === '"') inString = !inString;
    if (inString) continue;
    if (ch === "{") depth++;
    if (ch === "}") {
      depth--;
      if (depth === 0) {
        const slice = candidate.slice(start, i + 1);
        try {
          return JSON.parse(slice) as T;
        } catch (err) {
          throw new Error(
            `Model returned malformed JSON: ${err instanceof Error ? err.message : String(err)}`
          );
        }
      }
    }
  }
  throw new Error("Model response contained an unterminated JSON object");
}
