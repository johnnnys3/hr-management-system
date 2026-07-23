import { defineConfig } from '@playwright/test'

// docs/03-tech-stack.md §9's E2E tool. Runs against the deployed
// composition (docs/04-system-architecture.md §6) at Caddy's single
// origin, per ADR-0004 — no mocked backend, per docs/08-testing-plan.md
// §6. The stack (docker compose) must already be up; this config does
// not start it (CI's e2e job does that itself, matching the backend
// job's own docker-compose-driven pattern).
export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  retries: process.env.CI ? 1 : 0,
  reporter: 'list',
  // CI's shared runner is measurably slower than local dev for these
  // antd-heavy pages (the same resource-contention shape already found
  // and documented for vitest, frontend/vitest.config.ts) — a bit more
  // headroom on assertions than the 5s default.
  expect: { timeout: 8000 },
  use: {
    baseURL: process.env.E2E_BASE_URL ?? 'http://localhost:8080',
    trace: 'retain-on-failure',
    // Several antd Modals (e.g. New Employee) are taller than a typical
    // default viewport, which pushes a Select's popup options out of the
    // visible area — not a bug in the app, just this suite's own viewport.
    viewport: { width: 1280, height: 1600 },
  },
})
