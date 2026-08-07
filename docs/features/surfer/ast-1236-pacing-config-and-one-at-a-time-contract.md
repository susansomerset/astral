# AST-1236 — Pacing config and one-at-a-time contract

**Linear:** [AST-1236](https://linear.app/astralcareermatch/issue/AST-1236/pacing-config-and-one-at-a-time-contract-human-paced-fan-out-over-the)
**Parent:** [AST-1174](https://linear.app/astralcareermatch/issue/AST-1174/human-paced-fan-out-over-the-batch-worklist) — Human-paced fan-out over the batch worklist
**Publish ref:** `origin/sub/AST-1174/AST-1236-pacing-config`

Named config for the Surfer fan-out dwell window (**10 ± 5 seconds**) and the max-tabs ceiling (**1**), plus the shared client `dwell()` helper and a max-tabs slot contract that sibling **AST-1239** will call. Introduces the **client-driven paced fan-out** shape on the config half: values live in `src/utils/config.py`, are served by a thin authenticated GET so they can change without rebuilding the extension, and the extension sleeps only through `dwell()` (ordinary timers — not `chrome.alarms`). Does **not** own the open/dwell/post/close loop (**AST-1239**), progress/cancel (**AST-1176**), or resume (**AST-1177**).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `SURFER_PACING_CONFIG` block + module-load asserts (bounds under MV3 30s idle ceiling) | utils |
| `src/ui/api/api_surfer.py` | New blueprint: authenticated `GET /api/surfer/pacing_config` returns the block | ui |
| `src/ui/server.py` | Register `surfer_bp` | ui |
| `src/ui/extension/src/lib/pacingConfig.ts` | New: types, `fetchPacingConfig`, in-memory cache getters, `createTabBudget` | ui |
| `src/ui/extension/src/lib/dwell.ts` | New: shared `dwell()` — random sleep inside configured (or override) bounds | ui |

**No changes expected:** fan-out loop / tab open-close (**AST-1239**), `chrome.alarms`, WXT scaffold / manifest / package.json (**AST-1170** owns the extension shell — this ticket only drops `src/lib/` modules under the settled `src/ui/extension/` path), progress/cancel UI, resume prompt, `tests/` / bible (Betty after Code Complete).

⚠️ **Decision — land extension `src/lib/` modules even if AST-1170 scaffold is not yet on this branch:** Placement is settled at `src/ui/extension/` (AST-1170). Create the `src/lib/` files and directories only — do **not** invent `package.json`, WXT config, or entrypoints. If `src/ui/extension/` does not exist yet, create it as a directory containing only these planned files. AST-1170 wires them into the bundle; AST-1239 imports them. If at build time the path conflicts with an already-merged AST-1170 layout (different `src/` nesting), **stop and comment on the parent** — do not relocate silently.

⚠️ **Decision — server config + GET, not extension-baked literals:** Parent AC4 requires pacing / max-tabs changeable by config alone with **no extension rebuild**. `pattern.config.config-block` and `astral.config.config-source-of-truth` require the named block in `config.py`. Baking seconds into a TypeScript constant would invent a second source of truth and force a zip/rebuild to tune. The extension caches the GET response for the run; `dwell()` reads that cache (or explicit override bounds).

## Stage 1: `SURFER_PACING_CONFIG` in config.py

**Done when:** `SURFER_PACING_CONFIG` is importable with the keys and defaults below; module-load asserts reject an MV3-unsafe window; `python3 -m py_compile src/utils/config.py` succeeds (repo venv: `~/astral/.venv/bin/python`).

1. In `src/utils/config.py`, immediately after the `METEORITE_CONFIG` block and its asserts (after the `assert "METEORITE_NEW" in JOB_STATES["BOT_BLOCKED"]["prior_states"]` line ~2366), add:

```python
# ---------------------------------------------------------------------------
# SURFER_PACING_CONFIG: client-driven paced fan-out (AST-1236 / AST-1174).
# Dwell is centre ± spread seconds, re-rolled per page. max_tabs ships at 1 —
# raising it is a stealth-risk decision (Susan), not throughput tuning.
# Bounds must stay under the MV3 ~30s idle window (ordinary timers, not alarms).
# ---------------------------------------------------------------------------
SURFER_PACING_CONFIG = {
    "dwell_center_seconds": 10,
    "dwell_spread_seconds": 5,
    "max_tabs": 1,
}

_surfer_center = SURFER_PACING_CONFIG["dwell_center_seconds"]
_surfer_spread = SURFER_PACING_CONFIG["dwell_spread_seconds"]
assert isinstance(_surfer_center, (int, float)) and _surfer_center > 0
assert isinstance(_surfer_spread, (int, float)) and _surfer_spread >= 0
assert _surfer_center - _surfer_spread > 0, (
    "SURFER_PACING_CONFIG dwell floor (center - spread) must be > 0"
)
assert _surfer_center + _surfer_spread < 30, (
    "SURFER_PACING_CONFIG dwell ceiling (center + spread) must stay under "
    "the MV3 ~30s idle window (ordinary timers, not chrome.alarms)"
)
assert isinstance(SURFER_PACING_CONFIG["max_tabs"], int) and SURFER_PACING_CONFIG["max_tabs"] >= 1
```

⚠️ **Decision — keys in seconds, not milliseconds:** Parent and project language use seconds (10 ± 5). The extension converts to ms only inside `dwell()` for `setTimeout`. Do not store ms in config.

⚠️ **Decision — block name `SURFER_PACING_CONFIG`:** Surfer-scoped, pacing-only. Do not fold into `ASTRAL_CONFIG` or invent a broader `SURFER_CONFIG` until another Surfer child needs shared non-pacing keys.

2. Verify Stage 1:

```bash
~/astral/.venv/bin/python -c "
from src.utils.config import SURFER_PACING_CONFIG
assert SURFER_PACING_CONFIG['dwell_center_seconds'] == 10
assert SURFER_PACING_CONFIG['dwell_spread_seconds'] == 5
assert SURFER_PACING_CONFIG['max_tabs'] == 1
assert SURFER_PACING_CONFIG['dwell_center_seconds'] + SURFER_PACING_CONFIG['dwell_spread_seconds'] < 30
"
~/astral/.venv/bin/python -m py_compile src/utils/config.py
```

**Ritual:** `code(AST-1236): SURFER_PACING_CONFIG block`

## Stage 2: Authenticated pacing_config GET

**Done when:** `GET /api/surfer/pacing_config` with a valid Bearer returns JSON matching `SURFER_PACING_CONFIG` keys/values; unauthenticated request returns 401; blueprint is registered on the Flask app.

1. Create `src/ui/api/api_surfer.py` as a thin blueprint (mirror `api_meteorite.py` style — UI imports utils only, no core/data):

```python
"""Surfer extension API (AST-1236 pacing config; later Surfer routes may join)."""

from flask import Blueprint, jsonify

from ui.auth import require_auth
from src.utils.config import SURFER_PACING_CONFIG

surfer_bp = Blueprint("surfer", __name__, url_prefix="/api/surfer")


@surfer_bp.route("/pacing_config", methods=["GET"])
@require_auth
def pacing_config():
    # Return a plain dict copy so callers cannot mutate the config module.
    return jsonify({
        "dwell_center_seconds": SURFER_PACING_CONFIG["dwell_center_seconds"],
        "dwell_spread_seconds": SURFER_PACING_CONFIG["dwell_spread_seconds"],
        "max_tabs": SURFER_PACING_CONFIG["max_tabs"],
    })
```

⚠️ **Decision — path `/api/surfer/pacing_config` under blueprint prefix `/api/surfer`:** Keeps Surfer routes namespaced. Do not hang this off `/api/system` or `/api/nav_config` — those are web-app chrome, not the extension client.

⚠️ **Decision — no candidate_id in the path:** Pacing is product-wide, not per-candidate. Auth still required so the endpoint is not open.

2. In `src/ui/server.py`, register the blueprint next to the other API blueprints (after `meteorite_bp` is fine):

```python
from ui.api.api_surfer import surfer_bp  # noqa: E402
app.register_blueprint(surfer_bp)
```

3. Verify Stage 2 (compile only — full HTTP smoke is Betty/UAT; do not add tests here):

```bash
~/astral/.venv/bin/python -m py_compile src/ui/api/api_surfer.py src/ui/server.py
~/astral/.venv/bin/python -c "
from ui.api.api_surfer import surfer_bp, pacing_config
assert surfer_bp.url_prefix == '/api/surfer'
"
```

**Ritual:** `code(AST-1236): GET /api/surfer/pacing_config`

## Stage 3: Extension `pacingConfig.ts` + `dwell.ts`

**Done when:** The two modules exist at the paths below with the exact exports listed; `dwell()` uses only `setTimeout` (no `chrome.alarms`); `createTabBudget(1)` refuses a second acquire until release; no fan-out loop is written.

1. Create directory `src/ui/extension/src/lib/` if missing (see Decision above).

2. Create `src/ui/extension/src/lib/pacingConfig.ts`:

```typescript
/** Surfer pacing — server SURFER_PACING_CONFIG mirror (AST-1236). */

export type SurferPacingConfig = {
  dwell_center_seconds: number;
  dwell_spread_seconds: number;
  max_tabs: number;
};

let cached: SurferPacingConfig | null = null;

/** Replace the in-memory cache (call after a successful fetch, or in tests). */
export function setPacingConfig(config: SurferPacingConfig): void {
  cached = {
    dwell_center_seconds: config.dwell_center_seconds,
    dwell_spread_seconds: config.dwell_spread_seconds,
    max_tabs: config.max_tabs,
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
 * acquire() waits until a slot is free; release() frees one. Never opens more than max_tabs.
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
      inFlight += 1;
    },
    release() {
      if (inFlight <= 0) {
        throw new Error("createTabBudget.release called with nothing in flight");
      }
      inFlight -= 1;
      const next = waiters.shift();
      if (next) next();
    },
    inFlight: () => inFlight,
  };
}
```

⚠️ **Decision — `getJson` injected, not a hardcoded Astral base URL:** Endpoint base and auth live in the extension shell (**AST-1170**). This ticket must not invent a second API client or bake a host string. AST-1239 / shell pass the authenticated getter.

⚠️ **Decision — `createTabBudget` is the one-at-a-time contract:** Exporting `max_tabs` alone is not enough — a second pacing implementation could ignore it. The slot helper is what sibling fan-out must use around each open→close. With shipped `max_tabs: 1`, two pages cannot be in flight.

3. Create `src/ui/extension/src/lib/dwell.ts`:

```typescript
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
 */
export async function dwell(bounds?: DwellBounds): Promise<number> {
  const cfg = bounds
    ? bounds
    : {
        centerSeconds: getPacingConfig().dwell_center_seconds,
        spreadSeconds: getPacingConfig().dwell_spread_seconds,
      };
  const lo = cfg.centerSeconds - cfg.spreadSeconds;
  const hi = cfg.centerSeconds + cfg.spreadSeconds;
  if (!(lo > 0) || !(hi >= lo)) {
    throw new Error(`dwell: invalid bounds lo=${lo} hi=${hi}`);
  }
  if (hi >= 30) {
    throw new Error(
      `dwell: ceiling ${hi}s must stay under MV3 ~30s idle window (no chrome.alarms)`,
    );
  }
  const seconds = lo + Math.random() * (hi - lo);
  await new Promise<void>((resolve) => {
    setTimeout(resolve, seconds * 1000);
  });
  return seconds;
}
```

⚠️ **Decision — `dwell` is the only sleep helper:** Any Surfer pause goes through this function. Do not add a second timer utility in this ticket or leave a comment inviting inline `setTimeout` in the fan-out. Sibling AST-1239 must import `dwell` from this module.

4. Verify Stage 3 by eye (no Vitest project may exist until AST-1170): confirm both files exist, export the names above, contain no `chrome.alarms` / `browser.alarms`, and contain no fan-out / `tabs.create` calls.

**Ritual:** `code(AST-1236): extension dwell + tab budget helpers`

## Self-Assessment

**Scope:** Single-Component — one config block, one thin Surfer API route, and two extension lib modules that introduce the pacing contract without the fan-out loop.

**Conf:** high — mirrors existing `METEORITE_CONFIG` + thin blueprint patterns; extension helpers are small and fully specified; placement under `src/ui/extension/` is already settled by AST-1170.

**Risk:** Medium — wrong bounds or a dual sleep path would either kill the service worker mid-pause or let a second timer underminestealth; the plan gates both with asserts and a single `dwell()` export. max_tabs misuse is contained by `createTabBudget` but only if AST-1239 actually uses it.

## Code rules check

- **§1.3 DRY:** One `dwell()`; one config block; no duplicate sleep helpers.
- **§2.1 config:** Values only in `SURFER_PACING_CONFIG`; API and extension read, do not redefine.
- **§2.4 batch:** N/A — no claim/process/release in this ticket (sibling).
- **§2.6 state machine:** N/A — no entity state transitions.
- **§3.3 imports:** `api_surfer.py` imports utils + auth only (no data/external). Extension modules stay self-contained under `src/ui/extension/src/lib/`.
- **§3.5 naming:** snake_case API path; camelCase TS exports matching frontend lib style.
- **§3.6:** No spike output under `docs/features/` or repo-root `artifacts/`.
