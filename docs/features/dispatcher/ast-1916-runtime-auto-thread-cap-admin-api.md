<!-- linear-archive: AST-1916 archived 2026-10-08 -->

## Linear archive (AST-1916)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1916/runtime-auto-thread-cap-admin-api-add-a-selection-box-on-scheduled  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1875 — add a selection box on Scheduled Tasks to set concurrent tasks limit  
**Blocked by / blocks / related:** parent: AST-1875; blocks: AST-1917

### Description

## What this implements

Makes the scheduler read its concurrency cap live each tick, adds the bounded getter/setter, and exposes them as two admin routes. Ships: cap changes via API take effect on the next tick with no restart; out-of-range values are rejected. Does **not** own the page dropdown (#2).

## Citations

`astral.ui.single-gunicorn-worker`, `astral.config.config-source-of-truth`, `astral.layers.import-direction`, `astral.idioms.require-auth-on-protected-endpoints`, `astral.standards.logging-via-utils`, `astral.standards.in-scope-only`.

## Scope

* `src/core/dispatcher.py` — **modified** — new module-level runtime override for the AUTO thread cap (unset = fall back to `ASTRAL_CONFIG["max_auto_threads"]`), guarded by the existing registry lock or its own lock; new public getter returning the effective cap; new public setter that validates against the config bounds and raises on out-of-range / non-integer input; modified `_tick_loop` so the slot calculation uses the getter every tick (the "captured once at thread start" behaviour for the cap is removed; `tick_rate_minutes` capture is unchanged). The setter does not cancel running threads.
* `src/ui/api/api_admin.py` — **modified** — new admin-protected GET route returning effective cap, config default, and bounds; new admin-protected POST/PUT route that calls the dispatcher setter and returns the new effective cap, or 400 with an error message when the value is rejected. Both under the existing `admin_bp` `/scheduler/` prefix.
* `src/utils/config.py` — **modified** — new min/max bound fields for the AUTO thread cap alongside `max_auto_threads` (values 1 and 100). `max_auto_threads` default itself is unchanged.

## Acceptance criteria

3. **API bounds.** `POST` to the set route with `0`, `101`, `"abc"` or `2.5` each returns 400 and a subsequent GET still reports the prior cap. `POST` with `1` and with `100` each returns 200 and GET reports that value. Fail: any out-of-range value accepted, or an in-range value rejected.
4. **Auth.** Both new routes return 401/403 without an admin session. Fail: 200 unauthenticated.
5. **Tick honours the live cap.** With the cap set to N and more than N AUTO tasks due, after the next tick `GET /api/admin/scheduler/thread_status` shows at most N running entries with `is_auto: true` — and raising the cap to M > N lets the following tick spawn up to M, with no restart. Fail: running AUTO count exceeds the cap, or a change needs a restart to take effect.
6. **No capture-once.** `grep -n 'max_auto = ASTRAL_CONFIG' src/core/dispatcher.py` returns nothing inside `_tick_loop` (the cap is not read once before the `while True`). Fail: the capture-once line survives.
7. **Lowering is non-destructive.** With K AUTO threads running, set the cap below K: none of the K threads is cancelled (all still `running: true` in `thread_status` until they finish on their own) and no new AUTO thread spawns until running AUTO < cap. Fail: any thread killed by the change, or a spawn while at/over cap.
8. **Single source for bounds** (backend half). The dispatcher setter/API validate against the config bound fields. Fail: bounds hardcoded outside `config.py`.
9. **Restart resets.** Set the cap to 7, restart the server: GET reports the `config.py` default again. Fail: 7 survives restart.

## Boundaries

No UI — the Scheduled Actions header dropdown is #2. No persistence (in-memory only, per Susan). No other scheduler knobs (tick rate, DeepSeek concurrency, timeout).

## Notes for planning

Blocks #2 (the dropdown consumes this child's GET/set routes). CLICK (manual Run) threads stay outside the cap, as today.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1875-runtime-auto-thread-cap`, child `sub/AST-1875/AST-1916-runtime-cap-api`. Created at dispatch-parent.

### Comments

#### radia — 2026-10-01T01:47:26.041Z
[code-rubric] PROCEED (Commit: 79ddf0b29) Live cap admin API

#### betty — 2026-10-01T01:44:28.952Z
`origin/sub/AST-1875/AST-1916-runtime-cap-api` @ `79ddf0b29` · 27 tests, manifest in bible

#### betty — 2026-10-01T00:56:51.115Z
@susan — QA held at publish. Tests + bible ready as `83c022c58` (local `betty-bak/AST-1916-runtime-cap-api`; 27 new tests green, no new reds).

Blocked: (1) `validate-tests-branch.sh` fails — `tests-clean-base` marker missing. (2) Normal `merge-tests` from origin/tests would drag AST-1902 `src/core/builder.py` + ast-1014 plan doc into this sub.

Need your call: cherry-pick vs merge-tests vs wait for AST-1902, plus the marker. Staying Code Complete.

#### joan — 2026-10-01T00:50:26.011Z
[plan-rubric] PROCEED (Commit: 1d1b956) Backend cap API plan

#### ada — 2026-10-01T00:49:02.688Z
`origin/sub/AST-1875/AST-1916-runtime-cap-api` @ `1d1b95639` · plan ready, estimate agreed

---

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


## Joan validate

[plan-rubric]
**Ticket:** AST-1916
**Overall:** APPROVED
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Publish ref:** `origin/sub/AST-1875/AST-1916-runtime-cap-api` @ `1d1b9563989e4d8e06b781b60d526b45e7d1b1d1`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| astral.ui.single-gunicorn-worker | A | | |
| astral.config.config-source-of-truth | A | | |
| astral.layers.import-direction | A | | |
| astral.idioms.require-auth-on-protected-endpoints | A | | |
| astral.standards.logging-via-utils | A | | |
| astral.standards.in-scope-only | A | | |

## Traceability

Child AC 3→Stages 2–3; 4→Stage 3; 5→Stage 2 (live `get_auto_thread_cap()` each tick); 6→Stage 2 step 3; 7→Stage 2 (setter + existing `slots > 0` guard); 8→Stage 1 + Stage 2/3 reading bounds from `ASTRAL_CONFIG`; 9→module global `None` override. Parent AC 1–2 N/A (AST-1917 UI). Stages 1–3 trace to parent Purpose items 1–2, 4–5 and backend half of AC 8.

## Findings

**discuss** — Location: ticket `## Scope` vs plan Stage 3  
Ticket Scope still says “POST/PUT”; plan commits to POST only with explicit Decision (AC 3, sibling route shape). Acceptable narrowing; optional Scope wording cleanup on next plan touch so dispatch text matches the contract.

**acceptable** — Location: plan doc (no `## Self-assessment`)  
Other dispatcher plans often carry Scope/Conf/Risk axes; this plan is small and decisions are explicit. Not `!!-NONE` conf; no escalation.

**acceptable** — Location: `astral.idioms.require-auth-on-protected-endpoints`  
Plan names `@require_admin`; statute examples say `@require_auth`. Matches existing `/scheduler/thread_status` and `require_admin` wraps `require_auth` — scored A on intent.

context_tokens≈28000

---

```
[plan-rubric] PROCEED (Commit: 1d1b956) Backend cap API plan
```

## Review (build)

**Built:** `sub/AST-1875/AST-1916-runtime-cap-api` @ `abcd7ca3c`
**Scope:** `max_auto_threads_min`/`_max` in `ASTRAL_CONFIG`; `get_auto_thread_cap()` / `set_auto_thread_cap()` in dispatcher with `_tick_loop` reading the cap every tick; admin `GET`/`POST /api/admin/scheduler/auto_thread_cap`.
**Betty:** dispatcher getter/setter bounds + type rejection (bool, float, str, None), tick slot calc uses live cap, admin route 200/400/401 paths per AC 3–4. No linter is configured in this repo; compile + Flask test-client smoke only.

## Radia review

[code-rubric]
**Ticket:** AST-1916
**Publish ref:** `79ddf0b297045cba227554796d5cd8912b144632` (`origin/sub/AST-1875/AST-1916-runtime-cap-api`)
**Corpus:** `bd68954dc854ca80fca1fc391821dff9ff288a7a`
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| astral.ui.single-gunicorn-worker | A | | |
| astral.config.config-source-of-truth | A | | |
| astral.layers.import-direction | A | | |
| astral.idioms.require-auth-on-protected-endpoints | A | | |
| astral.standards.logging-via-utils | A | | |
| astral.standards.in-scope-only | A | | |

## Column diff vs plan stage

(aligned) — all six ids match Joan’s plan-stage **A** grades.

## Frame diff

- [ ] **Boundaries / Scope wording:** Linear `## Scope` still says “POST/PUT”; shipped surface is **GET + POST** only (matches plan Stage 3 and API contract). Optional description cleanup on next doc touch — not a product change.

(none required for resolve-child product work)

## Findings

**fix-now**

(none)

**discuss**

- **Location:** Linear `## Scope` vs plan + diff (`src/ui/api/api_admin.py`)  
  **Decision:** Whether to edit the ticket description to drop “PUT” so dispatch text matches the POST-only contract.  
  **Default:** Leave description as-is; AST-1917 consumes GET/POST per the plan doc; no API change.

**advisory**

- **sibling test carry:** `tests/component/frontend/pages/test_AdminSessionResumePaste.test.tsx`, `docs/test-bible/frontend/pages.md` — AST-1908 “Save to Candidate” coverage from `merge-tests`; ignore for AST-1916 scoring (per spawn note).
- **Plan fidelity:** Product diff matches `docs/features/dispatcher/ast-1916-runtime-auto-thread-cap-admin-api.md` Stages 1–3 (config bounds, getter/setter + live `_tick_loop` slot math outside `_registry_lock`, admin routes + shared payload helper). AC 6 satisfied: no `max_auto = ASTRAL_CONFIG` in `_tick_loop`. `start_scheduler` still logs config default at boot (plan-explicit).
- **Estimate footprint:** Chuckles estimate **2** — three `src/**` files + plan doc; fits.

## What’s solid

- Bounds and default read from `ASTRAL_CONFIG`; setter validates via `max_auto_threads_min` / `max_auto_threads_max` (AC 8).
- `@require_admin` on both routes (`require_admin` wraps `@require_auth` in `src/ui/auth.py`), consistent with `/scheduler/thread_status`.
- `set_auto_thread_cap` uses `logger` from `get_logger`; strict `type(value) is not int` matches plan.
- Component tests (`TestAst1916AutoThreadCap`, `TestAst1916AutoThreadCapApi`) cover bounds, auth, live tick raise/lower, and config-driven bounds — aligns with child AC 3–7; AC 9 (restart reset) is inherent module-global `None` override.

## Recommended actions (Chuckles / downstream — not Radia)

- Append this artifact to the issue doc; `docs(AST-1916): Radia review — clean`; post slim upshot `--as radia`; move **Tests Passed → Review Posted**; datt **PROCEED** → **User Testing** (no canon fix-now for `resolve-child`).
- Optional: one-line Linear description tweak POST/PUT → POST when editing the parent/child description anyway.

context_tokens≈38000
