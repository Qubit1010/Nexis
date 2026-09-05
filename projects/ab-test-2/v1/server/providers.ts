/**
 * Draft providers.
 *
 * This file is what makes "runs and is fully testable without an API key" true rather than
 * aspirational. Everything upstream of here talks to the `DraftProvider` interface, and
 * `selectProvider` decides at runtime which implementation is behind it. The Anthropic SDK is
 * imported lazily, so with no key the process never even loads it.
 */

import { MODEL_ID } from './pricing.ts';
import { AppError } from './errors.ts';

export type DraftInput = {
  systemPrompt: string;
  subject: string;
  body: string;
};

export type DraftResult = {
  text: string;
  inputTokens: number | null;
  outputTokens: number | null;
};

export type ProviderName = 'anthropic' | 'stub';

export type DraftProvider = {
  name: ProviderName;
  model: string;
  draft(input: DraftInput): Promise<DraftResult>;
};

function userMessage(input: DraftInput): string {
  return `An enquiry has come in. Draft my reply.\n\nSubject: ${input.subject}\n\n${input.body}`;
}

// --------------------------------------------------------------------------------------
// Anthropic
// --------------------------------------------------------------------------------------

/**
 * Request shape follows the `claude-api` skill:
 *   - adaptive thinking (`budget_tokens` is rejected with a 400 on Opus 5)
 *   - no assistant prefill (also a 400 on this model family)
 *   - `effort` lives inside `output_config`, not at the top level
 *
 * NOT VERIFIED AGAINST THE LIVE API. There is no API key in this environment, so this path
 * has never been executed. It is written from the skill's documented request shape and is
 * exercised in tests only through a fake SDK client.
 */
export function createAnthropicProvider(apiKey: string, model: string = MODEL_ID): DraftProvider {
  let clientPromise: Promise<AnthropicLike> | null = null;

  async function getClient(): Promise<AnthropicLike> {
    if (clientPromise === null) {
      clientPromise = import('@anthropic-ai/sdk').then((mod) => {
        const Ctor = mod.default;
        return new Ctor({ apiKey }) as unknown as AnthropicLike;
      });
    }
    return clientPromise;
  }

  return {
    name: 'anthropic',
    model,
    async draft(input: DraftInput): Promise<DraftResult> {
      const client = await getClient();
      return draftWithClient(client, model, input);
    },
  };
}

/** The slice of the SDK this app actually uses. Kept narrow so a fake is trivial in tests. */
export type AnthropicLike = {
  messages: {
    create(params: Record<string, unknown>): Promise<AnthropicResponse>;
  };
};

export type AnthropicResponse = {
  content: Array<{ type: string; text?: string }>;
  stop_reason?: string | null;
  stop_details?: { type?: string; category?: string | null; explanation?: string | null } | null;
  usage?: { input_tokens?: number; output_tokens?: number } | null;
};

/** Exported so tests can drive the real request/response handling with a fake client. */
export async function draftWithClient(
  client: AnthropicLike,
  model: string,
  input: DraftInput,
): Promise<DraftResult> {
  let response: AnthropicResponse;
  try {
    response = await client.messages.create({
      model,
      max_tokens: 4000,
      system: input.systemPrompt,
      thinking: { type: 'adaptive' },
      output_config: { effort: 'medium' },
      messages: [{ role: 'user', content: userMessage(input) }],
    });
  } catch (cause) {
    const message = cause instanceof Error ? cause.message : 'Unknown Anthropic SDK error';
    throw new AppError('provider_error', `Anthropic request failed: ${message}`, 502);
  }

  // `stop_details` is populated only on a refusal, so guard before reading it.
  if (response.stop_reason === 'refusal') {
    const category = response.stop_details?.category ?? 'unspecified';
    throw new AppError(
      'provider_error',
      `The model declined to answer this enquiry (category: ${category}).`,
      502,
    );
  }

  const parts: string[] = [];
  for (const block of response.content ?? []) {
    if (block.type === 'text' && typeof block.text === 'string') parts.push(block.text);
  }
  const text = parts.join('\n').trim();

  if (text.length === 0) {
    throw new AppError('provider_error', 'Anthropic returned no text content.', 502);
  }

  return {
    text,
    inputTokens: response.usage?.input_tokens ?? null,
    outputTokens: response.usage?.output_tokens ?? null,
  };
}

// --------------------------------------------------------------------------------------
// Stub
// --------------------------------------------------------------------------------------

export const STUB_MARKER = '[STUB DRAFT - no ANTHROPIC_API_KEY set, no model was called]';

/** FNV-1a. Only needs to be stable and well spread, not cryptographic. */
function hash(text: string): number {
  let h = 0x811c9dc5;
  for (let i = 0; i < text.length; i += 1) {
    h ^= text.charCodeAt(i);
    h = Math.imul(h, 0x01000193) >>> 0;
  }
  return h >>> 0;
}

const OPENERS = [
  'Thanks for reaching out about this.',
  'Appreciate you getting in touch.',
  'Thanks for the detail, that helps.',
  'Good to hear from you.',
];

const MIDDLES = [
  'From what you have described, this is well inside what we do, and the shape of it is clear enough to scope properly.',
  'This is a familiar problem and there are two sensible ways to approach it, depending on how fixed your timeline is.',
  'There is enough here to give you a straight answer, though a couple of specifics would sharpen the estimate.',
  'The core of it is straightforward. The part worth talking through is where it touches your existing setup.',
];

const CLOSERS = [
  'Happy to walk through it on a short call this week. What does your Thursday look like?',
  'If you can share a little more on timeline and budget, I can come back with a concrete plan.',
  'I can put a scoped proposal together. Would that be useful?',
  'Let me know which way you would rather go and I will take it from there.',
];

function pick<T>(list: readonly T[], seed: number, salt: number): T {
  return list[(seed + salt) % list.length] as T;
}

/**
 * Deterministic offline draft. Same prompt + same enquiry always produces the same text,
 * which is what lets the integration tests assert on real content instead of mocking.
 *
 * It varies with the system prompt as well as the enquiry, so that editing the prompt
 * visibly changes the output even with no key. That makes the whole review loop walkable
 * offline. It is not a language model and is never presented as one.
 */
export function createStubProvider(model: string = MODEL_ID): DraftProvider {
  return {
    name: 'stub',
    model,
    async draft(input: DraftInput): Promise<DraftResult> {
      const promptSeed = hash(input.systemPrompt);
      const enquirySeed = hash(`${input.subject}\n${input.body}`);
      const seed = (promptSeed ^ enquirySeed) >>> 0;

      const firstLine = input.body.trim().split(/\r?\n/)[0] ?? '';
      const echo = firstLine.length > 120 ? `${firstLine.slice(0, 117)}...` : firstLine;

      const text = [
        STUB_MARKER,
        '',
        'Hi,',
        '',
        pick(OPENERS, seed, 0),
        '',
        `On "${input.subject.trim()}" - ${echo}`,
        '',
        pick(MIDDLES, seed, 1),
        '',
        pick(CLOSERS, seed, 2),
        '',
        'Best,',
        'Aleem',
        '',
        `(stub fingerprint: prompt ${promptSeed.toString(16)} / enquiry ${enquirySeed.toString(16)})`,
      ].join('\n');

      return { text, inputTokens: null, outputTokens: null };
    },
  };
}

// --------------------------------------------------------------------------------------
// Selection
// --------------------------------------------------------------------------------------

export function selectProvider(apiKey: string | undefined, model: string): DraftProvider {
  const trimmed = (apiKey ?? '').trim();
  if (trimmed.length > 0) return createAnthropicProvider(trimmed, model);
  return createStubProvider(model);
}
