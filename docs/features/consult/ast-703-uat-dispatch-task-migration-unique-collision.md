<!-- linear-archive: AST-703 archived 2026-06-23 -->

## Linear archive (AST-703)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-703/uat-dispatch-tasks-admin-500-prefilter-migration-unique-collision  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-700 — prefilter as batch process  
**Blocked by / blocks / related:** parent: AST-700

### Description

## What failed

Opening **Scheduled Actions** (admin dispatch tasks UI) returns **HTTP 500** on `GET /api/admin/dispatch_tasks` and `GET /api/admin/dispatch_tasks/task_keys`. Server log shows `sqlite3.IntegrityError: UNIQUE constraint failed: dispatch_task.candidate_id, dispatch_task.task_key, dispatch_task.trigger_state` during `_ensure_dispatch_task_schema` while handling the request. Susan cannot view or configure `fetch_website` / `prefilter` dispatch rows.

## Expected

Admin dispatch-task endpoints load successfully after AST-700 lands. Susan can open Scheduled Actions, see task keys (including `fetch_website`), and inspect/edit dispatch rows for the two-phase prefilter pipeline.

## Repro

1. Run app on `origin/dev` (or staging) with AST-700 landed and a candidate DB that already had legacy `prefilter` rows at both `WEBSITE_FOUND` and `WEBSITE_FOUND_RETRY`.
2. Open **Scheduled Actions** in the admin UI (or `GET /api/admin/dispatch_tasks` and `/api/admin/dispatch_tasks/task_keys`).
3. Observe **500** and IntegrityError in server log.

## Parent AC (quoted inline)

> **fetch_website dispatch task.** A new schedulable company dispatch task claims companies in **WEBSITE_FOUND** (and **WEBSITE_FOUND_RETRY** when applicable).
>
> **Batch prefilter dispatch task.** A schedulable company dispatch task claims companies in **HOMEPAGE_READY**.

## Boundaries

* This bug does **not** change: prefilter rubric, batch evaluate logic, scrape behavior, or UI layout beyond making dispatch admin APIs load.
* Does **not** re-open AST-701/702 feature scope — migration/idempotency fix only.

### Comments

#### betty — 2026-06-16T17:40:41.534Z
## QA test manifest (AST-703)

**Publish ref:** `origin/sub/AST-700/AST-703-uat-dispatch-task-migration-unique-collision` @ `93f0fd3` (tests `22998eb`)

1. **Dual-row migration** — legacy `prefilter`/`WEBSITE_FOUND` + `prefilter`/`WEBSITE_FOUND_RETRY` on one candidate migrates to exactly one `HOMEPAGE_READY` row with `batch_call_mode=1` without UNIQUE violation — `tests/component/data/database/test_dispatch_tasks.py::TestAst703PrefilterMigrationUniqueCollision`

2. **AST-702 regression** — base-row migrate + obsolete retry delete + `_RETRY_TASK_SEED` — `tests/component/data/database/test_dispatch_tasks.py::TestAst702PrefilterDispatchMigration`

**Narrowed run:**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_dispatch_tasks.py::TestAst703PrefilterMigrationUniqueCollision \
  tests/component/data/database/test_dispatch_tasks.py::TestAst702PrefilterDispatchMigration
```

**Pass criterion:** pytest green — not zero-arg harness / branch-lock gate.

**Bible shasum (`origin/sub/...`):**
- `docs/test-bible/core/consult.md` 7958d31e50d17dca73506666d4ec7329ad1eac5db505987dcd14f7be9f78c8b2
- `docs/test-bible/core/roster.md` e55e1710c131c20b1504b2ef9111e7a559e132c227194ba455da225c8d9afc49

— Betty

#### hedy — 2026-06-16T17:40:25.680Z
Plan doc: [ast-703-uat-dispatch-tasks-admin-500-prefilter-migration-unique-collision.md](https://github.com/susansomerset/astral/blob/sub/AST-700/AST-703-uat-dispatch-task-migration-unique-collision/docs/features/consult/ast-703-uat-dispatch-tasks-admin-500-prefilter-migration-unique-collision.md) @ `4169ec7d`

**Root cause:** AST-702 migration `UPDATE`d both `prefilter` @ `WEBSITE_FOUND` and @ `WEBSITE_FOUND_RETRY` to `HOMEPAGE_READY` before `DELETE` — triple-unique `(candidate_id, task_key, trigger_state)` violation when both legacy rows exist.

**Fix (Stage 1):** `DELETE` retry row first, then `UPDATE` base `WEBSITE_FOUND` → `HOMEPAGE_READY` + `batch_call_mode=1`. Stage 2: Betty regression test for both rows on same candidate.

**Self-assessment**
- **Scope:** minor — single migration block in `database.py`
- **Conf:** high — repro confirmed locally; reorder of existing AST-702 SQL
- **Risk:** Medium — edge orphan retry-only rows lose dispatch row; admin schema ensure contained

#### hedy — 2026-06-16T17:38:32.611Z
Plan: `docs/features/consult/ast-703-uat-dispatch-task-migration-unique-collision.md`
https://github.com/susansomerset/astral/blob/sub/AST-700/AST-703-uat-dispatch-task-migration-unique-collision/docs/features/consult/ast-703-uat-dispatch-task-migration-unique-collision.md

**Root cause:** AST-702 migration UPDATEs both legacy `prefilter`/`WEBSITE_FOUND` and `prefilter`/`WEBSITE_FOUND_RETRY` to `HOMEPAGE_READY` in one statement before DELETE — triple unique collision when both rows exist.

**Fix:** DELETE obsolete `prefilter`/`WEBSITE_FOUND_RETRY` first; UPDATE only `prefilter`/`WEBSITE_FOUND` → `HOMEPAGE_READY` + `batch_call_mode=1`.

**Self-assessment**
- Scope: `minor` — one migration block in `database.py`.
- Conf: `high` — error matches code path; reorder is direct fix for Susan's repro.
- Risk: `Medium` — migration runs on first admin dispatch schema ensure; localized but admin-critical path.

---

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
