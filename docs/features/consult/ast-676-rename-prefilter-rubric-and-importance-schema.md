# AST-676 — Rename prefilter rubric task and require importance in craft rubric schema

**Linear:** [AST-676](https://linear.app/astralcareermatch/issue/AST-676/rename-prefilter-rubric-task-and-require-importance-in-craft-rubric)  
**Parent:** [AST-655](https://linear.app/astralcareermatch/issue/AST-655/update-criteria-prompts-to-specify-the-importance-and-explain-what)  
**Publish ref:** `origin/sub/AST-655/AST-676-rename-prefilter-rubric-and-importance-schema`  
**Project:** Team Astral

## Summary

Rename the company prefilter craft task key from **`craft_company_prefilter`** to **`craft_prefilter_rubric`** in backend/config/tests/non-UI call sites (stored artifact key **`company_prefilter`** unchanged). Extend **`TASK_CONFIG`** response validation for all six rubric craft tasks so every `criteria` item requires integer **`importance`** in **1–10**, enforced at **`do_task`** schema validation with clear errors. UI task rename (**AST-677**) and admin prompt bodies (**AST-678**) are sibling scope — this ticket lands config + validator only.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Rename task key; add shared rubric criterion `items_schema`; wire all six craft rubric `response_schema` entries | utils |
| `src/core/agent.py` | Extend `_validate_response_schema` for int `min`/`max` and bool rejection | core |
| `tests/component/core/test_agent.py` | Tests for int bounds, bool rejection, craft rubric criterion schema | tests |
| `tests/component/utils/test_config.py` | Assert renamed task key present; shared schema shape | tests |
| `scripts/spikes/ast438_admin_prompt_rubric_diagnostic.py` | Update rubric task key list | scripts |

**Out of scope (sibling tickets):** `src/ui/frontend/**` (**AST-677**), admin prompt DB rows (**AST-678**), consult scoring math, rubric UI editor behavior, feature doc archives under `docs/features/**` (historical references to old task key may remain).

## Stage 1: Shared rubric criterion schema + task key rename

**Done when:** `TASK_CONFIG` contains **`craft_prefilter_rubric`** (not **`craft_company_prefilter`**) with the same phase/seq/flags as today; all six rubric craft tasks share one criterion `items_schema` requiring `label`, `content`, and `importance`; `grep craft_company_prefilter src/` returns only the UI file (out of scope).

1. In `src/utils/config.py`, immediately **before** the Phase B craft rubric block (currently `"craft_company_prefilter"`), add module-level constants:

   ```python
   _CRAFT_RUBRIC_CRITERION_ITEMS_SCHEMA: Dict[str, Dict[str, Any]] = {
       "label": {"type": "str", "required": True},
       "content": {"type": "str", "required": True},
       "importance": {"type": "int", "required": True, "min": 1, "max": 10},
   }
   _CRAFT_RUBRIC_CRITERIA_RESPONSE_SCHEMA: Dict[str, Dict[str, Any]] = {
       "criteria": {
           "type": "list",
           "required": True,
           "items_schema": _CRAFT_RUBRIC_CRITERION_ITEMS_SCHEMA,
       },
   }
   ```

   Use the same `Dict` / `Any` imports already present in the file.

2. Rename the **`TASK_CONFIG`** entry key **`craft_company_prefilter`** → **`craft_prefilter_rubric`**. Keep **`phase`**, **`seq`**, **`entity_type`**, **`requires_candidate_key`**, **`trigger_state`**, and **`response_format`** unchanged.

3. For **`craft_prefilter_rubric`** and each of **`craft_joblist_rubric`**, **`craft_jobdesc_rubric`**, **`craft_get_rubric`**, **`craft_do_rubric`**, **`craft_like_rubric`**, set:

   ```python
   "response_schema": _CRAFT_RUBRIC_CRITERIA_RESPONSE_SCHEMA,
   ```

   replacing the inline `criteria` / `items_schema` blocks (label + content only).

4. Do **not** change **`RUBRIC_CRITERIA_ARTIFACT_KEYS`**, **`company_prefilter`** artifact key, token names, or consult task keys.

⚠️ **Decision:** Bounds are literal `min: 1`, `max: 10` on the schema field (matching `ASTRAL_CONFIG["consult_importance"]`) rather than a dynamic `"bounds": "consult_importance"` indirection — keeps `_validate_response_schema` generic and avoids config coupling in the validator loop.

## Stage 2: Enforce int min/max (and reject bool) in response schema validation

**Done when:** `_validate_response_schema` rejects missing `importance`, non-int values, bool masquerading as int, and integers outside `[min, max]` when those keys are present on the field spec; existing tests for str/list/enum validation still pass.

1. In `src/core/agent.py`, inside `_validate_response_schema`, in the per-field loop after the existing `type_spec == "int"` isinstance check, add:

   - If `type_spec == "int"` and `isinstance(val, bool)`: return `f"Field '{field_name}' must be int, got bool"`.
   - If `type_spec == "int"` and `isinstance(val, int)` (and not bool): read optional `field_spec.get("min")` and `field_spec.get("max")`. When `min` is not `None` and `val < min`, return `f"Field '{field_name}' must be >= {min}, got {val}"`. When `max` is not `None` and `val > max`, return `f"Field '{field_name}' must be <= {max}, got {val}"`.

2. Place the bool guard **before** the existing `if type_spec == "int" and not isinstance(val, int)` line so `True`/`False` are not accepted as integers (Python `isinstance(True, int)` is true).

3. Do **not** change save-path **`normalize_rubric_artifacts_on_save`** / **`_normalize_importance_value`** behavior in this ticket.

## Stage 3: Tests and spike script reference update

**Done when:** Component tests cover the new validation rules and renamed task key; `pytest tests/component/core/test_agent.py tests/component/utils/test_config.py -q` passes for the new/edited tests (full manifest is Betty's **`merge-tests`** pass).

1. In `tests/component/core/test_agent.py`, extend **`TestValidateResponseSchema`** (or add a focused class adjacent to it):

   - Assert `_validate_response_schema` with a schema item `{"importance": {"type": "int", "required": True, "min": 1, "max": 10}}` returns `None` for payload `importance: 5`.
   - Assert missing required `importance` returns a message containing `Missing required field 'importance'`.
   - Assert `importance: True` returns a message containing `must be int, got bool`.
   - Assert `importance: 0` returns `must be >= 1`.
   - Assert `importance: 11` returns `must be <= 10`.
   - Assert nested list validation: schema matching `_CRAFT_RUBRIC_CRITERIA_RESPONSE_SCHEMA` with `criteria: [{"label": "L", "content": "c", "importance": 5}]` passes; omitting `importance` on the item returns an error containing `criteria[0]`.

2. In `tests/component/utils/test_config.py`, add tests:

   - `assert "craft_prefilter_rubric" in cfg.TASK_CONFIG`
   - `assert "craft_company_prefilter" not in cfg.TASK_CONFIG`
   - For `craft_prefilter_rubric` and one other rubric task (e.g. `craft_get_rubric`), assert `response_schema["criteria"]["items_schema"]["importance"]` equals `{"type": "int", "required": True, "min": 1, "max": 10}`.

3. In `scripts/spikes/ast438_admin_prompt_rubric_diagnostic.py`, replace **`craft_company_prefilter`** with **`craft_prefilter_rubric`** in the rubric task key tuple/list (line ~40).

4. Do **not** edit `tests/` files beyond the two component test modules above in this ticket.

## Self-Assessment

**Scope — `Single-Component`**  
Touches `config.py` schema registry, one validator function in `agent.py`, two component test modules, and one spike script — no UI, dispatcher, or consult scoring paths.

**Conf — `high`**  
Follows existing `response_schema` / `_validate_response_schema` patterns; bounds mirror landed `consult_importance` and `_normalize_importance_value`; rename is a straight key swap with shared schema constant.

**Risk — `Medium`**  
All six rubric **Generate** runs fail schema validation until models return `importance` (expected — prompts updated in **AST-678**); between this merge and **AST-677**, Company Watch UI still calls the old task key and will 404/fail lookup until the UI sibling lands.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|-------|
| §1.3 DRY | Single `_CRAFT_RUBRIC_CRITERIA_RESPONSE_SCHEMA` for six tasks; one validator change for int bounds. |
| §1.4 | Importance bounds declared in config schema; no magic `1`/`10` in core beyond field spec. |
| §2.1 Config | Task registry and response shapes live in `config.py`. |
| §2.4 Batch | N/A — craft tasks are on-demand, not batch dispatch. |
| §2.6 State machine | N/A — no new transitions. |
| §3.3 Imports | Core validator unchanged import graph; config constants stay in utils. |
| §3.5 Naming | `craft_prefilter_rubric` aligns with sibling `craft_*_rubric` keys. |

**Conflicts:** None blocking. Temporary UI/task-key mismatch until **AST-677** is intentional per child sequencing.

## Execution contract reminder

- Stages 1 → 3 in order; one `code()` commit per stage on epic worktree; publish each to **`origin/sub/AST-655/AST-676-rename-prefilter-rubric-and-importance-schema`** via `git push origin HEAD:sub/AST-655/AST-676-rename-prefilter-rubric-and-importance-schema`.
- Do not edit `src/ui/frontend/**`, admin prompt seed/migration scripts, or `docs/features/**` except this plan file during **build-child**.

## Review

| Field | Value |
|-------|-------|
| Branch | `origin/sub/AST-655/AST-676-rename-prefilter-rubric-and-importance-schema` |
| Tip | `e0089dc2` |
| Status | Review Posted (Radia) |

### What's solid

- Plan stages 1–3 land as specified: shared `_CRAFT_RUBRIC_CRITERIA_RESPONSE_SCHEMA`, `craft_company_prefilter` → `craft_prefilter_rubric` in `TASK_CONFIG`, int `min`/`max` + bool rejection in `_validate_response_schema`, spike script key list, Betty manifest tests + bible blocks.
- §1.3 DRY: one criterion schema wired to all six Phase B rubric craft tasks; validator change is minimal and localized.
- Sibling boundaries respected: no `src/ui/frontend/**`, no admin prompt DB work, `company_prefilter` artifact key unchanged; only `ArtifactsCompanyWatchCriteria.tsx` still references old task key (AST-677 scope).

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| advisory | `src/utils/config.py` | `importance` bounds are literal `min: 1`, `max: 10` on the schema field, not bound to `ASTRAL_CONFIG["consult_importance"]`. Plan documents this as intentional; if consult bounds change later, schema must be updated manually. |
| advisory | epic sequencing | Company Watch UI still calls `craft_company_prefilter` until **AST-677**; rubric Generate will fail schema validation until models return `importance` (**AST-678**). Both documented in Self-Assessment Risk — no surprise. |

### Recommended actions

| Item | Owner | Action |
|------|-------|--------|
| — | — | No fix-now items. Proceed to **resolve-child** if discuss items are acknowledged. |
| UI task key | AST-677 | Rename `taskKey` in `ArtifactsCompanyWatchCriteria.tsx` when that sibling lands. |
| Prompt bodies | AST-678 | Ensure craft rubric prompts emit `importance` per criterion so Generate passes post-merge. |
