import { test, describe, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import type { DatabaseSync } from 'node:sqlite';
import { openDb } from '../src/db.ts';
import * as svc from '../src/service.ts';
import { mockProvider } from '../src/providers/mock.ts';
import { seedIfEmpty, STARTER_PROMPT } from '../src/seed.ts';

const provider = mockProvider();

function fresh(): DatabaseSync {
  const db = openDb(':memory:');
  svc.createPrompt(db, { label: 'v1', system_prompt: 'Be brief.', activate: true });
  return db;
}

describe('prompt versions', () => {
  let db: DatabaseSync;
  beforeEach(() => { db = fresh(); });

  test('saving creates a new version rather than mutating the old one', () => {
    const first = svc.listPrompts(db)[0];
    svc.createPrompt(db, { label: 'v2', system_prompt: 'Be warm and ask a question.' });

    const all = svc.listPrompts(db);
    assert.equal(all.length, 2);
    assert.equal(all[0].system_prompt, first.system_prompt, 'v1 text must be untouched');
  });

  test('only one version is active at a time', () => {
    const v2 = svc.createPrompt(db, { label: 'v2', system_prompt: 'Another.' });
    const active = svc.listPrompts(db).filter((p) => p.is_active === 1);
    assert.equal(active.length, 1);
    assert.equal(active[0].id, v2.id);
  });

  test('activating an old version deactivates the current one', () => {
    const v1 = svc.listPrompts(db)[0];
    svc.createPrompt(db, { label: 'v2', system_prompt: 'Another.' });
    svc.activatePrompt(db, v1.id);
    assert.equal(svc.getActivePrompt(db)!.id, v1.id);
    assert.equal(svc.listPrompts(db).filter((p) => p.is_active === 1).length, 1);
  });

  test('activating a version that does not exist returns null', () => {
    assert.equal(svc.activatePrompt(db, 9999), null);
  });

  test('activate:false saves without switching the active version', () => {
    const before = svc.getActivePrompt(db)!.id;
    svc.createPrompt(db, { label: 'draft idea', system_prompt: 'Untested.', activate: false });
    assert.equal(svc.getActivePrompt(db)!.id, before);
  });
});

describe('drafting', () => {
  let db: DatabaseSync;
  beforeEach(() => { db = fresh(); });

  test('a draft records which prompt version produced it', async () => {
    const e = svc.createEnquiry(db, { subject: 'Hello', body: 'Do you build dashboards?', sender: 'Ann' });
    const d = await svc.generateDraft(db, provider, { enquiryId: e.id });
    assert.equal(d.prompt_version_id, svc.getActivePrompt(db)!.id);
    assert.equal(d.provider, 'mock');
    assert.ok(d.text.length > 0);
  });

  test('drafting against an explicit version overrides the active one', async () => {
    const v2 = svc.createPrompt(db, { label: 'v2', system_prompt: 'Warm, ask a question.' });
    const v1 = svc.listPrompts(db)[0];
    const e = svc.createEnquiry(db, { subject: 'Hello', body: 'Hi', sender: 'Ann' });

    const d = await svc.generateDraft(db, provider, { enquiryId: e.id, promptVersionId: v1.id });
    assert.equal(d.prompt_version_id, v1.id);
    assert.notEqual(d.prompt_version_id, v2.id);
  });

  test('unknown enquiry and unknown version both raise NotFound', async () => {
    await assert.rejects(() => svc.generateDraft(db, provider, { enquiryId: 999 }), svc.NotFound);
    const e = svc.createEnquiry(db, { subject: 'x', body: 'y' });
    await assert.rejects(
      () => svc.generateDraft(db, provider, { enquiryId: e.id, promptVersionId: 999 }),
      svc.NotFound,
    );
  });
});

describe('reviews', () => {
  let db: DatabaseSync;
  beforeEach(() => { db = fresh(); });

  async function aDraft() {
    const e = svc.createEnquiry(db, { subject: 'Hello', body: 'Do you build dashboards?', sender: 'Ann' });
    return svc.generateDraft(db, provider, { enquiryId: e.id });
  }

  test('keeping the draft verbatim scores an edit ratio of 0', async () => {
    const d = await aDraft();
    const r = svc.saveReview(db, { draftId: d.id, verdict: 'good', finalText: d.text });
    assert.equal(r.edit_ratio, 0);
  });

  test('the edit ratio is computed server side, not trusted from the caller', async () => {
    const d = await aDraft();
    const r = svc.saveReview(db, { draftId: d.id, verdict: 'good', finalText: 'completely different text entirely' });
    assert.ok(r.edit_ratio > 0.5, `expected a large edit ratio, got ${r.edit_ratio}`);
  });

  test('re-rating overwrites instead of double counting', async () => {
    const d = await aDraft();
    svc.saveReview(db, { draftId: d.id, verdict: 'bad', finalText: 'nope' });
    svc.saveReview(db, { draftId: d.id, verdict: 'good', finalText: d.text });

    const board = svc.scoreboard(db);
    const row = board.find((v) => v.prompt_version_id === d.prompt_version_id)!;
    assert.equal(row.reviewed, 1, 'one draft must contribute exactly one review');
    assert.equal(row.good, 1);
    assert.equal(row.bad, 0);
  });

  test('reviewing a draft that does not exist raises NotFound', () => {
    assert.throws(() => svc.saveReview(db, { draftId: 999, verdict: 'good', finalText: 'x' }), svc.NotFound);
  });
});

describe('scoreboard', () => {
  let db: DatabaseSync;
  beforeEach(() => { db = fresh(); });

  test('an unrated version reports null approval, not zero', async () => {
    const e = svc.createEnquiry(db, { subject: 'Hello', body: 'Hi' });
    await svc.generateDraft(db, provider, { enquiryId: e.id });
    const row = svc.scoreboard(db)[0];
    assert.equal(row.approval, null);
    assert.equal(row.median_edit_ratio, null);
    assert.equal(row.drafts_total, 1);
    assert.equal(row.reviewed, 0);
  });

  test('cost is null when any draft in the group carried no cost', async () => {
    const e = svc.createEnquiry(db, { subject: 'Hello', body: 'Hi' });
    await svc.generateDraft(db, provider, { enquiryId: e.id });
    assert.equal(svc.scoreboard(db)[0].cost_usd, null, 'mock drafts must not render as money spent');
  });

  test('attribution follows the version, not the clock', async () => {
    const v1 = svc.listPrompts(db)[0];
    const v2 = svc.createPrompt(db, { label: 'v2', system_prompt: 'Warm, ask a question, propose a call.' });
    const e = svc.createEnquiry(db, { subject: 'Hello', body: 'Hi' });

    const a = await svc.generateDraft(db, provider, { enquiryId: e.id, promptVersionId: v1.id });
    const b = await svc.generateDraft(db, provider, { enquiryId: e.id, promptVersionId: v2.id });
    svc.saveReview(db, { draftId: a.id, verdict: 'bad', finalText: 'x' });
    svc.saveReview(db, { draftId: b.id, verdict: 'good', finalText: b.text });

    const board = svc.scoreboard(db);
    assert.equal(board.find((r) => r.prompt_version_id === v1.id)!.approval, 0);
    assert.equal(board.find((r) => r.prompt_version_id === v2.id)!.approval, 1);
  });
});

describe('scope and provider honesty', () => {
  let db: DatabaseSync;
  beforeEach(() => { db = fresh(); });

  test('scope separates bench drafts from real inbox drafts', async () => {
    const v1 = svc.listPrompts(db)[0];
    svc.createEnquiry(db, { subject: 'Bench', body: 'Bench body', in_bench: true });
    const live = svc.createEnquiry(db, { subject: 'Live', body: 'Live body' });

    const { drafts } = await svc.runBench(db, provider, v1.id);
    svc.saveReview(db, { draftId: drafts[0].id, verdict: 'good', finalText: drafts[0].text });

    const liveDraft = await svc.generateDraft(db, provider, { enquiryId: live.id });
    svc.saveReview(db, { draftId: liveDraft.id, verdict: 'bad', finalText: 'rewritten entirely here' });

    assert.equal(svc.scoreboard(db, 'bench')[0].reviewed, 1);
    assert.equal(svc.scoreboard(db, 'bench')[0].good, 1);
    assert.equal(svc.scoreboard(db, 'live')[0].reviewed, 1);
    assert.equal(svc.scoreboard(db, 'live')[0].good, 0);
    assert.equal(svc.scoreboard(db, 'all')[0].reviewed, 2);
  });

  test('mixed providers are flagged rather than silently averaged', async () => {
    const e = svc.createEnquiry(db, { subject: 'Hello', body: 'Hi' });
    const d1 = await svc.generateDraft(db, provider, { enquiryId: e.id });
    svc.saveReview(db, { draftId: d1.id, verdict: 'good', finalText: d1.text });
    assert.equal(svc.scoreboard(db)[0].mixed_providers, false);

    const fakeLive = {
      name: 'anthropic' as const,
      model: 'claude-sonnet-5',
      async draft() {
        return {
          text: 'A live-looking draft.',
          provider: 'anthropic' as const,
          model: 'claude-sonnet-5',
          inputTokens: 800,
          outputTokens: 300,
          costUsd: 0.0046,
          latencyMs: 900,
        };
      },
    };
    const d2 = await svc.generateDraft(db, fakeLive, { enquiryId: e.id });
    svc.saveReview(db, { draftId: d2.id, verdict: 'good', finalText: d2.text });

    assert.equal(svc.scoreboard(db)[0].mixed_providers, true);
    assert.deepEqual(svc.scoreboard(db)[0].providers, ['anthropic', 'mock']);
  });
});

describe('bench', () => {
  let db: DatabaseSync;
  beforeEach(() => { db = fresh(); });

  test('refuses to run against an empty bench', async () => {
    const v1 = svc.listPrompts(db)[0];
    await assert.rejects(() => svc.runBench(db, provider, v1.id), svc.BadRequest);
  });

  test('drafts every bench enquiry exactly once, and nothing else', async () => {
    svc.createEnquiry(db, { subject: 'One', body: 'First body', in_bench: true });
    svc.createEnquiry(db, { subject: 'Two', body: 'Second body', in_bench: true });
    svc.createEnquiry(db, { subject: 'Not benched', body: 'Third body' });

    const { run, drafts } = await svc.runBench(db, provider, svc.listPrompts(db)[0].id);
    assert.equal(drafts.length, 2);
    assert.equal(svc.benchRunDrafts(db, run.id).length, 2);
  });

  test('two versions on the same bench see identical inputs and still differ', async () => {
    svc.createEnquiry(db, { subject: 'One', body: 'First body', in_bench: true });
    const v1 = svc.listPrompts(db)[0];
    const v2 = svc.createPrompt(db, { label: 'v2', system_prompt: 'Warm. Ask a question. Propose a call.' });

    const runA = await svc.runBench(db, provider, v1.id);
    const runB = await svc.runBench(db, provider, v2.id);

    assert.equal(runA.drafts[0].enquiry_id, runB.drafts[0].enquiry_id);
    assert.notEqual(runA.drafts[0].text, runB.drafts[0].text);
  });

  test('bench membership can be toggled after the fact', () => {
    const e = svc.createEnquiry(db, { subject: 'One', body: 'Body' });
    assert.equal(e.in_bench, 0);
    assert.equal(svc.setBenchMembership(db, e.id, true)!.in_bench, 1);
    assert.equal(svc.setBenchMembership(db, e.id, false)!.in_bench, 0);
    assert.equal(svc.setBenchMembership(db, 999, true), null);
  });

  test('running the bench against an unknown version raises NotFound', async () => {
    svc.createEnquiry(db, { subject: 'One', body: 'Body', in_bench: true });
    await assert.rejects(() => svc.runBench(db, provider, 9999), svc.NotFound);
  });
});

describe('comparison end to end', () => {
  function benchDb() {
    const db = fresh();
    for (let i = 0; i < 6; i++) {
      svc.createEnquiry(db, { subject: `Enquiry ${i}`, body: `Body number ${i}`, in_bench: true });
    }
    return db;
  }

  test('a clean sweep on the bench is reported as better', async () => {
    const db = benchDb();
    const v1 = svc.listPrompts(db)[0];
    const v2 = svc.createPrompt(db, { label: 'v2', system_prompt: 'Warm. Ask a question. Propose a call.' });

    const runA = await svc.runBench(db, provider, v1.id);
    const runB = await svc.runBench(db, provider, v2.id);
    for (const d of runA.drafts) svc.saveReview(db, { draftId: d.id, verdict: 'bad', finalText: 'rewritten' });
    for (const d of runB.drafts) svc.saveReview(db, { draftId: d.id, verdict: 'good', finalText: d.text });

    const c = svc.comparison(db, v1.id, v2.id, 'bench');
    assert.equal(c.verdict, 'better');
    assert.equal(c.a.approval, 0);
    assert.equal(c.b.approval, 1);
  });

  test('a one-draft difference on six samples is reported as noise', async () => {
    const db = benchDb();
    const v1 = svc.listPrompts(db)[0];
    const v2 = svc.createPrompt(db, { label: 'v2', system_prompt: 'Warm. Ask a question.' });

    const runA = await svc.runBench(db, provider, v1.id);
    const runB = await svc.runBench(db, provider, v2.id);
    runA.drafts.forEach((d, i) => svc.saveReview(db, { draftId: d.id, verdict: i < 3 ? 'good' : 'bad', finalText: d.text }));
    runB.drafts.forEach((d, i) => svc.saveReview(db, { draftId: d.id, verdict: i < 4 ? 'good' : 'bad', finalText: d.text }));

    assert.equal(svc.comparison(db, v1.id, v2.id, 'bench').verdict, 'no detectable difference');
  });

  test('an unreviewed version yields "not enough data", never a fake win', async () => {
    const db = benchDb();
    const v1 = svc.listPrompts(db)[0];
    const v2 = svc.createPrompt(db, { label: 'v2', system_prompt: 'Warm.' });
    const runA = await svc.runBench(db, provider, v1.id);
    for (const d of runA.drafts) svc.saveReview(db, { draftId: d.id, verdict: 'good', finalText: d.text });

    assert.equal(svc.comparison(db, v1.id, v2.id, 'bench').verdict, 'not enough data');
  });
});

describe('seed', () => {
  test('seeds a starter prompt and a bench, once', () => {
    const db = openDb(':memory:');
    assert.equal(seedIfEmpty(db), true);
    assert.equal(seedIfEmpty(db), false, 'seeding must be idempotent');

    assert.equal(svc.listPrompts(db).length, 1);
    assert.equal(svc.getActivePrompt(db)!.system_prompt, STARTER_PROMPT);
    assert.ok(svc.benchEnquiries(db).length >= 5, 'the bench needs enough variety to be useful');
  });

  test('the seeded bench runs end to end with no API key', async () => {
    const db = openDb(':memory:');
    seedIfEmpty(db);
    const { drafts } = await svc.runBench(db, provider, svc.getActivePrompt(db)!.id);
    assert.equal(drafts.length, svc.benchEnquiries(db).length);
    for (const d of drafts) assert.ok(d.text.length > 20);
  });
});
