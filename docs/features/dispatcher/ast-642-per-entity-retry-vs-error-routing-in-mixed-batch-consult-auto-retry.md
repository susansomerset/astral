# Per-entity retry vs error routing in mixed batch consult (Auto retry — AST-642)

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-642/per-entity-retry-vs-error-routing-in-mixed-batch-consult-auto-retry  
**Parent:** https://linear.app/astralcareermatch/issue/AST-630/auto-retry  

**Publish ref (origin):** `sub/AST-630/AST-642-per-entity-batch-retry`  
**Parent integration ref:** `ftr/ast-630-auto-retry`  
**Depends on (landed):** AST-641 union claim/count — mixed primary + `*_RETRY` entities may share one dispatch batch.

After AST-641, a primary-trigger dispatch row can claim jobs in both `VALID_TITLE` and `VALID_TITLE_RETRY` (and analogous pairs) in one batch. `_run_batch_consult` currently derives a single batch-level `retry_state` from `jobs[0].state`, so every missing ID and `bad_grades` row routes to the first job’s retry or error destination. This ticket fixes routing so each entity’s **actual current state** decides retry vs terminal error. Entities already in a `*_RETRY` holding state must not loop in retry.

**Verified (plan time):** `consult._run_batch_consult` lines ~907–909 set `input_state = jobs[0].get("state")` and one `retry_state` for the whole batch. Missing IDs (~993–994), `bad_grades` (~1065–1067), envelope failure (~953–954), and hydration failure (~964–965) transition all affected IDs to the same destination. `_run_analysis_upshot_batch` (~685–709) always uses `task_cfg["error_state"]` (`PASSED_LIKE_RETRY`) per entity without checking whether the entity is already in that retry holding state. `qualify_job_listings` short-title path (~1179–1180) hard-codes `cfg["error_state"]` instead of per-entity retry routing.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | Add `_consult_batch_fail_dest` helper; per-entity grouped transitions in `_run_batch_consult`; use helper in `_run_analysis_upshot_batch` and `qualify_job_listings` short-title path | core |

**Not in scope:** `src/utils/config.py` / `JOB_STATES` registry edits, `src/data/database.py`, `src/core/dispatcher.py`, company `roster._prefilter_fail` (per-entity but separate path — not batch-level `input_state` bug), in-place duplicate API calls (AST-340).

**Tests (Betty at Code Complete — engineer does not edit `tests/` in build):** extend `tests/component/core/test_consult.py` with mixed-state batch fixtures for `qualify_job_listings`, `evaluate_jd`, and `analysis_upshot` per AC below.

---

## Stage 1: Per-entity fail-destination helper

**Done when:** `_consult_batch_fail_dest(entity_state, error_state)` returns the correct destination for all AC state pairs; `python3 -m py_compile src/core/consult.py` passes.

1. In `src/core/consult.py`, add a module-level helper immediately before `_run_batch_consult` (~887):

   ```python
   def _consult_batch_fail_dest(entity_state: Optional[str], error_state: Optional[str]) -> Optional[str]:
       """AST-642: route batch consult failure per entity — primary → retry holding, *_RETRY → terminal."""
       st = (entity_state or "").strip()
       if not st:
           return error_state
       retry = JOB_STATES.get(st, {}).get("retry_state")
       if retry:
           return retry
       if st == error_state:
           # analysis_upshot: TASK_CONFIG error_state IS the retry holding (PASSED_LIKE_RETRY)
           return "FAILED_TECHNICAL"
       return error_state
   ```

2. Run:

   ```bash
   python3 -m py_compile src/core/consult.py
   ```

⚠️ **Decision:** Second-attempt terminal for `analysis_upshot` when entity is already in `PASSED_LIKE_RETRY` (where `error_state == PASSED_LIKE_RETRY`) is **`FAILED_TECHNICAL`** — `prior_states` is unrestricted in `JOB_STATES`, and no `ERROR_*` upshot state exists in config. Qualify/evaluate terminal paths continue to use `ERROR_QUALIFY_JOB_LISTINGS` / `ERROR_EVALUATE_JD` via the `return error_state` branch when entity is in `*_RETRY` but `st != error_state`.

---

## Stage 2: `_run_batch_consult` — per-entity grouped transitions

**Done when:** Missing IDs, `bad_grades`, envelope failure, and hydration failure each transition jobs to destinations derived from **that job’s** `state`, not `jobs[0].state`; debug logging reflects mixed states; homogeneous batches behave as today; `python3 -m py_compile src/core/consult.py` passes.

1. Add a private grouper immediately after `_consult_batch_fail_dest`:

   ```python
   def _transition_batch_consult_failures(
       task_key: str,
       job_rows: List[Dict[str, Any]],
       error_state: Optional[str],
   ) -> None:
       """Group jobs by per-entity fail dest and transition once per destination."""
       by_dest: Dict[str, List[str]] = {}
       for row in job_rows:
           aid = row.get("astral_job_id")
           if not aid:
               continue
           dest = _consult_batch_fail_dest(row.get("state"), error_state)
           if dest:
               by_dest.setdefault(dest, []).append(aid)
       for dest, ids in by_dest.items():
           _transition_job_state_for_task(task_key, ids, dest)
   ```

2. In `_run_batch_consult`, **remove** batch-level `input_state` / `retry_state` derivation (~907–909). Keep a local `batch_states` set for debug only:

   ```python
   batch_states = sorted({j.get("state") for j in jobs if j.get("state")})
   ```

3. Update batch-start `debug_detail` (~921–923) to log `batch_states={batch_states!r}` instead of `input_state=…`.

4. **Envelope failure** (`not result.get("success")`, ~952–955): replace `_transition_job_state_for_task(task_key, astral_ids, error_state)` with `_transition_batch_consult_failures(task_key, jobs, error_state)`.

5. **Hydration failure** (`ValueError` from `_hydrate_response_jobs_grade_reasons`, ~964–965): same replacement — `_transition_batch_consult_failures(task_key, jobs, error_state)`.

6. **Missing IDs** (~987–994): replace single-dest transition with:

   ```python
   missing_rows = [input_by_id[mid] for mid in missing if mid in input_by_id]
   _transition_batch_consult_failures(task_key, missing_rows, error_state)
   ```

   Update warning / `dest_label` logging: when all missing share one dest, log that dest; when mixed, log `per-entity retry/error routing` and sorted `{dest: count}` summary (no silent single-dest assumption).

7. **bad_grades** (~1062–1067): replace single-dest transition with:

   ```python
   bad_rows = [input_by_id[aid] for aid in error_ids if aid in input_by_id]
   _transition_batch_consult_failures(task_key, bad_rows, error_state)
   ```

8. **truncated_note** (~1075–1077): when `missing`, note `per-entity routing` if destinations differ; else keep `truncated: N IDs -> {dest}: [ids]` using the sole dest when homogeneous.

9. Update `_run_batch_consult` docstring (~900): replace “if the input_state has one” with “per entity’s current state via `_consult_batch_fail_dest`”.

10. Run:

    ```bash
    python3 -m py_compile src/core/consult.py
    ```

⚠️ **Decision:** Envelope and hydration failures use **per-entity** routing (not whole-batch single `error_state`) so a mixed `VALID_TITLE` + `VALID_TITLE_RETRY` batch does not send first-attempt primaries to `ERROR_QUALIFY_JOB_LISTINGS` when the envelope fails on a batch whose first row is retry-state. This extends AST-340’s whole-batch envelope rule only where AST-641 mixed claim applies; homogeneous retry-only batches still route all rows to terminal error.

---

## Stage 3: `analysis_upshot` and qualify short-title paths

**Done when:** `_run_analysis_upshot_batch` failure transitions use `_consult_batch_fail_dest(row.get("state"), task_cfg["error_state"])`; `qualify_job_listings` short-title branch uses the same helper with `input_job.get("state")`; `python3 -m py_compile src/core/consult.py` passes.

1. In `_run_analysis_upshot_batch`, replace every `_transition_job_state_for_task("analysis_upshot", [aid], task_cfg["error_state"])` (~685, ~692, ~704, ~709) with:

   ```python
   dest = _consult_batch_fail_dest(row.get("state"), task_cfg.get("error_state"))
   if dest:
       _transition_job_state_for_task("analysis_upshot", [aid], dest)
   ```

   Use `fresh.get("state")` on the ~691 branch where state is re-read.

2. In `qualify_job_listings` `process` closure, short-title branch (~1176–1181): replace `cfg["error_state"]` with:

   ```python
   dest = _consult_batch_fail_dest(input_job.get("state"), cfg.get("error_state"))
   ```

   Transition to `dest` when truthy; log `dest` in warning/debug lines.

3. Run:

   ```bash
   python3 -m py_compile src/core/consult.py
   ```

---

## Execution contract reminders

- **AST-641** must be on the integration line before build (union claim) — already on `origin/ftr/ast-630-auto-retry` at plan time.
- Do **not** edit `JOB_STATES`, seed dispatch rows, or change `dispatch_claim_states`.
- Betty’s tests should cover at minimum:
  - Mixed batch `[VALID_TITLE, VALID_TITLE_RETRY]` + missing ID for retry row → `ERROR_QUALIFY_JOB_LISTINGS`; missing for primary → `VALID_TITLE_RETRY`.
  - Mixed batch + `bad_grades` on retry row → `ERROR_QUALIFY_JOB_LISTINGS` (not left in `VALID_TITLE_RETRY`).
  - Same patterns for `evaluate_jd` (`JD_READY` / `JD_READY_RETRY` → `ERROR_EVALUATE_JD`).
  - `analysis_upshot`: `PASSED_LIKE` failure → `PASSED_LIKE_RETRY`; `PASSED_LIKE_RETRY` failure → `FAILED_TECHNICAL`.
  - Homogeneous single-state batch regression: behavior unchanged vs pre-642 for all-primary or all-retry slices.

---

## Self-Assessment

**Scope:** `Single-Component` — one core module (`consult.py`), one helper and call-site wiring; no config or data-layer changes.

**Conf:** `high` — AST-641 landed the mixed claim; fix is localized replacement of batch-level `jobs[0].state` with per-row lookup following existing `JOB_STATES.retry_state` + `TASK_CONFIG.error_state` contract.

**Risk:** `Medium` — incorrect grouping would leave jobs stuck in `*_RETRY` or over-route primaries to terminal error; blast radius is batch consult failure paths only, but those sit on the critical job pipeline.

---

## ASTRAL_CODE_RULES self-review

| Rule | Compliance |
|------|------------|
| §1.3 DRY | Single `_consult_batch_fail_dest` + `_transition_batch_consult_failures`; no duplicated retry logic in qualify/upshot |
| §2.1 Config as source of truth | Uses `JOB_STATES[].retry_state` and task `error_state` only — no new inline state lists |
| §2.4 Batch processing | Claim/get/clear unchanged; only post-`do_task` failure routing |
| §2.6 State machine | No registry edits; transitions use existing legal states |
| §3.3 Imports | Helper stays in core; no new cross-layer imports |
| §3.5 Naming | `_consult_batch_fail_dest` matches consult module prefix |

No conflicts requiring `conf-!!-NONE`.

---

## Review (build)

**Branch:** `sub/AST-630/AST-642-per-entity-batch-retry`  
**Tip:** `65a52f86` — `code(AST-642): per-entity retry vs error routing in mixed batch consult`

**Summary:** Added `_consult_batch_fail_dest` and `_transition_batch_consult_failures`; wired per-entity grouped transitions into `_run_batch_consult` (envelope, hydration, missing IDs, bad_grades), `_run_analysis_upshot_batch`, and qualify short-title path.

**Compile:** `python3 -m py_compile src/core/consult.py` — pass.

**Tests:** Betty at Code Complete (mixed-state batch fixtures per execution contract).

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-630/AST-642-per-entity-batch-retry` (three-dot). Product delta for this ticket: commit `65a52f86` (`src/core/consult.py` only). Stack also carries unmerged **AST-641** (union claim/count — Radia clean at `a053a5cc`); not re-litigated here.

**Tip:** `2e6f1a38`

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | `_consult_batch_fail_dest` + `_transition_batch_consult_failures` match Stages 1–3; batch-level `jobs[0].state` removed; envelope, hydration, missing IDs, `bad_grades`, analysis_upshot, and qualify short-title paths wired. |
| §2.1 / §2.6 | Retry vs terminal derived from `JOB_STATES[].retry_state` and task `error_state`; `PASSED_LIKE_RETRY` → `FAILED_TECHNICAL` special case documented in helper. |
| §2.4 batch pattern | Claim/get/clear untouched; only post-`do_task` failure routing changes. |
| §1.5.1 debug | Mixed-batch `debug_detail` logs `batch_states`; per-missing-ID `debug_index` shows per-entity destination. |
| Tests | `test_consult.py` covers helper matrix, mixed missing/bad_grades for qualify and evaluate_jd, analysis_upshot paths per execution contract. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| — | — | None (fix-now / discuss). |

### Recommended actions

| Action | Owner |
|--------|-------|
| Proceed to `resolve-child` (optional — no fix-now items). | Ada |
