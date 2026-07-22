<!-- linear-archive: AST-793 archived 2026-07-22 -->

## Linear archive (AST-793)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-793/uat-divergence-banner-persists-after-revert-to-file  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-756 — create repo json files for agent and agent_task.  
**Blocked by / blocks / related:** parent: AST-756

### Description

## What failed

Susan UAT (2026-06-25): On localhost and staging, the **task prompts** divergence banner stays visible after clicking **Revert to file**:

> Local **task prompts** in the database differ from `data/admin/agent_task.json`. Changes will be overwritten on the next server restart or deploy unless you run `python3 scripts/export_repo_admin_json.py` and commit the updated JSON.

Revert appears to succeed (no error), but `/api/admin/repo_json/status` still reports `agent_task.diverged: true`, so the banner never clears.

## Expected

After **Revert to file** for `agent_task`, DB export rows match checked-in `data/admin/agent_task.json` under the same normalization used by `get_repo_admin_json_divergence_status`. Banner clears immediately; `agent_task.diverged` is **false** until the admin edits prompts again.

## Repro

1. Open admin task prompts page where divergence banner shows for `agent_task`.
2. Click **Revert to file** and confirm.
3. Observe banner still present on localhost/staging.
4. Optional: `GET /api/admin/repo_json/status` — `agent_task.diverged` remains true after revert.

## Parent AC (quoted inline)

> After a fresh clone and server start, current (`current = 1`) rows in `agent` and `agent_task` match the checked-in `data/admin/` JSON files (field values for every row present in JSON).

## Boundaries

* Does **not** re-seed repo JSON (AST-786/787) or re-fix grouping import (AST-790).
* Fix divergence compare and/or revert so post-revert status is accurate; minimal UI change only if refetch wiring is wrong.

### Comments

#### radia — 2026-06-25T01:03:36.876Z
### Plan fidelity (AST-793) — FIX-UAT

Diff `origin/dev...origin/sub/AST-756/AST-793-divergence-banner-persists-after-revert-to-file` @ `03e435e` (+ doc `9ea7219`).

UAT bug fix verified: `code(AST-793)` @ `05b4374` replaces `apply_agent_task_copy_upsert` in `apply_agent_task_repo_json_startup` with `_apply_agent_task_repo_json_rows_exact` — upserts by `task_key_uuid` with verbatim file columns (`updated_at` included), fixing metadata-only divergence after revert. `apply_agent_task_copy_upsert` unchanged for Copy Output. Betty manifest `TestAst793AgentTaskRevertDivergence` locks divergence clear, UUID preservation, double-revert.

**fix-now:** none.

**advisory:** Branch diff vs `origin/dev` includes AST-792 deploy_status/linear bible rollup; AST-793 product delta is `database.py` only. Repo JSON grouping now comes from exact row write (all columns), not AST-790 copy-upsert path — correct for repo-wins.

Combined review: `docs/features/foundation/ast-793-uat-divergence-banner-persists-after-revert-to-file.md` (Radia review section).

#### betty — 2026-06-25T01:01:54.463Z
## QA test manifest (AST-793)

**Publish:** `origin/sub/AST-756/AST-793-divergence-banner-persists-after-revert-to-file` @ `03e435e` (`merge-tests(AST-793): origin/tests 7b2051b`)

**Scope:** `apply_agent_task_repo_json_startup` uses exact repo JSON apply (`_apply_agent_task_repo_json_rows_exact`) so revert clears **`agent_task.diverged`**. **`src/data/database.py` only** — no compare/UI/repo JSON seed changes.

### Manifest (test-child)

1. **Revert clears divergence** — `tests/component/core/test_repo_admin_json.py::TestAst793AgentTaskRevertDivergence::test_revert_clears_agent_task_divergence_after_db_edit`

2. **Preserves file `task_key_uuid`** — `TestAst793AgentTaskRevertDivergence::test_revert_preserves_repo_task_key_uuid`

3. **Double revert idempotent** — `TestAst793AgentTaskRevertDivergence::test_double_revert_agent_task_stays_not_diverged`

4. **Scope gate (required):** `git show 05b4374 --name-only` — expect **only** `src/data/database.py` and `docs/features/foundation/ast-793-uat-divergence-banner-persists-after-revert-to-file.md` (no `data/admin/**`).

**Narrowed run:**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_repo_admin_json.py::TestAst793AgentTaskRevertDivergence \
  -q
```

**Pass criterion:** pytest green on items 1–3 + scope gate item 4.

**Bible shasum (`origin/sub/...`):**
- `docs/test-bible/core/repo_admin_json.md` `77c2f0ed4493313d4d4c7b40863c17de86af56ee5b50b24e3b07853fb1b07594`

#### katherine — 2026-06-25T00:58:42.805Z
Plan: `https://github.com/susansomerset/astral/blob/sub/AST-756/AST-793-divergence-banner-persists-after-revert-to-file/docs/features/foundation/ast-793-uat-divergence-banner-persists-after-revert-to-file.md`

**Scope:** Single-Component — fix `apply_agent_task_repo_json_startup` so revert/startup writes exact repo JSON row values (`task_key_uuid`, `updated_at`), not Manage Tasks versioning via `_save_agent_task_on_connection`.

**Conf:** high — reproduced locally: all 37 rows match file content after revert but compare fails on metadata-only diff.

**Risk:** Medium — repo-wins apply path for `agent_task`; mitigated by inline revert smoke + Betty divergence tests.

---

# AST-793 — UAT: divergence banner persists after Revert to file

**Linear (this ticket):** [AST-793](https://linear.app/astralcareermatch/issue/AST-793/uat-divergence-banner-persists-after-revert-to-file)  
**Parent:** [AST-756](https://linear.app/astralcareermatch/issue/AST-756/create-repo-json-files-for-agent-and-agent-task) (User Testing)  
**Publish ref:** `origin/sub/AST-756/AST-793-divergence-banner-persists-after-revert-to-file` (child of AST-756; ignore Linear `gitBranchName`)

## Summary

Susan UAT: on Manage Tasks, **Revert to file** for `agent_task` returns success but the divergence banner stays visible because `GET /api/admin/repo_json/status` still reports `agent_task.diverged: true`.

**Root cause (reproduced on epic worktree):** `revert_repo_admin_json_table("agent_task")` → `apply_agent_task_repo_json_startup` retires all `current = 1` rows, then `apply_agent_task_copy_upsert` inserts via `_save_agent_task_on_connection`, which **mints a new `task_key_uuid` and `updated_at`** instead of writing the repo JSON values. Prompt/grouping fields match the file after revert, but compare still fails on identity metadata — **37/37 rows** differ only on `task_key_uuid` and `updated_at`.

**Fix:** repo-wins startup/revert for `agent_task` must persist **exact file row values** (including `task_key_uuid` and `updated_at`), using the same direct upsert pattern as historical Copy Output rows in `apply_agent_task_copy_upsert` — not Manage Tasks versioning via `_save_agent_task_on_connection`.

UI refetch wiring in `RepoJsonDivergenceBanner` is already correct (`fetchStatus()` after POST revert); no React change unless build proves otherwise.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Exact repo JSON apply for `agent_task` in `apply_agent_task_repo_json_startup` | data |

**Out of scope (explicit):** re-seed repo JSON (AST-786/787), grouping import (AST-790), divergence compare logic changes in `repo_admin_json.py`, admin UI copy, `tests/` / `docs/test-bible/**`, `data/admin/*.json` edits.

## Stage 1: Exact repo JSON apply for `agent_task`

**Done when:** After `revert_repo_admin_json_table("agent_task")` or `apply_repo_admin_json_at_startup()` on a DB that previously diverged, `get_repo_admin_json_divergence_status()["agent_task"]["diverged"]` is **false** when `data/admin/agent_task.json` is unchanged; `python3 -m py_compile src/data/database.py` passes.

1. In **`src/data/database.py`**, locate **`apply_agent_task_repo_json_startup`** (AST-782). It currently:

   ```python
   conn.execute("UPDATE agent_task SET current = 0 WHERE current = 1")
   apply_agent_task_copy_upsert(conn, rows)
   ```

2. **Replace** the `apply_agent_task_copy_upsert(conn, rows)` call with a repo-JSON-specific exact apply helper in the **same file** (private name, e.g. `_apply_agent_task_repo_json_rows_exact`). Do **not** change `apply_agent_task_copy_upsert` behavior for Manage Tasks Copy Output imports.

3. **`_apply_agent_task_repo_json_rows_exact(conn, rows)`** — caller already validated rows via `_validate_agent_task_repo_json_rows`; caller owns transaction:

   - `columns_ordered = table_columns(conn, "agent_task")`
   - `qt = _sql_quote_ident("agent_task")`
   - `cols_join = ",".join(_sql_quote_ident(c) for c in columns_ordered)`
   - `placeholders = ",".join("?" * len(columns_ordered))`
   - For each `row` in `rows` (order arbitrary; all `current = 1`):

     a. `uuid_pk = str(row["task_key_uuid"]).strip()` — raise `ValueError` if missing/blank (same as historical Copy Output path).

     b. `existing = conn.execute(f"SELECT {cols_join} FROM {qt} WHERE {_sql_quote_ident('task_key_uuid')} = ?", (uuid_pk,)).fetchone()`

     c. **If `existing` is None:**  
        `INSERT INTO agent_task ({cols_join}) VALUES ({placeholders})` with `tuple(row[c] for c in columns_ordered)`.

     d. **If `existing` is not None:**  
        `UPDATE` all columns **except** `task_key_uuid` from `row`, and set `current = 1` (file rows are always current). Mirror the historical-row update branch in `apply_agent_task_copy_upsert` (set clause excludes PK).

   - Return `len(rows)` for callers that need a count (optional; `apply_agent_task_repo_json_startup` stays void).

4. **Do not** call `_save_agent_task_on_connection` from this path — that helper always generates new UUID/timestamp on insert and is correct for Manage Tasks edits, not repo-wins restore.

5. **Verify before commit** (epic worktree, `.venv` active):

   ```bash
   python3 -c "
   from src.core import repo_admin_json as r
   from src.data import database

   # Force divergence: edit one current task in DB without touching file
   conn = database._get_connection()
   try:
       conn.execute(
           \"UPDATE agent_task SET task_name = task_name || ' uat-edit' WHERE task_key = 'prefilter_company' AND current = 1\"
       )
       conn.commit()
   finally:
       conn.close()

   assert r.get_repo_admin_json_divergence_status()['agent_task']['diverged'] is True
   r.revert_repo_admin_json_table('agent_task')
   assert r.get_repo_admin_json_divergence_status()['agent_task']['diverged'] is False
   print('ok')
   "
   ```

6. **Second revert smoke** (same session): run `revert_repo_admin_json_table('agent_task')` twice in a row — must not raise (PK/unique errors) and second pass must still report `diverged: false`.

⚠️ **Decision:** Fix the **apply/revert write path**, not divergence compare exclusions — AST-783 contract compares full export-shaped rows; parent AST-756 AC expects DB field values to match checked-in JSON after revert.

⚠️ **Decision:** Upsert by **`task_key_uuid`** (file PK), not `task_key` — matches historical Copy Output import and preserves stable UUIDs referenced elsewhere; retired rows for the same `task_key` may remain `current = 0` as history.

## Execution contract (build-child)

- One **`code(AST-793)`** commit on epic worktree; publish to **`origin/sub/AST-756/AST-793-divergence-banner-persists-after-revert-to-file`** before **Code Complete**.
- Do not add files beyond the table above without stopping and commenting on parent AST-756.
- Betty owns regression tests — note in Code Complete comment that post-revert `agent_task.diverged === false` should be locked (extend AST-783 divergence tests or new AST-793 class).

## Self-Assessment

**Scope:** `Single-Component` — one data-layer apply helper + swap call site in `apply_agent_task_repo_json_startup`.

**Conf:** `high` — root cause reproduced locally (metadata-only mismatch on all 37 rows); fix pattern already exists in the same file for historical Copy Output rows.

**Risk:** `Medium` — touches repo-wins startup/revert for `agent_task`; incorrect upsert could break apply at boot or leave stale `current = 1` rows — mitigated by inline revert smoke before commit and Betty manifest on divergence/revert paths.

## Plan vs ASTRAL_CODE_RULES

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuse column-order / upsert pattern from existing `apply_agent_task_copy_upsert` historical branch — no duplicate SQL dialect |
| §2.1 config | Row keys validated by existing `_validate_agent_task_repo_json_rows` against live schema |
| §3.3 layers | Data-layer fix only; core compare/revert and UI unchanged |
| §3.6 | Inline verify script only — no repo-root artifacts |

No unresolved conflicts.

## Parent / sibling context (reference only)

- **AST-783** added divergence compare + revert UI; agent revert path already clears banner (uses `apply_agent_repo_json_startup` which preserves file fields).
- **AST-786/787** seeded repo JSON — not this ticket.
- **AST-790** grouping import — out of scope per bug boundaries.

## Build review stub

**Built:** `origin/sub/AST-756/AST-793-divergence-banner-persists-after-revert-to-file` @ `05b4374`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `05b4374` | `_apply_agent_task_repo_json_rows_exact` — revert/startup writes file uuid + updated_at |

**Hand-verify:** post-revert `agent_task.diverged` false; double-revert smoke green.

## Radia review (2026-06-25) — FIX-UAT

**Ref:** `origin/dev...origin/sub/AST-756/AST-793-divergence-banner-persists-after-revert-to-file` @ `03e435e`

### What's solid

- **Root cause + fix aligned:** `apply_agent_task_repo_json_startup` now calls `_apply_agent_task_repo_json_rows_exact` — upserts by `task_key_uuid` with **verbatim** file columns (including `updated_at`), avoiding `_save_agent_task_on_connection` minting new UUID/timestamp. `apply_agent_task_copy_upsert` unchanged for Manage Tasks Copy Output (AST-790 grouping path preserved there).
- **Scope gate:** `code(AST-793)` @ `05b4374` product delta is **`src/data/database.py` only** (+ plan stub in same commit).
- **§1.3 DRY / §3.3:** reuses historical Copy Output upsert pattern in-file; data-layer only; no compare/UI changes.
- **Tests:** `TestAst793AgentTaskRevertDivergence` locks divergence clear after revert, UUID preservation, and double-revert smoke — matches plan verify script.

### Issues

| Severity | Location | Finding |
| --- | --- | --- |
| **advisory** | Branch diff vs `origin/dev` | Includes sibling **AST-792** deploy_status/linear/merge_ticket_log bible+test rollup from merge-tests — AST-793 product footprint stays in `database.py`. |
| **advisory** | Repo vs Copy Output paths | Grouping for repo JSON now comes from exact row write (all columns), not AST-790's `apply_agent_task_copy_upsert` forward — correct for repo-wins; Copy Output paste still uses AST-790 path. |

No **fix-now** items.

### Recommended actions

| Priority | Action |
| --- | --- |
| resolve-child | None — merge when parent UAT lane clears. |
| Post-merge UAT | Manage Tasks **Revert to file** → banner clears without page reload. |

## Resolution (2026-06-25)

**Radia review:** clean — no **fix-now** items.

**Product changes:** none — resolve pass is doc-only. Exact repo JSON apply shipped in `code(AST-793)` @ `05b4374`.

**§9a dry-run:** `origin/sub/AST-756/AST-793-divergence-banner-persists-after-revert-to-file` merges cleanly into `origin/dev` and `origin/ftr/AST-756-repo-json-agent-agent-task`.

**Publish tip at resolve:** `origin/sub/AST-756/AST-793-divergence-banner-persists-after-revert-to-file` @ `84e33e9`.
