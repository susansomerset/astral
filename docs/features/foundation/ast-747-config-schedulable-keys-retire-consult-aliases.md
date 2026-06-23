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
| `src/utils/config.py` | Replace `consult_*` with `grade_*` in schedulable/batch frozensets; add `DISPATCH_RETIRED_TASK_KEYS` + `dispatch_task_key_retired_message`; remove `_CONSULT_TASK_TO_AGENT_TASK`; identity `resolve_dispatch_task_config_key`; update trigger/entity helpers | utils |
| `src/core/bootstrap.py` | Tighten schedulable-key validation now that graded keys are direct `TASK_CONFIG` members | core |
| `src/ui/api/api_admin.py` | Reject retired `consult_*` on dispatch create; ensure `task_keys` metadata uses `grade_*` without alias resolution | ui |
| `docs/ASTRAL_CODE_RULES.md` | Dispatch pipeline table + §2.7 alias wording → `grade_*` | docs |
| `docs/ASTRAL_TEST_BIBLE.md` | Schedulable-key / dispatch admin notes → `grade_*` | docs |
| `docs/test-bible/utils/config.md` | Schedulable hop name → `grade_like` where describing dispatch vocabulary | docs |
| `docs/test-bible/ui/server.md` | `DISPATCH_SCHEDULABLE_TASK_KEYS` example + alias note → `grade_*` / no alias | docs |

**Out of scope (sibling tickets — do not touch):**

| Ticket | Owner | Scope |
|--------|-------|-------|
| AST-748 | Hedy | DB row rename migration; `consult.py` / `dispatcher.py` runtime cutover |
| AST-749 | Katherine | Scheduled Actions React UI; dispatch modals |

**QA manifest (Betty — not engineer commits):** Update `tests/component/utils/test_config.py` schedulable-key assertions; `tests/component/ui/api/test_api_admin.py` task_keys derivation tests; `docs/test-bible/core/consult.md`, `docs/test-bible/core/dispatcher.md` runtime wording when **AST-748** lands.

## Prerequisite (build gate — not a commit stage)

**Done when:** Epic worktree is on `sub/AST-736/AST-747-config-schedulable-keys-retire-consult-aliases` with `origin/dev` and `origin/ftr/ast-736-task-keys-vs-dispatch-task-keys` merged.

⚠️ **Decision:** **test-child** green on the full component manifest requires **AST-748** runtime changes — removing the config alias breaks `consult.run_consult_task` paths that still pass `consult_*` until Hedy lands. Ada completes **code()** for config + admin + rules only; do not patch `src/core/consult.py` or `src/core/dispatcher.py` in this ticket.

## Stage 1: Config — schedulable keys, retired keys, collapse alias map

**Done when:** `grep consult_do src/utils/config.py` returns no schedulable/alias references (JOB_STATES comments may still mention consult outcomes); `dispatch_task_admin_defaults("grade_do")` returns `entity_type=job`, `trigger_state=PASSED_JD`, `batch_call_mode=1`; `dispatch_task_admin_defaults("consult_do")` raises with a retired-key message; `resolve_dispatch_task_config_key("grade_do")` returns `"grade_do"`.

1. In `src/utils/config.py`, add module-level frozenset immediately above `DISPATCH_SCHEDULABLE_TASK_KEYS`:

```python
DISPATCH_RETIRED_TASK_KEYS = frozenset({
    "consult_do", "consult_get", "consult_like",
})
```

2. Add public helper (same file, near `dispatch_task_admin_defaults`):

```python
_RETIRED_DISPATCH_TASK_KEY_REPLACEMENTS = {
    "consult_do": "grade_do",
    "consult_get": "grade_get",
    "consult_like": "grade_like",
}

def dispatch_task_key_retired_message(task_key: str) -> str | None:
    """Return operator-facing error text when task_key is retired, else None."""
```

When `task_key.strip()` is in `DISPATCH_RETIRED_TASK_KEYS`, return exactly:
`f"task_key {tk!r} is retired; use {_RETIRED_DISPATCH_TASK_KEY_REPLACEMENTS[tk]!r}"`.

3. In `DISPATCH_SCHEDULABLE_TASK_KEYS`, remove `"consult_do"`, `"consult_get"`, `"consult_like"`. Add `"grade_do"`, `"grade_get"`, `"grade_like"`. Keep `"analysis_upshot"` and all other existing keys unchanged.

4. In `_DISPATCH_BATCH_CALL_MODE_ONE`, replace `"consult_do"`, `"consult_get"`, `"consult_like"` with `"grade_do"`, `"grade_get"`, `"grade_like"`.

5. Delete dict `_CONSULT_TASK_TO_AGENT_TASK` entirely.

6. Replace `resolve_dispatch_task_config_key` body with identity only:

```python
def resolve_dispatch_task_config_key(task_key: str) -> str:
    """Return task_key unchanged — dispatch and TASK_CONFIG share one string (AST-736)."""
    return (task_key or "").strip()
```

Do **not** map retired keys to replacements in this function.

7. In `_dispatch_trigger_state_for_task_key`, replace the three `consult_*` branches with `grade_do` → `PASSED_JD`, `grade_get` → `PASSED_DO`, `grade_like` → `PASSED_GET`.

8. In `_dispatch_entity_type_for_task_key`, replace the hardcoded tuple `"consult_do", "consult_get", "consult_like"` with `"grade_do", "grade_get", "grade_like"`.

9. In `dispatch_task_admin_defaults`, as the **first** statement after normalizing `tk`:

```python
    retired = dispatch_task_key_retired_message(tk)
    if retired:
        raise KeyError(retired)
```

Keep existing `DISPATCH_SCHEDULABLE_TASK_KEYS` membership check unchanged after the retired guard.

10. Simplify `dispatch_task_key_is_scored`:

```python
def dispatch_task_key_is_scored(task_key: str) -> bool:
    tk = (task_key or "").strip()
    return bool((TASK_CONFIG.get(tk) or {}).get("scored"))
```

11. Grep `src/utils/config.py` for remaining `consult_do`, `consult_get`, `consult_like` — only JOB_STATES / comment references to consult **outcomes** may remain.

⚠️ **Decision:** Keep `resolve_dispatch_task_config_key` as a named identity function — **AST-748** still imports it from `consult.py` / `bootstrap.py`; removing the symbol would break the tree before runtime cutover.

## Stage 2: Bootstrap + Admin API — validation and task_keys metadata

**Done when:** Server bootstrap passes with new schedulable set; `POST /api/admin/dispatch_tasks` with `task_key: "consult_do"` returns HTTP 400 with body containing `retired` and `grade_do`; `GET /api/admin/dispatch_tasks/task_keys` includes `grade_do` / `grade_get` / `grade_like` with correct trigger defaults and `is_scored: true`.

1. In `src/core/bootstrap.py`, in `_validate_runtime_coupling()`, replace the schedulable loop body with:

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

Remove the `resolved = resolve_dispatch_task_config_key(key)` branch. Remove `resolve_dispatch_task_config_key` from imports if unused.

2. In `src/ui/api/api_admin.py`, add import: `dispatch_task_key_retired_message` from `src.utils.config`.

3. In `create_dtask()`, immediately after the required-field check and **before** `save_dispatch_task`:

```python
    retired = dispatch_task_key_retired_message(data.get("task_key", ""))
    if retired:
        return jsonify({"error": retired}), 400
```

4. In `_dispatch_task_key_form_meta`, set `catalog_key = (task_key or "").strip()` instead of `resolve_dispatch_task_config_key(task_key)`. Remove `resolve_dispatch_task_config_key` from imports if unused elsewhere.

5. Update the adhoc live-content comment near line 973 from `consult_do/get/like` to `grade_do/get/like`.

6. Grep `src/ui/api/api_admin.py` for `consult_do`, `consult_get`, `consult_like` — zero remaining references.

⚠️ **Decision:** Do **not** add retired-key validation to `PUT /api/admin/dispatch_tasks/<id>` — updates cannot change `task_key`; migration of existing rows is **AST-748**.

## Stage 3: Documentation — operator-facing vocabulary

**Done when:** `grep consult_do docs/ASTRAL_CODE_RULES.md` returns zero matches; schedulable dispatch vocabulary in listed test-bible files uses `grade_*`.

1. In `docs/ASTRAL_CODE_RULES.md` §3.3 dispatch pipeline table (~lines 373–375), rename rows to `grade_do`, `grade_get`, `grade_like` (keep PW/AI/DB columns unchanged).

2. In §2.6 Jobs example (~line 195), change to **`grade_do`** dispatch task.

3. In §2.7 step 1 (~line 209), replace alias wording with: resolve orchestration via **`TASK_CONFIG[task_type]`** — dispatch `task_key` and catalog key are the same string for graded consult steps.

4. In `docs/ASTRAL_TEST_BIBLE.md` (~line 370), rename schedulable hop **`consult_like`** → **`grade_like`** where describing dispatch vocabulary.

5. In `docs/ASTRAL_TEST_BIBLE.md` (~line 1839), replace `consult_do` example and alias sentence with `grade_do` / identity-only resolver note.

6. In `docs/test-bible/utils/config.md` (~line 38) and `docs/test-bible/ui/server.md` (~line 29), update schedulable-key examples to `grade_*`.

## Execution contract

Binding per **plan-child**: stages **1 → 2 → 3** in order; **one commit per stage** on epic worktree during **build-child**, publish each to **`origin/sub/AST-736/AST-747-config-schedulable-keys-retire-consult-aliases`**. Do not edit `tests/` or `src/core/consult.py`, `src/core/dispatcher.py`, `src/data/database.py`. On ambiguity — **`🛑 Stage N blocked`** on **AST-736** parent; stop.

## Self-Assessment

**Scope:** `Single-Component` — primarily `src/utils/config.py` schedulable vocabulary and alias removal, with bootstrap validation, admin API guard, and rules-doc updates.

**Conf:** `high` — AST-549 established the `dispatch_task_admin_defaults` pattern; this ticket renames three frozenset members and removes a three-entry alias dict.

**Risk:** `Medium` — config-only cutover breaks runtime consult routing until **AST-748** merges; incorrect schedulable/trigger pairing would mis-label admin defaults for the three graded consult hops.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Status |
|------|--------|
| §1.3 DRY | Retiring alias map removes duplicate vocabulary. |
| §2.1 config | Schedulable keys remain explicit frozenset; retired keys fail loudly. |
| §2.4 batch | `batch_call_mode` frozenset updated in same edit as schedulable keys. |
| §2.6 state machine | Trigger states unchanged; only task_key strings change. |
| §3.3 imports | Utils-only in Stage 1; ui imports one config helper in Stage 2. |
| §3.5 naming | `grade_*` matches existing `TASK_CONFIG` index. |

No conflicts requiring `!!-NONE`.

## Integration notes (for build-child / siblings)

- **AST-748** must land before Susan can run migrated `grade_*` rows end-to-end.
- **Betty** updates component tests referencing `consult_do` in `task_keys` metadata — do not edit tests in this ticket.
- **`resolve_dispatch_task_config_key`** remains imported by `consult.py` until **AST-748** removes those call sites.
