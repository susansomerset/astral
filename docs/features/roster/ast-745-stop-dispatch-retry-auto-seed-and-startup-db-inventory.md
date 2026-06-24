<!-- linear-archive: AST-745 archived 2026-06-23 -->

## Linear archive (AST-745)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-745/stop-dispatch-retry-auto-seed-and-startup-db-inventory-stop-rebuilding  
**Status at archive:** Done  
**Project:** Astral Roster  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-741 — Stop rebuilding unnecessary dispatch_task data  
**Blocked by / blocks / related:** parent: AST-741

### Description

## What this implements

Remove legacy automatic `dispatch_task` row seeding on lazy schema ensure: stop `INSERT OR IGNORE` of separate `*_RETRY` companion rows and decommissioned `gaze_board` companion rows. Preserve primary-row companion claim behavior (one row on primary trigger state processes both primary and retry holding states). Produce `debug/startup_db_inventory.md` cataloging every code path that mutates `agent_task` or `dispatch_task`, tagged automatic vs operator-initiated.

## Acceptance criteria

1. Susan deletes all `*_RETRY` `dispatch_task` rows for a candidate, restarts the server, and those rows are still absent.
2. Primary dispatch rows for the same `task_key` continue to claim and process entities in the companion retry holding state (e.g. jobs in `VALID_TITLE_RETRY` still process when `qualify_job_listings` is scheduled on `VALID_TITLE`).
3. No automatic path re-inserts `gaze_board` dispatch rows on restart or schema ensure.
4. `debug/startup_db_inventory.md` lists every mutating code path for `agent_task` and `dispatch_task`, tagged automatic vs manual, with enough detail that Susan can tell which paths may recreate deleted rows.
5. No automatic writer re-inserts deleted `*_RETRY` dispatch rows on restart or lazy schema ensure.
6. Manage Dispatch and Manage Tasks still create, update, and delete rows as today.

## Boundaries

* Does not change job/company state machines or consult retry routing into holding states.
* Does not implement AST-572 retry-flag UI or Scheduled Actions filters.
* Does not remove `sync_agent_tasks` blank-row inserts for missing `TASK_CONFIG` keys.
* Does not add or extend `gaze_board` task content beyond removing its automatic seed path.
* Does not alter `dispatch_ledger` or other tables.

## Notes for planning

* Primary files: `src/data/database.py` (`_RETRY_TASK_SEED`, `_ensure_dispatch_task_schema`, `_ensure_gaze_board_dispatch_tasks`), `src/core/bootstrap.py` (`sync_agent_tasks` — document only unless inventory proves delete-then-reappear). Companion claim logic lives in config `dispatch_claim_states` — do not break.
* Inventory path: `debug/startup_db_inventory.md` (Susan-specified). Include admin API, config-table upsert, push/pull scripts, dispatcher runtime updates (`last_run_at`), and one-time migrations vs recurring seeds.
* Tests: component tests for schema ensure no longer re-inserting deleted retry rows after restart simulation.

## Git branch (authoritative)

Per **orientation** § Branch law: parent `ftr/ast-741-stop-dispatch-retry-seed`, child `sub/AST-741/AST-742-stop-dispatch-retry-seed`. Created at **dispatch-parent**. Engineers cherry-pick to `origin/<ftr-ref>` or `origin/<sub-ref>` — never Linear `gitBranchName` when it disagrees.

### Comments

#### chuckles — 2026-06-23T19:02:08.989Z
[merge-child] blocked: git pull merge on sub + AST-747/AST-751 pollution — see parent.

#### radia — 2026-06-23T19:00:45.753Z
### Review — `origin/dev...origin/sub/AST-741/AST-745-stop-dispatch-retry-seed`

**Plan fidelity:** Stage 1 removes only `_RETRY_TASK_SEED`, the retry `INSERT OR IGNORE` loop, `_ensure_gaze_board_dispatch_tasks`, and its trailing call; module header updated. One-time migrations (prefilter HOMEPAGE_READY cutover, triple-unique rebuild, gaze/`find_job_page` retargets) remain in `_ensure_dispatch_task_schema`. Stage 2 delivers `debug/startup_db_inventory.md` with required columns and **Removed AST-745** / **Not in scope** sections; `.gitignore` uses `debug/*` + `!debug/startup_db_inventory.md` (correct negation pattern). `dispatch_claim_states` / `config.py` untouched. Self-assessment **Single-Component** / **high** conf matches the diff.

**ASTRAL_CODE_RULES (touched paths):**
- **§2.1 / §2.6:** Recurring seed dict removed; companion entity claim stays on primary rows via config — covered by `TestAst745StopAutomaticDispatchRowSeeding::test_primary_row_claims_retry_entities_without_retry_dispatch_row` and regression `TestAst641UnionClaimCount`.
- **§3.3 / B2:** Data-layer-only deletion; no new cross-layer imports.
- **§1.5 / D2:** No new logging or swallowed exceptions in `database.py`.
- **Database binds:** Deletions only; remaining migration SQL unchanged (column/`?` counts consistent).

**Tests (Betty, on publish ref):** `TestAst745StopAutomaticDispatchRowSeeding` covers AC 1–3; obsolete `TestAst701FetchWebsiteRetrySeed` and `_RETRY_TASK_SEED` symbol test removed appropriately; `test_api_admin` comment updated after gaze_board seed removal.

**advisory:** `docs/test-bible/core/gazer.md` still describes `_RETRY_TASK_SEED` companion rows (pre–AST-745); not in this diff — optional Betty bible trim on parent closeout.

**fix-now:** none

**discuss:** none

#### betty — 2026-06-18T22:54:09.758Z
## QA test manifest (AST-745)

**Publish ref:** `origin/sub/AST-741/AST-745-stop-dispatch-retry-seed` @ `317f8d4`
**Tests SHA:** `cdfc64c` on `origin/tests`

**Bible shasum:** `docs/test-bible/data/database/dispatch_tasks.md` → `64162a4c53a9e2ff403cffbb4ed14f64777f7bec`

### Broken / obsolete (revised this pass)
- `TestAst701FetchWebsiteRetrySeed` — asserted auto-insert of `WEBSITE_FOUND_RETRY` row; removed with AST-745 product change
- `TestAst702PrefilterDispatchMigration::test_retry_task_seed_omits_prefilter_website_found_retry` — `_RETRY_TASK_SEED` symbol deleted

### Manifest (test-child)

1. **No retry re-seed (required):** `tests/component/data/database/test_dispatch_tasks.py::TestAst745StopAutomaticDispatchRowSeeding::test_schema_ensure_does_not_reinsert_deleted_retry_rows`

2. **No gaze_board re-seed (required):** `tests/component/data/database/test_dispatch_tasks.py::TestAst745StopAutomaticDispatchRowSeeding::test_schema_ensure_does_not_reinsert_gaze_board_rows`

3. **Companion claim intact (required):** `tests/component/data/database/test_dispatch_tasks.py::TestAst745StopAutomaticDispatchRowSeeding::test_primary_row_claims_retry_entities_without_retry_dispatch_row`

4. **Regression — union claim (required):** `tests/component/data/database/test_dispatch_tasks.py::TestAst641UnionClaimCount`

5. **Regression — one-time prefilter migrations unchanged (required):** `tests/component/data/database/test_dispatch_tasks.py::TestAst702PrefilterDispatchMigration` + `TestAst703PrefilterMigrationUniqueCollision`

6. **Inventory artifact audit (required):** `debug/startup_db_inventory.md` on publish ref lists `dispatch_task` + `agent_task` writers, automatic vs operator-initiated, and **Removed AST-745** subsection.

**Narrowed run:**

```bash
.venv/bin/python -m pytest \
  tests/component/data/database/test_dispatch_tasks.py::TestAst745StopAutomaticDispatchRowSeeding \
  tests/component/data/database/test_dispatch_tasks.py::TestAst641UnionClaimCount \
  tests/component/data/database/test_dispatch_tasks.py::TestAst702PrefilterDispatchMigration \
  tests/component/data/database/test_dispatch_tasks.py::TestAst703PrefilterMigrationUniqueCollision \
  -q
```

**Pass criterion:** items 1–5 pytest green; item 6 artifact present — not zero-arg harness / branch-lock gate.

#### hedy — 2026-06-18T22:48:26.047Z
Plan doc: [docs/features/roster/ast-745-stop-dispatch-retry-auto-seed-and-startup-db-inventory.md](https://github.com/susansomerset/astral/blob/sub/AST-741/AST-745-stop-dispatch-retry-seed/docs/features/roster/ast-745-stop-dispatch-retry-auto-seed-and-startup-db-inventory.md) @ `117c611f`

**Self-assessment**
- **Scope:** `Single-Component` — removes `_RETRY_TASK_SEED` + `_ensure_gaze_board_dispatch_tasks` recurring inserts from `_ensure_dispatch_task_schema`; adds checked-in `debug/startup_db_inventory.md`.
- **Conf:** `high` — restart re-seed is the documented `INSERT OR IGNORE` loop; companion claim stays in `dispatch_claim_states` (no config changes).
- **Risk:** `Medium` — schema-ensure runs on every admin dispatch read until ensured; one-time migrations must remain untouched (plan limits deletion to the two seed blocks only).

Two build stages: (1) delete automatic retry/gaze_board row seeding, (2) inventory doc + `.gitignore` exception for `debug/startup_db_inventory.md`. Betty owns component tests for deleted-row survival after restart simulation.

---

# Stop dispatch retry auto-seed and startup DB inventory

**Linear:** [AST-745](https://linear.app/astralcareermatch/issue/AST-745/stop-dispatch-retry-auto-seed-and-startup-db-inventory-stop-rebuilding)  
**Parent:** [AST-741](https://linear.app/astralcareermatch/issue/AST-741/stop-rebuilding-unnecessary-dispatch-task-data) (AC reference only)  
**Publish ref:** `origin/sub/AST-741/AST-745-stop-dispatch-retry-seed`

Susan deletes `dispatch_task` rows whose `trigger_state` ends in `_RETRY`; they reappear after server restart because `_ensure_dispatch_task_schema` runs on first DB access and `INSERT OR IGNORE`s companion retry rows from `_RETRY_TASK_SEED`, and `_ensure_gaze_board_dispatch_tasks` re-seeds decommissioned `gaze_board` rows. This ticket removes those **recurring automatic row inserts** while preserving **companion-state claim** on primary rows (`dispatch_claim_states` in config — one primary row still counts entities in both `VALID_TITLE` and `VALID_TITLE_RETRY`). It also delivers a checked-in inventory of every code path that mutates `agent_task` or `dispatch_task`.

**Out of scope:** job/company state machines, consult retry routing, AST-572 retry-flag UI, `sync_agent_tasks` blank-row inserts for missing `TASK_CONFIG` keys, new `gaze_board` task content, `dispatch_ledger`, admin UI redesign.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Remove `_RETRY_TASK_SEED`, retry `INSERT OR IGNORE` loop, `_ensure_gaze_board_dispatch_tasks`, and its call; update module header comments | data |
| `debug/startup_db_inventory.md` | New catalog of all `agent_task` / `dispatch_task` mutators (automatic vs operator-initiated) | docs |
| `.gitignore` | Add `!debug/startup_db_inventory.md` negation so Susan’s inventory is tracked while `debug/` stays ignored | repo |

Betty may add component tests (schema ensure no longer re-inserts deleted `*_RETRY` rows after restart simulation) in **astral-tests** — engineer does **not** edit `tests/` or `docs/test-bible/**`.

---

## Stage 1: Remove automatic retry and gaze_board dispatch row seeding

**Done when:** `_ensure_dispatch_task_schema` no longer contains `_RETRY_TASK_SEED` or `_ensure_gaze_board_dispatch_tasks`; deleted `*_RETRY` and `gaze_board` rows stay absent after process restart / schema ensure; one-time migrations (column adds, triple-unique rebuild, prefilter DELETE/UPDATE, gaze `sort_by`, `locate_job_page` → `find_job_page`, `recheck_no_openings`) remain unchanged; `dispatch_claim_states` in `src/utils/config.py` is **not** modified.

1. In `src/data/database.py`, **delete** the module-level `_RETRY_TASK_SEED` list (~5674–5678):

   ```python
   _RETRY_TASK_SEED = [
       ("qualify_job_listings", "VALID_TITLE_RETRY"),
       ("evaluate_jd",          "JD_READY_RETRY"),
       ("fetch_website",        "WEBSITE_FOUND_RETRY"),
   ]
   ```

2. **Delete** the entire `_ensure_gaze_board_dispatch_tasks(conn)` function (~5681–5727) — both `INSERT OR IGNORE` blocks (gaze-row clone and `board_search` fallback).

3. In `_ensure_dispatch_task_schema`, **delete** the block `# Add retry task rows for each candidate that has the corresponding base task` (~5905–5927): the `for base_key, retry_trigger in _RETRY_TASK_SEED:` loop and its `INSERT OR IGNORE` / `commit`.

4. In `_ensure_dispatch_task_schema`, **delete** the trailing call `_ensure_gaze_board_dispatch_tasks(conn)` (~6014) — keep `_dispatch_task_schema_ensured = True` immediately after the AST-702/703 prefilter migration `commit`.

5. Update the `database.py` file header comment block (~lines 18–22) if it still describes automatic retry companion dispatch rows — replace with: primary dispatch rows only; companion `*_RETRY` entities claimed via `dispatch_claim_states`, not separate dispatch rows.

6. **Do not touch:** `dispatch_claim_states`, `DISPATCH_SCHEDULABLE_TASK_KEYS`, `save_dispatch_task`, `update_dispatch_task`, admin API, dispatcher runners, or one-time migration SQL (including `DELETE FROM dispatch_task WHERE task_key = 'prefilter' AND trigger_state = 'WEBSITE_FOUND_RETRY'`).

7. Manual verification on epic worktree (throwaway DB — do **not** commit):

   - Open SQLite with a candidate that has a primary `qualify_job_listings` row at `VALID_TITLE` and **no** row at `VALID_TITLE_RETRY`.
   - `DELETE` any `*_RETRY` dispatch rows and any `gaze_board` rows for that candidate.
   - Set `database._dispatch_task_schema_ensured = False`, call `_ensure_dispatch_task_schema(conn)`.
   - Assert `SELECT COUNT(*) FROM dispatch_task WHERE trigger_state LIKE '%_RETRY'` is **0** and `task_key = 'gaze_board'` count is **0**.
   - Call `database.count_eligible_for_dispatch_task` on the primary `qualify_job_listings` / `VALID_TITLE` row with a job in `VALID_TITLE_RETRY` — count must include that job (companion claim intact).

⚠️ **Decision:** Remove seeding entirely rather than gating on a config flag — Susan’s deletes must survive restart with no opt-in; companion claim already lives in config, not extra rows.

---

## Stage 2: Startup DB inventory document

**Done when:** `debug/startup_db_inventory.md` exists, is committed (via `.gitignore` exception), and lists every mutating path below with columns: **Path**, **Table**, **Operation**, **Trigger**, **Automatic vs operator**, **Idempotent?**, **Can recreate deleted rows?**, **Notes**.

1. Add to `.gitignore` immediately after the `debug/` line:

   ```
   !debug/startup_db_inventory.md
   ```

2. Create `debug/startup_db_inventory.md` with an intro paragraph (purpose, how to use, last updated AST-745) and two sections: **`dispatch_task`** then **`agent_task`**. Populate from code survey — minimum rows:

   **dispatch_task — automatic (recurring):**

   | Path | Trigger | Can recreate deleted rows? |
   |------|---------|----------------------------|
   | `_ensure_dispatch_task_schema` — NULL-column backfill `UPDATE` | First connection / admin list / upsert ensure | No (updates existing rows only) |
   | `_ensure_dispatch_task_schema` — `score_floor` backfill `UPDATE` | Same | No |
   | `_ensure_dispatch_task_schema` — one-time migration `UPDATE`/`DELETE`/`CREATE TABLE` blocks | Same, once per process until `_dispatch_task_schema_ensured` | No (migrations only; retry/gaze_board **INSERT** seeds removed AST-745) |
   | `ensure_table_schema_for_upsert` → `_ensure_dispatch_task_schema` | Config table upsert / copy upsert | Indirect (schema ensure only) |

   **dispatch_task — operator-initiated:**

   | Path | Trigger | Can recreate deleted rows? |
   |------|---------|----------------------------|
   | `save_dispatch_task` | `POST /api/admin/dispatch_tasks` (Manage Dispatch create) | Yes — explicit create |
   | `update_dispatch_task` | `PUT /api/admin/dispatch_tasks/<id>` | No (updates only) |
   | `update_dispatch_task(last_run_at=…)` | Dispatcher after batch run (`src/core/dispatcher.py`) | No |
   | `apply_config_table_upsert` for `dispatch_task` | `POST /api/admin/data/upsert_config_table`, `scripts/push_tables_to_prod.py`, `scripts/upsert_tables_from_prod.py` | Yes — upserts rows present in payload |
   | Direct SQLite / external DBA | Susan manual | N/A |

   **agent_task — automatic (recurring):**

   | Path | Trigger | Can recreate deleted rows? |
   |------|---------|----------------------------|
   | `sync_agent_tasks` | `bootstrap_runtime()` on server start (`src/core/bootstrap.py`) | Yes — inserts blank `current=1` row for each `TASK_CONFIG` key missing from DB |
   | `_apply_ast738_task_grouping_metadata_seed` | Called from `sync_agent_tasks` and `_ensure_agent_task_schema` | No (metadata UPDATE on existing rows) |
   | `_ensure_agent_task_schema` — v1→versioned migration `INSERT` | First access | One-time only |

   **agent_task — operator-initiated:**

   | Path | Trigger | Can recreate deleted rows? |
   |------|---------|----------------------------|
   | `save_agent_task` / `_save_agent_task_on_connection` | `PUT /api/admin/tasks/<task_key>` (Manage Tasks) | Yes — versions row or inserts if missing |
   | `apply_agent_task_copy_upsert` | `POST /api/admin/data/table_copy_upsert` | Yes |
   | `apply_config_table_upsert` for `agent_task` | upsert_config_table / push / upsert scripts | Yes |
   | One-time scripts: `scripts/migrations/backfill_task_grouping_metadata.py`, rubric token migration helpers in `database.py` | Manual CLI | One-time UPDATE |
   | Direct SQLite / external DBA | Susan manual | N/A |

3. Add a **“Removed AST-745”** subsection noting `_RETRY_TASK_SEED` companion inserts and `_ensure_gaze_board_dispatch_tasks` no longer run.

4. Add a **“Not in scope”** note: `dispatch_ledger`, entity tables, `sync_agent_tasks` blank inserts (explicit parent boundary).

---

## Execution contract (build-child)

- Execute stages **1 → 2** in order; **one commit per stage** on epic worktree (`astral-AST-741`), then publish each to **`origin/sub/AST-741/AST-745-stop-dispatch-retry-seed`** via `git push origin HEAD:sub/AST-741/AST-745-stop-dispatch-retry-seed`.
- Do **not** edit `tests/`, `docs/ASTRAL_TEST_BIBLE.md`, or `docs/test-bible/**`.
- Do **not** modify `src/utils/config.py` except if a compile error references removed symbols (none expected).
- Blocking ambiguity → `🛑 Stage N blocked` comment on **AST-741** parent per plan-child execution contract.

---

## Self-Assessment

**Scope:** `Single-Component` — Primary change is `src/data/database.py` schema-ensure seed removal plus one inventory markdown file and a single `.gitignore` negation line.

**Conf:** `high` — Root cause is explicit `_RETRY_TASK_SEED` / `_ensure_gaze_board_dispatch_tasks` `INSERT OR IGNORE` on every schema ensure; companion claim is already implemented in `dispatch_claim_states` and must remain untouched.

**Risk:** `Medium` — Wrong deletion (e.g. removing one-time prefilter migration) could break admin dispatch on legacy DBs; mitigated by surgical removal of only the two recurring seed blocks and manual verification steps in Stage 1.

---

## Code rules self-review

| Rule | Assessment |
|------|------------|
| §2.1 config / `dispatch_tasks` | Schedulable defaults stay in `dispatch_task_admin_defaults`; no new seed dicts. |
| §2.6 state machine | Job/company states and `retry_state` routing unchanged; claim via `dispatch_claim_states` preserved. |
| §2.4 batch processing | Dispatcher `last_run_at` updates and claim paths unchanged. |
| §1.3 DRY | Deleting dead seed code; inventory doc replaces tribal knowledge. |
| §3.3 imports | No new cross-layer imports. |
| §3.6 debug output | Inventory at Susan-specified `debug/startup_db_inventory.md` with explicit gitignore exception — not under `debug/spikes/`. |

No conflicts requiring **Conf: !!-NONE**.

---

## Built (AST-745)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `88b48ed` | Remove `_RETRY_TASK_SEED`, `_ensure_gaze_board_dispatch_tasks`, and retry insert loop from `_ensure_dispatch_task_schema` |
| 2 | (this commit) | `debug/startup_db_inventory.md` + `.gitignore` exception |

**Publish ref:** `origin/sub/AST-741/AST-745-stop-dispatch-retry-seed`

**Review:** Radia clean sign-off — no fix-now; no discuss (2026-06-23).

---

## Resolution (AST-745)

**Date:** 2026-06-23  
**Review:** Radia — **fix-now:** none · **discuss:** none · **advisory:** optional Betty bible trim for `docs/test-bible/core/gazer.md` `_RETRY_TASK_SEED` prose (parent closeout; out of scope here).

**Outcome:** No product changes required. Plan fidelity confirmed against `origin/dev...origin/sub/AST-741/AST-745-stop-dispatch-retry-seed`. §9a dry-run: publish ref merges cleanly into `origin/dev` and `origin/ftr/ast-741-stop-dispatch-retry-seed`.

**Shipped commits (publish ref):**

| Stage | Commit | Summary |
|-------|--------|---------|
| plan | `117c611` | Plan doc |
| code 1 | `88b48ed` | Remove automatic retry/gaze_board dispatch row seeding |
| code 2 | `22466b4` | `debug/startup_db_inventory.md` + `.gitignore` exception |
| test | `cdfc64c` | Betty manifest — schema-ensure guards, obsolete test removal |
| merge-tests | `317f8d4` | Betty merge-tests on publish ref |

**Publish ref:** `origin/sub/AST-741/AST-745-stop-dispatch-retry-seed`
