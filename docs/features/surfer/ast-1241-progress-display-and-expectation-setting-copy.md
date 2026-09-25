# AST-1241 — Progress display and expectation-setting copy

**Linear:** [AST-1241](https://linear.app/astralcareermatch/issue/AST-1241/progress-display-and-expectation-setting-copy-progress-cancellation)
**Parent:** [AST-1176](https://linear.app/astralcareermatch/issue/AST-1176/progress-cancellation-and-discarding-a-batch) — Progress, cancellation, and discarding a batch
**Publish ref:** `origin/sub/AST-1176/AST-1241-progress-display-and-copy`

Candidate-facing Surfer progress surface for a paced fan-out: expectation-setting copy before the wait, a position counter that advances as pages are visited, a finishing phase that covers the gap between the last tab closing and outcomes resolving, and a finished phase that appears on its own. All strings live in a named config block and are served over an authenticated GET. Injected into the job-site page via the AST-1170 shadow-root toast host (extended, not replaced). Parallel with discard-state (**AST-1240**); does **not** own cancel/stop or the keep-or-discard prompt (**AST-1242**); does **not** change pacing (**AST-1174** / **AST-1236** / **AST-1239**).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `SURFER_PROGRESS_CONFIG` (copy + poll interval + active status key) + asserts; document in module header | utils |
| `src/ui/api/api_surfer.py` | Add authenticated `GET /api/surfer/progress_config` (create blueprint file if absent — see Decision) | ui |
| `src/ui/server.py` | Register `surfer_bp` if this ticket creates `api_surfer.py` for the first time on the tip | ui |
| `src/ui/extension/src/lib/progressConfig.ts` | New: types, fetch/cache for progress config | ui |
| `src/ui/extension/src/lib/toastHost.ts` | New **only if** AST-1170 toast host is absent on the tip — provisional shadow-root host (see Decision) | ui |
| `src/ui/extension/src/lib/progressSurface.ts` | New: phase renderer on the toast host (expectation / visiting / finishing / finished) | ui |
| `src/ui/extension/src/lib/runWithProgress.ts` | New: expectation → fan-out + remaining poll → finishing → finished orchestration | ui |

**No changes expected:** `dwell.ts` / `pacingConfig.ts` / `SURFER_PACING_CONFIG` (**AST-1236**), `fanOut.ts` loop body (**AST-1239** — do not edit), cancel/prompt UI (**AST-1242**), discard state (**AST-1240**), WXT `package.json` / entrypoints / manifest (**AST-1170**), `tests/` / bible (Betty after Code Complete).

⚠️ **Decision — land extension `src/lib/` modules even if AST-1170 scaffold is not yet on this branch:** Same placement rule as AST-1236 / AST-1239. Create only the planned lib files under settled `src/ui/extension/src/lib/`. Do **not** invent `package.json`, WXT config, or `entrypoints/`. AST-1170 (or the shell that wires fan-out) imports `runWithProgress`. If at build time the path conflicts with an already-merged AST-1170 layout (different `src/` nesting), **stop and comment on the parent** — do not relocate silently.

⚠️ **Decision — extend the toast host; do not invent a second injected surface:** Parent + ticket require one shadow-root surface. Progress renders by calling a `ToastHost` port (set primary + detail text, show/hide). If `src/ui/extension/src/lib/toast.ts` (or equivalent AST-1170 host exporting a compatible `ToastHost`) **already exists** on the tip, implement progress against that export and **do not** add `toastHost.ts`. If it is **absent**, add provisional `toastHost.ts` implementing the same `ToastHost` interface in a shadow root — AST-1170 later owns replacing/merging this file into the canonical toast module; builder must not leave two hosts mounted.

⚠️ **Decision — do not edit `fanOut.ts`:** AST-1239 forbids progress UI inside the loop. This ticket wraps `runPacedFanOut` in `runWithProgress` and drives the surface from `fetchRemaining` polls (same remaining contract as AST-1239). Progress advances when `visited = total_count - remaining_urls.length` changes after visits are recorded server-side.

⚠️ **Decision — one config block owns progress copy and the cancel/prompt strings AST-1242 will render:** Parent AC10 / child AC3 require every message on progress, prompt, and cancel surfaces to come from the server. This ticket introduces `SURFER_PROGRESS_CONFIG` with keys for all three surfaces so there is a single source of truth. This ticket **renders only** expectation / visiting / finishing / finished. Cancel control + keep-or-discard prompt UI stay **AST-1242**, which must read the cancel/prompt keys from this block (or the GET) rather than minting client strings.

⚠️ **Decision — server config + GET, not extension-baked copy:** `pattern.config.config-block` + `astral.layers.ui-config-driven-business-logic`. Changing a string in `config.py` and restarting the server must change what the candidate reads without rebuilding the extension.

## Pre-build dependency gate (before Stage 1 code)

**Done when:** Builder can name the live symbols below (or confirm provisional contracts still match published sibling plans).

1. Confirm AST-1239 `runPacedFanOut` + `FanOutPorts` / `RemainingWork` exist at `src/ui/extension/src/lib/fanOut.ts` (or the published plan's Consumer contract still matches). Required fields on remaining: `batch_id`, `status`, `remaining_urls`, `done_count`, `total_count`.
2. Confirm AST-1236 pacing helpers are **not** reimplemented here.
3. Confirm toast host situation (Decision above): extend existing toast **or** land provisional `toastHost.ts`.
4. If `RemainingWork` shape on the tip differs from the Consumer contract (missing `status` / `total_count`, or `remaining_urls` includes non-pending) → **STOP**, comment on **AST-1241** with the delta — do not invent a second remaining vocabulary.
5. If `api_surfer.py` / `SURFER_PACING_CONFIG` are absent on the tip, still proceed (create progress route / config as specified). Do **not** re-add pacing keys.

## Stage 1: `SURFER_PROGRESS_CONFIG` in config.py

**Done when:** `SURFER_PROGRESS_CONFIG` is importable with the keys below; module docstring lists the block; asserts pass; `python3 -m py_compile src/utils/config.py` succeeds (repo venv: `~/astral/.venv/bin/python`).

1. In `src/utils/config.py` module docstring `Config sections:`, add:
   `SURFER_PROGRESS_CONFIG — Surfer fan-out progress / expectation / cancel-prompt copy + finishing poll (AST-1241)`.

2. Placement: immediately after the `SURFER_PACING_CONFIG` asserts if that block exists on the tip; otherwise after the `METEORITE_CONFIG` / `BOT_BLOCKED` asserts (same anchor AST-1236 used — after `assert "METEORITE_NEW" in JOB_STATES["BOT_BLOCKED"]["prior_states"]`).

3. Add:

```python
# ---------------------------------------------------------------------------
# SURFER_PROGRESS_CONFIG: candidate-facing Surfer batch UX copy (AST-1241 / AST-1176).
# Progress surface renders expectation / visiting / finishing / finished.
# Cancel + keep-or-discard prompt strings are owned here for AC10; UI is AST-1242.
# Magnitude note: AST-1174 dwell is ~10±5s/page → ~12s/page average — write copy to that.
# ---------------------------------------------------------------------------
SURFER_PROGRESS_CONFIG = {
    # Must match SURFER_BATCH_CONFIG["initial_status"] when that block exists ("RUNNING").
    "active_batch_status": "RUNNING",
    # How often runWithProgress re-asks remaining while fan-out / finishing are in flight.
    "finishing_poll_interval_ms": 1000,
    "copy": {
        # Shown once before paced visits begin (tab must stay open; slowness is deliberate).
        "expectation": (
            "Keep this tab open while Astral visits each listing — about twelve seconds "
            "per page, so a long search can take several minutes. It's slow on purpose; "
            "safer that way. Go work on something else and let this tab cook."
        ),
        # {visited} = pages already visited (delivered or failed); {total} = worklist size.
        "visiting": "Visiting {visited} of {total}…",
        # remaining_urls empty, batch still active (outcomes resolving after last tab).
        "finishing": "Wrapping up — finishing the last results. You can leave this tab open.",
        # Batch status is no longer active_batch_status (COMPLETED / CANCELLED / …).
        "finished": "Done — this run is finished.",
        # AST-1242 renders these; do not use in the progress surface on this ticket.
        "cancel_button": "Stop",
        "cancel_prompt_title": "Stop this run?",
        "cancel_prompt_body": (
            "Keep the jobs already collected, or discard them from your Jobs views? "
            "Discard cannot be undone from here."
        ),
        "cancel_prompt_keep": "Keep what I have",
        "cancel_prompt_discard": "Discard them",
    },
}

_surfer_progress_copy = SURFER_PROGRESS_CONFIG["copy"]
assert isinstance(SURFER_PROGRESS_CONFIG["active_batch_status"], str) and SURFER_PROGRESS_CONFIG["active_batch_status"]
assert isinstance(SURFER_PROGRESS_CONFIG["finishing_poll_interval_ms"], int)
assert SURFER_PROGRESS_CONFIG["finishing_poll_interval_ms"] > 0
for _surfer_progress_key in (
    "expectation",
    "visiting",
    "finishing",
    "finished",
    "cancel_button",
    "cancel_prompt_title",
    "cancel_prompt_body",
    "cancel_prompt_keep",
    "cancel_prompt_discard",
):
    assert _surfer_progress_key in _surfer_progress_copy
    assert isinstance(_surfer_progress_copy[_surfer_progress_key], str) and _surfer_progress_copy[_surfer_progress_key].strip()
assert "{visited}" in _surfer_progress_copy["visiting"] and "{total}" in _surfer_progress_copy["visiting"]
```

4. If `SURFER_BATCH_CONFIG` is already defined in the same file, add immediately after the asserts above:

```python
assert SURFER_PROGRESS_CONFIG["active_batch_status"] == SURFER_BATCH_CONFIG["initial_status"]
```

If `SURFER_BATCH_CONFIG` is absent, skip this assert (do not invent the batch block here).

⚠️ **Decision — copy magnitude ~12s/page:** Parent planning note (AST-1174 dwell 10±5 → ~twelve seconds a page). Do not invent hour-scale wording. Do not reference raw dwell center/spread numbers in the string if that would duplicate `SURFER_PACING_CONFIG` as a second source — the prose "about twelve seconds" is expectation-setting, not a second pacing control.

⚠️ **Decision — `{visited}` / `{total}` placeholders only on `visiting`:** Client does simple `.replace` — no i18n framework. Do not add other format syntax.

⚠️ **Decision — `finishing_poll_interval_ms` in config:** Named, changeable without rebuild. Do not hardcode `1000` in TypeScript.

5. Verify Stage 1:

```bash
~/astral/.venv/bin/python -c "
from src.utils.config import SURFER_PROGRESS_CONFIG
assert 'expectation' in SURFER_PROGRESS_CONFIG['copy']
assert '{visited}' in SURFER_PROGRESS_CONFIG['copy']['visiting']
assert SURFER_PROGRESS_CONFIG['finishing_poll_interval_ms'] > 0
"
~/astral/.venv/bin/python -m py_compile src/utils/config.py
```

**Ritual:** `code(AST-1241): SURFER_PROGRESS_CONFIG block`

## Stage 2: Authenticated `progress_config` GET

**Done when:** `GET /api/surfer/progress_config` with a valid Bearer returns JSON matching the config keys below; unauthenticated → 401; blueprint registered.

1. **If** `src/ui/api/api_surfer.py` exists (AST-1236): add the route and import `SURFER_PROGRESS_CONFIG` alongside pacing. Do **not** remove or rewrite `pacing_config`.

2. **If** the file does not exist: create it as a thin blueprint (mirror `api_meteorite.py` / AST-1236 style):

```python
"""Surfer extension API (AST-1241 progress config; sibling Surfer routes may join)."""

from flask import Blueprint, jsonify

from ui.auth import require_auth
from src.utils.config import SURFER_PROGRESS_CONFIG

surfer_bp = Blueprint("surfer", __name__, url_prefix="/api/surfer")
```

Then register in `src/ui/server.py` next to other API blueprints:

```python
from ui.api.api_surfer import surfer_bp  # noqa: E402
app.register_blueprint(surfer_bp)
```

If creating the file fresh, **do not** re-implement `pacing_config` here (AST-1236 owns it). Merge conflict with a later pacing landing is expected and resolved by keeping both routes.

3. Add the route (same body whether extending or creating):

```python
@surfer_bp.route("/progress_config", methods=["GET"])
@require_auth
def progress_config():
    # Plain dict copy so callers cannot mutate the config module.
    copy = SURFER_PROGRESS_CONFIG["copy"]
    return jsonify({
        "active_batch_status": SURFER_PROGRESS_CONFIG["active_batch_status"],
        "finishing_poll_interval_ms": SURFER_PROGRESS_CONFIG["finishing_poll_interval_ms"],
        "copy": {
            "expectation": copy["expectation"],
            "visiting": copy["visiting"],
            "finishing": copy["finishing"],
            "finished": copy["finished"],
            "cancel_button": copy["cancel_button"],
            "cancel_prompt_title": copy["cancel_prompt_title"],
            "cancel_prompt_body": copy["cancel_prompt_body"],
            "cancel_prompt_keep": copy["cancel_prompt_keep"],
            "cancel_prompt_discard": copy["cancel_prompt_discard"],
        },
    })
```

⚠️ **Decision — path `/api/surfer/progress_config`:** Same namespace as pacing. Auth required; no `candidate_id` in the path (copy is product-wide).

4. Verify:

```bash
PYTHONPATH=src ~/astral/.venv/bin/python -m py_compile src/ui/api/api_surfer.py src/ui/server.py
PYTHONPATH=src ~/astral/.venv/bin/python -c "
from ui.api.api_surfer import surfer_bp
assert surfer_bp.url_prefix == '/api/surfer'
"
```

**Ritual:** `code(AST-1241): GET /api/surfer/progress_config`

## Stage 3: Extension progress modules

**Done when:** The TypeScript modules below exist with the listed exports; no WXT entrypoints added; no edits to `fanOut.ts`; no React; no `chrome.alarms`; all candidate-visible strings come from the cached progress config (or ToastHost displaying those strings).

### 3a. `progressConfig.ts`

Create `src/ui/extension/src/lib/progressConfig.ts`:

```typescript
/** Surfer progress UX — server SURFER_PROGRESS_CONFIG mirror (AST-1241). */

export type SurferProgressCopy = {
  expectation: string;
  visiting: string;
  finishing: string;
  finished: string;
  cancel_button: string;
  cancel_prompt_title: string;
  cancel_prompt_body: string;
  cancel_prompt_keep: string;
  cancel_prompt_discard: string;
};

export type SurferProgressConfig = {
  active_batch_status: string;
  finishing_poll_interval_ms: number;
  copy: SurferProgressCopy;
};

let cached: SurferProgressConfig | null = null;

export function setProgressConfig(config: SurferProgressConfig): void {
  cached = {
    active_batch_status: config.active_batch_status,
    finishing_poll_interval_ms: config.finishing_poll_interval_ms,
    copy: { ...config.copy },
  };
}

export function getProgressConfig(): SurferProgressConfig {
  if (!cached) {
    throw new Error("Surfer progress config not loaded — call fetchProgressConfig first");
  }
  return cached;
}

/** GET /api/surfer/progress_config via caller-supplied authenticated fetch (AST-1170 owns network). */
export async function fetchProgressConfig(
  getJson: (path: string) => Promise<SurferProgressConfig>,
): Promise<SurferProgressConfig> {
  const config = await getJson("/api/surfer/progress_config");
  setProgressConfig(config);
  return getProgressConfig();
}

/** Fill visiting template; visited/total are non-negative integers from remaining math. */
export function formatVisitingCopy(visited: number, total: number): string {
  const template = getProgressConfig().copy.visiting;
  return template
    .replace(/\{visited\}/g, String(visited))
    .replace(/\{total\}/g, String(total));
}
```

### 3b. `ToastHost` + provisional `toastHost.ts` (conditional)

Shared interface (document at top of `progressSurface.ts` even when toast is imported from AST-1170):

```typescript
export type ToastHost = {
  /** Ensure the shadow-root surface exists on the page (idempotent). */
  ensure(): void;
  /** Primary line — always server copy (or formatVisitingCopy result). */
  setMessage(text: string): void;
  /** Optional secondary line; pass null to clear. */
  setDetail(text: string | null): void;
  /** Hide the surface without destroying the host element. */
  hide(): void;
};
```

**If AST-1170 toast is absent**, create `src/ui/extension/src/lib/toastHost.ts`:

- `createToastHost(doc: Document = document): ToastHost`
- Mount a single host element on `doc.documentElement` (e.g. `id="astral-surfer-toast-host"`) with `attachShadow({ mode: "open" })`.
- Inside the shadow root: minimal plain DOM — a container, a `.message` node, a `.detail` node. Inline styles on the shadow tree only (fixed position, high z-index, readable contrast). No host-page class names.
- `setMessage` / `setDetail` write `textContent` only (never `innerHTML`).
- `hide()` sets host display none; `ensure()` + setMessage shows it.
- Do **not** import React or frontend Toast components.

**If AST-1170 toast exists**, export or adapt its API to `ToastHost` inside `progressSurface.ts` (thin adapter allowed) and skip creating `toastHost.ts`.

### 3c. `progressSurface.ts`

Create `src/ui/extension/src/lib/progressSurface.ts`:

```typescript
export type ProgressPhase = "expectation" | "visiting" | "finishing" | "finished";

export type ProgressSurface = {
  showExpectation: () => void;
  showVisiting: (visited: number, total: number) => void;
  showFinishing: () => void;
  showFinished: () => void;
  hide: () => void;
};

export function createProgressSurface(host: ToastHost): ProgressSurface;
```

Behavior:

| Phase | Primary message | Detail |
|-------|-----------------|--------|
| expectation | `copy.expectation` | `null` |
| visiting | `formatVisitingCopy(visited, total)` | `null` |
| finishing | `copy.finishing` | `null` |
| finished | `copy.finished` | `null` |

Each `show*` calls `host.ensure()`, then `setMessage` / `setDetail`. Clamp `visited` to `[0, total]` when `total >= 0`. If `total === 0`, still show visiting with `0 of 0` (empty batch) — do not invent alternate copy.

Do **not** render cancel button or prompt elements here.

### 3d. `runWithProgress.ts`

Create `src/ui/extension/src/lib/runWithProgress.ts`:

```typescript
import { runPacedFanOut, type FanOutPorts, type FanOutResult } from "./fanOut";
import { fetchProgressConfig, getProgressConfig } from "./progressConfig";
import { createProgressSurface, type ProgressSurface } from "./progressSurface";
import type { ToastHost } from "./toastHost"; // or from AST-1170 toast module

export type RunWithProgressOptions = {
  debug?: boolean;
  /** Injected surface; required — shell / AST-1170 supplies the host. */
  toastHost: ToastHost;
  /**
   * Optional surface override for tests. Default: createProgressSurface(toastHost).
   */
  surface?: ProgressSurface;
};

/**
 * Expectation copy → paced fan-out with remaining polls → finishing → finished.
 * Does not own cancel. Does not change pacing. Does not edit fanOut.ts.
 */
export async function runWithProgress(
  batchId: string,
  ports: FanOutPorts,
  opts: RunWithProgressOptions,
): Promise<FanOutResult>;
```

Algorithm (literal):

1. `await fetchProgressConfig(ports.getJson)` (reuse `FanOutPorts.getJson`).
2. `const surface = opts.surface ?? createProgressSurface(opts.toastHost)`.
3. `surface.showExpectation()`.
4. Start a poll helper:
   - `async function refreshProgress(): Promise<"active" | "finishing" | "finished">`  
     - `const rem = await ports.fetchRemaining(batchId)`  
     - `const total = rem.total_count`  
     - `const visited = Math.max(0, total - (rem.remaining_urls?.length ?? 0))`  
     - If `rem.status !== getProgressConfig().active_batch_status` → `surface.showFinished()`; return `"finished"`.  
     - If `(rem.remaining_urls?.length ?? 0) === 0` → `surface.showFinishing()`; return `"finishing"`.  
     - Else → `surface.showVisiting(visited, total)`; return `"active"`.
5. `await refreshProgress()` once (moves off expectation onto visiting/finishing/finished as appropriate).
6. Start interval: `setInterval` every `getProgressConfig().finishing_poll_interval_ms` that awaits `refreshProgress()` (ignore overlapping ticks with a simple `inFlight` boolean — skip if previous tick still running). Store interval id.
7. In parallel: `const result = await runPacedFanOut(batchId, ports, { debug: opts?.debug })`.
8. After fan-out returns: call `refreshProgress()`; then **poll until finished**:
   - While `refreshProgress() !== "finished"`, `await` a single delay of `finishing_poll_interval_ms` (ordinary `setTimeout`, not alarms), then refresh again.
   - This covers AC12: last tab closed, outcomes still resolving → finishing copy, then finished without reload/re-click.
9. `clearInterval` the poller in a `finally`. Do **not** auto-`hide()` on finished — leave the finished message visible until the shell/AST-1242 dismisses or navigates. (Shell may call `surface.hide()` later; not this ticket.)
10. Return the `FanOutResult` from step 7.

⚠️ **Decision — visited = total_count - remaining_urls.length:** Matches "advances as pages are visited" because AST-1239 remaining is pending-only; delivered/failed/success drop out of `remaining_urls`. Do not use `done_count` for the visiting counter (`done_count` is terminal outcomes only and would lag behind visits during the finishing gap).

⚠️ **Decision — finishing when remaining empty AND status still active:** Exactly the AST-1168 / parent "honest tail" window. Finished when status leaves `active_batch_status` (COMPLETED after auto-complete, or CANCELLED if AST-1242 cancelled — progress still resolves; it does not own cancel).

⚠️ **Decision — ordinary `setInterval` / `setTimeout` for progress polls only:** Not pacing. Pacing sleeps stay inside `dwell()`. Do not use `chrome.alarms`.

⚠️ **Decision — shell wiring is out of scope for code on this ticket:** Document only (Stage 4). Do not add `entrypoints/background.ts`.

### 3e. Verify Stage 3

```bash
test -f src/ui/extension/src/lib/progressConfig.ts
test -f src/ui/extension/src/lib/progressSurface.ts
test -f src/ui/extension/src/lib/runWithProgress.ts
# toastHost.ts only when AST-1170 toast absent:
# test -f src/ui/extension/src/lib/toastHost.ts
rg -n 'chrome\.alarms|browser\.alarms|innerHTML|from \"react\"|cancel_prompt|Stop this run' src/ui/extension/src/lib/progress*.ts src/ui/extension/src/lib/runWithProgress.ts src/ui/extension/src/lib/toastHost.ts 2>/dev/null
# expect: no alarms, no innerHTML, no react; cancel_prompt strings may appear only as type fields in progressConfig.ts, not rendered in progressSurface/runWithProgress
rg -n 'runPacedFanOut|fetchProgressConfig|showFinishing|formatVisitingCopy|finishing_poll_interval_ms' src/ui/extension/src/lib/runWithProgress.ts src/ui/extension/src/lib/progressSurface.ts src/ui/extension/src/lib/progressConfig.ts
# expect imports + phase helpers present
# fanOut.ts must be untouched:
git diff --name-only | rg 'fanOut\.ts' || true
```

**Ritual:** `code(AST-1241): progress surface + runWithProgress`

## Stage 4: Shell wiring note (documentation-only — no code)

**Done when:** Plan documents how AST-1170 / the background shell must call this; **no files changed in this stage**.

After a search-page intake returns a `batch_id`, the shell starts:

```typescript
await runWithProgress(batchId, ports, { toastHost, debug });
```

instead of bare `runPacedFanOut(...)`. AST-1242 later adds cancel affordance beside the same `ToastHost` without a second shadow root.

If build-child is tempted to add `entrypoints/` to "make it run" → **STOP** — that is AST-1170.

**Ritual:** none (no commit).

## Self-Assessment

**Scope:** Single-Component — one config block, one thin authenticated GET on `surfer_bp`, and extension lib modules under `src/ui/extension/src/lib/` that consume AST-1239 fan-out + remaining without editing the loop.

**Conf:** Medium — config/GET/surface phases are fully specified against published AST-1236/1239 patterns, but the toast host may be provisional until AST-1170 lands, and `RemainingWork.status` / pending-only semantics are still owned by AST-1231; the pre-build gate + STOP rules prevent guessing.

**Risk:** Medium — wrong visited math (using `done_count` instead of pending-gap) would make the bar look stalled during the finishing window this epic exists to fix; a second injected surface would fight LinkedIn/Indeed CSS and steal AST-1170; baking copy into the client would fail AC3/AC10. Mitigated by explicit visited formula, ToastHost single-surface Decision, and config-driven GET.

## Code rules check

- **§1.3 DRY:** Single progress orchestrator; reuses `runPacedFanOut` and `FanOutPorts.fetchRemaining` — no second fan-out loop.
- **§2.1 / config-source-of-truth / no-hardcoded-sets:** All candidate-facing strings and the poll interval live in `SURFER_PROGRESS_CONFIG`; GET returns a copy; client formats only `{visited}`/`{total}`.
- **§2.4 batch:** Client-driven remaining polls; no dispatcher claim/release; no delete.
- **§2.6 state:** Does not transition batch or job state — read-only remaining/status for display.
- **§3.2 ui-config-driven-business-logic:** Copy and phase thresholds (active status string, poll ms) resolved server-side / from config; extension renders.
- **§3.3 import-direction:** Python UI imports utils (+ auth) only. Extension modules import sibling libs only — no React frontend imports.
- **§3.5 / frontend-file-placement:** Files under settled `src/ui/extension/` (sibling to frontend). Provisional toast host is explicit until AST-1170 merges.
- **astral.patterns.require-auth-on-protected-endpoints:** GET behind `@require_auth`.
- **engineer-test-tree-ban:** No `tests/` / bible edits on this ticket.
- **debug-contract-gated:** No new Style D in this ticket (forward `debug` into `runPacedFanOut` only).

## Build-child sync note

```bash
~/.cursor/scripts/git/sync-child.sh sub/AST-1176/AST-1241-progress-display-and-copy \
  --ftr AST-1176 \
  --worktree /home/susan/astral-AST-1176/
```

Parent publish ref (epic registry): `ftr/AST-1176-progress-cancellation-and-discarding-a-batch`. `sync-child.sh --ftr AST-1176` looks for exact `origin/ftr/AST-1176` and will skip until that short name exists; if only the slug ref is on origin, re-run with `--ftr AST-1176-progress-cancellation-and-discarding-a-batch`.
