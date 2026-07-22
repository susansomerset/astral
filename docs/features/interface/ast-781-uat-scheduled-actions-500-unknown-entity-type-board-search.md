<!-- linear-archive: AST-781 archived 2026-07-22 -->

## Linear archive (AST-781)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-781/uat-scheduled-actions-500-unknown-entity-type-board-search  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-763 — Cannot change task_key in the scheduled task modal  
**Blocked by / blocks / related:** parent: AST-763

### Description

## What failed

Opening **Admin → Scheduled Actions** (`/admin/scheduled_actions`) fails to load the dispatch task list. Browser shows loading/error; server log shows `GET /api/admin/dispatch_tasks` returning **500** with:

`ValueError: Unknown entity_type: board_search`

at `api_admin.list_dtasks` → `database.count_eligible_for_dispatch_task` → `count_entities_in_state`.

## Expected

Scheduled Actions page loads all dispatch rows (including any legacy rows) without error; Available counts show **0** or **—** for rows that cannot be counted, not a 500 for the whole page.

## Repro

1. Log in as admin with at least one `dispatch_task` row whose `entity_type` is `board_search` (legacy boards sunset data).
2. Navigate to **Scheduled Actions**.
3. Observe `GET /api/admin/dispatch_tasks` → 500 and page does not render the table.

## Parent AC (quoted inline)

> 7. Add Task, run/stop, AUTO/Dbg column toggles, filters, collapsible task groups, and Stop All still behave as before UAT on AST-735.

## Boundaries

* This bug does **not** change: edit-modal task_key selector (AST-773); scheduler tick/claim logic; re-introducing boards product features.
* Fix should tolerate retired `entity_type` values on existing rows (count **0** / skip eligibility) or document one-time admin cleanup — not crash the list endpoint.

### Comments

#### radia — 2026-06-24T05:40:32.321Z
## Radia review — AST-781

**Diff:** `origin/dev...origin/sub/AST-763/AST-781-scheduled-actions-500-board-search-entity-type` @ `15db572`
**AST-781 product commits:** `2e229d6` (code), `8f64615` (tests), `15db572` (merge-tests)

### Plan fidelity

Stage 1 matches the plan: `ENTITY_TYPES` added to the existing config import block; `count_eligible_for_dispatch_task` returns `0` when `entity_type not in ENTITY_TYPES` before fall-through to `count_entities_in_state`. Shared callers (`list_dtasks`, `get_due_tasks`, `run_task` enrichment) get the tolerant path without UI or dispatcher changes. `count_entities_in_state` stays strict for known types.

### ASTRAL_CODE_RULES

| Check | Result |
|-------|--------|
| §2.1 config / DRY | `ENTITY_TYPES` from `config.py` — not a hardcoded allowlist |
| §3.3 layer | Data-layer guard only; no UI/core imports |
| D3 fallbacks | Returning `0` for retired types is the documented AC (legacy rows show Available=0), not a silent swallow |
| B1/B2/E1 | No new imports-at-function-scope, layer bends, or logging |

No **fix-now** items.

### Tests / bible

- `TestAst766BoardSchemaSunset::test_count_eligible_board_search_entity_returns_zero` — flipped correctly.
- `TestAst781ListDtasksRetiredEntityType::test_list_dtasks_legacy_board_search_row_returns_zero_available_count` — stubs `list_dispatch_tasks` only; exercises real `count_eligible_for_dispatch_task` (no count monkeypatch). Covers the UAT 500 path.
- Bible manifest in `docs/test-bible/ui/api/api_admin.md` and `dispatch_tasks.md` matches the narrowed pytest block.

### Advisory (non-blocking)

- `8f64615` also adds `AdminScheduledActions` **`AST-785`** UX describe block in the same commit as AST-781 tests — sibling scope on the sub branch, not in AST-781 product diff. Fine for epic rollup; keep resolve-child scoped to AST-781 only.
- Three-dot diff vs `origin/dev` includes sibling test/bible rollup from `merge-tests(AST-781)` — expected on the shared sub ref; only `src/data/database.py` (+3 lines) is AST-781 product code.

**Self-Assessment alignment:** Scope `minor`, Conf `high`, Risk `low` — matches the diff.

Katherine: **resolve-child** when ready — no fix-now from this pass.

#### betty — 2026-06-24T05:38:45.311Z
## QA test manifest (AST-781)

**Publish:** `origin/sub/AST-763/AST-781-scheduled-actions-500-board-search-entity-type` @ `15db572` (`merge-tests(AST-781): origin/tests 8f64615`)

1. **Existing coverage revised (AST-766 flip):** `tests/component/data/database/test_dispatch_tasks.py::TestAst766BoardSchemaSunset::test_count_eligible_board_search_entity_returns_zero` — legacy `board_search` entity_type returns **0**, not `ValueError`.
2. **New gap — admin list enrichment:** `tests/component/ui/api/test_api_admin.py::TestAst781ListDtasksRetiredEntityType::test_list_dtasks_legacy_board_search_row_returns_zero_available_count` — real `count_eligible_for_dispatch_task` (no count monkeypatch); `GET /api/admin/dispatch_tasks` **200** with `available_count == 0`.

**Narrowed run:**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_dispatch_tasks.py::TestAst766BoardSchemaSunset::test_count_eligible_board_search_entity_returns_zero \
  tests/component/ui/api/test_api_admin.py::TestAst781ListDtasksRetiredEntityType \
  -q
```

**Bible shasum on publish ref:**
- `docs/test-bible/data/database/dispatch_tasks.md` → `b3d321e305f838840f7a039be64d40509269543a`
- `docs/test-bible/ui/api/api_admin.md` → `c4d6481e980277f0e0bee85f86bf416bf0407882`

#### katherine — 2026-06-24T02:56:18.748Z
Betty: flip `test_count_eligible_board_search_entity_raises` → expect `0`; add admin `list_dtasks` regression with legacy `board_search` row (plan QA manifest).

`origin/sub/AST-763/AST-781-scheduled-actions-500-board-search-entity-type` @ `628b899`

#### katherine — 2026-06-24T02:55:17.409Z
Plan: `docs/features/interface/ast-781-uat-scheduled-actions-500-unknown-entity-type-board-search.md`

https://github.com/susansomerset/astral/blob/sub/AST-763/AST-781-scheduled-actions-500-board-search-entity-type/docs/features/interface/ast-781-uat-scheduled-actions-500-unknown-entity-type-board-search.md

**Self-assessment**
- **Scope:** minor — one guard + import in `database.py`
- **Conf:** high — stack trace matches AST-766 fall-through; `ENTITY_TYPES` guard is established pattern
- **Risk:** low — only legacy invalid entity_type rows; valid counts unchanged

Single stage: early return 0 in `count_eligible_for_dispatch_task` when `entity_type not in ENTITY_TYPES`. Betty flips AST-766 regression test and adds admin list test.

---

# AST-781 — UAT: Scheduled Actions 500 — Unknown entity_type board_search

**Linear:** [AST-781 — UAT: Scheduled Actions 500 — Unknown entity_type board_search](https://linear.app/astralcareermatch/issue/AST-781/uat-scheduled-actions-500-unknown-entity-type-board-search)  
**Parent:** AST-763 (AC reference only — inline in ticket Description)  
**Publish ref:** `origin/sub/AST-763/AST-781-scheduled-actions-500-board-search-entity-type`

## Summary

Susan UAT: **Admin → Scheduled Actions** (`GET /api/admin/dispatch_tasks`) returns **500** when any legacy `dispatch_task` row still has `entity_type='board_search'` (boards sunset per AST-766 left DB rows, not product code). The failure is `ValueError: Unknown entity_type: board_search` from `count_eligible_for_dispatch_task` → `count_entities_in_state`. Fix: treat entity types outside `ENTITY_TYPES` as **zero eligible** — page loads all rows; legacy rows show **Available = 0** instead of crashing the whole list. **No** reintroduction of boards product, scheduler changes, or edit-modal work (AST-773).

**Root cause (verified on branch):** AST-766 removed the `board_search` count branch; fall-through hits `count_entities_in_state`, which raises for unknown types. Callers affected: `api_admin.list_dtasks`, `database.get_due_tasks`, `dispatcher.run_task` (available_count enrichment).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Early return `0` in `count_eligible_for_dispatch_task` when `entity_type not in ENTITY_TYPES`; import `ENTITY_TYPES` from config | data |

**QA manifest (Betty — not engineer commits):**

| File | Change |
|------|--------|
| `tests/component/data/database/test_dispatch_tasks.py` | Rename/update `test_count_eligible_board_search_entity_raises` → expect `0`, not `ValueError` |
| `tests/component/ui/api/test_api_admin.py` | Add test: `list_dtasks` returns 200 with legacy `board_search` row and `available_count == 0` (real `count_eligible`, no monkeypatch) |

**Out of scope:** Deleting legacy `board_search` dispatch rows; `count_entities_in_state` signature change; dispatcher `_run_unified` entity routing for retired types; AST-773 edit-modal task_key selector; frontend changes.

---

## Stage 1: Guard count path for retired entity types

**Done when:** `count_eligible_for_dispatch_task({"entity_type": "board_search", "trigger_state": "ACTIVE", "candidate_id": "c1", ...})` returns `0` without raising; `GET /api/admin/dispatch_tasks` returns 200 when `list_dispatch_tasks` includes a legacy `board_search` row; `python3 -m py_compile src/data/database.py` passes.

1. In `src/data/database.py`, add `ENTITY_TYPES` to the existing `from src.utils.config import (...)` block (~line 61).

2. In **`count_eligible_for_dispatch_task`** (~line 5721), immediately after the existing guard:
   ```python
   if not entity_type or not state or not candidate_id:
       return 0
   ```
   add:
   ```python
   if entity_type not in ENTITY_TYPES:
       return 0
   ```

   ⚠️ **Decision:** Guard at **`count_eligible_for_dispatch_task`** (not `api_admin.list_dtasks` only) so **`get_due_tasks`**, **`run_task`**, and admin list share one tolerant path. Uses **`ENTITY_TYPES`** from config (rules §2.1 single source) — covers `board_search` and any future retired type without a hardcoded allowlist.

3. **Do not** change `count_entities_in_state` — it remains strict for callers that pass known types; the guard above prevents fall-through for legacy rows.

4. Manual smoke (engineer, before Code Complete comment):
   ```bash
   python3 -m py_compile src/data/database.py
   python3 -c "
   from src.data import database as db
   assert db.count_eligible_for_dispatch_task({
       'entity_type': 'board_search', 'trigger_state': 'ACTIVE',
       'candidate_id': 'c1', 'task_key': 'gaze_board',
   }) == 0
   print('ok')
   "
   ```

5. Post **Code Complete** Linear comment on AST-781 noting Betty must flip `test_count_eligible_board_search_entity_raises` and add admin list regression test per QA manifest above. Engineer does **not** edit `tests/`.

---

## Self-Assessment

**Scope:** `minor` — One guard clause + one import in `database.py`; no UI or dispatcher logic.

**Conf:** `high` — Root cause confirmed in stack trace and AST-766 fallout; pattern matches `ENTITY_TYPES` usage in `agent.py`; existing AST-766 test documents the regression to flip.

**Risk:** `low` — Only affects rows whose `entity_type` is already invalid for claim/run; valid job/company/candidate counts unchanged.

---

## ASTRAL_CODE_RULES check

| Rule | Status |
|------|--------|
| §2.1 config / DRY | Uses `ENTITY_TYPES` from `config.py`, not a duplicated list |
| §2.4 batch | Retired types report 0 eligible — consistent with “cannot be counted” AC |
| §3.3 imports | `ENTITY_TYPES` added to existing config import block |
| Layer boundaries | Data-layer guard only; no UI/core changes |

No conflicts.

---

## Review (build)

**Built:** `origin/sub/AST-763/AST-781-scheduled-actions-500-board-search-entity-type` @ `2e229d6`

Stage 1: `ENTITY_TYPES` import + early return `0` in `count_eligible_for_dispatch_task` when `entity_type not in ENTITY_TYPES` — legacy `board_search` rows no longer 500 the admin list.

**Betty / qa-child:** Flip `test_count_eligible_board_search_entity_raises` to expect `0`; add `test_api_admin.py` regression for `list_dtasks` with legacy `board_search` row (`available_count == 0`, no count monkeypatch).

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-763/AST-781-scheduled-actions-500-board-search-entity-type` @ `15db572`  
**Product:** `2e229d6` — no **fix-now** items. Plan fidelity and ASTRAL_CODE_RULES checks passed.

---

## Resolution (2026-06-24)

Radia review had **zero fix-now** items — no product changes in resolve pass. Betty manifest green (2 tests). §9a dry-run: `HEAD` merges cleanly into `origin/dev` and `origin/ftr/AST-763-edit-modal-task-key` after epic worktree synced with `origin/dev`.

**Publish tip:** `origin/sub/AST-763/AST-781-scheduled-actions-500-board-search-entity-type` @ _(tip after push)_
