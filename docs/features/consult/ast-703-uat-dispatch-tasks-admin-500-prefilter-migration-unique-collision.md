# UAT: dispatch_tasks admin 500 — prefilter migration UNIQUE collision

**Linear:** [AST-703](https://linear.app/astralcareermatch/issue/AST-703/uat-dispatch-tasks-admin-500-prefilter-migration-unique-collision)  
**Parent:** [AST-700](https://linear.app/astralcareermatch/issue/AST-700/prefilter-as-batch-process)  
**Publish ref:** `origin/sub/AST-700/AST-703-uat-dispatch-task-migration-unique-collision`

Susan cannot open **Scheduled Actions** because `_ensure_dispatch_task_schema` raises `sqlite3.IntegrityError: UNIQUE constraint failed: dispatch_task.candidate_id, dispatch_task.task_key, dispatch_task.trigger_state` on databases that still have **both** legacy `prefilter` rows at `WEBSITE_FOUND` and `WEBSITE_FOUND_RETRY`. AST-702 Stage 6 runs `UPDATE` on both trigger states **before** `DELETE` of the retry row, collapsing two rows to the same triple `(candidate_id, 'prefilter', 'HOMEPAGE_READY')`. This ticket fixes migration order/idempotency only — no prefilter rubric, batch evaluate, scrape, or admin UI layout changes.

**Related plans (context only):** [AST-702 Stage 6](ast-702-batch-prefilter-evaluate-phase.md) introduced the broken sequence; [AST-535](../dispatcher/ast-535-dispatch-task-triple-unique-and-roster-to-watch-task-key-routing-bug.md) established triple-unique semantics.

---

## Root cause

In `src/data/database.py` (~5020–5027), the AST-702 block currently executes:

1. `UPDATE … SET trigger_state = 'HOMEPAGE_READY' … WHERE … IN ('WEBSITE_FOUND', 'WEBSITE_FOUND_RETRY')` — **both** rows become `(prefilter, HOMEPAGE_READY)`.
2. `DELETE … WHERE trigger_state = 'WEBSITE_FOUND_RETRY'` — no-op after step 1 (retry rows no longer match).

Legacy `_RETRY_TASK_SEED` used `("prefilter", "WEBSITE_FOUND_RETRY")` before AST-702 swapped retry to `fetch_website`. Candidates with both companion rows hit the UNIQUE violation on every admin request that calls `_ensure_dispatch_task_schema`.

**Verified repro (local):** two `prefilter` rows for one `candidate_id` at `WEBSITE_FOUND` + `WEBSITE_FOUND_RETRY`; wrong order raises `IntegrityError`; delete-retry-first then update-base succeeds.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Reorder AST-702 prefilter migration: delete retry row **before** updating base row to `HOMEPAGE_READY` | data |

**Tests (Betty — qa-child):** Engineer does **not** edit `tests/` or bible. Post **`[qa-handoff]`** if Betty's manifest omits the regression case below.

| File | Change | Layer |
|------|--------|-------|
| `tests/component/data/database/test_dispatch_tasks.py` | Add regression: both `prefilter` @ `WEBSITE_FOUND` and @ `WEBSITE_FOUND_RETRY` for same candidate → schema ensure succeeds → single row @ `HOMEPAGE_READY`, `batch_call_mode=1` | tests |

---

## Stage 1: Fix prefilter dispatch migration order

**Done when:** `_ensure_dispatch_task_schema` completes without error on a DB with both legacy `prefilter` rows; admin `GET /api/admin/dispatch_tasks` and `/task_keys` return 200; migrated DB has at most one `prefilter` row per candidate at `HOMEPAGE_READY` with `batch_call_mode=1`.

1. In `src/data/database.py`, locate the AST-702 block comment `# AST-702: prefilter batch claims HOMEPAGE_READY; retry scrape is fetch_website only.` (~5020).

2. **Replace** the two statements + single commit with this **order** (comment `# AST-703: delete retry before collapse — triple unique` on the DELETE):

   ```python
   conn.execute(
       "DELETE FROM dispatch_task "
       "WHERE task_key = 'prefilter' AND trigger_state = 'WEBSITE_FOUND_RETRY'"
   )
   conn.execute(
       "UPDATE dispatch_task SET trigger_state = 'HOMEPAGE_READY', batch_call_mode = 1 "
       "WHERE task_key = 'prefilter' AND trigger_state = 'WEBSITE_FOUND'"
   )
   conn.commit()
   ```

   Do **not** include `WEBSITE_FOUND_RETRY` in the `UPDATE` `IN (...)` clause.

3. Manual verification on epic worktree (Susan repro path):
   - Seed or use a candidate DB with **both** `prefilter` rows (`WEBSITE_FOUND` + `WEBSITE_FOUND_RETRY`).
   - Reset module flag if re-testing in one process: `database._dispatch_task_schema_ensured = False`.
   - Call `_ensure_dispatch_task_schema(conn)` or hit `GET /api/admin/dispatch_tasks` — must not 500.
   - Confirm SQL: exactly one `prefilter` row per affected candidate with `trigger_state='HOMEPAGE_READY'` and `batch_call_mode=1`; zero rows with `prefilter` + `WEBSITE_FOUND_RETRY`.

⚠️ **Decision:** Obsolete `prefilter` @ `WEBSITE_FOUND_RETRY` rows are **deleted**, not migrated — retry scrape is `fetch_website` only (AST-702). Candidates with **only** a retry row (no base) lose that row; acceptable edge — retry companion without base should not exist on real DBs. If Susan reports orphans, follow-up can `UPDATE` orphan retry → `HOMEPAGE_READY` when no base row exists (out of scope here).

---

## Stage 2: Regression test (Betty)

**Done when:** `TestAst702PrefilterDispatchMigration` (or adjacent class) includes a test that inserts **both** rows for one `candidate_id`, runs `_ensure_dispatch_task_schema`, and asserts one `HOMEPAGE_READY` row — test fails on current code, passes after Stage 1.

1. Betty adds `test_schema_migrates_prefilter_when_base_and_retry_both_exist` in `tests/component/data/database/test_dispatch_tasks.py`:
   - `save_dispatch_task(cid, "prefilter", trigger_state="WEBSITE_FOUND")`
   - `save_dispatch_task(cid, "prefilter", trigger_state="WEBSITE_FOUND_RETRY")` — may require direct SQL insert if `save_dispatch_task` rejects duplicate task_key with different trigger (use same pattern as existing AST-702 tests).
   - Reset `_dispatch_task_schema_ensured = False`; call ensure.
   - Assert count of `prefilter` rows for `cid` is `1`; assert `(HOMEPAGE_READY, 1)`.

Engineer: if Betty's manifest during **test-child** does not include this case, post **`[qa-handoff]`** on AST-703 citing this stage.

---

## Self-Assessment

### Scope — **minor**

Single migration block in `database.py` — data layer only; no config, core, or UI changes.

### Conf — **high**

Root cause confirmed by code read and local SQLite repro; fix is reorder two SQL statements already authored in AST-702.

### Risk — **Medium**

Wrong migration could drop the only `prefilter` dispatch row for edge-case candidates (retry-only legacy rows) or leave admin broken if order regresses; contained to dispatch admin schema ensure, not runtime prefilter evaluation.

---

## Plan vs ASTRAL_CODE_RULES cross-check

- **§2.1 config:** Dispatch defaults unchanged; migration aligns existing rows with AST-702 config (`HOMEPAGE_READY`, `batch_call_mode=1`).
- **§2.4 batch processing:** No claim/runner changes — `batch_call_mode=1` set on migrated row only.
- **§1.3 DRY:** No new helpers; fix is ordering of existing AST-702 statements.
- **§3.3 imports:** No import changes.

No conflicts requiring plan revision.
