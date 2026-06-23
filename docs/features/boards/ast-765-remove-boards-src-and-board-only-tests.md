# Remove boards src implementation and board-only tests (Sunset Astral Boards)

**Linear:** [AST-765](https://linear.app/astralcareermatch/issue/AST-765/remove-boards-src-implementation-and-board-only-tests-sunset-astral)  
**Parent:** [AST-757](https://linear.app/astralcareermatch/issue/AST-757/sunset-astral-boards)  
**Publish ref:** `sub/AST-757/AST-765-remove-boards-src-and-board-only-tests`

Delete all Astral Boards product code under `src/` — core module, REST API, config registry, dispatch/consult/gazer/tracker/playwright paths, and admin catalog entries for `gaze_board`. Company-centric gazer and roster flows must remain intact. Board spike CLIs under `scripts/spikes/` stay untouched.

**Pre-removal `dev` SHA (dispatch):** `8d9b01e5e75ace9c04c32711488430503075e0c3` — recorded for sibling **AST-767** Code Rules sunset section; this ticket’s **first `code(AST-765)` commit** is the second SHA.

## Out of scope (sibling tickets — do not touch)

| Ticket | Scope |
|--------|--------|
| **AST-766** | Drop `board_search` / `board_search_run` schema, job `board_search_id` column, board DDL helpers in `src/data/database.py` |
| **AST-767** | Test bible, `docs/features/boards/` archive framing, Code Rules sunset section |
| **scripts/spikes/** | Board spike CLIs (historical R&D) |

**Engineer does not commit under `tests/` or `docs/test-bible/**`** (pre-commit hook). Betty owns board test removal via **qa-child** manifest below.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/boards.py` | **Delete** entire module | core |
| `src/ui/api/api_boards.py` | **Delete** entire module | ui |
| `src/utils/url_merge.py` | **Delete** (only consumer is board deeplink) | utils |
| `src/ui/server.py` | Remove `boards_bp` import and `register_blueprint` | ui |
| `src/utils/config.py` | Remove board config blocks, helpers, dispatch/admin catalog entries | utils |
| `src/core/dispatcher.py` | Remove `board_search` entity claim/clear/identifier branches | core |
| `src/core/consult.py` | Remove `entity_type == "board_search"` routing | core |
| `src/core/gazer.py` | Remove `process_gaze_board_batch` and board DB imports | core |
| `src/core/tracker.py` | Remove `ingest_board_listings` and board-only imports/constants | core |
| `src/external/playwright.py` | Remove both `board_search_deeplink` definitions and `url_merge` import; keep `extract_raw_job_listings` (company roster) | external |

**Not in engineer commits:** `src/data/database.py` (AST-766), `tests/**`, `docs/test-bible/**`, `docs/ASTRAL_TEST_BIBLE.md`, `scripts/spikes/**`.

### QA manifest (Betty — qa-child, not engineer)

Betty deletes board-only tests and trims shared tests/fixtures after **Code Complete**. Engineer lists expected Betty work here; do not land test edits in **build-child**.

| Test file | Expected Betty change |
|-----------|----------------------|
| `tests/component/core/test_boards.py` | **Delete** |
| `tests/component/core/test_boards_gaze_ast487.py` | **Delete** |
| `tests/component/core/test_boards_generate_ast521.py` | **Delete** |
| `tests/component/core/test_board_sourced_qualify_evaluate.py` | **Delete** |
| `tests/component/ui/api/test_api_boards.py` | **Delete** |
| `tests/component/data/database/test_board_search_integration.py` | **Delete** (schema drops in AST-766) |
| `tests/component/scripts/test_cleanup_duplicate_and_board_gaze_jobs.py` | **Delete** or strip board-only cases if file mixes concerns |
| `tests/component/ui/conftest.py` | Remove `boards_client` fixture and `_board_search_schema_ensured` reset entries if only used for boards API tests |
| `tests/component/core/conftest.py` | Remove `_board_search_schema_ensured` / `_board_search_run_schema_ensured` reset entries if only for board tests |
| `tests/component/core/test_dispatcher.py` | Remove `test_claims_board_search_batch_*` / `test_board_search_*` methods |
| `tests/component/core/test_consult.py` | Remove `test_routes_board_search_to_process_gaze_board_batch` |
| `tests/component/core/test_gazer.py` | Remove `process_gaze_board_batch` test methods |
| `tests/component/core/test_tracker.py` | Remove `ingest_board_listings` test class/methods |
| `tests/component/utils/test_config.py` | Remove `list_adopted_boards` / `get_board_entry` test classes and `_board_entry` helper |
| `tests/component/ui/api/test_api_admin.py` | Remove AST-649 `gaze_board` hide tests (task key removed from catalog, not hidden) |
| `tests/component/external/test_playwright.py` | Remove `board_search_deeplink` tests only; keep roster/playwright tests |
| `tests/integration/conftest.py` | Remove board-only fixtures if present |

⚠️ **Decision:** Test deletion is Betty’s lane per `ASTRAL_GIT_WORKFLOW.md` engineer hook ban; ticket AC #2 is satisfied when Betty’s `merge-tests(AST-765)` lands, not at `code()` time.

## Stage 1: Delete boards modules and unregister API

**Done when:** `src/core/boards.py`, `src/ui/api/api_boards.py`, and `src/utils/url_merge.py` are gone; Flask no longer registers `/api/boards`; `python3 -m py_compile src/ui/server.py` passes.

1. **Delete** `src/core/boards.py`.
2. **Delete** `src/ui/api/api_boards.py`.
3. **Delete** `src/utils/url_merge.py`.
4. In `src/ui/server.py`, remove lines importing and registering `boards_bp`:
   - Delete `from ui.api.api_boards import boards_bp  # noqa: E402`
   - Delete `app.register_blueprint(boards_bp)`

## Stage 2: Purge board config and dispatch catalog

**Done when:** `rg` on `src/utils/config.py` finds no `BOARD_CONFIG`, `BOARDS_CONFIG`, `BOARD_SEARCH_STATES`, `list_adopted_boards`, `get_board_entry`, or `gaze_board` in dispatch sets; `ENTITY_TYPES` unchanged (`candidate`, `company`, `job` only); `python3 -m py_compile src/utils/config.py` passes.

1. In `src/utils/config.py`, **delete** the block from the comment `# Workflow state for saved board searches` through `get_board_entry()` (~lines 669–718): `BOARD_SEARCH_STATES`, `BOARDS_CONFIG`, entire `BOARD_CONFIG` dict, `list_adopted_boards`, `get_board_entry`.
2. In `DISPATCH_SCHEDULABLE_TASK_KEYS`, remove `"gaze_board"` from the frozenset (~line 1306).
3. In `_DISPATCH_BATCH_CALL_MODE_ONE`, remove `"gaze_board"` (~line 1315).
4. In `_dispatch_trigger_state_for_task_key`, delete the branch:
   ```python
   if task_key == "gaze_board":
       return "ACTIVE"
   ```
5. In `_dispatch_entity_type_for_task_key`, delete the branch:
   ```python
   if task_key == "gaze_board":
       return "board_search"
   ```
6. In `_dispatch_sort_by_for`, delete the branch:
   ```python
   if entity_type == "board_search":
       return "last_scan_at"
   ```
7. In `ADMIN_CONFIG`, **delete** the `hidden_dispatch_task_keys` entry and its AST-649 comment (~lines 2390–2391). Leave `admin_hidden_dispatch_task_keys()` in place — it returns an empty frozenset when the key is absent.
8. Search `TASK_CONFIG` for keys `craft_board_search_label` and `craft_board_search_criteria`. If either entry exists, **delete the entire task block** for that key. (As of dispatch, these keys may be absent from `TASK_CONFIG`; do not add replacements.)

⚠️ **Decision:** Do not remove generic strings like `"job board"` in comments, `boards.greenhouse.io` ATS vendor patterns, or `NEW` state comment “ingested from job board scans” — those are company/roster context, not the boards channel.

## Stage 3: Excise board wiring from core and external layers

**Done when:** No `src/` import of `src.core.boards`, no `board_search` entity dispatch path, no `process_gaze_board_batch`, no `ingest_board_listings`; company gazer paths (`extract_raw_job_listings`, `process_gazer_batch`, etc.) unchanged; all touched `.py` files pass `python3 -m py_compile`.

### `src/core/dispatcher.py`

1. In `_dispatch_entity_identifier`, delete the `entity_type == "board_search"` branch (~lines 51–52).
2. In `_run_unified`, delete the entire `if entity_type == "board_search":` claim block (~lines 222–239) including lazy imports of `claim_board_search_batch`, `BOARDS_CONFIG`.
3. In the `finally` block of `_run_unified`, delete the `elif entity_type == "board_search":` branch that calls `clear_board_search_batch` (~lines 398–400).

### `src/core/consult.py`

1. Delete the entire block (~lines 1771–1782):
   ```python
   if entity_type == "board_search":
       from src.core.gazer import process_gaze_board_batch
       ...
   ```

### `src/core/gazer.py`

1. Update module docstring: remove `process_gaze_board_batch` from in-scope list.
2. Remove `BOARD_SEARCH_STATES` from the `src.utils.config` import line.
3. Remove from `src.data.database` import: `set_board_search_state`, `update_board_search_last_scan_at`.
4. **Delete** the entire `async def process_gaze_board_batch(...)` function (~lines 849–909) and any board-only helpers used exclusively by it.

### `src/core/tracker.py`

1. Remove `BOARDS_CONFIG` from `src.utils.config` imports.
2. Delete module-level `_BOARD_LISTING_LINK_RE` if only used by board ingest (~line 40).
3. **Delete** the entire `ingest_board_listings(...)` function (~lines 119–191).

### `src/external/playwright.py`

1. Remove `from src.utils.url_merge import merge_url_query_params` (~line 21).
2. **Delete** the first `async def board_search_deeplink(...)` (~lines 265–278).
3. In `get_page` docstring, remove the sentence referencing `board_search_deeplink` (~line 321).
4. **Delete** the second `async def board_search_deeplink(...)` at file bottom (~lines 2396–2411).
5. **Do not delete** `extract_raw_job_listings` — `src/core/gazer.py` uses it for company job-list parsing (~line 780).

## Stage 4: Verification gate

**Done when:** Product grep checks pass on `src/`; compile check passes; engineer records first-removal SHA for AST-767 handoff.

1. Run compile on every file touched in stages 1–3:
   ```bash
   python3 -m py_compile src/ui/server.py src/utils/config.py \
     src/core/dispatcher.py src/core/consult.py src/core/gazer.py \
     src/core/tracker.py src/external/playwright.py
   ```
2. Run product grep (must return **zero** matches in `src/`):
   ```bash
   rg -n 'BOARD_CONFIG|BOARDS_CONFIG|board_search|gaze_board|/api/boards|src\.core\.boards|api_boards' src/
   ```
3. Run allowed residual grep (these **may** still match — do not “clean” them in this ticket):
   ```bash
   rg -n 'board' src/ | rg -v 'greenhouse|job board|clipboard|Keyboard|Dashboard|keyboard'
   ```
   Inspect hits manually; only escalate if a hit is boards-channel product code (placeholder `__board__`, `board_search_id` writes, etc.). **`board_search_id` in `database.py` is AST-766.**
4. Note the **first `code(AST-765)` commit SHA** in the **Code Complete** Linear comment for sibling **AST-767** (second sunset SHA).

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — Removes the entire boards channel across config, core, UI API, and external playwright helpers (~10 `src/` files), but leaves data layer and docs to siblings.

**Conf:** `high` — Removal is mechanical grep-driven excision with explicit keep-list for company roster (`extract_raw_job_listings`, greenhouse patterns, gazer batch paths).

**Risk:** `Medium` — A missed import or dispatch branch could break scheduler/dispatcher at runtime; wrong deletion of `extract_raw_job_listings` would break company job-list parsing.

## ASTRAL_CODE_RULES alignment

| Rule | Plan compliance |
|------|-----------------|
| §1.1 In-scope only | Only boards-channel symbols listed; no unrelated refactors |
| §2.1 Config as truth | Removes orphaned board enums/task keys from config; no inline magic sets added |
| §2.4 Batch processing | Removes board_search claim path only; company/job batch patterns untouched |
| §2.6 State machine | Does not alter `JOB_STATES` / `COMPANY_STATES` |
| §3.3 Imports | Deletes cross-layer board imports; no new violations |
| §3.5 Naming | No new public API surface |

**Conflict note:** `src/data/database.py` retains board DDL/DML until **AST-766** — acceptable transient orphan per sibling split; engineer must not edit `database.py` in this ticket.
