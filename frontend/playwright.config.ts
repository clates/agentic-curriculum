import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: 'html',

  globalSetup: require.resolve('./global-setup'),
  globalTeardown: require.resolve('./global-teardown'),

  use: {
    baseURL: 'http://localhost:3002',
    trace: 'on-first-retry',
  },

  // Journeys tell the product's story (e2e/journeys/1-5); the app shell is checked on every
  // form factor a parent might use.
  projects: [
    {
      name: 'desktop',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'mobile',
      use: { ...devices['Pixel 7'] },
      testMatch: 'app-shell.spec.ts',
    },
  ],

  webServer: {
    command: 'PORT=3002 BACKEND_URL=http://localhost:8182 npm run dev',
    url: 'http://localhost:3002',
    reuseExistingServer: !process.env.CI,
    timeout: 60_000,
  },
});
