# UAT: dispatch_tasks admin 500 — prefilter migration UNIQUE collision

**Linear:** [AST-703](https://linear.app/astralcareermatch/issue/AST-703/uat-dispatch-tasks-admin-500-prefilter-migration-unique-collision)  
**Parent:** [AST-700](https://linear.app/astralcareermatch/issue/AST-700/prefilter-as-batch-process) (AC reference only — fetch_website + batch prefilter dispatch rows)  
**Publish ref:** `origin/sub/AST-700/AST-703-uat-dispatch-task-migration-unique-collision`

Susan UAT: **Scheduled Actions** returns **HTTP 500** on `GET /api/admin/dispatch_tasks` and `/task_keys`. Server log: `sqlite3.IntegrityError: UNIQUE constraint failed: dispatch_task.candidate_id, dispatch_task.task_key, dispatch_task.trigger_state` inside `_ensure_dispatch_task_schema`. Legacy candidates that had **both** `prefilter`/`WEBSITE_FOUND` and `prefilter`/`WEBSITE_FOUND_RETRY` dispatch rows (pre–AST-702 `_RETRY_TASK_SEED`) hit a bad migration order from **AST-702 Stage 6**. This UAT bug fixes migration **idempotency/order only** — no rubric, scrape, batch evaluate, or UI layout changes.

**Root cause (current code on `origin/ftr/AST-700-prefilter-as-batch-process`):**

AST-702 Stage 6 appended to `_ensure_dispatch_task_schema` (~5020–5027 in `src/data/database.py`):

1. `UPDATE dispatch_task SET trigger_state = 'HOMEPAGE_READY', batch_call_mode = 1 WHERE task_key = 'prefilter' AND trigger_state IN ('WEBSITE_FOUND', 'WEBSITE_FOUND_RETRY')`
2. `DELETE FROM dispatch_task WHERE task_key = 'prefilter' AND trigger_state = 'WEBSITE_FOUND_RETRY'`

When **both** companion rows exist for one `candidate_id`, step 1 tries to set **two** rows to the same triple `(candidate_id, 'prefilter', 'HOMEPAGE_READY')`, violating **`UNIQUE(candidate_id, task_key, trigger_state)`** (AST-535) **before** step 2 runs. `_ensure_dispatch_task_schema` is invoked on the first admin dispatch-task request; the uncaught `IntegrityError` surfaces as **500** on Scheduled Actions.

**Out of scope:** prefilter rubric/decode, `fetch_website` scrape logic, batch prefilter runner, admin UI components, re-opening AST-701/702 feature work beyond this migration block.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Re-order and narrow AST-702 prefilter dispatch migration in `_ensure_dispatch_task_schema` | data |

Betty may add a collision regression row to `TestAst702PrefilterDispatchMigration` in **astral-tests** — engineer does **not** edit `tests/` or the bible.

---

## Stage 1: Fix prefilter dispatch migration order

**Done when:** `_ensure_dispatch_task_schema` completes without `IntegrityError` when a candidate has legacy `prefilter` rows at both `WEBSITE_FOUND` and `WEBSITE_FOUND_RETRY`; exactly one `prefilter`/`HOMEPAGE_READY` row remains with `batch_call_mode=1`; existing `TestAst702PrefilterDispatchMigration` cases still pass after Betty merges tests.

1. In `src/data/database.py`, block `# AST-702: prefilter batch claims HOMEPAGE_READY; retry scrape is fetch_website only.` (~5020–5027), **replace** the two statements with this order and narrower `UPDATE`:

   ```python
   # AST-702 / AST-703: drop obsolete prefilter retry companions before retargeting base row.
   conn.execute(
       "DELETE FROM dispatch_task WHERE task_key = 'prefilter' AND trigger_state = 'WEBSITE_FOUND_RETRY'"
   )
   conn.execute(
       "UPDATE dispatch_task SET trigger_state = 'HOMEPAGE_READY', batch_call_mode = 1 "
       "WHERE task_key = 'prefilter' AND trigger_state = 'WEBSITE_FOUND'"
   )
   conn.commit()
   ```

   ⚠️ **Decision:** **DELETE first**, then **UPDATE only `WEBSITE_FOUND`** — not `IN ('WEBSITE_FOUND', 'WEBSITE_FOUND_RETRY')`. Retry companions are obsolete after cutover (`fetch_website` owns `WEBSITE_FOUND_RETRY` per AST-702); base row carries batch prefilter on `HOMEPAGE_READY`.

2. Manual verification on epic worktree (throwaway SQLite file — do **not** commit):

   - Create minimal `dispatch_task` table with triple unique (copy column list from `_ensure_dispatch_task_schema` greenfield `CREATE TABLE`).
   - `INSERT` two rows for one `candidate_id`: `prefilter`/`WEBSITE_FOUND` and `prefilter`/`WEBSITE_FOUND_RETRY` (mirror legacy `_RETRY_TASK_SEED` layout).
   - Set `database._dispatch_task_schema_ensured = False`, call `_ensure_dispatch_task_schema(conn)` on that connection.
   - Assert no exception; `SELECT COUNT(*)` for `task_key='prefilter'` is **1**; row has `trigger_state='HOMEPAGE_READY'` and `batch_call_mode=1`.

3. Manual verification (admin path): with a candidate DB that previously reproduced the 500, start app and `GET /api/admin/dispatch_tasks` — **200** with rows including `fetch_website` and migrated `prefilter` → `HOMEPAGE_READY`.

---

## Execution contract

- Execute Stage 1 only; **one `code(AST-703)` commit** on epic worktree, then publish to **`origin/sub/AST-700/AST-703-uat-dispatch-task-migration-unique-collision`** via `git push origin HEAD:sub/AST-700/AST-703-uat-dispatch-task-migration-unique-collision`.
- Do **not** edit `tests/`, `docs/ASTRAL_TEST_BIBLE.md`, or `docs/test-bible/**`.
- Blocking ambiguity → 🛑 comment on **AST-700** per plan-child execution contract.

---

## Self-Assessment

**Scope:** `minor` — One idempotent migration block in `src/data/database.py`; no config, core, or UI layers.

**Conf:** `high` — Error message names the triple unique; AST-702 plan’s UPDATE-before-DELETE order is the direct collision; fix matches AST-702 intent (retry scrape → `fetch_website`, batch prefilter → `HOMEPAGE_READY`).

**Risk:** `Medium` — `_ensure_dispatch_task_schema` runs on admin dispatch reads for every process until ensured; a wrong migration still bricks Scheduled Actions, but change is localized and covered by existing AST-702 migration tests plus manual collision check.

---

## Code rules self-review

| Rule | Assessment |
|------|------------|
| §2.1 config / dispatch_tasks | Migration retargets DB rows only; schedulable defaults remain in `dispatch_task_admin_defaults` — no config drift. |
| §2.4 batch processing | Sets `batch_call_mode=1` on migrated `prefilter` row — unchanged intent from AST-702. |
| §1.3 DRY | No new helpers; reorder existing AST-702 SQL. |
| §3.3 imports | No import or layer changes. |

No conflicts requiring **Conf: !!-NONE**.

---

## Review

**Branch:** `origin/sub/AST-700/AST-703-uat-dispatch-task-migration-unique-collision`  
**Build tip:** `ad2d51b`

**Built:** Stage 1 — reorder AST-702 prefilter dispatch migration: DELETE `prefilter`/`WEBSITE_FOUND_RETRY` before UPDATE `prefilter`/`WEBSITE_FOUND` → `HOMEPAGE_READY` + `batch_call_mode=1`.
