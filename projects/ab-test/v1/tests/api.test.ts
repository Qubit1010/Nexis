import { afterAll, beforeAll, beforeEach, describe, expect, it } from 'vitest';
import { GET as getLeads, POST as postLead } from '@/app/api/leads/route';
import { DELETE as deleteLead, PATCH as patchLead } from '@/app/api/leads/[id]/route';
import { GET as getRules, PUT as putRules } from '@/app/api/rules/route';
import { POST as postSession } from '@/app/api/session/route';
import { createSessionToken, SESSION_COOKIE } from '@/lib/auth';
import { resetRateLimits } from '@/lib/rate-limit';
import type { Lead, Rule, StatusCounts } from '@/types';
import { dropTempDb, useTempDb } from './helpers/test-db';

const BASE = 'http://localhost:3000';
let cookie = '';

beforeAll(async () => {
  process.env.ADMIN_PASSWORD = 'test-password';
  process.env.SESSION_SECRET = 'test-secret';
  useTempDb();
  cookie = SESSION_COOKIE + '=' + encodeURIComponent(await createSessionToken());
});

afterAll(() => {
  dropTempDb();
});

beforeEach(() => {
  resetRateLimits();
});

function submission(overrides: Record<string, unknown> = {}) {
  return {
    name: 'Dana Reyes',
    email: 'dana@acme.io',
    company: 'Acme',
    budget: 10000,
    timeline: 'asap',
    services: ['ai-automation'],
    needs: 'We want our lead intake automated end to end.',
    source: 'referral',
    ...overrides,
  };
}

function publicPost(body: unknown, ip = '10.0.0.1'): Request {
  return new Request(BASE + '/api/leads', {
    method: 'POST',
    headers: { 'content-type': 'application/json', 'x-forwarded-for': ip },
    body: JSON.stringify(body),
  });
}

function adminRequest(path: string, method = 'GET', body?: unknown): Request {
  return new Request(BASE + path, {
    method,
    headers: {
      'content-type': 'application/json',
      cookie,
      'x-forwarded-for': '10.0.0.9',
    },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
}

function anonRequest(path: string, method = 'GET', body?: unknown): Request {
  return new Request(BASE + path, {
    method,
    headers: { 'content-type': 'application/json' },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
}

async function listAll(): Promise<{ leads: Lead[]; counts: StatusCounts }> {
  const response = await getLeads(adminRequest('/api/leads'));
  return (await response.json()) as { leads: Lead[]; counts: StatusCounts };
}

/* ------------------------------------------------------------------ authz */

describe('authorization', () => {
  it('refuses every admin endpoint without a session', async () => {
    const attempts = [
      await getLeads(anonRequest('/api/leads')),
      await getRules(anonRequest('/api/rules')),
      await putRules(anonRequest('/api/rules', 'PUT', { rules: [], bands: { hot: 70, warm: 40 } })),
      await patchLead(anonRequest('/api/leads/x', 'PATCH', { status: 'dead' }), {
        params: Promise.resolve({ id: 'x' }),
      }),
      await deleteLead(anonRequest('/api/leads/x', 'DELETE'), {
        params: Promise.resolve({ id: 'x' }),
      }),
    ];

    for (const response of attempts) {
      expect(response.status).toBe(401);
      const body = (await response.json()) as { code: string; leads?: unknown };
      expect(body.code).toBe('unauthorized');
      expect(body.leads).toBeUndefined();
    }
  });

  it('refuses a forged session cookie', async () => {
    const forged = new Request(BASE + '/api/leads', {
      headers: { cookie: SESSION_COOKIE + '=' + (Date.now() + 100000) + '.notarealsignature' },
    });
    expect((await getLeads(forged)).status).toBe(401);
  });

  it('accepts a valid session cookie', async () => {
    expect((await getLeads(adminRequest('/api/leads'))).status).toBe(200);
  });
});

describe('POST /api/session', () => {
  it('sets a session cookie for the right password', async () => {
    const response = await postSession(
      publicPost({ password: 'test-password' }, '10.0.0.2'),
    );
    expect(response.status).toBe(200);
    expect(response.headers.get('set-cookie')).toContain(SESSION_COOKIE + '=');
    expect(response.headers.get('set-cookie')).toContain('HttpOnly');
  });

  it('rejects the wrong password without setting a cookie', async () => {
    const response = await postSession(publicPost({ password: 'nope' }, '10.0.0.3'));
    expect(response.status).toBe(401);
    expect(response.headers.get('set-cookie')).toBeNull();
  });

  it('rejects a missing password with a validation error', async () => {
    const response = await postSession(publicPost({}, '10.0.0.4'));
    expect(response.status).toBe(400);
    expect(((await response.json()) as { code: string }).code).toBe('validation_error');
  });
});

/* ------------------------------------------------- public intake boundary */

describe('POST /api/leads (public)', () => {
  it('accepts a valid submission and scores it with the seeded rules', async () => {
    const response = await postLead(publicPost(submission()));
    expect(response.status).toBe(201);

    const body = (await response.json()) as { ok: boolean; id: string; score?: number };
    expect(body.ok).toBe(true);
    expect(body.id).toMatch(/^[0-9a-f-]{36}$/);
    // The score is internal. Leaking it would expose the rule set to anyone probing.
    expect(body.score).toBeUndefined();

    const { leads } = await listAll();
    const created = leads.find((lead) => lead.id === body.id);
    expect(created).toBeDefined();
    // 10k budget (+35 and +20), asap (+20), ai-automation (+15), company (+8),
    // "automated" matches the automation keyword (+5) = 103, capped at 100.
    expect(created?.score).toBe(100);
    expect(created?.band).toBe('hot');
    expect(created?.status).toBe('new');
    expect(created?.breakdown.length).toBeGreaterThan(3);
  });

  it('scores a weak lead low and lands it in cold', async () => {
    const response = await postLead(
      publicPost(
        submission({
          name: 'Sam Doe',
          email: 'sam@gmail.com',
          company: '',
          budget: 0,
          timeline: 'exploring',
          services: ['website'],
          needs: 'Just looking around at what a small site might cost me.',
        }),
      ),
    );
    expect(response.status).toBe(201);

    const id = ((await response.json()) as { id: string }).id;
    const { leads } = await listAll();
    const created = leads.find((lead) => lead.id === id);
    expect(created?.score).toBe(0);
    expect(created?.band).toBe('cold');
  });

  it('rejects an invalid payload with per-field details', async () => {
    const response = await postLead(
      publicPost(submission({ email: 'not-an-email', needs: 'short', services: [] })),
    );
    expect(response.status).toBe(400);

    const body = (await response.json()) as {
      code: string;
      details: Record<string, string[]>;
    };
    expect(body.code).toBe('validation_error');
    expect(body.details.email).toBeDefined();
    expect(body.details.needs).toBeDefined();
    expect(body.details.services).toBeDefined();
  });

  it('rejects a body that is not JSON', async () => {
    const request = new Request(BASE + '/api/leads', {
      method: 'POST',
      headers: { 'content-type': 'application/json', 'x-forwarded-for': '10.0.0.5' },
      body: 'not json at all',
    });
    const response = await postLead(request);
    expect(response.status).toBe(400);
    expect(((await response.json()) as { code: string }).code).toBe('bad_request');
  });

  it('swallows a honeypot submission: fake 201, nothing written', async () => {
    const before = (await listAll()).leads.length;

    const response = await postLead(
      publicPost(submission({ name: 'Spam Bot', website: 'http://spam.example' })),
    );
    expect(response.status).toBe(201);

    const after = await listAll();
    expect(after.leads.length).toBe(before);
    expect(after.leads.some((lead) => lead.name === 'Spam Bot')).toBe(false);
  });

  it('rate limits a single IP after five submissions', async () => {
    const statuses: number[] = [];
    for (let attempt = 0; attempt < 6; attempt += 1) {
      const response = await postLead(publicPost(submission(), '203.0.113.7'));
      statuses.push(response.status);
    }
    expect(statuses.slice(0, 5)).toEqual([201, 201, 201, 201, 201]);
    expect(statuses[5]).toBe(429);
  });
});

/* ----------------------------------------------------------- triage loop */

describe('GET /api/leads (admin)', () => {
  it('returns leads sorted by score and a status tally', async () => {
    const { leads, counts } = await listAll();
    expect(leads.length).toBeGreaterThan(0);

    const scores = leads.map((lead) => lead.score);
    expect([...scores].sort((a, b) => b - a)).toEqual(scores);
    expect(counts.all).toBe(leads.length);
  });

  it('filters by status and searches across name, company and needs', async () => {
    const filtered = await getLeads(adminRequest('/api/leads?status=new&q=acme'));
    const body = (await filtered.json()) as { leads: Lead[] };
    expect(body.leads.length).toBeGreaterThan(0);
    expect(body.leads.every((lead) => lead.status === 'new')).toBe(true);
    expect(
      body.leads.every((lead) =>
        (lead.name + lead.company + lead.email + lead.needs).toLowerCase().includes('acme'),
      ),
    ).toBe(true);
  });

  it('ignores a junk sort key instead of failing or injecting SQL', async () => {
    const response = await getLeads(
      adminRequest('/api/leads?sort=name);DROP TABLE leads;--&order=sideways'),
    );
    expect(response.status).toBe(200);
    expect(((await response.json()) as { leads: Lead[] }).leads.length).toBeGreaterThan(0);
  });
});

describe('PATCH and DELETE /api/leads/:id', () => {
  it('moves a lead through the triage states and keeps counts in step', async () => {
    const id = (await listAll()).leads[0]?.id as string;

    for (const status of ['contacted', 'qualified', 'dead'] as const) {
      const response = await patchLead(
        adminRequest('/api/leads/' + id, 'PATCH', { status }),
        { params: Promise.resolve({ id }) },
      );
      expect(response.status).toBe(200);
      expect(((await response.json()) as { lead: Lead }).lead.status).toBe(status);
    }

    const { leads, counts } = await listAll();
    expect(leads.find((lead) => lead.id === id)?.status).toBe('dead');
    expect(counts.dead).toBe(leads.filter((lead) => lead.status === 'dead').length);
  });

  it('saves a note without touching the status', async () => {
    const lead = (await listAll()).leads[0] as Lead;
    const response = await patchLead(
      adminRequest('/api/leads/' + lead.id, 'PATCH', { notes: 'Called, wants a proposal.' }),
      { params: Promise.resolve({ id: lead.id }) },
    );

    const body = (await response.json()) as { lead: Lead };
    expect(body.lead.notes).toBe('Called, wants a proposal.');
    expect(body.lead.status).toBe(lead.status);
  });

  it('rejects an unknown status and an empty patch', async () => {
    const id = (await listAll()).leads[0]?.id as string;
    const context = { params: Promise.resolve({ id }) };

    const badStatus = await patchLead(
      adminRequest('/api/leads/' + id, 'PATCH', { status: 'archived' }),
      context,
    );
    expect(badStatus.status).toBe(400);

    const empty = await patchLead(adminRequest('/api/leads/' + id, 'PATCH', {}), context);
    expect(empty.status).toBe(400);
  });

  it('returns 404 for an id that does not exist', async () => {
    const context = { params: Promise.resolve({ id: 'no-such-lead' }) };
    const patched = await patchLead(
      adminRequest('/api/leads/no-such-lead', 'PATCH', { status: 'dead' }),
      context,
    );
    expect(patched.status).toBe(404);

    const removed = await deleteLead(
      adminRequest('/api/leads/no-such-lead', 'DELETE'),
      context,
    );
    expect(removed.status).toBe(404);
  });

  it('deletes a lead and drops it from the list', async () => {
    const before = await listAll();
    const id = before.leads[before.leads.length - 1]?.id as string;

    const response = await deleteLead(adminRequest('/api/leads/' + id, 'DELETE'), {
      params: Promise.resolve({ id }),
    });
    expect(response.status).toBe(200);

    const after = await listAll();
    expect(after.leads.some((lead) => lead.id === id)).toBe(false);
    expect(after.counts.all).toBe(before.counts.all - 1);
  });
});

/* -------------------------------------------------- rules and rescoring */

describe('rules', () => {
  it('serves the seeded rule set and bands', async () => {
    const response = await getRules(adminRequest('/api/rules'));
    expect(response.status).toBe(200);

    const body = (await response.json()) as { rules: Rule[]; bands: { hot: number; warm: number } };
    expect(body.rules.length).toBeGreaterThan(5);
    expect(body.bands).toEqual({ hot: 70, warm: 40 });
    expect(body.rules[0]?.position).toBe(0);
  });

  it('rescores every existing lead when the rule set changes', async () => {
    const before = await listAll();
    expect(before.leads.some((lead) => lead.score > 0)).toBe(true);

    // Replace everything with one rule that no lead can satisfy.
    const response = await putRules(
      adminRequest('/api/rules', 'PUT', {
        rules: [
          {
            label: 'Impossible budget',
            field: 'budget',
            operator: 'gte',
            value: 99_000_000,
            points: 50,
            enabled: true,
          },
        ],
        bands: { hot: 70, warm: 40 },
      }),
    );
    expect(response.status).toBe(200);

    const body = (await response.json()) as { rescored: number; rules: Rule[] };
    expect(body.rules).toHaveLength(1);
    expect(body.rescored).toBe(before.leads.length);

    const after = await listAll();
    expect(after.leads.every((lead) => lead.score === 0)).toBe(true);
    expect(after.leads.every((lead) => lead.band === 'cold')).toBe(true);
    expect(after.leads.every((lead) => lead.breakdown.length === 0)).toBe(true);
  });

  it('applies a new rule to every stored lead, not just new ones', async () => {
    await putRules(
      adminRequest('/api/rules', 'PUT', {
        rules: [
          {
            label: 'Everyone gets fifty',
            field: 'email',
            operator: 'present',
            value: '',
            points: 50,
            enabled: true,
          },
        ],
        bands: { hot: 45, warm: 20 },
      }),
    );

    const { leads } = await listAll();
    expect(leads.every((lead) => lead.score === 50)).toBe(true);
    expect(leads.every((lead) => lead.band === 'hot')).toBe(true);
    expect(leads.every((lead) => lead.breakdown[0]?.label === 'Everyone gets fifty')).toBe(true);
  });

  it('honours a disabled rule on save', async () => {
    await putRules(
      adminRequest('/api/rules', 'PUT', {
        rules: [
          {
            label: 'Switched off',
            field: 'email',
            operator: 'present',
            value: '',
            points: 90,
            enabled: false,
          },
        ],
        bands: { hot: 70, warm: 40 },
      }),
    );

    const { leads } = await listAll();
    expect(leads.every((lead) => lead.score === 0)).toBe(true);
  });

  it('rejects a rule set where hot is not above warm, leaving the saved rules intact', async () => {
    const before = (await getRules(adminRequest('/api/rules'))).json();

    const response = await putRules(
      adminRequest('/api/rules', 'PUT', {
        rules: [],
        bands: { hot: 20, warm: 60 },
      }),
    );
    expect(response.status).toBe(400);
    expect(((await response.json()) as { code: string }).code).toBe('validation_error');

    const after = (await getRules(adminRequest('/api/rules'))).json();
    expect((await after).rules).toEqual((await before).rules);
  });

  it('rejects a malformed rule (gte without a number)', async () => {
    const response = await putRules(
      adminRequest('/api/rules', 'PUT', {
        rules: [
          {
            label: 'Nonsense',
            field: 'budget',
            operator: 'gte',
            value: ['not', 'a', 'number'],
            points: 10,
            enabled: true,
          },
        ],
        bands: { hot: 70, warm: 40 },
      }),
    );
    expect(response.status).toBe(400);
  });
});

/* ------------------------------------------------------------ full loop */

describe('the core loop end to end', () => {
  it('submits, scores, triages and rescores a single lead', async () => {
    // A rule set with one clear signal.
    await putRules(
      adminRequest('/api/rules', 'PUT', {
        rules: [
          {
            label: 'Ready now',
            field: 'timeline',
            operator: 'eq',
            value: 'asap',
            points: 80,
            enabled: true,
          },
        ],
        bands: { hot: 70, warm: 40 },
      }),
    );

    const created = await postLead(
      publicPost(
        submission({ name: 'Loop Tester', email: 'loop@corp.io', timeline: 'asap' }),
        '198.51.100.4',
      ),
    );
    const id = ((await created.json()) as { id: string }).id;

    const findMe = async () =>
      (await listAll()).leads.find((lead) => lead.id === id) as Lead;

    expect((await findMe()).score).toBe(80);
    expect((await findMe()).band).toBe('hot');
    expect((await findMe()).status).toBe('new');

    await patchLead(adminRequest('/api/leads/' + id, 'PATCH', { status: 'qualified' }), {
      params: Promise.resolve({ id }),
    });
    expect((await findMe()).status).toBe('qualified');

    // Turn the signal off; the stored lead must follow, and keep its status.
    await putRules(
      adminRequest('/api/rules', 'PUT', {
        rules: [
          {
            label: 'Ready now',
            field: 'timeline',
            operator: 'eq',
            value: 'asap',
            points: 10,
            enabled: true,
          },
        ],
        bands: { hot: 70, warm: 40 },
      }),
    );

    const rescored = await findMe();
    expect(rescored.score).toBe(10);
    expect(rescored.band).toBe('cold');
    expect(rescored.status).toBe('qualified');
    expect(rescored.breakdown).toEqual([
      { ruleId: expect.any(String), label: 'Ready now', points: 10 },
    ]);
  });
});
