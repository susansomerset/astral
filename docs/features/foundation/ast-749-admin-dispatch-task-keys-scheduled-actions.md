<!-- linear-archive: AST-749 archived 2026-06-23 -->

## Linear archive (AST-749)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-749/admin-dispatch-task-keys-and-scheduled-actions-alignment-task-keys-vs  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-736 — Task keys vs. dispatch task keys  
**Blocked by / blocks / related:** parent: AST-736

### Description

## What this implements

Admin dispatch surfaces expose `grade_*` keys directly: `GET /api/admin/dispatch_tasks/task_keys` and Scheduled Actions phase grouping/sequence use `TASK_CONFIG` metadata for the row's `task_key` without consult alias resolution or `(unassigned)` buckets.

## Acceptance criteria

4. Scheduled Actions phase grouping and sequence order for the three graded consult tasks match `TASK_CONFIG` without `(unassigned)` buckets caused by alias resolution.
5. Admin API rejects new saves using retired `consult_*` keys with a clear validation error; no read-time alias accepts them post-cutover; `GET /api/admin/dispatch_tasks/task_keys` lists `grade_*` with correct phase/seq/trigger defaults.

## Boundaries

* Does **not** own [config.py](<http://config.py>) alias removal — blocked on **AST-737** (may consume its API shape).
* Does **not** own DB migration or consult batch execution — sibling **Hedy** ticket.
* Does **not** implement **AST-572** filters or Retry flag UI.

## Notes for planning

* Primary: `src/ui/api/api_admin.py` (`dispatch_task_keys`, form meta), Scheduled Actions admin React components.
* Follow **AST-568** pattern: group by dispatch row `task_key`; metadata from config, not literal `TASK_CONFIG.get("consult_do")`.

## Git branch (authoritative)

Parent `ftr/ast-736-task-keys-vs-dispatch-task-keys`, child `sub/AST-736/AST-739-admin-dispatch-task-keys-scheduled-actions`.

### Comments

#### radia — 2026-06-23T19:50:55.001Z
## Radia review (AST-749)

**Diff:** `origin/dev...origin/sub/AST-736/AST-749-admin-dispatch-task-keys-scheduled-actions` @ `276ab22` (+ doc commit pending push)
**Doc:** `docs/features/foundation/ast-749-admin-dispatch-task-keys-scheduled-actions.md` (Review Radia section)

**AST-749 commits:** `b303a07` (+7 lines), `18f5cfe`. Sibling **AST-747/748** changes on publish ref — not Katherine product scope (§5d clean).

### What's solid

- **Stage 1:** `DISPATCH_RETIRED_TASK_KEYS` loop skip + terminal `seen.pop`; docstring; direct `catalog_key` trim (no alias map).
- **Tests:** API excludes legacy `consult_*` from `task_keys`; Vitest `grade_do` groups under `task_group_name`, not `(unassigned)`.

### fix-now

None.

### Recommended

**resolve-child** — no code changes. Susan UAT: Add Task picker has `grade_*` not `consult_*`; Scheduled Actions buckets `grade_do` after **AST-748** migration.

#### betty — 2026-06-23T19:48:05.029Z
## QA test manifest (AST-749)

**Publish:** `origin/sub/AST-736/AST-749-admin-dispatch-task-keys-scheduled-actions` @ `276ab22` (`merge-tests(AST-749): origin/tests 18f5cfe`)

**Run (narrowed):**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst749DispatchTaskKeysRetiredFilter \
  tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_create_dispatch_task_rejects_retired_consult_key \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  --testNamePattern="AST-749"
```

1. `tests/component/ui/api/test_api_admin.py` — `TestAst749DispatchTaskKeysRetiredFilter::test_dispatch_task_keys_excludes_retired_consult_keys` (`consult_*` absent from GET even when `list_dispatch_tasks` returns legacy rows; `grade_do` present with schedulable defaults)
2. `tests/component/ui/api/test_api_admin.py` — `TestDispatchTasks::test_create_dispatch_task_rejects_retired_consult_key` (verify **AST-747** POST guard)
3. `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` — `AST-749: grade_do row groups under task_keys metadata not (unassigned)` (**§6c** routed page)

**Bible shasum (`origin/sub/…` @ `276ab22`):**
- `docs/test-bible/ui/api/api_admin.md` — `269623c3f7aba5a14472b1bbb8b16c09267833a6339f106b7db4e68e2997dbd2`
- `docs/test-bible/frontend/pages.md` — `8f56a6647502feb5b84e3c84365eca037524f7f8a10fbc3bd4d68930b5c5c543`

— Betty

#### katherine — 2026-06-23T19:45:54.049Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-736/AST-749-admin-dispatch-task-keys-scheduled-actions/docs/features/foundation/ast-749-admin-dispatch-task-keys-scheduled-actions.md

**Scope:** `Single-Component` — `dispatch_task_keys` retirement filter + docstring in `api_admin.py`; Scheduled Actions already buckets by `allTaskKeys[row.task_key]` (AST-739).

**Conf:** `high` — mirrors hidden-key pop pattern; AST-747 already guards POST and identity catalog lookup.

**Risk:** `Medium` — mis-filtering would hide keys from Add Task picker or mis-bucket `grade_*` in UI without breaking runtime.

---

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
| Publish ref | `origin/sub/AST-736/AST-749-admin-dispatch-task-keys-scheduled-actions` @ `276ab22` |
| Commits | `b303a07` task_keys retirement filter · `18f5cfe` test (Betty) |

**Out of build scope (Betty / qa-child):** component tests and test-bible rows per QA hints above.

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-736/AST-749-admin-dispatch-task-keys-scheduled-actions` · tip **`276ab22`**

**AST-749 product commits:** `b303a07`, `18f5cfe`. Publish ref rolls up **AST-747** / **AST-748** / sibling qa on `api_admin.py` — Katherine commit is +7 lines only (§5d boundary clean).

### What's solid

| Area | Notes |
|------|-------|
| Plan Stage 1 | `DISPATCH_RETIRED_TASK_KEYS` import; loop `continue` + terminal `seen.pop` mirror `admin_hidden_dispatch_task_keys`; docstring updated; `catalog_key = (task_key or "").strip()` (no alias resolver). |
| §1.3 DRY | Reuses config frozenset; dual filter matches hidden-key pop pattern. |
| §3.3 layer | UI API imports one config constant; grouping still via `database.get_agent_task`. |
| Tests | `TestAst749DispatchTaskKeysRetiredFilter` — legacy `consult_*` rows absent, `grade_do` schedulable defaults; Vitest `grade_do` section under `task_group_name`, not `(unassigned)`. |

### Issues

| Severity | Item | Location |
|----------|------|----------|
| — | **No fix-now or discuss.** | — |

### Recommended actions

| Action | Owner |
|--------|-------|
| **resolve-child** — no code changes required from review. | Katherine |
| Susan UAT: Add Task picker shows `grade_*` not `consult_*`; Scheduled Actions `grade_do` rows bucket under DB grouping after **AST-748** migration. | Susan |

---

## Resolution

**Date:** 2026-06-23  
**Review ref:** Radia — no fix-now or discuss (`5bda6f0`).

No product changes required. §9a dry-run: `origin/sub/AST-736/AST-749-admin-dispatch-task-keys-scheduled-actions` → `origin/dev`: clean · → `origin/ftr/ast-736-task-keys-vs-dispatch-task-keys`: clean.
