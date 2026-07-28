# AST-1000: Restore stage-dispatch provision helper (getting a stack trace on localhost boot)

**Linear:** [AST-1000](https://linear.app/astralcareermatch/issue/AST-1000/restore-stage-dispatch-provision-helper-getting-a-stack-trace-on)
**Parent:** [AST-995](https://linear.app/astralcareermatch/issue/AST-995/getting-a-stack-trace-on-localhost-boot)
**Publish ref:** `sub/AST-995/AST-1000-restore-stage-dispatch-provision-helper`

Boot-time stage-dispatch provisioning (AST-972) still calls `database.list_candidate_ids_with_dispatch_tasks()` from `provision_candidate_stage_dispatch_tasks`, but that data-layer helper was dropped when AST-973 rewrote `src/data/database.py`. Restore the listing contract so localhost scheduler start no longer AttributeErrors / logs `AST-972 stage dispatch provision failed` for a missing attribute.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Restore public `list_candidate_ids_with_dispatch_tasks()` between `list_dispatch_tasks_for_candidate` and `count_dispatch_tasks_by_candidate` | data |

**Not touched:** `src/core/dispatcher.py` (caller + `start_scheduler` try/except already correct), `src/utils/config.py`, AST-973 migration helpers / `CANDIDATE_LEGACY_*`, craft/claim/resolve paths, Stytch/Vite, `tests/` / bible (Betty owns those; existing component tests already assert this contract).

## Stage 1: Restore listing helper

**Done when:** `hasattr(database, "list_candidate_ids_with_dispatch_tasks")` is true; calling it returns a `list[str]` of distinct non-empty `dispatch_task.candidate_id` values ordered ASC (empty list when none); `python -m compileall` on the touched file is clean. No dispatcher edits.

1. In `src/data/database.py`, immediately after `list_dispatch_tasks_for_candidate` and before `count_dispatch_tasks_by_candidate`, add exactly this public function (AST-972 contract from commit `2ce7a744` / `ae2d18ab` — restore, do not redesign):

   ```python
   def list_candidate_ids_with_dispatch_tasks() -> List[str]:
       """Distinct candidate_id values that already own ≥1 dispatch_task row."""
       def _with_conn() -> List[str]:
           conn = _get_connection()
           try:
               _ensure_dispatch_task_schema(conn)
               rows = conn.execute(
                   "SELECT DISTINCT candidate_id FROM dispatch_task "
                   "WHERE candidate_id IS NOT NULL AND TRIM(candidate_id) != '' "
                   "ORDER BY candidate_id ASC"
               ).fetchall()
               return [str(r[0]) for r in rows if r[0] is not None]
           finally:
               conn.close()
       return _run_with_retry(_with_conn)
   ```

2. Do **not** change the header table inventory unless `dispatch_task` is somehow missing (it is already listed). Do **not** add logging in the data layer (§1.5 — raise only; dispatcher already logs provision failures).

3. Do **not** edit `ensure_candidate_stage_dispatch_tasks`, `provision_candidate_stage_dispatch_tasks`, or `start_scheduler` — they already call this helper and catch exceptions with `_sched_log.exception("AST-972 stage dispatch provision failed")`.

4. Do **not** alter AST-973 behavior: leave `_legacy_candidate_migrate_conn`, `hard_delete_candidate`, `CANDIDATE_LEGACY_STATE_MAP` / trigger remaps, and ensure-time BC migration untouched.

5. Compile check: `python -m compileall -q src/data/database.py`. Fix only syntax/import errors introduced by this restore.

⚠️ **Decision:** Exact restore of the AST-972 SQL + `_run_with_retry` / `_ensure_dispatch_task_schema` wrapper rather than deriving ids from `count_dispatch_tasks_by_candidate().keys()`. Matches existing component contract (`tests/component/data/database/test_dispatch_tasks.py::test_list_candidate_ids_with_dispatch_tasks`) and the dispatcher monkeypatch surface; no new API shape.

**Commit message:** `code(AST-1000): restore list_candidate_ids_with_dispatch_tasks`

## Out of scope

- Redesigning candidate state machine (AST-871) or reopening AST-972 / AST-973 product scope
- Changing REQUESTED_* claim/resolve, craft prompts, or eligibility counts
- Stytch, Vite, unrelated boot messages
- Writing or patching `tests/` / `docs/test-bible/**` (engineer does not own the test tree; existing coverage already names this helper)

## Acceptance mapping

| AC | How this plan satisfies it |
|----|----------------------------|
| 1–2 | Attribute restored → provision path no longer AttributeErrors → no provision-failed traceback from that cause |
| 3 | Helper returns candidates that own ≥1 `dispatch_task` row; provision iterates them via existing `ensure_*` |
| 4 | Empty DISTINCT result → empty for-loop; scheduler thread still starts after the try/except |
| 5 | Existing tests that call / monkeypatch `list_candidate_ids_with_dispatch_tasks` regain a real attribute (Betty/test-child verify green) |

## Self-Assessment

**Scope:** minor — one public data-layer listing function restored next to existing `dispatch_task` list helpers; no core/UI/config changes.

**Conf:** high — caller and SQL contract already shipped under AST-972; git history preserves the exact implementation dropped by AST-973’s `database.py` rewrite.

**Risk:** low — additive restore of a missing attribute; wrong SQL would only affect which candidates get REQUESTED_* upsert at boot, not claim/resolve paths; empty DB remains safe.

## Code rules check

| Rule | Plan alignment |
|------|----------------|
| §1.3 DRY | Reuse `_ensure_dispatch_task_schema`, `_get_connection`, `_run_with_retry`; no parallel query helpers |
| §1.5 data raises / caller logs | No logging in restore; dispatcher provision try/except unchanged |
| §2.1 config SSoT | No new state sets or config keys |
| §2.4 batch | Listing only; claim/clear patterns untouched |
| §2.6 state machine | No state transitions |
| §3.3 imports | Data layer only; no new cross-layer imports |
| §3.5 / public-then-helpers | Placed with other public `dispatch_task` list APIs |

## Review (build stub)

**Built:** `origin/sub/AST-995/AST-1000-restore-stage-dispatch-provision-helper` @ `64a30851e469613f3e8e7e0b36e644d951afed54`.

**Stages delivered:**
- Stage 1: restore `list_candidate_ids_with_dispatch_tasks` in `src/data/database.py` — `64a30851e469613f3e8e7e0b36e644d951afed54`.

## Review (Radia — code-rubric.v1)

`[code-rubric] revision=1`

**Rubric:** code-rubric.v1  
**Ticket:** AST-1000  
**Publish ref:** `ffe47510942ce0acd50098fc02f6eadb0724c590` (`origin/sub/AST-995/AST-1000-restore-stage-dispatch-provision-helper`)  
**Overall:** DISCUSS

**Diff change set:** `src/data/database.py` (modify/data); `docs/features/foundation/ast-1000-restore-stage-dispatch-provision-helper.md` (add/docs); `docs/test-bible/data/database/dispatch_tasks.md` + `tests/component/data/database/test_dispatch_tasks.py` (modify/docs via Betty `merge-tests`).

### What’s solid

- Exact AST-972 body restored between `list_dispatch_tasks_for_candidate` and `count_dispatch_tasks_by_candidate` (byte-match to plan Stage 1).
- Data raises only — no data-layer logging; dispatcher provision caller untouched.
- Header inventory already lists `dispatch_task`; no new table.
- Engineer `code()` touched only `src/data/database.py`; bible/tests arrived via `merge-tests`.

### Findings

**discuss (C4 straggler):** `astral.debug.spikes-under-debug-dir` — Joan excluded (plan Files Changed = data only); three-dot diff includes `docs/features/**`. Re-score: **conforms** (plan doc is not a spike under `debug/`).

**discuss (C4 straggler):** `astral.docs.features-single-file-per-ticket` — Joan excluded; plan file is in the diff. Re-score: **conforms** (single `ast-1000-…` features file).

**discuss (C4 straggler):** `astral.git.engineer-test-tree-ban` — Joan excluded (plan said engineer would not touch tests); three-dot includes `tests/**` + `docs/test-bible/**` from Betty `merge-tests`. Re-score: **conforms** (engineer `code()` commit is src-only).

No fix-now. No product action required for the stragglers unless Archie wants plan-time exclusion notes refined for pipeline docs/tests paths.

### Recommended actions

- Implementer (`resolve-child`): acknowledge stragglers; no code change expected for CLEAN product restore.

## Resolution (2026-07-28 — resolve-child, Ada)

**Radia Overall:** DISCUSS (C4 stragglers only). **fix-now:** 0.

**Discuss handled:**
- Acknowledged three C4 stragglers (`astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`) — already re-scored **conforms** in Radia review; pipeline docs/tests paths vs plan-time product Files Changed, not product defects.
- No product code changes; no plan-time exclusion refinements (Archie did not ask).

**Publish tip after resolve:** see commit subject `resolve(AST-1000): — clean`.

**Tip rebuild (2026-07-28):** Restacked on `origin/ftr/AST-995-localhost-boot-stack-trace` for validate-sub-log (removed `Merge remote-tracking` / foreign AST-996..998 history; `plan()` subject; single `merge-tests` from `1150959778d4cfe0301a40cd280decb0a15ea0da`; empty `test()` — no product fixes).
