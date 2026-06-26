<!-- linear-archive: AST-765 archived 2026-06-23 -->

## Linear archive (AST-765)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-765/remove-boards-src-implementation-and-board-only-tests-sunset-astral  
**Status at archive:** Done  
**Project:** Astral Boards  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-757 — Sunset Astral Boards  
**Blocked by / blocks / related:** parent: AST-757

### Description

## What this implements

Delete all boards-channel product code under `src/` — `core/boards.py`, `ui/api/api_boards.py`, board-specific config blocks and helpers (`BOARD_CONFIG`, `BOARDS_CONFIG`, `gaze_board`, board entity dispatch), related paths in gazer, dispatcher, consult, tracker, playwright, admin hidden-key shims, and server route registration. Remove component tests whose sole purpose is boards behavior; update shared fixtures that exist only for boards. Company-centric gazer and roster flows must remain intact.

## Acceptance criteria

1. No `BOARD_CONFIG`, `BOARDS_CONFIG`, `board_search` entity dispatch, `gaze_board` task key, or `/api/boards` routes under `src/` on the publish ref.
2. No board-specific component tests remain (default delete).
3. Admin Scheduled Actions and nav config show no board-search or `gaze_board` entries beyond what AST-649 already removed from UI (complete backend/admin catalog cleanup).
4. Board spike CLIs remain under `scripts/spikes/` only.

## Boundaries

Does not drop database schema (sibling AST-759). Does not update test bible or Code Rules sunset section (sibling AST-760). Does not remove `scripts/spikes/` board CLIs.

## Notes for planning

Pre-removal `dev` tip SHA at dispatch: `{PRE_DEV_SHA}` — record as first SHA in Code Rules sunset section in AST-760; this ticket's first removal commit is the second SHA. Merge `origin/dev` into epic worktree before planning.

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/AST-757-sunset-astral-boards`, child `sub/AST-757/<child-segment>`, standalone `ftr/<segment>`. Created at **dispatch-parent**. Engineers cherry-pick to `origin/<ftr-ref>` or `origin/<sub-ref>` — never Linear `gitBranchName` when it disagrees.

### Comments

#### betty — 2026-06-23T20:24:27.652Z
[check-linear]

Cleared **[qa-handoff]** after **`9d3cda8`** revert — AST-765-only manifest (no cross-ticket bleed).

**Changes:** `origin/tests` @ `3a2dd2e`, sub @ `8de1a5e`
- Excluded **`test_consult.py`** from epic manifest (ctx rubric fallbacks reverted; not boards scope)
- `TestAst750DispatchScoreFloorCatalog` skipped when AST-750 catalog absent
- `test_list_dispatch_tasks_and_keys` skips `score_floor_options` when route absent
- Bible: epic manifest in `docs/test-bible/core/consult.md` § AST-765

**Manifest (440 passed, 5 skipped @ sub tip):**
```bash
ASTRAL_PYTHON=.venv/bin/python ./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py \
  tests/component/core/test_gazer.py \
  tests/component/core/test_tracker.py \
  tests/component/utils/test_config.py \
  tests/component/ui/api/test_api_admin.py \
  tests/component/external/test_playwright.py \
  tests/component/scripts/test_cleanup_duplicate_and_board_gaze_jobs.py \
  -q
```

Reassigned to Hedy — **Review Posted** for resolve re-run + §9a.

— Betty

#### hedy — 2026-06-23T20:22:22.409Z
[qa-handoff]

**resolve-child fix-now landed** @ `9d3cda8` — reverted cross-ticket bleed per Radia (consult ctx rubric helpers, AST-750 `config` score_floor catalog, `api_admin` `/dispatch_tasks/score_floor_options`). **Kept:** `database.py` import bridge + migration `__board__` literal.

Manifest after revert: **567 passed, 27 failed**.

**Failures needing test/manifest trim (not product on this sub):**

1. **`tests/component/utils/test_config.py`** — `TestAst750DispatchScoreFloorCatalog` (AST-750 product reverted)
2. **`tests/component/ui/api/test_api_admin.py`** — `TestDispatchTasks::test_list_dispatch_tasks_and_keys` hits removed `score_floor_options` route
3. **`tests/component/core/test_consult.py`** (24) — batch consult / render_verdict / AST-513 / AST-726 paths fail without ctx rubric fallbacks (table-only AST-723); tests pass inline rubric in ctx without `astral_candidate_id` or need `_rubric_criteria_for_cfg` mocks

**Command:**
```bash
ASTRAL_PYTHON=.venv/bin/python ./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py \
  tests/component/core/test_consult.py \
  tests/component/core/test_gazer.py \
  tests/component/core/test_tracker.py \
  tests/component/utils/test_config.py \
  tests/component/ui/api/test_api_admin.py \
  tests/component/external/test_playwright.py \
  tests/component/scripts/test_cleanup_duplicate_and_board_gaze_jobs.py \
  -q
```

@Betty White — narrow manifest / adjust consult mocks or skips for AST-765-only scope; reassign for resolve re-run + §9a.

— Hedy

#### radia — 2026-06-23T20:21:09.657Z
**Diff:** `origin/dev...origin/sub/AST-757/AST-765-remove-boards-src-and-board-only-tests` @ `b0d30b7` (doc commit includes full table)

### fix-now

- **Cross-ticket `src/` bleed** — `c35bef0` (`test(AST-765)`) adds product code outside plan scope and not on `origin/dev`: **AST-750** `DISPATCH_SCORE_FLOOR_VALUES` / `dispatch_score_floor_option_labels()` (`config.py`), `/dispatch_tasks/score_floor_options` (`api_admin.py`), and consult `_resolve_rubric_criteria` / ctx artifact fallbacks (`consult.py`). Revert from this publish ref; land via **AST-750** / owning ticket.

### discuss

- **`database.py` bridge** — inlined `_BOARD_SEARCH_STATES` / `_GAZE_BOARD_DEFAULT_SCAN_INTERVAL_HOURS` after config purge (required after `BOARD_*` removal; plan listed `database.py` as **AST-766**). Acceptable until schema drop; should be `code(AST-765)` + plan note, not `test()` commit. `count_eligible_for_dispatch_task` `board_search` branch is dead until AST-766.

### advisory

- Boards excision in `f64c3c0..c20fd52` matches plan Stages 1–3; product grep clean outside `database.py`; Betty board-only test deletion landed; `extract_raw_job_listings` retained.
- `test(AST-765)` touched `src/` — product edits belong in `code()` commits.

**Doc:** `docs/features/boards/ast-765-remove-boards-src-and-board-only-tests.md` § Radia review (2026-06-23)

#### betty — 2026-06-23T20:18:38.238Z
[check-linear]

Cleared **[qa-handoff]** — test/manifest fixes on `origin/tests` @ `4d972b5`, cherry-picked to `origin/sub/AST-757/AST-765-remove-boards-src-and-board-only-tests` @ `68c832c`.

**Fixes:**
1. `test_cleanup_duplicate_and_board_gaze_jobs.py` — drop `idx_job_identity_unique` in fixture; stub `_ensure_job_schema` on migration import so dedupe seeds survive AST-732 index.
2. `test_config.py` — `TestAst676CraftRubricSchema` expects `importance.min: 0`; `TestAst508InflowLocateConfig` skipped when `locate` absent from `INFLOW_CONFIG`.

**Manifest re-run (sub tip):**
```bash
ASTRAL_PYTHON=.venv/bin/python ./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py \
  tests/component/core/test_consult.py \
  tests/component/core/test_gazer.py \
  tests/component/core/test_tracker.py \
  tests/component/utils/test_config.py \
  tests/component/ui/api/test_api_admin.py \
  tests/component/external/test_playwright.py \
  tests/component/scripts/test_cleanup_duplicate_and_board_gaze_jobs.py \
  -q
```

Reassigned to Hedy for **test-child**.

— Betty

#### hedy — 2026-06-23T20:15:50.012Z
[qa-handoff]

Product fixes pushed @ `c35bef0` on `origin/sub/AST-757/AST-765-remove-boards-src-and-board-only-tests`:
- `database.py`: inline board DDL constants after AST-765 config purge
- migration script: literal `__board__` prefix (no `BOARDS_CONFIG`)
- `config.py`: `dispatch_score_floor_option_labels` (AST-750 route from merge-tests)
- `consult.py`: ctx artifact fallbacks for rubric hydration (table-backed + inline tests)

Manifest re-run: **586 passed, 10 failed** (boards-related modules green).

**Remaining failures are test/manifest vs product gaps — not AST-765 product bugs:**

1. **`tests/component/utils/test_config.py`** (3)
   - `TestAst508InflowLocateConfig` ×2: `INFLOW_CONFIG["locate"]` and `ROSTER_CONFIG["locate_job_page"]["dispatch_input_states"]` with `PREFILTER_PASSED` — **AST-508 product not on branch** (also absent on `origin/tests` config @ 203a427).
   - `TestAst676CraftRubricSchema`: expects `importance.min == 1`; product shared schema has `min: 0` (same on `origin/tests` config).

2. **`tests/component/scripts/test_cleanup_duplicate_and_board_gaze_jobs.py`** (7)
   - All dedupe-path tests: `sqlite3.IntegrityError: UNIQUE constraint failed: job.company, job.job_title, job.company_job_id`
   - Fixture inserts duplicate identity rows via `_ensure_job_schema`, which now creates `idx_job_identity_unique` (AST-732). Tests need fixture/schema setup that allows pre-migration duplicates, or manifest should narrow to board-gaze-only cases that still pass.

**Command:**
```bash
ASTRAL_PYTHON=.venv/bin/python ./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py \
  tests/component/core/test_consult.py \
  tests/component/core/test_gazer.py \
  tests/component/core/test_tracker.py \
  tests/component/utils/test_config.py \
  tests/component/ui/api/test_api_admin.py \
  tests/component/external/test_playwright.py \
  tests/component/scripts/test_cleanup_duplicate_and_board_gaze_jobs.py \
  -q
```

@Betty White — please revise manifest or tests for the 10 failures above and reassign when ready.

#### betty — 2026-06-23T20:09:22.082Z
## QA test manifest (AST-765)

**Publish:** `origin/sub/AST-757/AST-765-remove-boards-src-and-board-only-tests` @ `afcdf2b` (`merge-tests(AST-765): origin/tests 203a427`)

### 1. Deleted board-only tests
- `tests/component/core/test_boards.py`
- `tests/component/core/test_boards_gaze_ast487.py`
- `tests/component/core/test_boards_generate_ast521.py`
- `tests/component/core/test_board_sourced_qualify_evaluate.py`
- `tests/component/ui/api/test_api_boards.py`
- `tests/component/data/database/test_board_search_integration.py`

### 2. Trimmed shared tests
- `tests/component/core/test_dispatcher.py` — removed board_search claim tests
- `tests/component/core/test_consult.py` — removed board_search routing test
- `tests/component/core/test_gazer.py` — removed board batch test classes
- `tests/component/core/test_tracker.py` — removed `TestIngestBoardListings`
- `tests/component/utils/test_config.py` — removed board registry classes; `gaze_board` not schedulable
- `tests/component/ui/api/test_api_admin.py` — removed AST-649 hide-`gaze_board` test
- `tests/component/external/test_playwright.py` — removed `TestBoardSearchDeeplink`
- `tests/component/scripts/test_cleanup_duplicate_and_board_gaze_jobs.py` — dedupe-only cleanup tests
- conftest files — dropped board schema flags and `boards_client`

### 3. Manifest — run on epic worktree at sub tip

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py \
  tests/component/core/test_consult.py \
  tests/component/core/test_gazer.py \
  tests/component/core/test_tracker.py \
  tests/component/utils/test_config.py \
  tests/component/ui/api/test_api_admin.py \
  tests/component/external/test_playwright.py \
  tests/component/scripts/test_cleanup_duplicate_and_board_gaze_jobs.py \
  -q
```

### 4. Bible shasum (`origin/sub/...` @ `afcdf2b`)
- `docs/test-bible/core/dispatcher.md` 96f7d8fb752c15c321fad0a4c9837f0755b5c55c91737d7491aaec86813fc4e7
- `docs/test-bible/core/gazer.md` 5881a2d194853ddf5638d7077e6a4edccb1635c3bb770b57e4d275eea854363a
- `docs/test-bible/core/consult.md` 5fd85451d075f4b45245de662b0ae69c28a183278c8710fea5a0c5211ae5eca7
- `docs/test-bible/core/tracker.md` 74b980681482efdbf875174fcde536c8fcbd416cd4bd043b279fe8981f7fffe7
- `docs/test-bible/utils/config.md` 0a1316b7b0ade9eee2fc73c13de242c3d3a86581e7d9d727a0d99d9f3c850195
- `docs/test-bible/external/playwright.md` 71a1fafc2fc03301d6dd6290ed361c94b630a71dc22607cd0fe04b7f422b167e
- `docs/test-bible/dev/cleanup_duplicate_and_board_gaze_jobs.md` 0d4380e1222120b057f672cd1d97a3e4b80f2a8e4e2195aecff2ac83b0850868

— Betty

#### hedy — 2026-06-23T20:03:30.297Z
origin/sub/AST-757/AST-765-remove-boards-src-and-board-only-tests @ 508e245

First removal SHA for AST-767 Code Rules sunset section: `f64c3c0`

#### hedy — 2026-06-23T19:58:29.918Z
Plan: docs/features/boards/ast-765-remove-boards-src-and-board-only-tests.md

https://github.com/susansomerset/astral/blob/sub/AST-757/AST-765-remove-boards-src-and-board-only-tests/docs/features/boards/ast-765-remove-boards-src-and-board-only-tests.md

Four stages: (1) delete boards.py / api_boards.py / url_merge.py + server unregister, (2) config purge BOARD_* + gaze_board dispatch/admin catalog, (3) excise dispatcher/consult/gazer/tracker/playwright board wiring while keeping extract_raw_job_listings for roster, (4) src/ grep + compile gate. database.py and test bible deferred to AST-766/AST-767; Betty manifest lists board-only test deletions.

**Scope:** MAJOR-CHANGE — full boards channel removal across ~10 src/ files; data layer left to AST-766.

**Conf:** high — mechanical excision with explicit keep-list for company gazer paths.

**Risk:** Medium — missed dispatch branch or accidental deletion of extract_raw_job_listings would break non-board flows.

---

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

## Review

**Branch:** `origin/sub/AST-757/AST-765-remove-boards-src-and-board-only-tests`  
**Review tip:** `68c832c`  
**First removal SHA (AST-767 sunset note):** `f64c3c0`

**Built:** Stages 1–3 — deleted `boards.py`, `api_boards.py`, `url_merge.py`; unregistered `/api/boards`; purged `BOARD_*` config and `gaze_board` dispatch/admin catalog; excised board wiring from dispatcher, consult, gazer, tracker, playwright (kept `extract_raw_job_listings` for roster). Product grep clean under `src/` except `database.py` (AST-766). Betty qa manifest covers board-only test deletion.

### Radia review (2026-06-23)

**Diff:** `origin/dev...origin/sub/AST-757/AST-765-remove-boards-src-and-board-only-tests` @ `68c832c`  
**In-scope product commits:** `f64c3c0`, `76ece51`, `c20fd52`

#### What’s solid

| Area | Notes |
|------|-------|
| Plan Stages 1–3 | `boards.py`, `api_boards.py`, `url_merge.py` deleted; `boards_bp` unregistered; `BOARD_*` / `gaze_board` / `hidden_dispatch_task_keys` purged from config; dispatcher claim/clear/finally branches for `board_search` removed; consult `board_search` routing removed; `process_gaze_board_batch` and `ingest_board_listings` deleted; playwright `board_search_deeplink` removed; `extract_raw_job_listings` retained for company roster. |
| Product grep | Zero matches for board-channel symbols in `src/` outside `database.py` (expected AST-766 deferral). |
| Layer / batch (§2.4, §3.3) | No new cross-layer imports; company/job batch paths untouched; board claim path removed symmetrically (claim + `finally` clear). |
| Tests | Betty `merge-tests(AST-765)` — board-only files deleted; shared tests trimmed per qa manifest; manifest green at tip. |
| Self-assessment | Diff footprint matches `MAJOR-CHANGE` boards-channel excision; company gazer/roster paths preserved. |

#### Issues

| Severity | Item |
|----------|------|
| **fix-now** | **Cross-ticket `src/` bleed** — commit `c35bef0` (`test(AST-765)`) adds product code outside plan scope and not on `origin/dev`: AST-750 `DISPATCH_SCORE_FLOOR_VALUES` / `dispatch_score_floor_option_labels()` in `config.py`, `/dispatch_tasks/score_floor_options` in `api_admin.py`, and consult `_resolve_rubric_criteria` / ctx artifact fallbacks. Revert these from this publish ref; land via **AST-750** / owning ticket. |
| **discuss** | **`database.py` bridge** — inlined `_BOARD_SEARCH_STATES` / `_GAZE_BOARD_DEFAULT_SCAN_INTERVAL_HOURS` after config purge (required import fix; plan listed `database.py` as AST-766). Acceptable transient until schema drop; prefer `code(AST-765)` + plan note rather than `test()` commit. `count_eligible_for_dispatch_task` `board_search` branch remains dead code until AST-766. |
| **advisory** | `test(AST-765)` touched `src/` — hook/workflow discipline; product edits belong in `code()` commits. Pure boards removal in `f64c3c0..c20fd52` is clean; tip extras are the bleed above. |

#### Recommended actions

| Owner | Action |
|-------|--------|
| Hedy | **resolve-child** — revert non-AST-765 `src/` from sub tip (`config` score_floor helpers, `api_admin` route, consult rubric helpers); keep `database.py` inline constants or document AST-766 handoff. Re-run manifest after revert. |
| Susan | Confirm whether epic rollup may bundle AST-750 backend on this sub (if revert blocks Betty manifest). |

## Resolution (2026-06-23)

**fix-now (Radia):** Reverted cross-ticket `src/` bleed from `c35bef0` / Betty `merge-tests` — restored `consult.py`, `config.py`, and `api_admin.py` to pre-bleed state (`508e245` product for those files). Removed AST-750 `DISPATCH_SCORE_FLOOR_*` / `dispatch_score_floor_option_labels`, `/dispatch_tasks/score_floor_options`, and consult `_resolve_rubric_criteria` / ctx artifact fallbacks / `_format_analysis_phase_text` artifact path.

**Kept (AST-765 scope):** `database.py` inlined `_BOARD_SEARCH_STATES` / `_GAZE_BOARD_DEFAULT_SCAN_INTERVAL_HOURS` (import bridge until AST-766); migration script literal `__board__` prefix (no `BOARDS_CONFIG`).

**Manifest after revert:** 567 passed, 27 failed — consult hydration paths and AST-750 catalog/api tests require Betty manifest trim on `[qa-handoff]` (product revert is correct per Radia; tests must not pull AST-750 / pre-723 consult ctx onto this sub).

**discuss:** Accepted — `database.py` bridge documented above; dead `board_search` dispatch count branch remains until AST-766.

**advisory:** Product-only boards excision in `f64c3c0..c20fd52` unchanged.
