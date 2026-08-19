# AST-1451 — Ad Hoc import list and load payload

- **Linear:** [AST-1451](https://linear.app/astralcareermatch/issue/AST-1451)
- **Parent:** [AST-1439](https://linear.app/astralcareermatch/issue/AST-1439)
- **Publish ref:** `sub/AST-1439/AST-1451-ad-hoc-import-list-and-load-payload`

Agent Ad Hoc can author a prompt from a catalog task, but it cannot pull a past `agent_data` run. This ticket owns the **read path only**: an authenticated admin list of stored runs (one JSON object per `batch_id`, newest first, no filter/cap), the existing batch-block GET as the Load payload, debug found→recorded on the list when `debug=True`, and a one-prefix strip so Test of an already-prefixed `adhoc-<task_key>` does not write `adhoc-adhoc-<task_key>`. Picker chrome, editor mapping, dirty-editor confirm, and `entity_id` restore on the page are **AST-1452** (Hedy).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Add `list_agent_data_batches`; name it on the `agent_data` header-inventory line | data |
| `src/core/agent.py` | Add `list_agent_data_runs` (debug found→recorded); strip one leading `adhoc-` in `run_adhoc_workbench_test` before the AST-515 prefix | core |
| `src/ui/api/api_admin.py` | Add `GET /api/admin/adhoc/runs` (`@require_admin`) calling core | ui |

Do **not** edit: `src/ui/frontend/**` (sibling AST-1452), `GET /api/agent_data/<batch_id>` in `src/ui/api/api_system.py` (that route **is** the Load payload), Manage Tasks, production `do_task`, dispatch, Save As, Execution History chrome, `src/utils/config.py` (`BLOCK_TYPES` already lists SYSTEM / CACHE_A–D / NO_CACHE / TASK / RESPONSE), `tests/`, bible. Do **not** add a second inspector or a new load route. Do **not** UPDATE/DELETE `agent_data` rows.

**Load contract for AST-1452:** After the operator picks a list row, Load fetches `GET /api/agent_data/<batch_id>` (existing `@require_auth` route → `src.core.agent.get_agent_data(batch_id)` → `get_agent_data_by_batch`). That JSON is the full set of blocks for the batch, `block_data` already resolved to plain text (refs followed). This ticket does not change that handler.

## Stage 1: Data — one row per batch, no cap

**Done when:** `list_agent_data_batches()` returns a Python `list` of dicts `{batch_id, created_at, entity_id, task_key}` with one dict per distinct `agent_data.batch_id`, ordered by `created_at` descending (newest first), including rows whose `task_key` starts with `adhoc-` and rows that do not. Empty table → `[]`. There is no `LIMIT`, no `WHERE` on candidate/date/`task_key`. `python3 -m py_compile src/data/database.py` passes.

1. In `src/data/database.py`, on the header inventory line that currently reads (abbreviated) `agent_data — Prompt/response content blocks keyed by batch_id (save_agent_data, get_agent_data_by_batch, get_agent_data, list_entity_latest_agent_refs); …`, insert `list_agent_data_batches` into that parenthetical list of functions. Do not add a new table.

2. In `src/data/database.py`, immediately after `get_agent_data_by_batch` and before `get_agent_data(agent_data_id)`, add:

```python
def list_agent_data_batches() -> List[Dict[str, Any]]:
    """One metadata row per agent_data.batch_id, newest batch first. No filter, no cap."""
    def _with_conn() -> List[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_agent_data_schema(conn)
            rows = conn.execute(
                """
                SELECT batch_id,
                       MAX(created_at) AS created_at,
                       MAX(task_key) AS task_key,
                       MAX(entity_id) AS entity_id
                FROM agent_data
                GROUP BY batch_id
                ORDER BY created_at DESC
                """
            ).fetchall()
            return [_row_to_dict(row) for row in rows]
        finally:
            conn.close()
    return _run_with_retry(_with_conn)
```

   Do **not** resolve or select `block_data`. Do **not** decompress. Do **not** join `dispatch_ledger`. Raise on DB errors (data layer does not log).

⚠️ **Decision:** `GROUP BY batch_id` with `MAX(created_at)` / `MAX(task_key)` / `MAX(entity_id)` rather than one list row per `agent_data` block or per RESPONSE `entity_id`. Parent AC is one visible row per batch. `MAX(entity_id)` is lexicographic when a batch has several non-null ids (batch RESPONSE copies); the list still returns that batch once. `MAX(task_key)` is identical for all rows of a normal batch. `MAX(created_at)` is the last block write for that batch (RESPONSE after prompts).

## Stage 2: Core — list + debug + single `adhoc-` prefix

**Done when:** `list_agent_data_runs(debug=False)` returns the same dicts as the data helper and emits **no** `debug_index` / `debug_detail` / `debug_detail_block` lines. `list_agent_data_runs(debug=True)` with N batches emits N `debug_index` headers (`func="list_agent_data_runs"`, `index` 1..N, `total=N`, `identifier=<batch_id>`, `outcome="listed"`) and, under each header, a found detail line then a recorded detail line (fields below). `run_adhoc_workbench_test(..., workbench_task_key="adhoc-evaluate_jd")` writes ledger + `agent_data.task_key` as `adhoc-evaluate_jd` (not `adhoc-adhoc-evaluate_jd`); `workbench_task_key="evaluate_jd"` still writes `adhoc-evaluate_jd`. `python3 -m py_compile src/core/agent.py` passes.

1. In `src/core/agent.py`, add `list_agent_data_batches` to the `from src.data.database import (` block (alongside `get_agent_data_by_batch`).

2. In `src/core/agent.py`, immediately after `get_agent_data(...)` (the batch-block reader, currently ~3871) and before `get_entity_response`, add:

```python
def list_agent_data_runs(*, debug: bool = False) -> List[Dict[str, Any]]:
    """Ad Hoc import list: one dict per stored batch, newest first."""
    rows = list_agent_data_batches()
    if debug:
        dbg = get_logger(__name__, debug_flag=True)
        total = len(rows)
        for i, row in enumerate(rows, start=1):
            batch_id = row.get("batch_id") or ""
            created_at = row.get("created_at")
            entity_id = row.get("entity_id")
            task_key = row.get("task_key")
            dbg.debug_index(
                func="list_agent_data_runs",
                index=i,
                total=total,
                identifier=str(batch_id),
                outcome="listed",
            )
            dbg.debug_detail(
                f"found created_at={created_at!r} entity_id={entity_id!r} task_key={task_key!r}"
            )
            dbg.debug_detail(
                f"recorded batch_id={batch_id!r} created_at={created_at!r} "
                f"entity_id={entity_id!r} task_key={task_key!r}"
            )
    return rows
```

   Do **not** log `block_data`. Do **not** call `debug_detail_block` on this path (list metadata is short; truncation is for payloads >50 lines and does not apply here). When `debug=False`, do not construct a debug-flagged logger and do not call `debug_index` / `debug_detail`.

3. In `src/core/agent.py`, at the **start** of `run_adhoc_workbench_test` (before `ledger_task_key = f"adhoc-{workbench_task_key}"`), replace that assignment and the `TASK_CONFIG.get(workbench_task_key)` line with:

```python
    catalog_task_key = (workbench_task_key or "").strip()
    if catalog_task_key.startswith("adhoc-"):
        catalog_task_key = catalog_task_key[len("adhoc-"):]
    ledger_task_key = f"adhoc-{catalog_task_key}"
    batch_id = f"{ledger_task_key}-{_uuid4()}"
    entity_type = (TASK_CONFIG.get(catalog_task_key) or {}).get("entity_type") or "candidate"
```

   Keep every later call that today passes `workbench_task_key` into `run_adhoc` / log format strings as-is **except** `save_dispatch_ledger` / `agent_data` storage already use `ledger_task_key` / `_store_prompt_blocks(..., task_key=ledger_task_key)` — those pick up the stripped prefix automatically. Strip **one** leading `adhoc-` only (do not loop). Do **not** change `run_adhoc` itself. Do **not** change `adhoc/preview`.

⚠️ **Decision:** Strip in `run_adhoc_workbench_test`, not in `_resolve_adhoc`. This ticket owns Test persist, not editor `task_key` state. AST-1452 will also strip for the workbench dropdown so catalog lookup / `task_key_uuid` stay honest; this strip is the last-line guarantee if Test is posted with `task_key` already `adhoc-foo`. `TASK_CONFIG.get` uses `catalog_task_key` so `entity_type` still resolves when the posted key was prefixed.

## Stage 3: Admin list route

**Done when:** `GET /api/admin/adhoc/runs` with an admin session returns HTTP 200 and a JSON **array** of `{batch_id, created_at, entity_id, task_key}` (same keys as Stage 1), newest first. Unauthenticated / non-admin follows the same 401/403 behavior as `GET /api/admin/adhoc/entities`. The handler does not write `agent_data`. `python3 -m py_compile src/ui/api/api_admin.py` passes.

1. In `src/ui/api/api_admin.py`, add `list_agent_data_runs` to the `from src.core.agent import (` block (next to `run_adhoc_workbench_test`).

2. In `src/ui/api/api_admin.py`, immediately after `adhoc_entities` and before `_resolve_adhoc`, add:

```python
@admin_bp.route("/adhoc/runs")
@require_admin
def adhoc_runs():
    """Import picker source: one agent_data batch per row, newest first."""
    return jsonify(list_agent_data_runs(debug=ui_llm_debug()))
```

   Pass `debug=ui_llm_debug()` with **no** extra query-arg plumbing (same as `adhoc_test`). Do **not** add candidate_id / date / limit query params. Do **not** shape rows in the route beyond `jsonify` of the core list. `entity_id` JSON `null` when the data helper returns `None`.

## Estimate

Confirm Chuckles estimate: 3 — agree

Known admin-list + existing GET load + one prefix strip. Debug contract is mechanical (same Style D as `_store_prompt_blocks`). No schema migration, no frontend.
