# AST-1875 — add a selection box on Scheduled Tasks to set concurrent tasks limit

<!-- linear-archive: AST-1875 archived 2026-10-08 -->

## Linear archive (AST-1875)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1875/add-a-selection-box-on-scheduled-tasks-to-set-concurrent-tasks-limit  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 3  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

The dispatcher caps how many AUTO task threads run at once (`max_auto_threads` in `src/utils/config.py`, today 3), and that cap is read once when the scheduler thread starts — changing it means a code edit plus a redeploy. Susan wants to tune throughput live from the Scheduled Actions page so she can watch how the system behaves at different concurrency levels and pick a sane default from real evidence rather than guesswork.

## Functional scope

1. **Runtime concurrency cap.** The scheduler honours an operator-set cap on concurrent AUTO task threads that can change while the server is running; with no override set, it uses the `config.py` default exactly as today.
2. **Read / set the cap over the admin API.** An admin can read the current effective cap (and the `config.py` default) and set a new whole-number value between 1 and 100 inclusive; anything else is rejected and the cap is unchanged.
3. **Header dropdown on Scheduled Actions.** The Scheduled Actions page header shows a dropdown (1–100, step 1) pre-selected to the current effective cap (the `config.py` default until changed). Picking a value applies it immediately via the API. (Susan confirmed the cap is `max_auto_threads`, not `DEEPSEEK_CONCURRENCY.max_concurrent`.)
4. **Lowering below the running count is non-destructive.** If the cap is lowered below the number of AUTO threads already running, nothing is killed; the scheduler simply spawns no new AUTO threads until the running count drops below the new cap. CLICK (manual Run) threads stay outside the cap, as today.
5. **Override is process-local.** The override lives in memory in the single gunicorn worker (see `astral.ui.single-gunicorn-worker`); a restart or deploy returns to the `config.py` default. (Susan confirmed: no persistence — once testing finds a good number, `max_auto_threads` in `config.py` gets updated by a normal change.)

## Component scope

* `src/core/dispatcher.py` — **modified** — tick loop reads the cap each tick from a runtime value instead of capturing it once at thread start; module gains the get/set surface for that value.
* `src/ui/api/api_admin.py` — **modified** — admin routes to read and set the cap, next to the existing `/scheduler/thread_status` and `/scheduler/stop_all` routes.
* `src/utils/config.py` — **modified** — bounds for the cap (min 1, max 100) live beside `max_auto_threads` so dispatcher, API and UI share one source.
* `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — **modified** — header dropdown in the `list-page-header` controls cluster (beside the "N running" badge / Stop All / + Add Task).

## Technical scope

* `src/core/dispatcher.py` — new module-level runtime override for the AUTO thread cap (unset = fall back to `ASTRAL_CONFIG["max_auto_threads"]`), guarded by the existing registry lock or its own lock; new public getter returning the effective cap; new public setter that validates against the config bounds and raises on out-of-range / non-integer input; modified `_tick_loop` so the slot calculation uses the getter every tick (the "captured once at thread start" behaviour for the cap is removed; `tick_rate_minutes` capture is unchanged). The setter does not cancel running threads.
* `src/ui/api/api_admin.py` — new admin-protected GET route returning effective cap, config default, and bounds; new admin-protected POST/PUT route that calls the dispatcher setter and returns the new effective cap, or 400 with an error message when the value is rejected. Both under the existing `admin_bp` `/scheduler/` prefix.
* `src/utils/config.py` — new min/max bound fields for the AUTO thread cap alongside `max_auto_threads` (values 1 and 100). `max_auto_threads` default itself is unchanged.
* `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — new state + load of the cap from the GET route on page load; new `<select>` in the header whose options are generated from the returned bounds (no hardcoded 1/100 in the component); change handler posts to the set route and reflects the server-returned value (reverts on error).

## Architectural definition

**Patterns to reuse**

* no established pattern applies — none of the active `patt.*` directives (artifact, entity batch, task daisy-chain / dispatch-retry) cover runtime operator overrides of scheduler knobs.

**New patterns proposed**

* none

**Applicable statutes**

* `astral.ui.single-gunicorn-worker` — an in-memory override is only coherent because there is exactly one scheduler/registry per deploy. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/ui/astral.ui.single-gunicorn-worker.md>)
* `astral.config.config-source-of-truth` — the default and the 1–100 bounds live in `config.py`; no second copy in dispatcher, API or TSX. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>)
* `astral.layers.ui-config-driven-business-logic` — dropdown range comes from the API/config, not literals in the page. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.ui-config-driven-business-logic.md>)
* `astral.layers.import-direction` — ui → core; API calls the dispatcher's public getter/setter, never pokes module globals. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md>)
* `astral.idioms.require-auth-on-protected-endpoints` — both new routes carry `@require_admin` like their `/scheduler/*` siblings. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/idioms/astral.idioms.require-auth-on-protected-endpoints.md>)
* `astral.standards.logging-via-utils` — cap-change log line (if any) goes through the project logger. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.logging-via-utils.md>)
* `astral.ui.frontend-file-placement` — control stays inside the existing page file; no new component unless the plan justifies it. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/ui/astral.ui.frontend-file-placement.md>)
* `astral.standards.in-scope-only` — no persistence table, no other scheduler knobs (tick rate, DeepSeek concurrency, timeout) in this epic. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>)
* Universal orchestration set (`orch.pipeline.*`, `orch.git.*`, `orch.roles.*`) applies to delivery mechanics as usual.

## Acceptance criteria

1. **Default shown.** Fresh server start, open Scheduled Actions: header dropdown shows the value of `ASTRAL_CONFIG["max_auto_threads"]` (3 today). Fail: any other value, or no dropdown.
2. **Range.** The dropdown offers exactly the integers 1..100 (100 options, first 1, last 100). Fail: missing/extra options or non-integer steps.
3. **API bounds.** `POST` to the set route with `0`, `101`, `"abc"` or `2.5` each returns 400 and a subsequent GET still reports the prior cap. `POST` with `1` and with `100` each returns 200 and GET reports that value. Fail: any out-of-range value accepted, or an in-range value rejected.
4. **Auth.** Both new routes return 401/403 without an admin session. Fail: 200 unauthenticated.
5. **Tick honours the live cap.** With the cap set to N and more than N AUTO tasks due, after the next tick `GET /api/admin/scheduler/thread_status` shows at most N running entries with `is_auto: true` — and raising the cap to M > N lets the following tick spawn up to M, with no restart. Fail: running AUTO count exceeds the cap, or a change needs a restart to take effect.
6. **No capture-once.** `grep -n 'max_auto = ASTRAL_CONFIG' src/core/dispatcher.py` returns nothing inside `_tick_loop` (the cap is not read once before the `while True`). Fail: the capture-once line survives.
7. **Lowering is non-destructive.** With K AUTO threads running, set the cap below K: none of the K threads is cancelled (all still `running: true` in `thread_status` until they finish on their own) and no new AUTO thread spawns until running AUTO < cap. Fail: any thread killed by the change, or a spawn while at/over cap.
8. **Single source for bounds.** `grep -rn '\b100\b' src/ui/frontend/src/pages/AdminScheduledActions.tsx` shows no literal used as the dropdown max, and the dispatcher setter/API validate against the config bound fields. Fail: bounds hardcoded outside `config.py`.
9. **Restart resets.** Set the cap to 7, restart the server: GET reports the `config.py` default again. Fail: 7 survives restart.

## Open questions

none

## Proposed child tickets

#### 1!: **Runtime AUTO-thread cap + admin API - Ada**

Makes the scheduler read its concurrency cap live each tick, adds the bounded getter/setter, and exposes them as two admin routes. Ships: cap changes via API take effect on the next tick with no restart; out-of-range values are rejected. Does **not** own the page dropdown (#2).
**Citations:** `astral.ui.single-gunicorn-worker`, `astral.config.config-source-of-truth`, `astral.layers.import-direction`, `astral.idioms.require-auth-on-protected-endpoints`, `astral.standards.logging-via-utils`, `astral.standards.in-scope-only`.
**Scope:**

* `src/core/dispatcher.py` — **modified** — new module-level runtime override for the AUTO thread cap (unset = fall back to `ASTRAL_CONFIG["max_auto_threads"]`), guarded by the existing registry lock or its own lock; new public getter returning the effective cap; new public setter that validates against the config bounds and raises on out-of-range / non-integer input; modified `_tick_loop` so the slot calculation uses the getter every tick (the "captured once at thread start" behaviour for the cap is removed; `tick_rate_minutes` capture is unchanged). The setter does not cancel running threads.
* `src/ui/api/api_admin.py` — **modified** — new admin-protected GET route returning effective cap, config default, and bounds; new admin-protected POST/PUT route that calls the dispatcher setter and returns the new effective cap, or 400 with an error message when the value is rejected. Both under the existing `admin_bp` `/scheduler/` prefix.
* `src/utils/config.py` — **modified** — new min/max bound fields for the AUTO thread cap alongside `max_auto_threads` (values 1 and 100). `max_auto_threads` default itself is unchanged.

Estimate: 2

#### 2: **Scheduled Actions header dropdown - Hedy**

After #1. Adds the 1–100 dropdown to the Scheduled Actions header, pre-selected to the live cap from #1's GET route, applying changes through #1's set route. Does **not** own validation or scheduler behaviour (#1).
**Citations:** `astral.layers.ui-config-driven-business-logic`, `astral.ui.frontend-file-placement`, `astral.config.config-source-of-truth`.
**Scope:**

* `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — **modified** — new state + load of the cap from the GET route on page load; new `<select>` in the header whose options are generated from the returned bounds (no hardcoded 1/100 in the component); change handler posts to the set route and reflects the server-returned value (reverts on error).

Estimate: 1

**New patterns:** none.

**Monolith check:** Functional scope N = 5, children M = 2 — backend (scheduler + API) and UI split along the layer line.

**Scope partition check:** all four Component scope files claimed exactly once (dispatcher / api_admin / config → #1; AdminScheduledActions.tsx → #2).

---

## Original brief

Add to the header a dropdown  that defaults to the cap set in [config.py](<http://config.py>) so I can change the limit at runtime and validate performance.  Minimum is 1, maximum is 100, increments of 1.

### Comments

#### chuckles — 2026-10-01T02:01:00.914Z
@susan before you merge PR #202:

- **Merge after AST-1899 lands, or ask Betty to strip it.** Through shared `origin/tests`, this PR picked up AST-1908's Vitest file `tests/component/frontend/pages/test_AdminSessionResumePaste.test.tsx` and a `frontend/pages.md` bible block. Its 7 cases fail on this branch because AST-1899's Save to Candidate change isn't on dev yet. Everything else passes (93 of 100 in that Vitest run).
- **AST-1911 heads-up.** While cleaning the shared tests checkout, Betty moved AST-1911's unpublished commit `f0000cf10` to local branch `betty-bak/tests-pre-AST-1916-20261001` in astral-tests.

#### chuckles — 2026-10-01T00:58:08.058Z
@susan no new call needed. Your AST-1913 decision covers this one too: wait for AST-1902 to land on dev, then restore `tests-clean-base` at `82423d73b` if it's still missing. AST-1913 now blocks AST-1916 and AST-1875. Betty's `83c022c58` stays parked on `betty-bak/AST-1916-runtime-cap-api`, and she'll publish it with a normal `merge-tests` once AST-1913 is Done.

#### chuckles — 2026-10-01T00:57:26.383Z
@susan AST-1916 REVIEW — Betty qa-child held at publish: `tests-clean-base` marker missing (validate-tests-branch.sh) and merge-tests from origin/tests would drag AST-1902 code; needs your call on the AST-1916 thread (cherry-pick vs merge vs wait, plus marker).

#### chuckles — 2026-10-01T00:44:10.864Z
@susan

1. **Linear project** — still unset, and dispatch can't create children without one. Please set it on the ticket (probably **Astral Dispatcher**); then it's ready for Todo + Chuckles.

#### chuckles — 2026-09-29T19:12:55.963Z
@susan

- **Missing Linear project** on the parent — dispatch can't create children without one (they'd be project-less). Likely **Astral Dispatcher** (sibling AST-1829 lives in `docs/features/dispatcher/`). Set the project, then back to Todo + Chuckles.
- Your inline answers to both open questions are folded in as-is — nothing else outstanding.

#### chuckles — 2026-09-29T18:45:55.781Z
@susan

1. **Which cap?** I read "concurrent tasks limit" as the dispatcher's `max_auto_threads` (AUTO Scheduled Actions threads running at once, default **3**; manual Run/CLICK threads aren't counted). The other candidate is `DEEPSEEK_CONCURRENCY.max_concurrent` (**20**, DeepSeek calls in flight across all threads) — your 1–100 range fits that one a bit better. Which should the dropdown control?
2. **Survive restart/deploy?** Draft assumes no — in-memory override for perf testing, restart falls back to `config.py`. Persisting it adds a DB setting and scope.

---

_Implementation detail may live in git history on `origin/dev`._
