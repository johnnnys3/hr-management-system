import { defineConfig, mergeConfig } from 'vitest/config'
import viteConfig from './vite.config'

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: 'jsdom',
      setupFiles: ['./src/test/setup.ts'],
      globals: true,
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
