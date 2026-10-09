import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Demo hubs are private, per-prospect pages: never let them be indexed or framed.
  async headers() {
    return [{ source: "/:path*", headers: [
      { key: "X-Robots-Tag", value: "noindex, nofollow" },
      { key: "X-Frame-Options", value: "SAMEORIGIN" },
      { key: "Referrer-Policy", value: "no-referrer" },
    ] }];
  },
};

export default nextConfig;
