import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');

/**
 * Boots the real entrypoint as a child process.
 *
 * The unit and HTTP suites import modules directly, so none of them ever executed
 * src/main.ts. A syntax error or a bad wiring there would have shipped with a green test
 * run. This is the test that would have caught it.
 */
function boot(env: Record<string, string>) {
  const child = spawn(
    process.execPath,
    ['--disable-warning=ExperimentalWarning', join(ROOT, 'src', 'main.ts')],
    { env: { ...process.env, ANTHROPIC_API_KEY: '', ...env }, stdio: ['ignore', 'pipe', 'pipe'] },
  );
  let out = '';
  child.stdout.on('data', (d) => { out += String(d); });
  child.stderr.on('data', (d) => { out += String(d); });
  return {
    child,
    output: () => out,
    waitFor: (needle: string, ms = 15000) =>
      new Promise<void>((resolve, reject) => {
        const started = Date.now();
        const tick = setInterval(() => {
          if (out.includes(needle)) { clearInterval(tick); resolve(); }
          else if (Date.now() - started > ms) { clearInterval(tick); reject(new Error(`timed out waiting for ${needle}. Got:\n${out}`)); }
        }, 100);
      }),
  };
}

describe('the app actually starts', () => {
  test('boots on its own ports, serves the UI, and drafts with no API key', async (t) => {
    const dir = mkdtempSync(join(tmpdir(), 'drafter-smoke-'));
    const webPort = 3391;
    const apiPort = 4391;
    const app = boot({ WEB_PORT: String(webPort), API_PORT: String(apiPort), DB_PATH: join(dir, 'smoke.db') });

    t.after(() => {
      app.child.kill();
      try { rmSync(dir, { recursive: true, force: true }); } catch { /* windows may hold the file */ }
    });

    await app.waitFor('Reply Drafter');
    assert.match(app.output(), /offline mock/, 'with no key it must announce the offline drafter');
    assert.match(app.output(), /seeded/, 'a fresh database gets the starter prompt and bench');

    const base = `http://127.0.0.1:${webPort}`;

    const page = await fetch(base + '/');
    assert.equal(page.status, 200);
    assert.match(await page.text(), /Reply Drafter/);

    const health = await (await fetch(base + '/api/health')).json();
    assert.equal(health.ok, true);
    assert.equal(health.live_api_key, false, 'no key means no live drafting');
    assert.equal(health.provider, 'mock');

    const enquiry = await (await fetch(base + '/api/enquiries', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ subject: 'Smoke test', body: 'Can you build us an internal tool?', sender: 'Sam' }),
    })).json();

    const draft = await (await fetch(base + '/api/drafts', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ enquiry_id: enquiry.id }),
    })).json();

    assert.ok(draft.text.length > 20, 'a real draft came back through the proxy');
    assert.equal(draft.provider, 'mock');
    assert.ok(draft.text.includes('Sam'), 'the draft addresses the sender');

    // The key must never leak through any surface, even when one is set.
    assert.ok(!JSON.stringify(health).includes('sk-'));
  });

  test('a taken port fails with a readable message instead of a stack trace', async (t) => {
    const dirA = mkdtempSync(join(tmpdir(), 'drafter-a-'));
    const dirB = mkdtempSync(join(tmpdir(), 'drafter-b-'));
    const first = boot({ WEB_PORT: '3392', API_PORT: '4392', DB_PATH: join(dirA, 'a.db') });
    t.after(() => {
      first.child.kill();
      for (const d of [dirA, dirB]) { try { rmSync(d, { recursive: true, force: true }); } catch { /* ignore */ } }
    });
    await first.waitFor('Reply Drafter');

    const second = boot({ WEB_PORT: '3392', API_PORT: '4392', DB_PATH: join(dirB, 'b.db') });
    const code = await new Promise<number>((resolve) => second.child.on('exit', (c) => resolve(c ?? -1)));

    assert.equal(code, 1, 'it should exit non-zero rather than hang');
    assert.match(second.output(), /already in use/);
    assert.ok(!second.output().includes('at ModuleLoader'), 'no raw stack trace');
  });
});
