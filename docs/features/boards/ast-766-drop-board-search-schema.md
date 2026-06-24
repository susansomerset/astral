<!-- linear-archive: AST-766 archived 2026-06-23 -->

## Linear archive (AST-766)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-766/drop-board-search-schema-and-board-only-db-surface-sunset-astral  
**Status at archive:** Done  
**Project:** Astral Boards  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-757 — Sunset Astral Boards  
**Blocked by / blocks / related:** parent: AST-757

### Description

## What this implements

Remove `board_search` table and job/company columns or sentinel values used only for board-sourced ingest from the data layer and schema ensure/migration paths. No runtime code may read or write board-search rows after this ships. No production data purge — schema/code removal only.

## Acceptance criteria

1. Database schema on a fresh migrate/ensure reflects removal of board-only tables/columns.
2. No application layer imports board-search DDL helpers after sibling AST-758 lands.
3. Grep-equivalent: no `board_search` table usage in active code paths on publish ref.

## Boundaries

Does not remove src/ boards modules (AST-758 — must be Review Posted first). Does not update test bible or Code Rules (AST-760).

## Notes for planning

Blocked until AST-758 removes all src references to board_search. Data layer changes only.

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/AST-757-sunset-astral-boards`, child `sub/AST-757/<child-segment>`, standalone `ftr/<segment>`. Created at **dispatch-parent**. Engineers cherry-pick to `origin/<ftr-ref>` or `origin/<sub-ref>` — never Linear `gitBranchName` when it disagrees.

### Comments

#### radia — 2026-06-23T20:37:37.262Z
**Diff:** `origin/dev...origin/sub/AST-757/AST-766-drop-board-search-schema` @ `7e9bd1e` (doc commit adds full table)

### advisory

- Three-dot diff vs `origin/dev` includes **AST-765** boards `src/` removal (expected epic stacking). AST-766 product commit `0a1efd3` is `database.py` only and matches plan Stages 1–5.
- `fix(AST-766)` reverted merge-tests cross-ticket bleed — good branch hygiene.

### clean

- `_apply_board_schema_sunset`: drops board tables, rebuilds `job` without `board_search_id` (explicit cols + identity index recreation).
- Board DDL/DML block, bridge constants, `save_job` param, upsert registry keys, `count_eligible` `board_search` branch, and `gaze_board` migration removed.
- Product grep clean outside sunset strings in `database.py`.
- Betty board-only test deletion + dispatch_tasks bible updates landed; manifest green.

**Doc:** `docs/features/boards/ast-766-drop-board-search-schema.md` § Radia review (2026-06-23)

#### betty — 2026-06-23T20:35:44.340Z
## QA test manifest (AST-766)

**Publish ref:** `origin/sub/AST-757/AST-766-drop-board-search-schema` @ `7e9bd1e` (`merge-tests(AST-766): origin/tests 0effd2c`; bleed revert `7e9bd1e`)

**tests commit:** `0effd2c` on `origin/tests`

1. **New:** `TestAst766BoardSchemaSunset` — fresh DB no board tables/column; legacy sunset migration; board DDL helpers removed; `count_eligible_for_dispatch_task` raises for `entity_type=board_search`.
2. **Retired:** `test_board_ingest.py`; `board_search_integration.md`; `TestAst745StopAutomaticDispatchRowSeeding::test_schema_ensure_does_not_reinsert_gaze_board_rows`; conftest board_search schema flags.

**Narrowed run (test-child):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_dispatch_tasks.py::TestAst766BoardSchemaSunset \
  -q
```

**Bible shasums on publish ref:**
- `docs/test-bible/data/database.md` → `4f69f8be269c089a8e0d91c0ea482d872d57fc3c7eb6d5cd6c94ad95edfb3379`
- `docs/test-bible/data/database/dispatch_tasks.md` → `a6f468c58a0acd3cc08f6302b3fe3b4cdc67622c959fc9b1baf3bb69807402d4`

Note: `merge-tests` briefly pulled AST-750 config/admin bible bleed from `tests` ftr merge; reverted on sub before push so delivery is tests+bible only.

— Betty

#### ada — 2026-06-23T20:31:39.145Z
origin/sub/AST-757/AST-766-drop-board-search-schema @ 0a1efd3

Betty: delete/update board-only tests (`test_board_ingest.py`, `test_board_search_integration.py`, conftest `_board_search_schema_ensured` resets).

#### ada — 2026-06-23T20:29:40.271Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-757/AST-766-drop-board-search-schema/docs/features/boards/ast-766-drop-board-search-schema.md

**Scope:** Single-Component — `src/data/database.py` only: drop `board_search`/`board_search_run`, rebuild `job` without `board_search_id`, delete all board DDL/DML helpers and the dead `count_eligible_for_dispatch_task` `board_search` branch.

**Conf:** high — AST-765 left a documented orphan inventory; no remaining `src/` importers outside `database.py`.

**Risk:** Medium — job table rebuild on legacy DBs must preserve columns/indexes; Betty owns test manifest updates after `code()`.

#### ada — 2026-06-23T20:29:37.433Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-757/AST-766-drop-board-search-schema/docs/features/boards/ast-766-drop-board-search-schema.md

**Scope:** Single-Component — `src/data/database.py` only: drop `board_search`/`board_search_run`, rebuild `job` without `board_search_id`, delete all board DDL/DML helpers and the dead `count_eligible_for_dispatch_task` `board_search` branch.

**Conf:** high — AST-765 left a documented orphan inventory; no remaining `src/` importers outside `database.py`.

**Risk:** Medium — job table rebuild on legacy DBs must preserve columns/indexes; Betty owns test manifest updates after `code()`.

---

# Drop board_search schema and board-only DB surface (Sunset Astral Boards)

**Parent:** [AST-757](https://linear.app/astralcareermatch/issue/AST-757/sunset-astral-boards)  
**Publish ref:** `sub/AST-757/AST-766-drop-board-search-schema`

**Summary:** Complete the AST-757 data-layer sunset after sibling **AST-765** removed all non-`database.py` boards product code. Delete `board_search` / `board_search_run` tables, drop the job `board_search_id` column, and remove every board-only DDL/DML helper and dead dispatch-eligibility branch from `src/data/database.py`. Schema/code removal only — no production row purge (parent AC).

**Prerequisite (satisfied on ftr @ `b47c001`):** `rg` on `src/` outside `database.py` finds no `board_search`, `claim_board_search_batch`, `gaze_board`, or `/api/boards` references. AST-765 left inlined `_BOARD_SEARCH_STATES` / `_GAZE_BOARD_DEFAULT_SCAN_INTERVAL_HOURS` and the full board DDL block as intentional orphans — this ticket removes them.

**Not in engineer commits:** `tests/**`, `docs/test-bible/**`, `docs/ASTRAL_TEST_BIBLE.md`, `docs/ASTRAL_CODE_RULES.md`, `docs/features/boards/` archive framing (**AST-767**), `scripts/**`.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Drop board tables/columns; delete board DDL/DML; update header inventory; remove dead `count_eligible_for_dispatch_task` branch | data |

---

## Stage 1: Idempotent sunset migration (drop tables + job column)

**Done when:** On a DB that previously had board schema, `_apply_board_schema_sunset(conn)` drops `board_search_run` and `board_search`, rebuilds `job` without `board_search_id`, and sets a process flag so the migration runs once per connection lifecycle; on a fresh DB the helper is a no-op; `PRAGMA table_info(job)` never lists `board_search_id`; `sqlite_master` has no `board_search` / `board_search_run` tables after ensure.

1. Near the module globals (~lines 169–170), **delete** `_board_search_schema_ensured` and `_board_search_run_schema_ensured`. Add `_board_schema_sunset_applied = False`.

2. Implement **`_apply_board_schema_sunset(conn: sqlite3.Connection) -> None`** immediately before the deleted `# ---- board_search ----` section (or where that section was — see Stage 2). Logic:
   - If `_board_schema_sunset_applied` is True, return.
   - `conn.execute("DROP TABLE IF EXISTS board_search_run")` then `conn.execute("DROP TABLE IF EXISTS board_search")`.
   - Read job columns via `PRAGMA table_info(job)`. If table missing, set flag and return (fresh DB — `_ensure_job_schema` creates job without `board_search_id` per Stage 3).
   - If `"board_search_id"` **not** in column set, set flag and return.
   - Otherwise rebuild `job` without `board_search_id`, preserving all other columns present on disk. Copy columns explicitly (do not `SELECT *` — avoids reintroducing dropped column):

   ```text
   astral_job_id, company, company_job_id, job_title, job_link, job_data,
   state, state_history, batch_id, batch_created_at, created_at, updated_at,
   state_changed_at, agent_responses, latest_score
   ```

   Use the existing rebuild pattern from `_finalize_board_search_state_schema` / `dispatch_task_new`:
   - `CREATE TABLE job_next (...)` — same types as current `job` minus `board_search_id`.
   - `INSERT INTO job_next (<cols>) SELECT <cols> FROM job` — only include source columns that exist in PRAGMA (use conditional list if `agent_responses` / `latest_score` may be absent on very old DBs).
   - `DROP TABLE job`; `ALTER TABLE job_next RENAME TO job`.
   - Recreate **`idx_job_identity_unique`** (`_JOB_IDENTITY_UNIQUE_INDEX`) if it existed before rebuild (same partial unique index SQL already in `_ensure_job_schema`).
   - `conn.commit()`; set `_board_schema_sunset_applied = True`.

   ⚠️ **Decision:** One-time drop inside schema ensure (not a separate operator CLI). Parent AC forbids data purge scripts; orphaned board rows disappear with table drop, which is acceptable for sunset. Job rows keep all non-board columns.

3. At the **start** of `_ensure_job_schema` (after the `_job_schema_ensured` early return guard, before `CREATE TABLE IF NOT EXISTS job`), call **`_apply_board_schema_sunset(conn)`** when `_job_schema_ensured` is False. Reset `_job_schema_ensured = False` before rebuild if sunset mutates schema (or call sunset before setting `_job_schema_ensured` True at end).

---

## Stage 2: Delete board_search / board_search_run DDL block and bridge constants

**Done when:** Lines ~2654–3194 (`# ---- board_search ----` through `record_board_search_run`) are gone; module-level `_BOARD_SEARCH_STATES` and `_GAZE_BOARD_DEFAULT_SCAN_INTERVAL_HOURS` (~lines 100–101) are gone; `board_listing_is_duplicate` is gone; header inventory bullets for `board_search` and `board_search_run` (~lines 23–26) are removed.

1. In the module header **Tables used (inventory)**, delete the two bullets documenting `board_search` and `board_search_run`.

2. **Delete** module constants `_BOARD_SEARCH_STATES` and `_GAZE_BOARD_DEFAULT_SCAN_INTERVAL_HOURS` (AST-765 bridge — no remaining callers outside this file after Stage 4).

3. **Delete** the entire section from `# ---- board_search ----` through the end of **`record_board_search_run`** (inclusive), including:
   - `_finalize_board_search_state_schema`, `_BOARD_SEARCH_PATCH_OMIT`
   - `_ensure_board_search_table`, `_parse_board_search_row`
   - `save_board_search_row`, `get_board_search_row`, `list_board_search_rows`, `update_board_search_row`, `update_board_search_last_scan_at`
   - `claim_board_search_batch`, `clear_board_search_batch`, `set_board_search_state`, `delete_board_search_row`
   - **`board_listing_is_duplicate`** (dead after AST-765 removed ingest; only definition left in repo)
   - `_ensure_board_search_run_table`, `record_board_search_run`

4. Leave **`# ---- company_search_terms (AST-524) ----`** and everything below it unchanged except Stage 3–4 edits.

---

## Stage 3: Job schema and `save_job` — remove `board_search_id`

**Done when:** Fresh `_ensure_job_schema` never adds `board_search_id`; `save_job` has no `board_search_id` parameter; INSERT/UPDATE SQL omits the column; `python3 -m py_compile src/data/database.py` passes.

1. In `_ensure_job_schema`, remove `("board_search_id", "TEXT")` from the migration `for col, col_def in [...]` list (~line 1204).

2. In **`save_job`**, remove keyword parameter `board_search_id: Optional[str] = None`.

3. In the INSERT branch, remove `board_search_id` from column list and VALUES — adjust placeholder count:
   - Columns end at `state_changed_at` before timestamps (match existing column order minus `board_search_id`).
   - Remove `board_search_id` from the values tuple.

4. In the UPDATE branch field loop, remove the `("board_search_id", board_search_id)` tuple from the `for col, val in [...]` list.

5. Grep `database.py` for remaining `board_search_id` — expect **zero** matches after this stage.

---

## Stage 4: Registry and dispatch-eligibility cleanup

**Done when:** `_UPSERT_*` registries have no board entries; `count_eligible_for_dispatch_task` has no `board_search` branch; legacy `gaze_board` dispatch_task sort migration removed; docstring on `count_eligible_for_dispatch_task` no longer mentions board_search.

1. In **`_UPSERT_SCHEMA_ENSURE_FLAGS`**, delete keys `"board_search"` and `"board_search_run"`.

2. In **`_UPSERT_LAZY_SCHEMA_HANDLERS`**, delete keys `"board_search"` and `"board_search_run"`.

3. In **`count_eligible_for_dispatch_task`**:
   - Update the docstring — remove the sentence about `board_search` / `gaze_board` / `_GAZE_BOARD_DEFAULT_SCAN_INTERVAL_HOURS`.
   - **Delete** the entire `if entity_type == "board_search":` block (~lines 6270–6293 including nested `_with_conn_bs`).

4. In **`_ensure_dispatch_task_schema`**, **delete** the legacy migration block (~lines 5855–5858):

   ```python
   conn.execute(
       "UPDATE dispatch_task SET sort_by = 'last_scan_at' WHERE task_key = 'gaze_board' AND sort_by = 'updated_at'"
   )
   conn.commit()
   ```

   Keep the adjacent `gaze` (company WATCH) migration unchanged.

---

## Stage 5: Verification

**Done when:** Product grep clean; compile passes; no board symbols left in `database.py` except this plan's historical mentions.

1. Run:

   ```bash
   rg -n 'board_search|board_search_run|board_search_id|_BOARD_SEARCH|_GAZE_BOARD|claim_board_search|clear_board_search|board_listing_is_duplicate|gaze_board' src/
   ```

   Expect **zero** matches on publish ref after `code(AST-766)`.

2. Run `python3 -m py_compile src/data/database.py`.

3. Post **Code Complete** Linear comment noting Betty must update/delete board-only tests (`tests/component/data/test_board_ingest.py`, `tests/component/data/database/test_board_search_integration.py` if still present, shared conftest `_board_search_schema_ensured` resets) — engineer does **not** edit `tests/` (hook + AST-767 split).

---

## Self-Assessment

**Scope:** `Single-Component` — All work is confined to `src/data/database.py` schema ensure, one migration helper, and `save_job` signature/SQL; no core, UI, or config layers.

**Conf:** `high` — AST-765 documented the exact orphan inventory; table-rebuild and DROP patterns already exist in this module; no remaining `src/` importers of board DDL helpers.

**Risk:** `Medium` — Incorrect `job` table rebuild could drop columns or indexes on legacy DBs; mitigated by explicit column list, index recreation, and Betty's component suite after `merge-tests()`.

---

## ASTRAL_CODE_RULES review

| Rule | Assessment |
|------|------------|
| §1.3 inventory | Header bullets removed; no new tables |
| §2.1 config | No config edits; removes inlined constants that duplicated deleted config |
| §2.4 batch | Removes dead `board_search` claim/count paths only |
| §2.6 state machine | No workflow state changes outside dropped tables |
| §3.3 imports | No new cross-layer imports |
| §3.5 naming | Sunset helper follows `_ensure_*` / `_apply_*` module conventions |

No conflicts requiring escalation.

---

## Review (build-child stub)

**Branch:** `origin/sub/AST-757/AST-766-drop-board-search-schema`  
**Built:** Stages 1–5 — `_apply_board_schema_sunset` drops board tables and rebuilds `job` without `board_search_id`; deleted board DDL/DML block and bridge constants; cleaned `save_job`, upsert registries, `count_eligible_for_dispatch_task`, and legacy `gaze_board` migration. Product grep clean under `src/` outside sunset DROP strings in `database.py`.

**Betty handoff:** Delete/update board-only tests (`test_board_ingest.py`, `test_board_search_integration.py`, conftest `_board_search_schema_ensured` resets).

### Radia review (2026-06-23)

**Diff:** `origin/dev...origin/sub/AST-757/AST-766-drop-board-search-schema` @ `7e9bd1e`  
**Product commit reviewed:** `0a1efd3` (`src/data/database.py` only)

#### What’s solid

| Area | Notes |
|------|-------|
| Plan Stages 1–5 | `_apply_board_schema_sunset` drops `board_search_run` / `board_search`, rebuilds `job` without `board_search_id` with explicit column list + `idx_job_identity_unique` recreation; bridge constants and full board DDL/DML block deleted; `save_job` omits `board_search_id`; upsert registries cleaned; `count_eligible_for_dispatch_task` `board_search` branch removed; legacy `gaze_board` sort migration removed. |
| Product grep | Only sunset DROP / `board_search_id` strings remain in `database.py` (expected). |
| §2.4 / §3.3 | Dead claim/count paths removed; no new cross-layer imports; `BOARD_SEARCH_STATES` / `BOARDS_CONFIG` imports dropped. |
| Tests | Betty `merge-tests(AST-766)` — `test_board_ingest.py` and `test_board_search_integration.py` deleted; `test_dispatch_tasks.py` updated; bible trimmed. `fix(AST-766)` reverted merge-tests cross-ticket `src/` bleed. |
| Self-assessment | Single-component data-layer scope matches diff; AST-765 prerequisite satisfied on branch. |

#### Issues

| Severity | Item |
|----------|------|
| **advisory** | Three-dot diff vs `origin/dev` also carries **AST-765** boards `src/` removal (expected epic stacking on shared publish ancestry). AST-766-specific product surface is `0a1efd3` only. |

#### Recommended actions

| Owner | Action |
|-------|--------|
| Ada | **resolve-child** — no code changes required. |

---

## Resolution (2026-06-23)

**Review:** Radia clean — no fix-now, discuss, or product changes.

**§9a:** `origin/sub/AST-757/AST-766-drop-board-search-schema` merges cleanly into `origin/dev` and `origin/ftr/AST-757-sunset-astral-boards`.

**Shipped @ resolve:** `7566300` (Radia review doc) — product unchanged from `0a1efd3`; tests @ `7e9bd1e`.
