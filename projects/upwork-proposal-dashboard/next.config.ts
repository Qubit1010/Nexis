import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  outputFileTracingIncludes: {
    "/api/generate": ["./src/skill.md"],
    "/api/generate-loom-script": ["./src/loom-skill.md"],
  },
};

export default nextConfig;
