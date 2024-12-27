import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api", // All requests to /api will be proxied
        destination: "https://l.vv0lll.com", // Directly proxy to the root endpoint
      },
    ];
  },
};

export default nextConfig;
