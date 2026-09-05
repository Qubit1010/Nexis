/**
 * Model identity and per-token pricing, kept as data so the app can show a real cost
 * per draft instead of the number living only in a document.
 *
 * PROVENANCE — read this before changing anything here.
 * Both the model ID and the two prices were taken from the `claude-api` skill's
 * "Current Models" table, which is marked `cached: 2026-06-24`. That is a cached table
 * shipped with the skill, not a live pricing lookup. Nothing here was written from memory.
 * The skill's standing instruction is to use `claude-opus-5` unless the user names another
 * model, and never to downgrade for cost on the user's behalf.
 *
 * To re-verify live: https://claude.com/pricing (or the Pricing row of the skill's
 * shared/live-sources.md).
 */

export const MODEL_ID = 'claude-opus-5';

export const PRICING = {
  model: MODEL_ID,
  inputPerMTok: 5.0,
  outputPerMTok: 25.0,
  source: 'claude-api skill, "Current Models" table, cached 2026-06-24',
} as const;

const PER_MILLION = 1_000_000;

/**
 * Cost of one draft in USD, or null when token usage is unknown.
 * The stub provider reports no usage, so its drafts cost nothing and say so.
 */
export function estimateCostUsd(
  inputTokens: number | null | undefined,
  outputTokens: number | null | undefined,
): number | null {
  if (inputTokens == null && outputTokens == null) return null;
  const input = ((inputTokens ?? 0) / PER_MILLION) * PRICING.inputPerMTok;
  const output = ((outputTokens ?? 0) / PER_MILLION) * PRICING.outputPerMTok;
  return input + output;
}
