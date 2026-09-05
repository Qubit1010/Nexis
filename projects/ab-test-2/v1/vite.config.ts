import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3200,
    strictPort: true,
    proxy: {
      // Browser only ever talks to 3200, so there is no CORS surface to configure.
      '/api': { target: 'http://localhost:4200', changeOrigin: true },
    },
  },
  build: { outDir: 'dist' },
  test: {
    environment: 'node',
    include: ['tests/**/*.test.ts'],
    // node:sqlite is stable enough to depend on but still prints an ExperimentalWarning.
    poolOptions: { forks: { execArgv: ['--disable-warning=ExperimentalWarning'] } },
  },
});
