import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

// scoring.json is optional. Fetch it at runtime only if it existed at build time,
// so a missing file never produces a 404 in the browser console.
const hasScoring = existsSync(fileURLToPath(new URL('./public/data/scoring.json', import.meta.url)));

export default defineConfig({
  // Relative base + hash routing: the built site works from any static host or sub-path.
  base: './',
  plugins: [react()],
  define: {
    __HAS_SCORING_JSON__: JSON.stringify(hasScoring),
  },
  build: {
    target: 'es2020',
    sourcemap: false,
  },
  preview: {
    port: 4173,
    strictPort: true,
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    include: ['tests/unit/**/*.test.{ts,tsx}', 'tests/integration/**/*.test.{ts,tsx}'],
    css: false,
    testTimeout: 30000,
  },
});
