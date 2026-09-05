import type { Server } from 'node:http';
import type { AddressInfo } from 'node:net';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import { buildApp } from '../server/app.ts';
import type { Db, Draft, Enquiry, PromptVersion } from '../server/db.ts';
import { openDb } from '../server/db.ts';
import { createStubProvider } from '../server/providers.ts';
import type { Scoreboard } from '../server/scoreboard.ts';

let db: Db;
let server: Server;
let base: string;

beforeEach(async () => {
  db = openDb(':memory:');
  const app = buildApp({ db, provider: createStubProvider(), hasApiKey: false });
  server = await new Promise<Server>((resolve) => {
    const listening = app.listen(0, () => resolve(listening));
  });
  base = `http://127.0.0.1:${(server.address() as AddressInfo).port}`;
});

afterEach(async () => {
  await new Promise<void>((resolve) => server.close(() => resolve()));
  db.close();
});

async function call<T>(
  path: string,
  init?: { method?: string; body?: unknown },
): Promise<{ status: number; body: T }> {
  const response = await fetch(`${base}${path}`, {
    method: init?.method ?? 'GET',
    headers: init?.body ? { 'content-type': 'application/json' } : undefined,
    body: init?.body ? JSON.stringify(init.body) : undefined,
  });
  const text = await response.text();
  return { status: response.status, body: (text ? JSON.parse(text) : null) as T };
}

async function newEnquiry(subject = 'Booking rebuild', body = 'Our booking flow is broken.') {
  const result = await call<Enquiry>('/api/enquiries', { method: 'POST', body: { subject, body } });
  return result.body;
}

describe('GET /api/health', () => {
  it('reports stub mode honestly when there is no key', async () => {
    const { status, body } = await call<{
      provider: string;
      hasApiKey: boolean;
      model: string;
      pricing: { inputPerMTok: number; outputPerMTok: number };
    }>('/api/health');

    expect(status).toBe(200);
    expect(body.provider).toBe('stub');
    expect(body.hasApiKey).toBe(false);
    expect(body.model).toBe('claude-opus-5');
    expect(body.pricing.inputPerMTok).toBe(5);
    expect(body.pricing.outputPerMTok).toBe(25);
  });
});

describe('enquiries', () => {
  it('creates and reads one back', async () => {
    const created = await newEnquiry('Website redesign', 'We need a new site by June.');
    expect(created.id).toBeGreaterThan(0);

    const { body } = await call<{ enquiry: Enquiry; drafts: Draft[] }>(
      `/api/enquiries/${created.id}`,
    );
    expect(body.enquiry.subject).toBe('Website redesign');
    expect(body.drafts).toEqual([]);
  });

  it('rejects an empty subject or body with a 400 in the contract error shape', async () => {
    const { status, body } = await call<{ error: { code: string; message: string } }>(
      '/api/enquiries',
      { method: 'POST', body: { subject: '', body: '' } },
    );
    expect(status).toBe(400);
    expect(body.error.code).toBe('validation_error');
  });

  it('404s an unknown enquiry rather than throwing a 500', async () => {
    const { status, body } = await call<{ error: { code: string } }>('/api/enquiries/9999');
    expect(status).toBe(404);
    expect(body.error.code).toBe('not_found');
  });

  it('404s a non-numeric id path as a validation error', async () => {
    const { status } = await call('/api/enquiries/not-a-number');
    expect(status).toBe(400);
  });

  it('summarises draft count and latest rating in the list', async () => {
    const enquiry = await newEnquiry();
    const draft = await call<Draft>(`/api/enquiries/${enquiry.id}/drafts`, { method: 'POST' });
    await call(`/api/drafts/${draft.body.id}`, { method: 'PATCH', body: { rating: 'good' } });

    const { body } = await call<Array<{ id: number; draftCount: number; latestRating: string }>>(
      '/api/enquiries',
    );
    expect(body[0]?.draftCount).toBe(1);
    expect(body[0]?.latestRating).toBe('good');
  });
});

describe('drafting', () => {
  it('generates a draft attributed to the active prompt version', async () => {
    const enquiry = await newEnquiry();
    const { status, body } = await call<Draft>(`/api/enquiries/${enquiry.id}/drafts`, {
      method: 'POST',
    });

    expect(status).toBe(201);
    expect(body.promptVersion).toBe(1);
    expect(body.provider).toBe('stub');
    expect(body.model).toBe('claude-opus-5');
    expect(body.generatedText.length).toBeGreaterThan(0);
    expect(body.rating).toBeNull();
    expect(body.editedText).toBeNull();
  });

  it('404s when drafting against an enquiry that does not exist', async () => {
    const { status } = await call('/api/enquiries/4242/drafts', { method: 'POST' });
    expect(status).toBe(404);
  });

  it('records an edit without ever overwriting what the model wrote', async () => {
    const enquiry = await newEnquiry();
    const draft = (await call<Draft>(`/api/enquiries/${enquiry.id}/drafts`, { method: 'POST' }))
      .body;
    const original = draft.generatedText;

    const { body: edited } = await call<Draft>(`/api/drafts/${draft.id}`, {
      method: 'PATCH',
      body: { editedText: 'Hi, thanks for reaching out. Short answer: yes. Aleem' },
    });

    // The invariant the edit-distance signal depends on.
    expect(edited.generatedText).toBe(original);
    expect(edited.editedText).toBe('Hi, thanks for reaching out. Short answer: yes. Aleem');
    expect(edited.editDistance).toBeGreaterThan(0);
    expect(edited.keepRatio).not.toBeNull();
  });

  it('measures a second edit against the original draft, not against the first edit', async () => {
    const enquiry = await newEnquiry();
    const draft = (await call<Draft>(`/api/enquiries/${enquiry.id}/drafts`, { method: 'POST' }))
      .body;

    const first = (
      await call<Draft>(`/api/drafts/${draft.id}`, {
        method: 'PATCH',
        body: { editedText: 'totally different text here' },
      })
    ).body;

    const second = (
      await call<Draft>(`/api/drafts/${draft.id}`, {
        method: 'PATCH',
        body: { editedText: draft.generatedText },
      })
    ).body;

    expect(first.editDistance).toBeGreaterThan(0);
    // Reverting to the original means zero distance from the original.
    expect(second.editDistance).toBe(0);
    expect(second.keepRatio).toBe(1);
  });

  it('rates, re-rates, and clears a rating', async () => {
    const enquiry = await newEnquiry();
    const draft = (await call<Draft>(`/api/enquiries/${enquiry.id}/drafts`, { method: 'POST' }))
      .body;

    const good = (
      await call<Draft>(`/api/drafts/${draft.id}`, { method: 'PATCH', body: { rating: 'good' } })
    ).body;
    expect(good.rating).toBe('good');
    expect(good.ratedAt).not.toBeNull();

    const bad = (
      await call<Draft>(`/api/drafts/${draft.id}`, { method: 'PATCH', body: { rating: 'bad' } })
    ).body;
    expect(bad.rating).toBe('bad');

    const cleared = (
      await call<Draft>(`/api/drafts/${draft.id}`, { method: 'PATCH', body: { rating: null } })
    ).body;
    expect(cleared.rating).toBeNull();
    expect(cleared.ratedAt).toBeNull();
  });

  it('rejects an empty patch body and an invalid rating', async () => {
    const enquiry = await newEnquiry();
    const draft = (await call<Draft>(`/api/enquiries/${enquiry.id}/drafts`, { method: 'POST' }))
      .body;

    expect((await call(`/api/drafts/${draft.id}`, { method: 'PATCH', body: {} })).status).toBe(400);
    expect(
      (await call(`/api/drafts/${draft.id}`, { method: 'PATCH', body: { rating: 'great' } })).status,
    ).toBe(400);
  });

  it('404s a patch against an unknown draft', async () => {
    const { status } = await call('/api/drafts/777', { method: 'PATCH', body: { rating: 'good' } });
    expect(status).toBe(404);
  });
});

describe('prompt versions', () => {
  it('seeds exactly one active starting version', async () => {
    const { body } = await call<PromptVersion[]>('/api/prompts');
    expect(body).toHaveLength(1);
    expect(body[0]?.version).toBe(1);
    expect(body[0]?.isActive).toBe(true);
  });

  it('saving a prompt creates a new version and activates it, leaving the old text intact', async () => {
    const before = (await call<PromptVersion[]>('/api/prompts')).body[0];

    const { status, body: created } = await call<PromptVersion>('/api/prompts', {
      method: 'POST',
      body: { systemPrompt: 'Be much shorter. Always ask about budget.', label: 'Shorter' },
    });

    expect(status).toBe(201);
    expect(created.version).toBe(2);
    expect(created.isActive).toBe(true);

    const all = (await call<PromptVersion[]>('/api/prompts')).body;
    expect(all).toHaveLength(2);
    const v1 = all.find((version) => version.version === 1);
    expect(v1?.systemPrompt).toBe(before?.systemPrompt);
    expect(v1?.isActive).toBe(false);
  });

  it('rejects an empty prompt', async () => {
    const { status } = await call('/api/prompts', {
      method: 'POST',
      body: { systemPrompt: '   ' },
    });
    expect(status).toBe(400);
  });

  it('can roll back to an earlier version', async () => {
    const v1 = (await call<PromptVersion[]>('/api/prompts')).body[0];
    await call('/api/prompts', { method: 'POST', body: { systemPrompt: 'Version two text' } });

    const { body: reactivated } = await call<PromptVersion>(`/api/prompts/${v1?.id}/activate`, {
      method: 'POST',
    });
    expect(reactivated.version).toBe(1);
    expect(reactivated.isActive).toBe(true);

    const all = (await call<PromptVersion[]>('/api/prompts')).body;
    expect(all.filter((version) => version.isActive)).toHaveLength(1);
  });

  it('404s activating a version that does not exist', async () => {
    const { status } = await call('/api/prompts/888/activate', { method: 'POST' });
    expect(status).toBe(404);
  });
});

describe('the full loop, end to end', () => {
  it('drafts under v1, changes the prompt, re-drafts under v2, and attributes each rating correctly', async () => {
    const enquiry = await newEnquiry();

    // Two good ratings under v1.
    for (let i = 0; i < 2; i += 1) {
      const draft = (await call<Draft>(`/api/enquiries/${enquiry.id}/drafts`, { method: 'POST' }))
        .body;
      expect(draft.promptVersion).toBe(1);
      await call(`/api/drafts/${draft.id}`, { method: 'PATCH', body: { rating: 'good' } });
    }

    // Change the prompt. This must not disturb v1's record.
    await call('/api/prompts', {
      method: 'POST',
      body: { systemPrompt: 'Be terse. Two sentences maximum.', label: 'Terse' },
    });

    // One bad rating under v2, on the same enquiry.
    const v2Draft = (await call<Draft>(`/api/enquiries/${enquiry.id}/drafts`, { method: 'POST' }))
      .body;
    expect(v2Draft.promptVersion).toBe(2);
    await call(`/api/drafts/${v2Draft.id}`, { method: 'PATCH', body: { rating: 'bad' } });

    const { body: board } = await call<Scoreboard>('/api/stats');

    const v1 = board.versions.find((version) => version.version === 1);
    const v2 = board.versions.find((version) => version.version === 2);

    expect(v1?.rated).toBe(2);
    expect(v1?.good).toBe(2);
    expect(v1?.goodRate).toBe(1);
    expect(v2?.rated).toBe(1);
    expect(v2?.bad).toBe(1);
    expect(v2?.goodRate).toBe(0);

    // And neither is treated as conclusive at this sample size.
    expect(v1?.enoughData).toBe(false);
    expect(v2?.enoughData).toBe(false);
    expect(v1?.wilsonLow).toBeLessThan(1);

    expect(board.totals).toMatchObject({ enquiries: 1, drafts: 3, rated: 3, versions: 2 });
  });

  it('a different prompt version produces different draft text for the same enquiry', async () => {
    const enquiry = await newEnquiry();
    const first = (await call<Draft>(`/api/enquiries/${enquiry.id}/drafts`, { method: 'POST' }))
      .body;

    await call('/api/prompts', {
      method: 'POST',
      body: { systemPrompt: 'A completely different instruction set.' },
    });

    const second = (await call<Draft>(`/api/enquiries/${enquiry.id}/drafts`, { method: 'POST' }))
      .body;

    expect(second.generatedText).not.toBe(first.generatedText);
    expect(second.promptVersion).not.toBe(first.promptVersion);
  });
});

describe('unknown endpoints', () => {
  it('returns the contract error shape, not an HTML page', async () => {
    const { status, body } = await call<{ error: { code: string } }>('/api/nope');
    expect(status).toBe(404);
    expect(body.error.code).toBe('not_found');
  });
});
