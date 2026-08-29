# AST-1534 — Scoped adhoc runs list API

- **Linear:** [AST-1534](https://linear.app/astralcareermatch/issue/AST-1534)
- **Parent:** [AST-1532](https://linear.app/astralcareermatch/issue/AST-1532)
- **Publish ref:** `sub/AST-1532/AST-1534-scoped-adhoc-runs-list-api`

Agent Ad Hoc import (`GET /api/admin/adhoc/runs` from AST-1451) returns every `agent_data` batch with no filter or cap. This ticket owns the **backend scoped list only**: named config literals for the import cap (10) and picker visible-row count (5), a `dispatch_ledger`-joined filtered limited query, `list_agent_data_runs` filter/limit kwargs with Style D debug only on the returned set, and query params on `adhoc_runs`. React chrome / five-line scroll viewport / Load wiring are **AST-1535** (Hedy).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `adhoc_import_runs_limit` (10) and `adhoc_import_picker_visible_rows` (5) under `UI_CONFIG` | utils |
| `src/data/database.py` | Extend `list_agent_data_batches` with candidate / optional task_key / limit; join `dispatch_ledger` on `batch_id` | data |
| `src/core/agent.py` | Pass filters/limit through `list_agent_data_runs`; debug found→recorded only for returned rows | core |
| `src/ui/api/api_admin.py` | Read `candidate_id` / `task_key` query args; pass config limit into core | ui |

Do **not** edit: `src/ui/frontend/**` (sibling AST-1535), `GET /api/agent_data/<batch_id>`, Save As / Preview / Test / `run_adhoc_workbench_test` prefix strip, production `do_task`, `tests/`, bible. Do **not** accept a client-supplied `limit` query param (config is the only cap). Do **not** add a new route or table.

**Contract for AST-1535:** `GET /api/admin/adhoc/runs?candidate_id=<id>&task_key=<catalog_key>` returns a JSON **array** (same row shape as today: `{batch_id, created_at, entity_id, task_key}`), at most `UI_CONFIG["adhoc_import_runs_limit"]` rows, newest `created_at` first. Omit or blank `candidate_id` → `[]`. Blank/omit `task_key` with a candidate → last N runs for that candidate across task keys. `UI_CONFIG["adhoc_import_picker_visible_rows"]` is served via existing `GET /api/system/ui_config` (`**UI_CONFIG`) for the sibling viewport height — this ticket does not use that key in SQL.

## Stage 1: Config literals

**Done when:** `UI_CONFIG` contains integer keys `adhoc_import_runs_limit: 10` and `adhoc_import_picker_visible_rows: 5`. `GET /api/system/ui_config` (unchanged handler) includes both keys in its JSON because it spreads `UI_CONFIG`. No other file reads them yet. `python3 -m py_compile src/utils/config.py` passes.

1. In `src/utils/config.py`, inside the `UI_CONFIG = { ... }` dict, after the existing `cover_letter_signature_image` block and before the closing `}`, add:

```python
    # AST-1534: Agent Ad Hoc import picker — API list cap + sibling viewport row count.
    "adhoc_import_runs_limit": 10,
    "adhoc_import_picker_visible_rows": 5,
```

⚠️ **Decision:** Flat keys on `UI_CONFIG` (same style as `list_table_frozen_data_columns`) rather than a nested `adhoc_import` object. Sibling AST-1535 and `/api/system/ui_config` already consume flat `UI_CONFIG` keys; nesting would force a new consumer shape for no gain. Cap and visible-row both live here even though only the cap is used by the API in this ticket — parent Component scope puts both literals on this child so the sibling never invents a magic `5`.

## Stage 2: Data — filtered limited batch list

**Done when:** Calling `list_agent_data_batches(candidate_id="", limit=10)` or `list_agent_data_batches(candidate_id=None, limit=10)` returns `[]` with no SQL. With a non-empty `candidate_id`, results are only batches whose `dispatch_ledger.batch_id` matches `agent_data.batch_id` and `dispatch_ledger.candidate_id` equals that id, one dict per `batch_id` with keys `{batch_id, created_at, entity_id, task_key}`, `ORDER BY created_at DESC`, at most `limit` rows when `limit` is a positive int. When `task_key` is non-empty after strip, only rows whose stored `agent_data.task_key` matches that catalog key after stripping **one** leading `adhoc-` from the stored value (so `adhoc-evaluate_jd` matches query `evaluate_jd`, and bare `evaluate_jd` matches query `evaluate_jd`). When `task_key` is empty/None, no task filter. Empty match set → `[]`. Raise on DB errors (no logging in data). Header inventory still names `list_agent_data_batches` on the `agent_data` line (signature change only — no new function name). `python3 -m py_compile src/data/database.py` passes.

1. In `src/data/database.py`, replace the body of `list_agent_data_batches` (keep the name; do not add a second helper) with:

```python
def list_agent_data_batches(
    *,
    candidate_id: Optional[str] = None,
    task_key: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """One metadata row per agent_data.batch_id for a candidate, newest first.

    Joins dispatch_ledger on batch_id for candidate_id scope. Optional task_key
    match strips one leading ``adhoc-`` from stored agent_data.task_key.
    Empty/blank candidate_id → []. Optional limit caps rows (ORDER BY created_at DESC).
    """
    cid = (candidate_id or "").strip()
    if not cid:
        return []

    catalog_task_key = (task_key or "").strip()
    if catalog_task_key.startswith("adhoc-"):
        catalog_task_key = catalog_task_key[len("adhoc-"):]

    def _with_conn() -> List[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_agent_data_schema(conn)
            _ensure_dispatch_ledger_schema(conn)
            clauses = ["dl.candidate_id = ?"]
            params: List[Any] = [cid]
            if catalog_task_key:
                # Strip one leading adhoc- from stored task_key for catalog compare.
                clauses.append(
                    """(
                        CASE
                            WHEN ad.task_key LIKE 'adhoc-%'
                            THEN substr(ad.task_key, 7)
                            ELSE ad.task_key
                        END
                    ) = ?"""
                )
                params.append(catalog_task_key)
            where = " AND ".join(clauses)
            sql = f"""
                SELECT ad.batch_id,
                       MAX(ad.created_at) AS created_at,
                       MAX(ad.task_key) AS task_key,
                       MAX(ad.entity_id) AS entity_id
                FROM agent_data ad
                INNER JOIN dispatch_ledger dl ON dl.batch_id = ad.batch_id
                WHERE {where}
                GROUP BY ad.batch_id
                ORDER BY created_at DESC
            """
            if limit is not None and int(limit) > 0:
                sql += " LIMIT ?"
                params.append(int(limit))
            rows = conn.execute(sql, params).fetchall()
            return [_row_to_dict(row) for row in rows]
        finally:
            conn.close()
    return _run_with_retry(_with_conn)
```

   Do **not** resolve or select `block_data`. Do **not** decompress. Do **not** log. Do **not** change `save_agent_data` / `get_agent_data_by_batch`. Batches with `agent_data` but no `dispatch_ledger` row are excluded by the `INNER JOIN` (Ad Hoc Test always writes ledger — AST-1451).

⚠️ **Decision:** Extend `list_agent_data_batches` kwargs in place rather than a new function name. Sole caller today is `list_agent_data_runs`; unfiltered full-history list is intentionally retired for this path (parent purpose). Empty candidate returns `[]` in data so every caller gets the same contract without each layer re-checking.

⚠️ **Decision:** `substr(ad.task_key, 7)` — SQLite `substr` is 1-based; `"adhoc-"` is 6 characters, so index 7 is the first catalog character. Matches Python `task_key[len("adhoc-"):]` used in `run_adhoc_workbench_test`. Strip query `task_key` once the same way so a caller that posts `adhoc-evaluate_jd` still matches.

## Stage 3: Core — kwargs + debug on returned set only

**Done when:** `list_agent_data_runs(candidate_id="c1", task_key="evaluate_jd", limit=10, debug=False)` returns the data helper’s filtered list and emits no debug-contract lines. With `debug=True` and N returned rows, emits exactly N `debug_index` headers (`func="list_agent_data_runs"`, `index` 1..N, `total=N`, `identifier=<batch_id>`, `outcome="listed"`) each followed by the same found then recorded `debug_detail` lines as today — **only** for those N rows (never for batches filtered out). `python3 -m py_compile src/core/agent.py` passes.

1. In `src/core/agent.py`, replace `list_agent_data_runs` with:

```python
def list_agent_data_runs(
    *,
    candidate_id: Optional[str] = None,
    task_key: Optional[str] = None,
    limit: Optional[int] = None,
    debug: bool = False,
) -> List[Dict[str, Any]]:
    """Ad Hoc import list: filtered/capped agent_data batches, newest first."""
    rows = list_agent_data_batches(
        candidate_id=candidate_id,
        task_key=task_key,
        limit=limit,
    )
    if debug:
        dbg = get_logger(__name__, debug_flag=True)
        total = len(rows)
        for i, row in enumerate(rows, start=1):
            batch_id = row.get("batch_id") or ""
            created_at = row.get("created_at")
            entity_id = row.get("entity_id")
            row_task_key = row.get("task_key")
            dbg.debug_index(
                func="list_agent_data_runs",
                index=i,
                total=total,
                identifier=str(batch_id),
                outcome="listed",
            )
            dbg.debug_detail(
                f"found created_at={created_at!r} entity_id={entity_id!r} task_key={row_task_key!r}"
            )
            dbg.debug_detail(
                f"recorded batch_id={batch_id!r} created_at={created_at!r} "
                f"entity_id={entity_id!r} task_key={row_task_key!r}"
            )
    return rows
```

   Keep the found→recorded Style D shape identical to AST-1451; only the input set changes (already filtered/limited by data). When `debug=False`, do not construct a debug-flagged logger. Do **not** change `run_adhoc_workbench_test` or `_store_prompt_blocks`.

## Stage 4: Admin route — query params + config limit

**Done when:** `GET /api/admin/adhoc/runs?candidate_id=<cid>&task_key=<key>` as admin returns HTTP 200 and a JSON array of at most `UI_CONFIG["adhoc_import_runs_limit"]` matching rows (shape unchanged). Same path with no / blank `candidate_id` returns `[]`. Same path with `candidate_id` and blank/omitted `task_key` returns up to the config cap for that candidate across task keys. Auth unchanged (`@require_admin` → same 401/403 as `adhoc_entities`). Handler does not write `agent_data`. Ignores any `limit` query string if present (does not read it). `python3 -m py_compile src/ui/api/api_admin.py` passes.

1. In `src/ui/api/api_admin.py`, add `UI_CONFIG` to the `from src.utils.config import (` block (alphabetically near other uppercase config names is fine; place after `TRACKER_CONFIG` or adjacent to `ADMIN_CONFIG`).

2. In `src/ui/api/api_admin.py`, replace `adhoc_runs` with:

```python
@admin_bp.route("/adhoc/runs")
@require_admin
def adhoc_runs():
    """Import picker source: candidate-scoped agent_data batches, newest first, config-capped."""
    candidate_id = (request.args.get("candidate_id") or "").strip()
    task_key = (request.args.get("task_key") or "").strip()
    return jsonify(
        list_agent_data_runs(
            candidate_id=candidate_id or None,
            task_key=task_key or None,
            limit=UI_CONFIG["adhoc_import_runs_limit"],
            debug=ui_llm_debug(),
        )
    )
```

   Do **not** reshape rows beyond `jsonify` of the core list. Do **not** read a `limit` query param. Do **not** touch `adhoc_entities` / `adhoc_preview` / `adhoc_test`.

## Estimate

Confirm Chuckles estimate: 2 — agree

Extends the AST-1451 list path with config + join filter + query params; no schema migration, no frontend, known admin-endpoint pattern.

## Traceability

- Child AC1 (≤10 rows, candidate + task_key incl. `adhoc-` equivalence, newest first) → Stages 1–4
- Child AC2 (empty candidate → `[]`; candidate + empty task_key → last 10 for candidate; refresh = new query params) → Stages 2–4 (API side; UI refetch is AST-1535)
- Child AC3 (debug only on filtered returned rows) → Stage 3
- Parent AC2 (five-row viewport) → N/A here (`adhoc_import_picker_visible_rows` config only; chrome AST-1535)
- Parent AC4 (Load unchanged) → N/A (no Load path edits)

## Joan validate

```
[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1534
**Overall:** APPROVED
**Publish ref:** `sub/AST-1532/AST-1534-scoped-adhoc-runs-list-api` @ `2e0a22407ec816283877e5c3056a39e5e21a0934`

## Traceability
AC1→Stages 1–4; AC2→Stages 2–4 (API; UI refetch AST-1535); AC3→Stage 3; parent AC2/AC4→N/A (config-only / out of scope)

## Findings

### acceptable
- **Location:** Stage 2 — `INNER JOIN dispatch_ledger`
- **Finding:** Batches with `agent_data` but no ledger row are excluded.
- **Recommendation:** Acceptable — plan documents AST-1451 Ad Hoc Test always writes ledger; matches parent scoped-recent-runs intent.

- **Location:** Stage 1 — `adhoc_import_picker_visible_rows`
- **Finding:** Config key added here but not read by API in this ticket.
- **Recommendation:** Acceptable — parent Component scope assigns both literals to child #1; sibling AST-1535 consumes via `GET /api/system/ui_config`.

- **Location:** `docs/test-bible/**` (out of plan Files Changed)
- **Finding:** Bible still describes unfiltered/capped-less list path.
- **Recommendation:** Acceptable at plan gate — plan explicitly excludes `tests/` and bible; Betty owns qa-child manifest refresh.

## Notes
- Ticket status `Plan Ready` — valid entry gate.
- Assignee on Linear is Ada (not Joan); Chuckles spawn carries validate-plan authority for this pass.
- Zero completed `[plan-discuss]` rounds — no discuss tag required for APPROVED.
- Scope matches child `## Scope` and parent backend slice only; no frontend, no sibling creep.
- Layers: utils→data→core→ui; `@require_admin` preserved; cap from `UI_CONFIG` only (no client `limit`); filter/limit in data with API query params — conforms to `astral.layers.ui-config-driven-business-logic` and `pattern.ui.admin-endpoint`.
- `list_agent_data_batches` kwargs extension is safe — sole runtime caller is `list_agent_data_runs`; signature change is intentional retirement of unfiltered full-history for this path.
- `adhoc-` strip semantics (`substr(..., 7)` / Python `len("adhoc-")`) align with `run_adhoc_workbench_test` ledger vs stored task_key shapes.
- Self-assessment / Estimate confirm (2) matches footprint.

context_tokens≈42000
```

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-1532/AST-1534-scoped-adhoc-runs-list-api`  
**Product commit:** `31515387` — Stages 1–4 (`UI_CONFIG` caps, filtered `list_agent_data_batches`, `list_agent_data_runs` kwargs + debug, `GET /adhoc/runs` query params)

Frontend picker chrome left to AST-1535. Load path / Test prefix / `tests/` / bible untouched.
