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
