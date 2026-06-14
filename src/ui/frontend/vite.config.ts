import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

const frontendRoot = fileURLToPath(new URL('.', import.meta.url))
const repoRoot = path.resolve(frontendRoot, '../../..')
const frontendNodeModules = path.join(frontendRoot, 'node_modules')

const vitestMaxWorkers = Number(process.env.ASTRAL_VITEST_MAX_WORKERS ?? "2")

export default defineConfig({
  // Repo-root .env (same file Flask loads via python-dotenv) — not src/ui/frontend/.
  envDir: repoRoot,
  plugins: [react()],
  resolve: {
    alias: {
      react: path.join(frontendNodeModules, 'react'),
      'react-dom': path.join(frontendNodeModules, 'react-dom'),
      'react-router-dom': path.join(frontendNodeModules, 'react-router-dom'),
      '@testing-library/react': path.join(frontendNodeModules, '@testing-library/react'),
      '@testing-library/user-event': path.join(frontendNodeModules, '@testing-library/user-event'),
      '@testing-library/jest-dom': path.join(frontendNodeModules, '@testing-library/jest-dom'),
    },
  },
  server: {
    fs: {
      allow: [repoRoot],
    },
    proxy: {
      '/api': 'http://localhost:5001',
    },
  },
  test: {
    environment: 'jsdom',
    alias: {
      '@stytch/react': path.join(repoRoot, 'tests/component/frontend/stytchMock.tsx'),
    },
    testTimeout: 120000,
    // Default 2 workers; raise with ASTRAL_VITEST_MAX_WORKERS when the machine has headroom.
    maxWorkers: Number.isFinite(vitestMaxWorkers) && vitestMaxWorkers > 0 ? vitestMaxWorkers : 2,
    setupFiles: [path.join(frontendRoot, 'vitest.setup.ts')],
    include: [path.join(repoRoot, 'tests/component/frontend/**/*.test.{ts,tsx}')],
    coverage: {
      provider: 'v8',
      reporter: ['json', 'json-summary'],
      reportsDirectory: '../../../tests/.coverage/frontend',
      include: ['src/**/*.{ts,tsx}'],
      exclude: ['src/main.tsx', 'src/vite-env.d.ts'],
      all: true,
    },
  },
})
