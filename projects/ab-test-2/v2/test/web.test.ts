import { test, describe, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { dirname, join, resolve } from 'node:path';
import { request as httpRequest } from 'node:http';
import type { Server } from 'node:http';
import { createWebServer, safeResolve } from '../src/web.ts';
import { stripNul } from '../src/http.ts';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB_ROOT = join(HERE, '..', 'web');
const NUL = String.fromCharCode(0);

describe('safeResolve', () => {
  test('resolves an ordinary file inside the root', () => {
    const got = safeResolve(WEB_ROOT, '/app.js');
    assert.equal(got, resolve(WEB_ROOT, 'app.js'));
  });

  test('refuses to walk out of the root', () => {
    assert.equal(safeResolve(WEB_ROOT, '/../package.json'), null);
    assert.equal(safeResolve(WEB_ROOT, '/../../../../etc/passwd'), null);
    assert.equal(safeResolve(WEB_ROOT, '/a/b/../../../secrets.txt'), null);
  });

  test('refuses percent-encoded traversal', () => {
    assert.equal(safeResolve(WEB_ROOT, '/%2e%2e/package.json'), null);
    assert.equal(safeResolve(WEB_ROOT, '/%2e%2e%2fpackage.json'), null);
  });

  test('refuses a NUL byte and a malformed escape', () => {
    assert.equal(safeResolve(WEB_ROOT, `/app.js${NUL}.png`), null);
    assert.equal(safeResolve(WEB_ROOT, '/%zz'), null);
  });

  test('a path that only looks like traversal is still served', () => {
    assert.equal(safeResolve(WEB_ROOT, '/..style.css'), resolve(WEB_ROOT, '..style.css'));
  });

  test('backslash traversal is refused too, since Windows treats it as a separator', () => {
    const BSLASH = String.fromCharCode(92);
    assert.equal(safeResolve(WEB_ROOT, `/..${BSLASH}package.json`), null);
  });
});

describe('stripNul', () => {
  test('removes NUL and leaves everything else alone', () => {
    assert.equal(stripNul(`a${NUL}b`), 'ab');
    assert.equal(stripNul('plain text'), 'plain text');
    assert.equal(stripNul(`${NUL}${NUL}x`), 'x');
    assert.equal(stripNul(''), '');
  });
});

describe('static server', () => {
  let server: Server;
  let port: number;

  before(async () => {
    // API port 1 is deliberately dead: nothing here should reach a backend.
    server = createWebServer(WEB_ROOT, 1);
    await new Promise<void>((r) => server.listen(0, '127.0.0.1', r));
    port = (server.address() as { port: number }).port;
  });

  after(() => server.close());

  const get = (path: string) => fetch(`http://127.0.0.1:${port}${path}`);

  /** Sends the path verbatim, bypassing the URL normalisation fetch() applies. */
  const rawStatus = (path: string): Promise<number> =>
    new Promise((res, rej) => {
      const r = httpRequest({ host: '127.0.0.1', port, path, method: 'GET' }, (up) => {
        up.resume();
        res(up.statusCode ?? 0);
      });
      r.on('error', rej);
      r.end();
    });

  test('serves the app shell at the root', async () => {
    const res = await get('/');
    assert.equal(res.status, 200);
    assert.match(res.headers.get('content-type') ?? '', /text\/html/);
    assert.match(await res.text(), /Reply Drafter/);
  });

  test('serves the stylesheet and script with correct content types', async () => {
    assert.match((await get('/style.css')).headers.get('content-type') ?? '', /text\/css/);
    assert.match((await get('/app.js')).headers.get('content-type') ?? '', /javascript/);
  });

  test('sets nosniff on served assets', async () => {
    assert.equal((await get('/app.js')).headers.get('x-content-type-options'), 'nosniff');
  });

  test('a missing file is a 404, not a 500', async () => {
    assert.equal((await get('/does-not-exist.js')).status, 404);
  });

  test('traversal out of the web root is refused', async () => {
    // fetch() resolves "/../" out of a URL before sending it, so the server would never
    // see the traversal. These go out as raw request lines with the path untouched.
    assert.equal(await rawStatus('/../package.json'), 403);
    assert.equal(await rawStatus('/%2e%2e/package.json'), 403);
    assert.equal(await rawStatus('/a/b/../../../package.json'), 403);
  });

  test('an unreachable API surfaces a 502 rather than hanging', async () => {
    const res = await get('/api/health');
    assert.equal(res.status, 502);
    assert.match((await res.json()).error, /not reachable/);
  });

  test('non-GET methods on static paths are refused', async () => {
    const res = await fetch(`http://127.0.0.1:${port}/style.css`, { method: 'PUT' });
    assert.equal(res.status, 405);
  });
});

describe('web server host check', () => {
  let server: Server;
  let port: number;

  before(async () => {
    server = createWebServer(WEB_ROOT, 1);
    await new Promise<void>((r) => server.listen(0, '127.0.0.1', r));
    port = (server.address() as { port: number }).port;
  });

  after(() => server.close());

  const statusWithHost = (host: string, path = '/'): Promise<number> =>
    new Promise((res, rej) => {
      const r = httpRequest({ host: '127.0.0.1', port, path, method: 'GET', headers: { host } }, (up) => {
        up.resume();
        res(up.statusCode ?? 0);
      });
      r.on('error', rej);
      r.end();
    });

  test('loopback hosts are served', async () => {
    assert.equal(await statusWithHost(`127.0.0.1:${port}`), 200);
    assert.equal(await statusWithHost(`localhost:${port}`), 200);
  });

  test('a rebound hostname is refused, including on a GET that carries no Origin', async () => {
    assert.equal(await statusWithHost('attacker.example.com'), 403);
    // The API path would otherwise be proxied with the Host rewritten, losing the evidence.
    assert.equal(await statusWithHost('attacker.example.com', '/api/scoreboard'), 403);
  });
});
