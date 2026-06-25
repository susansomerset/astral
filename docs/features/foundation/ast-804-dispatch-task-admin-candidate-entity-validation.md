# AST-804 — Dispatch task admin validation for candidate entity type

**Linear:** [AST-804 — Dispatch task admin validation for candidate entity type (Over-validation on entity type for candidate)](https://linear.app/astralcareermatch/issue/AST-804/dispatch-task-admin-validation-for-candidate-entity-type-over)  
**Parent:** [AST-799 — Over-validation on entity type for candidate](https://linear.app/astralcareermatch/issue/AST-799/over-validation-on-entity-type-for-candidate)  
**Publish ref:** `origin/sub/AST-799/AST-804-dispatch-task-admin-candidate-entity-validation`

## Summary

Scheduled Actions save/update rejects candidate-scoped dispatch rows because `_dispatch_task_key_trigger_error` in `api_admin.py` validates only job and company entity types and treats everything else as unsupported — even when `dispatch_task_admin_defaults` and the dispatcher already support **candidate** (e.g. **inflow_discovery** at **LIVE_PROMPTS**). This ticket aligns admin validation with **ENTITY_TYPES** and the existing state registries (**CANDIDATE_STATES** alongside **JOB_STATES** / **COMPANY_STATES**), exposes candidate states on the state-options endpoint, and wires the Scheduled Actions edit modal to use them. No dispatcher, eligibility count, or inflow batch execution changes.

**Root cause (verified on branch):** `_dispatch_task_key_trigger_error` (~line 931) has `if et == "job"` / `elif et == "company"` / `else: unsupported`. **inflow_discovery** derives `entity_type="candidate"` from config; PUT from the edit modal always includes `task_key`, so Susan's repro hits this path.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `dispatch_entity_state_registry(entity_type)` mapping **ENTITY_TYPES** members to their state dicts | utils |
| `src/ui/api/api_admin.py` | Refactor `_dispatch_task_key_trigger_error`; import `CANDIDATE_STATES`, `ENTITY_TYPES`, `dispatch_entity_state_registry`; call validation on POST create and PUT trigger_state-only updates; add `candidate` to `dispatch_task_state_options` | ui |
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Extend `stateOptions` type/load; pick candidate states for Input State when `form.entity_type === "candidate"` | ui |

**QA manifest (Betty — not engineer commits):**

| File | Change |
|------|--------|
| `tests/component/ui/api/test_api_admin.py` | Extend `_dispatch_task_key_trigger_error` helper tests: **inflow_discovery** + **LIVE_PROMPTS** → `None`; invalid candidate state → error; regression **grade_do** / **vet_inflow_discovery** unchanged; PUT success for candidate row; `state_options` includes **candidate** with **LIVE_PROMPTS** |
| `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` | Normalize/load `candidate` array from state_options payload; assert Input State options include **LIVE_PROMPTS** when editing **inflow_discovery** row |

**Out of scope:** `database.py` eligibility counts; dispatcher claim/run; retired **board_search** rows (AST-781); edit-modal task_key picker redesign (AST-773); adding new schedulable task keys beyond config.

---

## Stage 1: Config registry helper + admin validation

**Done when:** `_dispatch_task_key_trigger_error("inflow_discovery", "LIVE_PROMPTS")` returns `None`; `_dispatch_task_key_trigger_error("inflow_discovery", "NOT_A_CANDIDATE_STATE")` returns a non-empty error mentioning **inflow_discovery**; `_dispatch_task_key_trigger_error("grade_do", "PASSED_JD")` and `_dispatch_task_key_trigger_error("vet_inflow_discovery", "NEW")` still return `None`; `GET /api/admin/dispatch_tasks/state_options` JSON includes `"candidate"` with **LIVE_PROMPTS**; `python3 -m py_compile src/utils/config.py src/ui/api/api_admin.py` passes.

1. In `src/utils/config.py`, immediately after the **`ENTITY_TYPES`** declaration (~line 717), add:

   ```python
   def dispatch_entity_state_registry(entity_type: str) -> Dict[str, Any]:
       """Return the state registry for a dispatch entity_type (ENTITY_TYPES members only)."""
       registries: Dict[str, Dict[str, Any]] = {
           "job": JOB_STATES,
           "company": COMPANY_STATES,
           "candidate": CANDIDATE_STATES,
       }
       if entity_type not in registries:
           raise KeyError(f"unknown dispatch entity_type: {entity_type!r}")
       return registries[entity_type]
   ```

   ⚠️ **Decision:** Helper lives in **config** (rules §2.1) so admin validation and any future callers share one map keyed by **ENTITY_TYPES** — no parallel elif chains in the API layer.

2. In `src/ui/api/api_admin.py`, extend the existing `from src.utils.config import (...)` block to include **`CANDIDATE_STATES`**, **`ENTITY_TYPES`**, and **`dispatch_entity_state_registry`**.

3. In **`_dispatch_task_key_trigger_error`** (~line 916), replace the job/company `if`/`elif`/`else unsupported` block with:

   - After resolving `defaults = dispatch_task_admin_defaults(tk)` and validating `ts`, set `et = defaults["entity_type"]`.
   - If `et not in ENTITY_TYPES`, return `f"task_key {tk!r} has unsupported entity_type {et!r}"` (preserves existing message shape for retired/unknown types).
   - Call `dispatch_entity_state_registry(et)` inside `try`/`except KeyError` — on **KeyError**, return the same unsupported-entity_type message.
   - If `ts not in registry`, return `f"task_key {tk!r} ({et}) is not valid for trigger_state {ts!r}"` (parallel wording to existing job/company errors).
   - **Keep unchanged** the trailing **`resume_artifact_hop_task_keys()`** guard (job-only BUILD_ARTIFACTS hop rules) after entity/trigger validation.

4. In **`create_dtask`** (~line 877), after the retired-key check and **before** the `save_dispatch_task` try block, add:

   ```python
   tk_err = _dispatch_task_key_trigger_error(data.get("task_key", ""), data.get("trigger_state"))
   if tk_err:
       return jsonify({"error": tk_err}), 400
   ```

5. In **`update_dtask`** (~line 945), extend validation coverage:
   - Existing block when `"task_key" in data` stays as-is (already calls `_dispatch_task_key_trigger_error`).
   - Add an **`elif "trigger_state" in data:`** branch (when task_key is not being changed) that calls `_dispatch_task_key_trigger_error(row.get("task_key", ""), data.get("trigger_state"))` and returns 400 on error.

6. In **`dispatch_task_state_options`** (~line 866), change the return to:

   ```python
   return jsonify({
       "job": list(JOB_STATES.keys()),
       "company": list(COMPANY_STATES.keys()),
       "candidate": list(CANDIDATE_STATES.keys()),
   })
   ```

7. Manual smoke (engineer, before Code Complete comment):

   ```bash
   python3 -m py_compile src/utils/config.py src/ui/api/api_admin.py
   python3 -c "
   from src.ui.api import api_admin as adm
   assert adm._dispatch_task_key_trigger_error('inflow_discovery', 'LIVE_PROMPTS') is None
   bad = adm._dispatch_task_key_trigger_error('inflow_discovery', 'PASSED_JD')
   assert bad and 'inflow_discovery' in bad
   assert adm._dispatch_task_key_trigger_error('grade_do', 'PASSED_JD') is None
   assert adm._dispatch_task_key_trigger_error('vet_inflow_discovery', 'NEW') is None
   print('ok')
   "
   ```

8. Post **Code Complete** Linear comment on AST-804 noting Betty manifest items in the QA table above. Engineer does **not** edit `tests/` or `docs/test-bible/**`.

---

## Stage 2: Scheduled Actions UI — candidate Input State options

**Done when:** Edit modal for a row with `entity_type="candidate"` (e.g. **inflow_discovery**) shows **LIVE_PROMPTS** (and other **CANDIDATE_STATES** keys) in the Input State `<select>` instead of job states; `npm run build` in `src/ui/frontend` succeeds.

1. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx`, change the `stateOptions` state type from `{ job: string[]; company: string[] }` to `{ job: string[]; company: string[]; candidate: string[] }` with default `{ job: [], company: [], candidate: [] }`.

2. In **`loadData`**, when parsing `statesRes`, set:

   ```typescript
   candidate: Array.isArray(states?.candidate) ? states.candidate : [],
   ```

   alongside existing `job` / `company` normalization.

3. Replace the Input State option source (~line 845):

   ```typescript
   const inputStateOptions =
     form.entity_type === "company"
       ? stateOptions.company
       : form.entity_type === "candidate"
         ? stateOptions.candidate
         : stateOptions.job
   ```

   Use `inputStateOptions.map(...)` in the `<select>`.

4. Run `cd src/ui/frontend && npm run build` before stage commit.

---

## Self-Assessment

**Scope:** `Single-Component` — Three product files (`config.py`, `api_admin.py`, `AdminScheduledActions.tsx`) in utils + admin API + one admin page; no core/dispatcher/data layer.

**Conf:** `high` — Root cause is a single missing branch in a known helper; config and dispatcher already treat candidate as first-class; pattern mirrors existing job/company validation and AST-773 edit-modal wiring.

**Risk:** `Medium` — Admin save validation is on the critical path for Scheduled Actions configuration; incorrect refactor could reject valid job/company rows or accept invalid states — mitigated by preserving message shapes and explicit regression checks in Betty manifest.

---

## ASTRAL_CODE_RULES check

| Rule | Status |
|------|--------|
| §1.3 DRY | `dispatch_entity_state_registry` replaces duplicated entity-type branching |
| §1.4 no hardcoded sets | Validation uses **JOB_STATES**, **COMPANY_STATES**, **CANDIDATE_STATES**, **ENTITY_TYPES** from config |
| §2.1 config source of truth | Admin acceptance driven by `dispatch_task_admin_defaults` + state registries |
| §2.6 state machine | Candidate trigger_state validated against **CANDIDATE_STATES** same as job/company |
| §3.3 imports | New symbols imported through existing config import block in `api_admin.py` |
| Layer boundaries | UI API + config helper only; no data/core changes |

No conflicts.
