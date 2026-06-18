# AST-747 — Config schedulable keys retire consult aliases

- **Linear (this ticket):** [AST-747](https://linear.app/astralcareermatch/issue/AST-747/config-schedulable-keys-retire-consult-aliases-task-keys-vs-dispatch)
- **Parent:** [AST-736](https://linear.app/astralcareermatch/issue/AST-736/task-keys-vs-dispatch-task-keys)
- **Publish ref:** `origin/sub/AST-736/AST-747-config-schedulable-keys-retire-consult-aliases`

## Summary

Retire `consult_do`, `consult_get`, and `consult_like` from the schedulable dispatch vocabulary in `src/utils/config.py` and admin validation paths. Promote `grade_do`, `grade_get`, and `grade_like` as the sole schedulable keys for those pipeline hops — the same strings already used in `TASK_CONFIG` and Manage Tasks. Remove the consult→grade alias map so config derivation, batch-call-mode grouping, scored-trigger helpers, and `GET /api/admin/dispatch_tasks/task_keys` never resolve a parallel dispatch-only name. Hard cutover in config/admin: retired keys are rejected on new saves; no read-time alias acceptance.

**Sibling scope (do not implement here):** DB row rename and consult/dispatcher runtime paths (**AST-748**, Hedy); Scheduled Actions React UI (**AST-749**, Katherine).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Replace `consult_*` with `grade_*` in schedulable/batch frozensets; delete `_CONSULT_TASK_TO_AGENT_TASK`; make `resolve_dispatch_task_config_key` identity-only; update trigger/entity helper branches | utils |
| `src/core/bootstrap.py` | Tighten schedulable-key validation now that graded keys are direct `TASK_CONFIG` members | core |
| `src/ui/api/api_admin.py` | Reject retired `consult_*` on dispatch create; ensure `task_keys` metadata uses `grade_*` without alias resolution | ui |
| `docs/ASTRAL_CODE_RULES.md` | Dispatch pipeline table + §2.7 alias wording → `grade_*` | docs |
| `docs/ASTRAL_TEST_BIBLE.md` | Schedulable-key / dispatch admin notes → `grade_*` | docs |
| `docs/test-bible/utils/config.md` | `consult_like` dispatch hop name → `grade_like` where describing schedulable vocabulary | docs |
| `docs/test-bible/ui/server.md` | `DISPATCH_SCHEDULABLE_TASK_KEYS` example + alias note → `grade_*` / no alias | docs |

**Out of scope (do not touch):** `src/core/consult.py`, `src/core/dispatcher.py`, `src/data/database.py` (migration + save paths — **AST-748**), React admin UI (**AST-749**), `tests/**`, `TASK_CONFIG` entry bodies / grading semantics.

## Stage 1: Config — schedulable keys and alias removal

**Done when:** `grep consult_do src/utils/config.py` returns no matches in schedulable/trigger/entity/batch sets or alias map; `grade_do`, `grade_get`, `grade_like` appear in `DISPATCH_SCHEDULABLE_TASK_KEYS` and `_DISPATCH_BATCH_CALL_MODE_ONE`; `dispatch_task_admin_defaults("grade_do")` returns `entity_type="job"`, `trigger_state="PASSED_JD"`, `batch_call_mode=1`; `dispatch_task_admin_defaults("consult_do")` raises `KeyError`; `resolve_dispatch_task_config_key("consult_do")` returns `"consult_do"` (no alias).

1. In `src/utils/config.py`, add a module-level frozenset after `_DISPATCH_BATCH_CALL_MODE_ONE`:

```python
RETIRED_DISPATCH_TASK_KEYS = frozenset({"consult_do", "consult_get", "consult_like"})
```

Export it (no `__all__` change required unless one exists for dispatch helpers — match surrounding style).

2. In `DISPATCH_SCHEDULABLE_TASK_KEYS` (~line 1299), replace `"consult_do", "consult_get", "consult_like"` with `"grade_do", "grade_get", "grade_like"`. Keep `"analysis_upshot"` and all other keys unchanged.

3. In `_DISPATCH_BATCH_CALL_MODE_ONE` (~line 1308), replace `"consult_do", "consult_get", "consult_like"` with `"grade_do", "grade_get", "grade_like"`.

4. Delete the entire `_CONSULT_TASK_TO_AGENT_TASK` dict (~lines 1318–1322).

5. Replace `resolve_dispatch_task_config_key` (~lines 1325–1328) with identity passthrough:

```python
def resolve_dispatch_task_config_key(task_key: str) -> str:
    """Return task_key unchanged (AST-747: consult→grade alias map retired)."""
    return (task_key or "").strip()
```

6. In `_dispatch_trigger_state_for_task_key`, replace the three branches:

```python
    if task_key == "consult_do":
        return "PASSED_JD"
    if task_key == "consult_get":
        return "PASSED_DO"
    if task_key == "consult_like":
        return "PASSED_GET"
```

with:

```python
    if task_key == "grade_do":
        return "PASSED_JD"
    if task_key == "grade_get":
        return "PASSED_DO"
    if task_key == "grade_like":
        return "PASSED_GET"
```

7. In `_dispatch_entity_type_for_task_key`, in the explicit job-entity tuple (~lines 1396–1400), replace `"consult_do", "consult_get", "consult_like"` with `"grade_do", "grade_get", "grade_like"`.

8. In `_dispatch_entity_type_for_task_key` and `_dispatch_trigger_state_for_task_key`, remove fallback paths that call `resolve_dispatch_task_config_key` **only where** the sole purpose was consult alias lookup — keep the fallback for keys whose `TASK_CONFIG` entry uses `not_ready_state` (e.g. roster keys) unchanged:

   - `_dispatch_trigger_state_for_task_key`: after direct branches, keep `cfg = TASK_CONFIG.get(task_key)` then `resolved = TASK_CONFIG.get(resolve_dispatch_task_config_key(task_key))` — with identity resolver this is equivalent to a single `TASK_CONFIG.get(task_key)` lookup; leave structure as-is (no drive-by refactor).
   - `_dispatch_entity_type_for_task_key`: same — leave dual lookup; identity makes it harmless.

9. `dispatch_task_key_is_scored` (~line 1448): keep `rk = resolve_dispatch_task_config_key(task_key)` (identity); no logic change required once schedulable keys are `grade_*` in `TASK_CONFIG`.

10. Grep `src/utils/config.py` for `consult_do`, `consult_get`, `consult_like`. Remaining hits must be comments only (e.g. historical AST-479 notes). Update any operator-facing comment that implies `consult_*` is schedulable to reference `grade_*` instead.

⚠️ **Decision:** Keep `resolve_dispatch_task_config_key` as a public identity function rather than deleting it — **AST-748** still imports it from `consult.py` / `bootstrap.py`; removing the symbol would break the tree before the runtime cutover lands. Alias removal is the behavioral change.

⚠️ **Decision:** Do not add read-time compat that maps `consult_*` → `grade_*` anywhere in config or admin — hard cutover per parent AC.

## Stage 2: Bootstrap + Admin API — validation and task_keys metadata

**Done when:** Server bootstrap passes with new schedulable set; `POST /api/admin/dispatch_tasks` with `task_key: "consult_do"` returns HTTP 400 with a clear error mentioning retired keys; same request with `task_key: "grade_do"` succeeds (or returns 409 on duplicate, not 400 on key); `GET /api/admin/dispatch_tasks/task_keys` includes `grade_do` / `grade_get` / `grade_like` with `trigger_state` `PASSED_JD` / `PASSED_DO` / `PASSED_GET` and `is_scored: true`; response does **not** include schedulable defaults for `consult_*` from the `DISPATCH_SCHEDULABLE_TASK_KEYS` loop (keys may still appear if legacy DB rows exist — **AST-748** removes those rows).

1. In `src/core/bootstrap.py`, in `_validate_runtime_coupling()` (~lines 33–42), replace the schedulable loop body with:

```python
    for key in DISPATCH_SCHEDULABLE_TASK_KEYS:
        if key in TASK_CONFIG:
            continue
        try:
            dispatch_task_admin_defaults(key)
        except KeyError as exc:
            raise RuntimeError(
                f"bootstrap: dispatch schedulable key {key!r} missing from TASK_CONFIG"
            ) from exc
```

Remove the `resolved = resolve_dispatch_task_config_key(key)` branch — graded keys are direct `TASK_CONFIG` members; alias resolution is retired.

Remove `resolve_dispatch_task_config_key` from the import tuple if no longer referenced in this file.

2. In `src/ui/api/api_admin.py`, add to config imports:

```python
    RETIRED_DISPATCH_TASK_KEYS,
```

3. Add a private helper near `_dispatch_task_key_form_meta`:

```python
def _retired_dispatch_task_key_error(task_key: str) -> str | None:
    tk = (task_key or "").strip()
    if tk in RETIRED_DISPATCH_TASK_KEYS:
        return (
            f"task_key {tk!r} is retired; use "
            f"grade_do, grade_get, or grade_like instead"
        )
    return None
```

4. In `create_dtask()` (~line 823), after the required-fields check and **before** `save_dispatch_task`:

```python
    retired_err = _retired_dispatch_task_key_error(data.get("task_key"))
    if retired_err:
        return jsonify({"error": retired_err}), 400
```

5. In `_dispatch_task_key_form_meta` (~line 762), set `catalog_key = task_key` (use stripped task_key) instead of `resolve_dispatch_task_config_key(task_key)`. Remove `resolve_dispatch_task_config_key` from imports if unused elsewhere in the file.

6. Grep `src/ui/api/api_admin.py` for `resolve_dispatch_task_config_key` — zero remaining references after step 5.

7. Do **not** add `task_key` to `update_dtask` allowed fields (PUT cannot retarget rows today). No PUT change required.

⚠️ **Decision:** Retired-key rejection lives in the admin API layer for this ticket; **AST-748** may add matching guards in `save_dispatch_task` / DB migration. Duplicate defense: `dispatch_task_admin_defaults("consult_do")` already raises `KeyError` if something bypasses the API — acceptable until Hedy wires database validation.

## Stage 3: Documentation — operator-facing vocabulary

**Done when:** `grep -E 'consult_do|consult_get|consult_like' docs/ASTRAL_CODE_RULES.md docs/ASTRAL_TEST_BIBLE.md docs/test-bible/utils/config.md docs/test-bible/ui/server.md` shows no operator-facing schedulable dispatch names (runtime function names like `consult_do_batch` in other test-bible files may remain until **AST-748**).

1. In `docs/ASTRAL_CODE_RULES.md` §2.6 example (~line 195), change “consult_get dispatch task” to “`grade_get` dispatch task”.

2. In §2.7 step 1 (~line 209), replace:

   > `resolve_dispatch_task_config_key(task_type)` (`consult_*` dispatch keys map to `grade_*` orchestration entries)

   with:

   > `TASK_CONFIG[task_type]` directly — schedulable graded consult hops use `grade_do`, `grade_get`, and `grade_like` (same keys as Manage Tasks; no dispatch alias).

3. In the Dispatch pipeline table (~lines 373–375), rename rows:

   | consult_do | → | grade_do |
   | consult_get | → | grade_get |
   | consult_like | → | grade_like |

   Keep PW/AI/DB columns unchanged (`/` for grade_like PW column).

4. In `docs/ASTRAL_TEST_BIBLE.md` (~line 370), where **`consult_like`** describes the dispatch hop / schedulable step, rename to **`grade_like`**. Leave **`analysis_upshot`** and state names (`PASSED_LIKE`, etc.) unchanged.

5. In `docs/ASTRAL_TEST_BIBLE.md` (~line 1839 test-child note), replace the example schedulable key `consult_do` and the alias sentence with: schedulable keys are literal `TASK_CONFIG` index strings (e.g. **`grade_do`**, **`prefilter`**); **`resolve_dispatch_task_config_key`** is identity-only post-AST-747.

6. In `docs/test-bible/utils/config.md` (~line 38), rename schedulable hop **`consult_like`** → **`grade_like`** in the dispatch sentence; keep state machine names.

7. In `docs/test-bible/ui/server.md` (~line 29), replace the `consult_do` example and alias-resolution note with `grade_do` and “no consult→grade alias map”.

## Self-Assessment

**Scope:** `Single-Component` — touches config utils, one bootstrap validation loop, one admin API module, and doc strings; no runtime consult/dispatcher or DB migration.

**Conf:** `high` — pattern is explicit key substitution plus deleting a known alias dict; `grade_*` entries already exist in `TASK_CONFIG` with correct pass/fail states.

**Risk:** `Medium` — wrong schedulable set or leftover alias acceptance would let Susan create `consult_*` rows or mis-bucket tasks in admin metadata until **AST-748**/**AST-749** land; pipeline execution paths are out of scope so production dispatch is unchanged until sibling merges.

## ASTRAL_CODE_RULES self-review

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Alias map removed; single vocabulary for schedulable graded hops. |
| §2.1 config | Schedulable keys remain explicit frozenset; missing config stays crash-worthy via `KeyError`. |
| §2.4 batch | `_DISPATCH_BATCH_CALL_MODE_ONE` updated in place; no new batch patterns. |
| §2.6 state machine | Trigger states unchanged (`PASSED_JD` → DO, etc.); only task_key strings change. |
| §3.3 imports | No new cross-layer imports; bootstrap still imports utils only. |
| §3.5 naming | Aligns dispatch `task_key` with `TASK_CONFIG` index — parent epic intent. |

No conflicts requiring `conf-!!-NONE`.

## Integration notes (for build-child / siblings)

- **AST-748** must land before Susan can run migrated `grade_*` rows end-to-end; until then, existing `consult_*` DB rows remain but are not schedulable in config defaults.
- **Betty** will update `tests/component/ui/api/test_api_admin.py` assertions that reference `consult_do` in `task_keys` metadata (e.g. AST-739 grouping tests) — do not edit tests in this ticket.
- **`resolve_dispatch_task_config_key`** remains imported by `consult.py` until **AST-748** removes those call sites; identity behavior is intentional.
