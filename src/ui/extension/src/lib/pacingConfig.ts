/** Surfer pacing — server SURFER_PACING_CONFIG mirror (AST-1236). */

export type SurferPacingConfig = {
  dwell_center_seconds: number;
  dwell_spread_seconds: number;
  max_tabs: number;
  mv3_idle_ceiling_seconds: number;
};

let cached: SurferPacingConfig | null = null;

/** Replace the in-memory cache (call after a successful fetch, or in tests). */
export function setPacingConfig(config: SurferPacingConfig): void {
  cached = {
    dwell_center_seconds: config.dwell_center_seconds,
    dwell_spread_seconds: config.dwell_spread_seconds,
    max_tabs: config.max_tabs,
    mv3_idle_ceiling_seconds: config.mv3_idle_ceiling_seconds,
  };
}

/** Current cached pacing config; throws if fetch/set has not run. */
export function getPacingConfig(): SurferPacingConfig {
  if (!cached) {
    throw new Error("Surfer pacing config not loaded — call fetchPacingConfig first");
  }
  return cached;
}

/**
 * GET /api/surfer/pacing_config via the caller-supplied authenticated fetch.
 * Background context owns network I/O (AST-1170); this module does not call fetch itself
 * with a hardcoded base URL — the shell passes an already-authenticated GET helper.
 */
export async function fetchPacingConfig(
  getJson: (path: string) => Promise<SurferPacingConfig>,
): Promise<SurferPacingConfig> {
  const config = await getJson("/api/surfer/pacing_config");
  setPacingConfig(config);
  return getPacingConfig();
}

/**
 * One-at-a-time (or max_tabs) slot contract. Default max from getPacingConfig().max_tabs.
 * acquire() waits until a slot is free; release() transfers the slot to a waiter when
 * one is queued (no decrement), or decrements when the queue is empty.
 * Never opens more than max_tabs — including under interleaved acquire/release.
 */
export function createTabBudget(maxTabs?: number): {
  acquire: () => Promise<void>;
  release: () => void;
  inFlight: () => number;
} {
  const limit = maxTabs ?? getPacingConfig().max_tabs;
  if (!Number.isInteger(limit) || limit < 1) {
    throw new Error(`createTabBudget: max_tabs must be integer >= 1, got ${limit}`);
  }
  let inFlight = 0;
  const waiters: Array<() => void> = [];
  return {
    async acquire() {
      if (inFlight < limit) {
        inFlight += 1;
        return;
      }
      await new Promise<void>((resolve) => {
        waiters.push(resolve);
      });
      // Slot already transferred by release() — do not increment again.
    },
    release() {
      if (inFlight <= 0) {
        throw new Error("createTabBudget.release called with nothing in flight");
      }
      const next = waiters.shift();
      if (next) {
        // Transfer: leave inFlight booked; woken acquire must not re-increment.
        next();
        return;
      }
      inFlight -= 1;
    },
    inFlight: () => inFlight,
  };
}
