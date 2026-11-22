import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  // The E2E suite builds into its own directory so it never clobbers a running `npm run dev`.
  distDir: process.env.NEXT_DIST_DIR || '.next',
  // `next build` rewrites its tsconfig (adds the dist dir's types). Point the E2E build at a
  // generated throwaway copy so running the suite never dirties the tracked tsconfig.json.
  // A second E2E build (the login project) names its own copy so two builds never share one file.
  typescript: {
    tsconfigPath: process.env.NEXT_DIST_DIR
      ? (process.env.NEXT_TSCONFIG ?? 'tsconfig.e2e.json')
      : 'tsconfig.json',
  },
};

export default nextConfig;
