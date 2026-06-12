# AST-468 — Absorb CONSULT_CONFIG: dispatcher, database, admin resolution and removal

**Linear:** [AST-468](https://linear.app/astralcareermatch/issue/AST-468/absorb-consult-config-dispatcher-database-admin-resolution-and-removal)  
**Parent:** [AST-376](https://linear.app/astralcareermatch/issue/AST-376/absorb-consult-config-into-gazer-config-task-config-and-dispatch-task-metadata)  
**Feature ref:** `sub/AST-376/AST-468-absorb-consult-config-dispatcher-database-admin-resolution-and-removal` (origin only)

## Summary

**AST-466** makes **`TASK_CONFIG`** + **`GAZER_CONFIG`** authoritative and **`CONSULT_CONFIG`** a shim. This ticket (**AST-468**) stops using **`CONSULT_CONFIG`** for dispatch/admin/data-layer scoring metadata: introduce small **pure** resolvers in **`config.py`** used by **`dispatcher.py`**, **`database.py`**, and **`api_admin.py`**, consolidate the duplicated **`CONSULT_CONFIG` → `agent_task` → `TASK_CONFIG.scored`** logic into one helper, refresh **`scripts/spikes/ast438_admin_prompt_rubric_diagnostic.py`**, and **remove **`CONSULT_CONFIG`** entirely** once no runtime module under **`src/`** imports or subscripts it (**depends on AST-467** for **`consult.py`** / **`gazer.py`**). Document **`pass_threshold`** vs **`dispatch_task.score_floor`** where runtime behavior is explained (mandate + inline docstrings if needed). **`fallback_batch_size` vs `dispatch_task.batch_size`:** DB row wins at runtime per existing pattern — no change to that precedence; only remove **`CONSULT_CONFIG**` as the source of **`agent_task`** indirection in the three duplicated sites.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add **`resolve_dispatch_task_config_key(task_key: str) -> str`**: return **`CONSULT_CONFIG[task_key]["agent_task"]`** when present during transition, else **`task_key`**; after **`CONSULT_CONFIG`** deletion, replace with a literal map **`{"consult_do": "grade_do", "consult_get": "grade_get", "consult_like": "grade_like"}`** only (or equivalent) + identity default. Add **`dispatch_task_key_is_scored(task_key: str) -> bool`** using **`TASK_CONFIG[resolve_dispatch_task_config_key(task_key)].get("scored")`**. Add **`trigger_state_used_by_scored_dispatch_task(trigger_state: str) -> bool`** implementing the same membership rules as today’s **`_trigger_state_scored`** but reading pass/fail/error fields from **`TASK_CONFIG`** entries for **`resolve_dispatch_task_config_key`** of each **`task_key`** in **`database.dispatch_task_seed_templates()`** / **`_DISPATCH_TASK_SEED`** keys (mirror current behavior: skip `*_RETRY` trigger_states; collect **`pass_state`**, **`fail_state`**, **`error_state`**, and list **`error_states`**). Remove **`CONSULT_CONFIG`** shim and **`_build_consult_config_shim`** only in the final stage when **`src/`** is clean. | utils |
| `src/core/dispatcher.py` | Remove **`CONSULT_CONFIG`** import; replace **`_task_key_scored`** / **`_trigger_state_scored`** bodies with calls to **`config`** helpers above (or inline single import of those two functions). | core |
| `src/data/database.py` | Remove **`CONSULT_CONFIG`** import from scoring helpers; use same **`config`** helpers for **`_task_key_scored`** / **`_trigger_state_scored`** (delete local duplicates). | data |
| `src/ui/api/api_admin.py` | Remove **`CONSULT_CONFIG`** import; replace **`_task_is_scored`** / **`_trigger_state_is_scored`** with **`config`** helpers (names may wrap the same functions for clarity). | ui |
| `scripts/spikes/ast438_admin_prompt_rubric_diagnostic.py` | Drop **`CONSULT_CONFIG`** import; build **`_ARTIFACT_CONSUMERS`** by iterating **`TASK_CONFIG`** entries that have **`rubric_artifact`**, using the **`TASK_CONFIG`** key as the consumer label (and include **`qualify_job_listings`**, **`evaluate_jd`**, **`grade_*`** — same informational table intent as today). | scripts |
| `docs/ASTRAL_CODE_RULES.md` | Remove **shim** language for **`CONSULT_CONFIG`** after deletion; align §2.1 and §2.7 with **`TASK_CONFIG`**/**`GAZER_CONFIG`**-only narrative; ensure **`pass_threshold`** vs **`score_floor`** wording matches AST-466/468 reality. | docs |
| Tests under `tests/` | Update imports/assertions that patch or read **`CONSULT_CONFIG`** (e.g. **`tests/component/utils/test_config.py`**, **`tests/component/core/test_consult.py`**) to use **`TASK_CONFIG`** keys or **`monkeypatch`** the new resolver map — **exact file list finalized during build** by grepping **`CONSULT_CONFIG`** in **`tests/`**; do not skip failing tests. | tests |

**Out of scope (per boundaries):** no edits to **`src/core/consult.py`** or **`src/core/gazer.py`** in this ticket — those are **AST-467** (Hedy). Final **`CONSULT_CONFIG`** removal from **`config.py`** is **gated**: see Stage 6.

---

## Stage 1: Config helpers (no `CONSULT_CONFIG` consumers yet)

**Done when:** New functions exist in **`config.py`**, unit-testable from existing patterns, and duplicate the current boolean/scored behavior of **`dispatcher._task_key_scored`**, **`dispatcher._trigger_state_scored`**, **`database._task_key_scored`**, **`database._trigger_state_scored`**, **`api_admin._task_is_scored`**, **`api_admin._trigger_state_is_scored`** for all **`task_key`** / **`trigger_state`** pairs used in production.

1. Add **`resolve_dispatch_task_config_key(task_key: str) -> str`**:
   - **While `CONSULT_CONFIG` still exists (early in this ticket or on a branch that still has the shim):**  
     `entry = CONSULT_CONFIG.get(task_key) or {}`; return **`entry.get("agent_task") or task_key`**.
   - Document in a one-line comment that after **`CONSULT_CONFIG`** removal this becomes a **small fixed map** for **`consult_do`/`consult_get`/`consult_like`** only.

2. Add **`dispatch_task_key_is_scored(task_key: str) -> bool`**:  
   **`bool((TASK_CONFIG.get(resolve_dispatch_task_config_key(task_key)) or {}).get("scored"))`**.

3. Add **`trigger_state_used_by_scored_dispatch_task(trigger_state: Optional[str]) -> bool`**:
   - If falsy trigger_state → **`False`**.
   - If **`trigger_state.endswith("_RETRY")`** → **`False`** (preserve current rule).
   - Else iterate **`tk`** over the keys of **`_DISPATCH_TASK_SEED`** (the same dict that backs **`dispatch_task_seed_templates()`** in **`database.py`** — import is not allowed **utils → data**; **duplicate the key list as a frozenset literal in `config.py`** mirroring current seed keys, or expose keys from a **`DISPATCH_TASK_SEED_KEYS`** frozenset defined next to **`_DISPATCH_TASK_SEED`** in **`database.py`** and import **data → utils** is forbidden — so **keep the frozenset of task_key strings in `config.py`** copy-pasted from **`database._DISPATCH_TASK_SEED`** at time of build, with a comment “keep in sync with `_DISPATCH_TASK_SEED`”).

   ⚠️ **Decision:** Maintain **`DISPATCH_TASK_SEED_KEYS`** as a **`frozenset`** in **`config.py`** listing exactly the keys in **`database._DISPATCH_TASK_SEED`** today; builder updates both if seed changes (same commit). This avoids layering violations.

   For each **`tk`**, if **`not dispatch_task_key_is_scored(tk)`**: continue. Let **`rk = resolve_dispatch_task_config_key(tk)`**, **`cfg = TASK_CONFIG.get(rk) or {}`**. Collect states list = **`[cfg.get("pass_state"), cfg.get("fail_state"), cfg.get("error_state"), *(cfg.get("error_states") or [])]`**; filter **`None`**. If **`trigger_state`** is in that list → return **`True`**. Else after loop → **`False`**.

4. Run **`rg CONSULT_CONFIG src/utils/config.py`** — helpers may still reference **`CONSULT_CONFIG`** until Stage 6.

---

## Stage 2: `dispatcher.py` — use helpers

**Done when:** **`dispatcher.py`** does not import **`CONSULT_CONFIG`**; **`_task_key_scored`** and **`_trigger_state_scored`** delegate to **`config.dispatch_task_key_is_scored`** and **`config.trigger_state_used_by_scored_dispatch_task`** (or the file imports those two names and deletes the underscore-prefixed duplicates).

1. Edit imports: **`from src.utils.config import ASTRAL_CONFIG, TASK_CONFIG, dispatch_task_key_is_scored, trigger_state_used_by_scored_dispatch_task`** (exact names as implemented).

2. Replace function bodies accordingly; preserve call sites (`_run_unified` score floor path).

---

## Stage 3: `database.py` — use helpers

**Done when:** **`database.py`** does not import **`CONSULT_CONFIG`**; local **`_task_key_scored`** / **`_trigger_state_scored`** removed or thin wrappers to **`config`**.

1. Remove **`CONSULT_CONFIG`** from the module import list at top (where present).

2. Import the two helpers from **`src.utils.config`**.

3. Replace **`get_new_job_batch` / `count_eligible` / `save_dispatch_task`** paths that referenced local copies — ensure **`is_scored`** resolution matches pre-change behavior.

---

## Stage 4: `api_admin.py` — use helpers

**Done when:** **`api_admin.py`** does not import **`CONSULT_CONFIG`**; **`list_dtasks`**, **`dispatch_task_keys`**, and dispatch task **`POST`/`PUT`** use **`dispatch_task_key_is_scored`** and **`trigger_state_used_by_scored_dispatch_task`** instead of **`_task_is_scored`** / **`_trigger_state_is_scored`**.

---

## Stage 5: Spike `ast438` + precedence documentation

**Done when:** Script runs without **`CONSULT_CONFIG`**; admin/dispatch behavioral docs are consistent.

1. **`scripts/spikes/ast438_admin_prompt_rubric_diagnostic.py`**: Replace the loop that fills **`_ARTIFACT_CONSUMERS`** from **`CONSULT_CONFIG`** with a loop over **`TASK_CONFIG`**: for each **`task_key`** where **`TASK_CONFIG[task_key].get("rubric_artifact"`** exists, append **`task_key`** to **`_ARTIFACT_CONSUMERS[rubric_artifact]`**. Remove **`CONSULT_CONFIG`** from imports.

2. In **`docs/ASTRAL_CODE_RULES.md`**, ensure the **`pass_threshold` vs `score_floor`** explanation states:
   - Dispatch code path uses **`score_floor`** from the **`dispatch_task`** row only (with existing **`NULL` → 1.0** behavior for scored tasks in **`database`/`dispatcher`**).
   - Grading uses **`pass_threshold`** from **`TASK_CONFIG`** for scored consult **`render_verdict`** — **do not substitute one for the other** in code.

3. Add a one-line docstring near **`dispatch_task_key_is_scored`** in **`config.py`** cross-referencing the above if not already redundant.

---

## Stage 6: Remove `CONSULT_CONFIG` (hard gate)

**Done when:** **`CONSULT_CONFIG` name does not exist in `src/utils/config.py`** and **`rg CONSULT_CONFIG src/`** returns **no matches**.

**Gate (mandatory):** Before executing this stage, run **`rg CONSULT_CONFIG src/`**. If **`consult.py`** or **`gazer.py`** (or any other **`src/`** file except tests) still references **`CONSULT_CONFIG`**, **stop implementation**, post a Linear comment on **AST-468** with **`🛑`** template naming the blocking file and **AST-467**, and **do not** delete **`CONSULT_CONFIG`**. Susan/Chuckles merges **AST-467** first or coordinates a combined branch.

When the gate passes:

1. Replace **`resolve_dispatch_task_config_key`** implementation with the fixed map (**`consult_*` → `grade_*`**) + identity default; remove any **`CONSULT_CONFIG`** reference.

2. Delete **`CONSULT_CONFIG`**, **`_build_consult_config_shim`**, and shim-related comments.

3. Update **`tests/`** and **`docs/ASTRAL_CODE_RULES.md`** per the table above.

4. **`python3 -m py_compile`** on touched modules and run **dispatch + consult** tests per **test-astral** / manifest when this ticket reaches **Tests Ready**.

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — Cross-cuts **`config`**, **`dispatcher`**, **`database`**, **`api_admin`**, spike script, tests, and mandate doc; removal gate ties to sibling **AST-467**.

**Conf:** `Medium` — Helpers must match duplicated logic exactly; **`DISPATCH_TASK_SEED_KEYS`** sync is a mild footgun (mitigated by comment + grep in plan).

**Risk:** `HIGH` — Wrong **`is_scored`** or trigger-state membership breaks job batch claiming, admin “Available” counts, or score floor application.

---

## Plan vs ASTRAL_CODE_RULES (self-review)

| Section | Alignment |
|---------|-----------|
| §1.3 DRY | One resolver in **`utils`**, duplicated consult/dispatch/indirection eliminated in three modules. |
| §2.1 Config | **`CONSULT_CONFIG`** removed only when **`src/`** clean; **`TASK_CONFIG`** remains SOT for tasks. |
| §2.4 / dispatch | **`batch_size`** precedence unchanged (DB overrides config fallback — still true for fallback_batch_size elsewhere). |
| §3.3 Imports | **`data` → `utils`** only; **`ui` → `utils`**; **`core` → `utils`**; no upward imports. |
| §3.5 Naming | Resolver names are verb phrases, consistent with helpers in **`config.py`**. |

No conflicts requiring **`conf-!!-NONE`**.

---

## Execution contract (developer agent)

Execute stages **1 → 6** in order on **`dev-ada`**; one commit per stage during **build-astral**, cherry-pick commits whose subject includes **`AST-468`** to **`origin/sub/AST-376/AST-468-absorb-consult-config-dispatcher-database-admin-resolution-and-removal`**. If Stage 6 is blocked by **AST-467**, complete **Stages 1–5** only, leave **`CONSULT_CONFIG`** in place, and comment on **AST-468** — do not improvise **`consult.py`**/**`gazer.py`** fixes.

---

## Review (build)

- **Publish ref:** `sub/AST-376/AST-468-absorb-consult-config-dispatcher-database-admin-resolution-and-removal`
- **Commits:** `ae2a51be` — implementation (stages 1–5); plan doc updated in the same dev-ada train (see branch log for docs commit)

## Review

Radia (`review-astral`) · **`git diff origin/dev...origin/sub/AST-376/AST-468-absorb-consult-config-dispatcher-database-admin-resolution-and-removal`** · Tip before this doc-only commit `2b3d8e7f`

### What's solid

- **`dispatch_task_key_is_scored`** / **`trigger_state_used_by_scored_dispatch_task`** live in **`config.py`** per plan; **`dispatcher.py`**, **`database.py`**, **`api_admin.py`** drop **`CONSULT_CONFIG`** plumbing for scoring metadata without introducing upward imports (**§5a B2**).
- **Stage 6 gate honored:** **`CONSULT_CONFIG`** shim persists while **`consult.py`** / **`gazer.py`** still import it (**AST‑467**), matching the written refusal to delete prematurely.
- Trigger-state aggregation now walks **`DISPATCH_TASK_SEED_KEYS`** instead of iterating the shim-only keys — for current scored dispatch rows (`consult_*` → graded tasks plus **`qualify_job_listings`**, **`evaluate_jd`**) the boolean matches legacy behavior (prior helpers never meaningfully consulted the unused **`task_key`** argument anyway).
- **`scripts/spikes/ast438_admin_prompt_rubric_diagnostic.py`** now keys consumers off **`TASK_CONFIG["rubric_artifact"]`** as intended.

### Issues

| Severity | Topic | Detail |
|---------|-------|--------|
| **advisory** | Seed sync | **`DISPATCH_TASK_SEED_KEYS`** duplicates **`database._DISPATCH_TASK_SEED`** — drift would skew **`trigger_state_used_by_scored_dispatch_task`**; keep the mandated “same-commit” invariant when touching seed templates. |

### Recommended actions

- After **AST‑467** lands, rerun Stage 6 to delete **`CONSULT_CONFIG`** and swap **`resolve_dispatch_task_config_key`** to the fixed **`consult_*` → `grade_*`** map-only implementation (ticket already outlines this).

### Severity counts

**fix-now:** 0 · **discuss:** 0 · **advisory:** 1

_(Radia Linear comment carries the **`docs(AST-468):`** commit SHA.)_
