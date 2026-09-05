import type { DraftRequest, DraftResult, Provider } from './types.ts';

/**
 * Model choice: claude-sonnet-5.
 *
 * Drafting a client reply is tone-matching, not reasoning, so Opus 5 ($5/$25 per MTok) is
 * 2.5x the price for capability this task does not use. Haiku 4.5 ($1/$5) is half the
 * price, but this is client-facing copy where voice IS the product, so the step down is
 * not worth it.
 *
 * Model ID and prices read from https://platform.claude.com/docs/en/about-claude/pricing
 * and .../models/overview on 2026-09-01. Worth checking rather than recalling: the pricing
 * page carries a note that Sonnet 5's introductory $2/$10 became the standard price, and
 * that the scheduled rise to $3/$15 on 2026-09-01 will not happen.
 *
 * Per the models overview, every current Claude model ID is a pinned snapshot, including
 * the dateless ones from the 4.6 generation on, so 'claude-sonnet-5' is safe to hardcode.
 */
export const MODEL = 'claude-sonnet-5';

/** USD per million tokens. Source and date as above. */
export const PRICING = {
  'claude-sonnet-5': { inputPerMTok: 2.0, outputPerMTok: 10.0 },
} as const;

const API_URL = 'https://api.anthropic.com/v1/messages';
/** Latest anthropic-version, confirmed against the versioning docs on 2026-09-01. */
const API_VERSION = '2023-06-01';
const MAX_TOKENS = 1024;
const TIMEOUT_MS = 60_000;

export function costUsd(model: string, inputTokens: number, outputTokens: number): number | null {
  const p = PRICING[model as keyof typeof PRICING];
  if (!p) return null;
  return (inputTokens * p.inputPerMTok + outputTokens * p.outputPerMTok) / 1_000_000;
}

function userMessage(req: DraftRequest): string {
  // Delimited so an enquiry body containing instruction-shaped text is read as data.
  return [
    'Draft a reply to this inbound enquiry. Output only the reply body, no subject line and no commentary.',
    '',
    '<enquiry>',
    `<from>${req.sender ?? 'unknown'}</from>`,
    `<subject>${req.subject}</subject>`,
    '<body>',
    req.body,
    '</body>',
    '</enquiry>',
  ].join('\n');
}

export function anthropicProvider(apiKey: string): Provider {
  return {
    name: 'anthropic',
    model: MODEL,
    async draft(req: DraftRequest): Promise<DraftResult> {
      const started = performance.now();
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'x-api-key': apiKey,
          'anthropic-version': API_VERSION,
          'content-type': 'application/json',
        },
        body: JSON.stringify({
          model: MODEL,
          max_tokens: MAX_TOKENS,
          system: req.systemPrompt,
          messages: [{ role: 'user', content: userMessage(req) }],
          // Effort is nested under output_config, not top level. Verified against the
          // effort docs, which recommend "low" for latency-sensitive non-coding work.
          output_config: { effort: 'low' },
        }),
        signal: AbortSignal.timeout(TIMEOUT_MS),
      });

      if (!res.ok) {
        const detail = await res.text().catch(() => '');
        // Truncated, and the key is never in this string, so it is safe to surface.
        throw new Error(`Claude API ${res.status}: ${detail.slice(0, 400)}`);
      }

      const json = (await res.json()) as {
        content?: Array<{ type: string; text?: string }>;
        usage?: { input_tokens?: number; output_tokens?: number };
      };

      const text = (json.content ?? [])
        .filter((b) => b.type === 'text' && typeof b.text === 'string')
        .map((b) => b.text as string)
        .join('')
        .trim();

      if (!text) throw new Error('Claude API returned no text content');

      const inputTokens = json.usage?.input_tokens ?? null;
      const outputTokens = json.usage?.output_tokens ?? null;

      return {
        text,
        provider: 'anthropic',
        model: MODEL,
        inputTokens,
        outputTokens,
        costUsd:
          inputTokens !== null && outputTokens !== null
            ? costUsd(MODEL, inputTokens, outputTokens)
            : null,
        latencyMs: Math.round(performance.now() - started),
      };
    },
  };
}
