import { createServer, request as httpRequest } from 'node:http';
import type { IncomingMessage, Server, ServerResponse } from 'node:http';
import { createReadStream } from 'node:fs';
import { stat } from 'node:fs/promises';
import { join, normalize, resolve, sep, extname } from 'node:path';

const MIME: Record<string, string> = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
};

/** Both path separators, however the host platform spells them. */
const SEPARATORS = new Set(['/', String.fromCharCode(92)]);

/**
 * Resolve a URL path inside the web root, or null if it escapes.
 *
 * Order matters here. Leading separators are stripped BEFORE normalising, because
 * normalise clamps ".." at the root: normalising "/../package.json" first would quietly
 * turn it into "/package.json" and the containment check below would never get to decide
 * anything. Stripping first keeps the traversal visible so the check is what rejects it.
 */
export function safeResolve(root: string, urlPath: string): string | null {
  let decoded: string;
  try {
    decoded = decodeURIComponent(urlPath);
  } catch {
    return null;
  }
  if (decoded.includes(String.fromCharCode(0))) return null;

  let i = 0;
  while (i < decoded.length && SEPARATORS.has(decoded[i])) i++;

  const abs = resolve(root, normalize(decoded.slice(i)));
  const rootAbs = resolve(root);
  if (abs !== rootAbs && !abs.startsWith(rootAbs + sep)) return null;
  return abs;
}

function proxyToApi(req: IncomingMessage, res: ServerResponse, apiPort: number): void {
  const proxied = httpRequest(
    {
      host: '127.0.0.1',
      port: apiPort,
      path: req.url,
      method: req.method,
      headers: { ...req.headers, host: `127.0.0.1:${apiPort}` },
    },
    (upstream) => {
      res.writeHead(upstream.statusCode ?? 502, upstream.headers);
      upstream.pipe(res);
    },
  );

  proxied.on('error', () => {
    if (res.headersSent) {
      res.destroy();
      return;
    }
    res.writeHead(502, { 'content-type': 'application/json; charset=utf-8' });
    res.end(JSON.stringify({ error: `API server not reachable on 127.0.0.1:${apiPort}` }));
  });

  req.pipe(proxied);
}

/**
 * Accept only loopback Host headers.
 *
 * The API applies the same check, but a proxied request reaches it with the Host rewritten
 * to 127.0.0.1, so the API can no longer see the original. Checking here is what actually
 * stops a rebound hostname reading data through a plain GET, which carries no Origin
 * header for the API's other check to catch.
 */
function hostIsLocal(host: string | undefined): boolean {
  const hostname = (host ?? '').replace(/:\d+$/, '').toLowerCase();
  return hostname === '127.0.0.1' || hostname === 'localhost' || hostname === '[::1]';
}

export function createWebServer(webRoot: string, apiPort: number): Server {
  return createServer(async (req, res) => {
    if (!hostIsLocal(req.headers.host)) {
      res.writeHead(403, { 'content-type': 'text/plain; charset=utf-8' }).end('local requests only');
      return;
    }

    const rawPath = (req.url ?? '/').split('?')[0];

    if (rawPath.startsWith('/api/')) {
      proxyToApi(req, res, apiPort);
      return;
    }

    if (req.method !== 'GET' && req.method !== 'HEAD') {
      res.writeHead(405).end();
      return;
    }

    const target = safeResolve(webRoot, rawPath === '/' ? '/index.html' : rawPath);
    if (target === null) {
      res.writeHead(403).end('forbidden');
      return;
    }

    try {
      const info = await stat(target);
      const file = info.isDirectory() ? join(target, 'index.html') : target;
      const size = info.isDirectory() ? (await stat(file)).size : info.size;

      res.writeHead(200, {
        'content-type': MIME[extname(file).toLowerCase()] ?? 'application/octet-stream',
        'content-length': size,
        'cache-control': 'no-cache',
        'x-content-type-options': 'nosniff',
      });
      if (req.method === 'HEAD') {
        res.end();
        return;
      }
      createReadStream(file).pipe(res);
    } catch {
      res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' }).end('not found');
    }
  });
}
