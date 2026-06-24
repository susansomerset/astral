# AST-790 — UAT: agent_task grouping metadata not applied on revert/startup

**Linear (this ticket):** [AST-790](https://linear.app/astralcareermatch/issue/AST-790/uat-agent-task-grouping-metadata-not-applied-on-revert-startup)  
**Parent:** [AST-756](https://linear.app/astralcareermatch/issue/AST-756/create-repo-json-files-for-agent-and-agent-task)  
**Publish ref:** `origin/sub/AST-756/AST-790-agent-task-grouping-metadata-not-applied-on-revert-startup` (UAT bug child; ignore Linear `gitBranchName`)

## Summary

Susan UAT: `data/admin/agent_task.json` carries full grouping metadata (`task_group_name`, `task_group_order`, `task_name`, `task_seq`) per task — e.g. `anticipate_scan` → **Job Artifacts** / **5000** / **Anticipate Scan** / **1**. After **Revert to file** (AST-783) or cold **startup repo-wins upsert** (AST-782), DB `current=1` rows instead get seed defaults: **(unassigned)** / **ZZZ** / raw `task_key` / **999**. Prompts and `agent_id` load; grouping does not.

**Root cause (confirmed on scratch DB):** `apply_agent_task_copy_upsert` in `database.py` calls `_save_agent_task_on_connection(..., import_explicit=True)` with prompt/`agent_id`/`run_next` only — **never forwards the four grouping columns** from the pasted/repo JSON row. `_resolved_grouping_fields` therefore falls back to `seed_values_for_task_key` defaults. A second gap: when prompt content is unchanged, the function sets `skip_row = True` and **never invokes** `_save_agent_task_on_connection`, so grouping-only diffs are also dropped on revert.

**AST-790** fixes **`apply_agent_task_copy_upsert` only** — the shared import path used by startup (`apply_agent_task_repo_json_startup`), admin Copy Output paste, and revert (`revert_repo_admin_json_table`). No repo JSON seed edits, no UI, no `repo_admin_json.py` changes.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Forward grouping columns in `apply_agent_task_copy_upsert`; extend skip guard to compare grouping | data |

**Out of scope (explicit):** `data/admin/agent_task.json`, `docs/uat-fixtures/**`, `src/core/repo_admin_json.py`, admin React/API, `tests/`, `docs/test-bible/**`, agent personas (AST-787).

## Stage 1: Forward grouping on Copy Output / repo JSON import

**Done when:** After `apply_agent_task_repo_json_startup(conn, rows)` on a scratch DB seeded from `load_repo_admin_json_file("agent_task")`, `get_agent_task("anticipate_scan")` returns `task_group_name == "Job Artifacts"`, `task_group_order == "5000"`, `task_name == "Anticipate Scan"`, `task_seq == 1.0` (or `1` — SQLite REAL). Same result after `revert_repo_admin_json_table("agent_task")` when DB prompts already match repo JSON (grouping-only revert case). `python3 -m py_compile src/data/database.py` passes. No other files touched.

1. In `src/data/database.py`, locate **`apply_agent_task_copy_upsert`**. Extend the **`sel_cur`** query (the `SELECT … FROM agent_task WHERE task_key = ? AND current = 1` used before the per-row import loop) to also fetch **`task_group_order`, `task_group_name`, `task_seq`, `task_name`** (indices 10–13 — same order as `_save_agent_task_on_connection`'s `existing` row).

2. Add a small **in-function helper** (keep inside `apply_agent_task_copy_upsert` — no new module-level symbol unless reuse is obvious):

   ```python
   def _grouping_from_copy_row(r: dict[str, Any]) -> tuple[str, str, float, str]:
       go = "" if r["task_group_order"] is None else (
           r["task_group_order"] if isinstance(r["task_group_order"], str) else str(r["task_group_order"])
       )
       gn = "" if r["task_group_name"] is None else (
           r["task_group_name"] if isinstance(r["task_group_name"], str) else str(r["task_group_name"])
       )
       gs = float(r["task_seq"]) if r["task_seq"] is not None else 999.0
       tn = "" if r["task_name"] is None else (
           r["task_name"] if isinstance(r["task_name"], str) else str(r["task_name"])
       )
       return go.strip(), gn.strip(), gs, tn.strip()
   ```

   Use **`r["task_group_order"]`** etc. directly — `_validate_copy_row_keys` already enforced all schema columns exist on each row.

3. In the **`skip_row`** block (when `cur_before is not None` and prompt/`agent_id`/`run_next` content matches):

   a. Parse DB grouping from `cur_before` tail: `db_go, db_gn, db_gs, db_tn` at the new column indices.

   b. Parse file grouping: `file_go, file_gn, file_gs, file_tn = _grouping_from_copy_row(r)`.

   c. Treat grouping as changed if any of the four differ (compare `task_seq` with `float()` on both sides).

   d. Set **`skip_row = False`** when grouping changed — even if prompt content unchanged. Keep existing **`skip_row = True`** only when **both** content **and** grouping match.

4. In the **`_save_agent_task_on_connection(...)`** call at the bottom of the per-`task_key` loop, add kwargs (still with **`import_explicit=True`**):

   ```python
   task_group_order=r["task_group_order"],
   task_group_name=r["task_group_name"],
   task_seq=r["task_seq"],
   task_name=r["task_name"],
   ```

   Do **not** pre-resolve through `_resolved_grouping_fields` here — pass raw row values so `import_explicit` empty-string semantics apply consistently with other Copy Output columns.

5. **Hand-verify** (document in build completion comment):

   ```python
   from src.core.repo_admin_json import load_repo_admin_json_file, revert_repo_admin_json_table
   from src.data import database

   rows = load_repo_admin_json_file("agent_task")
   conn = database._get_connection()
   try:
       database.apply_agent_task_repo_json_startup(conn, rows)
       conn.commit()
       t = database.get_agent_task("anticipate_scan")
       assert t["task_group_name"] == "Job Artifacts"
       assert t["task_group_order"] == "5000"
       assert t["task_name"] == "Anticipate Scan"
       assert float(t["task_seq"]) == 1.0
   finally:
       conn.close()

   # Grouping-only revert: mutate DB grouping, revert, confirm repo values restored
   conn = database._get_connection()
   try:
       database.apply_agent_task_repo_json_startup(conn, rows)
       conn.commit()
       uuid = conn.execute(
           "SELECT task_key_uuid FROM agent_task WHERE task_key='anticipate_scan' AND current=1"
       ).fetchone()[0]
       conn.execute(
           "UPDATE agent_task SET task_group_name='(unassigned)', task_group_order='ZZZ' WHERE task_key_uuid=?",
           (uuid,),
       )
       conn.commit()
   finally:
       conn.close()
   revert_repo_admin_json_table("agent_task")
   t2 = database.get_agent_task("anticipate_scan")
   assert t2["task_group_name"] == "Job Artifacts"
   ```

⚠️ **Decision:** Fix lives in **`apply_agent_task_copy_upsert`** (not a parallel repo-json import) so startup, revert, and Admin Data Management paste share one code path — matches AST-782 plan decision to reuse Copy Output semantics.

⚠️ **Decision:** Do **not** change `_resolved_grouping_fields` or seed defaults — Manage Tasks saves without explicit grouping still use catalog seed; only **explicit** Copy Output / repo JSON rows should overwrite grouping.

## Execution contract (build-child)

- **One** `code(AST-790)` commit for Stage 1 (`src/data/database.py` only).
- Publish to **`origin/sub/AST-756/AST-790-agent-task-grouping-metadata-not-applied-on-revert-startup`** before **Code Complete**.
- Betty owns tests/manifest; do not edit `tests/` or `docs/test-bible/**`.

## Self-Assessment

**Scope:** `minor` — single function in `database.py`; no layer boundary changes.

**Conf:** `high` — root cause reproduced on scratch DB; fix is forwarding four existing columns through an established import path.

**Risk:** `Medium` — `apply_agent_task_copy_upsert` also serves Admin Copy Output paste; grouping-forward fix is intended for all import paths but must not regress prompt versioning — mitigated by keeping content-change logic unchanged and only extending skip guard + kwargs.

## Plan vs ASTRAL_CODE_RULES

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Extend existing import function; reuse `_save_agent_task_on_connection` grouping kwargs — no duplicate SQL. |
| §2.1 config | No new config; grouping values come from pasted/repo row, not TASK_CONFIG. |
| §3.3 imports | Data-layer-only change; no new cross-layer imports. |

No unresolved conflicts.
