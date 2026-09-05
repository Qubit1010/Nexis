import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: ['test/**/*.test.ts'],
    // Only NODE_ENV, which silences the request logger. The suite passes its own admin
    // password to buildApp, so it does not depend on anything injected here.
    env: { NODE_ENV: 'test' },
  },
});
