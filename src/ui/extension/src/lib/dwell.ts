/** Shared randomized dwell — only pacing sleep in Surfer (AST-1236 / AST-1174). */

import { getPacingConfig } from "./pacingConfig";

export type DwellBounds = {
  centerSeconds: number;
  spreadSeconds: number;
};

/**
 * Sleep a uniform random duration in [center - spread, center + spread] seconds.
 * Bounds default from getPacingConfig(); optional override is for future config-only
 * gaps (parent OQ2) without a second sleep helper.
 * Uses ordinary setTimeout — never chrome.alarms (dwell stays under MV3 idle window).
 * Returns the chosen duration in seconds (for observability / tests).
 * Requires pacing config loaded (even when `bounds` is passed) so the MV3 ceiling
 * comes from the server key, not a client-side bare literal.
 */
export async function dwell(bounds?: DwellBounds): Promise<number> {
  const pacing = getPacingConfig();
  const cfg = bounds
    ? bounds
    : {
        centerSeconds: pacing.dwell_center_seconds,
        spreadSeconds: pacing.dwell_spread_seconds,
      };
  const lo = cfg.centerSeconds - cfg.spreadSeconds;
  const hi = cfg.centerSeconds + cfg.spreadSeconds;
  const ceiling = pacing.mv3_idle_ceiling_seconds;
  if (!(lo > 0) || !(hi >= lo)) {
    throw new Error(`dwell: invalid bounds lo=${lo} hi=${hi}`);
  }
  if (hi >= ceiling) {
    throw new Error(
      `dwell: ceiling ${hi}s must stay under mv3_idle_ceiling_seconds=${ceiling} (no chrome.alarms)`,
    );
  }
  const seconds = lo + Math.random() * (hi - lo);
  await new Promise<void>((resolve) => {
    setTimeout(resolve, seconds * 1000);
  });
  return seconds;
}
