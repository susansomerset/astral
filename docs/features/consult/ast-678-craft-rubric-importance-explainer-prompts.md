# AST-678 — Craft rubric importance explainer and admin prompt updates

**Linear:** [AST-678](https://linear.app/astralcareermatch/issue/AST-678/craft-rubric-importance-explainer-and-admin-prompt-updates-update)  
**Parent:** [AST-655](https://linear.app/astralcareermatch/issue/AST-655/update-criteria-prompts-to-specify-the-importance-and-explain-what)  
**Publish ref:** `origin/sub/AST-655/AST-678-craft-rubric-importance-explainer-prompts`  
**Project:** Team Astral

## Summary

Author one **shared importance explainer** (identical prose across all six rubric craft tasks) describing 1–10 weights, the configured multiplier table, and how importance combines with runtime letter grades and confidence at consult scoring time. Insert that explainer into admin-managed **`agent_task.user_prompt`** bodies for all six **`craft_*_rubric`** tasks (including **`craft_prefilter_rubric`** after rename), and instruct the model to return integer **`importance`** on every criterion. Migrate **`craft_company_prefilter`** → **`craft_prefilter_rubric`** in the **`agent_task`** store so Company Watch **Generate** resolves prompts after **AST-676** / **AST-677** land. Schema validation (**AST-676**) and UI task key (**AST-677**) are sibling scope — this ticket is prompt bodies + DB migration + deploy path only.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Shared explainer constant, patch helper, idempotent AST-678 migration (prefilter task-key rename + six-task prompt patch); wire into `_ensure_agent_task_schema` | data |
| `tests/component/data/test_ast678_craft_rubric_importance_migration.py` | Migration idempotency, prefilter rename, explainer marker present on all six keys | tests |

**Out of scope (sibling tickets):** `src/utils/config.py` `TASK_CONFIG` / `response_schema` (**AST-676**), `src/core/agent.py` validator (**AST-676**), `src/ui/frontend/**` task key rename (**AST-677**), consult scoring math, rubric UI layout, bulk re-generation of existing candidate rubrics.

## Stage 1: Shared explainer + agent_task migration

**Done when:** `_ensure_agent_task_schema` runs an idempotent AST-678 migration that (a) retires `craft_company_prefilter` and ensures a current `craft_prefilter_rubric` row carries the former prompts (patched), and (b) inserts the shared explainer into `user_prompt` for all six rubric craft task keys; re-running migration is a no-op.

1. In `src/data/database.py`, near the other AST prompt migrations (before `_apply_ast561_analysis_upshot_take_jd_migration`), add module-level constants:

   ```python
   _AST678_CRAFT_RUBRIC_TASK_KEYS: Tuple[str, ...] = (
       "craft_prefilter_rubric",
       "craft_joblist_rubric",
       "craft_jobdesc_rubric",
       "craft_get_rubric",
       "craft_do_rubric",
       "craft_like_rubric",
   )
   _AST678_IMPORTANCE_MARKER = "AST-678_VECTOR_IMPORTANCE"
   _AST678_CRAFT_RUBRIC_IMPORTANCE_EXPLAINER = """..."""
   ```

   Set `_AST678_CRAFT_RUBRIC_IMPORTANCE_EXPLAINER` to **exactly** this prose (shared across all six tasks — do not vary by stage):

   ```text
   ## Vector importance (1–10)

   Each criterion you return is a scoring **vector**. Assign every vector an integer **`importance`** from **1** (lowest priority) to **10** (highest priority). You **must** return `importance` on **every** criterion in your JSON — do not omit it or leave priority implicit.

   Spread importance meaningfully when vectors differ in how much they should move the consult score. Avoid assigning **5** to every vector when priorities clearly differ.

   ### Weight multipliers (importance → score contribution)

   Importance scales each vector's contribution to the overall consult score:

   - 1 → 30% of baseline
   - 2 → 49%
   - 3 → 68%
   - 4 → 87%
   - 5 → 106% (baseline)
   - 6 → 125%
   - 7 → 144%
   - 8 → 163%
   - 9 → 182%
   - 10 → 200%

   These match the runtime table in `ASTRAL_CONFIG["consult_importance"]` (AST-358 / AST-429).

   ### How importance combines with grades and confidence at scoring time

   At runtime each vector receives a letter grade (**A–D**, plus **F** and **X**) and a **confidence** integer **1–5**. Consult scoring combines all three:

   - **Counted vectors** contribute: `(equal base share among counted vectors) × (grade density) × (importance multiplier) × (confidence multiplier)`.
   - **Grade density** uses universal letter values (A highest, D lowest) times the confidence multiplier (1 → 0%, 2 → 25%, 3 → 50%, 4 → 75%, 5 → 100% of grade value).
   - **F** with confidence **2–5** is a **dealbreaker** — the rubric fails immediately regardless of other vectors.
   - **X** (cannot evaluate) and **confidence 1** vectors are **excluded** from the scored numerator (they do not add points; remaining vectors share the base).
   - The summed contribution is normalized to a **0–10** consult score and compared to the stage pass threshold.

   Return `importance` as an integer field **1–10** alongside `label` and `content` on each criterion object.

   <!-- AST-678_VECTOR_IMPORTANCE -->
   ```

   Keep the HTML comment marker as the last line of the explainer block (idempotency guard).

2. Add `_patch_ast678_importance_into_user_prompt(user_prompt: str) -> str`:

   - If `_AST678_IMPORTANCE_MARKER` is already in `user_prompt`, return `user_prompt` unchanged.
   - If `user_prompt` contains the literal substring `{$RESPONSE_SCHEMA}`, insert `_AST678_CRAFT_RUBRIC_IMPORTANCE_EXPLAINER` **immediately before** that token (preserve a single blank line between explainer and the existing JSON/schema paragraph).
   - Else if `user_prompt.strip()` is empty, return `_AST678_CRAFT_RUBRIC_IMPORTANCE_EXPLAINER` only.
   - Else append `\n\n` + explainer at end of `user_prompt` (fallback for prompts that lack `{$RESPONSE_SCHEMA}` — should not happen on current six tasks, but keeps migration safe).

3. Add `_apply_ast678_craft_rubric_importance_migration(conn: sqlite3.Connection) -> None`:

   **3a — Prefilter task-key rename in `agent_task` (DB only; artifact key `company_prefilter` unchanged):**

   - Try to load current row for `craft_company_prefilter` and `craft_prefilter_rubric`.
   - If a current `craft_company_prefilter` row exists:
     - If no current `craft_prefilter_rubric` row **or** the `craft_prefilter_rubric` row has empty `user_prompt` and empty `cache_prompt` (blank row inserted by `sync_agent_tasks` after **AST-676**):
       - Copy `agent_id`, all prompt segments, `run_next`, `system_prompt` from the `craft_company_prefilter` row as the source.
       - Patch `user_prompt` via `_patch_ast678_importance_into_user_prompt`.
       - Call `_save_agent_task_on_connection(conn, "craft_prefilter_rubric", now=_utc_now(), ...)` with the copied + patched fields.
     - `UPDATE agent_task SET current = 0 WHERE task_key = 'craft_company_prefilter' AND current = 1` (retire old key; do not delete history).

   **3b — Patch all six rubric craft tasks:**

   - For each `task_key` in `_AST678_CRAFT_RUBRIC_TASK_KEYS`:
     - Load current row; skip if missing.
     - Compute `new_up = _patch_ast678_importance_into_user_prompt(row["user_prompt"] or "")`.
     - If `new_up == row["user_prompt"]`, continue (already patched).
     - Call `_save_agent_task_on_connection(conn, task_key, now=_utc_now(), agent_id=row["agent_id"], user_prompt=new_up, cache_prompt=row["cache_prompt"], cache_prompt_b=row["cache_prompt_b"], cache_prompt_c=row["cache_prompt_c"], cache_prompt_d=row["cache_prompt_d"], nocache_prompt=row["nocache_prompt"], system_prompt=row["system_prompt"], run_next=row["run_next"])`.
   - `conn.commit()` once at end of migration function.

4. In `_ensure_agent_task_schema`, after `_apply_ast561_analysis_upshot_take_jd_migration(conn)`, call `_apply_ast678_craft_rubric_importance_migration(conn)`.

⚠️ **Decision:** Explainer lives in `database.py` beside other prompt migrations (AST-561 pattern), not in `config.py` — it is admin prompt prose, not a behavior-driving config block (§2.1). Multiplier literals in the explainer are copied from `ASTRAL_CONFIG["consult_importance"]["multipliers"]` at authoring time; if Susan later changes the table in config, prompt prose must be updated manually (same tradeoff as **AST-676** literal schema bounds).

⚠️ **Decision:** Patch **`user_prompt` only** — all six current craft rubric tasks carry `{$RESPONSE_SCHEMA}` and JSON instructions in `user_prompt`; `nocache_prompt` holds runtime candidate context on some tasks and must not receive the explainer.

## Stage 2: Component tests for migration

**Done when:** `pytest tests/component/data/test_ast678_craft_rubric_importance_migration.py -q` passes; migration is idempotent and covers prefilter rename.

1. Create `tests/component/data/test_ast678_craft_rubric_importance_migration.py`.

2. Use a temporary SQLite file per test (stdlib `sqlite3` + `tempfile`). Import `database` module functions; call `database._ensure_agent_task_schema(conn)` (or the migration directly if tests need isolation — prefer public schema ensure path).

3. Test cases (minimum):

   - **`test_patch_inserts_before_response_schema`:** Seed one `agent_task` row for `craft_joblist_rubric` with `user_prompt` containing `{$RESPONSE_SCHEMA}` and no marker; run migration; assert `_AST678_IMPORTANCE_MARKER` in `user_prompt` and marker appears **before** `{$RESPONSE_SCHEMA}`.
   - **`test_migration_idempotent`:** Run `_ensure_agent_task_schema` twice on same conn; assert `user_prompt` byte-identical after second run (no duplicate explainer blocks).
   - **`test_prefilter_task_key_rename`:** Seed current `craft_company_prefilter` with non-empty `user_prompt` and `agent_id='test_agent'`; no `craft_prefilter_rubric` row; run migration; assert current `craft_prefilter_rubric` exists with same `agent_id`, marker present, and `craft_company_prefilter` has `current=0`.
   - **`test_all_six_keys_receive_marker`:** Seed minimal current rows for all six keys in `_AST678_CRAFT_RUBRIC_TASK_KEYS` (use `craft_company_prefilter` only in rename test — here seed `craft_prefilter_rubric` directly); run migration; assert each current row's `user_prompt` contains `_AST678_IMPORTANCE_MARKER`.

4. Do **not** edit `tests/` beyond this new file in this ticket (Betty owns bible alignment on **merge-tests**).

## Stage 3: Local verification + production deploy path

**Done when:** Linear comment on **AST-678** documents local smoke + Susan's production push steps; builder confirms Generate returns `importance` on at least one rubric page when **AST-677** is on the same ftr line.

1. **Local DB apply:** Restart app or open any DB path that calls `_ensure_agent_task_schema` (e.g. start server once, or run a one-liner that opens `database._get_connection()` and ensures schema). Verify with sqlite3:

   ```bash
   sqlite3 data/astral.db "SELECT task_key, instr(user_prompt,'AST-678_VECTOR_IMPORTANCE')>0 AS has_marker FROM agent_task WHERE task_key LIKE 'craft_%rubric' AND current=1 ORDER BY task_key;"
   ```

   Expect six rows, all `has_marker=1`; no current `craft_company_prefilter` row.

2. **Generate smoke (manual, post-AST-677 on ftr):** On any rubric Artifacts page (e.g. Job List Criteria), click **Generate**; confirm returned criteria tabs show non-default `importance` values in the editor **before** save. If model returns valid JSON with `importance`, schema validation (**AST-676**) passes.

3. **Production deploy (Susan — out of band, document in Linear comment):**

   - After local verification and merge to staging, Susan pushes **`agent_task`** rows only:

     ```bash
     python3 scripts/push_tables_to_prod.py agent_task
     ```

   - Requires `ASTRAL_PROD_URL`, `ASTRAL_ADMIN_BEARER`, and IP allow-list (same as **AST-438** / `scripts/push_tables_to_prod.py` header).
   - Optional read-only diff before push: `python3 scripts/spikes/ast438_admin_prompt_rubric_diagnostic.py --prompt-only`.

4. Post Linear comment on **AST-678** with: local marker query result, whether Generate smoke was run (and which page), and reminder that Susan runs `push_tables_to_prod.py agent_task` for production.

⚠️ **Decision:** No automated prod write in this ticket — Susan's established **`push_tables_to_prod.py`** path is the deploy contract (**AST-438** explicitly excluded auto-sync).

## Self-Assessment

**Scope — `scope-Single-Component`**  
Touches `database.py` prompt migration helpers and one new component test module — no config schema, core validator, UI, or consult scoring changes.

**Conf — `conf-high`**  
Follows AST-561 idempotent `agent_task` migration pattern; explainer content mirrors landed `consult_importance` multipliers and `_render_score` behavior in `consult.py`; all six tasks already use `{$RESPONSE_SCHEMA}` in `user_prompt` (verified on local `data/astral.db`).

**Risk — `risk-Medium`**  
Incorrect explainer placement or duplicate patches could confuse model outputs on all six rubric **Generate** paths; until this lands, **AST-676** schema requires `importance` so generates fail without prompt update — expected epic sequencing with **AST-677** UI key rename.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|-------|
| §1.3 DRY | One `_AST678_CRAFT_RUBRIC_IMPORTANCE_EXPLAINER` constant; one patch helper; one migration for six keys + prefilter rename. |
| §2.1 Config | Multiplier **behavior** stays in `ASTRAL_CONFIG`; prompt prose is admin-managed `agent_task` content (TASK_CONFIG prompts removed per registry comment). |
| §2.4 Batch | N/A — craft rubric tasks are on-demand Generate, not batch dispatch. |
| §2.6 State machine | N/A — no job/company transitions. |
| §3.3 Imports | Migration stays in data layer; calls existing `_save_agent_task_on_connection`. |
| §3.5 Naming | Uses canonical `craft_prefilter_rubric` task key aligned with **AST-676**. |

**Conflicts:** None blocking. Epic requires **AST-677** + this ticket before Company Watch **Generate** end-to-end succeeds.

## Execution contract reminder

- Stages 1 → 3 in order; one `code()` commit per stage on epic worktree; publish each to **`origin/sub/AST-655/AST-678-craft-rubric-importance-explainer-prompts`** via `git push origin HEAD:sub/AST-655/AST-678-craft-rubric-importance-explainer-prompts`.
- Do not edit `src/utils/config.py`, `src/core/agent.py`, `src/ui/frontend/**`, or consult scoring paths during **build-child**.

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-655/AST-678-craft-rubric-importance-explainer-prompts` @ `1325d02b`

### What's solid

- AST-678 footprint matches plan Stages 1–2: explainer constant, patch helper, migration wired into `_ensure_agent_task_schema`.
- Explainer prose matches plan; idempotent marker; inserts before `{$RESPONSE_SCHEMA}`; `user_prompt` only.
- Prefilter `agent_task` rename copies `craft_company_prefilter` → `craft_prefilter_rubric` when new row blank; retires old key.
- Component tests cover patch placement, idempotency, prefilter rename, all six keys.

### Issues

| Severity | Finding |
|----------|---------|
| **discuss** | Epic stacking on sub vs ftr — expected; AST-678-only product scope is `database.py` migration. |
| **discuss** | `except sqlite3.Error: pass` on prefilter retire `UPDATE` — acceptable for merge; tighten later if needed. |
| **advisory** | Literal multiplier prose vs `ASTRAL_CONFIG` — documented plan tradeoff. |
| **advisory** | Generate smoke deferred until AST-677 on ftr. |

**fix-now:** none.

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-655/AST-678-craft-rubric-importance-explainer-prompts`  
**Product commit:** `e0cf5bb3` — Stage 1: `_AST678_CRAFT_RUBRIC_IMPORTANCE_EXPLAINER`, `_patch_ast678_importance_into_user_prompt`, `_apply_ast678_craft_rubric_importance_migration` wired into `_ensure_agent_task_schema`.

**Local verification (temp copy of `data/astral.db`):** all six `craft_*_rubric` current rows have `AST-678_VECTOR_IMPORTANCE` marker; no current `craft_company_prefilter` row.

**Generate smoke:** not run — requires **AST-677** UI task key on same ftr line.

**Production deploy (Susan):** after staging merge, `python3 scripts/push_tables_to_prod.py agent_task` (optional pre-check: `python3 scripts/spikes/ast438_admin_prompt_rubric_diagnostic.py --prompt-only`).

## Resolution (resolve-child, 2026-06-15)

**Radia review @ `1325d02b`:** fix-now none — clean resolve.

| Finding | Resolution |
|---------|------------|
| **discuss** — 15-file three-dot diff vs stacked AST-676/677/674 on ftr | Expected epic stacking; AST-678-only product scope is `database.py` migration (+ Betty tests, plan doc). No sibling re-touch. |
| **discuss** — `except sqlite3.Error: pass` on `craft_company_prefilter` retire `UPDATE` | Acknowledged. Matches low-risk migration pattern; AST-561 uses early return on read failure. Tighten only if retire failures surface in prod. |
| **advisory** — literal multiplier prose vs `ASTRAL_CONFIG` | Accepted plan tradeoff (documented in plan Stage 1). |
| **advisory** — Generate smoke (AC 3) | Deferred to UAT — confirm on one rubric Artifacts page once **AST-677** is on ftr. |
| **advisory** — production `push_tables_to_prod.py agent_task` | Susan path documented in build stub; out of band. |

**§9a dry-run:** `origin/sub/AST-655/AST-678-craft-rubric-importance-explainer-prompts` merges cleanly into `origin/dev` and `origin/ftr/AST-655-update-criteria-prompts-to-specify-the-importance-and-explain-what`.

