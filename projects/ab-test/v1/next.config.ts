import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // node:sqlite is a runtime builtin; keep it out of the server bundle graph.
  serverExternalPackages: ['node:sqlite'],
};

export default nextConfig;
