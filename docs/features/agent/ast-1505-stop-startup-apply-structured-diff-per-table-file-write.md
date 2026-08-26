# AST-1505 — Stop startup apply, structured diff, and per-table file write

**Linear (this ticket):** [AST-1505](https://linear.app/astralcareermatch/issue/AST-1505/stop-startup-apply-structured-diff-and-per-table-file-write)  
**Parent:** [AST-1455](https://linear.app/astralcareermatch/issue/AST-1455/add-show-differences-and-update-file-with-table-version)  
**Publish ref:** `origin/sub/AST-1455/AST-1505-stop-startup-apply-structured-diff-per-table-file-write`

## Summary

Child #1 of AST-1455. Adds core comparison and per-table repo JSON export for `agent` and `agent_task`, exposes them through authenticated admin API routes, and finalizes removal of automatic JSON→database apply at boot. Katherine's sibling AST-1506 wires **Show Differences** and **Update file with table version** in `RepoJsonDivergenceBanner.tsx` against these endpoints. AST-1497/AST-1502 already removed the bootstrap wire and made `apply_repo_admin_json_at_startup` a no-op; this ticket makes that permanent product behavior, adds the missing compare/write surface, and updates operator-facing config text.

## UAT fitness

- **AC restored:** Parent AC — *"After **Update file with table version** on Manage Agents … the personas JSON matches the live personas table; sibling task JSON unchanged when tasks still diverge"* and *"After a successful database edit that diverges from the file, restarting the server (any deploy env) leaves the live table as edited — it is **not** overwritten from the JSON file."*
- **Correct outcome:** Admin can GET a structured row/field diff for one table and POST to overwrite only that table's checked-in JSON from the live DB; server restart never re-applies repo JSON into SQLite; **Revert to file** still restores DB from file on demand.
- **Sibling check:** AST-1506 consumes `GET /api/admin/repo_json/compare/<table_key>` and `POST /api/admin/repo_json/write/<table_key>`; existing `GET /status` and `POST /revert/<table_key>` unchanged; cancel-on-confirm is UI-only (Katherine).
- **Not sufficient:** Leaving `apply_repo_admin_json_at_startup` as a silent no-op without compare/write APIs, or only updating banner copy without per-table file write — operators still cannot see drift or persist one table's version from the product.
- **Wrong fix rejected:** Re-enabling boot-time repo-wins apply, writing both JSON files when updating one table, or forking a second normalization path that could disagree with `get_repo_admin_json_divergence_status`.

## Scope gate

All files and change kinds below are taken from this ticket's **## Scope** only. Out of scope: `RepoJsonDivergenceBanner.tsx`, React pages, statute file edits, git commit/push, sibling-table writes, `tests/**`, `docs/test-bible/**`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/repo_admin_json.py` | Structured per-table comparison; per-table DB→file export; remove `apply_repo_admin_json_at_startup` | core |
| `src/core/bootstrap.py` | Confirm module docstring matches permanent no boot-apply (no functional change expected) | core |
| `src/ui/api/api_admin.py` | `GET /api/admin/repo_json/compare/<table_key>`; `POST /api/admin/repo_json/write/<table_key>` | ui |
| `src/utils/config.py` | Update `REPO_ADMIN_JSON_CONFIG` header comment only — Revert-only apply semantics | utils |

**Out of scope (explicit):** `src/ui/frontend/**` (AST-1506); `canon/statutes/**`; `scripts/export_repo_admin_json.py` (CLI both-table export stays); `src/data/database.py`; `data/admin/*.json`; `tests/**`; `docs/test-bible/**`.

## Stage 1: Core structured comparison

**Done when:** `get_repo_admin_json_table_comparison(table_key)` returns the structured diff payload; when `_repo_admin_json_table_diverged` is false for a table, all three diff lists are empty; when true, at least one list is non-empty; `python3 -m py_compile src/core/repo_admin_json.py` passes. No API routes yet.

1. In `src/core/repo_admin_json.py`, add private helper **`_normalized_row_maps(table_key: str, file_rows: list[dict], db_rows: list[dict]) -> tuple[dict[str, dict], dict[str, dict], dict[str, dict], dict[str, dict]]`** returning `(file_by_key, db_by_key, file_norm_by_key, db_norm_by_key)` where:
   - `key_col = _REPO_JSON_ROW_KEY[table_key]`
   - Keys are `str(row.get(key_col) or "")` for each row in file and db lists
   - `*_norm_by_key` values come from `_normalize_repo_json_row(table_key, row)` on the **raw** row
   - `file_by_key` / `db_by_key` hold the **export-shaped raw rows** (same objects as input lists) for display in the API

2. Add public function **`get_repo_admin_json_table_comparison(table_key: str) -> dict[str, Any]`**:
   - Validate `table_key in get_repo_admin_json_table_keys()` else `ValueError`
   - Open one connection via `database._get_connection()`; `try/finally` close
   - `file_rows = load_repo_admin_json_file(table_key)` (propagate `RuntimeError` / `ValueError`)
   - `db_rows = _fetch_db_repo_json_rows(conn, table_key)`
   - Build maps via `_normalized_row_maps`
   - `file_keys = set(file_by_key)`; `db_keys = set(db_by_key)`
   - **`only_in_database`:** list of `db_by_key[k]` for each `k in sorted(db_keys - file_keys)`
   - **`only_in_file`:** list of `file_by_key[k]` for each `k in sorted(file_keys - db_keys)`
   - **`changed_rows`:** for each `k in sorted(file_keys & db_keys)`, compare `file_norm_by_key[k]` vs `db_norm_by_key[k]` field-by-field (union of keys in both normalized dicts). For each field where normalized values differ, append `{"field": name, "file_value": file_by_key[k].get(name), "database_value": db_by_key[k].get(name)}`. If the fields list is non-empty, append `{"row_key": k, "fields": [...]}` to `changed_rows`
   - Return:

     ```python
     {
         "table_key": table_key,
         "diverged": _repo_admin_json_table_diverged(conn, table_key),
         "repo_relative_path": REPO_ADMIN_JSON_CONFIG["tables"][table_key]["repo_relative_path"],
         "only_in_database": [...],
         "only_in_file": [...],
         "changed_rows": [...],
     }
     ```

3. Add **`get_repo_admin_json_table_comparison`** to **`__all__`**.

⚠️ **Decision:** Reuse existing `_normalize_repo_json_row`, `_sorted_normalized_rows`, and `_repo_admin_json_table_diverged` — do not duplicate scalar rules. Invariant: when `diverged` is false, `only_in_database`, `only_in_file`, and `changed_rows` must all be empty.

## Stage 2: Core per-table export and startup apply removal

**Done when:** `export_repo_admin_json_table_to_file(table_key)` writes exactly one JSON file and returns metadata; `apply_repo_admin_json_at_startup` is removed from the module; `export_repo_admin_json_to_files()` still writes both tables (CLI unchanged); `REPO_ADMIN_JSON_CONFIG` comment reflects Revert-only apply; `python3 -m py_compile src/core/repo_admin_json.py src/core/bootstrap.py src/utils/config.py` passes.

1. In `src/core/repo_admin_json.py`, add **`export_repo_admin_json_table_to_file(table_key: str) -> dict[str, Any]`**:
   - Validate `table_key in get_repo_admin_json_table_keys()` else `ValueError`
   - Open connection; fetch rows via `_fetch_db_repo_json_rows(conn, table_key)`; close connection
   - `path = get_repo_admin_json_path(table_key)`; `path.parent.mkdir(parents=True, exist_ok=True)`
   - Write `json.dumps(rows, indent=2, ensure_ascii=False) + "\n"` with UTF-8 (same as `export_repo_admin_json_to_files`)
   - Return `{"table_key": table_key, "row_count": len(rows), "repo_relative_path": REPO_ADMIN_JSON_CONFIG["tables"][table_key]["repo_relative_path"]}`
   - **Do not** read or write the sibling table's path

2. Add **`export_repo_admin_json_table_to_file`** to **`__all__`**. Leave **`export_repo_admin_json_to_files`** unchanged (both-table CLI path).

3. **Remove** function **`apply_repo_admin_json_at_startup`** entirely:
   - Delete the function body and its **`__all__`** entry
   - Update module docstring (lines 1–7): boot-time apply is **removed** (AST-1455), not merely kill-switched; export, load, compare, revert, and per-table write remain

4. In `src/core/bootstrap.py`, read the module docstring. If it still references AST-1497 kill-switch only, update to cite AST-1455 permanent removal. **Do not** re-add any call to repo JSON apply. `bootstrap_runtime()` stays: validate → schema ensure → scheduler.

5. In `src/utils/config.py`, change the comment above **`REPO_ADMIN_JSON_CONFIG`** (~line 3866) from *"checked-in JSON applied at startup (AST-782)"* to state that checked-in JSON under `data/admin/` is the durable seed, **explicit Revert to file** (and future scripted apply) loads repo-wins into the DB, and **server start does not apply** these files (AST-1455). Do not change table keys, paths, or column definitions.

⚠️ **Decision:** Remove `apply_repo_admin_json_at_startup` rather than keep a no-op stub — `bootstrap_runtime` already does not call it (AST-1502). `revert_repo_admin_json_table` remains the product JSON→DB path. Betty may revise `TestApplyRepoAdminJsonAtStartup` in qa-child; Ada does not edit `tests/`.

## Stage 3: Admin API compare and write routes

**Done when:** Authenticated admin GET returns comparison JSON; POST writes one table's file and returns success metadata; invalid `table_key` returns 400; core errors return 500; routes follow the same thin-wrapper pattern as existing `/repo_json/status` and `/repo_json/revert/<table_key>`; `python3 -m py_compile src/ui/api/api_admin.py` passes.

1. In `src/ui/api/api_admin.py`, extend imports from `src.core.repo_admin_json`:

   ```python
   from src.core.repo_admin_json import (
       export_repo_admin_json_table_to_file,
       get_repo_admin_json_divergence_status,
       get_repo_admin_json_table_comparison,
       revert_repo_admin_json_table,
   )
   ```

2. Add route **`GET /api/admin/repo_json/compare/<table_key>`** with `@require_admin`:
   - If `table_key not in get_repo_admin_json_table_keys()` (import from `src.utils.config`), return `jsonify({"error": "unknown repo admin JSON table"})`, **400**
   - Try `get_repo_admin_json_table_comparison(table_key)`; on `RuntimeError` / `ValueError`, return `jsonify({"error": str(exc)})`, **500**
   - Else return `jsonify(comparison)`, **200**

3. Add route **`POST /api/admin/repo_json/write/<table_key>`** with `@require_admin`:
   - Same `table_key` validation → **400**
   - Try `export_repo_admin_json_table_to_file(table_key)`; on `RuntimeError` / `ValueError`, return `jsonify({"error": str(exc)})`, **500**
   - Else return `jsonify({"ok": True, **result})`, **200** where `result` is the core helper's return dict

4. Place both routes in the existing **Repo admin JSON divergence (AST-783)** section, immediately after `repo_json_revert`.

⚠️ **Decision:** Validate `table_key` against `get_repo_admin_json_table_keys()` from config — not a hardcoded `("agent", "agent_task")` tuple — per `astral.standards.no-hardcoded-sets`. Optionally align `repo_json_revert` to the same guard in this stage only if the one-line change is adjacent; do not otherwise refactor revert.

## Hand-verify (build completion, before Betty)

Run on epic worktree with local server or Flask test client:

1. Edit one persona in Manage Agents (or insert a test row), confirm `GET /api/admin/repo_json/compare/agent` shows the field in `changed_rows` and `diverged: true`.
2. `POST /api/admin/repo_json/write/agent` — confirm `data/admin/agent.json` on disk matches DB export shape; `GET /api/admin/repo_json/status` shows `agent.diverged: false`; `agent_task` status unchanged if tasks were not edited.
3. Restart server (or re-run `bootstrap_runtime()` in a shell) — edited DB row still present; not overwritten from JSON.
4. `POST /api/admin/repo_json/revert/agent` — DB restores from file; divergence clears.

Document pass/fail in the Stage 3 Linear completion comment only (no prompt bodies in comments).

## Estimate

Confirm Chuckles estimate: 5 — agree. Startup wire is already gone; remaining work is comparison logic, per-table export, API surface, and config/doc cleanup — fits 5 points with Betty manifest on compare/write/revert invariants.

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1505
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1455/AST-1505-stop-startup-apply-structured-diff-per-table-file-write` @ `b14c091c45a50a4969c535660728f817cccd3c48`

## Traceability

AC1–2 → Stage 2 `export_repo_admin_json_table_to_file` + Stage 3 `POST /repo_json/write/<table_key>` (sibling AST-1506 wires UI); AC3 → N/A this child (cancel is Katherine confirm-only); AC4 → Stage 2 preserves `revert_repo_admin_json_table` + existing revert route; AC5 → Stage 2 removes `apply_repo_admin_json_at_startup` + bootstrap docstring; parent Show Differences → Stage 1 `GET /repo_json/compare/<table_key>` for AST-1506.

## Findings

### discuss

- **Location:** Stage 1 `get_repo_admin_json_table_comparison` / `astral.standards.dry-and-focused-functions`
- **Finding:** After building `file_rows`/`db_rows` and normalized maps, the stage calls `_repo_admin_json_table_diverged(conn, table_key)`, which reloads file and DB rows again.
- **Recommendation:** Optional implement-time tweak: derive `diverged` from the maps already built (or pass pre-fetched rows into a narrowed helper) to avoid duplicate I/O. Not blocking — correctness is sound.

- **Location:** Stage 2 / `astral.seed.agent-tables-in-repo-json`
- **Finding:** Canon statute still documents kill-switch no-op as the conforming boot path; this plan permanently removes `apply_repo_admin_json_at_startup`. Parent AST-1455 and child Boundaries correctly defer statute amendment to Archie.
- **Recommendation:** Track Archie canon update on parent; do not block build on statute file edit in this child.

- **Location:** Plan structure / R6 self-assessment checklist
- **Finding:** No `## Self-Assessment` section (Estimate confirm line is present).
- **Recommendation:** Optional add before build if Ada wants explicit conf/risk flags; not required for approval given detailed stages and hand-verify checklist.

### acceptable

- **Location:** Stage 3 optional `repo_json_revert` guard alignment
- **Finding:** Plan leaves existing hardcoded `("agent", "agent_task")` tuple on revert unless adjacent one-line change is convenient; new routes correctly use `get_repo_admin_json_table_keys()`.
- **Recommendation:** Aligning revert in Stage 3 is nice consistency; skipping is fine within child scope.

- **Location:** Betty / `orch.roles.betty-owns-test-tree`
- **Finding:** Removing `apply_repo_admin_json_at_startup` will break `tests/component/core/test_repo_admin_json.py` until Betty revises manifest in qa-child (plan acknowledges this).
- **Recommendation:** Expected pipeline — no Ada test edits.

## Build

**Publish ref:** `origin/sub/AST-1455/AST-1505-stop-startup-apply-structured-diff-per-table-file-write` @ `f131f7d45ecbff3b946d58916d004f1cc6e8e5f8`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `e8a037b2` | `get_repo_admin_json_table_comparison` + `_normalized_row_maps` |
| 2 | `7ecb2895` | `export_repo_admin_json_table_to_file`; remove `apply_repo_admin_json_at_startup`; config/bootstrap docstrings |
| 3 | `f131f7d4` | `GET/POST /api/admin/repo_json/compare|write/<table_key>`; revert guard via `get_repo_admin_json_table_keys()` |

Hand-verify: `py_compile` on all touched `.py` files; compare `diverged` invariant checked at import time when env available. Full Flask smoke deferred to Betty manifest.

## Radia review

# Radia review — AST-1505

**Rubric:** code-rubric.v2  
**Ticket:** AST-1505  
**Publish ref:** `origin/sub/AST-1455/AST-1505-stop-startup-apply-structured-diff-per-table-file-write` @ `c49368370d433a775de41f2bd266b69c10723744`  
**Overall:** DISCUSS  
**Diff:** `origin/dev...origin/sub/AST-1455/AST-1505-stop-startup-apply-structured-diff-per-table-file-write` — 10 files, +532/−45 (core compare/write + boot-apply removal, admin routes, Betty test manifest merge, plan doc)

---

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no agent dispatch / confidence paths in diff |
| astral.agent.do-task-delegation | scoped | not-applicable | no do_task changes |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade vector changes |
| astral.batch.batch-id-first | scoped | not-applicable | no batch paths |
| astral.batch.batch-id-format | scoped | not-applicable | no batch paths |
| astral.batch.claim-process-release | scoped | not-applicable | no batch paths |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no batch paths |
| astral.config.config-source-of-truth | scoped | conforms | `REPO_ADMIN_JSON_CONFIG` comment only; table defs unchanged |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no secrets/env reads |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug artifacts |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no debug spikes |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch seed paths |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no run_next changes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single child plan doc in diff |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty paths only in tests/test-bible |
| astral.git.engineer-test-tree-ban | scoped | conforms | test-tree edits via Betty `merge-tests` SHA, not engineer product commits |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | no external layer |
| astral.layers.import-direction | scoped | conforms | core→data/utils; ui→core/utils; no layer violations |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | no frontend; API uses config table keys |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no consult/render paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | compare/write routes use `@require_admin` (existing admin pattern) |
| astral.seed.agent-tables-in-repo-json | scoped | needs-discussion | product removes boot apply entry point; statute still documents kill-switch no-op as conforming |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no seed catalog changes |
| astral.seed.boot-only-not-hot-path | scoped | conforms | bootstrap docstring: schema ensure only, no boot JSON apply |
| astral.seed.define-approved | scoped | not-applicable | no new seed catalog |
| astral.seed.operator-rows-stay-deleted | scoped | conforms | boot does not re-apply repo JSON; operator DB edits survive restart |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no coverage join paths |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no data layer changes |
| astral.standards.database-header-inventory | scoped | not-applicable | no database.py / migration changes |
| astral.standards.debug-contract-gated | scoped | not-applicable | no debug logging added |
| astral.standards.dry-and-focused-functions | scoped | conforms | `_normalized_row_maps` shared; removed dead logger with apply removal |
| astral.standards.in-scope-only | scoped | conforms | no frontend, no statute files, no sibling-table smuggling |
| astral.standards.logging-via-utils | scoped | conforms | removed unused `get_logger` import with apply removal |
| astral.standards.names-not-ticket-ids | scoped | conforms | public helpers named by behavior |
| astral.standards.no-cross-contamination | scoped | conforms | repo JSON surface only |
| astral.standards.no-hardcoded-sets | scoped | conforms | routes/revert use `get_repo_admin_json_table_keys()` |
| astral.standards.public-then-helpers | scoped | conforms | new public helpers precede private maps in module |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | utils change is comment-only |
| astral.state.core-decides-transitions | scoped | not-applicable | no job/state transitions |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job state paths |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no run chain changes |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend |
| astral.ui.naming-conventions | scoped | conforms | route names match existing `repo_json_*` pattern |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no server worker config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1505)` lands Betty manifest at publish tip |
| orch.git.commit-vocabulary | universal | conforms | stage commits follow vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | sub-branch topology respected |
| orch.git.ftr-sub-topology | universal | conforms | child on `sub/AST-1455/...` |
| orch.git.merge-on-checkout | universal | conforms | no checkout violations in diff |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no forbidden git ops |
| orch.git.no-dev-agent-branches | universal | conforms | no agent-named branches |
| orch.git.one-epic-worktree-per-parent | universal | conforms | review on AST-1455 epic worktree |
| orch.git.three-permanent-branches | universal | conforms | diff vs origin/dev baseline |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | no unresolved product forks |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–3 delivered per plan |
| orch.pipeline.project-scoped-queues | universal | conforms | scoped child ticket |
| orch.pipeline.status-gates-skill-entry | universal | conforms | reviewed at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | statute amendment deferred to parent per Joan/plan |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns merged test manifest |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | N/A to code diff |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada assignee at Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path engineer commits in product stages |

Registry table: 63 active rows scored (README cites 65 corpus; 2 not in harvested table).

---

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | plan / parent cite no catalog patterns |

---

## Plan adherence

Stages 1–3 are implemented on the publish tip:

- **`get_repo_admin_json_table_comparison`** + **`_normalized_row_maps`** — structured diff with empty lists when aligned; field-level `changed_rows` on DB edit (tested).
- **`export_repo_admin_json_table_to_file`** — writes one table’s JSON only (tested); sibling file untouched.
- **`apply_repo_admin_json_at_startup`** removed from module and `__all__` (tested).
- Bootstrap + `REPO_ADMIN_JSON_CONFIG` comments updated to AST-1455 permanent semantics.
- Admin **`GET /repo_json/compare/<table_key>`** and **`POST /repo_json/write/<table_key>`** — thin wrappers, `@require_admin`, config-driven `table_key` guard, 400/500 handling matching revert pattern.
- **`repo_json_revert`** guard aligned to `get_repo_admin_json_table_keys()` (plan optional item — done).
- No `RepoJsonDivergenceBanner.tsx` / frontend scope (AST-1506).
- Hand-verify Flask smoke deferred to Betty manifest per plan; Betty manifest merged at tip.

**Estimate (5):** footprint matches — core helpers, two routes, doc cleanup, Betty tests; no scope creep.

**Joan:** plan-rubric APPROVED attached; no Excluded statute list in artifact → no straggler callouts.

---

## Findings

### discuss

- **Location:** `astral.seed.agent-tables-in-repo-json` / parent AST-1455 canon track  
- **Finding:** Statute still lists `apply_repo_admin_json_at_startup` no-op as a conforming kill-switch path. This diff permanently deletes that entry point — correct product behavior per plan, but statute corpus is stale.  
- **Recommendation:** Track Archie statute amendment on parent AST-1455 (already noted in Joan plan review); do not block this child on canon file edits.

- **Location:** `src/core/repo_admin_json.py` — `get_repo_admin_json_table_comparison` `diverged` field (~line 138)  
- **Finding:** Plan text specified returning `diverged` from `_repo_admin_json_table_diverged(conn, table_key)`; implementation derives `diverged` from `only_in_*` / `changed_rows`. Joan flagged duplicate I/O as optional optimization — implementation avoids re-read. For normal single-key-per-row data this matches status endpoint logic. Edge case: duplicate row keys in file/DB collapse in `_normalized_row_maps` but still appear in `_sorted_normalized_rows` — `compare.diverged` could disagree with `GET /status` `diverged`.  
- **Recommendation:** Optional resolve-child tweak: call `_repo_admin_json_table_diverged` with already-fetched rows (narrowed helper) for guaranteed parity with status, or document duplicate-key as invalid input. Not blocking for current two-table catalog.

### advisory

- **Location:** `docs/test-bible/core/bootstrap.md`  
- **Finding:** Historical § still references AST-1502 kill-switch narrative; AST-1505 section notes supersession but full bootstrap bible sweep not done.  
- **Recommendation:** Betty or parent close-out can tighten bootstrap bible prose.

- **Location:** `tests/component/core/test_repo_admin_json.py`  
- **Finding:** Compare tests cover aligned + `changed_rows` paths; no explicit `only_in_file` / `only_in_database` cases.  
- **Recommendation:** Betty may add if she wants fuller diff-list coverage.

- **Location:** `tests/component/ui/api/test_api_admin.py`  
- **Finding:** Write route success + 400 covered; no 500 surfacing test for write (compare has 500 test).  
- **Recommendation:** Optional Betty addition.

---

## What’s solid

- Thin admin API layer: validate table key from config → delegate to core → consistent error JSON.
- Per-table file write isolation tested (`task_path` stays `["unchanged"]` when exporting `agent`).
- Dead boot-apply stub and unused logger removed cleanly.
- Revert route hardcoded tuple replaced — consistent with new routes.
- Betty manifest at tip exercises compare invariant, export isolation, route wiring, and apply removal.

---

## Frame diff

`(none)` — diff matches planned scope: core compare/write + boot-apply removal, admin routes, config/bootstrap comments, Betty test manifest, plan doc. No frontend (AST-1506), no `data/admin/**` edits, no `database.py` changes.

---

## Notes

- Joan plan-rubric verdict attached (APPROVED @ `b14c091c`).
- No plan Excluded statutes → no straggler rows.
- C7 artifact complete for Chuckles writeback.

`context_tokens≈95000`

---

## Resolution

**2026-08-26 — resolve-child (Ada)**

Radia **DISCUSS** @ `c4936837` — **no fix-now** items. Product tip unchanged.

| Finding | Action |
|---------|--------|
| Statute `astral.seed.agent-tables-in-repo-json` stale vs removed boot apply | Deferred to parent AST-1455 / Archie per plan Boundaries — no child canon edit |
| `diverged` derived from diff lists vs `_repo_admin_json_table_diverged` | Kept implementation — avoids duplicate I/O (Joan discuss); duplicate row keys not valid for current catalog |
| Bootstrap bible / Betty test coverage gaps | Advisory only — no engineer test-tree edits |

§9a dry-run: publish ref merges cleanly into `origin/dev` and `origin/ftr/AST-1455-show-differences-update-file`.

**Publish ref @ resolve:** `origin/sub/AST-1455/AST-1505-stop-startup-apply-structured-diff-per-table-file-write` @ `dde9a333`

