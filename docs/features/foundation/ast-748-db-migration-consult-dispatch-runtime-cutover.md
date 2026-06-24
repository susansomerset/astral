<!-- linear-archive: AST-748 archived 2026-06-23 -->

## Linear archive (AST-748)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-748/db-migration-and-consult-dispatch-runtime-cutover-task-keys-vs  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-736 — Task keys vs. dispatch task keys  
**Blocked by / blocks / related:** parent: AST-736

### Description

## What this implements

Ship idempotent DB rename of existing `dispatch_task` rows from `consult_*` to `grade_*` under triple-unique constraint, and update consult/dispatcher runtime so manual Run, AUTO dispatch, and Execution History record `grade_do` / `grade_get` / `grade_like` with no consult alias layer post-cutover.

## Acceptance criteria

1. Susan can create and run a `grade_do` dispatch row at `PASSED_JD` (and `PASSED_JD_RETRY` where used) with no `consult_do` row or alias required.
2. After migration, existing environments show **zero** `dispatch_task` rows with `task_key` in `{consult_do, consult_get, consult_like}`; equivalent `grade_*` rows preserve scheduling fields (`freq_hrs`, `batch_size`, `debug`, `AUTO`, etc.).
3. Manual Run and AUTO dispatch for those rows execute the same graded consult batches as today; Execution History first-hop Task column shows `grade_do` / `grade_get` / `grade_like`.

## Boundaries

* Does **not** own config schedulable-key catalog changes — blocked on sibling **AST-737**.
* Does **not** own Scheduled Actions UI phase grouping — sibling Katherine ticket.
* Does **not** backfill historical `dispatch_ledger` alias strings.

## Notes for planning

* Primary: `src/data/database.py` (migration), `src/core/consult.py`, `src/core/dispatcher.py`.
* Preserve **AST-534** row `task_key` drives entry; remove consult-only routing assumptions.
* Migration must be idempotent on deploy.

## Git branch (authoritative)

Parent `ftr/ast-736-task-keys-vs-dispatch-task-keys`, child `sub/AST-736/AST-738-db-migration-consult-dispatch-runtime-cutover`.

### Comments

#### radia — 2026-06-23T19:40:29.357Z
## Radia review (AST-748)

**Diff:** `origin/dev...origin/sub/AST-736/AST-748-db-migration-consult-dispatch-runtime-cutover` @ `d6949be`
**Doc:** `docs/features/foundation/ast-748-db-migration-consult-dispatch-runtime-cutover.md` (Review Radia section)

**AST-748 commits:** `bf8eaa3`, `61eaf25`, `27d950d`. Publish ref rolls up resolved **AST-747** / sibling qa — not in Hedy product commits (§5d clean).

### What's solid

- **Stage 1:** Migration block matches plan — collision DELETE then UPDATE; local rename tuple; triple-unique safe.
- **Stage 2:** Zero `consult_*` in `consult.py` / `dispatcher.py`; `_consult_orchestration` → `TASK_CONFIG[tk]`; `grade_*_batch` entrypoints; `run_consult_task` + `_CHUNK_EXHAUST_CONSULT_JOB_KEYS` cutover.
- **§2.7:** `agent_task` fallback to dispatch key — Execution History attribution `grade_*` (intended AST-736).
- **Tests:** `TestAst748ConsultToGradeDispatchMigration` (rename + collision); consult/dispatcher manifest on `grade_*`.

### fix-now

None.

### Recommended

**resolve-child** — no code changes from review. Susan UAT: legacy `consult_*` rows renamed on staging; Run/AUTO graded hops show `grade_*` in Execution History.

#### betty — 2026-06-23T19:38:07.262Z
## QA test manifest (AST-748)

**Publish:** `origin/sub/AST-736/AST-748-db-migration-consult-dispatch-runtime-cutover` @ `13352e9` (`merge-tests(AST-748): origin/tests 27d950d`)

**Run (narrowed — 9 pytest):**
```bash
./scripts/testing/run_component_tests.sh   tests/component/data/database/test_dispatch_tasks.py::TestAst748ConsultToGradeDispatchMigration   tests/component/core/test_consult.py::TestRunConsultTask::test_ast503_routes_two_passed_jd_jobs_to_grade_do_batch   tests/component/core/test_consult.py::TestAst534DispatchTaskKeyHonesty   tests/component/core/test_dispatcher.py::TestRunUnified::test_uses_default_score_floor_for_scored_states   -q
```

1. `tests/component/data/database/test_dispatch_tasks.py` — `TestAst748ConsultToGradeDispatchMigration` (consult_*→grade_* schema rename + duplicate-row delete when grade triple exists)
2. `tests/component/core/test_consult.py` — `test_ast503_routes_two_passed_jd_jobs_to_grade_do_batch` (PASSED_JD → `grade_do_batch`)
3. `tests/component/core/test_consult.py` — `TestAst534DispatchTaskKeyHonesty` (dispatch keys `grade_do` / `grade_get` / `grade_like`; no `consult_*` routing)
4. `tests/component/core/test_dispatcher.py` — `test_uses_default_score_floor_for_scored_states` (`task_key: grade_do`)

**Bible shasum (`origin/sub/…` @ `13352e9`):**
- `docs/test-bible/core/consult.md` — `f2d355cb7f2d6ac0bc0a01643d9234274faaad8dedaf1569a1ec56a623859dfb`
- `docs/test-bible/core/dispatcher.md` — `e4f433654a47cc56d2562ce33599aaab0a9724be629f9356048e2e3f5a304268`
- `docs/test-bible/data/database/dispatch_tasks.md` — `191ce4ccfc6351d8f08ea4b7e0c504b47819830cfe897832bcca0fb5503565d1`

**Out of manifest (sibling integration):** full `test_consult.py` zero-arg harness; `test_roster.py` ledger dedup tests retain legacy `consult_*` strings in historical `agent_response` fixtures until roster cutover sibling lands.

— Betty

#### hedy — 2026-06-23T19:33:21.907Z
Plan: [docs/features/foundation/ast-748-db-migration-consult-dispatch-runtime-cutover.md](https://github.com/susansomerset/astral/blob/sub/AST-736/AST-748-db-migration-consult-dispatch-runtime-cutover/docs/features/foundation/ast-748-db-migration-consult-dispatch-runtime-cutover.md) on `origin/sub/AST-736/AST-748-db-migration-consult-dispatch-runtime-cutover` @ `1adffe5`.

**Self-assessment**
- **Scope:** Single-Component — `database.py` consult→grade row migration, `consult.py` graded routing, `dispatcher.py` chunk-exhaustion frozenset.
- **Conf:** high — AST-703-style DELETE-before-UPDATE collision pattern; runtime is string rename + drop `resolve_dispatch_task_config_key` in consult.
- **Risk:** HIGH — migration `IntegrityError` bricks Scheduled Actions; wrong `agent_task` breaks `render_verdict` / timesheet attribution for graded hops.

---

# AST-748 — DB migration and consult dispatch runtime cutover

- **Linear (this ticket):** [AST-748](https://linear.app/astralcareermatch/issue/AST-748/db-migration-and-consult-dispatch-runtime-cutover-task-keys-vs-dispatch)
- **Parent:** [AST-736](https://linear.app/astralcareermatch/issue/AST-736/task-keys-vs-dispatch-task-keys)
- **Publish ref:** `origin/sub/AST-736/AST-748-db-migration-consult-dispatch-runtime-cutover`

## Summary

Ship an idempotent `dispatch_task` row rename from retired `consult_do` / `consult_get` / `consult_like` to `grade_do` / `grade_get` / `grade_like` under the triple-unique constraint, then cut over consult and dispatcher runtime so manual Run, AUTO dispatch, batch exhaustion, and Execution History first-hop Task attribution use `grade_*` strings with no consult alias layer. **AST-534** preserved: row `task_key` drives entry; `trigger_state` claims only.

**Sibling scope (do not implement here):** Config schedulable vocabulary and admin retired-key guard (**AST-747**, Ada — prerequisite); Scheduled Actions React UI (**AST-749**, Katherine).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Idempotent `consult_*` → `grade_*` migration in `_ensure_dispatch_task_schema` | data |
| `src/core/consult.py` | Runtime cutover: `grade_*` routing, orchestration without alias resolver, batch entry renames | core |
| `src/core/dispatcher.py` | `_CHUNK_EXHAUST_CONSULT_JOB_KEYS` → `grade_*` | core |

**Out of scope (sibling tickets — do not touch):**

| Ticket | Owner | Scope |
|--------|-------|-------|
| AST-747 | Ada | `DISPATCH_SCHEDULABLE_TASK_KEYS`, admin API, `resolve_dispatch_task_config_key` identity, retired-key messages |
| AST-749 | Katherine | Scheduled Actions React grouping UI |
| Betty | Betty | `tests/component/core/test_consult.py`, `test_dispatcher.py`, `test_config.py`, `test_api_admin.py`; `docs/test-bible/core/consult.md`, `dispatcher.md` |

**QA manifest (Betty — not engineer commits):** Update consult/dispatcher component tests still passing `consult_*` as `dispatch_task_key`; bible runtime wording when **AST-748** lands (**AST-747** plan integration note).

## Prerequisite (build gate — not a commit stage)

**Done when:** Epic worktree includes **AST-747** config cutover (`grade_*` in schedulable frozensets; `consult_*` in `DISPATCH_RETIRED_TASK_KEYS`; identity `resolve_dispatch_task_config_key`) — merge `origin/sub/AST-736/AST-747-config-schedulable-keys-retire-consult-aliases` or equivalent on `origin/ftr/ast-736-task-keys-vs-dispatch-task-keys` before **build-child** Stage 2.

⚠️ **Decision:** Do **not** edit `src/utils/config.py`, `src/core/bootstrap.py`, `src/ui/api/api_admin.py`, or rules docs in this ticket — **AST-747** owns schedulable vocabulary.

## Stage 1: Database — idempotent `consult_*` → `grade_*` row rename

**Done when:** `_ensure_dispatch_task_schema` leaves **zero** rows with `task_key IN ('consult_do','consult_get','consult_like')`; existing `grade_*` rows at the same `(candidate_id, trigger_state)` triple survive with scheduling fields preserved; manual throwaway DB with both legacy and target rows migrates without `IntegrityError`.

1. In `src/data/database.py`, near the existing idempotent migrations at the end of `_ensure_dispatch_task_schema` (after AST-702 prefilter block, **before** `_ensure_gaze_board_dispatch_tasks(conn)` and `_dispatch_task_schema_ensured = True`), add block:

```python
    # AST-736 / AST-748: retire consult_* dispatch row keys → grade_* (triple-unique safe).
    _CONSULT_TO_GRADE_DISPATCH_KEYS = (
        ("consult_do", "grade_do"),
        ("consult_get", "grade_get"),
        ("consult_like", "grade_like"),
    )
    for retired_key, grade_key in _CONSULT_TO_GRADE_DISPATCH_KEYS:
        # Drop legacy row when canonical grade_* row already exists for same triple.
        conn.execute(
            """
            DELETE FROM dispatch_task AS d
            WHERE d.task_key = ?
              AND EXISTS (
                SELECT 1 FROM dispatch_task AS g
                WHERE g.candidate_id = d.candidate_id
                  AND g.task_key = ?
                  AND g.trigger_state = d.trigger_state
              )
            """,
            (retired_key, grade_key),
        )
        conn.execute(
            "UPDATE dispatch_task SET task_key = ? WHERE task_key = ?",
            (grade_key, retired_key),
        )
    conn.commit()
```

2. Do **not** import `_RETIRED_DISPATCH_TASK_KEY_REPLACEMENTS` from config — keep the tuple local in the migration block (data already imports `dispatch_task_admin_defaults`; avoid widening the import surface for a one-time rename).

3. Manual verification on epic worktree (throwaway SQLite — do **not** commit):

   - Create `dispatch_task` with triple unique matching greenfield schema in `_ensure_dispatch_task_schema`.
   - **Case A — rename only:** one row `consult_do` / `PASSED_JD` with `freq_hrs=4`, `batch_size=8`, `auto_mode=1`; after `_ensure_dispatch_task_schema`, row has `task_key='grade_do'` and scheduling columns unchanged.
   - **Case B — collision:** rows `consult_do`/`PASSED_JD` and `grade_do`/`PASSED_JD` for same `candidate_id`; after ensure, exactly one `grade_do`/`PASSED_JD` row remains (the pre-existing `grade_*` row); `consult_*` row deleted.
   - **Case C — retry trigger:** row `consult_get` / `PASSED_DO_RETRY` renames to `grade_get` / `PASSED_DO_RETRY` when no collision.
   - `SELECT COUNT(*) FROM dispatch_task WHERE task_key IN ('consult_do','consult_get','consult_like')` → **0**.

⚠️ **Decision:** When both legacy and canonical rows exist for the same triple, **delete the `consult_*` row** — do not merge scheduling fields. Susan's canonical row (`grade_*`) wins; duplicate legacy rows are migration debris after **AST-747** admin rejects new `consult_*` saves.

## Stage 2: Runtime — consult + dispatcher `grade_*` cutover

**Done when:** `grep -E 'consult_do|consult_get|consult_like' src/core/consult.py src/core/dispatcher.py` returns **zero** matches (module docstring may mention historical consult outcomes in prose — update docstrings to `grade_*`); `run_consult_task(..., dispatch_task_key='grade_do')` routes DO batch path; `dispatcher._CHUNK_EXHAUST_CONSULT_JOB_KEYS` contains `grade_do` not `consult_do`; `render_verdict('grade_do', ...)` runs without `KeyError` on `agent_task`.

1. In `src/core/consult.py`, update module docstring lines that describe `consult_do → grade_do via _consult_orchestration` — graded consult dispatch and `TASK_CONFIG` share one string (**AST-736**).

2. Replace `_consult_orchestration` body:

```python
def _consult_orchestration(task_key: str) -> Dict[str, Any]:
    """Return TASK_CONFIG orchestration for dispatch/catalog task_key (same string after AST-736)."""
    tk = (task_key or "").strip()
    return TASK_CONFIG[tk]
```

Remove `resolve_dispatch_task_config_key` from imports if unused after edits.

3. In `_INPUT_STATE_TO_TASK`, replace consult entries with grade keys:

```python
    "PASSED_JD":          "grade_do",
    "PASSED_DO":          "grade_get",
    "PASSED_GET":         "grade_like",
```

Keep comment: `# Legacy map — not used for dispatch routing (AST-534). Tests pass dispatch_task_key explicitly.`

4. Replace `_DISPATCH_CONSULT_TO_HEADER` with:

```python
_GRADE_DISPATCH_TO_HEADER = {
    "grade_do": "DO",
    "grade_get": "GET",
    "grade_like": "LIKE",
}
```

Update `_consult_scored_dispatch_batch_encoded` to use `_GRADE_DISPATCH_TO_HEADER[dispatch_task_key]` (parameter remains `dispatch_task_key`).

5. In `_consult_scored_dispatch_batch_encoded`, replace `agent_tk = cfg_dispatch["agent_task"]` with:

```python
    agent_tk = cfg_dispatch.get("agent_task") or dispatch_task_key
```

6. In `render_verdict`, replace `agent_task = cfg["agent_task"]` with:

```python
    agent_task = cfg.get("agent_task") or task_type
```

7. In `_apply_render_verdict_decoded_job`, replace `agent_task = cfg.get("agent_task") or resolve_dispatch_task_config_key(dispatch_task_key)` with:

```python
    agent_task = cfg.get("agent_task") or (dispatch_task_key or "").strip()
```

In the scored branch `ValueError` for missing rubric, replace `orch_key = resolve_dispatch_task_config_key(dispatch_task_key)` with `orch_key = (dispatch_task_key or "").strip()`.

8. Rename batch entry functions (names match **TASK_CONFIG** keys):

   - `consult_do_batch` → `grade_do_batch` (body calls `_consult_scored_dispatch_batch_encoded("grade_do", ...)`)
   - `consult_get_batch` → `grade_get_batch` (`"grade_get"`)
   - `consult_like_batch` → `grade_like_batch` (`"grade_like"`)

9. In `run_consult_task`, replace the branch:

```python
    elif task_key in ("grade_do", "grade_get", "grade_like"):
        if len(entities) == 1:
            aid = entities[0]["astral_job_id"]
            orch = _consult_orchestration(task_key)
            rv = await render_verdict(task_key, aid, ctx=ctx, debug=debug)
            ...
        _batch = {
            "grade_do": grade_do_batch,
            "grade_get": grade_get_batch,
            "grade_like": grade_like_batch,
        }[task_key]
        r = await _batch(batch_id, entities, ctx=ctx, debug=debug, batch_chunk_index=batch_chunk_index)
```

10. In `src/core/dispatcher.py`, replace `_CHUNK_EXHAUST_CONSULT_JOB_KEYS` members:

```python
_CHUNK_EXHAUST_CONSULT_JOB_KEYS = frozenset({
    "qualify_job_listings",
    "evaluate_jd",
    "grade_do",
    "grade_get",
    "grade_like",
})
```

11. Grep `src/core/consult.py` and `src/core/dispatcher.py` for `consult_do`, `consult_get`, `consult_like` — zero remaining (docstrings updated in step 1).

⚠️ **Decision:** Keep `render_verdict` accepting the dispatch/catalog key (`grade_do`) as `task_type` — no separate wrapper key. `do_task` and timesheet attribution use `grade_do` (Execution History AC #3).

## Execution contract

Binding per **plan-child**: stages **1 → 2** in order; **one commit per stage** on epic worktree during **build-child**, publish each to **`origin/sub/AST-736/AST-748-db-migration-consult-dispatch-runtime-cutover`**. Do not edit `tests/`, `docs/ASTRAL_TEST_BIBLE.md`, or `docs/test-bible/**`. On ambiguity — **`🛑 Stage N blocked`** on **AST-736** parent; stop.

## Self-Assessment

**Scope:** `Single-Component` — `database.py` dispatch row migration plus `consult.py` graded-consult routing and `dispatcher.py` chunk-exhaustion frozenset; no config or UI layers.

**Conf:** `high` — AST-703/AST-485 migration ordering pattern is established; AST-747 already collapsed config alias map; runtime changes are string renames and removing `resolve_dispatch_task_config_key` call sites in consult.

**Risk:** `HIGH` — incorrect migration order could `IntegrityError` on admin dispatch reads (Scheduled Actions 500); wrong `agent_task` resolution would mis-attribute timesheets or break `render_verdict` for graded rows.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Status |
|------|--------|
| §1.3 DRY | Migration tuple local; orchestration reads `TASK_CONFIG` directly — no duplicate alias map. |
| §2.1 config | Schedulable keys unchanged here (**AST-747**); migration uses fixed rename pairs matching config replacements. |
| §2.4 batch | `_CHUNK_EXHAUST_CONSULT_JOB_KEYS` stays aligned with `_DISPATCH_BATCH_CALL_MODE_ONE` grade members. |
| §2.6 state machine | `trigger_state` claim rules unchanged; only `task_key` strings on rows and runtime routing change. |
| §2.7 render_verdict | `task_type` / dispatch key = `TASK_CONFIG` index for graded steps. |
| §3.3 imports | Data migration block uses SQL only; core consult drops utils alias helper import. |
| §3.5 naming | `grade_*` matches `TASK_CONFIG` and Manage Tasks catalog. |

No conflicts requiring `!!-NONE`.

## Integration notes (for build-child / siblings)

- **AST-747** must be on the integration line before **test-child** — config rejects new `consult_*` rows while runtime still accepted them until this ticket lands.
- **Betty** updates tests monkeypatching `consult_do_batch` / `dispatch_task_key='consult_do'` — do not patch tests in this ticket.
- **dispatch_ledger** historical rows may still show legacy strings — parent boundary excludes backfill.

## Review (build)

| Field | Value |
|-------|-------|
| Build date | 2026-06-23 |
| Publish ref | `origin/sub/AST-736/AST-748-db-migration-consult-dispatch-runtime-cutover` @ `13352e9` |
| Commits | `bf8eaa3` database migration · `61eaf25` consult + dispatcher runtime · `27d950d` test (Betty) |

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-736/AST-748-db-migration-consult-dispatch-runtime-cutover` · tip **`13352e9`**

**AST-748 product commits:** `bf8eaa3`, `61eaf25`, `27d950d`. Publish ref rolls up resolved **AST-747**, **AST-751**, and other sibling qa merges — not attributed to Hedy commits (§5d boundary clean).

### What's solid

| Area | Notes |
|------|-------|
| Plan Stage 1 | Idempotent migration block matches plan verbatim: collision DELETE then UPDATE per pair; local tuple (no config import widening); placement after AST-702, before schema-ensured flag. |
| Plan Stage 2 | Zero `consult_do`/`consult_get`/`consult_like` in `consult.py` / `dispatcher.py`; `_consult_orchestration` reads `TASK_CONFIG` directly; batch entrypoints renamed; `run_consult_task` routes `grade_*`; `_CHUNK_EXHAUST_CONSULT_JOB_KEYS` aligned. |
| §2.7 render_verdict | `agent_task = cfg.get("agent_task") or task_type` — timesheet / Execution History attribution now `grade_*` (intended AST-736 AC). |
| §2.4 batch | Chunk-exhaust frozenset matches config `_DISPATCH_BATCH_CALL_MODE_ONE` grade members. |
| §3.3 layer | Data migration SQL-only; consult drops `resolve_dispatch_task_config_key` import. |
| Tests | `TestAst748ConsultToGradeDispatchMigration` covers rename-with-preserved scheduling (Case A) and collision delete (Case B); consult/dispatcher tests use `grade_*` keys and `grade_do_batch`. |

### Issues

| Severity | Item | Location |
|----------|------|----------|
| — | **No fix-now or discuss.** | — |

### Recommended actions

| Action | Owner |
|--------|-------|
| **resolve-child** — no code changes required from review. | Hedy |
| Susan UAT: confirm legacy `consult_*` dispatch rows renamed on staging DB; Run/AUTO graded consult hops show `grade_*` in Execution History. | Susan |

## Resolution

| Field | Value |
|-------|-------|
| Date | 2026-06-23 |
| Publish ref | `origin/sub/AST-736/AST-748-db-migration-consult-dispatch-runtime-cutover` @ `d6949be` |

### Outcome

Radia review: **no fix-now** or **discuss** items. No product or plan edits required from review feedback.

### §9a dry-run

- `origin/sub/AST-736/AST-748-db-migration-consult-dispatch-runtime-cutover` → `origin/dev`: clean
- `origin/sub/AST-736/AST-748-db-migration-consult-dispatch-runtime-cutover` → `origin/ftr/ast-736-task-keys-vs-dispatch-task-keys`: clean
