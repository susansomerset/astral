# AST-1439 — Add "import agent data" to Agent Ad Hoc

**Component:** agent  
**Children:** AST-1451, AST-1452  
**Linear archived:** AST-1439 2026-09-09; AST-1451 2026-09-09; AST-1452 2026-09-09

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-19 09:35 | AST-1451 | docs | `f0f511714` | plan — Ad Hoc import list and load payload |
| 2026-08-19 09:41 | AST-1451 | docs | `fc30f05e0` | Joan validate — plan approved |
| 2026-08-19 09:43 | AST-1451 | code | `0990d1afd` | list agent_data batches newest first |
| 2026-08-19 09:44 | AST-1451 | docs | `05c4d57f4` | review stub after build |
| 2026-08-19 09:44 | AST-1451 | code | `5a1c95a5d` | admin GET adhoc runs list |
| 2026-08-19 09:44 | AST-1451 | code | `b378cd81f` | list runs debug and strip adhoc prefix |
| 2026-08-19 09:54 | AST-1451 | test | `7c28e1115` | cover Ad Hoc import list, load GET, and single adhoc- prefix |
| 2026-08-19 09:55 | AST-1451 | merge-tests | `b7d06892e` | origin/tests 7c28e1115a3850960a49c65d565e4ae46949800d |
| 2026-08-19 13:10 | AST-1451 | docs | `caa6e96bf` | Radia review — Clean read-path list |
| 2026-08-19 13:11 | AST-1451 | resolve | `3dcce39ce` | — clean |
| 2026-08-19 13:19 | AST-1452 | docs | `590f37461` | plan — ad hoc import picker and Load |
| 2026-08-19 13:23 | AST-1452 | docs | `441d2650c` | Joan validate — plan approved |
| 2026-08-19 13:25 | AST-1452 | code | `7a5d1f19c` | import run list and Load button |
| 2026-08-19 13:26 | AST-1452 | code | `5cd9cef27` | Load editors, skip catalog fetch, entity lock |
| 2026-08-19 13:27 | AST-1452 | docs | `c4f6883c3` | review stub after build |
| 2026-08-24 14:57 | AST-1452 | docs | `e1af196f0` | test bible — import picker/load manifest |
| 2026-08-24 14:57 | AST-1452 | test | `0637ea498` | Ad Hoc import picker and Load Vitest |
| 2026-08-24 14:58 | AST-1452 | merge-tests | `bb58525ce` | origin/tests e1af196f |
| 2026-08-24 15:04 | AST-1452 | docs | `b69e3ebfb` | Radia review — clean PROCEED |
| 2026-08-24 15:06 | AST-1452 | resolve | `8ccacb4f4` | — clean |
| 2026-08-24 15:08 | AST-1439 | sync | `c7377d2b7` | origin/ftr/AST-1439-add-import-agent-data-to-agent-ad-hoc |
| 2026-08-24 15:10 | AST-1439 | merge | `a0f80b6c6` | Merge remote-tracking branch 'origin/dev' into tmp-refresh-AST-1 |
| 2026-08-24 15:11 | AST-1439 | sync | `c137119ad` | origin/ftr/AST-1439-add-import-agent-data-to-agent-ad-hoc |
| 2026-09-09 17:55 | AST-1451 | docs | `4d39f7116` | archive Linear issue content |
| 2026-09-09 17:55 | AST-1452 | docs | `f4cc3055d` | archive Linear issue content |
| 2026-09-09 18:05 | AST-1439 | docs | `213481b92` | archive Linear issue content |

## Epic — AST-1439

_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1439/add-import-agent-data-to-agent-ad-hoc · Status at archive: Archive · Project: Astral Agent · Assignee: chuckles · Priority / estimate: High / 5_

### Purpose

Agent Ad Hoc can author a prompt from a catalog task, but it cannot pull a *past run* back onto the workbench. Operators who want to tweak something that already went to the model have to reconstruct it by hand from Execution History. This epic adds an import path: pick a stored `agent_data` run, load its prompt (and see its response if one exists), edit, and Test again — without rewriting the rows that were loaded. New Tests keep the existing `adhoc-<task_key>` audit label, including when the source run was itself an ad hoc Test.

### Functional scope

* **Pick a stored run.** Agent Ad Hoc shows a selection list of stored `agent_data` runs. Each row is one batch (not one block): timestamp, `entity_id`, and `task_key`. The list includes production hops and previous ad hoc Tests (`adhoc-*`). Newest first. No candidate filter, date filter, or display cap in this epic — the list is the table. When `debug=True` on the list path, logs show what was **found** and what was **recorded** per listed run (index header, timestamp / entity / task_key, outcome) using the AST-538 contract (`|` detail prefix; payloads >50 lines truncated 15 / omitted / 15). When `debug=False`, no new debug-contract lines.
* **Load copies into the session.** A Load control copies that batch’s prompt blocks into the seven Ad Hoc editors (System, Cache A–D, No Cache, User from the TASK block). Missing slots become empty so leftover editor text does not mix with the import. If a RESPONSE exists, it is shown with the existing agent_data panes for that batch. Load does not write `agent_data`. If the editors already have content, confirm replace the same way fetch-from-task does.
* **Edit and run without touching the source.** After Load, the operator edits and uses Preview / Test as today. Test does not send the imported response. Test writes a **new** batch. Source rows stay unchanged. Load sets the workbench task key to the source `task_key` with a single leading `adhoc-` stripped, so Test still records `adhoc-<task_key>` (AST-515) and does not double-prefix. That task-key update must not fetch catalog prompts over the imported editors. Load also restores the run’s `entity_id` into the session. Agent stays whatever the operator already selected (agent is not stored on `agent_data`).

### Architectural definition

* **Patterns to reuse**
  * `pattern.ui.admin-endpoint` — new list (and load, if not already covered by `GET /api/agent_data/<batch_id>`) is a thin authenticated admin route; React renders the resolved rows and does not query `agent_data` itself.
  * `pattern.ui.shared-button-roles` — Load is a labeled commit (`btn primary`); cancel on the replace-confirm is `btn secondary`; destructive-looking replace confirm matches the existing fetch-from-task pair.
  * `pattern.layers.import-discipline` — UI → core (or existing agent-data read helpers); core → data; no UI → data.
  * `pattern.config.config-block` — `BLOCK_TYPES` is the map from stored blocks onto editors and panes.
* **New patterns proposed** — none. Import is a workbench read of existing `agent_data` plus the existing Test writer.
* **Applicable statutes**
  * Universal set (`tier: universal`, `status: active`) — product epic.
  * `astral.idioms.require-auth-on-protected-endpoints` — new admin Ad Hoc routes stay authenticated (same family as current `/adhoc/*`).
  * `astral.layers.import-direction` / `astral.layers.ui-config-driven-business-logic` — list/load shaping in API/core; React renders.
  * `astral.standards.debug-contract-gated` — list found→recorded only when `debug=True`.
  * `astral.standards.dry-and-focused-functions` — reuse `GET /api/agent_data/<batch_id>` and `BatchAgentDataPanes` for block bodies and response display; do not fork a second inspector.
  * `astral.standards.in-scope-only` / `astral.standards.database-header-inventory` — `agent_data` only; no new table. A new list query still has to be a listed `agent_data` use.
  * `astral.standards.data-raises-caller-logs` / `astral.standards.logging-via-utils` — data raises; core/API logs.
  * `astral.standards.names-not-ticket-ids` / `astral.standards.no-hardcoded-sets` — domain names; block types from config.
  * `astral.ui.frontend-file-placement` / `astral.ui.naming-conventions` — stays on the existing Ad Hoc page; no nested page tree.
  * `astral.agent.do-task-delegation` — this is workbench import + existing `run_adhoc` Test, not a new `do_task` hop.

### Boundaries

* Does **not** edit, delete, or rewrite the loaded `agent_data` rows. Load is copy-into-editors only.
* Does **not** add filters, search, pagination, or a cap on the picker.
* Does **not** change Manage Tasks, production `do_task`, dispatch, `run_next`, Save As, or Execution History chrome.
* Does **not** add a Response editor tab. Response is display-only; Test ignores it.
* Does **not** persist which agent ran the source hop (not stored on `agent_data`).
* Does **not** snapshot historical live content as its own editor. Stored prompt blocks load as-is; Preview/Test then follow existing rules (including rebuilding live content from the **current** entity when a task and entity are selected). Clear the entity to send only the loaded text.
* Must **not** break: seven-segment editors (AST-1403), fetch-from-task, Preview modal, post-Test panes, Execution History `adhoc-<task_key>` rows, Preview-does-not-ledger.

### Acceptance criteria

1. Agent Ad Hoc shows a selection list whose rows are stored `agent_data` batches. Each visible row has timestamp, `entity_id`, and `task_key`. A production hop and an earlier Ad Hoc Test (`adhoc-<task_key>`) both appear. Newest first.
2. Load on a batch that has System + Cache A + User + Response fills those three editors, leaves Cache B–D and No Cache empty if those blocks were absent, and shows the stored Response in the existing agent_data panes for **that** batch. The source `agent_data` row contents are unchanged after Load.
3. After Load, editing User and running Test creates a **new** `agent_data` batch (new `batch_id`). The imported batch’s prompt and response blocks are bit-for-bit the same as before Test. The new ledger/task label is `adhoc-<task_key>` with a single `adhoc-` prefix even when the imported run was already `adhoc-<task_key>`.
4. Load of a run whose `task_key` is `evaluate_jd` (or `adhoc-evaluate_jd`) does not replace the imported editor text with catalog `agent_task` prompts for that key.
5. Load of a run that has an `entity_id` leaves that id selected for the next Preview/Test. Preview/Test still require an agent, same as today.
6. Load with dirty editors asks to replace (Yes / Cancel). Cancel leaves editors and panes as they were.
7. When `debug=True` on the list path, logs show a per-run index header plus found → recorded detail; when `debug=False`, listing adds no new debug-contract lines.

### Dependencies and blockers

* **AST-1403** (User Testing) — seven-segment Ad Hoc workbench, Preview modal, post-Test agent_data panes. This epic attaches to that page.
* **AST-514 / AST-515** (Done) — Test already writes ledger + `agent_data` as `adhoc-<task_key>`. This epic consumes that label; it does not invent a second one.

none blocking start (AST-1403 is already on `origin/dev`).

### Open questions

none

### Proposed child tickets


##### 1!: **Ad Hoc import list and load payload - Ada**

Own the read path: an authenticated admin list of `agent_data` runs (one row per batch: timestamp, `entity_id`, `task_key`, plus whatever identity Load needs — typically `batch_id`), including `adhoc-*` rows, newest first, no filter/cap. Load payload is that batch’s prompt blocks (and RESPONSE if present), via existing agent_data read helpers where they already return the blocks. When `debug=True`, list logs found → recorded per run. Does **not** own the picker chrome or editor mapping (#2). Does **not** change Test persist except as needed so a workbench task key of `adhoc-foo` still stores as `adhoc-foo` rather than `adhoc-adhoc-foo` (strip one leading `adhoc-` before applying the AST-515 prefix, or equivalent).
**Citations:** `pattern.ui.admin-endpoint`, `pattern.layers.import-discipline`, `pattern.config.config-block`, `astral.idioms.require-auth-on-protected-endpoints`, `astral.standards.debug-contract-gated`, `astral.standards.database-header-inventory`, `astral.standards.data-raises-caller-logs`
**Estimate: 3**

##### 2: **Ad Hoc import picker and Load - Hedy**

After #1. Agent Ad Hoc grows the selection list and a Load button. Load fills the seven editors from the payload (TASK → User; missing slots empty), shows RESPONSE via existing `BatchAgentDataPanes` for that batch, restores `entity_id`, sets the workbench task key with a single `adhoc-` stripped, and does **not** run fetch-from-task over the imported text. Dirty-editor replace confirm matches fetch-from-task. Does **not** own the list query (#1). Does **not** change Save As, Preview modal, or production `do_task`.
**Citations:** `pattern.ui.shared-button-roles`, `pattern.config.config-block`, `astral.ui.frontend-file-placement`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.dry-and-focused-functions`
**Estimate: 3**

---

### Original brief

Give me a selection list of timestamp, entity_id, and task_key from the agent_data table, and an "load" button, which will load the prompt content (with response, if we have one), and allow me to edit and run the prompt (ignoring the response) in the ad hoc session without changing the originally loaded agent_data content.  Include previous adhoc data from agent data, just add "adhoc-<task_key>"

#### Comments


##### chuckles — 2026-08-24T21:50:14.919Z

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered).

Replacement UUID: `ec6e0ee2-7688-4695-ab12-d31c98c6a1f8`.

Watcher rule `datt` on `AST-1439` (Thread owner `AST-1439`).

---

_Implementation detail may live in git history on `origin/dev`._

## Sub-issues

### AST-1451 — Ad Hoc import list and load payload

_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1451/ad-hoc-import-list-and-load-payload-add-import-agent-data-to-agent-ad · Status at archive: Archive · Project: Astral Agent · Assignee: ada · Priority / estimate: None / 3 · Blocked by / blocks / related: parent: AST-1439; blocks: AST-1452_

#### What this implements

Own the read path: an authenticated admin list of `agent_data` runs (one row per batch: timestamp, `entity_id`, `task_key`, plus whatever identity Load needs — typically `batch_id`), including `adhoc-*` rows, newest first, no filter/cap. Load payload is that batch’s prompt blocks (and RESPONSE if present), via existing agent_data read helpers where they already return the blocks. When `debug=True`, list logs found → recorded per run. Does **not** own the picker chrome or editor mapping (#2). Does **not** change Test persist except as needed so a workbench task key of `adhoc-foo` still stores as `adhoc-foo` rather than `adhoc-adhoc-foo` (strip one leading `adhoc-` before applying the AST-515 prefix, or equivalent).

#### Citations

`pattern.ui.admin-endpoint`, `pattern.layers.import-discipline`, `pattern.config.config-block`, `astral.idioms.require-auth-on-protected-endpoints`, `astral.standards.debug-contract-gated`, `astral.standards.database-header-inventory`, `astral.standards.data-raises-caller-logs`

#### Acceptance criteria

- [X] 1. Agent Ad Hoc shows a selection list whose rows are stored `agent_data` batches. Each visible row has timestamp, `entity_id`, and `task_key`. A production hop and an earlier Ad Hoc Test (`adhoc-<task_key>`) both appear. Newest first.
- [X] 2. After Load, editing User and running Test creates a **new** `agent_data` batch (new `batch_id`). The imported batch’s prompt and response blocks are bit-for-bit the same as before Test. The new ledger/task label is `adhoc-<task_key>` with a single `adhoc-` prefix even when the imported run was already `adhoc-<task_key>`.
- [X] 3. When `debug=True` on the list path, logs show a per-run index header plus found → recorded detail; when `debug=False`, listing adds no new debug-contract lines.

#### Boundaries

- [X] Does **not** own the picker chrome or editor mapping (sibling #2). Does **not** change Manage Tasks, production `do_task`, dispatch, Save As, or Execution History chrome. Does **not** edit, delete, or rewrite loaded `agent_data` rows.

#### Notes for planning

Citations as above. List is the `agent_data` table with no candidate/date filter or cap. Reuse existing agent_data read helpers for block bodies. Confirm Chuckles estimate: 3.

##### Comments


###### radia — 2026-08-19T20:10:35.641Z

[code-rubric] PROCEED (Commit: b7d06892) Clean read-path list

###### betty — 2026-08-19T16:56:11.145Z

`origin/sub/AST-1439/AST-1451-ad-hoc-import-list-and-load-payload` @ `b7d06892` · list load prefix tests

###### joan — 2026-08-19T16:41:03.221Z

[plan-rubric] PROCEED (Commit: f0f511714d010d4615a3f9f34c70a128d4aba013) list and load payload

###### ada — 2026-08-19T16:35:52.189Z

`origin/sub/AST-1439/AST-1451-ad-hoc-import-list-and-load-payload` @ `f0f51171` · plan published

---

#### Stage 1: Data — one row per batch, no cap

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

#### Stage 2: Core — list + debug + single `adhoc-` prefix

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

#### Stage 3: Admin list route

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

#### Estimate

Confirm Chuckles estimate: 3 — agree

Known admin-list + existing GET load + one prefix strip. Debug contract is mechanical (same Style D as `_store_prompt_blocks`). No schema migration, no frontend.

#### Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1451
**Overall:** APPROVED
**Publish-ref:** `origin/sub/AST-1439/AST-1451-ad-hoc-import-list-and-load-payload` @ `f0f511714d010d4615a3f9f34c70a128d4aba013`

##### Traceability

Child AC1→S1+S3; AC2→S2 one-prefix strip + no `agent_data` writes (Load body = existing `GET /api/agent_data/<batch_id>`); AC3→S2 debug gate. Parent AC2 editor/panes fill, AC4 no catalog overwrite, AC5 `entity_id` restore, AC6 dirty confirm = N/A — sibling AST-1452 / child Boundaries (“Does **not** own the picker chrome or editor mapping”).

R1–R3 (in-session): 18 universal considered, all `conforms`. 36 scoped considered, all `conforms` (auth via `@require_admin` which wraps `@require_auth`; list/load stay ui→core→data; header inventory updated on `agent_data`; debug only when `debug=True` via `get_logger`/`debug_index`/`debug_detail`; data raises, no data-layer logs; reuse existing batch GET, no second inspector). 10 scoped excluded (path/layer miss): `astral.debug.no-repo-root-artifacts-dir`, `astral.debug.spikes-under-debug-dir`, `astral.dispatch.seed-auto-false`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.layers.scripts-exempt-from-layer-rules`, `astral.seed.agent-tables-in-repo-json`, `astral.seed.archie-catalog-wins`, `astral.standards.utils-data-late-import-only`, `astral.ui.frontend-file-placement`. Cited patterns `pattern.ui.admin-endpoint`, `pattern.layers.import-discipline`, `pattern.config.config-block` are `status: approved` and match the plan shape. Estimate 3 is honest.

R6: plan matches the child definition (read path + Test prefix, not chrome). No `src/utils/config.py` change is justified (`BLOCK_TYPES` already complete). No frontend files. No claim/process/release or new `do_task` hop.

Findings: none (`fix-now` / `discuss`).

context_tokens≈48000

---

#### Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-1439/AST-1451-ad-hoc-import-list-and-load-payload`
**Product commits:** `0990d1af` (Stage 1 — `list_agent_data_batches`), `b378cd81` (Stage 2 — `list_agent_data_runs` debug + one `adhoc-` strip), `5a1c95a5` (Stage 3 — `GET /api/admin/adhoc/runs`)

Frontend picker, editor mapping, and `GET /api/agent_data/<batch_id>` left untouched.

#### Radia review

[code-rubric] revision=2
**Rubric:** code-rubric.v2
**Ticket:** AST-1451
**Publish ref:** `origin/sub/AST-1439/AST-1451-ad-hoc-import-list-and-load-payload` @ `b7d06892e954c4ac4fa525d36d89c0a2d50ffb6c`
**Overall:** CLEAN

#### Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | No agent confidence / grade-vector paths in AST-1451 product diff |
| astral.agent.do-task-delegation | scoped | not-applicable | No `do_task` delegation changes in AST-1451 commits |
| astral.agent.grade-vector-validation | scoped | not-applicable | No grade-vector validation touched |
| astral.batch.batch-id-first | scoped | conforms | Prefix strip preserves single `adhoc-<task_key>` batch id shape |
| astral.batch.batch-id-format | scoped | conforms | Workbench batch ids still `adhoc-<catalog_key>-<uuid>` |
| astral.batch.claim-process-release | scoped | not-applicable | No batch claim/release paths |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | List is metadata-only; no RESPONSE latest lookup |
| astral.config.config-source-of-truth | scoped | conforms | `TASK_CONFIG.get(catalog_task_key)` for entity_type after strip |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | No env/secret surface in AST-1451 product diff |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | No debug artifact dirs |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | No spike scripts |
| astral.dispatch.seed-auto-false | scoped | not-applicable | No dispatch seed changes in AST-1451 commits |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | No run_next / chain routing |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Issue doc at planned path |
| astral.git.betty-no-src-or-features | scoped | conforms | Product commits touch `src/` only; tests via Betty merge |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer product commits exclude `tests/`; Betty landed tests |
| astral.layers.core-vs-external-bright-line | scoped | conforms | No external layer involvement |
| astral.layers.import-direction | scoped | conforms | ui→core→data on list path; core→data import at module top |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | No `scripts/` changes in AST-1451 product commits |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Route is thin `jsonify(core)`; no UI business rules |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | No coat-check storage |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | No consult/render-verdict |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | `GET /api/admin/adhoc/runs` uses `@require_admin` (wraps `@require_auth`) |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | No seed JSON edits in AST-1451 commits |
| astral.seed.archie-catalog-wins | scoped | not-applicable | No catalog override |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | List is admin hot-path read, not boot seed |
| astral.seed.define-approved | scoped | not-applicable | No define/seed work |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | No operator seed rows |
| astral.seed.other-via-coverage-join | scoped | not-applicable | No coverage join |
| astral.standards.data-raises-caller-logs | scoped | conforms | `list_agent_data_batches` raises via `_run_with_retry`; no data-layer logging |
| astral.standards.database-header-inventory | scoped | conforms | `list_agent_data_batches` added to `agent_data` header inventory line |
| astral.standards.debug-contract-gated | scoped | conforms | Style D only when `debug=True`; found→recorded per batch row |
| astral.standards.dry-and-focused-functions | scoped | conforms | Small focused helpers; no duplicate list logic |
| astral.standards.in-scope-only | scoped | conforms | AST-1451 product footprint matches read-path + prefix strip only |
| astral.standards.logging-via-utils | scoped | conforms | `get_logger` from utils; no `print()` / raw `logging` |
| astral.standards.names-not-ticket-ids | scoped | conforms | Function/route names are domain-shaped |
| astral.standards.no-cross-contamination | scoped | conforms | No unrelated subsystem edits in AST-1451 product commits |
| astral.standards.no-hardcoded-sets | scoped | conforms | No new hardcoded state/task sets |
| astral.standards.public-then-helpers | scoped | conforms | Public list APIs before private helpers in file order |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | No utils→data late-import in AST-1451 product diff |
| astral.state.core-decides-transitions | scoped | not-applicable | No entity state transitions |
| astral.state.job-prior-states-enforced | scoped | not-applicable | No job state changes |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | No daisy-chain run paths |
| astral.ui.frontend-file-placement | scoped | not-applicable | AST-1451 product commits touch no `src/ui/frontend/**` |
| astral.ui.naming-conventions | scoped | conforms | `adhoc_runs` / `list_agent_data_runs` naming consistent |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | No server worker config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Betty `merge-tests` lands test manifest on publish ref |
| orch.git.commit-vocabulary | universal | conforms | `code` / `test` / `docs` commits use ticket vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Work on `sub/AST-1439/AST-1451-…`; no reverse flow |
| orch.git.ftr-sub-topology | universal | conforms | Child `sub/<parent>/<child>` topology |
| orch.git.merge-on-checkout | universal | conforms | `sync(dev)` present on branch history |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No forbidden git ops observed |
| orch.git.no-dev-agent-branches | universal | conforms | No agent-named dev branches |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Epic worktree `astral-AST-1439` |
| orch.git.three-permanent-branches | universal | conforms | Diff baseline `origin/dev` |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | No unresolved product forks in AST-1451 scope |
| orch.pipeline.plan-is-bible | universal | conforms | Implementation matches staged plan for this ticket |
| orch.pipeline.project-scoped-queues | universal | conforms | Ticket scoped to AST-1439 epic |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review at Tests Passed per pipeline |
| orch.roles.archie-approves-statutes | universal | conforms | Joan APPROVED plan; patterns approved |
| orch.roles.betty-owns-test-tree | universal | conforms | Tests landed via Betty merge, not engineer product commits |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee Ada through Tests Passed |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Engineer remains assignee at Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | No banned-path commits in AST-1451 product set |

(62 rows scored from active registry tables; corpus reports 65 active — remainder are exemplar duplicates of rows above.)

#### Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.ui.admin-endpoint | conforms | Thin admin route; `@require_admin`; core list; no data/external from ui |
| pattern.layers.import-discipline | conforms | Module-top imports; ui→core→data chain on list path |
| pattern.config.config-block | not-applicable | No config-block / `BLOCK_TYPES` changes (plan N/A) |

#### Plan adherence

AST-1451 product commits (`0990d1af`, `b378cd81`, `5a1c95a5`) match all three plan stages:

- **Stage 1:** `list_agent_data_batches()` — `GROUP BY batch_id`, `ORDER BY created_at DESC`, metadata keys only, header inventory updated.
- **Stage 2:** `list_agent_data_runs` with gated Style D; one leading `adhoc-` strip + `catalog_task_key` for `TASK_CONFIG` in `run_adhoc_workbench_test`.
- **Stage 3:** `GET /api/admin/adhoc/runs` with `@require_admin`, `ui_llm_debug()`, no query filters.

Boundaries held on product commits: no frontend, no new load route, no `agent_data` writes on list path, no `config.py` edits. Load contract remains existing `GET /api/agent_data/<batch_id>` (bible points Betty manifest to existing `TestSystemAuthRoutes::test_agent_data_returns_rows` — appropriate regression, not a new test).

Estimate 3 still honest for AST-1451 footprint.

Joan plan-rubric verdict attached (APPROVED). No straggler: excluded statutes remain `not-applicable` on AST-1451 product diff; `astral.standards.database-header-inventory` was considered (not excluded) at plan time.

**Branch context:** Three-dot diff `origin/dev…publish-ref` includes substantial sibling epic work (frontend, config, other `agent.py` / `api_admin.py` hunks). That rollup is expected on the shared sub tip; it is **not** attributable to AST-1451 product commits. Findings below are scoped to AST-1451 unless noted as branch-level advisory.

#### Findings


##### fix-now

(none)

##### discuss

(none)

##### advisory

- **Branch hygiene (sibling):** `src/data/database.py` imports `is_valid_candidate_batch_claim_state` twice (lines ~81 and ~100) — duplicate from sibling merge, not AST-1451 commits; harmless at runtime but worth cleaning on a sibling touch.
- **List semantics (plan-approved):** Global unfiltered `agent_data` batch list with `MAX(entity_id)` / `MAX(task_key)` aggregation — intentional per plan Decision; operators should expect production + adhoc rows and lexicographic `MAX(entity_id)` when a batch has multiple stamped ids.

#### What's solid

- Read path is thin and layered: admin route → core list → data aggregation, no `block_data` on list.
- Debug contract is correctly gated and mechanical (index per batch, found→recorded, no `debug_detail_block` on short metadata).
- Prefix strip is exactly one `adhoc-`, with test locking ledger `task_key` and batch id shape.
- Betty manifest covers data list, core debug gate, admin auth, prefix strip, and existing load GET regression.

#### Frame diff

(none) — implementation matches the approved plan stages; no material plan frame drift for AST-1451.

#### Notes

- Joan plan-rubric verdict attached (APPROVED @ `f0f51171`).
- Load GET coverage is via existing `test_api_system` test per bible — no new load test required for this ticket.
- §5f / §5g not triggered on AST-1451 product diff (debug on list path conforms §5f; no external/LLM module changes).

context_tokens≈52000

#### Resolution (2026-08-19 — resolve-child)

**Review ref:** Radia `[code-rubric] PROCEED` + plan `## Radia review` @ `caa6e96b` (CLEAN).

| Item | Action |
|------|--------|
| fix-now | None |
| discuss | None |
| advisory — duplicate `is_valid_candidate_batch_claim_state` import | Left as sibling merge residue; not an AST-1451 product change |
| advisory — `MAX(entity_id)` list semantics | Plan-approved; no code change |

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/data/database.py` | Add `list_agent_data_batches`; name it on the `agent_data` h | `0990d1afd` |
| ✓ | `src/core/agent.py` | Add `list_agent_data_runs` (debug found→recorded); strip one | `b378cd81f` |
| ✓ | `src/ui/api/api_admin.py` | Add `GET /api/admin/adhoc/runs` (`@require_admin`) calling c | `5a1c95a5d` |
| | _tests_ | — | 3 file(s) |

### AST-1452 — Ad Hoc import picker and Load

_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1452/ad-hoc-import-picker-and-load-add-import-agent-data-to-agent-ad-hoc · Status at archive: Archive · Project: Astral Agent · Assignee: hedy · Priority / estimate: None / 3 · Blocked by / blocks / related: parent: AST-1439_

#### What this implements

After #1. Agent Ad Hoc grows the selection list and a Load button. Load fills the seven editors from the payload (TASK → User; missing slots empty), shows RESPONSE via existing `BatchAgentDataPanes` for that batch, restores `entity_id`, sets the workbench task key with a single `adhoc-` stripped, and does **not** run fetch-from-task over the imported text. Dirty-editor replace confirm matches fetch-from-task. Does **not** own the list query (#1). Does **not** change Save As, Preview modal, or production `do_task`.

#### Citations

`pattern.ui.shared-button-roles`, `pattern.config.config-block`, `astral.ui.frontend-file-placement`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.dry-and-focused-functions`

#### Acceptance criteria

- [X] 2. Load on a batch that has System + Cache A + User + Response fills those three editors, leaves Cache B–D and No Cache empty if those blocks were absent, and shows the stored Response in the existing agent_data panes for **that** batch. The source `agent_data` row contents are unchanged after Load.
- [X] 3. After Load, editing User and running Test creates a **new** `agent_data` batch (new `batch_id`). The imported batch’s prompt and response blocks are bit-for-bit the same as before Test. The new ledger/task label is `adhoc-<task_key>` with a single `adhoc-` prefix even when the imported run was already `adhoc-<task_key>`.
- [X] 4. Load of a run whose `task_key` is `evaluate_jd` (or `adhoc-evaluate_jd`) does not replace the imported editor text with catalog `agent_task` prompts for that key.
- [X] 5. Load of a run that has an `entity_id` leaves that id selected for the next Preview/Test. Preview/Test still require an agent, same as today.
- [X] 6. Load with dirty editors asks to replace (Yes / Cancel). Cancel leaves editors and panes as they were.

#### Boundaries

- [X] Does **not** own the list query (sibling #1). Does **not** change Save As, Preview modal, or production `do_task`. Does **not** add filters, search, pagination, or a Response editor tab.

#### Notes for planning

Citations as above. After sibling #1. Confirm Chuckles estimate: 3.

##### Comments


###### hedy — 2026-08-24T22:06:46.329Z

origin/sub/AST-1439/AST-1452-ad-hoc-import-picker-and-load @ `c83d1c5e` · §9a clean · ftr dry-run clean

###### radia — 2026-08-24T22:04:06.965Z

[code-rubric] PROCEED (Commit: bb58525) Ad hoc import picker clean

###### betty — 2026-08-24T21:58:35.794Z

origin/sub/AST-1439/AST-1452-ad-hoc-import-picker-and-load @ `bb58525c` · import picker Vitest manifest

###### joan — 2026-08-19T20:23:10.615Z

[plan-rubric] PROCEED (Commit: 590f37461b21e84ed5012792785cf6a98e5dfa66) picker and Load UI

###### hedy — 2026-08-19T20:19:29.716Z

`origin/sub/AST-1439/AST-1452-ad-hoc-import-picker-and-load` @ `590f37461b21e84ed5012792785cf6a98e5dfa66` · picker Load plan

---

#### Stage 1: Import list on Agent Ad Hoc

**Done when:** Opening Agent Ad Hoc as an admin loads `GET /api/admin/adhoc/runs` once and renders every returned row in a `list-page-table` (columns: timestamp = `created_at`, `entity_id`, `task_key`) with no filter, search, pagination, or row cap. Clicking a row selects it (visual selected state). Empty array → table headers plus empty tbody (no placeholder rows). Failed list GET → existing `Toast` error; table stays empty. `npx tsc --noEmit` in `src/ui/frontend` passes.

1. In `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx`, add this type next to `EntityMeta`:
```ts
interface ImportRun {
  batch_id: string
  created_at: string | null
  entity_id: string | null
  task_key: string | null
}
```

2. In `AnthropicAdHoc`, add state:
```ts
const [importRuns, setImportRuns] = useState<ImportRun[]>([])
const [selectedImportBatchId, setSelectedImportBatchId] = useState<string>("")
```

3. Add a `useEffect` with `[]` deps (mount once) that calls `api("/api/admin/adhoc/runs")`, then `r.ok ? r.json() : Promise.reject(new Error(...))`, then `setImportRuns(Array.isArray(d) ? d : [])`. On catch, `setToast({ text: e.message, variant: "error" })` and leave `importRuns` as `[]`. Do **not** pass query params. Do **not** slice/limit the array.

4. In the JSX, **above** the `{/* ── Action buttons ── */}` block (after the entity-meta row), insert:
```tsx
      <div className="list-page-table-wrap" style={{ marginBottom: 16, maxHeight: "none" }}>
        <table className="list-page-table">
          <thead>
            <tr>
              <th>timestamp</th>
              <th>entity_id</th>
              <th>task_key</th>
            </tr>
          </thead>
          <tbody>
            {importRuns.map(run => (
              <tr
                key={run.batch_id}
                className="clickable"
                onClick={() => setSelectedImportBatchId(run.batch_id)}
                style={selectedImportBatchId === run.batch_id ? { background: "var(--bg-card)" } : undefined}
              >
                <td>{run.created_at ?? ""}</td>
                <td>{run.entity_id ?? ""}</td>
                <td>{run.task_key ?? ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
```

   Render `created_at` / `entity_id` / `task_key` as the API strings (empty cell when null). Do **not** add filters, search inputs, “showing N of M”, or `slice`. Do **not** add a new CSS class in `App.css`.

5. In the action-buttons row, **before** the Preview button, add:
```tsx
        <button
          className="btn primary"
          disabled={!selectedImportBatchId}
          onClick={() => { /* Stage 2 wires this */ }}
        >
          Load
        </button>
```

   Leave `onClick` as a no-op function `() => {}` until Stage 2 (button still disabled when nothing is selected). Do **not** change Preview / Test / Save As handlers in this stage.

⚠️ **Decision:** Full unfiltered table (parent: “the list is the table”), not a `<select>`. No `maxHeight`/`overflow` cap on the wrap — parent forbids a display cap.

#### Stage 2: Load into editors, panes, task key, entity, confirm

**Done when:** Load of a selected batch fills System / Cache A–D / No Cache / User from SYSTEM / CACHE_A–D / NO_CACHE / TASK `block_data` (missing types → `""`), does not put RESPONSE into an editor, and shows `BatchAgentDataPanes` for **that** `batch_id`. Source rows are only read (GET). Workbench Task Key becomes the run’s `task_key` with a **single** leading `adhoc-` stripped, and the taskKey effect does **not** call `doFetchFrom` / `setConfirmFetch` for that set. If the run has `entity_id`, the next Preview/Test POST sends that id as `entity_id` and omits `entity_ids`. Dirty seven-editor content shows the same Yes, Replace (`btn danger`) / Cancel (`btn secondary`) banner family as fetch-from-task; Cancel leaves editors, `testBatchId`/panes, task key, and entity lock unchanged. `npx tsc --noEmit` in `src/ui/frontend` passes.

1. Add helpers **inside** `AnthropicAdHoc` (after `previewField` is not available inside — place them as inner functions after `hasContent`):
```ts
  function stripOneAdhocPrefix(raw: string): string {
    const s = (raw || "").trim()
    return s.startsWith("adhoc-") ? s.slice("adhoc-".length) : s
  }

  function textOfBlocks(blocks: { block_type?: string; block_data?: string }[], blockType: string): string {
    return blocks
      .filter(b => b.block_type === blockType)
      .map(b => (typeof b.block_data === "string" ? b.block_data : ""))
      .join("\n\n")
  }
```

   Strip **one** prefix only (no while-loop). `textOfBlocks` returns `""` when no blocks of that type.

2. Add refs/state:
```ts
  const skipCatalogFetchRef = useRef(false)
  const [importEntityLock, setImportEntityLock] = useState<string | null>(null)
  const [confirmLoad, setConfirmLoad] = useState<string | null>(null)
```

   `importEntityLock`: `null` = not in import-entity mode (Preview/Test use today’s batch vs single logic). Non-null string (including `""`) = Load restored that `entity_id` and Preview/Test must send it as a single entity.

3. In the `useEffect` that depends on `[taskKey, selectedId]` (comment `{/* When task key changes, load entity list + prompts */}`), **keep** the `adhoc/entities` fetch exactly as today. After the `isInitialMount` early return, add **before** `const existing = tasks.find(...)`:
```ts
    if (skipCatalogFetchRef.current) {
      skipCatalogFetchRef.current = false
      return
    }
```

   That return skips `setConfirmFetch` and `doFetchFrom` only. It must **not** skip the entities `api(...)` call above it.

4. On the Task Key `<select>`, change `onChange` to:
```ts
onChange={e => { setImportEntityLock(null); setTaskKey(e.target.value) }}
```

   On the entity `<select>` (non-batch branch), wrap `setEntityId` with `setImportEntityLock(null)` then `setEntityId`. On the batchCount `<input>`, wrap with `setImportEntityLock(null)` then existing `setBatchCount`. Do **not** clear the lock when `setTaskKey` is called from `doLoad`.

5. Replace `handlePreview` / `handleTest` body field `entity_id` / `entity_ids` with:
```ts
        entity_id: importEntityLock !== null
          ? importEntityLock
          : (entityMeta_batchIds ? "" : (entityId || "")),
        entity_ids: importEntityLock !== null ? undefined : (entityMeta_batchIds || undefined),
```

   Agent-required checks stay unchanged (`if (!agentId) { setToast...; return }`). Do **not** change Preview modal JSX, tab list, or `/api/admin/adhoc/preview` / `test` URLs.

6. Implement `doLoad(batchId: string)`:
```ts
  function doLoad(batchId: string) {
    setConfirmLoad(null)
    api(`/api/agent_data/${encodeURIComponent(batchId)}`)
      .then(r => {
        if (!r.ok) return r.json().then(e => { throw new Error(e.error || `HTTP ${r.status}`) })
        return r.json()
      })
      .then(data => {
        const blocks = Array.isArray(data) ? data : []
        setSystemPrompt(textOfBlocks(blocks, "SYSTEM"))
        setCachePrompt(textOfBlocks(blocks, "CACHE_A"))
        setCachePromptB(textOfBlocks(blocks, "CACHE_B"))
        setCachePromptC(textOfBlocks(blocks, "CACHE_C"))
        setCachePromptD(textOfBlocks(blocks, "CACHE_D"))
        setNocachePrompt(textOfBlocks(blocks, "NO_CACHE"))
        setUserPrompt(textOfBlocks(blocks, "TASK"))
        const run = importRuns.find(r => r.batch_id === batchId)
        const catalog = stripOneAdhocPrefix(run?.task_key || "")
        if (catalog !== taskKey) {
          skipCatalogFetchRef.current = true
          setTaskKey(catalog)
        }
        const restoredEntity = run?.entity_id == null ? "" : String(run.entity_id)
        setEntityId(restoredEntity)
        setImportEntityLock(restoredEntity)
        setTestBatchId(batchId)
        setToast({ text: `Loaded agent data ${batchId}`, variant: "success" })
      })
      .catch(e => setToast({ text: e.message, variant: "error" }))
  }
```

   Do **not** call `doFetchFrom`. Do **not** write `agentId`. Do **not** PUT/POST `agent_data`. If `task_key` after strip is not in `taskKeysSorted`, still `setTaskKey(catalog)` (the select will show the raw value if the browser keeps it; do **not** add a fake catalog fetch). FEEDBACK / RESPONSE are not assigned to the seven editors.

7. `handleLoadClick`:
```ts
  function handleLoadClick() {
    if (!selectedImportBatchId) return
    if (hasContent) setConfirmLoad(selectedImportBatchId)
    else doLoad(selectedImportBatchId)
  }
```

   Wire the Stage 1 Load button `onClick={handleLoadClick}`.

8. Next to the existing `{confirmFetch && (...)}` banner, add a **same-structure** banner for `confirmLoad`:

- Gold border card, copy: `Replace current prompt content with imported run?`
- `button className="btn danger"` → `onClick={() => doLoad(confirmLoad)}` labeled `Yes, Replace`
- `button className="btn secondary"` → `onClick={() => setConfirmLoad(null)}` labeled `Cancel`

   Cancel must not call `doLoad`, must not change `testBatchId`, editors, `taskKey`, or `importEntityLock`.

9. If `entityMeta` is showing and `entityId` is non-empty and that id is **not** in `entityMeta.entities`, append `{ id: entityId, label: entityId }` to the mapped `<option>` list (non-batch select only) so the restored id remains visible/selected. Do **not** invent extra entity rows when the id is already in the list.

⚠️ **Decision:** Skip catalog fetch with `skipCatalogFetchRef`, not by leaving Task Key blank. AC4 is “do not replace imported editor text with catalog `agent_task` prompts”; the dropdown still needs the catalog key so Test records `adhoc-<task_key>` (AST-1451 already strips a second `adhoc-` if the posted key is prefixed).

⚠️ **Decision:** `importEntityLock` rather than changing global batch_mode Preview/Test. Today batch_mode ignores `entityId` and sends `entity_ids`. AC5 requires the loaded run’s `entity_id` on the next Preview/Test; the lock does that until the operator changes Task Key, entity select, or First-N.

#### Estimate

Confirm Chuckles estimate: 3 — agree

One page, existing GET + `BatchAgentDataPanes`, confirm cloned from fetch-from-task, one skip-fetch ref. No new routes or schema.

#### Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1452
**Overall:** APPROVED
**Publish-ref:** `origin/sub/AST-1439/AST-1452-ad-hoc-import-picker-and-load` @ `590f37461b21e84ed5012792785cf6a98e5dfa66`

##### Traceability

AC2→S2 editor fill + `BatchAgentDataPanes` on imported `batch_id`; AC3→S2 task-key strip + no catalog fetch (Test prefix = AST-1451); AC4→S2 `skipCatalogFetchRef`; AC5→S2 `importEntityLock` + entity option append; AC6→S2 `confirmLoad` banner. Parent AC1 list chrome→S1 table + row select (data from AST-1451 `GET /api/admin/adhoc/runs`); parent AC7 debug list→N/A (sibling #1).

R1–R3 (in-session): 18 universal considered, all `conforms`. 18 scoped considered, all `conforms` (single `ui` page edit; reuses `BatchAgentDataPanes` + fetch-from-task confirm shape; `btn primary` / `btn danger` / `btn secondary`; block-type strings match existing `BatchAgentDataModal` `BLOCK_TYPE_ORDER`; no new routes/API; `importEntityLock` is presentation/session state, not duplicated catalog rules). 28 scoped excluded (no `src/core`/`data`/scripts/docs touch). Cited patterns `pattern.ui.shared-button-roles`, `pattern.config.config-block`, all `status: approved` and match plan shape. Sibling contract for list/load GET is explicit; does not reimplement AST-1451.

R6: faithful to child definition (picker + Load only). Boundaries respected (no list query, no Save As/Preview chrome, no `do_task`). `skipCatalogFetchRef` placement matches existing `taskKey` effect (`isInitialMount` return first, then skip, then `confirmFetch`/`doFetchFrom`). Estimate 3 is honest.

Findings: none (`fix-now` / `discuss`).

context_tokens≈58000

#### Review stub (Hedy / build)

**Publish ref:** `origin/sub/AST-1439/AST-1452-ad-hoc-import-picker-and-load`
**Product commits:** `7a5d1f19` (Stage 1 — import run list + Load button), `5cd9cef2` (Stage 2 — editor mapping, skip catalog fetch, entity lock, replace confirm)

No API or `config.py` edits. List source remains `GET /api/admin/adhoc/runs`; Load body remains `GET /api/agent_data/<batch_id>`; panes reuse `BatchAgentDataPanes`.

#### Radia review

```
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1452
**Publish ref:** origin/sub/AST-1439/AST-1452-ad-hoc-import-picker-and-load @ bb58525ce540f117af1fd662b9b43c093f408500
**Overall:** CLEAN
```

Full-set statute sweep: 64 active rows — all conforms or not-applicable. Pattern conformance: `pattern.ui.shared-button-roles`, `pattern.config.config-block` — conforms. Plan adherence: Stage 1 list + Load button; Stage 2 editor mapping, panes, adhoc- strip, skip catalog fetch, entity lock, dirty confirm — matches plan. Sibling boundary (AST-1451) respected.

##### fix-now

(none)

##### discuss

(none)

##### advisory

1. merge-tests footprint includes sibling AST-1451 tests — product review footprint is `AdminAnthropicAdHoc.tsx` only.
2. Dual confirm banners (fetch + load) could both render if both flags set — unlikely in practice.

context_tokens≈72000

#### Resolution

**2026-08-24** — Radia **CLEAN** / Linear `[code-rubric] PROCEED` @ `bb58525c`. No `fix-now` or `discuss`. Advisories left as-is (merge-tests sibling footprint noted; dual-banner edge left without product change). `resolve(AST-1452): — clean` on publish ref after Radia `docs()` intake; §9a dry-run vs `origin/dev` before User Testing.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx` | Import list table, Load, editor mapping, skip catalog fetch, | `5cd9cef27` `7a5d1f19c` |
| | _tests_ | — | 1 file(s) |
