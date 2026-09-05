import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    // Bind IPv4 explicitly. Left to itself Vite binds ::1 only, and 127.0.0.1:3100 then
    // refuses the connection on hosts where localhost does not resolve to IPv6.
    host: '127.0.0.1',
    port: 3100,
    strictPort: true,
    // Same-origin in dev as in production, so no CORS and no environment-specific API base URL.
    proxy: { '/api': { target: 'http://127.0.0.1:4100', changeOrigin: true } },
  },
  build: { outDir: 'dist', sourcemap: false },
});
