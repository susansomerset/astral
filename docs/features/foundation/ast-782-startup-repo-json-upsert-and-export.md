<!-- linear-archive: AST-782 archived 2026-07-22 -->

## Linear archive (AST-782)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-782/startup-repo-json-upsert-and-export-create-repo-json-files-for-agent  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-756 — create repo json files for agent and agent_task.  
**Blocked by / blocks / related:** parent: AST-756; blocks: AST-783

### Description

## What this implements

Repo-owned JSON under `data/admin/` for the `agent` and `agent_task` tables, startup upsert during `bootstrap_runtime()` (set all rows `current=0`, then upsert JSON as current rows), bootstrap ordering before `sync_agent_tasks`, and an export path that writes current=1 rows only.

## Acceptance criteria

* After a fresh clone and server start, current (`current = 1`) rows in `agent` and `agent_task` match the checked-in `data/admin/` JSON files (field values for every row present in JSON).
* Rows absent from repo JSON do not appear in Manage Agents / Manage Tasks after startup upsert; retired versions remain stored with `current = 0`.
* Deploying a commit that changes either repo JSON file results in updated prompt/persona content after the next server restart, without manual Table Upsert or prod push scripts.
* Export from the current database produces JSON containing current rows only and round-trips through startup upsert without data loss.
* `sync_agent_tasks` runs after repo JSON upsert and only adds missing blank catalog rows for new task keys — it does not overwrite repo-loaded prompt bodies.

## Boundaries

* Does not implement Manage Agents / Manage Tasks divergence UI or Revert to file (sibling Katherine ticket).
* Does not include `dispatch_task`, `candidate`, or other tables.
* Does not auto-commit or push repo JSON on admin save.

## Notes for planning

* Paths: `data/admin/agent.json` and `data/admin/agent_task.json` (or equivalent under `data/admin/` per config block).
* Attach to existing `bootstrap_runtime()` after validation, before `sync_agent_tasks`.
* Reuse or extend existing config-table upsert semantics where possible.

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/AST-756-repo-json-agent-agent-task`, child `sub/AST-756/AST-757-startup-repo-json-upsert-and-export`. Created at **dispatch-parent**.

### Comments

#### radia — 2026-06-24T05:22:17.764Z
### Plan fidelity (AST-782)

Diff `origin/dev...origin/sub/AST-756/AST-782-startup-repo-json-upsert-and-export` @ `1cb5ba9` (+ doc `4fd6901`).

Stages 1–4 match plan: `REPO_ADMIN_JSON_CONFIG`, `repo_admin_json.py`, data upsert/export, bootstrap wire before `sync_agent_tasks`, export CLI + `data/admin/*.json`. Layers OK (§3.3): core orchestrates + count-only INFO; data raises, no log. Transaction: `BEGIN IMMEDIATE`, FK on, rollback on failure. `agent_task` reuses `apply_agent_task_copy_upsert` after retire-all-current; `agent` upsert excludes legacy `model_code`. Tests cover manifest + bootstrap ordering.

**fix-now:** none.

**discuss:** `data/admin/agent.json` is `[]` — startup runs `DELETE FROM agent` when the array is empty (plan hand-verify `agent=0`). By design per plan HIGH-risk note; confirm empty personas in repo until export is intentional before prod deploy.

**advisory:** Full branch diff vs `origin/dev` also includes sibling **AST-775/776** bible/roster test rollup from epic merge; AST-782 product commits stay within the plan file table.

Combined review: `docs/features/foundation/ast-782-startup-repo-json-upsert-and-export.md` (Radia review section).

#### betty — 2026-06-24T05:19:34.049Z
## QA test manifest (AST-782)

**Publish:** `origin/sub/AST-756/AST-782-startup-repo-json-upsert-and-export` @ `1cb5ba9` (`merge-tests(AST-782): origin/tests 68cad04`)

**Broken / revised this pass:** `TestBootstrapRuntime` call-order — must include `apply_repo_admin_json_at_startup` between validation and `sync_agent_tasks`.

### Manifest (test-child)

1. **Bootstrap ordering** — `tests/component/core/test_bootstrap.py` (full file)

2. **Core repo JSON load / apply / export** — `tests/component/core/test_repo_admin_json.py` (full file)

3. **Config paths + apply order** — `tests/component/utils/test_config.py::TestAst782RepoAdminJsonConfig`

4. **Agent repo upsert + export queries** — `tests/component/data/database/test_agents.py::TestAst782AgentRepoJsonStartup`

5. **Agent_task repo upsert + export queries** — `tests/component/data/database/test_agent_tasks.py::TestAst782AgentTaskRepoJsonStartup`

**Narrowed run:**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_bootstrap.py \
  tests/component/core/test_repo_admin_json.py \
  tests/component/utils/test_config.py::TestAst782RepoAdminJsonConfig \
  tests/component/data/database/test_agents.py::TestAst782AgentRepoJsonStartup \
  tests/component/data/database/test_agent_tasks.py::TestAst782AgentTaskRepoJsonStartup \
  -q
```

**Pass criterion:** pytest green on items 1–5 — not zero-arg harness / branch-lock gate.

**Bible shasum (`origin/sub/...`):**
- `docs/test-bible/core/bootstrap.md` `c5ffd707d42fae585d46f2728f92a2276ad171864410a26640d81975f8a8d8d9`
- `docs/test-bible/core/repo_admin_json.md` `e814f3e26b35ddb89bf4eeba53b3c405c0b0eea4952db504750e5038b6ede0b1`
- `docs/test-bible/data/database/agents.md` `fc17d14b040b113563fd278d237f4d2f24cb3be1ed95e567928c78b1c51e1cf8`
- `docs/test-bible/data/database/agent_tasks.md` `c2206c05ffc7aff8805aacf5521b81e530b7d11f38cdcac9e19f8c121f92da4d`
- `docs/test-bible/ui/server.md` `f105fc40da48906c354b5952cf735ea7e98bfab2122a959a268f94d5d3c58043`
- `docs/test-bible/utils/config.md` `0e9143144c039cf6362364266447c4a2e7af1dbe791c8f4a91758d999ce89e7c`

#### ada — 2026-06-24T02:59:27.490Z
Plan doc: https://github.com/susansomerset/astral/blob/sub/AST-756/AST-782-startup-repo-json-upsert-and-export/docs/features/foundation/ast-782-startup-repo-json-upsert-and-export.md

**Self-assessment**
- **Scope:** MAJOR-CHANGE — config block, new `repo_admin_json` core module, data-layer startup upsert/export queries, bootstrap ordering, seed JSON under `data/admin/`, export CLI.
- **Conf:** Medium — reuses `apply_agent_task_copy_upsert` for task import; `agent` deletes rows absent from JSON (no `current` column); seed content comes from local DB at build time.
- **Risk:** HIGH — bad startup upsert could wipe prompts on deploy; mitigated by transactional apply, fail-loud missing files, retire-all-current before task import, and insert-only `sync_agent_tasks`.

---

# AST-782 — Startup repo JSON upsert and export

**Linear (this ticket):** [AST-782](https://linear.app/astralcareermatch/issue/AST-782/startup-repo-json-upsert-and-export-create-repo-json-files-for-agent)  
**Parent:** [AST-756](https://linear.app/astralcareermatch/issue/AST-756/create-repo-json-files-for-agent-and-agent-task)  
**Publish ref:** `origin/sub/AST-756/AST-782-startup-repo-json-upsert-and-export` (child of AST-756; ignore Linear `gitBranchName`)

## Summary

Make `agent` and `agent_task` **repo-owned** under `data/admin/`: two checked-in JSON files are the source of truth applied on every server start inside existing `bootstrap_runtime()`, **before** `sync_agent_tasks`. Add an on-demand **export** path that writes `current = 1` rows only (all `agent` rows — that table has no versioning) back to those files so Susan can bootstrap from a live DB or commit admin edits. Divergence UI and **Revert to file** are **AST-783** (Katherine) — not this ticket.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `REPO_ADMIN_JSON_CONFIG` block: table keys, repo-relative paths, export column policy | utils |
| `src/core/repo_admin_json.py` | **New:** load/validate JSON files, `apply_repo_admin_json_at_startup()`, `export_repo_admin_json_to_files()` | core |
| `src/data/database.py` | `apply_agent_repo_json_startup(conn, rows)`, `apply_agent_task_repo_json_startup(conn, rows)`, `fetch_agent_repo_json_export_rows(conn)`, `fetch_agent_task_repo_json_export_rows(conn)` | data |
| `src/core/bootstrap.py` | Insert repo JSON upsert between `_validate_runtime_coupling()` and `sync_agent_tasks` | core |
| `scripts/export_repo_admin_json.py` | CLI: export current DB rows → `data/admin/*.json` | scripts |
| `data/admin/agent.json` | Initial seed — current `agent` rows from export (committed) | data |
| `data/admin/agent_task.json` | Initial seed — `current = 1` `agent_task` rows from export (committed) | data |

**Out of scope (explicit):** Manage Agents / Manage Tasks divergence banner, **Revert to file** UI/API (AST-783); `dispatch_task`, `candidate`, or other tables; auto-commit on admin save; changes to `push_tables_to_prod.py` / `upsert_tables_from_prod.py`.

## Stage 1: Config contract and JSON file helpers

**Done when:** `REPO_ADMIN_JSON_CONFIG` exists with literal paths and table keys; `src/core/repo_admin_json.py` can read both JSON files, validate envelope shape, and raise `ValueError` with path context on malformed input; `python3 -m py_compile` passes for touched modules. No bootstrap or DB writes yet.

1. In `src/utils/config.py`, after `ASTRAL_CONFIG` (or adjacent admin-related blocks), add **`REPO_ADMIN_JSON_CONFIG`**:

   ```python
   REPO_ADMIN_JSON_CONFIG = {
       "schema_version": 1,
       "tables": {
           "agent": {
               "repo_relative_path": "data/admin/agent.json",
               # PRAGMA columns written/read for repo JSON (exclude legacy model_code — brain_setting is authoritative)
               "columns": (
                   "agent_id",
                   "content",
                   "brain_setting",
                   "temperature",
                   "max_tokens",
                   "updated_at",
               ),
           },
           "agent_task": {
               "repo_relative_path": "data/admin/agent_task.json",
               # Full PRAGMA column list in SQLite order — same shape as Copy Output / table_copy_upsert
               "columns": None,  # resolved at runtime via database.table_columns(conn, "agent_task")
           },
       },
   }
   ```

   Add helpers:
   - `get_repo_admin_json_path(table_key: str) -> Path` — resolves `repo_relative_path` against repo root (`Path(__file__).resolve().parent.parent.parent` pattern used elsewhere in config).
   - `get_repo_admin_json_table_keys() -> tuple[str, ...]` — `("agent", "agent_task")` in fixed order **agent first, then agent_task** (personas before tasks that reference `agent_id`).

2. Create `src/core/repo_admin_json.py` with module docstring: repo JSON is applied at startup (AST-782); not invoked from admin save paths; AST-381 admin snapshot remains cancelled.

3. Implement **`_repo_root() -> Path`** (repo root = parent of `src/`).

4. Implement **`load_repo_admin_json_file(table_key: str) -> list[dict[str, Any]]`**:
   - Resolve path from config; if file missing, raise **`RuntimeError`** with full path (`bootstrap` must fail loud — no silent empty default).
   - Read UTF-8 text; `json.loads`; require **top-level JSON array** (same as Copy Output paste format).
   - Each element must be a `dict` with **only flat JSON scalars** (reject nested `dict`/`list` — reuse validation rule from `table_copy_upsert` / `_copy_reject_nested_json` semantics; raise `ValueError` with `table_key` and 1-based row index).
   - Return the list unchanged (column validation deferred to data layer per table).

5. Implement **`validate_repo_admin_json_rows(table_key: str, rows: list[dict], *, conn)`** (internal):
   - For `agent`: row keys must equal `REPO_ADMIN_JSON_CONFIG["tables"]["agent"]["columns"]` exactly.
   - For `agent_task`: row keys must equal `database.table_columns(conn, "agent_task")` exactly.
   - Every exported/import row for `agent_task` must have `current` coercing to **`1`** via existing `_coerce_agent_task_current_for_import`.
   - At most one `current = 1` row per `task_key` in the payload.

6. Set `__all__ = ["apply_repo_admin_json_at_startup", "export_repo_admin_json_to_files", "load_repo_admin_json_file", "repo_admin_json_paths"]` (stubs raising `NotImplementedError` OK until Stage 3/4 — remove stubs when implementing).

⚠️ **Decision:** JSON on disk is a **bare array** of row objects (Copy Output shape), not the AST-381 `{schema_version, exported_at, tables}` envelope — keeps round-trip identical to Admin Data Management **Copy Output** and existing `apply_agent_task_copy_upsert` paste path. `schema_version` lives in config only.

⚠️ **Decision:** `agent` repo JSON excludes `model_code` (legacy DB column; `brain_setting` is authoritative per AST-492). Startup upsert writes `brain_setting` only; `model_code` left untouched on existing rows or NULL on new inserts.

## Stage 2: Data-layer startup upsert and export queries

**Done when:** Data functions exist; unit-testable with in-memory or fixture DB; no bootstrap wire yet. `python3 -m py_compile src/data/database.py` passes.

1. In `src/data/database.py`, add **`fetch_agent_repo_json_export_rows(conn) -> list[dict]`**:
   - `_ensure_agent_schema(conn)`.
   - `SELECT` columns from `REPO_ADMIN_JSON_CONFIG["tables"]["agent"]["columns"]` in that order (`ORDER BY agent_id`).
   - Return list of dicts (raw DB values — no `_expose_agent_public` computed keys).

2. Add **`fetch_agent_task_repo_json_export_rows(conn) -> list[dict]`**:
   - `_ensure_agent_task_schema(conn)`.
   - `SELECT *` (all PRAGMA columns) `FROM agent_task WHERE current = 1 ORDER BY task_key`.
   - Return `_row_to_dict` per row.

3. Add **`apply_agent_repo_json_startup(conn, rows: list[dict]) -> None`** on caller-owned connection (caller commits):
   - `_ensure_agent_schema(conn)`.
   - Validate each row has exactly the agent export columns; `agent_id` non-empty string.
   - For each row: `validate_allowed_brain_setting` on `brain_setting` when present/non-empty; upsert via same SQL as `save_agent` (**INSERT** new / **UPDATE** existing on `agent_id`) using row values for `content`, `brain_setting`, `temperature`, `max_tokens`, `updated_at` (use `_utc_now()` when `updated_at` missing or empty).
   - After upserts: **`DELETE FROM agent WHERE agent_id NOT IN (<ids from JSON>)`**. If JSON is empty array, delete all agents (repo wins).
   - ⚠️ **Decision:** `agent` has no `current` column — removal from JSON **deletes** the row (equivalent to “no longer in Manage Agents list”). Historical `agent_task` versions stay `current = 0`; `agent` has no version history.

4. Add **`apply_agent_task_repo_json_startup(conn, rows: list[dict]) -> None`** on caller-owned connection:
   - `_ensure_agent_task_schema(conn)`.
   - Validate rows via `validate_repo_admin_json_rows("agent_task", rows, conn=conn)` (import from core or duplicate minimal checks in data — prefer **data validates shape**, core orchestrates file I/O).
   - **Step A:** `UPDATE agent_task SET current = 0 WHERE current = 1` (retire entire active set).
   - **Step B:** Call existing **`apply_agent_task_copy_upsert(conn, rows)`** with the JSON rows (all `current = 1`). Reuse import semantics — do not reimplement `_save_agent_task_on_connection`.
   - Keys absent from JSON remain `current = 0` only → hidden from `list_candidate_tasks` / `get_agent_task`.

5. Do **not** change `sync_agent_tasks`, `save_agent`, `save_agent_task`, or Copy Output admin routes in this stage.

## Stage 3: Core orchestration and bootstrap wire

**Done when:** Server start applies repo JSON before `sync_agent_tasks`; missing/malformed JSON fails startup with `RuntimeError`; `python3 -m py_compile src/core/bootstrap.py src/core/repo_admin_json.py` passes.

1. In `src/core/repo_admin_json.py`, implement **`apply_repo_admin_json_at_startup() -> None`**:
   - Open one connection via `database._get_connection()` (or public getter if preferred — match existing bootstrap pattern).
   - `conn.execute("PRAGMA foreign_keys=ON")`.
   - `conn.execute("BEGIN IMMEDIATE")`.
   - For `table_key` in `get_repo_admin_json_table_keys()` order:
     - `rows = load_repo_admin_json_file(table_key)`.
     - If `table_key == "agent"`: `database.apply_agent_repo_json_startup(conn, rows)`.
     - Elif `table_key == "agent_task"`: `database.apply_agent_task_repo_json_startup(conn, rows)`.
   - `conn.commit()` in `try`; `ROLLBACK` on any exception; always `conn.close()`.
   - Log one INFO line per table via `get_logger(__name__)`: `repo_admin_json applied table=agent rows=N` (counts only — no prompt bodies).

2. Update `src/core/bootstrap.py` module docstring: order becomes validation → **repo admin JSON upsert** → `sync_agent_tasks` → scheduler.

3. In **`bootstrap_runtime()`**, insert after `_validate_runtime_coupling()` and before `database.sync_agent_tasks(...)`:

   ```python
   from src.core.repo_admin_json import apply_repo_admin_json_at_startup

   apply_repo_admin_json_at_startup()
   ```

   (Prefer top-level import in `bootstrap.py` alongside other imports — not inline inside the function.)

4. Confirm **`sync_agent_tasks`** is unchanged and still runs **after** repo JSON — it only `INSERT`s blank rows for `task_key` not in `existing` current set; it must not overwrite repo-loaded prompt bodies (existing behavior).

## Stage 4: Export CLI and seed JSON files

**Done when:** `scripts/export_repo_admin_json.py` writes both files; committed `data/admin/agent.json` and `data/admin/agent_task.json` exist; a local restart round-trips export → startup upsert without changing current row counts or prompt text.

1. In `src/core/repo_admin_json.py`, implement **`export_repo_admin_json_to_files() -> dict[str, int]`**:
   - Open connection, ensure schemas, call `fetch_agent_repo_json_export_rows` and `fetch_agent_task_repo_json_export_rows`.
   - Write each list to its configured path with `json.dumps(rows, indent=2, ensure_ascii=False) + "\n"` (UTF-8).
   - Create `data/admin/` directory if missing.
   - Return `{"agent": len(agent_rows), "agent_task": len(task_rows)}`.

2. Add **`scripts/export_repo_admin_json.py`**:
   - Shebang + docstring: `python3 scripts/export_repo_admin_json.py` — exports **current** DB rows to repo JSON paths; does not restart server.
   - `sys.path` bootstrap matching other scripts in `scripts/`.
   - Call `export_repo_admin_json_to_files()`; print counts to stdout; exit 0.

3. **Seed files `10f050b`:** On the epic worktree, run `python3 scripts/export_repo_admin_json.py` against the local DB Susan uses for development (the worktree `data/astral.db` symlink target). Commit the resulting `data/admin/agent.json` and `data/admin/agent_task.json`.

4. Hand-verify (document in build completion comment, not in plan execution during build):
   - `SELECT COUNT(*) FROM agent` equals JSON array length.
   - `SELECT COUNT(*) FROM agent_task WHERE current = 1` equals JSON array length.
   - Restart Flask once; counts unchanged; spot-check one `task_key` prompt hash or length unchanged.

⚠️ **Decision:** No admin HTTP export route in AST-782 — CLI + core function are the contract AST-783 may call later. Do not add React UI in this ticket.

## Execution contract (build-child)

- Execute stages **in order**; one **`code(AST-782)`** commit per stage on epic worktree; publish each to **`origin/sub/AST-756/AST-782-startup-repo-json-upsert-and-export`** before the next stage.
- Do not add files beyond the table above without stopping and commenting on parent AST-756.
- If `apply_agent_task_copy_upsert` behavior conflicts with “repo wins full replace” after Step A retire-all-current, stop — do not fork import logic; comment with repro.

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — New config block, new core module, data-layer startup upsert + export queries, bootstrap ordering change, two repo-tracked JSON seed files, and export CLI across utils / core / data / scripts layers.

**Conf:** `Medium` — `agent_task` path reuses `apply_agent_task_copy_upsert`; `agent` uses delete-not-in-json because the table has no `current` column; bootstrap ordering and “repo wins” retire-all-current step are explicit, but export seed content depends on Susan’s local DB at build time.

**Risk:** `HIGH` — Incorrect startup upsert could retire or delete production prompt/persona rows on deploy; mitigated by transactional apply, fail-loud missing JSON, export round-trip verification, and keeping `sync_agent_tasks` insert-only for missing keys.

## Plan vs ASTRAL_CODE_RULES

| Rule | Assessment |
|------|------------|
| §1.2 / §3.3 layers | Core orchestrates; data holds SQL; UI untouched in AST-782. `bootstrap.py` may import new core module only. |
| §1.3 DRY | Reuse `apply_agent_task_copy_upsert` for `agent_task` import; do not duplicate `_save_agent_task_on_connection`. |
| §2.1 config | Paths, column policy, table keys, and `schema_version` in `REPO_ADMIN_JSON_CONFIG` literals. |
| §1.5 logging | One INFO line per table at startup in core; data layer raises, no log. |
| §3.6 debug output | No spikes under `debug/` for this feature; seed JSON lives at `data/admin/` (tracked). |

No unresolved conflicts.

## Build review stub

**Built:** `origin/sub/AST-756/AST-782-startup-repo-json-upsert-and-export` @ `10f050b`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `a986669` | `REPO_ADMIN_JSON_CONFIG` + `repo_admin_json.py` loaders |
| 2 | `10ec853` | Data-layer startup upsert + export queries |
| 3 | `1a82413` | Bootstrap wire before `sync_agent_tasks` |
| 4 | `10f050b` | Export CLI + seed `data/admin/*.json` |

**Hand-verify:** Export counts matched local DB (`agent=0`, `agent_task current=33`); `apply_repo_admin_json_at_startup()` round-trip preserved counts.

**Radia:** diff `origin/dev...origin/sub/AST-756/AST-782-startup-repo-json-upsert-and-export` when Tests Passed.

## Radia review (2026-06-24)

**Ref:** `origin/dev...origin/sub/AST-756/AST-782-startup-repo-json-upsert-and-export` @ `1cb5ba9`

### What's solid

- All four plan stages landed: `REPO_ADMIN_JSON_CONFIG`, `repo_admin_json.py` load/apply/export, data-layer upsert + export queries, bootstrap wire before `sync_agent_tasks`, export CLI + seed JSON.
- **§3.3 layers:** core orchestrates file I/O + one INFO line per table; data holds SQL and raises; UI untouched. Bootstrap top-level import only.
- **§2.4 / transactions:** `BEGIN IMMEDIATE`, `PRAGMA foreign_keys=ON`, rollback on failure, single connection for agent → agent_task order.
- **§1.3 DRY:** `agent_task` path reuses `apply_agent_task_copy_upsert` after retire-all-current; `agent` upsert mirrors `save_agent` column set (excludes legacy `model_code` per plan).
- **§1.5 logging:** count-only INFO in core; no data-layer logging.
- Tests align with Betty manifest (`test_repo_admin_json`, `TestAst782*` data tests, bootstrap call-order update, config path helpers).

### Issues

| Severity | Location | Finding |
| --- | --- | --- |
| **discuss** | `data/admin/agent.json` (`[]`) | Empty repo file deletes all `agent` rows on every startup (`DELETE FROM agent` when JSON array empty). Matches plan hand-verify (`agent=0`) and documented HIGH deploy risk — confirm Susan wants empty personas in repo until populated via export. |
| **advisory** | Branch diff vs `origin/dev` | Diff also carries sibling **AST-775/776** roster tests + bible rows from epic merge line; **AST-782 product footprint** stays within the plan file table — not scope smuggling in the AST-782 commits. |

No **fix-now** items (layers, SQL bind counts, silent failure, debug contract N/A).

### Recommended actions

| Priority | Action |
| --- | --- |
| Before prod deploy | Run `scripts/export_repo_admin_json.py` after personas exist if `agent.json` should not wipe `agent` on boot. |
| resolve-child | None required — proceed when discuss item acknowledged. |

## Resolution (2026-06-24)

**Radia review:** clean — no **fix-now** items.

**Discuss (`data/admin/agent.json` = `[]`):** Acknowledged. Seed came from build-time export against local dev DB (`agent=0`, `agent_task current=33`). Empty array is repo-wins-by-design per plan — startup deletes all `agent` rows when JSON is `[]`. Operators populate personas via Manage Agents then `python3 scripts/export_repo_admin_json.py` before prod deploy if empty personas are not intended.

**Product changes:** none — resolve pass is doc-only.

**§9a dry-run:** `origin/sub/AST-756/AST-782-startup-repo-json-upsert-and-export` merges cleanly into `origin/dev` and `origin/ftr/AST-756-repo-json-agent-agent-task` (no conflict markers in `git merge-tree`).

**Publish tip at resolve:** `origin/sub/AST-756/AST-782-startup-repo-json-upsert-and-export` @ Radia doc `4fd6901`.
