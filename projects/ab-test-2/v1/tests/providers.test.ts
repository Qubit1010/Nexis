import { describe, expect, it } from 'vitest';

import { AppError } from '../server/errors.ts';
import type { AnthropicLike } from '../server/providers.ts';
import {
  STUB_MARKER,
  createStubProvider,
  draftWithClient,
  selectProvider,
} from '../server/providers.ts';

const input = {
  systemPrompt: 'Reply briefly and warmly.',
  subject: 'Booking system rebuild',
  body: 'Our booking flow is broken and we are losing appointments. What would you charge?',
};

describe('selectProvider', () => {
  it('chooses the stub when there is no key at all', () => {
    expect(selectProvider(undefined, 'claude-opus-5').name).toBe('stub');
  });

  it('chooses the stub when the key is blank or whitespace', () => {
    expect(selectProvider('', 'claude-opus-5').name).toBe('stub');
    expect(selectProvider('   ', 'claude-opus-5').name).toBe('stub');
  });

  it('chooses anthropic when a key is present', () => {
    expect(selectProvider('sk-ant-not-a-real-key', 'claude-opus-5').name).toBe('anthropic');
  });

  it('carries the configured model through either way', () => {
    expect(selectProvider(undefined, 'claude-opus-5').model).toBe('claude-opus-5');
    expect(selectProvider('sk-ant-x', 'claude-opus-5').model).toBe('claude-opus-5');
  });
});

describe('stub provider', () => {
  it('produces the same draft for the same prompt and enquiry', async () => {
    const provider = createStubProvider();
    const first = await provider.draft(input);
    const second = await provider.draft(input);
    expect(first.text).toBe(second.text);
  });

  it('marks itself so a stub draft cannot be mistaken for a real one', async () => {
    const result = await createStubProvider().draft(input);
    expect(result.text).toContain(STUB_MARKER);
  });

  it('changes when the prompt changes, so prompt edits are visible with no key', async () => {
    const provider = createStubProvider();
    const before = await provider.draft(input);
    const after = await provider.draft({ ...input, systemPrompt: 'Be terse. Ask about budget.' });
    expect(after.text).not.toBe(before.text);
  });

  it('changes when the enquiry changes', async () => {
    const provider = createStubProvider();
    const before = await provider.draft(input);
    const after = await provider.draft({ ...input, subject: 'Something else entirely' });
    expect(after.text).not.toBe(before.text);
  });

  it('reports no token usage, because nothing was actually spent', async () => {
    const result = await createStubProvider().draft(input);
    expect(result.inputTokens).toBeNull();
    expect(result.outputTokens).toBeNull();
  });
});

/**
 * These drive the real Anthropic response-handling code through a fake client.
 * They prove the parsing, the refusal branch, and the error mapping. They do NOT prove the
 * request is accepted by the live API, which has never been executed here.
 */
describe('anthropic response handling (fake client)', () => {
  function fakeClient(handler: (params: Record<string, unknown>) => unknown): AnthropicLike {
    return {
      messages: {
        create: async (params: Record<string, unknown>) => handler(params) as never,
      },
    };
  }

  it('joins the text blocks and reads usage', async () => {
    const client = fakeClient(() => ({
      content: [
        { type: 'thinking', thinking: 'ignored' },
        { type: 'text', text: 'Hi there,' },
        { type: 'text', text: 'Happy to help.' },
      ],
      stop_reason: 'end_turn',
      usage: { input_tokens: 120, output_tokens: 45 },
    }));

    const result = await draftWithClient(client, 'claude-opus-5', input);
    expect(result.text).toBe('Hi there,\nHappy to help.');
    expect(result.inputTokens).toBe(120);
    expect(result.outputTokens).toBe(45);
  });

  it('sends the request shape the claude-api skill documents for Opus 5', async () => {
    let seen: Record<string, unknown> = {};
    const client = fakeClient((params) => {
      seen = params;
      return { content: [{ type: 'text', text: 'ok' }], usage: {} };
    });

    await draftWithClient(client, 'claude-opus-5', input);

    expect(seen.model).toBe('claude-opus-5');
    expect(seen.system).toBe(input.systemPrompt);
    expect(seen.thinking).toEqual({ type: 'adaptive' });
    // budget_tokens is rejected with a 400 on this model family, so it must never appear.
    expect(seen).not.toHaveProperty('budget_tokens');
    // effort belongs inside output_config, not at the top level.
    expect(seen.output_config).toEqual({ effort: 'medium' });
    expect(seen).not.toHaveProperty('effort');
    // No assistant prefill: the only message is the user's.
    const messages = seen.messages as Array<{ role: string }>;
    expect(messages).toHaveLength(1);
    expect(messages[0]?.role).toBe('user');
  });

  it('surfaces a refusal as a provider error rather than an empty draft', async () => {
    const client = fakeClient(() => ({
      content: [],
      stop_reason: 'refusal',
      stop_details: { type: 'refusal', category: 'cyber' },
    }));

    await expect(draftWithClient(client, 'claude-opus-5', input)).rejects.toMatchObject({
      code: 'provider_error',
      status: 502,
    });
  });

  it('rejects an empty response instead of storing a blank draft', async () => {
    const client = fakeClient(() => ({ content: [], stop_reason: 'end_turn' }));
    await expect(draftWithClient(client, 'claude-opus-5', input)).rejects.toBeInstanceOf(AppError);
  });

  it('maps an SDK throw to a 502 rather than a 500', async () => {
    const client = fakeClient(() => {
      throw new Error('rate limited');
    });
    await expect(draftWithClient(client, 'claude-opus-5', input)).rejects.toMatchObject({
      code: 'provider_error',
      status: 502,
    });
  });

  it('tolerates a response with no usage block', async () => {
    const client = fakeClient(() => ({ content: [{ type: 'text', text: 'fine' }] }));
    const result = await draftWithClient(client, 'claude-opus-5', input);
    expect(result.inputTokens).toBeNull();
    expect(result.outputTokens).toBeNull();
  });
});
