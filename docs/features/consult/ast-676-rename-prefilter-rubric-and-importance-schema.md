<!-- linear-archive: AST-676 archived 2026-06-23 -->

## Linear archive (AST-676)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-676/rename-prefilter-rubric-task-and-require-importance-in-craft-rubric  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-655 — update criteria prompts to specify the importance and explain what that means  
**Blocked by / blocks / related:** parent: AST-655; blocks: AST-678; blocks: AST-677

### Description

## What this implements

Rename the company prefilter craft task from **craft_company_prefilter** to **craft_prefilter_rubric** across the product codebase (config task registry, backend references, tests, and any non-UI call sites). Extend **TASK_CONFIG** response validation for all six rubric craft tasks so each criterion in the `criteria` list requires an integer **importance** in 1–10, matching rubric artifact normalization bounds.

## Acceptance criteria

1. **craft_company_prefilter** is renamed to **craft_prefilter_rubric** everywhere the craft task key is referenced in backend/config/tests (UI handled in sibling **AST-657**).
2. Task response schema for all six requires `importance` (integer, 1–10) on every `criteria` item; missing or out-of-range values fail the craft task with a clear validation error.

## Boundaries

* Does **not** update React Artifacts pages (sibling **AST-657**).
* Does **not** author or deploy admin prompt text (sibling **AST-658**).
* Does **not** change consult scoring math or rubric UI behavior.

## Notes for planning

* Six tasks: renamed prefilter rubric plus the five existing `craft_*_rubric` consult criteria tasks.
* Stored artifact key `company_prefilter` stays unchanged; only the craft **task key** renames.
* Prompt bodies live in **agent_task** DB — out of scope here.

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/AST-655-update-criteria-prompts-to-specify-the-importance-and-explain-what`, child `sub/AST-655/AST-656-rename-prefilter-rubric-and-importance-schema`. Created at dispatch-parent.

### Comments

#### ada — 2026-06-15T18:27:57.898Z
**[merge-child] fix:** Republished `origin/sub/AST-655/AST-676-rename-prefilter-rubric-and-importance-schema` — removed `Merge remote-tracking branch` commits (216b896b, e65192e4). Sub history now stacked cleanly on `origin/ftr/AST-655-update-criteria-prompts-to-specify-the-importance-and-explain-what` via cherry-pick; `plan(AST-676)` / `resolve(AST-676)` subjects aligned with `validate-sub-log`. Tip after push: see validate-sub-log on main repo.

#### radia — 2026-06-15T18:24:26.596Z
**Diff:** `origin/dev...origin/sub/AST-655/AST-676-rename-prefilter-rubric-and-importance-schema` @ `e4074d1a` (8 files, +253/−40).

**Plan fidelity:** Stages 1–3 match the combined plan — shared `_CRAFT_RUBRIC_CRITERIA_RESPONSE_SCHEMA`, `craft_prefilter_rubric` rename in `TASK_CONFIG`, `_validate_response_schema` int `min`/`max` + bool guard, spike script, Betty manifest tests + bible blocks.

### fix-now
None.

### discuss
None blocking. Sequencing risks (UI still on `craft_company_prefilter` until **AST-677**; Generate fails until prompts return `importance` in **AST-678**) are documented in the plan Self-Assessment and are intentional sibling scope.

### advisory
- **`src/utils/config.py`:** `importance` bounds are literal `1`/`10` on the schema field, not wired to `ASTRAL_CONFIG["consult_importance"]`. Plan documents this decision; acceptable — note if consult bounds ever change, update schema manually.
- **`grep craft_company_prefilter src/`:** only `ArtifactsCompanyWatchCriteria.tsx` remains — correct per AST-677 boundary.

### ASTRAL_CODE_RULES
- §1.3 DRY: single shared schema for six tasks; validator change localized in `agent.py`.
- §1.4 / §2.1: task registry and response shapes in `config.py`; no magic numbers in core beyond field spec.
- §2.3: schema validation path correct; bool-before-int guard handles Python `isinstance(True, int)`.
- Layer / logging / batch / debug: N/A — no touched paths in those areas.

**Doc:** [ast-676-rename-prefilter-rubric-and-importance-schema.md](https://github.com/susansomerset/astral/blob/sub/AST-655/AST-676-rename-prefilter-rubric-and-importance-schema/docs/features/consult/ast-676-rename-prefilter-rubric-and-importance-schema.md) — Review section updated @ `e4074d1a`.

#### betty — 2026-06-15T18:20:43.910Z
## QA test manifest (AST-676)

**Publish ref:** `origin/sub/AST-655/AST-676-rename-prefilter-rubric-and-importance-schema` @ `e0089dc2` (`merge-tests(AST-676): origin/tests a0e02d28`)

1. **`tests/component/utils/test_config.py::TestAst676CraftRubricSchema`** — `craft_prefilter_rubric` present; `craft_company_prefilter` absent; all six rubric craft tasks share `importance` int 1–10 in `items_schema`.
2. **`tests/component/core/test_agent.py::TestResponseSchemaBranches::test_ast676_int_bounds_and_bool_rejection`** — `_validate_response_schema` accepts in-range int, rejects missing/bool/out-of-range.
3. **`tests/component/core/test_agent.py::TestResponseSchemaBranches::test_ast676_craft_rubric_criteria_schema`** — nested `criteria[]` validation passes with `importance`; fails when omitted.

**Narrowed run:**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst676CraftRubricSchema \
  tests/component/core/test_agent.py::TestResponseSchemaBranches::test_ast676_int_bounds_and_bool_rejection \
  tests/component/core/test_agent.py::TestResponseSchemaBranches::test_ast676_craft_rubric_criteria_schema
```

**Bible shasum (publish ref):**
- `docs/test-bible/utils/config.md` → `441298317614c38f0d5cfb30c729a33c125be9ec1200b546734283f52a775d4f`
- `docs/test-bible/core/agent.md` → `1fc26ddb3d66084f6ba44092af903ab23ae08769deaef0018d42f1ed28c4b110`

**Coverage notes:** Product code landed without Stage 3 tests (build test-tree ban); Betty added manifest tests + bible blocks. UI task key rename (**AST-677**) and admin prompts (**AST-678**) remain sibling scope — not in this manifest.

— Betty

#### ada — 2026-06-15T18:17:28.990Z
`origin/sub/AST-655/AST-676-rename-prefilter-rubric-and-importance-schema` @ `faf4d24f` — product code complete. Plan stage 3 component tests (`test_agent.py`, `test_config.py`) deferred to **qa-child** per build test-tree ban.

#### ada — 2026-06-15T18:15:37.574Z
Plan: [ast-676-rename-prefilter-rubric-and-importance-schema.md](https://github.com/susansomerset/astral/blob/sub/AST-655/AST-676-rename-prefilter-rubric-and-importance-schema/docs/features/consult/ast-676-rename-prefilter-rubric-and-importance-schema.md)

Three stages: (1) shared `_CRAFT_RUBRIC_CRITERIA_RESPONSE_SCHEMA` + rename `craft_company_prefilter` → `craft_prefilter_rubric` in `TASK_CONFIG`; (2) extend `_validate_response_schema` with int `min`/`max` and bool rejection; (3) component tests + spike script key list.

**Self-assessment**
- **Scope — Single-Component:** `config.py`, `agent.py`, two test modules, one spike script only.
- **Conf — high:** Reuses existing schema validation patterns; bounds match landed `consult_importance`.
- **Risk — Medium:** Rubric Generate fails until prompts return `importance` (AST-678); Company Watch UI still uses old task key until AST-677.

---

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

## Resolution (`resolve-child`)

**Date:** 2026-06-15

**Against:** Radia `review-child` § **Review** on `origin/sub/AST-655/AST-676-rename-prefilter-rubric-and-importance-schema` @ **`e4074d1a`**.

**Product / plan**

- **`fix-now`:** None — shared `_CRAFT_RUBRIC_CRITERIA_RESPONSE_SCHEMA`, `craft_company_prefilter` → `craft_prefilter_rubric`, int `min`/`max` + bool rejection in `_validate_response_schema`, spike script key list, and Betty manifest tests are as-reviewed; publish tip already includes **`docs(AST-676): Radia review — …`** before this appendix.
- **Discuss — epic sequencing:** Accepted as documented in Self-Assessment Risk — Company Watch UI still calls `craft_company_prefilter` until **AST-677**; rubric Generate fails schema validation until models return `importance` (**AST-678**). No product changes in this resolve pass.
- **Advisory — literal `importance` bounds (1–10):** Accepted per plan Stage 1 decision — bounds stay literal on the schema field rather than dynamic `"bounds": "consult_importance"` indirection; manual sync if `ASTRAL_CONFIG["consult_importance"]` changes later.

**Integration:** §9a dry-runs vs **`origin/dev`** and **`origin/ftr/AST-655-update-criteria-prompts-to-specify-the-importance-and-explain-what`** — both clean before **User Testing**.
