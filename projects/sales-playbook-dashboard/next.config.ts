import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Ensure the bundled playbook markdown is traced into the serverless function
  // when deployed to Vercel (the API route reads these files at runtime).
  outputFileTracingIncludes: {
    "/api/draft": ["./prompts/**/*"],
  },
};

export default nextConfig;
