<!-- linear-archive: AST-733 archived 2026-07-22 -->

## Linear archive (AST-733)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-733/post-qualify-identity-collision-delete-duplicate-jobs-ingested  
**Status at archive:** Archive  
**Project:** Astral Tracker  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-728 — Duplicate jobs ingested  
**Blocked by / blocks / related:** parent: AST-728

### Description

## What this implements

When Consult delivers job metadata after `qualify_job_listings` that would populate `(company, job_title, company_job_id)` on the current row but another row already holds that triple, delete the current job row by `astral_job_id` instead of updating into a duplicate. The existing row with that triple remains canonical.

## Acceptance criteria

* When `qualify_job_listings` metadata would collide with an existing identity triple on another row, the current job row is deleted and no duplicate triple exists afterward.
* No regression in Consult job initialization paths covered by existing tests.

## Boundaries

* Does not add the unique index or insert-time tolerance — **AST-732**.
* Does not run one-time historical cleanup — **AST-729**.
* Does not re-point or delete related records when removing the colliding job row.

## Notes for planning

* Touch `initialize_job` / qualify path in `src/core/consult.py` and/or `src/core/tracker.py`.
* Depends on **AST-732** unique constraint existing for defense in depth; collision handling is explicit delete of current row.
* Batch must continue without unhandled error when a row is deleted.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-728-duplicate-jobs-ingested`, child `sub/AST-728/AST-733-post-qualify-identity-collision-delete`. Created at dispatch-parent.

### Comments

#### radia — 2026-06-18T05:43:58.127Z
**Diff:** `origin/dev...origin/sub/AST-728/AST-733-post-qualify-identity-collision-delete` @ `31fc1fc`
**Plan doc:** `docs/features/tracker/ast-733-post-qualify-identity-collision-delete.md` (Review section)

### Plan fidelity
`get_job_id_by_identity` (self-exclusion) + `delete_job` (no cascade) in data layer. `initialize_job` proactive collision delete when complete triple matches another row; IntegrityError fallback for race; bool return. `qualify_job_listings` returns `fail_state` on collision — skips save/transition, batch continues without raise.

### ASTRAL_CODE_RULES
- **§2.6 state machine:** Collision deletes current row and skips transition — no state write on deleted id.
- **§3.3 layering:** consult → tracker → database; `sqlite3` in tracker for IntegrityError fallback only (plan-approved).
- **Data layer no log:** Lookup/delete return values only.
- **§5f debug:** Production INFO on collision when `debug=False` — normal path, not debug-contract emission.

### Tests
Manifest covers identity helpers, initialize collision/save/incomplete-skip, qualify batch failed count with no save/transition.

### fix-now
None.

### advisory
- Diff vs `origin/dev` stacks AST-732 + AST-729 test artifacts — expected epic stacking; AST-733 product scope is collision path only.
- `_is_job_identity_unique_violation` duplicated in tracker + database (plan-specified fallback).
- No component test for IntegrityError fallback in `initialize_job` — proactive path covered.

#### hedy — 2026-06-18T05:43:53.757Z
**Diff:** `origin/dev...origin/sub/AST-728/AST-733-post-qualify-identity-collision-delete` (AST-733 product: `database.get_job_id_by_identity`, `database.delete_job`, `initialize_job` collision delete + bool return, `qualify_job_listings` wiring; branch stacks **AST-732** + Betty tests/bible)

### Plan fidelity
- **Stage 1:** `get_job_id_by_identity` (exact triple match, optional `exclude_astral_job_id`, `LIMIT 1`) and `delete_job` (single-row `DELETE`, no cascade, empty-id guard) via `_ensure_job_schema` / `_run_with_retry`.
- **Stage 2:** `_identity_triple_complete` guard; proactive canonical lookup → `delete_job(current)` + `False`; incomplete triples skip lookup; `IntegrityError` fallback on identity unique violation also deletes current row; successful save → `True`.
- **Stage 3:** `qualify_job_listings` `process` — on `initialize_job` `False`, logs collision, returns `cfg["fail_state"]` without `_save_joblist_result` or `_transition_job_state_for_task`; batch continues (`_run_batch_consult` counts as `failed`).
- Boundaries: no cleanup migration (**AST-729**), no new index work beyond stacked **AST-732**; `evaluate_jd_batch` untouched.

### ASTRAL_CODE_RULES
- **§2.6 state machine:** Deleted row gets no transition or grade write — correct.
- **§3.3 layering:** `consult` → `tracker` → `database`; `sqlite3` in tracker for IntegrityError fallback only.
- **Data layer no log:** Lookup/delete return values only.
- **D2:** IntegrityError re-raised when not identity violation; collision path is explicit, not swallowed.

### Code quality
- Tests cover identity helpers, canonical-delete path, no-collision save, incomplete-triple skip, consult batch `failed` accounting without save/transition, plus stacked AST-732 ingest/index coverage.

### Advisory (not blocking)
- **Stacked diff:** Branch includes full **AST-732** product changes and sibling test bundles (**AST-729** script tests) from epic `merge-tests` — expected for stacked sub branch.
- **DRY:** `_is_job_identity_unique_violation` duplicated in `tracker.py` and `database.py` — acceptable per plan (tracker fallback without importing private DB helper).
- **Orphan refs:** Deleted colliding row leaves related audit rows as-is — intentional per epic; canonical row unchanged.

**Verdict:** No fix-now or discuss items. Ready for `resolve-child`.

#### betty — 2026-06-18T05:41:52.626Z
## QA test manifest (AST-733)

**Publish ref:** `origin/sub/AST-728/AST-733-post-qualify-identity-collision-delete` @ `275f3473` (`merge-tests(AST-733): origin/tests 013d0268`)

**Depends on:** **AST-732** unique index + insert tolerance (stacked on this sub ref).

### 1. Data layer identity helpers (required)

`tests/component/data/database/test_jobs.py::TestAst733JobIdentityHelpers`

- `test_get_job_id_by_identity_finds_canonical_excludes_self`
- `test_delete_job_removes_row`

### 2. `initialize_job` collision delete (required)

`tests/component/core/test_tracker.py::TestAst733InitializeJobCollision`

- `test_deletes_current_row_when_canonical_exists` — current row deleted, canonical untouched
- `test_saves_when_no_collision`
- `test_incomplete_identity_skips_collision_lookup` — NULL/missing `company_job_id` skips SELECT

### 3. `qualify_job_listings` batch wiring (required)

`tests/component/core/test_consult.py::TestAst733QualifyIdentityCollision`

- `test_collision_skips_save_and_transition_counts_failed` — `initialize_job` `False` → no `save_job_data`, no transition, `failed` += 1

### 4. Regression (required)

- `tests/component/core/test_tracker.py::TestInitializeJob` (existing column/metadata split)
- `tests/component/core/test_consult.py::TestQualifyJobListings::test_runs_debug_and_passing_job_path` (rubric substrate patch for AST-723 table-backed criteria)

**Narrowed run:**

```bash
.venv/bin/python -m pytest \
  tests/component/data/database/test_jobs.py::TestAst733JobIdentityHelpers \
  tests/component/core/test_tracker.py::TestAst733InitializeJobCollision \
  tests/component/core/test_consult.py::TestAst733QualifyIdentityCollision \
  tests/component/core/test_tracker.py::TestInitializeJob \
  tests/component/core/test_consult.py::TestQualifyJobListings::test_runs_debug_and_passing_job_path \
  -q
```

**Bible shasums on publish ref:**

- `docs/test-bible/data/database/jobs.md` — `45d3cb8e6ae5118c4ff8a5c5174c7a3374f1e288c710dc78ec0702566fb0796f`
- `docs/test-bible/core/tracker.md` — `19508e44388268d443ea009ef357f66bad063c47cdc606bcc78622699e229147`
- `docs/test-bible/core/consult.md` — `4b7258a8e0c8a75273d8cfddcb090f51c5e33b4c7d72745696ca3f9ab5c4ead3`

— Betty

#### hedy — 2026-06-18T05:34:10.583Z
Plan doc: `docs/features/tracker/ast-733-post-qualify-identity-collision-delete.md`

GitHub: https://github.com/susansomerset/astral/blob/sub/AST-728/AST-733-post-qualify-identity-collision-delete/docs/features/tracker/ast-733-post-qualify-identity-collision-delete.md

**Self-assessment**
- **Scope:** `Single-Component` — `get_job_id_by_identity` + `delete_job` in data layer; collision logic in `initialize_job`; `qualify_job_listings` process skip on delete.
- **Conf:** `high` — single production caller of `initialize_job`; explicit SELECT-before-write delete and batch-continue behavior specified.
- **Risk:** `Medium` — false-positive identity match deletes a valid row; mitigated by exact triple + exclude-self, complete-triple guard only, AST-732 IntegrityError fallback.

Four stages: (1) data helpers, (2) `initialize_job` returns `False` on collision delete, (3) qualify `process` skips save/transition and returns `fail_state`, (4) compile gate. Depends on **AST-732** merged first.

---

# Post-qualify identity collision delete (Duplicate jobs ingested)

**Linear issue:** https://linear.app/astralcareermatch/issue/AST-733/post-qualify-identity-collision-delete-duplicate-jobs-ingested

**Publish ref:** `sub/AST-728/AST-733-post-qualify-identity-collision-delete`

When `qualify_job_listings` delivers structured metadata (`company_job_id`, `job_title`, `job_link`) for a passing job, but another row already owns the same `(company, job_title, company_job_id)` triple, delete the **current** row by `astral_job_id` and leave the existing canonical row untouched. Batch processing continues without raising. Related records for the deleted row are left as-is per epic boundaries.

**Depends on AST-732** (unique index + insert tolerance) landing first for defense in depth; this ticket adds explicit pre-write collision detection and delete.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | `get_job_id_by_identity`, `delete_job` helpers | data |
| `src/core/tracker.py` | `initialize_job` collision check, delete-on-collision, bool return | core |
| `src/core/consult.py` | `qualify_job_listings` `process` handles collision delete | core |

## Stage 1: Data layer identity lookup and single-row delete

**Done when:** `database.get_job_id_by_identity` and `database.delete_job` exist, use `_ensure_job_schema`, and compile cleanly.

1. Add public function in `src/data/database.py`:
   ```python
   def get_job_id_by_identity(
       company: str,
       job_title: str,
       company_job_id: str,
       *,
       exclude_astral_job_id: Optional[str] = None,
   ) -> Optional[str]:
   ```
   - Return `astral_job_id` of first matching row where `company`, `job_title`, and `company_job_id` match exactly (callers pass stripped values).
   - SQL: `SELECT astral_job_id FROM job WHERE company = ? AND job_title = ? AND company_job_id = ?` plus `AND astral_job_id != ?` when `exclude_astral_job_id` is set. `LIMIT 1`.
   - Call `_ensure_job_schema(conn)` inside `_run_with_retry` closure; return `None` when no match.
2. Add public function:
   ```python
   def delete_job(astral_job_id: str) -> bool:
   ```
   - `DELETE FROM job WHERE astral_job_id = ?`; commit; return `cursor.rowcount > 0`.
   - Return `False` when `astral_job_id` is empty (mirror `_remove_jobs_by_company` guard).
   - Do **not** cascade-delete agent_data, agent_responses, timesheets, or dispatch_ledger rows.
3. No header inventory table list change required (still `job` table only).

⚠️ **Decision:** New public `delete_job` / `get_job_id_by_identity` rather than importing private `_remove_jobs_by_company` — single-row delete and identity lookup are distinct operations.

## Stage 2: `initialize_job` collision delete

**Done when:** `initialize_job` returns `True` when metadata is saved, `False` when current row was deleted due to identity collision; incomplete identity triples skip collision check and behave as today.

1. Add module-level helper in `src/core/tracker.py` (near `_JOB_COLUMN_FIELDS`):
   ```python
   def _identity_triple_complete(company_job_id: Optional[str], job_title: Optional[str]) -> bool:
       return bool(
           company_job_id and job_title
           and str(company_job_id).strip()
           and str(job_title).strip()
       )
   ```
2. Change `initialize_job` signature from `-> None` to `-> bool`. Docstring: `True` = structured fields saved; `False` = current `astral_job_id` deleted because another row already holds the complete identity triple.
3. After building `col_kwargs` from `parsed_job` (existing logic), before `database.save_job`:
   - Set `cid = col_kwargs.get("company_job_id")`, `title = col_kwargs.get("job_title")`.
   - If `_identity_triple_complete(cid, title)` is false: skip collision check (proceed to save — same as today for pre-identity rows).
   - Else:
     - `canonical = database.get_job_id_by_identity(company, str(title).strip(), str(cid).strip(), exclude_astral_job_id=astral_job_id)`
     - If `canonical` is not None: call `database.delete_job(astral_job_id)` and `return False`.
4. On no collision, call existing `database.save_job(...)` with same kwargs as today.
5. **Defense in depth (AST-732):** wrap `database.save_job(...)` in try/except for `sqlite3.IntegrityError`. Import `sqlite3` at top of `tracker.py` if not present. On catch, if error matches identity unique index (reuse same message check as AST-732 plan: `"idx_job_identity_unique"` in message or `unique constraint failed` with `job.company`, `job.job_title`, `job.company_job_id`): call `database.delete_job(astral_job_id)` and `return False`. Otherwise re-raise.
6. On successful save: `return True`.

⚠️ **Decision:** Collision check uses proactive SELECT before UPDATE, not only IntegrityError — explicit delete per ticket; IntegrityError path is fallback when AST-732 index catches a race.

## Stage 3: `qualify_job_listings` batch wiring

**Done when:** Passing-path `process` in `qualify_job_listings` skips save/transition when `initialize_job` returns `False`; batch completes without exception; deleted job counts as non-pass in batch summary.

1. In `src/core/consult.py`, in `qualify_job_listings` inner `process`, replace:
   ```python
   tracker.initialize_job(aid, input_job["company"], response_job)
   _save_joblist_result()
   _transition_job_state_for_task(task_key, [aid], to_state, score)
   ```
   with:
   ```python
   if not tracker.initialize_job(aid, input_job["company"], response_job):
       if not debug:
           logger.info(f"  {aid} -> deleted (identity collision)")
       # Count as non-pass in _run_batch_consult; do not transition or save grades to deleted row.
       return cfg["fail_state"]
   _save_joblist_result()
   _transition_job_state_for_task(task_key, [aid], to_state, score)
   ```
2. Do **not** raise on collision — `process` must return normally so `_run_batch_consult` continues the batch loop.
3. Do **not** change fail-path (`to_state == cfg["fail_state"]`) or title/link validation branches.
4. Do **not** change `evaluate_jd_batch` or other consult tasks — collision applies only after `qualify_job_listings` metadata write.

⚠️ **Decision:** Return `cfg["fail_state"]` on collision so batch `failed` counter increments and no state transition runs on a deleted row; deleted duplicate is not counted as `passed`.

## Stage 4: Compile gate

**Done when:** `python -m py_compile src/data/database.py src/core/tracker.py src/core/consult.py` exits 0.

1. Run compile from repo root on all three touched files.
2. Fix syntax/import errors before stage commit.

## Self-Assessment

**Scope:** `Single-Component` — three core/data files on the qualify → initialize path only; no UI, Gazer, or schema index work (AST-732).

**Conf:** `high` — single call site for `initialize_job` in production (`qualify_job_listings`); collision rule and batch-continue requirement are explicit in AST-733/AST-728.

**Risk:** `Medium` — wrong identity match deletes a valid new job; mitigated by exact triple match excluding self, complete-triple guard only, and AST-732 index as backstop.

## ASTRAL_CODE_RULES self-review

- **§1.3 DRY:** One lookup + one delete primitive in data layer; identity-complete guard local to tracker.
- **§2.1 Config:** No new config; uses existing qualify pass/fail states for batch accounting only.
- **§2.6 State machine:** Collision path skips transition — deleted row leaves pipeline without invalid state write.
- **§3.3 Imports:** `consult` → `tracker` → `database` (unchanged layering); `sqlite3` in tracker for IntegrityError fallback only.
- **Data layer no log:** Lookup/delete return values only.
- **No conflicts** requiring plan revision.

---

## Review

**Branch:** `origin/sub/AST-728/AST-733-post-qualify-identity-collision-delete`  
**Diff baseline:** `origin/dev`  
**Review tip:** `275f347`

**Built:** Stages 1–4 — `get_job_id_by_identity` + `delete_job` in database; `initialize_job` proactive collision delete + IntegrityError fallback with bool return; `qualify_job_listings` skips save/transition on collision (returns `fail_state`); stacked AST-732; Betty manifest + component tests on `origin/tests` merge.

### What's solid

- Plan fidelity: identity lookup with self-exclusion; single-row `delete_job` without cascade; `_identity_triple_complete` guard skips incomplete triples; proactive SELECT before save; IntegrityError fallback on race; consult returns `fail_state` without raising so batch continues.
- State machine: collision path deletes current row and skips transition — no invalid state write on deleted `astral_job_id`.
- Layer rules: data helpers return values only (no logging); consult → tracker → database unchanged; production INFO on collision when `debug=False` is appropriate (not debug-contract noise).
- Tests: database lookup/delete helpers, initialize collision/save/skip-lookup paths, qualify batch wiring (failed count, no save/transition) — aligned with test-bible manifest.

### Issues

| Severity | Location | Finding |
| --- | --- | --- |
| — | — | No fix-now items. |

### Recommended actions

| Severity | Location | Action |
| --- | --- | --- |
| advisory | diff vs `origin/dev` | Diff stacks AST-732 + AST-729 test artifacts (siblings not on dev) — expected epic branch stacking; AST-733 product scope is consult/tracker/database collision path only. |
| advisory | `src/core/tracker.py` | `_is_job_identity_unique_violation` duplicates `database.py` helper — plan-specified; optional future extract to shared util if a third caller appears. |
| advisory | tests | No component test for IntegrityError fallback path in `initialize_job` — proactive collision path covered; fallback is defense-in-depth. |

---

## Resolution

**Date:** 2026-06-18  
**Resolved by:** Hedy (resolve-child)

Radia posted **no fix-now** items. Advisory notes (stacked sibling diffs; duplicated `_is_job_identity_unique_violation`; no IntegrityError fallback test) accepted as documented.

**§9a dry-run:** `origin/sub/AST-728/AST-733-post-qualify-identity-collision-delete` (post ftr merge + resolve) merges cleanly into **`origin/dev`** and **`origin/ftr/duplicate-jobs-ingested`**.

**Product changes in resolve:** none — review clean. Manifest re-run: 10 passed.
