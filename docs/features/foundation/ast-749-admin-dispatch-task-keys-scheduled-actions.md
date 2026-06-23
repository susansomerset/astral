# AST-749 — Admin dispatch task_keys and Scheduled Actions alignment

- **Linear (this ticket):** [AST-749](https://linear.app/astralcareermatch/issue/AST-749/admin-dispatch-task-keys-and-scheduled-actions-alignment-task-keys-vs-dispatch)
- **Parent:** [AST-736](https://linear.app/astralcareermatch/issue/AST-736/task-keys-vs-dispatch-task-keys)
- **Publish ref:** `origin/sub/AST-736/AST-749-admin-dispatch-task-keys-scheduled-actions`

## Summary

Close parent **AST-736** acceptance criteria **#4** and **#5** on the admin dispatch surfaces Katherine owns: `GET /api/admin/dispatch_tasks/task_keys` and Scheduled Actions phase grouping must use the row's `task_key` string directly (`grade_do`, `grade_get`, `grade_like`) with grouping metadata from the matching `agent_task` row and schedulable defaults from `dispatch_task_admin_defaults` — no consult→grade alias resolution and no `(unassigned)` buckets caused by legacy `consult_*` keys. Retired `consult_*` keys must not appear in the Add Task picker; POST rejection for retired keys is already **AST-747** (verify only).

**Sibling scope (do not implement here):** Config schedulable frozensets and `resolve_dispatch_task_config_key` identity (**AST-747**, Ada); DB row rename and consult/dispatcher runtime (**AST-748**, Hedy); **AST-572** filters / Retry flag UI.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_admin.py` | Exclude retired `consult_*` from `dispatch_task_keys`; fix `_dispatch_task_key_form_meta` docstring | ui |

**Out of scope (sibling tickets — do not touch):**

| Ticket | Owner | Scope |
|--------|-------|-------|
| AST-747 | Ada | `DISPATCH_SCHEDULABLE_TASK_KEYS`, `dispatch_task_key_retired_message`, identity `resolve_dispatch_task_config_key`, `create_dtask` POST guard |
| AST-748 | Hedy | `dispatch_task` row migration `consult_*` → `grade_*`, `consult.py` / `dispatcher.py` runtime |
| Betty | Betty | `tests/component/ui/api/test_api_admin.py`, `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx`; test-bible rows |

**No planned edits:** `src/ui/frontend/**` (Scheduled Actions already buckets by `allTaskKeys[row.task_key]` per **AST-739**); `src/utils/config.py`; `src/data/database.py`; `tests/**`.

## Prerequisite (build gate — not a commit stage)

**Done when:** Epic worktree `astral-AST-736/` is on `sub/AST-736/AST-749-admin-dispatch-task-keys-scheduled-actions` with `origin/dev` merged (`BEHIND=0` vs `origin/dev`) and `origin/ftr/ast-736-task-keys-vs-dispatch-task-keys` merged; **AST-747** config cutover present on ftr (`grade_*` in `DISPATCH_SCHEDULABLE_TASK_KEYS`, `consult_*` in `DISPATCH_RETIRED_TASK_KEYS`, identity `resolve_dispatch_task_config_key`).

⚠️ **Decision:** **AST-748** migration should be on ftr before Susan UATs migrated rows, but this ticket's API/UI alignment can build once **AST-747** is on ftr. Do not edit `database.py` here.

## Stage 1: `dispatch_task_keys` — direct `grade_*` metadata, hide retired keys

**Done when:** `GET /api/admin/dispatch_tasks/task_keys` includes `grade_do`, `grade_get`, and `grade_like` with `entity_type` / `trigger_state` from `dispatch_task_admin_defaults` and grouping fields from `database.get_agent_task` for those same keys; `consult_do`, `consult_get`, and `consult_like` are **absent** from the JSON even when `list_dispatch_tasks()` still returns legacy rows (pre-migration DB); `POST /api/admin/dispatch_tasks` with `task_key: consult_do` still returns 400 with retired message (verify — **AST-747**, no edit unless missing).

1. In `src/ui/api/api_admin.py`, add `DISPATCH_RETIRED_TASK_KEYS` to the existing `src.utils.config` import block (alongside `DISPATCH_SCHEDULABLE_TASK_KEYS`).

2. Confirm `_dispatch_task_key_form_meta` already sets `catalog_key = (task_key or "").strip()` and calls `_catalog_task_grouping_meta(catalog_key)` — **do not** reintroduce `resolve_dispatch_task_config_key`. If the file still aliases consult→grade, replace with direct `task_key` lookup and stop.

3. Replace the `_dispatch_task_key_form_meta` docstring (~line 762) with:

```python
    """Scheduled Actions form defaults: schedulable keys use dispatch_task_admin_defaults;
    grouping fields from agent_task row for the dispatch task_key (AST-736 — no alias map)."""
```

4. In `dispatch_task_keys()`, inside the `for r in list_dispatch_tasks():` loop, after `k = r.get("task_key", "")` and the empty check, add:

```python
        if k in DISPATCH_RETIRED_TASK_KEYS:
            continue
```

5. After the existing `hidden` pop loop at the end of `dispatch_task_keys()`, add the same retirement filter on the response dict:

```python
    for tk in DISPATCH_RETIRED_TASK_KEYS:
        seen.pop(tk, None)
```

6. Grep `src/ui/api/api_admin.py` for `consult_do`, `consult_get`, `consult_like` — expect only the adhoc live-content comment `grade_do/get/like` (line ~976) and consult module imports; **zero** schedulable-key or alias references.

7. Manual verification on epic worktree (Flask admin client or browser):

   - `GET /api/admin/dispatch_tasks/task_keys` → `keys["grade_do"]["entity_type"] == "job"`, `keys["grade_do"]["trigger_state"] == "PASSED_JD"` (from `dispatch_task_admin_defaults`).
   - Same response: `"consult_do" not in keys`, `"consult_get" not in keys`, `"consult_like" not in keys`.
   - `keys["grade_do"]` contains `task_group_name`, `task_group_order`, `task_seq`, `task_name` from DB seed (not `phase` / `seq` keys).
   - With a `dispatch_task` row `task_key=grade_do` and matching `agent_task` grouping (e.g. `task_group_name` **D. Job Analysis**), Scheduled Actions renders that row under **D. Job Analysis** — not `(unassigned)` — when candidate filter shows the row. Table Task column still shows `grade_do`.

⚠️ **Decision:** Do **not** add read-time alias that maps `consult_do` grouping to `grade_do` — retired keys are excluded from `task_keys` and migrated off rows by **AST-748**. Susan schedules `grade_*` only post-cutover.

## Execution contract

Binding per **plan-child**: **Stage 1** only; **one commit** on epic worktree during **build-child**, publish to **`origin/sub/AST-736/AST-749-admin-dispatch-task-keys-scheduled-actions`**. Do not edit `tests/`, `docs/ASTRAL_TEST_BIBLE.md`, or `docs/test-bible/**`. Do not edit `src/utils/config.py`, `src/data/database.py`, `src/core/consult.py`, or `src/ui/frontend/**`. On ambiguity — **`🛑 Stage 1 blocked`** on **AST-736** parent; stop.

## Self-Assessment

**Scope:** `Single-Component` — one admin API handler and docstring in `api_admin.py`; Scheduled Actions React already consumes `task_keys` by dispatch `task_key` (**AST-739**).

**Conf:** `high` — **AST-739** established DB-backed grouping; **AST-747** established retired-key POST guard and identity catalog lookup; this ticket adds retirement filtering on the `task_keys` read path mirroring `admin_hidden_dispatch_task_keys`.

**Risk:** `Medium` — incorrect retirement filtering could hide a legitimate key from the Add Task picker, but the frozenset is exactly the three retired consult aliases; wrong grouping metadata would mis-bucket `grade_*` rows in Scheduled Actions without breaking pipeline execution.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses existing `DISPATCH_RETIRED_TASK_KEYS` frozenset; mirrors `admin_hidden_dispatch_task_keys` pop pattern. |
| §2.1 config | No new config keys; reads existing retirement frozenset only. |
| §2.4 batch | N/A — admin metadata endpoint. |
| §2.6 state machine | N/A — display/scheduling metadata only. |
| §3.3 imports | UI API imports one additional config constant; grouping still via `database.get_agent_task`. |
| §3.5 naming | Response fields remain `task_group_order`, `task_group_name`, `task_seq`, `task_name`. |

No conflicts requiring `!!-NONE`.

## QA / test manifest hints (Betty)

| File | Expected change |
|------|-----------------|
| `tests/component/ui/api/test_api_admin.py` | Add `test_dispatch_task_keys_excludes_retired_consult_keys` — monkeypatch `list_dispatch_tasks` to return `consult_do` row; assert absent from GET body; assert `grade_do` present with schedulable defaults. |
| `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` | Add case: `grade_do` dispatch row + `taskKeysConfig.grade_do` grouping → section header matches `task_group_name` (e.g. `/D\. Job Analysis/`), not `(unassigned)`. |
| `docs/test-bible/ui/api/api_admin.md` | Row for AST-749 retirement filter on `task_keys`. |
| `docs/test-bible/frontend/pages.md` | Row for `grade_do` Scheduled Actions grouping test. |

## Review (build)

| Field | Value |
|-------|-------|
| Build date | 2026-06-23 |
| Publish ref | `origin/sub/AST-736/AST-749-admin-dispatch-task-keys-scheduled-actions` @ `b303a07` |
| Stages | Stage 1 — `DISPATCH_RETIRED_TASK_KEYS` filter on `dispatch_task_keys`; `_dispatch_task_key_form_meta` docstring |

**Out of build scope (Betty / qa-child):** component tests and test-bible rows per QA hints above.
