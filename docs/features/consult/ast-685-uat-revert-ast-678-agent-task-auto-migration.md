<!-- linear-archive: AST-685 archived 2026-06-23 -->

## Linear archive (AST-685)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-685/uat-revert-ast-678-agent-task-auto-migration-update-criteria-prompts  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-655 — update criteria prompts to specify the importance and explain what that means  
**Blocked by / blocks / related:** parent: AST-655; blocks: AST-686

### Description

## What failed

AST-678 landed an automatic `agent_task` migration in `database.py` that inserts the importance explainer into all six rubric craft prompts at schema init. Susan UAT: she wanted a **standalone text file** she could copy/paste via **Manage Tasks** — not product code that mutates prompt bodies.

## Expected

Remove AST-678 migration code, related tests, and bible entries from the epic branch. `agent_task` prompt bodies return to pre-678 behavior until Susan manually pastes approved text via the admin UI.

## Repro

1. Open Manage Tasks (or inspect local DB after app start).
2. Observe craft rubric task prompts already contain `AST-678_VECTOR_IMPORTANCE` marker text without manual edit.
3. Susan expected to paste explainer herself — not have migration inject it.

## Parent AC (quoted inline)

> All six rubric craft tasks share the same importance explainer in prompt text and explicitly instruct the model to return `importance` per criterion.

*(Delivery mechanism corrected per UAT: manual paste after approval — not auto-migration.)*

## Boundaries

* Does **not** change TASK_CONFIG / response_schema (**AST-676**).
* Does **not** change UI task key rename (**AST-677**).
* Does **not** add replacement prompt text in this bug — see sibling **UAT: proposed explainer text** bug.

### Comments

#### radia — 2026-06-15T21:20:54.332Z
### Plan fidelity (Stage 1)

**Solid:** `a74e0def` fully removes AST-678 — constants, `_patch_ast678_importance_into_user_prompt`, `_apply_ast678_craft_rubric_importance_migration`, and the call from `_ensure_agent_task_schema`. Migration chain is `_apply_ast469` → `_apply_ast561` → `_agent_task_schema_ensured = True`. `rg '678|ast678|AST678' src/data/database.py` — no matches on publish ref.

Matches plan decisions: no undo migration, no replacement explainer in product code; AST-676/677/686 boundaries respected.

### Betty manifest

**Solid:** `d7df703f` — deleted `test_ast678_craft_rubric_importance_migration.py`; bible § AST-678 → § AST-685; manual-paste notes in `pages.md` / `config.md` per plan.

### ASTRAL_CODE_RULES

Subtractive data-layer deletion only — no new imports, logging, layer violations, or SQL bind changes. Self-Assessment (minor / high conf / low risk) matches diff footprint.

### Cross-ticket (advisory)

Publish ref @ `d37d388e` also includes sibling **AST-687** / **AST-688** commits (`e690760b`, `f9201d8c`) — LLM attribution tests + bible README block. Not AST-685 scope; no conflict with revert. Track under those tickets at merge-parent.

---

**Verdict:** Clean — no **fix-now** / **discuss**.

**Doc:** [`docs/features/consult/ast-685-uat-revert-ast-678-agent-task-auto-migration.md`](https://github.com/susansomerset/astral/blob/sub/AST-655/AST-685-uat-revert-ast-678-agent-task-auto-migration/docs/features/consult/ast-685-uat-revert-ast-678-agent-task-auto-migration.md) — Radia review section @ `d37d388e`.

#### betty — 2026-06-15T21:17:37.253Z
## QA test manifest (AST-685)

**Publish ref:** `origin/sub/AST-655/AST-685-uat-revert-ast-678-agent-task-auto-migration` @ `bb18a3df` (`merge-tests(AST-685): origin/tests d7df703f`)

**Betty commit:** `d7df703f` — deleted `test_ast678_craft_rubric_importance_migration.py`; replaced **§ AST-678** bible block with **§ AST-685**; updated sibling notes in `pages.md` / `config.md`.

**Bible shasum on publish ref:**
- `docs/test-bible/data/database.md` → `063b950180bfd08288da19597ce5ede4a27963ac2f0b1f13d8d94743833a253e`
- `docs/test-bible/frontend/pages.md` → `e7d093c31ffaafae3a696d2f59d052d41db5e9052cc435c7b3acb627cdfdf2de`
- `docs/test-bible/utils/config.md` → `d2188a08579802d1c5bb240795bbd19ae674fe323fe8772ccc28893bc3247ff6`

### Manifest (test-child)

1. **Revert verification (required):** Confirm `src/data/database.py` has zero `678` / `AST678` / `_apply_ast678` references (Ada `code()` @ `a74e0def`).

2. **Database smoke (required):**

```bash
./scripts/testing/run_component_tests.sh tests/component/data/test_database.py
```

3. **AST-676 regression (required):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst676CraftRubricSchema \
  tests/component/core/test_agent.py::TestResponseSchemaBranches::test_ast676_int_bounds_and_bool_rejection \
  tests/component/core/test_agent.py::TestResponseSchemaBranches::test_ast676_craft_rubric_criteria_schema
```

4. **AST-677 regression (required — §6c routed page):**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_ArtifactsCompanyWatchCriteria.test.tsx
```

**Pass criterion:** items 1–4 green. **Not** zero-arg harness / full branch-lock gate.

**Broken / obsolete (resolved this pass):** `tests/component/data/test_ast678_craft_rubric_importance_migration.py` — deleted; **§ AST-678 · AST-655** removed from `docs/test-bible/data/database.md`.

— Betty

#### chuckles — 2026-06-15T19:50:30.715Z
[check-linear] answered: not stuck — Plan Ready > validate-plan (@susan)

#### susan — 2026-06-15T19:48:11.755Z
@chuckles Is this ticket stuck?

#### ada — 2026-06-15T19:32:19.497Z
Plan: [`docs/features/consult/ast-685-uat-revert-ast-678-agent-task-auto-migration.md`](https://github.com/susansomerset/astral/blob/sub/AST-655/AST-685-uat-revert-ast-678-agent-task-auto-migration/docs/features/consult/ast-685-uat-revert-ast-678-agent-task-auto-migration.md)

**Self-assessment**
- **Scope:** `minor` — Single-product-file revert in `database.py`; Betty owns test/bible cleanup in qa-child.
- **Conf:** `high` — Straight removal of isolated `ed37ea95` migration block; no new design.
- **Risk:** `low` — AST-676/677 untouched; forward migration removal only stops new auto-patching.

**Stage 1 (engineer):** Delete AST-678 constants/helpers/migration + call site in `_ensure_agent_task_schema`.

**QA manifest (Betty):** Delete `test_ast678_craft_rubric_importance_migration.py`; remove/update bible § AST-678 references in `database.md`, `pages.md`, `config.md`.

---

# AST-685 — UAT: Revert AST-678 agent_task auto-migration

**Linear:** [AST-685 — UAT: Revert AST-678 agent_task auto-migration](https://linear.app/astralcareermatch/issue/AST-685/uat-revert-ast-678-agent-task-auto-migration-update-criteria-prompts)  
**Parent:** [AST-655](https://linear.app/astralcareermatch/issue/AST-655/update-criteria-prompts-to-specify-the-importance-and-explain-what) (AC reference only)  
**Publish ref:** `origin/sub/AST-655/AST-685-uat-revert-ast-678-agent-task-auto-migration`  
**Project:** Team Astral

## Summary

Susan UAT: **AST-678** added an idempotent forward migration in `database.py` that auto-inserts the shared importance explainer into all six `craft_*_rubric` **`agent_task.user_prompt`** bodies at schema init. Susan wants a **standalone text file** she can copy/paste via **Manage Tasks** — not product code that mutates prompt bodies on startup. This UAT bug **fully removes** the AST-678 migration module (constants, patch helper, `_apply_ast678_craft_rubric_importance_migration`, and its call from `_ensure_agent_task_schema`). Betty removes the AST-678 component test file and bible rows in a follow-on **qa-child** pass. **`TASK_CONFIG` / response_schema (AST-676)**, UI task key rename (**AST-677**), and replacement explainer prose (sibling **UAT: proposed explainer text**) are **out of scope**.

**Reverts:** product commit `ed37ea95` (`code(AST-678): craft rubric importance explainer agent_task migration`).

**Builds on:** [AST-678 plan](ast-678-craft-rubric-importance-explainer-prompts.md) — this plan is a **subtractive delta** only; do not re-open AST-676/677/678 feature scope.

---

## Files Changed (planned)

| File | Change | Layer | Owner |
|------|--------|-------|-------|
| `src/data/database.py` | Delete AST-678 constants, `_patch_ast678_importance_into_user_prompt`, `_apply_ast678_craft_rubric_importance_migration`; remove call from `_ensure_agent_task_schema` | data | Engineer |
| `tests/component/data/test_ast678_craft_rubric_importance_migration.py` | **Delete file** | tests | Betty (qa-child) |
| `docs/test-bible/data/database.md` | Remove **§ AST-678 · AST-655** block and narrowed run | bible | Betty (qa-child) |
| `docs/test-bible/frontend/pages.md` | Update AST-677 sibling note: drop “admin prompt bodies are **AST-678**” | bible | Betty (qa-child) |
| `docs/test-bible/utils/config.md` | Update Phase B note: drop “admin prompts (**AST-678**) are sibling scope” | bible | Betty (qa-child) |

**Out of scope:** `src/utils/config.py` / `TASK_CONFIG` (**AST-676**), `src/ui/frontend/**` task key (**AST-677**), new explainer prose file (sibling UAT bug), consult scoring math, `docs/features/consult/ast-678-craft-rubric-importance-explainer-prompts.md` (historical plan — leave as-is).

---

## Stage 1: Remove AST-678 migration from database.py

**Done when:** `src/data/database.py` has zero references to `678`, `AST678`, `AST-678_VECTOR_IMPORTANCE`, or `_apply_ast678_craft_rubric_importance_migration`; `_ensure_agent_task_schema` ends with `_apply_ast561_analysis_upshot_take_jd_migration(conn)` then `_agent_task_schema_ensured = True`; `python -m compileall -q src/data/database.py` passes.

1. In `src/data/database.py`, delete the entire AST-678 block introduced by `ed37ea95` — from the comment `# AST-678: shared importance explainer…` through the end of `_apply_ast678_craft_rubric_importance_migration` (inclusive). This removes:
   - `_AST678_CRAFT_RUBRIC_TASK_KEYS`
   - `_AST678_IMPORTANCE_MARKER`
   - `_AST678_CRAFT_RUBRIC_IMPORTANCE_EXPLAINER`
   - `_patch_ast678_importance_into_user_prompt`
   - `_apply_ast678_craft_rubric_importance_migration`

2. In `_ensure_agent_task_schema`, remove the line:
   ```python
   _apply_ast678_craft_rubric_importance_migration(conn)
   ```
   so the migration chain is:
   ```python
   _apply_ast469_select_job_page_run_next_migration(conn)
   _apply_ast561_analysis_upshot_take_jd_migration(conn)
   _agent_task_schema_ensured = True
   ```

3. Run compile check:
   ```bash
   python -m compileall -q src/data/database.py
   ```

⚠️ **Decision:** **Full** removal of the AST-678 migration, including the bundled `craft_company_prefilter` → `craft_prefilter_rubric` **`agent_task`** row copy. Susan’s corrected delivery path is **manual** Manage Tasks edits; **AST-676** / **AST-677** already define `craft_prefilter_rubric` in config/UI. Environments that already ran the forward migration **keep** existing rows and patched prompt text in SQLite — this revert stops **new** auto-patching only; Susan strips explainer prose manually where already injected.

⚠️ **Decision:** **No undo migration.** Do not add code to strip `AST-678_VECTOR_IMPORTANCE` blocks from existing `user_prompt` rows — that is admin/UI work, not schema init.

---

## QA manifest (Betty — after Stage 1 `code()` lands on publish ref)

**Done when:** AST-678 test file and bible references are gone; no pytest collection imports deleted symbols.

1. **Delete** `tests/component/data/test_ast678_craft_rubric_importance_migration.py`.

2. In `docs/test-bible/data/database.md`, remove the entire subsection **`### AST-678 · AST-655`** (heading through the narrowed `run_component_tests.sh` block for that file).

3. In `docs/test-bible/frontend/pages.md` (~line 449), replace the trailing clause  
   `admin prompt bodies are **AST-678**`  
   with:  
   `admin prompt bodies: Susan pastes approved explainer via Manage Tasks (AST-685 reverts auto-migration; see sibling UAT explainer-text bug)`.

4. In `docs/test-bible/utils/config.md` (~line 228), replace  
   `UI rename (**AST-677**) and admin prompts (**AST-678**) are sibling scope`  
   with:  
   `UI rename (**AST-677**) is sibling scope; admin prompt bodies are manual paste (AST-685 reverts AST-678 auto-migration)`.

5. Confirm no remaining bible references to `test_ast678` or `_apply_ast678` (`rg '678|ast678' docs/test-bible/` → only the updated manual-paste notes above).

---

## Execution contract

- Execute **Stage 1** in order; one `code(AST-685)` commit on epic worktree; publish to **`origin/sub/AST-655/AST-685-uat-revert-ast-678-agent-task-auto-migration`**.
- Betty runs **qa-child** for the QA manifest — engineer does **not** commit `tests/` or `docs/test-bible/**` (pre-commit hook).
- Blocking ambiguity → `🛑` comment on **AST-685** per plan-child execution contract.

---

## Self-Assessment

**Scope:** `minor` — Single product file deletion (~130 lines) in `database.py`; test/bible cleanup is Betty-owned follow-on.

**Conf:** `high` — Straight revert of a known, isolated commit (`ed37ea95`); no new patterns.

**Risk:** `low` — Removing forward migration cannot break AST-676 schema validation or AST-677 UI; worst case is envs that never ran AST-678 still need Susan to copy prefilter prompts to `craft_prefilter_rubric` manually (same UAT intent).

---

## ASTRAL_CODE_RULES self-review

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Removing dead migration code reduces surface area — no new duplication. |
| §2.1 config | No config changes; explainer prose leaves `database.py` entirely. |
| §2.4 batch | N/A — no batch processing touched. |
| §2.6 state machine | N/A — no entity state transitions. |
| §3.3 imports | No new imports; deletion only. |
| §3.5 naming | N/A. |

No conflicts flagged.

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-655/AST-685-uat-revert-ast-678-agent-task-auto-migration`  
**Product commit:** `a74e0def` — Stage 1: removed AST-678 constants, `_patch_ast678_importance_into_user_prompt`, `_apply_ast678_craft_rubric_importance_migration`, and call from `_ensure_agent_task_schema`.

**Local verification:** `python3 -m compileall -q src/data/database.py` passes; `rg '678|ast678|AST678' src/data/database.py` — no matches.

**Betty follow-on:** QA manifest in this plan (delete `test_ast678_craft_rubric_importance_migration.py`, bible cleanup) — not in this build (test-tree ban).

---

## Radia review (AST-685)

**Ref:** `origin/sub/AST-655/AST-685-uat-revert-ast-678-agent-task-auto-migration` @ `bb18a3df`  
**Baseline:** `origin/dev` @ `1833e6b9`

### What's solid

| Area | Notes |
|------|-------|
| **Stage 1 / plan** | `a74e0def` removes the full AST-678 block (~131 lines) and drops `_apply_ast678_craft_rubric_importance_migration(conn)` from `_ensure_agent_task_schema`; chain ends `_apply_ast469` → `_apply_ast561` → `_agent_task_schema_ensured = True`. Zero `678`/`AST678` symbols remain in `database.py`. |
| **UAT intent** | No undo migration; no replacement explainer in product code — matches plan decisions and ticket boundaries (AST-676/677/686 out of scope). |
| **Betty manifest** | `d7df703f` deletes `test_ast678_craft_rubric_importance_migration.py`; bible § AST-678 replaced with § AST-685 + sibling manual-paste notes in `pages.md` / `config.md`. |
| **ASTRAL_CODE_RULES** | Subtractive data-layer change only — no new imports, logging, layer bends, or SQL bind surface. |

### Issues

None **fix-now**.

### Advisory

- Publish ref also carries sibling **AST-687** / **AST-688** commits (`e690760b`, `f9201d8c`) — LLM attribution tests + bible README manifest block. Not AST-685 deliverables; no conflict with the revert. Track under those tickets / merge-parent rollup.

### Recommended actions

| Severity | Action |
|----------|--------|
| — | Ada: none — proceed **resolve-child** if no open **discuss** threads. |
| advisory | Epic rollup: confirm AST-687/688 sibling commits land with parent **AST-655** merge, not mistaken for AST-685 scope. |

## Resolution (resolve-child, 2026-06-15)

**Radia review @ `d37d388e`:** fix-now none — clean resolve.

| Finding | Resolution |
|---------|------------|
| **Stage 1 / plan fidelity** | No product changes — `a74e0def` already matches plan; migration chain and zero AST-678 symbols verified on publish ref. |
| **Betty manifest** | No product changes — `d7df703f` / `bb18a3df` test+bible cleanup; test-child manifest items 1–4 green. |
| **advisory** — AST-687/688 sibling commits on publish ref | Acknowledged — LLM attribution tests + bible README block are sibling scope; no conflict with AST-685 revert. Track at merge-parent / those tickets. |

**§9a dry-run:** `origin/sub/AST-655/AST-685-uat-revert-ast-678-agent-task-auto-migration` merges cleanly into `origin/dev` and `origin/ftr/AST-655-update-criteria-prompts-to-specify-the-importance-and-explain-what`.
