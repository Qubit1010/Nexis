import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // The pages read data/weeks/*.json via fs at request time; tracing can't detect
  // that, so include the snapshots in every route's serverless bundle for Vercel.
  outputFileTracingIncludes: {
    "/": ["./data/weeks/**"],
    "/**": ["./data/weeks/**"],
  },
};

export default nextConfig;
