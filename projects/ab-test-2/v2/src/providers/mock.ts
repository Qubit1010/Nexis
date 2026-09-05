import type { DraftRequest, DraftResult, Provider } from './types.ts';

export const MOCK_MODEL = 'offline-mock-drafter-1';

/**
 * Deterministic offline drafter.
 *
 * This exists so the entire product — drafting, reviewing, scoring, benching, comparing —
 * runs and is testable with no API key. That imposes a requirement most mocks ignore: a
 * mock that returns a fixed string would make the measurement feature untestable, because
 * every prompt version would score identically and the scoreboard would have nothing to
 * show.
 *
 * So this reads directives out of the system prompt and changes its output accordingly.
 * Same inputs always give the same draft (seeded from a hash), which keeps tests stable,
 * but different prompt versions genuinely produce different drafts.
 */
function fnv1a(str: string): number {
  let h = 0x811c9dc5;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 0x01000193) >>> 0;
  }
  return h >>> 0;
}

function pick<T>(items: readonly T[], seed: number, salt: number): T {
  return items[(seed + salt * 2654435761) % items.length];
}

export type Directives = {
  brief: boolean;
  warm: boolean;
  askQuestion: boolean;
  mentionPricing: boolean;
  proposeCall: boolean;
  signOff: boolean;
};

/** Read the behavioural directives a system prompt is asking for. */
export function readDirectives(systemPrompt: string): Directives {
  const p = systemPrompt.toLowerCase();
  const has = (re: RegExp) => re.test(p);
  return {
    brief: has(/\b(brief|concise|short|terse|tight|succinct|no fluff)\b/),
    warm: has(/\b(warm|friendly|personable|human|approachable)\b/),
    askQuestion: has(/\b(question|discovery|qualify|qualifying|clarify)\b/),
    mentionPricing: has(/\b(pricing|price|budget|rate|rates|cost|investment)\b/),
    proposeCall: has(/\b(call|meeting|book|schedule|calendar)\b/),
    signOff: has(/\b(sign[- ]?off|signature|sign off|close with)\b/),
  };
}

/** Strip Re:/Fwd: noise and quote the subject back, the way a person mirrors a request. */
export function topicOf(subject: string): string {
  const cleaned = subject.replace(/^\s*((re|fwd|fw)\s*:\s*)+/i, '').trim();
  return cleaned.length > 0 ? cleaned : 'your enquiry';
}

function firstName(sender: string | null): string {
  if (!sender) return 'there';
  const n = sender.trim().split(/\s+/)[0];
  return n.length > 0 ? n : 'there';
}

const GREETINGS_WARM = ['Hi', 'Hey', 'Hello'] as const;
const GREETINGS_PLAIN = ['Hi', 'Hello'] as const;
const CLOSERS = ['Best', 'Thanks', 'Cheers'] as const;

export function mockDraft(req: DraftRequest): string {
  const d = readDirectives(req.systemPrompt);
  const seed = fnv1a(`${req.systemPrompt}\u0000${req.subject}\u0000${req.body}`);
  const name = firstName(req.sender);
  const topic = topicOf(req.subject);
  const greetings = d.warm ? GREETINGS_WARM : GREETINGS_PLAIN;

  const lines: string[] = [];
  lines.push(`${pick(greetings, seed, 1)} ${name},`);
  lines.push('');

  if (d.warm) {
    lines.push(`Thanks for reaching out about ${topic}. Good to hear from you.`);
  } else {
    lines.push(`Thanks for getting in touch about ${topic}.`);
  }

  lines.push('');
  lines.push(
    d.brief
      ? pick(
          [
            'This is the kind of work we take on, and it looks doable.',
            'Yes, this is in scope for us.',
            'Short answer: this is a fit.',
          ],
          seed,
          2,
        )
      : pick(
          [
            'This is squarely the kind of work we take on, and from what you have described there is a clear path through it.',
            'We have run projects shaped like this before, so I have a reasonable idea of what it would take.',
            'Having read through what you sent, this looks well within scope for us.',
          ],
          seed,
          2,
        ),
  );

  if (d.mentionPricing) {
    lines.push('');
    lines.push(
      d.brief
        ? 'Projects like this usually land in the mid four figures.'
        : 'To set expectations early: work at this shape usually lands in the mid four figures, though the exact number depends on scope and timeline.',
    );
  }

  if (d.askQuestion) {
    lines.push('');
    lines.push(
      pick(
        [
          'One thing before I scope it properly: what is driving the timeline on your side?',
          'What does success look like for you ninety days after this ships?',
          'What have you already tried here, and where did it fall down?',
        ],
        seed,
        3,
      ),
    );
  }

  if (d.proposeCall) {
    lines.push('');
    lines.push(
      d.brief
        ? 'Open to a short call this week?'
        : 'If it is useful, I can walk you through how I would approach it on a short call this week. Happy to work around your calendar.',
    );
  }

  lines.push('');
  lines.push(d.signOff ? `${pick(CLOSERS, seed, 4)},\nAleem` : pick(CLOSERS, seed, 4));

  return lines.join('\n').trim();
}

export function mockProvider(): Provider {
  return {
    name: 'mock',
    model: MOCK_MODEL,
    async draft(req: DraftRequest): Promise<DraftResult> {
      const started = performance.now();
      const text = mockDraft(req);
      return {
        text,
        provider: 'mock',
        model: MOCK_MODEL,
        // Never invent usage numbers. A mock has no real token cost, so it reports none.
        inputTokens: null,
        outputTokens: null,
        costUsd: null,
        latencyMs: Math.round(performance.now() - started),
      };
    },
  };
}
