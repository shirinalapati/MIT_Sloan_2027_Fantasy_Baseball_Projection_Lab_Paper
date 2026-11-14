/// <reference types="vite/client" />

/** True when public/data/scoring.json existed at build time (see vite.config.ts). */
declare const __HAS_SCORING_JSON__: boolean;

declare module '*.md?raw' {
  const content: string;
  export default content;
}
