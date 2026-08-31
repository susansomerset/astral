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

## Radia review

# Radia review — AST-1534

**Publish ref:** `origin/sub/AST-1532/AST-1534-scoped-adhoc-runs-list-api` @ `59ed7f520a0ebc7e98ba21b22b4139ba153cc582`  
**Baseline:** `origin/dev`  
**Status gate:** Tests Passed (spawn prompt — trusted)

---

```
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1534
**Publish ref:** 59ed7f520a0ebc7e98ba21b22b4139ba153cc582
**Overall:** FIX-NOW
```

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | core/agent.py touched but no confidence/scoring logic changed |
| astral.agent.do-task-delegation | scoped | not-applicable | no do_task / delegation path edits |
| astral.agent.grade-vector-validation | scoped | not-applicable | no vector validation changes |
| astral.batch.batch-id-first | scoped | not-applicable | list query only; no batch-id creation/claim ordering change |
| astral.batch.batch-id-format | scoped | not-applicable | no batch_id format logic |
| astral.batch.claim-process-release | scoped | not-applicable | no claim/process/finally clear helpers |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no entity-agent response selection logic |
| astral.config.config-source-of-truth | scoped | conforms | cap/visible-rows live in `UI_CONFIG`; handler reads config not literals |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no secrets/env wiring |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug artifacts |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no spikes |
| astral.dispatch.seed-auto-false | scoped | not-applicable | dispatcher/config seed-auto untouched |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no run-next / chain edits |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single `docs/features/interface/ast-1534-*.md` |
| astral.git.betty-no-src-or-features | scoped | conforms | src/features edits are engineer commits, not Betty |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer product commit `31515387` does not touch `tests/**` |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | external layer unchanged |
| astral.layers.import-direction | scoped | conforms | ui→core→data; utils config import only |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts/** changes |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | list cap from `UI_CONFIG["adhoc_import_runs_limit"]`; query params are filters not business rules |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check storage |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no render/consult orchestration |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | `@require_admin` preserved on `/adhoc/runs` |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no admin JSON / bootstrap seed edits |
| astral.seed.archie-catalog-wins | scoped | not-applicable | dispatcher catalog untouched |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no boot-path seed |
| astral.seed.define-approved | scoped | not-applicable | no define/seed approval flow |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no operator-row seed deletes |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no coverage-join seed logic |
| astral.standards.data-raises-caller-logs | scoped | conforms | `list_agent_data_batches` raises via `_run_with_retry`; no data-layer logging added |
| astral.standards.database-header-inventory | scoped | conforms | header still lists `list_agent_data_batches` on agent_data line |
| astral.standards.debug-contract-gated | scoped | conforms | Style D gated on `debug=True`; per-row index + found/recorded details |
| astral.standards.dry-and-focused-functions | scoped | conforms | kwargs extension in place; thin route handler |
| astral.standards.in-scope-only | scoped | conforms | src/** limited to planned four modules + adhoc config keys |
| astral.standards.logging-via-utils | scoped | conforms | `get_logger` in core; no new stdlib logging |
| astral.standards.names-not-ticket-ids | scoped | conforms | runtime names are domain terms; AST comment is ticket trace only |
| astral.standards.no-cross-contamination | scoped | conforms | no out-of-layer src imports |
| astral.standards.no-hardcoded-sets | scoped | conforms | 10/5 are config literals not duplicated magic in handler/SQL |
| astral.standards.public-then-helpers | scoped | conforms | public list helpers unchanged ordering |
| astral.standards.utils-data-late-import-only | scoped | conforms | config.py change is dict literals only |
| astral.state.core-decides-transitions | scoped | not-applicable | no state transition decisions |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job state enforcement |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no run daisy-chain |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend changes |
| astral.ui.naming-conventions | scoped | conforms | existing admin route naming preserved |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no worker/config deployment change |
| orch.git.betty-merge-tests-one-sha | universal | conforms | single `merge-tests(AST-1534)` on sub |
| orch.git.commit-vocabulary | universal | conforms | commit prefixes match ticket ids |
| orch.git.flow-direction-inviolable | universal | conforms | sub branch off dev; no reverse merge |
| orch.git.ftr-sub-topology | universal | conforms | correct `sub/AST-1532/AST-1534-*` publish ref |
| orch.git.merge-on-checkout | universal | conforms | no checkout merge violations observed |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | linear commits + one merge-tests |
| orch.git.no-dev-agent-branches | universal | conforms | no agent-named dev branches |
| orch.git.one-epic-worktree-per-parent | universal | conforms | AST-1532 epic worktree |
| orch.git.three-permanent-branches | universal | conforms | dev/sub topology respected |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | no product-policy bypass |
| orch.pipeline.plan-is-bible | universal | needs-discussion | product matches plan; test/bible diff includes AST-1537 hunks outside Files Changed |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Interface child reviewed in isolation |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed gate honored |
| orch.roles.archie-approves-statutes | universal | conforms | no canon statute edits |
| orch.roles.betty-owns-test-tree | universal | violates | AST-1537 test/bible hunks landed on AST-1534 publish ref |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | no Chuckles assignment flip |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada remains implementer |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path commits observed |

**Active set scored:** 65

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.ui.admin-endpoint | conforms | `@require_admin` admin blueprint route; thin handler delegates to core; cap from config |

(Joan cited `astral.layers.ui-config-driven-business-logic` — scored above, not a catalog pattern.)

## Plan adherence

**Product (`31515387`, four src files):** Matches Stages 1–4 exactly — `UI_CONFIG` literals, `dispatch_ledger`-joined filtered `list_agent_data_batches`, kwargs + Style-D-on-returned-rows in `list_agent_data_runs`, query params + config cap on `adhoc_runs`, no client `limit`, no frontend, no new route/table. Estimate 2 still fits.

**Tests/bible on tip:** AST-1534 manifest (7 classes) is well-aligned and passes locally (16/16). However the publish ref also carries **AST-1537** test + bible material (`bda5e714`, merged via `merge-tests`) with **no AST-1537 product code** on this branch — plan Files Changed explicitly excluded sibling scope; this is cross-ticket smuggling on the publish ref, not a product defect in the scoped list API itself.

## Findings

### fix-now

**Cross-ticket test/bible contamination (AST-1537 on AST-1534 sub)**  
- **Location:** `tests/component/core/test_inbox.py`, `test_meteorite_email.py`, `test_gmail.py`, `test_api_inbox.py`, `tests/component/utils/test_config.py` (`TestAst1049InboxCreateJobConfig`), plus AST-1537 sections in `docs/test-bible/core/inbox.md`, `meteorite_email.md`, `external/gmail.md`, `ui/api/api_inbox.md`, `utils/config.md`  
- **Evidence:** Commit `bda5e714 test(AST-1537)` is in the three-dot range; `src/core/inbox.py`, `src/external/gmail.py` (beyond pre-existing `date`), `src/ui/api/api_inbox.py` have **no** AST-1537 product diff vs `origin/dev`. Off-manifest tests are **red** on this tip (verified: `TestAst1049InboxCreateJobConfig`, `TestAst1049StripExtractEmailHtml`, `TestGetMessageHtml` fail).  
- **Why fix-now:** Violates `orch.roles.betty-owns-test-tree` and plan boundary (AST-1533/1537 work on AST-1532/1534 publish ref). Leaves a poisoned test tree on the sub even though the narrowed AST-1534 manifest is green.  
- **Recommended downstream action (not Radia lane):** Re-merge `origin/tests` at an AST-1534-only SHA (drop `bda5e714` / AST-1537 hunks), restore dev-compatible inbox/gmail/config tests on this sub, strip AST-1537 bible sections from this publish ref; keep product commit `31515387` as-is.

### discuss

**Plan-is-bible vs qa merge breadth**  
- **Location:** publish ref tip vs plan `## Files Changed`  
- **Question for Chuckles/Betty:** Was `origin/tests` intentionally shared across concurrent children? If yes, document the exception; if no, enforce ticket-scoped test SHAs before merge-tests. AST-1534 product is shippable once test tree is cleaned.

### advisory

**What's solid (product slice):** Layered filter/limit design is clean — empty candidate short-circuits in data, parameterized SQL with ledger join, `adhoc-` strip equivalence matches `run_adhoc_workbench_test`, debug contract on returned rows only, admin route ignores client `limit`. AST-1534 component tests cover scope, ledgerless exclusion, task filter, and cap behavior.

## Frame diff

| Layer | Files | Frame change |
|-------|-------|----------------|
| utils | `config.py` | +`adhoc_import_runs_limit` (10), +`adhoc_import_picker_visible_rows` (5) on `UI_CONFIG` |
| data | `database.py` | `list_agent_data_batches(*, candidate_id, task_key, limit)` — ledger join, optional task filter with one `adhoc-` strip, DESC + LIMIT |
| core | `agent.py` | `list_agent_data_runs` forwards filter/limit; Style D debug on returned rows only |
| ui | `api_admin.py` | `GET /adhoc/runs` reads `candidate_id`/`task_key`; passes config cap + `ui_llm_debug()` |
| tests/docs | 10 non-1534-scoped files | **AST-1537** test + bible hunks (out of ticket scope; several red off-manifest) |

## Notes

- Joan plan-rubric APPROVED attached; no Excluded-statute list → no C4 straggler callout.  
- §5f (debug contract): **conforms** on touched `list_agent_data_runs` path.  
- §5g / external cleanliness: **not applicable** (no external LLM diff).  
- C7 complete; recommend **Review Posted** only after test-tree cleanup — route to **resolve-child** for contamination, not product rework.

**context_tokens≈95000**

## Resolution

**2026-08-29 — Ada / resolve-child**

- **fix-now (AST-1537 test/bible smuggle):** Cleared by Betty — `dd4af004 test(AST-1534): strip smuggled AST-1537 test/bible from publish ref`. Tip after sync: `c46620fe`. Product `31515387` unchanged.
- **Re-ran Betty AST-1534 narrowed manifest:** 16 passed (config + revised AST-1451 + AST-1534 data/core/admin classes).
- **discuss (shared `origin/tests` breadth):** Left for Chuckles/Betty process — not a product gate on this child; no Ada code change.
- **advisory:** No action.
