# AST-1022 — Honor AUTO off for candidate stage dispatch

**Linear:** [AST-1022](https://linear.app/astralcareermatch/issue/AST-1022/honor-auto-off-for-candidate-stage-dispatch-dispatch-running-requested)
**Parent:** [AST-1018](https://linear.app/astralcareermatch/issue/AST-1018/dispatch-running-requested-resume-tasks-despite-the-auto-false)
**Publish ref:** `origin/sub/AST-1018/AST-1022-honor-auto-off-candidate-stage-dispatch`

Candidate stage-dispatch rows (`candidate_requested_resume` / `candidate_requested_artifacts`) were provisioned with AUTO on (AST-972). Operators turn AUTO off in Scheduled Actions expecting CLICK-only, but new seeds keep waking on the tick and any silent re-enable would fight the toggle. This ticket makes the seed default AUTO **off**, keeps existing operator toggles across boot/provision, leaves tick/`get_due_tasks` AUTO filtering intact (CLICK Run still works), and adds Style D debug when a debug-flagged AUTO-off stage row is skipped on the tick.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `auto_mode: False` seed default on each `CANDIDATE_STAGE_DISPATCH` entry | utils |
| `src/core/dispatcher.py` | Read seed `auto_mode` from config in `ensure_candidate_stage_dispatch_tasks`; tick-path Style D skip for AUTO-off + `debug=True` stage rows with available work | core |

**Out of scope:** craft prompts / REQUESTED_* workers; Scheduled Actions UI redesign; unrelated `task_key`s; re-seeding deleted `dispatch_task` rows (AST-745); one-time migration flipping already-seeded AUTO-on rows (operator toggle + new-seed default cover AC); changing `set_dispatch_tasks_from_template_rows` copy semantics (operator-initiated template apply may still copy template `auto_mode` — that is not boot provision).

---

## Diagnosis (code-backed)

1. **Seed hardcodes AUTO on.** `ensure_candidate_stage_dispatch_tasks` in `src/core/dispatcher.py` calls `database.save_dispatch_task(..., auto_mode=True, ...)` for every missing `(task_key, trigger_state)` pair from `CANDIDATE_STAGE_DISPATCH`. That matches AST-972 plan wording and explains AC6 failure for new rows.
2. **Tick already filters AUTO.** `database.get_due_tasks()` selects `WHERE auto_mode = 1`; `_tick_loop` only `run_task`s that list. `run_task(..., ui_initiated=True)` from admin Run does **not** require `auto_mode=1` — CLICK path is already correct for AC3.
3. **Provision does not rewrite existing rows.** `ensure_candidate_stage_dispatch_tasks` skips when `(task_key, trigger_state)` already exists — no `update_dispatch_task` on AUTO. Boot `provision_candidate_stage_dispatch_tasks` only calls ensure. AC5 holds for that path today; do not add writes that flip `auto_mode` on existing rows.
4. **No Style D AUTO-off skip today.** Tick never sees `auto_mode=0` rows, so AC7 needs an explicit debug-only side path for stage keys (not a change to spawn eligibility).

---

## Stage 1: Config seed default + ensure reads it

**Done when:** Both `CANDIDATE_STAGE_DISPATCH` entries declare `auto_mode: False`. A fresh `ensure_candidate_stage_dispatch_tasks(cid)` insert for a candidate missing those rows passes `auto_mode=False` into `save_dispatch_task`. A second ensure on the same candidate still skips existing pairs and does not call `update_dispatch_task` / `save_dispatch_task` for them. `get_due_tasks` SQL and `run_task` CLICK path are unchanged.

1. In `src/utils/config.py`, on `CANDIDATE_STAGE_DISPATCH["requested_resume"]` and `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]`, add the literal key `"auto_mode": False` next to the existing `task_key` / `trigger_state` fields (same bool shape as DB / `save_dispatch_task`).

   ⚠️ **Decision:** Seed default lives in `CANDIDATE_STAGE_DISPATCH` (config source of truth) — do **not** leave a bare `auto_mode=True`/`False` literal only in `dispatcher.py`. Do **not** add a parallel hardcoded set of stage task keys for this default.

2. In `src/core/dispatcher.py` `ensure_candidate_stage_dispatch_tasks`, replace the hardcoded `auto_mode=True` with the entry’s config value:

   ```python
   auto_mode=bool(entry.get("auto_mode", False)),
   ```

   Keep `min_count=1`, `batch_size=1`, `freq_hrs=0`, and the existing skip-if-`(tk, ts) in existing` logic exactly as today. Do **not** update `auto_mode` (or any column) on rows that already exist.

3. Do **not** edit `get_due_tasks`, `_tick_loop` spawn selection (except Stage 2 debug side path), `run_task`, admin AUTO toggle in `api_admin.py`, or React Scheduled Actions for this stage.

---

## Stage 2: Tick Style D skip for AUTO-off stage rows

**Done when:** On a tick, a `dispatch_task` whose `task_key` is one of the two `CANDIDATE_STAGE_DISPATCH[*]["task_key"]` values, with `auto_mode` falsy, `debug` truthy, and `count_eligible_for_dispatch_task(task) >= (min_count or 1)`, emits one Style D `debug_index` plus `|` `debug_detail` naming task_key, candidate_id, available count, and outcome that it was skipped because AUTO is off — and **does not** call `run_task` for that row. Rows with `debug` falsy emit nothing new. AUTO-on due rows still spawn as before.

1. In `src/core/dispatcher.py`, add a private helper (public-then-helpers: place below `_tick_loop` / near other scheduler helpers — if that would put it after a public function that currently sits below, put the helper immediately above `_tick_loop` instead so `_tick_loop` can call it without forward-reference noise):

   Name: `_debug_log_auto_off_stage_skips() -> None`.

   Behavior:
   - Build the frozenset of stage task_keys from `CANDIDATE_STAGE_DISPATCH.values()` → each `entry["task_key"]` (no inline string set of the two keys).
   - Load candidate stage rows for those keys that are AUTO off. Prefer: `database.list_dispatch_tasks()`, filter in Python to `task_key in stage_keys` and `not bool(task.get("auto_mode"))` and `bool(task.get("debug"))`. Do **not** add a new data-layer query unless list filtering is clearly wrong — keep this ticket off `database.py` if list is sufficient.
   - For each matching row with non-empty `entity_type`, `trigger_state`, and `candidate_id`: `avail = database.count_eligible_for_dispatch_task(task)`; if `avail < (task.get("min_count") or 1)`, continue (no log — not a would-have-run skip).
   - When the threshold is met: `logger.set_debug_flag(True)` then:

     ```python
     logger.debug_index(
         func="dispatcher._tick_loop",
         index=1,
         total=1,
         identifier=task.get("task_key"),
         outcome="skipped — AUTO off",
     )
     logger.debug_detail(
         f"candidate_id={task.get('candidate_id')!r} task_id={task.get('id')} "
         f"available={avail} min_count={task.get('min_count') or 1} auto_mode={task.get('auto_mode')}"
     )
     ```

   - Never call `run_task` from this helper.

   ⚠️ **Decision:** Scope debug AUTO-off skips to the two stage task_keys only (`in-scope-only`). Do not log every AUTO-off row in the catalog. Emit only when the row’s own `debug` column is truthy (debug-contract-gated — no new lines when debug is off).

2. In `_tick_loop`, after `due = database.get_due_tasks()` and **before** the spawn loop, call `_debug_log_auto_off_stage_skips()` inside the existing `try` (so failures are covered by the tick’s `except` / `_sched_log.exception`). Do not change `slots` / `run_task` selection logic.

3. Confirm by inspection (no product change required if already true):
   - `get_due_tasks` still `WHERE auto_mode = 1`.
   - Admin Run still uses `run_task(task_id, ui_initiated=True)` without requiring AUTO on.
   - `ensure_candidate_stage_dispatch_tasks` still never updates existing `auto_mode`.

---

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1018/AST-1022-honor-auto-off-candidate-stage-dispatch`.
- Do not edit `tests/`, `docs/test-bible/**`, or `docs/ASTRAL_TEST_BIBLE.md`.
- If `CANDIDATE_STAGE_DISPATCH` shape differs from what Stage 1 assumes, or `list_dispatch_tasks` is unsuitable for Stage 2, **stop** and comment on the **parent** (AST-1018) with the blocking format — do not invent a second seed path or data API.

---

## Self-Assessment

**Scope:** Single-Component — `config.py` seed field + `dispatcher.py` ensure + tick debug helper; no UI/data schema change.

**Conf:** high — smoking gun is the AST-972 `auto_mode=True` seed; tick/`get_due_tasks` already enforce AUTO for spawn; persist-on-provision already skips existing pairs.

**Risk:** Medium — wrong seed default or overly broad tick debug could hide real AUTO-on work or spam logs; mitigated by config-only False default, stage-key filter, and `debug` column gate.

---

## Rules self-review

| Rule | Status |
|------|--------|
| §1.3 DRY / focused helpers | Stage 2 isolates skip logging in one helper; ensure stays insert-only |
| §2.1 config source of truth | `auto_mode` seed on `CANDIDATE_STAGE_DISPATCH`, not a lone dispatcher literal |
| §2.4 batch claim-process-release | Unchanged when a row does run (AUTO on / CLICK) |
| §2.6 state machine | No candidate state changes |
| §1.5.1 debug contract | Style D + `\|` detail only when row `debug` is truthy |
| §1.4 no hardcoded sets | Stage keys from `CANDIDATE_STAGE_DISPATCH`, not inline frozenset of string literals |
| §3.3 import direction | Core already imports data + utils; no new layer violations |
| AST-745 | No re-seed of deleted rows; ensure remains insert-missing only |

---

## Review (build stub)

| Commit | Note |
|--------|------|
| `f0234c4c` | Stage 1 — `CANDIDATE_STAGE_DISPATCH.auto_mode=False`; ensure reads config |
| `de222da4` on `sub/AST-1018/AST-1022-honor-auto-off-candidate-stage-dispatch` | Stage 2 — `_debug_log_auto_off_stage_skips` (Style D index N/M); Code Complete |
