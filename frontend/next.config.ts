import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    // Wardrobe photos are served from Supabase Storage as short-lived signed
    // URLs — wildcard the project subdomain so this keeps working if the
    // project ref ever changes.
    remotePatterns: [{ protocol: "https", hostname: "*.supabase.co", pathname: "/storage/v1/object/sign/**" }],
  },
};

export default nextConfig;
