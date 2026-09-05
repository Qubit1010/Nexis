import { afterAll, beforeAll, describe, expect, it } from 'vitest';
import type { FastifyInstance, InjectOptions, LightMyRequestResponse } from 'fastify';
import { buildApp } from '../src/app.ts';

let app: FastifyInstance;
let cookie = '';

const goodLead = {
  name: 'Dana Reyes',
  email: 'dana@northwind.com',
  company: 'Northwind Trading',
  budget: 5,
  timeline: 5,
  needs: ['ai-automation', 'web-app'],
  message: 'We want to automate our intake and quoting process.',
};

const weakLead = {
  name: 'Sam Pool',
  email: 'sam@gmail.com',
  company: '',
  budget: 1,
  timeline: 1,
  needs: ['website'],
  message: 'Just looking around for now.',
};

type Inject = { method?: string; url: string; payload?: unknown; headers?: Record<string, string> };

// Deliberately mid-range: under the default rules this scores 18, far from both the 0 floor
// and the 100 ceiling, so a rule worth 40 points moves the score by exactly 40.
const midLead = {
  name: 'Mo Idris',
  email: 'mo@midrange.co',
  company: 'Midrange Ltd',
  budget: 3,
  timeline: 3,
  needs: ['website'],
  message: 'Just looking around at options for a rebuild.',
};

const submit = (body: object): Promise<LightMyRequestResponse> =>
  app.inject({ method: 'POST', url: '/api/leads', payload: body });
/** Every admin request carries the session cookie captured by the login test. */
const asAdmin = (opts: InjectOptions): Promise<LightMyRequestResponse> =>
  app.inject({ ...opts, headers: { ...opts.headers, cookie } });

const PASSWORD = 'test-password-123';

// The fixture password is passed in rather than read from the environment, so the suite
// behaves identically however vitest is invoked.
beforeAll(async () => {
  app = await buildApp({ dbPath: ':memory:', logger: false, adminPassword: PASSWORD });
  await app.ready();
});

afterAll(async () => {
  await app.close();
});

describe('public endpoints', () => {
  it('serves health and the form config without a session', async () => {
    expect((await app.inject({ url: '/api/health' })).statusCode).toBe(200);
    const res = await app.inject({ url: '/api/form-config' });
    expect(res.statusCode).toBe(200);
    const body = res.json();
    expect(body.budget).toHaveLength(5);
    expect(body.needs.length).toBeGreaterThan(0);
  });

  it('accepts a valid submission and returns only an id', async () => {
    const res = await submit(goodLead);
    expect(res.statusCode).toBe(201);
    const body = res.json();
    expect(body.id).toBeTypeOf('number');
    // The public form must never learn how the lead scored.
    expect(body).not.toHaveProperty('score');
    expect(body).not.toHaveProperty('band');
  });

  it('rejects a bad email with a per-field message', async () => {
    const res = await submit({ ...goodLead, email: 'not-an-email' });
    expect(res.statusCode).toBe(400);
    expect(res.json().fields).toHaveProperty('email');
  });

  it('rejects a budget value the form could never produce', async () => {
    const res = await submit({ ...goodLead, budget: 99 });
    expect(res.statusCode).toBe(400);
    expect(res.json().fields).toHaveProperty('budget');
  });

  it('rejects an unknown need value', async () => {
    const res = await submit({ ...goodLead, needs: ['crypto-rug-pull'] });
    expect(res.statusCode).toBe(400);
  });

  it('rejects an empty needs selection', async () => {
    const res = await submit({ ...goodLead, needs: [] });
    expect(res.statusCode).toBe(400);
    expect(res.json().fields).toHaveProperty('needs');
  });

  it('silently discards a honeypot submission', async () => {
    const res = await submit({ ...goodLead, website: 'http://spam.example' });
    expect(res.statusCode).toBe(201);
    expect(res.json().id).toBeNull();
  });
});

describe('auth', () => {
  it('refuses every admin route without a session', async () => {
    for (const url of ['/api/leads', '/api/rules', '/api/stats']) {
      expect((await app.inject({ url })).statusCode).toBe(401);
    }
    expect((await app.inject({ method: 'POST', url: '/api/rescore' })).statusCode).toBe(401);
    expect((await app.inject({ method: 'PATCH', url: '/api/leads/1', payload: { status: 'dead' } })).statusCode).toBe(401);
  });

  it('rejects the wrong password', async () => {
    const res = await app.inject({ method: 'POST', url: '/api/auth/login', payload: { password: 'wrong' } });
    expect(res.statusCode).toBe(401);
    expect(res.cookies.find((c) => c.name === 'li_session')).toBeUndefined();
  });

  it('rejects a forged session cookie', async () => {
    const forged = 'li_session=' + encodeURIComponent(JSON.stringify({ sub: 'admin', exp: Date.now() + 60000 }));
    const res = await app.inject({ url: '/api/leads', headers: { cookie: forged } });
    expect(res.statusCode).toBe(401);
  });

  it('issues an httpOnly session on the right password', async () => {
    const res = await app.inject({
      method: 'POST', url: '/api/auth/login', payload: { password: PASSWORD },
    });
    expect(res.statusCode).toBe(200);
    const session = res.cookies.find((c) => c.name === 'li_session');
    expect(session).toBeDefined();
    expect(session!.httpOnly).toBe(true);
    expect(session!.sameSite?.toLowerCase()).toBe('lax');
    cookie = `li_session=${session!.value}`;
    expect((await asAdmin({ url: '/api/auth/me' })).json().authed).toBe(true);
  });
});

describe('scoring through the whole stack', () => {
  it('scores a strong lead above a weak one under the default rules', async () => {
    await submit(weakLead);
    const res = await asAdmin({ url: '/api/leads' });
    expect(res.statusCode).toBe(200);
    const leads = res.json().leads as { name: string; score: number; band: string }[];
    const strong = leads.find((l) => l.name === 'Dana Reyes')!;
    const weak = leads.find((l) => l.name === 'Sam Pool')!;
    expect(strong.score).toBeGreaterThan(weak.score);
    expect(strong.band).toBe('hot');
    // Default sort is score descending.
    expect(leads[0]!.score).toBeGreaterThanOrEqual(leads[leads.length - 1]!.score);
  });

  it('stores a breakdown explaining the score', async () => {
    const leads = (await asAdmin({ url: '/api/leads' })).json().leads;
    const strong = leads.find((l: { name: string }) => l.name === 'Dana Reyes');
    const detail = (await asAdmin({ url: `/api/leads/${strong.id}` })).json().lead;
    expect(detail.score_breakdown.length).toBeGreaterThan(0);
    const matchedPoints = detail.score_breakdown
      .filter((b: { matched: boolean }) => b.matched)
      .reduce((sum: number, b: { points: number }) => sum + b.points, 0);
    expect(Math.max(0, Math.min(100, matchedPoints))).toBe(detail.score);
  });
});

describe('triage', () => {
  it('moves a lead through the statuses and saves notes', async () => {
    const leads = (await asAdmin({ url: '/api/leads' })).json().leads;
    const id = leads[0].id;
    for (const status of ['contacted', 'qualified', 'dead']) {
      const res = await asAdmin({ method: 'PATCH', url: `/api/leads/${id}`, payload: { status } });
      expect(res.statusCode).toBe(200);
      expect(res.json().lead.status).toBe(status);
    }
    const withNote = await asAdmin({ method: 'PATCH', url: `/api/leads/${id}`, payload: { notes: 'Called, left voicemail.' } });
    expect(withNote.json().lead.notes).toBe('Called, left voicemail.');
    expect(withNote.json().lead.status).toBe('dead');
  });

  it('rejects a status that is not in the allowed set', async () => {
    const leads = (await asAdmin({ url: '/api/leads' })).json().leads;
    const res = await asAdmin({ method: 'PATCH', url: `/api/leads/${leads[0].id}`, payload: { status: 'awesome' } });
    expect(res.statusCode).toBe(400);
  });

  it('404s on a lead that does not exist', async () => {
    expect((await asAdmin({ url: '/api/leads/999999' })).statusCode).toBe(404);
  });

  it('filters by status and searches across fields', async () => {
    const dead = (await asAdmin({ url: '/api/leads?status=dead' })).json().leads;
    expect(dead.every((l: { status: string }) => l.status === 'dead')).toBe(true);
    const found = (await asAdmin({ url: '/api/leads?q=northwind' })).json().leads;
    expect(found.length).toBeGreaterThan(0);
  });

  it('refuses an injected sort column instead of interpolating it', async () => {
    const res = await asAdmin({ url: '/api/leads?sort=score;DROP%20TABLE%20leads--' });
    expect(res.statusCode).toBe(400);
    // Prove the table survived.
    expect((await asAdmin({ url: '/api/leads' })).statusCode).toBe(200);
  });

  it('returns counts by status and band', async () => {
    const s = (await asAdmin({ url: '/api/stats' })).json();
    expect(s.total).toBeGreaterThan(0);
    expect(s).toHaveProperty('hot');
    expect(s).toHaveProperty('qualified');
  });
});

describe('rules', () => {
  it('ships a seeded default rule set', async () => {
    const body = (await asAdmin({ url: '/api/rules' })).json();
    expect(body.rules.length).toBeGreaterThan(5);
    expect(body.settings).toMatchObject({ hot_min: 60, warm_min: 30 });
  });

  it('creates a rule and rescores existing leads with it', async () => {
    await submit(midLead);
    const before = (await asAdmin({ url: '/api/leads?q=Mo%20Idris' })).json().leads[0];
    expect(before.score).toBeGreaterThan(0);
    expect(before.score).toBeLessThan(60);

    const created = await asAdmin({
      method: 'POST',
      url: '/api/rules',
      payload: { label: 'Mentions looking around', field: 'message', op: 'contains', value: 'looking around', points: 40, enabled: true, sort: 500 },
    });
    expect(created.statusCode).toBe(201);

    const rescore = await asAdmin({ method: 'POST', url: '/api/rescore' });
    expect(rescore.statusCode).toBe(200);
    expect(rescore.json().rescored).toBeGreaterThan(0);

    const after = (await asAdmin({ url: '/api/leads?q=Mo%20Idris' })).json().leads[0];
    expect(after.score).toBe(before.score + 40);
  });

  it('rejects an operator that cannot apply to the field', async () => {
    const res = await asAdmin({
      method: 'POST',
      url: '/api/rules',
      payload: { label: 'nonsense', field: 'budget', op: 'contains', value: 'x', points: 5 },
    });
    expect(res.statusCode).toBe(400);
    expect(res.json().fields).toHaveProperty('op');
  });

  it('rejects an illegal field/op pair introduced by a partial patch', async () => {
    const rules = (await asAdmin({ url: '/api/rules' })).json().rules;
    const budgetRule = rules.find((r: { field: string }) => r.field === 'budget');
    const res = await asAdmin({
      method: 'PATCH', url: `/api/rules/${budgetRule.id}`, payload: { op: 'contains' },
    });
    expect(res.statusCode).toBe(400);
  });

  it('rejects points outside the allowed range', async () => {
    const res = await asAdmin({
      method: 'POST', url: '/api/rules',
      payload: { label: 'too big', field: 'budget', op: 'gte', value: '1', points: 9999 },
    });
    expect(res.statusCode).toBe(400);
  });

  it('disabling a rule removes its contribution after a rescore', async () => {
    const rules = (await asAdmin({ url: '/api/rules' })).json().rules;
    const target = rules.find((r: { label: string }) => r.label === 'Mentions looking around');
    const before = (await asAdmin({ url: '/api/leads?q=Mo%20Idris' })).json().leads[0];

    await asAdmin({ method: 'PATCH', url: `/api/rules/${target.id}`, payload: { enabled: false } });
    await asAdmin({ method: 'POST', url: '/api/rescore' });

    const after = (await asAdmin({ url: '/api/leads?q=Mo%20Idris' })).json().leads[0];
    expect(after.score).toBe(before.score - 40);
  });

  it('deletes a rule', async () => {
    const rules = (await asAdmin({ url: '/api/rules' })).json().rules;
    const target = rules.find((r: { label: string }) => r.label === 'Mentions looking around');
    expect((await asAdmin({ method: 'DELETE', url: `/api/rules/${target.id}` })).statusCode).toBe(200);
    expect((await asAdmin({ method: 'DELETE', url: `/api/rules/${target.id}` })).statusCode).toBe(404);
  });
});

describe('thresholds', () => {
  it('rejects a hot threshold at or below the warm threshold', async () => {
    const res = await asAdmin({ method: 'PATCH', url: '/api/settings', payload: { hot_min: 20, warm_min: 30 } });
    expect(res.statusCode).toBe(400);
  });

  it('re-bands leads when the thresholds move', async () => {
    await asAdmin({ method: 'PATCH', url: '/api/settings', payload: { hot_min: 99, warm_min: 98 } });
    await asAdmin({ method: 'POST', url: '/api/rescore' });
    const leads = (await asAdmin({ url: '/api/leads' })).json().leads;
    expect(leads.every((l: { band: string }) => l.band === 'cold')).toBe(true);

    await asAdmin({ method: 'PATCH', url: '/api/settings', payload: { hot_min: 60, warm_min: 30 } });
    await asAdmin({ method: 'POST', url: '/api/rescore' });
    const restored = (await asAdmin({ url: '/api/leads' })).json().leads;
    expect(restored.some((l: { band: string }) => l.band === 'hot')).toBe(true);
  });
});

describe('logout', () => {
  it('ends the session', async () => {
    const res = await asAdmin({ method: 'POST', url: '/api/auth/logout' });
    expect(res.statusCode).toBe(200);
    const cleared = res.cookies.find((c) => c.name === 'li_session');
    expect(cleared?.value).toBe('');
  });
});
