# AST-828 — UAT: draft_cover_letter dispatch crashes on BUILD_ARTIFACTS.finalize_job_resume trigger state

- **Linear:** [AST-828 — UAT: draft_cover_letter dispatch crashes on BUILD_ARTIFACTS.finalize_job_resume trigger state](https://linear.app/astralcareermatch/issue/AST-828/uat-draft-cover-letter-dispatch-crashes-on-build-artifactsfinalize-job)
- **Parent:** [AST-752 — Use agent_data for the "caller" content](https://linear.app/astralcareermatch/issue/AST-752/use-agent-data-for-the-caller-content)
- **Publish ref:** `origin/sub/AST-752/AST-828-draft-cover-letter-compound-state-claim`
- **UAT bug of:** [AST-752](https://linear.app/astralcareermatch/issue/AST-752/use-agent-data-for-the-caller-content) — Susan staging run 2026-06-26 (`draft_cover_letter-fbdbc4dc-c45c-4485-b498-479134903585`, candidate `somerset`, 6 available)
- **Related:** [AST-595](https://linear.app/astralcareermatch/issue/AST-595) / [AST-803](https://linear.app/astralcareermatch/issue/AST-803) (legacy compound `BUILD_ARTIFACTS.<hop>` holding states), [AST-769](https://linear.app/astralcareermatch/issue/AST-769) (general caller hydration — out of scope except dispatch must reach `do_task`)

Scheduled dispatch of **`draft_cover_letter`** with **`trigger_state='BUILD_ARTIFACTS.finalize_job_resume'`** crashes before any LLM hop runs. Log: **`ValueError: Value 'BUILD_ARTIFACTS.finalize_job_resume' not in allowed list`** from **`get_new_job_batch`** → **`validate_value(_JOB_STATE_LIST, s)`**. Susan had **6 available** jobs (count path OK) but claim never starts.

**Root cause:** **`_JOB_STATE_LIST`** is **`list(JOB_STATES.keys())`** — flat registry only. Legacy compound holding states **`BUILD_ARTIFACTS.<hop>`** (AST-595 / AST-803) live on in-flight job rows and in **`prior_states`** references but are **not** keys in **`JOB_STATES`**. **`database.claim_job_batch`** and **`count_eligible_for_dispatch_task`** already accept arbitrary state strings in SQL; only **`tracker.get_new_job_batch`** rejects compound states at validation time. Resume-artifact hop dispatch avoids this when **`input_state == BUILD_ARTIFACTS`** because **`build_artifacts_claim_states()`** expands claim list — but **`draft_cover_letter`** (and any dispatch row) may legitimately target a **specific** compound hop holding state without going through flat **`BUILD_ARTIFACTS`**.

**Boundaries:** Fix batch-claim validation only so compound **`BUILD_ARTIFACTS.*`** states recognized by **`legacy_build_artifacts_hop`** are claimable. Does **not** add compound keys to **`JOB_STATES`**, change **`{$CALLER_*}`** hydration (**AST-769**), dispatch_task seeding (**AST-741** / **AST-745**), cover-letter chain logic, or state-transition rules in **`transition_job_state`**.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add **`is_valid_job_batch_claim_state(state)`** — flat **`JOB_STATES`** keys **or** legacy compound hop via **`legacy_build_artifacts_hop`** | utils |
| `src/core/tracker.py` | Replace **`validate_value(_JOB_STATE_LIST, …)`** in **`get_new_job_batch`** with the new helper (single-state and **`states=`** list paths) | core |

**Verify only (Betty / qa-child — engineer does not edit in build-child):**

| File | Change |
|------|--------|
| `tests/component/core/test_tracker.py` | Assert **`get_new_job_batch("BUILD_ARTIFACTS.finalize_job_resume", batch_id=…)`** does not raise; invalid compound suffix still raises |
| `tests/component/utils/test_config.py` | Unit tests for **`is_valid_job_batch_claim_state`** true/false cases |

**No changes expected:** `src/core/dispatcher.py`, `src/core/agent.py`, `src/core/consult.py`, `src/data/database.py`, `data/admin/*`, frontend.

---

## Stage 1: Confirm validation gap (investigation — no product commit unless regression)

**Done when:** Engineer reproduces that **`get_new_job_batch("BUILD_ARTIFACTS.finalize_job_resume", batch_id="probe-828")`** raises **`ValueError`** today, while **`legacy_build_artifacts_hop("BUILD_ARTIFACTS.finalize_job_resume")`** returns **`"finalize_job_resume"`** and **`count_eligible`** for Susan's dispatch row returns **> 0** without raising.

1. Read-only config check:
   ```bash
   python3 -c "
   from src.utils.config import legacy_build_artifacts_hop, JOB_STATES, build_artifacts_claim_states
   s = 'BUILD_ARTIFACTS.finalize_job_resume'
   print('hop', legacy_build_artifacts_hop(s))
   print('in JOB_STATES', s in JOB_STATES)
   print('in claim_states', s in build_artifacts_claim_states())
   "
   ```
   Expect: hop **`finalize_job_resume`**, **`in JOB_STATES False`**, **`in claim_states True`**.

2. Confirm crash site:
   ```bash
   rg -n "validate_value\\(_JOB_STATE_LIST" src/core/tracker.py
   ```
   Expect matches inside **`get_new_job_batch`** only (not **`transition_job_state`** in this ticket).

3. Repro (component-test DB or local):
   ```python
   import pytest
   from src.core import tracker as tracker_mod
   with pytest.raises(ValueError, match="not in allowed list"):
       tracker_mod.get_new_job_batch("BUILD_ARTIFACTS.finalize_job_resume", batch_id="probe-828")
   ```

4. **Stop gate:** If **`get_new_job_batch`** already accepts compound states on this branch — post 🛑 on **AST-752** with evidence; do not proceed (different root cause).

---

## Stage 2: Allow legacy compound states at batch claim validation

**Done when:** **`get_new_job_batch("BUILD_ARTIFACTS.finalize_job_resume", batch_id=…)`** returns **`(batch_id, [])`** or claims matching rows without **`ValueError`**; flat states (**`CANDIDATE_REVIEW`**, **`NEW`**) unchanged; **`BUILD_ARTIFACTS.not_a_hop`** still rejected.

1. In **`src/utils/config.py`**, immediately after **`legacy_build_artifacts_hop`** (~line 2980), add:

   ```python
   def is_valid_job_batch_claim_state(state: str) -> bool:
       """True for JOB_STATES keys and legacy BUILD_ARTIFACTS.<hop> holding states (batch claim only)."""
       s = (state or "").strip()
       if not s:
           return False
       if s in JOB_STATES:
           return True
       return legacy_build_artifacts_hop(s) is not None
   ```

   ⚠️ **Decision:** Claim-time validation only — **`transition_job_state`** keeps **`validate_value(_JOB_STATE_LIST, to_state)`** so compound holding states are not promoted to full registry entries (ticket boundary).

2. In **`src/core/tracker.py`**, import **`is_valid_job_batch_claim_state`** from **`src.utils.config`** (same block as **`validate_value`**).

3. Add private helper above **`get_new_job_batch`**:

   ```python
   def _assert_valid_job_batch_claim_state(state: str) -> None:
       if not is_valid_job_batch_claim_state(state):
           raise ValueError(
               f"Value {state!r} not in allowed list: {_JOB_STATE_LIST} "
               f"(legacy BUILD_ARTIFACTS.<hop> holding states are claim-only)"
           )
   ```

4. In **`get_new_job_batch`**, replace both **`validate_value(_JOB_STATE_LIST, state)`** and the **`for s in states: validate_value(...)`** loop with **`_assert_valid_job_batch_claim_state`** on each state string.

5. **Do not** change **`initialize_job`**, **`transition_job_state`**, or **`dispatcher._run_unified`** in this ticket.

6. Compile check:
   ```bash
   python3 -m py_compile src/utils/config.py src/core/tracker.py
   ```

7. Manual sanity (engineer, after Betty tests or local repro):
   - Dispatch **`draft_cover_letter`** with **`trigger_state='BUILD_ARTIFACTS.finalize_job_resume'`** on a job in that state — log shows claim + **`do_task`** start, not **`crashed`** with config validation error.
   - Default **`CANDIDATE_REVIEW`** **`draft_cover_letter`** row still claims (parity).

---

## Self-Assessment

**Scope:** `Single-Component` — Two files at config/tracker boundary: one claim-validation helper and one batch API guard; no dispatcher or agent hydration changes.

**Conf:** `high` — Stack trace and code path match exactly; **`legacy_build_artifacts_hop`** and **`build_artifacts_claim_states()`** already define the allowed compound set; fix mirrors existing AST-803 compound-state recognition in **`_dispatch_sort_by_for`**.

**Risk:** `low` — Over-broad acceptance would only allow claim on malformed **`BUILD_ARTIFACTS.*`** strings that **`legacy_build_artifacts_hop`** rejects; state transitions and **`JOB_STATES`** registry remain unchanged.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Single helper in config; tracker calls it once per state — no duplicated compound-prefix checks. |
| §2.1 Config as source of truth | Compound hop set derived from existing **`resume_artifact_hop_task_keys()`** via **`legacy_build_artifacts_hop`** — no new state lists. |
| §2.4 Batch processing | Fixes claim entry for batch dispatch; **`claim_job_batch`** SQL unchanged. |
| §2.6 State machine | **`transition_job_state`** validation untouched — compound states remain in-flight holding labels only. |
| §3.3 Imports | Tracker already imports config; one new symbol — no new cross-layer violations. |
| §3.5 Naming | Helper describes claim boundary, not general job-state membership. |

No conflicts requiring plan revision.

---

## Review

**Diff:** `origin/ftr/AST-752-agent-data-caller-content...origin/sub/AST-752/AST-828-draft-cover-letter-compound-state-claim` @ `aa6b161` (republished linear sub-log)

| Area | Notes |
|------|-------|
| Stage 2 | `is_valid_job_batch_claim_state` in config; `_assert_valid_job_batch_claim_state` in tracker `get_new_job_batch` only |
| Boundaries | `transition_job_state` / `initialize_job` unchanged; no dispatcher or agent changes |
| Verify | Compound `BUILD_ARTIFACTS.finalize_job_resume` claims without ValueError; `BUILD_ARTIFACTS.not_a_hop` still rejected |

Betty manifest green @ `8f4ec67`. Awaiting Radia **review-child**.
