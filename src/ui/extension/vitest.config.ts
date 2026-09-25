import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vitest/config';
import { WxtVitest } from 'wxt/testing/vitest-plugin';

const extensionRoot = fileURLToPath(new URL('.', import.meta.url));
const repoRoot = path.resolve(extensionRoot, '../../..');

export default defineConfig({
  plugins: [WxtVitest()],
  server: {
    fs: {
      // Repo-root tests/component/extension/** live outside the package root.
      allow: [repoRoot],
    },
  },
  test: {
    environment: 'node',
    include: [path.join(repoRoot, 'tests/component/extension/**/*.test.{ts,tsx}')],
    passWithNoTests: true,
  },
});
