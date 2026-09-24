import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests',
  workers: 1,
  retries: 0,
  timeout: 60_000,
  expect: { timeout: 10_000 },
  reporter: 'list',
  outputDir: '/tmp/cms-e2e-results',
  use: { baseURL: 'http://frontend:5173', trace: 'off' },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
  ],
})
