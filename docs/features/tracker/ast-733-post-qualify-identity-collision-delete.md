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
**Review tip:** `00f6d163`

**Built:** Stages 1–4 — `get_job_id_by_identity` + `delete_job` in database; `initialize_job` collision delete with bool return and IntegrityError fallback; `qualify_job_listings` skips save/transition on collision (returns fail_state); stacked AST-732; compile passes.
