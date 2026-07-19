import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Trace the bundled prompt markdown into the serverless function on Vercel
  // (the /api/draft route reads these files at runtime).
  outputFileTracingIncludes: {
    "/api/draft": ["./prompts/**/*"],
  },
};

export default nextConfig;
