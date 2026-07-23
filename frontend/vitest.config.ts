import { defineConfig, mergeConfig } from 'vitest/config'
import viteConfig from './vite.config'

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: 'jsdom',
      setupFiles: ['./src/test/setup.ts'],
      globals: true,
      // e2e/ is Playwright's own suite (frontend/e2e/playwright.config.ts),
      // not a vitest one — without this, vitest's default include glob
      // picks up e2e/tests/*.spec.ts too and fails on Playwright's own
      // fixture-based test() signature.
      exclude: ['e2e/**', 'node_modules/**'],
      // ponytail: antd-heavy pages under jsdom are expensive enough that
      // running every test file's own jsdom environment concurrently causes
      // real resource contention (CandidateDetailPage/RecruitmentPage time
      // out under it, worse on CI's shared runners than local dev). Running
      // files sequentially trades a few extra seconds of wall clock for a
      // suite that doesn't flake; revisit if the suite grows large enough
      // for that trade to stop being worth it.
      fileParallelism: false,
    },
  }),
)
