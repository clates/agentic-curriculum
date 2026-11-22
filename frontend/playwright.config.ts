import { defineConfig, devices } from '@playwright/test';

const FRONTEND_PORT = Number(process.env.E2E_FRONTEND_PORT ?? 3002);
const BACKEND_PORT = Number(process.env.E2E_BACKEND_PORT ?? 8182);

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: 'html',

  globalSetup: require.resolve('./global-setup'),
  globalTeardown: require.resolve('./global-teardown'),

  use: {
    baseURL: `http://localhost:${FRONTEND_PORT}`,
    trace: 'on-first-retry',
  },

  // Journeys tell the product's story (e2e/journeys/1-5); the app shell and the parent screens
  // are checked on a phone and at desktop width.
  projects: [
    {
      name: 'desktop',
      use: { ...devices['Desktop Chrome'] },
      // The phone tab bar does not exist at desktop width (the header nav replaces it).
      grepInvert: /tab bar/,
    },
    {
      name: 'mobile',
      use: { ...devices['Pixel 7'] },
      testMatch: ['app-shell.spec.ts', 'parent-shell.spec.ts', 'parent/**/*.spec.ts'],
    },
  ],

  // The suite runs against a production build (`next build` + `next start`), not `next dev`: the
  // dev server compiles each page on first hit and falls over under parallel load (page loads
  // abort, proxied requests reset, 5 s assertions race the compiler). Set E2E_DEV_SERVER=1 to use
  // the dev server for quick local iteration on the frontend.
  webServer: {
    command: process.env.E2E_DEV_SERVER
      ? `PORT=${FRONTEND_PORT} BACKEND_URL=http://localhost:${BACKEND_PORT} npm run dev`
      : `echo '{"extends":"./tsconfig.json"}' > tsconfig.e2e.json && NEXT_DIST_DIR=.next-e2e-${FRONTEND_PORT} npx next build && NEXT_DIST_DIR=.next-e2e-${FRONTEND_PORT} BACKEND_URL=http://localhost:${BACKEND_PORT} npx next start -p ${FRONTEND_PORT}`,
    url: `http://localhost:${FRONTEND_PORT}`,
    reuseExistingServer: !process.env.CI,
    timeout: 240_000,
  },
});
