import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { openDb } from './db.ts';
import { createApiServer, defaultDeps } from './api.ts';
import { createWebServer } from './web.ts';
import { seedIfEmpty } from './seed.ts';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, '..');

const WEB_PORT = Number(process.env.WEB_PORT ?? 3300);
const API_PORT = Number(process.env.API_PORT ?? 4300);
const DB_PATH = process.env.DB_PATH ?? join(ROOT, 'data', 'drafter.db');
/** Loopback only. Never 0.0.0.0: this tool has no auth by design. */
const HOST = '127.0.0.1';

const db = openDb(DB_PATH);
const seeded = seedIfEmpty(db);
const deps = defaultDeps(db);

const api = createApiServer(deps);
const web = createWebServer(join(ROOT, 'web'), API_PORT);

function onListenError(which: string, port: number) {
  return (err: Error & { code?: string }) => {
    console.error("");
    if (err.code === 'EADDRINUSE') {
      console.error(`  Port ${port} is already in use, so the ${which} could not start.`);
      console.error('  Stop whatever is on it, or set WEB_PORT / API_PORT to something free.');
    } else {
      console.error(`  The ${which} failed to start: ${err.message}`);
    }
    console.error("");
    process.exit(1);
  };
}

api.on('error', onListenError('API server', API_PORT));
web.on('error', onListenError('web server', WEB_PORT));

api.listen(API_PORT, HOST, () => {
  web.listen(WEB_PORT, HOST, () => {
    console.log('');
    console.log('  Reply Drafter');
    console.log(`  open        http://${HOST}:${WEB_PORT}`);
    console.log(`  api         http://${HOST}:${API_PORT}`);
    console.log(`  database    ${DB_PATH}${seeded ? '  (seeded)' : ''}`);
    console.log(
      deps.liveKey
        ? `  drafter     live Claude, ${deps.provider.model}`
        : '  drafter     offline mock (no ANTHROPIC_API_KEY set, everything still works)',
    );
    console.log('');
  });
});

function shutdown(): void {
  api.close();
  web.close();
  db.close();
  process.exit(0);
}

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
