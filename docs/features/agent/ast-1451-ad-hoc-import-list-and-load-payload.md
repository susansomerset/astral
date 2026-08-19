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

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1451
**Overall:** APPROVED
**Publish-ref:** `origin/sub/AST-1439/AST-1451-ad-hoc-import-list-and-load-payload` @ `f0f511714d010d4615a3f9f34c70a128d4aba013`

### Traceability
Child AC1→S1+S3; AC2→S2 one-prefix strip + no `agent_data` writes (Load body = existing `GET /api/agent_data/<batch_id>`); AC3→S2 debug gate. Parent AC2 editor/panes fill, AC4 no catalog overwrite, AC5 `entity_id` restore, AC6 dirty confirm = N/A — sibling AST-1452 / child Boundaries (“Does **not** own the picker chrome or editor mapping”).

R1–R3 (in-session): 18 universal considered, all `conforms`. 36 scoped considered, all `conforms` (auth via `@require_admin` which wraps `@require_auth`; list/load stay ui→core→data; header inventory updated on `agent_data`; debug only when `debug=True` via `get_logger`/`debug_index`/`debug_detail`; data raises, no data-layer logs; reuse existing batch GET, no second inspector). 10 scoped excluded (path/layer miss): `astral.debug.no-repo-root-artifacts-dir`, `astral.debug.spikes-under-debug-dir`, `astral.dispatch.seed-auto-false`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.layers.scripts-exempt-from-layer-rules`, `astral.seed.agent-tables-in-repo-json`, `astral.seed.archie-catalog-wins`, `astral.standards.utils-data-late-import-only`, `astral.ui.frontend-file-placement`. Cited patterns `pattern.ui.admin-endpoint`, `pattern.layers.import-discipline`, `pattern.config.config-block` are `status: approved` and match the plan shape. Estimate 3 is honest.

R6: plan matches the child definition (read path + Test prefix, not chrome). No `src/utils/config.py` change is justified (`BLOCK_TYPES` already complete). No frontend files. No claim/process/release or new `do_task` hop.

Findings: none (`fix-now` / `discuss`).

context_tokens≈48000

---

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-1439/AST-1451-ad-hoc-import-list-and-load-payload`  
**Product commits:** `0990d1af` (Stage 1 — `list_agent_data_batches`), `b378cd81` (Stage 2 — `list_agent_data_runs` debug + one `adhoc-` strip), `5a1c95a5` (Stage 3 — `GET /api/admin/adhoc/runs`)

Frontend picker, editor mapping, and `GET /api/agent_data/<batch_id>` left untouched.

## Radia review

[code-rubric] revision=2
**Rubric:** code-rubric.v2
**Ticket:** AST-1451
**Publish ref:** `origin/sub/AST-1439/AST-1451-ad-hoc-import-list-and-load-payload` @ `b7d06892e954c4ac4fa525d36d89c0a2d50ffb6c`
**Overall:** CLEAN

## Statutes checked

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

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.ui.admin-endpoint | conforms | Thin admin route; `@require_admin`; core list; no data/external from ui |
| pattern.layers.import-discipline | conforms | Module-top imports; ui→core→data chain on list path |
| pattern.config.config-block | not-applicable | No config-block / `BLOCK_TYPES` changes (plan N/A) |

## Plan adherence

AST-1451 product commits (`0990d1af`, `b378cd81`, `5a1c95a5`) match all three plan stages:

- **Stage 1:** `list_agent_data_batches()` — `GROUP BY batch_id`, `ORDER BY created_at DESC`, metadata keys only, header inventory updated.
- **Stage 2:** `list_agent_data_runs` with gated Style D; one leading `adhoc-` strip + `catalog_task_key` for `TASK_CONFIG` in `run_adhoc_workbench_test`.
- **Stage 3:** `GET /api/admin/adhoc/runs` with `@require_admin`, `ui_llm_debug()`, no query filters.

Boundaries held on product commits: no frontend, no new load route, no `agent_data` writes on list path, no `config.py` edits. Load contract remains existing `GET /api/agent_data/<batch_id>` (bible points Betty manifest to existing `TestSystemAuthRoutes::test_agent_data_returns_rows` — appropriate regression, not a new test).

Estimate 3 still honest for AST-1451 footprint.

Joan plan-rubric verdict attached (APPROVED). No straggler: excluded statutes remain `not-applicable` on AST-1451 product diff; `astral.standards.database-header-inventory` was considered (not excluded) at plan time.

**Branch context:** Three-dot diff `origin/dev…publish-ref` includes substantial sibling epic work (frontend, config, other `agent.py` / `api_admin.py` hunks). That rollup is expected on the shared sub tip; it is **not** attributable to AST-1451 product commits. Findings below are scoped to AST-1451 unless noted as branch-level advisory.

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Branch hygiene (sibling):** `src/data/database.py` imports `is_valid_candidate_batch_claim_state` twice (lines ~81 and ~100) — duplicate from sibling merge, not AST-1451 commits; harmless at runtime but worth cleaning on a sibling touch.
- **List semantics (plan-approved):** Global unfiltered `agent_data` batch list with `MAX(entity_id)` / `MAX(task_key)` aggregation — intentional per plan Decision; operators should expect production + adhoc rows and lexicographic `MAX(entity_id)` when a batch has multiple stamped ids.

## What's solid

- Read path is thin and layered: admin route → core list → data aggregation, no `block_data` on list.
- Debug contract is correctly gated and mechanical (index per batch, found→recorded, no `debug_detail_block` on short metadata).
- Prefix strip is exactly one `adhoc-`, with test locking ledger `task_key` and batch id shape.
- Betty manifest covers data list, core debug gate, admin auth, prefix strip, and existing load GET regression.

## Frame diff

(none) — implementation matches the approved plan stages; no material plan frame drift for AST-1451.

## Notes

- Joan plan-rubric verdict attached (APPROVED @ `f0f51171`).
- Load GET coverage is via existing `test_api_system` test per bible — no new load test required for this ticket.
- §5f / §5g not triggered on AST-1451 product diff (debug on list path conforms §5f; no external/LLM module changes).

context_tokens≈52000

