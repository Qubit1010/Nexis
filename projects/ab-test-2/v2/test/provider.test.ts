import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { mockDraft, mockProvider, readDirectives, topicOf } from '../src/providers/mock.ts';
import { MODEL, PRICING, costUsd } from '../src/providers/anthropic.ts';
import { hasApiKey, selectProvider } from '../src/providers/index.ts';

const ENQUIRY = {
  subject: 'Website redesign enquiry',
  body: 'Our marketing site is four years old and converts badly. What would a rebuild cost?',
  sender: 'Dana Whitfield',
};

describe('mock drafter', () => {
  test('is deterministic: same inputs give byte-identical output', () => {
    const req = { ...ENQUIRY, systemPrompt: 'Be brief and warm.' };
    assert.equal(mockDraft(req), mockDraft(req));
  });

  test('is prompt-sensitive, which is what makes the scoreboard testable offline', () => {
    const a = mockDraft({ ...ENQUIRY, systemPrompt: 'Be brief.' });
    const b = mockDraft({ ...ENQUIRY, systemPrompt: 'Be warm, ask a discovery question, propose a call.' });
    assert.notEqual(a, b);
  });

  test('honours the brevity directive', () => {
    const brief = mockDraft({ ...ENQUIRY, systemPrompt: 'Be concise.' });
    const full = mockDraft({ ...ENQUIRY, systemPrompt: 'Reply warmly and propose a call.' });
    assert.ok(brief.length < full.length, 'a brief prompt should produce a shorter draft');
  });

  test('asks a question only when the prompt asks for one', () => {
    assert.ok(!mockDraft({ ...ENQUIRY, systemPrompt: 'Be brief.' }).includes('?'));
    assert.ok(mockDraft({ ...ENQUIRY, systemPrompt: 'Ask one discovery question.' }).includes('?'));
  });

  test('addresses the sender by first name', () => {
    assert.ok(mockDraft({ ...ENQUIRY, systemPrompt: 'Be warm.' }).startsWith('Hi Dana') ||
      mockDraft({ ...ENQUIRY, systemPrompt: 'Be warm.' }).startsWith('Hey Dana') ||
      mockDraft({ ...ENQUIRY, systemPrompt: 'Be warm.' }).startsWith('Hello Dana'));
  });

  test('falls back gracefully with no sender', () => {
    const out = mockDraft({ ...ENQUIRY, sender: null, systemPrompt: 'Be brief.' });
    assert.ok(out.includes('there,'));
  });

  test('never reports invented token counts or cost', async () => {
    const result = await mockProvider().draft({ ...ENQUIRY, systemPrompt: 'Be brief.' });
    assert.equal(result.inputTokens, null);
    assert.equal(result.outputTokens, null);
    assert.equal(result.costUsd, null);
    assert.equal(result.provider, 'mock');
  });
});

describe('readDirectives', () => {
  test('reads each directive out of prose', () => {
    const d = readDirectives('Keep it short. Be warm. Ask a qualifying question. Mention pricing. Suggest a call. Close with a sign-off.');
    assert.deepEqual(d, {
      brief: true,
      warm: true,
      askQuestion: true,
      mentionPricing: true,
      proposeCall: true,
      signOff: true,
    });
  });

  test('an unrelated prompt sets nothing', () => {
    const d = readDirectives('Reply in the voice of the founder.');
    assert.equal(Object.values(d).some(Boolean), false);
  });
});

describe('topicOf', () => {
  test('strips reply and forward prefixes, including stacked ones', () => {
    assert.equal(topicOf('Re: Fwd: Re: Website redesign'), 'Website redesign');
    assert.equal(topicOf('FW: Pricing'), 'Pricing');
  });

  test('falls back when the subject is empty', () => {
    assert.equal(topicOf('   '), 'your enquiry');
    assert.equal(topicOf('Re:'), 'your enquiry');
  });
});

describe('provider selection', () => {
  test('no key means the offline drafter, so the app runs unconfigured', () => {
    assert.equal(selectProvider({}).name, 'mock');
    assert.equal(selectProvider({ ANTHROPIC_API_KEY: '' }).name, 'mock');
    assert.equal(selectProvider({ ANTHROPIC_API_KEY: '   ' }).name, 'mock');
    assert.equal(hasApiKey({}), false);
  });

  test('a key selects live Claude', () => {
    assert.equal(selectProvider({ ANTHROPIC_API_KEY: 'sk-ant-test' }).name, 'anthropic');
    assert.equal(hasApiKey({ ANTHROPIC_API_KEY: 'sk-ant-test' }), true);
  });

  test('the force-mock switch overrides a real key, so tests can never bill', () => {
    const env = { ANTHROPIC_API_KEY: 'sk-ant-test', REPLY_DRAFTER_FORCE_MOCK: '1' };
    assert.equal(selectProvider(env).name, 'mock');
    assert.equal(hasApiKey(env), false);
  });
});

describe('pricing', () => {
  test('the model id is the one the code actually sends', () => {
    assert.equal(MODEL, 'claude-sonnet-5');
    assert.ok(PRICING[MODEL], 'the selected model must have a price entry');
  });

  test('prices match what the docs listed on 2026-09-01', () => {
    assert.equal(PRICING['claude-sonnet-5'].inputPerMTok, 2.0);
    assert.equal(PRICING['claude-sonnet-5'].outputPerMTok, 10.0);
  });

  test('cost is computed per million tokens', () => {
    // 1M in + 1M out = $2 + $10.
    assert.equal(costUsd('claude-sonnet-5', 1_000_000, 1_000_000), 12);
    // A realistic draft: 800 in, 300 out.
    assert.ok(Math.abs(costUsd('claude-sonnet-5', 800, 300)! - 0.0046) < 1e-9);
  });

  test('an unknown model returns null rather than guessing a price', () => {
    assert.equal(costUsd('some-other-model', 1000, 1000), null);
  });
});
