# AST-898 — NEW_RETRY qualify holding and retire VALID_TITLE_RETRY

- **Linear (this ticket):** [AST-898](https://linear.app/astralcareermatch/issue/AST-898/new-retry-qualify-holding-and-retire-valid-title-retry-new-jobs-are)
- **Parent (coordination only):** [AST-895](https://linear.app/astralcareermatch/issue/AST-895/new-jobs-are-going-to-valid-title-retry-state) — NEW jobs are going to VALID_TITLE_RETRY state
- **Publish ref:** `origin/sub/AST-895/ast-898-new-retry-qualify-holding`

## Summary

After **AST-797**, `qualify_job_listings` claims jobs in **NEW**, runs inline title screening (`NEW` → `VALID_TITLE` / `INVALID_TITLE`), then the qualify AI hop. Recoverable first-attempt AI failures still look up `JOB_STATES["VALID_TITLE"]["retry_state"]` = **VALID_TITLE_RETRY**, so jobs that entered from **NEW** land in the wrong holding state. This ticket registers **NEW_RETRY**, points both **NEW** and **VALID_TITLE** `retry_state` at **NEW_RETRY**, companion-claims **NEW**+**NEW_RETRY** on the primary qualify row (`trigger_state=NEW`), includes **NEW_RETRY** in the AI hop (skip title re-screen), leaves existing **VALID_TITLE_RETRY** jobs + companion dispatch rows to drain, and stops all new qualify-path traffic from entering **VALID_TITLE_RETRY**.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Register **NEW_RETRY**; set `NEW`/`VALID_TITLE` `retry_state` → **NEW_RETRY**; priors on pass/fail + review UI + grades field | utils |
| `src/core/consult.py` | Qualify AI filter includes **NEW_RETRY**; `_INPUT_STATE_TO_TASK` map; §1.5.1 debug_index on fail→dest for qualify retry routing | core |

**Verify only (Betty / qa-child — engineer does not edit in build-child):**

| File | Change |
|------|--------|
| `tests/component/utils/test_config.py` | `dispatch_claim_states("NEW","job") == ["NEW","NEW_RETRY"]`; `_consult_batch_fail_dest` matrix via config (`VALID_TITLE`→`NEW_RETRY`, `NEW_RETRY`→error); **VALID_TITLE_RETRY** still in registry |
| `tests/component/core/test_consult.py` | Qualify: **NEW** recoverable fail → **NEW_RETRY** (not **VALID_TITLE_RETRY**); **NEW_RETRY** second fail → `ERROR_QUALIFY_JOB_LISTINGS`; **NEW_RETRY** jobs skip `validate_title_batch`; pass/fail from **NEW_RETRY** still reaches `PASSED_JOBLIST`/`FAILED_JOBLIST`; drain path: **VALID_TITLE_RETRY** second fail still terminals |
| `docs/test-bible/utils/config.md`, `docs/test-bible/core/consult.md` | Wording: qualify @ **NEW** companions **NEW_RETRY**; **VALID_TITLE_RETRY** drain-only |

**Out of scope:** qualify grading math; other job retry pairs (`JD_READY`/`JD_READY_RETRY`, etc.); restoring `validate_title` dispatch; migrating existing **VALID_TITLE_RETRY** jobs to **NEW_RETRY**; deleting AST-797 **VALID_TITLE_RETRY** companion `dispatch_task` rows (drain needs them until empty — post-drain cleanup is a follow-up, not this ticket).

---

## Stage 1: JOB_STATES + UI config — NEW_RETRY registry and claim companion

**Done when:** `JOB_STATES` contains **NEW_RETRY** with priors that allow transitions from **NEW** and **VALID_TITLE`; `dispatch_claim_states("NEW", "job")` returns `["NEW", "NEW_RETRY"]`; `_consult_batch_fail_dest`-relevant registry reads send first-attempt **VALID_TITLE** failures to **NEW_RETRY** and **NEW_RETRY** failures to the qualify `error_state` path (no nested retry); Jobs In Review UI / admin state lists surface **NEW_RETRY** with label **"New (retry)"**; **VALID_TITLE_RETRY** remains in the registry and UI for drain visibility.

1. In `src/utils/config.py` `JOB_STATES`, change the **NEW** entry from unrestricted-only to also carry the retry holding pointer:

   ```python
   "NEW": {"prior_states": None, "retry_state": "NEW_RETRY"},
   ```

2. Change the **VALID_TITLE** entry so first-attempt recoverable failures after inline title screening route to **NEW_RETRY** (this is the cutover that stops new traffic into **VALID_TITLE_RETRY**):

   ```python
   "VALID_TITLE": {"prior_states": ["NEW"], "retry_state": "NEW_RETRY"},
   ```

   ⚠️ **Decision:** Keep `retry_state` on **VALID_TITLE** (pointed at **NEW_RETRY**), do **not** invent special-case fail logic inside `consult.py` for this hop. After title screening the entity's current state is **VALID_TITLE**, and `_consult_batch_fail_dest` already reads `JOB_STATES[current]["retry_state"]` (AST-642). Pointing **VALID_TITLE.retry_state** at **NEW_RETRY** is the minimal, config-driven fix for AC1/AC7.

3. Insert **NEW_RETRY** immediately after **VALID_TITLE_RETRY** (keep **VALID_TITLE_RETRY** in place for drain):

   ```python
   "VALID_TITLE_RETRY": {"prior_states": ["VALID_TITLE"]},  # drain-only; no new writes from NEW qualify path
   "NEW_RETRY": {"prior_states": ["NEW", "VALID_TITLE"]},  # qualify_job_listings retry holding (post-AST-898)
   ```

   ⚠️ **Decision:** Priors include both **NEW** (if a fail path ever sees pre-title state) and **VALID_TITLE** (the real post–title-screen state today). Do **not** list **VALID_TITLE_RETRY** as a prior of **NEW_RETRY** — no migrate-in-place.

4. Extend pass/fail priors so second-attempt grade outcomes can leave **NEW_RETRY**:

   - `PASSED_JOBLIST["prior_states"]`: add `"NEW_RETRY"` (keep existing entries including **NEW**, **VALID_TITLE**, **VALID_TITLE_RETRY**, **JD_READY**, **JD_READY_RETRY**).
   - `FAILED_JOBLIST["prior_states"]`: add `"NEW_RETRY"` alongside **VALID_TITLE** and **VALID_TITLE_RETRY**.

5. In `IN_REVIEW_STATES`, insert `"NEW_RETRY"` immediately after `"VALID_TITLE_RETRY"` (ordered list for Jobs UI / nav counts).

6. In `JOBS_IN_REVIEW_UI_SECTIONS`, insert after the **VALID_TITLE_RETRY** row:

   ```python
   {"state": "NEW_RETRY", "label": "New (retry)"},
   ```

   Keep the **VALID_TITLE_RETRY** row labeled `"Valid Title (retry)"` so operators can still see draining jobs.

7. In `JOBS_IN_REVIEW_GRADE_FIELD`, add `"NEW_RETRY": "joblist_grades"` next to the existing `"VALID_TITLE_RETRY": "joblist_grades"` entry.

8. Do **not** edit `src/data/database.py` in this stage (or later): do **not** delete AST-797 `qualify_job_listings` / `VALID_TITLE_RETRY` companion rows; do **not** seed a **NEW_RETRY** companion row — companion claim is registry-driven via `NEW.retry_state` + existing `dispatch_claim_states` (AST-882 pattern). Admin list of job states (`list(JOB_STATES.keys())` in admin) picks up **NEW_RETRY** automatically — no separate admin hardcoded list edit.

**Manual check (no commit of throwaway notes):** from a Python REPL after the edit, `dispatch_claim_states("NEW", "job") == ["NEW", "NEW_RETRY"]` and `dispatch_claim_states("VALID_TITLE_RETRY", "job") == ["VALID_TITLE_RETRY"]`.

---

## Stage 2: qualify_job_listings — AI hop includes NEW_RETRY + debug destinations

**Done when:** A mixed claim of **NEW** + **NEW_RETRY** runs title screening **only** on **NEW** rows; **NEW_RETRY** jobs go straight to the qualify AI hop; recoverable batch failures from **VALID_TITLE** (post-title) transition to **NEW_RETRY**; recoverable failures from **NEW_RETRY** transition to `TASK_CONFIG["qualify_job_listings"]["error_state"]` (`ERROR_QUALIFY_JOB_LISTINGS`); with `debug=True`, each fail→dest path emits a Style D `debug_index` whose `outcome` names the destination so **NEW/VALID_TITLE → NEW_RETRY** is distinguishable from **NEW_RETRY → ERROR_QUALIFY_JOB_LISTINGS**. Clean pass/fail from **NEW_RETRY** still reaches `PASSED_JOBLIST` / `FAILED_JOBLIST` via existing `process` + priors from Stage 1.

1. In `src/core/consult.py` `_INPUT_STATE_TO_TASK`, add:

   ```python
   "NEW_RETRY": "qualify_job_listings",
   ```

   Leave the existing `"VALID_TITLE_RETRY": "qualify_job_listings"` entry (drain / legacy map).

2. In `qualify_job_listings`, change the AI-eligible filter from:

   ```python
   if (j.get("state") or "") in ("VALID_TITLE", "VALID_TITLE_RETRY")
   ```

   to:

   ```python
   if (j.get("state") or "") in ("VALID_TITLE", "VALID_TITLE_RETRY", "NEW_RETRY")
   ```

   Do **not** change the title-screen gate — it must remain `state == "NEW"` only (already true). That is what satisfies AC4 (second attempt = qualify AI only).

   ⚠️ **Decision:** Keep **VALID_TITLE_RETRY** in the AI filter so the drain companion row (trigger **VALID_TITLE_RETRY**) still runs qualify AI without re-title-screening. Removing it would strand drain jobs.

3. Fail routing uses existing `_consult_batch_fail_dest` — **do not** fork a qualify-only dest helper. After Stage 1 config, `_consult_batch_fail_dest("VALID_TITLE", error_state)` returns `"NEW_RETRY"` and `_consult_batch_fail_dest("NEW_RETRY", error_state)` returns `error_state`. Confirm by reading the helper; if the helper body has drifted from AST-642 semantics, **stop and comment on the parent** — do not invent a parallel table.

4. Debug contract (AC8) — when `debug=True`, ensure fail→dest emissions exist on the paths that actually write holding/terminal states for this ticket:

   a. In `_run_batch_consult`, immediately **before** `_transition_batch_consult_failures(task_key, bad_rows, error_state)` (the `bad_grades` block near the end), if `debug` and `bad_rows` is non-empty, loop with index `1..len(bad_rows)` and emit:

   ```python
   logger.debug_index(
       func=f"consult._run_batch_consult({task_key})",
       index=bi,
       total=len(bad_rows),
       identifier=_consult_job_identifier(row),
       outcome=f"bad_grades -> {_consult_batch_fail_dest(row.get('state'), error_state)}",
   )
   logger.debug_detail(
       f"astral_job_id={row.get('astral_job_id')!r} from_state={row.get('state')!r}"
   )
   ```

   (Mirror the existing missing-ID `debug_index` block already above it.)

   b. In `qualify_job_listings` `process`, on the short-title branch that already calls `_consult_batch_fail_dest`, when `debug=True` also emit a `debug_index` (same `func="consult.qualify_job_listings"` style as the input-job headers in that function, or `consult._run_batch_consult(qualify_job_listings)` — pick **one** and stay consistent with nearby headers in that function) with `outcome` like `title too short -> {dest}` and a `|` detail line noting `from_state=…`.

   c. Do **not** emit new debug lines when `debug=False`. Do **not** change grade math or `assemble` / `process` pass/fail destinations beyond the dest string now coming from config.

5. No other files in this stage. Dispatcher already uses `dispatch_claim_states` — Stage 1 makes the NEW companion real without dispatcher edits.

---

## Self-Assessment

**Scope:** `Single-Component` — `config.py` job registry/UI lists plus `consult.py` qualify filter and fail-path debug; no dispatcher/data-layer schema change.

**Conf:** `high` — reuses AST-642 `_consult_batch_fail_dest`, AST-882 registry `retry_state` companion claim, and AST-797 inline title screen; only the holding-state name and AI filter membership change.

**Risk:** `Medium` — wrong priors or dropping **VALID_TITLE_RETRY** from the AI filter would strand retries or break drain; a bug in `VALID_TITLE.retry_state` would either reintroduce **VALID_TITLE_RETRY** traffic or terminal too early.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|-------|
| §1.4 / §2.1 config source of truth | State names and retry pairing live only in `JOB_STATES`; no new hardcoded dest strings in consult beyond existing helper. |
| §2.6 state machine | One-retry: primary (`NEW`/`VALID_TITLE`) → `NEW_RETRY`; holding → `error_state`. Tracker still enforces `prior_states`. |
| §1.5.1 debug | New lines gated on `debug=True`; Style D `debug_index` + `|` detail; no `[DEBUG]` info spam. |
| §1.3 DRY | Reuse `_consult_batch_fail_dest` / `dispatch_claim_states`; no parallel dest map. |
| §3.3 imports | No new cross-layer imports. |

No rule conflicts that would force `conf-!!-NONE`.

## Build

- **Publish tip:** `origin/sub/AST-895/ast-898-new-retry-qualify-holding` @ `1663671370ba8b4d52724be7d41635f1ac87b510`
- Stage 1: `8d0a865` — NEW_RETRY registry + NEW companion claim
- Stage 2: `1663671` — qualify AI hop includes NEW_RETRY + fail-path debug

## Review

_(Radia — review-child)_
