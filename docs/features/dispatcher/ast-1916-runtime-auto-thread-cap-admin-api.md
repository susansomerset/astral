# AST-1916 — Runtime AUTO-thread cap + admin API

- **Parent:** AST-1875 — add a selection box on Scheduled Tasks to set concurrent tasks limit
- **Ticket:** AST-1916
- **Publish ref:** `sub/AST-1875/AST-1916-runtime-cap-api` (origin only)

The dispatcher's tick loop reads `ASTRAL_CONFIG["max_auto_threads"]` once when the scheduler thread starts, so changing the AUTO concurrency cap needs a code edit and a redeploy. This ticket adds an in-memory, process-local override (valid because production runs one gunicorn worker — `astral.ui.single-gunicorn-worker`), a bounded public getter/setter on `src/core/dispatcher.py`, makes `_tick_loop` read the effective cap every tick, and exposes the cap as two admin routes under `/api/admin/scheduler/`. Bounds (1–100) live in `src/utils/config.py`. No persistence: a restart returns to the config default. The Scheduled Actions header dropdown is sibling AST-1917 and is out of scope here.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `max_auto_threads_min` / `max_auto_threads_max` to `ASTRAL_CONFIG` beside `max_auto_threads` | utils |
| `src/core/dispatcher.py` | Add `_auto_thread_cap_override` global, `get_auto_thread_cap()`, `set_auto_thread_cap()`; `_tick_loop` reads the cap via the getter every tick | core |
| `src/ui/api/api_admin.py` | Add `GET` + `POST` `/api/admin/scheduler/auto_thread_cap` (both `@require_admin`) | ui |

Every row is named in this ticket's `## Scope`; no other files are touched.

## API contract (consumed by AST-1917)

- `GET /api/admin/scheduler/auto_thread_cap` → `200`
  `{"max_auto_threads": <effective int>, "default": <config int>, "min": <config int>, "max": <config int>}`
- `POST /api/admin/scheduler/auto_thread_cap` with JSON body `{"max_auto_threads": <int>}`
  - valid → `200` with the **same payload shape as GET** (reflecting the new effective cap)
  - invalid → `400` `{"error": "max_auto_threads must be a whole number between <min> and <max>"}`; cap unchanged
- No admin session → whatever `@require_admin` returns today (401/403), same as `/scheduler/thread_status`.

---

## Stage 1: Config bounds

**Done when:** `python -c "from src.utils.config import ASTRAL_CONFIG as c; print(c['max_auto_threads'], c['max_auto_threads_min'], c['max_auto_threads_max'])"` prints `3 1 100`.

1. In `src/utils/config.py`, inside `ASTRAL_CONFIG` under the `# --- Dispatcher (dispatcher) ---` block, immediately after the `"max_auto_threads": 3, ...` line (currently line 4500), insert exactly two lines, aligned with the neighbouring comments:

   ```python
       "max_auto_threads_min": 1,        # lowest runtime override accepted for max_auto_threads (admin API / Scheduled Actions)
       "max_auto_threads_max": 100,      # highest runtime override accepted for max_auto_threads (admin API / Scheduled Actions)
   ```

   Do not change the `max_auto_threads` value or any other key.

⚠️ **Decision:** Bounds live as flat keys in `ASTRAL_CONFIG` next to `max_auto_threads` (not a new block) — the Scope says "alongside `max_auto_threads`", and a sibling key is the smallest change that keeps one source of truth (`astral.config.config-source-of-truth`).

## Stage 2: Dispatcher runtime cap + live tick read

**Done when:** In a Python shell, `from src.core import dispatcher as d; d.get_auto_thread_cap()` returns `3`; `d.set_auto_thread_cap(7)` returns `7` and the getter then returns `7`; `d.set_auto_thread_cap(0)`, `(101)`, `("abc")`, `(2.5)`, `(True)`, `(None)` each raise `ValueError` and the getter still returns `7`. `grep -n 'max_auto = ASTRAL_CONFIG' src/core/dispatcher.py` returns nothing.

1. In `src/core/dispatcher.py`, directly below the existing `_tick_event = threading.Event()` line (currently line 986), add:

   ```python

   # Runtime override for the AUTO thread cap (None = use ASTRAL_CONFIG["max_auto_threads"]).
   # In-memory only — a restart/deploy returns to the config default. Coherent only because
   # production runs a single gunicorn worker (one scheduler, one registry per deploy).
   _auto_thread_cap_override: Optional[int] = None
   ```

2. In `src/core/dispatcher.py`, immediately **above** `def _tick_loop() -> None:` (currently line 1867), add these two public functions (two blank lines between top-level defs, matching the file):

   ```python
   def get_auto_thread_cap() -> int:
       """Effective cap on concurrent AUTO task threads: runtime override if set, else config default."""
       # Must NOT be called while holding _registry_lock (threading.Lock is not re-entrant).
       with _registry_lock:
           override = _auto_thread_cap_override
       return override if override is not None else ASTRAL_CONFIG["max_auto_threads"]


   def set_auto_thread_cap(value: Any) -> int:
       """Set the runtime AUTO thread cap. Raises ValueError unless value is an int within the
       config bounds. Never cancels running threads — the tick just stops spawning until
       running AUTO < cap."""
       global _auto_thread_cap_override
       lo = ASTRAL_CONFIG["max_auto_threads_min"]
       hi = ASTRAL_CONFIG["max_auto_threads_max"]
       # type() check (not isinstance) so bools, floats like 2.5 and numeric strings are rejected
       if type(value) is not int or not lo <= value <= hi:
           raise ValueError(f"max_auto_threads must be a whole number between {lo} and {hi}")
       with _registry_lock:
           previous = _auto_thread_cap_override
           _auto_thread_cap_override = value
       logger.info(
           "AUTO thread cap set to %d (was %s; config default %d)",
           value,
           previous if previous is not None else "default",
           ASTRAL_CONFIG["max_auto_threads"],
       )
       return value
   ```

3. In `_tick_loop`, replace the docstring, comment and the two capture lines at the top of the function:

   ```python
       """Global tick: wakes every tick_rate_minutes, spawns due AUTO tasks up to max_auto_threads."""
       # Captured once at thread start — changes to ASTRAL_CONFIG require a server restart
       tick_secs = ASTRAL_CONFIG.get("tick_rate_minutes", 1) * 60
       max_auto = ASTRAL_CONFIG.get("max_auto_threads", 3)
   ```

   with:

   ```python
       """Global tick: wakes every tick_rate_minutes, spawns due AUTO tasks up to get_auto_thread_cap()."""
       # Tick rate is captured once at thread start (changes need a restart); the AUTO cap is
       # re-read every tick via get_auto_thread_cap() so admin overrides apply on the next tick.
       tick_secs = ASTRAL_CONFIG.get("tick_rate_minutes", 1) * 60
   ```

4. In `_tick_loop`, replace the line `slots = max_auto - running_auto` (currently line 1904, directly **after** the `with _registry_lock:` block that computes `running_auto` / `running_ids`) with:

   ```python
               slots = get_auto_thread_cap() - running_auto  # live cap; outside the lock (non-re-entrant)
   ```

   It must stay outside/after the `with _registry_lock:` block — calling the getter inside that block deadlocks the tick thread.

5. Do **not** change `start_scheduler()` (its startup log line still prints the config default, which equals the effective cap at boot), `tick_secs`, `run_task`, CLICK paths, or any cancellation code.

⚠️ **Decision:** Reuse `_registry_lock` rather than a new lock (Scope allows either). One lock is fewer lines, and the override is only ever read next to the registry count. The cost is the re-entrancy hazard, handled by steps 2 and 4 keeping the getter call outside the existing `with` block.

⚠️ **Decision:** Strict type check `type(value) is not int`. That rejects `True`/`False` (a Python `bool` is an `int`), `2.5`, `5.0`, `"5"`, `"abc"`, and `None` (missing body key). So AST-1917 must send a JSON number, not a string. AC 3 only requires rejecting `"abc"` and `2.5`; this is the narrowest rule that also covers the type-confusion cases without coercion logic.

⚠️ **Decision:** The `ASTRAL_CONFIG.get("max_auto_threads", 3)` fallback literal is dropped in the getter (`ASTRAL_CONFIG["max_auto_threads"]`). The key always exists, and a second `3` would be a duplicate default outside `config.py`.

⚠️ **Decision:** Lowering the cap below the running count needs no extra code. `slots` goes ≤ 0, so the existing `if slots > 0:` guard spawns nothing, and running threads are never touched (AC 7).

## Stage 3: Admin routes

**Done when:** With an admin session, `GET /api/admin/scheduler/auto_thread_cap` returns `{"max_auto_threads": 3, "default": 3, "min": 1, "max": 100}` on a fresh start. `POST` with `{"max_auto_threads": 1}` and then `100` each return 200, and the following GET reflects the new value. `POST` with `0`, `101`, `"abc"` or `2.5` each return 400 with an `error` message, and GET still shows the prior value. Without an admin session both routes return 401/403.

1. In `src/ui/api/api_admin.py`, extend the existing `from src.core.dispatcher import (...)` block (currently lines 30–36) by appending `get_auto_thread_cap, set_auto_thread_cap,` on a new line after `meteorite_mailbox_trigger_allows,`.

2. In `src/ui/api/api_admin.py`, directly after the `scheduler_stop_all` function (ends `return jsonify({"killed": killed})`, currently line 2114) and before the `# Script: backfill_culture_links` divider, add:

   ```python


   def _auto_thread_cap_payload() -> Dict[str, int]:
       """Effective AUTO thread cap plus config default and bounds (bounds drive the UI dropdown)."""
       return {
           "max_auto_threads": get_auto_thread_cap(),
           "default": ASTRAL_CONFIG["max_auto_threads"],
           "min": ASTRAL_CONFIG["max_auto_threads_min"],
           "max": ASTRAL_CONFIG["max_auto_threads_max"],
       }


   @admin_bp.route("/scheduler/auto_thread_cap")
   @require_admin
   def scheduler_get_auto_thread_cap():
       return jsonify(_auto_thread_cap_payload())


   @admin_bp.route("/scheduler/auto_thread_cap", methods=["POST"])
   @require_admin
   def scheduler_set_auto_thread_cap():
       body = request.get_json(silent=True) or {}
       try:
           set_auto_thread_cap(body.get("max_auto_threads"))
       except ValueError as e:
           return jsonify({"error": str(e)}), 400
       return jsonify(_auto_thread_cap_payload())
   ```

   `ASTRAL_CONFIG`, `Dict`, `request`, `jsonify`, `require_admin` are already imported in this file — add no other imports.

⚠️ **Decision:** One path, two view functions split by method (`GET` / `POST`). Same shape as the sibling `/scheduler/*` routes. No `PUT`: AC 3 specifies `POST`, and adding a second verb is surface nobody consumes.

⚠️ **Decision:** POST returns the full GET payload, not just the effective cap. It is a superset of "returns the new effective cap" (Scope), costs one shared helper, and lets AST-1917 reflect the server value without a second GET.

⚠️ **Decision:** The API reads default/bounds from `ASTRAL_CONFIG` directly (ui → utils is allowed by `astral.layers.import-direction`). It reads/writes the override only through the dispatcher's public getter/setter and never touches `_auto_thread_cap_override`.

## Compile / lint (every stage, before commit)

- `python -m py_compile src/utils/config.py src/core/dispatcher.py src/ui/api/api_admin.py`
- Project linter on the touched files (same command build-child §7 uses on this repo); zero new findings.

## Execution contract

Execute stages in order, steps in order. Do not add files, keys, routes, verbs, or log lines beyond this plan. If a referenced line/function has drifted (e.g. `_tick_loop` no longer computes `slots` after a `with _registry_lock:` block, or `ASTRAL_CONFIG` no longer holds `max_auto_threads`), stop and post on the parent:

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

## Acceptance criteria map

| AC | Covered by |
|----|------------|
| 3 API bounds | Stage 2 step 2 validation + Stage 3 400 path |
| 4 Auth | Stage 3 `@require_admin` on both routes |
| 5 Tick honours live cap | Stage 2 step 4 (getter read every tick) |
| 6 No capture-once | Stage 2 step 3 removes `max_auto = ASTRAL_CONFIG...` |
| 7 Lowering non-destructive | Existing `if slots > 0:` guard; setter cancels nothing |
| 8 Single source for bounds | Stage 1 keys; setter + payload read them from `ASTRAL_CONFIG` |
| 9 Restart resets | Override is a module global initialised to `None` |

## Estimate

Confirm Chuckles estimate: 2 — agree
