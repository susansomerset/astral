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
