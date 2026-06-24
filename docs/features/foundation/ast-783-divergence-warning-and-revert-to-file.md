# AST-783 — Divergence warning and Revert to file UI

**Linear (this ticket):** [AST-783](https://linear.app/astralcareermatch/issue/AST-783/divergence-warning-and-revert-to-file-ui-create-repo-json-files-for)  
**Parent:** [AST-756](https://linear.app/astralcareermatch/issue/AST-756/create-repo-json-files-for-agent-and-agent-task)  
**Publish ref:** `origin/sub/AST-756/AST-783-divergence-warning-and-revert-to-file` (child of AST-756; ignore Linear `gitBranchName` and the stale `AST-758` segment in the ticket Description)

## Summary

When live SQLite content for `agent` or `agent_task` differs from the checked-in repo JSON under `data/admin/`, **Manage Agents** and **Manage Tasks** show a persistent warning that admin edits will be **clobbered on the next server restart/deploy** unless Susan exports and commits repo JSON. Each screen also offers **Revert to file**, which reloads that table from the checked-in JSON **without restarting** the server. Builds on AST-782’s `repo_admin_json` load/export/apply contract — no changes to startup bootstrap ordering or seed files in this ticket.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/repo_admin_json.py` | Add divergence compare + per-table revert orchestration | core |
| `src/ui/api/api_admin.py` | `GET /api/admin/repo_json/status`, `POST /api/admin/repo_json/revert/<table_key>` | ui |
| `src/ui/frontend/src/components/RepoJsonDivergenceBanner.tsx` | **New:** warning banner + Revert to file (shared) | ui |
| `src/ui/frontend/src/pages/AdminAgentPrompts.tsx` | Mount banner for `agent`; refresh after save/revert | ui |
| `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | Mount banner for `agent_task`; refresh after save/revert | ui |

**Out of scope (explicit):** Startup upsert / seed JSON / export CLI (AST-782); HTTP export route; auto-export on admin save; `push_tables_to_prod.py` / `upsert_tables_from_prod.py`; changes to `ListPage.tsx`; edits under `tests/` or `docs/test-bible/**`.

## Stage 1: Core divergence compare and revert

**Done when:** `get_repo_admin_json_divergence_status()` and `revert_repo_admin_json_table(table_key)` exist; `python3 -m py_compile src/core/repo_admin_json.py` passes; manual smoke in Flask shell shows `diverged=True` after an admin save and `diverged=False` after revert. No API or React yet.

1. In `src/core/repo_admin_json.py`, extend imports from `src.utils.config`:

   ```python
   from src.utils.config import (
       REPO_ADMIN_JSON_CONFIG,
       get_repo_admin_json_path,
       get_repo_admin_json_table_keys,
       ...
   )
   ```

2. Add module-level compare helpers (private, above public API):

   - **`_REPO_JSON_ROW_KEY = {"agent": "agent_id", "agent_task": "task_key"}`** — stable row identity for sorting and keyed maps.

   - **`_normalize_repo_json_scalar(value: Any) -> Any`**
     - `None` → `None`
     - `bool` → unchanged
     - `int` → unchanged
     - `float` with `value.is_integer()` → `int(value)` (SQLite `task_seq` vs JSON float)
     - `str` → unchanged (do not strip prompt bodies)
     - anything else → `str(value)`

   - **`_normalize_repo_json_row(table_key: str, row: dict[str, Any]) -> dict[str, Any]`**
     - Return `{k: _normalize_repo_json_scalar(v) for k, v in row.items()}` (key order not significant).

   - **`_sorted_normalized_rows(table_key: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]`**
     - Normalize each row; sort by `_REPO_JSON_ROW_KEY[table_key]` string value ascending.

   - **`_fetch_db_repo_json_rows(conn, table_key: str) -> list[dict[str, Any]]`**
     - `table_key == "agent"` → `database.fetch_agent_repo_json_export_rows(conn)`
     - `table_key == "agent_task"` → `database.fetch_agent_task_repo_json_export_rows(conn)`
     - else → `ValueError`

   - **`_repo_admin_json_table_diverged(conn, table_key: str) -> bool`**
     - `file_rows = load_repo_admin_json_file(table_key)` (may raise — caller handles)
     - `db_rows = _fetch_db_repo_json_rows(conn, table_key)`
     - Compare `_sorted_normalized_rows(table_key, db_rows) == _sorted_normalized_rows(table_key, file_rows)` — **exact list equality** after normalization (same row count, keys, and scalar values).

3. Add public functions:

   - **`get_repo_admin_json_divergence_status() -> dict[str, dict[str, Any]]`**
     - Open one connection via `database._get_connection()`; `try/finally` close.
     - For each `table_key` in `get_repo_admin_json_table_keys()`:
       - `repo_relative_path` from `REPO_ADMIN_JSON_CONFIG["tables"][table_key]["repo_relative_path"]`
       - `diverged = _repo_admin_json_table_diverged(conn, table_key)`
       - Return shape:

         ```python
         {
             "agent": {"diverged": bool, "repo_relative_path": "data/admin/agent.json"},
             "agent_task": {"diverged": bool, "repo_relative_path": "data/admin/agent_task.json"},
         }
         ```

     - If `load_repo_admin_json_file` raises (`RuntimeError` / `ValueError`), propagate — status endpoint should surface 500 (missing/malformed repo file is an operator error, same as startup).

   - **`revert_repo_admin_json_table(table_key: str) -> int`**
     - Validate `table_key in get_repo_admin_json_table_keys()` else `ValueError`.
     - `rows = load_repo_admin_json_file(table_key)`
     - Open connection; `PRAGMA foreign_keys=ON`; `BEGIN IMMEDIATE`; apply:
       - `agent` → `database.apply_agent_repo_json_startup(conn, rows)`
       - `agent_task` → `database.apply_agent_task_repo_json_startup(conn, rows)`
     - `commit` / `rollback` on failure; always close connection.
     - Return `len(rows)` (count applied from file).
     - **No** file write, **no** git, **no** bootstrap call.

4. Extend **`__all__`** with `"get_repo_admin_json_divergence_status"` and `"revert_repo_admin_json_table"`.

⚠️ **Decision:** Divergence uses the **same row shapes** as AST-782 export (`fetch_agent_repo_json_export_rows` / `fetch_agent_task_repo_json_export_rows` vs bare JSON array on disk) — not the enriched Manage Agents list payload (`content_length`, `task_count`, inferred `brain_setting`). Compare is DB-export-shaped vs file-shaped only.

⚠️ **Decision:** Revert reuses existing **`apply_agent_repo_json_startup`** / **`apply_agent_task_repo_json_startup`** — same repo-wins semantics as startup (including agent delete-not-in-json and agent_task retire-all-current). No duplicate SQL.

## Stage 2: Admin API routes

**Done when:** Authenticated admin can `GET` status and `POST` revert for each table; invalid `table_key` returns 400; `python3 -m py_compile src/ui/api/api_admin.py` passes.

1. In `src/ui/api/api_admin.py`, add top-level import:

   ```python
   from src.core.repo_admin_json import (
       get_repo_admin_json_divergence_status,
       revert_repo_admin_json_table,
   )
   ```

2. Add **`GET /api/admin/repo_json/status`** (`@require_admin`):
   - Call `get_repo_admin_json_divergence_status()`.
   - Return `jsonify(status)` with 200.
   - On `RuntimeError` / `ValueError` from core (missing/malformed JSON): `jsonify({"error": str(exc)})`, 500.

3. Add **`POST /api/admin/repo_json/revert/<table_key>`** (`@require_admin`):
   - If `table_key` not in `("agent", "agent_task")`: `jsonify({"error": "table_key must be agent or agent_task"})`, 400.
   - `try`: `count = revert_repo_admin_json_table(table_key)` → `jsonify({"ok": True, "table_key": table_key, "row_count": count})`, 200.
   - On `RuntimeError` / `ValueError`: `jsonify({"error": str(exc)})`, 500.

4. Do **not** add export HTTP route — CLI `scripts/export_repo_admin_json.py` remains the export path per AST-782.

## Stage 3: Shared React banner and page wiring

**Done when:** Manage Agents and Manage Tasks each show the warning when `diverged` is true; **Revert to file** restores DB content and clears the banner without page reload; saving an edit re-shows the banner after refresh. Frontend builds (`npm run build` in `src/ui/frontend`).

1. Create **`src/ui/frontend/src/components/RepoJsonDivergenceBanner.tsx`**:

   - Props: `{ tableKey: "agent" | "agent_task"; onReverted?: () => void }`.

   - On mount and after successful revert, `GET /api/admin/repo_json/status` via existing `api()` helper; read `data[tableKey]`.

   - If `!diverged`, render `null`.

   - If `diverged`, render a banner **above** page content using the same inline style pattern as **AdminAnthropicAdHoc** confirmation banners (`marginBottom: 12`, `padding: 12`, `borderRadius: 4`, `background: var(--bg-card)`, `border: 1px solid var(--accent-gold)`):

     - **Agent copy:** “Local **agent** personas in the database differ from `data/admin/agent.json`. Changes will be overwritten on the next server restart or deploy unless you run `python3 scripts/export_repo_admin_json.py` and commit the updated JSON.”

     - **Agent_task copy:** same pattern with “**task prompts**” and `data/admin/agent_task.json`.

     - Button row: **`Revert to file`** (class `dep-btn cancel`, fontSize 12) — not primary save styling.

   - **Revert flow:** `useUserConfirm()` from `../components/UserPrompt` (not `window.confirm`):

     - Title: `"Revert to file"`
     - Message: `"Restore {agents|task prompts} in the database from the checked-in repo JSON file? Unsaved local edits will be lost."`
     - `variant: "danger"`, confirmLabel: `"Revert to file"`

     - On confirm: `POST /api/admin/repo_json/revert/${tableKey}`; on 200 refetch status + call `onReverted?.()`; on error show toast via optional callback or local error state (use a one-line red text under banner if POST fails — no new toast infrastructure required if parent already has Toast; prefer passing nothing and using inline error on banner).

   - Export a **`refetch()`** via `useImperativeHandle` **or** simpler: export prop **`refreshToken?: number`** from parent that increments after save — **use the refreshToken pattern**:

     - Props: `{ tableKey; refreshToken?: number; onReverted?: () => void }`
     - `useEffect` depends on `[tableKey, refreshToken]` to refetch status.

2. In **`AdminAgentPrompts.tsx`**:
   - Add `const [repoJsonRefresh, setRepoJsonRefresh] = useState(0)`.
   - In the fragment **before** `<ListPage>`, render:

     ```tsx
     <RepoJsonDivergenceBanner
       tableKey="agent"
       refreshToken={repoJsonRefresh}
       onReverted={() => { setRepoJsonRefresh(n => n + 1); loadAll() }}
     />
     ```

   - After **successful** create/update/delete agent handlers (where `loadAll()` is already called), add `setRepoJsonRefresh(n => n + 1)`.

3. In **`AdminTaskPrompts.tsx`**:
   - Same pattern with `tableKey="agent_task"`.
   - Place banner immediately **after** the `<h1>Manage Tasks</h1>` header block and **before** loading/sections.
   - Increment `repoJsonRefresh` after successful task save (`handleEditSave` success path).

⚠️ **Decision:** One shared banner component with `tableKey` prop — Manage Agents only checks `agent`, Manage Tasks only checks `agent_task` (per-table warnings per parent AC, not a combined mega-banner).

⚠️ **Decision:** No export button in UI — warning text mentions the existing CLI only; keeps AST-782 boundary (no HTTP export).

## Execution contract (build-child)

- Execute stages **in order**; one **`code(AST-783)`** commit per stage on epic worktree; publish each to **`origin/sub/AST-756/AST-783-divergence-warning-and-revert-to-file`** before the next stage.
- Do not add files beyond the table above without stopping and commenting on parent AST-756.
- If normalized compare produces false positives/negatives on real `agent_task` rows (e.g. `task_seq` type drift), stop and comment — do not widen compare to fuzzy/partial field sets without Susan approval.

## Self-Assessment

**Scope:** `Single-Component` — One new core API surface (compare + revert), two thin admin HTTP routes, one shared React banner, and wiring on the two existing admin prompt pages; no data-layer SQL changes.

**Conf:** `Medium` — AST-782 export/apply paths are settled; scalar normalization for SQLite-vs-JSON compare is the main subtlety, but revert is a straight reuse of startup apply functions.

**Risk:** `Medium` — Incorrect compare logic could hide real drift (Susan loses edits on deploy) or show spurious warnings; **Revert to file** uses repo-wins delete/retire semantics — confirm dialog must stay destructive-styled. Mitigated by exact export-shape compare and reusing transactional apply from AST-782.

## Plan vs ASTRAL_CODE_RULES

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuse `load_repo_admin_json_file`, `fetch_*_export_rows`, `apply_*_repo_json_startup` — no duplicate SQL or file I/O |
| §2.1 config | Paths from `REPO_ADMIN_JSON_CONFIG`; table keys from `get_repo_admin_json_table_keys()` |
| §3.3 layers | Core compares/reverts; data retains SQL; UI API JSON only; React calls API only |
| §1.5 logging | No new logging in this ticket — revert is admin-initiated, not batch |
| §3.6 debug | No spike scripts; no repo-root artifacts |

No unresolved conflicts.

## Build review stub

**Built:** `origin/sub/AST-756/AST-783-divergence-warning-and-revert-to-file` @ `4a08123`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `31bcef0` | Core divergence compare + `revert_repo_admin_json_table` |
| 2 | `10d3273` | `GET /api/admin/repo_json/status`, `POST .../revert/<table_key>` |
| 3 | `c022d5c` | `RepoJsonDivergenceBanner` + Manage Agents / Manage Tasks wiring |

## Radia review (2026-06-24)

**Ref:** `origin/dev...origin/sub/AST-756/AST-783-divergence-warning-and-revert-to-file` @ `3d0132c`

### What's solid

- All three plan stages landed: core compare/revert (`get_repo_admin_json_divergence_status`, `revert_repo_admin_json_table`), admin API routes (`GET /api/admin/repo_json/status`, `POST .../revert/<table_key>`), shared `RepoJsonDivergenceBanner` wired on Manage Agents / Manage Tasks with `refreshToken` + `useUserConfirm` danger revert.
- **§3.3 layers:** React → API only; `api_admin` delegates to core; no new data-layer SQL; revert reuses AST-782 `apply_*_repo_json_startup` in a transaction (FK on, rollback on failure).
- **Compare contract:** export-shaped DB rows vs bare JSON array; scalar normalization (`task_seq` float→int); sort by stable row key; exact list equality — matches plan decisions.
- **§1.5:** no new logging (plan OK).
- Tests cover core divergence/revert integration, API status/error/revert paths, banner show/hide/revert confirm, and page wiring (manifest-aligned).

### Issues

| Severity | Location | Finding |
| --- | --- | --- |
| **advisory** | Branch diff vs `origin/dev` | Diff includes full **AST-782** foundation (bootstrap, seed JSON, data upsert) as dependency — expected on this publish ref, not AST-783 scope smuggling. |
| **discuss** | Inherited from AST-782 seed | `data/admin/agent.json` remains `[]`; **Revert to file** on Manage Agents runs the same repo-wins delete-all-agents semantics as startup. Confirm Susan accepts that revert path for empty persona file. |

No **fix-now** items (layers, silent failure, UI hardcoded job states N/A, debug contract N/A).

### Recommended actions

| Priority | Action |
| --- | --- |
| resolve-child | None required — proceed when discuss item acknowledged. |
| Before prod | Populate `agent.json` via export if revert/startup should not wipe personas (same as AST-782). |

## Resolution (2026-06-24)

**Radia review:** clean — no **fix-now** items.

**Discuss (inherited AST-782 `agent.json` = `[]`):** Acknowledged. **Revert to file** on Manage Agents uses the same repo-wins semantics as startup (`apply_agent_repo_json_startup` deletes agents absent from JSON). Empty `[]` is intentional per AST-782; operators populate via Manage Agents then `python3 scripts/export_repo_admin_json.py` before prod if personas must persist.

**Product changes:** none — resolve pass is doc-only.

**§9a dry-run:** `origin/sub/AST-756/AST-783-divergence-warning-and-revert-to-file` merges cleanly into `origin/dev` and `origin/ftr/AST-756-repo-json-agent-agent-task` (no `merge-tree` conflict hunks).

**Publish tip at resolve:** `origin/sub/AST-756/AST-783-divergence-warning-and-revert-to-file` @ Radia doc `b1d5cf1`.
