import { defineConfig, devices } from '@playwright/test';

const FRONTEND_PORT = Number(process.env.E2E_FRONTEND_PORT ?? 3002);
const BACKEND_PORT = Number(process.env.E2E_BACKEND_PORT ?? 8182);
// The login project runs against its own backend (AUTH_REQUIRED=1, its own database) and its own
// frontend, so the main suite keeps running with login off, exactly as before.
const AUTH_FRONTEND_PORT = Number(process.env.E2E_AUTH_FRONTEND_PORT ?? 3003);
const AUTH_BACKEND_PORT = Number(process.env.E2E_AUTH_BACKEND_PORT ?? 8184);
const AUTH_DB_FILE = process.env.E2E_AUTH_DB_FILE ?? `/tmp/playwright-auth-${AUTH_BACKEND_PORT}.db`;
// A small scale so a lockout lasts seconds, not minutes (test-only; production leaves it unset).
const AUTH_BACKOFF_SCALE = process.env.E2E_AUTH_BACKOFF_SCALE ?? '0.2';

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
      testIgnore: ['auth/**'],
    },
    {
      name: 'mobile',
      use: { ...devices['Pixel 7'] },
      testMatch: ['app-shell.spec.ts', 'parent-shell.spec.ts', 'parent/**/*.spec.ts'],
    },
    {
      // Sign-in, sessions and lockout, on a phone, against the AUTH_REQUIRED=1 servers below.
      name: 'auth',
      use: { ...devices['Pixel 7'], baseURL: `http://localhost:${AUTH_FRONTEND_PORT}` },
      testMatch: ['auth/**/*.spec.ts'],
    },
  ],

  // The suite runs against a production build (`next build` + `next start`), not `next dev`: the
  // dev server compiles each page on first hit and falls over under parallel load (page loads
  // abort, proxied requests reset, 5 s assertions race the compiler). Set E2E_DEV_SERVER=1 to use
  // the dev server for quick local iteration on the frontend.
  webServer: [
    {
      command: process.env.E2E_DEV_SERVER
        ? `PORT=${FRONTEND_PORT} BACKEND_URL=http://localhost:${BACKEND_PORT} npm run dev`
        : `echo '{"extends":"./tsconfig.json"}' > tsconfig.e2e.json && NEXT_DIST_DIR=.next-e2e-${FRONTEND_PORT} npx next build && NEXT_DIST_DIR=.next-e2e-${FRONTEND_PORT} BACKEND_URL=http://localhost:${BACKEND_PORT} npx next start -p ${FRONTEND_PORT}`,
      url: `http://localhost:${FRONTEND_PORT}`,
      reuseExistingServer: !process.env.CI,
      timeout: 240_000,
    },
    {
      // Login backend: fresh database, login required, short lockouts. Never reused, so the
      // database and the backoff scale are always the ones set here.
      command:
        `rm -f ${AUTH_DB_FILE} ${AUTH_DB_FILE}-wal ${AUTH_DB_FILE}-shm && cd ../src && ` +
        `CURRICULUM_DB_PATH=${AUTH_DB_FILE} AUTH_REQUIRED=1 AUTH_BACKOFF_SCALE=${AUTH_BACKOFF_SCALE} ` +
        `LLM_BASE_URL=http://127.0.0.1:9/v1 OPENROUTER_API_KEY=e2e-stub-not-a-real-key ` +
        `OPENAI_API_KEY=e2e-stub-not-a-real-key ` +
        `../venv/bin/uvicorn main:app --port ${AUTH_BACKEND_PORT} --timeout-keep-alive 120`,
      url: `http://localhost:${AUTH_BACKEND_PORT}/health`,
      reuseExistingServer: false,
      timeout: 60_000,
    },
    {
      // Login frontend: its own production build (own dist dir and tsconfig copy, so it can build
      // while the main suite's frontend builds) started with AUTH_REQUIRED=1.
      command:
        `echo '{"extends":"./tsconfig.json"}' > tsconfig.e2e-auth.json && ` +
        `NEXT_TSCONFIG=tsconfig.e2e-auth.json NEXT_DIST_DIR=.next-e2e-auth npx next build && ` +
        `AUTH_REQUIRED=1 NEXT_DIST_DIR=.next-e2e-auth BACKEND_URL=http://localhost:${AUTH_BACKEND_PORT} ` +
        `npx next start -p ${AUTH_FRONTEND_PORT}`,
      url: `http://localhost:${AUTH_FRONTEND_PORT}/login`,
      reuseExistingServer: false,
      timeout: 240_000,
    },
  ],
});
