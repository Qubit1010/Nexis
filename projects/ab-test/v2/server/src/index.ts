import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join, resolve } from 'node:path';
import fastifyStatic from '@fastify/static';

import { buildApp } from './app.ts';
import { config, usingDefaultPassword } from './config.ts';

const here = dirname(fileURLToPath(import.meta.url));
const webDist = resolve(here, '../../web/dist');

const app = await buildApp();

// In production the API also serves the built SPA, so deploying is one process on one port.
// In development Vite serves the frontend on 3100 and proxies /api here.
if (existsSync(join(webDist, 'index.html'))) {
  await app.register(fastifyStatic, { root: webDist, wildcard: false });
  app.setNotFoundHandler((req, reply) => {
    if (req.url.startsWith('/api/')) return reply.code(404).send({ error: 'Not found' });
    return reply.sendFile('index.html');
  });
  app.log.info('serving built frontend from %s', webDist);
}

if (usingDefaultPassword) {
  if (config.isProd) {
    app.log.error('ADMIN_PASSWORD is still the default. Refusing to start in production.');
    process.exit(1);
  }
  app.log.warn('ADMIN_PASSWORD is unset, so the dashboard password is "change-me". Set it in .env.');
}

try {
  await app.listen({ port: config.port, host: config.host });
  app.log.info('public form: http://localhost:3100/   dashboard: http://localhost:3100/admin');
} catch (err) {
  app.log.error(err);
  process.exit(1);
}

for (const signal of ['SIGINT', 'SIGTERM'] as const) {
  process.on(signal, () => {
    app.close().then(() => process.exit(0));
  });
}
