<!-- linear-archive: AST-804 archived 2026-07-22 -->

## Linear archive (AST-804)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-804/dispatch-task-admin-validation-for-candidate-entity-type-over  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-799 — Over-validation on entity type for candidate  
**Blocked by / blocks / related:** parent: AST-799

### Description

## What this implements

Align Admin Scheduled Actions save/update validation with config dispatch defaults so candidate-scoped dispatch rows (starting with **inflow_discovery**) are accepted when task_key and trigger_state are valid per config — no spurious "unsupported entity_type" errors for types in **ENTITY_TYPES**. Validate candidate trigger_state against **CANDIDATE_STATES** the same way job and company rows use **JOB_STATES** / **COMPANY_STATES**. Expose candidate states on the admin state-options endpoint when the Scheduled Actions UI needs them for trigger_state selection.

## Acceptance criteria

1. **Susan's repro cleared:** PUT on an **inflow_discovery** dispatch row for a live candidate (e.g. somerset / id 5373) with trigger_state **LIVE_PROMPTS** returns success — not HTTP 400 with `unsupported entity_type 'candidate'`.
2. **Scheduled Actions edit path:** From Admin → Scheduled Actions, an existing **inflow_discovery** row can be edited and saved without error when values match config defaults.
3. **Invalid candidate state still rejected:** A candidate-scoped task_key with a trigger_state **not** in **CANDIDATE_STATES** is rejected with a clear error (behavior parallel to invalid job/company states).
4. **Regression:** Job- and company-scoped dispatch task save/update behavior unchanged for representative task_keys (e.g. **grade_do**, **vet_inflow_discovery**).
5. **Future-proofing:** A schedulable task_key whose config-derived entity_type is **candidate**, **company**, or **job** per **ENTITY_TYPES** is saveable without adding entity-type-specific branches only in the admin layer.

## Boundaries

* Does **not** change inflow discovery batch execution, dispatcher claim logic, or database eligibility counts.
* Does **not** reintroduce retired entity types (e.g. legacy **board_search**) as schedulable.
* Does **not** redesign Scheduled Actions layout or edit-modal task_key picker (AST-773).
* Sibling scope: none — single implementation ticket for this parent.

## Notes for planning

* Root cause: `_dispatch_task_key_trigger_error` in admin API only validates job/company branches; **candidate** falls through to unsupported even though config and dispatcher support it.
* Prefer deriving validation from `dispatch_task_admin_defaults` / **ENTITY_TYPES** rather than expanding inline elif chains.
* `dispatch_task_state_options` currently returns job/company only — add candidate when UI needs it.
* Betty owns test manifest updates; engineer posts Code Complete handoff for qa.

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/AST-799-dispatch-task-entity-type-validation`, child `sub/AST-799/<child-segment>`, standalone `ftr/<segment>`. Created at **dispatch-parent**. Engineers publish to `origin/sub/…` — never Linear `gitBranchName` when it disagrees.

### Comments

#### chuckles — 2026-06-25T06:04:10.744Z
[merge-child] blocked: validate-sub-log — missing plan(AST-804): on origin/sub/AST-799/AST-804-dispatch-task-admin-candidate-entity-validation (plan landed as docs(AST-804): plan — …). Republish with canonical plan(AST-804): prefix per validate-sub-log.sh (@Katherine Johnson)

#### radia — 2026-06-25T06:00:20.567Z
### AST-804 review — `origin/dev...origin/sub/AST-799/AST-804-dispatch-task-admin-candidate-entity-validation` @ `6d8691b`

**fix-now:** None.

**discuss:** None.

**advisory:** None.

**Plan fidelity:** Stage 1 + 2 match combined plan — `dispatch_entity_state_registry`, refactored `_dispatch_task_key_trigger_error` (ENTITY_TYPES + CANDIDATE_STATES), POST create + PUT trigger_state-only validation, `state_options.candidate`, Scheduled Actions `inputStateOptions` for candidate rows. Out-of-scope areas untouched (dispatcher, eligibility, AST-773 picker).

**ASTRAL_CODE_RULES:** §1.3 DRY registry helper · §1.4 / §2.1 config-driven state validation · §3.2 UI resolves Input State from API · §3.3 layer imports clean. No §5f/§5g surface.

**Tests:** Betty manifest covers helper paths, POST/PUT HTTP, state_options, and edit-modal candidate Input State (`TestAst804CandidateDispatchAdminValidation` + frontend describe).

**Doc:** `docs/features/foundation/ast-804-dispatch-task-admin-candidate-entity-validation.md` — Radia review section @ `6d8691b`.

**Outcome:** Clean — Katherine → `resolve-child`.

#### betty — 2026-06-25T05:55:16.486Z
## QA test manifest (Tests Ready)

1. **Pytest (required):**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst804CandidateDispatchAdminValidation \
  -q
```

2. **Vitest (required — §6c routed page):**
```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  --testNamePattern="AST-804"
```

**Coverage map:**
- `_dispatch_task_key_trigger_error`: inflow_discovery + LIVE_PROMPTS → None; invalid candidate state → error; grade_do / vet_inflow_discovery regression unchanged
- POST create + PUT trigger_state-only validation for candidate entity rows
- `GET /api/admin/dispatch_tasks/state_options` includes candidate with LIVE_PROMPTS
- Scheduled Actions edit modal: candidate Input State options for inflow_discovery (not job PASSED_JD)

**Bible shasums (origin/sub/AST-799/AST-804-dispatch-task-admin-candidate-entity-validation):**
- docs/test-bible/ui/api/api_admin.md — 3cb0a964fb0b12c77df5504c365d948116400c239ba32909ab70311c8dc0fffd
- docs/test-bible/frontend/pages.md — 898a603d126ac038b307cdffb0d9279dedbb7f21f0037588d523b3ce0448c35f

**Publish:** origin/sub/AST-799/AST-804-dispatch-task-admin-candidate-entity-validation @ 8108fc1 (merge-tests(AST-804): origin/tests d80f757)

#### katherine — 2026-06-25T05:50:41.437Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-799/AST-804-dispatch-task-admin-candidate-entity-validation/docs/features/foundation/ast-804-dispatch-task-admin-candidate-entity-validation.md

Two build stages — config registry + admin validation (POST/PUT + state_options), then Scheduled Actions UI candidate Input State options. Root fix: `_dispatch_task_key_trigger_error` currently rejects all non-job/company entity types; plan routes validation through `dispatch_entity_state_registry` keyed by **ENTITY_TYPES**.

**Self-assessment**
- **Scope:** Single-Component — `config.py`, `api_admin.py`, `AdminScheduledActions.tsx` only.
- **Conf:** high — single missing candidate branch in a known helper; dispatcher/config already support **inflow_discovery** / **LIVE_PROMPTS**.
- **Risk:** Medium — admin save path is critical for Scheduled Actions; job/company regression covered in Betty manifest.

---

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

---

## Review (build)

**Built:** `origin/sub/AST-799/AST-804-dispatch-task-admin-candidate-entity-validation` @ `6358a7b`

Stage 1: `dispatch_entity_state_registry` in config; `_dispatch_task_key_trigger_error` validates all **ENTITY_TYPES** members via **CANDIDATE_STATES**; POST create + PUT trigger_state-only validation; `state_options` includes **candidate**.

Stage 2: `AdminScheduledActions` loads **candidate** state options and uses them in Input State when `entity_type === "candidate"`.

**Betty / qa-child:** Manifest in plan QA table — `test_api_admin.py` candidate validation + PUT success; `test_AdminScheduledActions.test.tsx` candidate state_options normalization.

---

## Radia review (2026-06-25)

**Diff:** `origin/dev...origin/sub/AST-799/AST-804-dispatch-task-admin-candidate-entity-validation` @ `8108fc1`  
**Product commits:** `2309bd5` config + api_admin · `6358a7b` AdminScheduledActions  
**Tests:** `d80f757` (Betty manifest on `origin/tests`)

### What's solid

| Area | Notes |
|------|-------|
| Stage 1 — config helper | `dispatch_entity_state_registry` maps job/company/candidate to state registries; KeyError path preserves unsupported-entity_type message shape. |
| Stage 1 — admin validation | `_dispatch_task_key_trigger_error` uses ENTITY_TYPES + registry lookup; **inflow_discovery** + **LIVE_PROMPTS** passes; invalid candidate state rejected; **resume_artifact_hop_task_keys** guard unchanged. |
| POST / PUT coverage | `create_dtask` validates before save; `update_dtask` `elif trigger_state`-only branch closes the gap when task_key is omitted. |
| state_options | `candidate` key exposes **CANDIDATE_STATES** keys (incl. **LIVE_PROMPTS**). |
| Stage 2 — UI | `stateOptions.candidate` loaded/normalized; `inputStateOptions` useMemo selects candidate states when `entity_type === "candidate"`. |
| §1.3 / §1.4 / §2.1 | DRY registry helper; no hardcoded state lists; config-driven validation via `dispatch_task_admin_defaults`. |
| §3.3 | `api_admin` imports config symbols only; no layer violations. |
| §3.2 UI config-driven | Input State options from API payload, not duplicated in React. |
| Plan Self-Assessment | Scope Single-Component matches diff; no sibling bleed (dispatcher/eligibility out of scope). |
| Tests + bible | `TestAst804CandidateDispatchAdminValidation` (5 cases) + frontend describe; bible rows in `api_admin.md` / `pages.md`. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| — | — | None. |

### Recommended actions

| Action | Owner |
|--------|-------|
| None blocking | — |

**Counts:** 0 fix-now · 0 discuss · 0 advisory

**Outcome:** Clean — Katherine may proceed with `resolve-child` (§9a dry-run).

---

## Resolution (2026-06-25)

Radia review had **zero fix-now / discuss / advisory** items — no product changes in resolve pass. Betty manifest green (pytest 5/5, Vitest 1/1). §9a dry-run: publish ref merges cleanly into **`origin/dev`** and **`origin/ftr/AST-799-dispatch-task-entity-type-validation`**.

**Publish tip:** `origin/sub/AST-799/AST-804-dispatch-task-admin-candidate-entity-validation` @ `6d8691b`
