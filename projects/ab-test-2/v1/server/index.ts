import { buildApp } from './app.ts';
import { loadConfig } from './config.ts';
import { openDb } from './db.ts';
import { selectProvider } from './providers.ts';

const config = loadConfig();
const db = openDb(config.dbPath);
const provider = selectProvider(config.apiKey, config.model);

const app = buildApp({ db, provider, hasApiKey: config.apiKey !== undefined });

app.listen(config.port, () => {
  console.log(`[replylab] api        http://localhost:${config.port}`);
  console.log(`[replylab] database   ${config.dbPath}`);
  console.log(
    provider.name === 'stub'
      ? '[replylab] provider   STUB (no ANTHROPIC_API_KEY set) - drafts are canned, no model is called'
      : `[replylab] provider   anthropic (${provider.model})`,
  );
});
